"""Unified server-owned Chat/LALM Station boundary."""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from api.google_account import AuthenticationError, user_id_from_request
from api.chat_state import _read_blob, _state_value, _headers
from api.chat_turn_state import begin_turn, canonical_history, finish_turn

CONTRACT = "swrlz-lalm-station-sync-v1"
MAX_ACTIVE = 8


def _status_list(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    raw = snapshot.get("status")
    if isinstance(raw, list):
        return [dict(item) for item in raw[-256:] if isinstance(item, dict)]
    phase = str(snapshot.get("phase") or "").strip()
    return [] if not phase else [{"seq": int(snapshot.get("lastSeq") or 0), "phase": phase, "at": float(snapshot.get("updatedAt") or 0)}]


def _generation_view(snapshot: dict[str, Any]) -> dict[str, Any]:
    identity = snapshot.get("identity") if isinstance(snapshot.get("identity"), dict) else {}
    return {
        "requestId": str(snapshot.get("requestId") or ""),
        "threadId": str(identity.get("threadId") or snapshot.get("threadId") or ""),
        "ownerId": str(snapshot.get("ownerId") or ""),
        "phase": str(snapshot.get("phase") or ""),
        "terminal": bool(snapshot.get("terminal")),
        "terminalType": str(snapshot.get("terminalType") or ""),
        "text": str(snapshot.get("text") or snapshot.get("transcript") or ""),
        "textRevision": int(snapshot.get("textRevision") or 0),
        "lastSeq": int(snapshot.get("lastSeq") or 0),
        "lastDeltaSeq": int(snapshot.get("lastDeltaSeq") or 0),
        "status": _status_list(snapshot),
        "createdAt": float(snapshot.get("createdAt") or 0),
        "updatedAt": float(snapshot.get("updatedAt") or 0),
        "storage": dict(snapshot.get("storage") or {}),
    }


def install(server, chat_extensions) -> None:
    app = server.app
    chat = chat_extensions.chat

    @app.post("/api/lalm_station/send", include_in_schema=False)
    async def station_send(request: Request):
        """Commit the turn, attach canonical history/identity, and dispatch local R39."""
        turn = None
        try:
            user_id_from_request(request)
            payload = await request.json()
            if not isinstance(payload, dict):
                return JSONResponse({"ok": False, "contract": CONTRACT, "code": "INVALID_JSON_OBJECT"}, status_code=400, headers=_headers())
            if not str(payload.get("prompt") or "").strip():
                return JSONResponse({"ok": False, "contract": CONTRACT, "code": "PROMPT_INVALID"}, status_code=400, headers=_headers())

            turn = begin_turn(request, payload)
            history, history_revision = canonical_history(request, thread_id=turn.thread_id, request_id=turn.request_id)
            admitted = dict(payload)
            admitted.update({
                "history": history,
                "threadId": turn.thread_id,
                "requestId": turn.request_id,
                "ingress": "SWRLZ_LALM_STATION",
                "stationIdentity": {
                    "accountScope": turn.account_scope,
                    "threadId": turn.thread_id,
                    "requestId": turn.request_id,
                    "userMessageId": turn.user_message_id,
                    "assistantMessageId": turn.assistant_message_id,
                },
            })
            normalized = chat._normalize_chat_request(admitted)
            response = chat._stream_response(normalized)
            if getattr(response, "status_code", 200) >= 400:
                # Continuity handoff is not a terminal model failure.
                if response.status_code != 409 or response.headers.get("X-SWRLZ-Continuity-Handoff") != "non-terminal-v1":
                    finish_turn(turn, text="", terminal_type="FAILED", reason=f"STATION_DISPATCH_HTTP_{response.status_code}")
                return response

            original = getattr(response, "body_iterator", None)
            if original is None:
                finish_turn(turn, text="", terminal_type="FAILED", reason="STATION_STREAM_MISSING")
                return JSONResponse({"ok": False, "contract": CONTRACT, "code": "STATION_STREAM_MISSING"}, status_code=503, headers=_headers())

            async def tracked():
                buffer = ""
                answer = ""
                terminal_seen = False
                try:
                    async for chunk in original:
                        decoded = chunk.decode("utf-8", errors="replace") if isinstance(chunk, bytes) else str(chunk)
                        buffer += decoded
                        lines = buffer.split("\n")
                        buffer = lines.pop() or ""
                        for line in lines:
                            if not line.strip():
                                continue
                            try:
                                event = json.loads(line)
                            except Exception:
                                continue
                            kind = str(event.get("type") or "").upper()
                            if kind == "RESET":
                                answer = ""
                            elif kind == "DELTA":
                                answer += str(event.get("text") or "")
                            if kind in {"COMPLETED", "CANCELLED", "FAILED"} and not terminal_seen:
                                finish_turn(turn, text=answer, terminal_type=kind, reason=str(event.get("reason") or "")[:2000])
                                terminal_seen = True
                        yield chunk
                    if not terminal_seen:
                        finish_turn(turn, text=answer, terminal_type="FAILED", reason="STATION_STREAM_ENDED_WITHOUT_TERMINAL")
                except BaseException as exc:
                    # Browser disconnect does not cancel the resumable generation owner.
                    # Do not write a false terminal here; Station sync/transcript follows it.
                    if type(exc).__name__ not in {"CancelledError", "GeneratorExit"} and not terminal_seen:
                        finish_turn(turn, text=answer, terminal_type="FAILED", reason=f"STATION_STREAM_EXCEPTION:{type(exc).__name__}")
                    raise

            headers = dict(getattr(response, "headers", {}) or {})
            headers["X-SWRLZ-LALM-Station"] = CONTRACT
            headers["X-SWRLZ-Canonical-History-Revision"] = str(history_revision)
            return StreamingResponse(tracked(), media_type="application/x-ndjson", headers=headers)
        except AuthenticationError as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "ACCOUNT_SESSION_INVALID", "detail": str(exc)}, status_code=401, headers=_headers())
        except Exception as exc:
            if turn is not None:
                try:
                    finish_turn(turn, text="", terminal_type="FAILED", reason=f"STATION_EXCEPTION:{type(exc).__name__}")
                except Exception:
                    pass
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "LALM_STATION_SEND_FAILED", "detail": f"{type(exc).__name__}: {exc}"}, status_code=503, headers=_headers())

    @app.get("/api/lalm_station/sync", include_in_schema=False)
    async def station_sync(request: Request):
        try:
            user_id = user_id_from_request(request)
            account_scope = hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:24]
            value = _read_blob(user_id)
            revision, state, _ = _state_value(value)
            state = state or {"version": 1, "currentId": "", "threads": []}
            current_id = str(state.get("currentId") or "")
            threads = list(state.get("threads") or [])
            current = next((t for t in threads if str(t.get("id") or "") == current_id), None)
            messages = list(current.get("messages") or []) if isinstance(current, dict) else []

            sessions = getattr(chat_extensions, "RESUMABLE_GENERATIONS", {})
            lock = getattr(chat_extensions, "RESUMABLE_GENERATION_LOCK", None)
            if lock is not None:
                with lock:
                    local = list(sessions.values())
            else:
                local = list(sessions.values())
            active = []
            for session in sorted(local, key=lambda item: float(item.get("updatedAt") or 0), reverse=True):
                if bool(session.get("terminal")):
                    continue
                identity = session.get("identity") if isinstance(session.get("identity"), dict) else {}
                session_scope = str(identity.get("accountScope") or session.get("accountScope") or "")
                if session_scope != account_scope:
                    continue
                active.append(_generation_view(session))
                if len(active) >= MAX_ACTIVE:
                    break

            primary = next((item for item in active if item.get("threadId") == current_id), active[0] if active else None)
            return JSONResponse({
                "ok": True,
                "contract": CONTRACT,
                "serverTime": time.time(),
                "revision": revision,
                "updatedAt": int(value.get("updatedAt") or 0) if value else 0,
                "stateAuthority": "server",
                "threads": threads,
                "currentThread": current,
                "messages": messages,
                "activeGeneration": primary,
                "activeGenerations": active,
                "synchronize": {
                    "required": bool(primary),
                    "requestId": str(primary.get("requestId") or "") if primary else "",
                    "afterSeq": int(primary.get("lastSeq") or 0) if primary else 0,
                    "transcriptEndpoint": "/api/chat/transcript",
                    "sendEndpoint": "/api/lalm_station/send",
                    "strategy": "station-owned-resume-existing-never-restart",
                },
            }, headers=_headers())
        except AuthenticationError as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "ACCOUNT_SESSION_INVALID", "detail": str(exc)}, status_code=401, headers=_headers())
        except Exception as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "LALM_STATION_SYNC_FAILED", "detail": f"{type(exc).__name__}: {exc}"}, status_code=503, headers=_headers())
