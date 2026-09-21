"""Unified server-owned Chat/LALM station synchronization boundary.

The station gives a Chat client one coherent account snapshot: thread list, current
thread, current messages, and active generation state/status.  The browser is a
renderer/subscriber; it is never conversation or generation authority.
"""
from __future__ import annotations

import time
import hashlib
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

import api.chat as chat, StreamingResponse

from api.google_account import AuthenticationError, user_id_from_request
from api.chat_state import _read_blob, _state_value, _headers
from api.chat_transcript_store import STORE
from api.chat_turn_state import begin_turn, canonical_history, finish_turn
import api.chat as chat

CONTRACT = "swrlz-lalm-station-sync-v1"
MAX_ACTIVE = 8


def _status_list(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    raw = snapshot.get("status")
    if isinstance(raw, list):
        return [dict(item) for item in raw[-256:] if isinstance(item, dict)]
    phase = str(snapshot.get("phase") or "").strip()
    if not phase:
        return []
    return [{
        "seq": int(snapshot.get("lastSeq") or 0),
        "phase": phase,
        "at": float(snapshot.get("updatedAt") or 0),
    }]


def _generation_view(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "requestId": str(snapshot.get("requestId") or ""),
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

    @app.post("/api/lalm_station/generate", include_in_schema=False)
    async def station_generate(request: Request):
        """Admit one authenticated Chat turn and delegate generation to the installed R39 owner."""
        try:
            user_id = user_id_from_request(request)
            payload = await chat._read_json(request)
            # Account authentication is the Station boundary; canonical turn/state
            # wrappers installed on chat._normalize_chat_request remain authoritative.
            payload["ingress"] = "SWRLZ_LALM_STATION"
            normalized = chat._normalize_chat_request(payload)
            response = chat._stream_response(normalized)
            response.headers["X-SWRLZ-LALM-Station"] = CONTRACT
            response.headers["X-SWRLZ-LALM-Station-Account"] = hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:24]
            return response
        except AuthenticationError as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "ACCOUNT_SESSION_INVALID", "detail": str(exc)}, status_code=401, headers=_headers())
        except chat.BridgeError as exc:
            return chat._json_error(exc.status, exc.code, exc.detail)
        except Exception as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "LALM_STATION_GENERATE_FAILED", "detail": f"{type(exc).__name__}: {exc}"}, status_code=503, headers=_headers())

    @app.post("/api/lalm_station/send", include_in_schema=False)
    async def station_send(request: Request):
        """Accept one authenticated Chat turn and dispatch it to the installed R39 owner."""
        try:
            user_id_from_request(request)
            # Reuse the canonical Chat ingress middleware and installed resumable
            # generation owner instead of creating a second inference path.
            payload = await request.json()
            if not isinstance(payload, dict):
                return JSONResponse({"ok": False, "contract": CONTRACT, "code": "INVALID_REQUEST"}, status_code=400, headers=_headers())
            payload["ingress"] = "SWRLZ_LALM_STATION"
            body = __import__("json").dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            # Starlette's middleware chain is the authority that installs canonical
            # turn identity/history. Route internally through /api/chat so the same
            # admission/commit contracts remain in force.
            scope = dict(request.scope)
            scope["path"] = "/api/chat"
            scope["raw_path"] = b"/api/chat"
            scope["query_string"] = b"action=stream"
            sent = False
            async def receive():
                nonlocal sent
                if sent:
                    return {"type": "http.disconnect"}
                sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            forwarded = Request(scope, receive)
            response = await chat_extensions.chat._post_action(forwarded, "stream")
            return response
        except AuthenticationError as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "ACCOUNT_SESSION_INVALID", "detail": str(exc)}, status_code=401, headers=_headers())
        except Exception as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "LALM_STATION_SEND_FAILED", "detail": f"{type(exc).__name__}: {exc}"}, status_code=503, headers=_headers())


    @app.post("/api/lalm_station/send", include_in_schema=False)
    async def station_send(request: Request):
        """Admit a user turn through the Station and hand generation to R39.

        The existing canonical-turn middleware remains the durable commit/history
        authority.  The Station owns the public Chat contract and delegates to the
        already-installed resumable generation owner rather than proxying through a
        second browser-facing bridge.
        """
        try:
            user_id_from_request(request)
            payload = await chat._read_json(request)
            payload["ingress"] = "SWRLZ_LALM_STATION"
            request._body = __import__("json").dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            request._json = payload
            # Reuse the canonical Chat action internally so its middleware commits
            # the turn, installs server-owned history, binds stationIdentity, and
            # the resumable owner keeps R39 alive after browser disconnect.
            return await chat._post_action(request, "stream")
        except AuthenticationError as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "ACCOUNT_SESSION_INVALID", "detail": str(exc)}, status_code=401, headers=_headers())
        except chat.BridgeError as exc:
            return chat._json_error(exc.status, exc.code, exc.detail)
        except Exception as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "LALM_STATION_SEND_FAILED", "detail": f"{type(exc).__name__}: {exc}"}, status_code=503, headers=_headers())

    @app.post("/api/lalm_station/send", include_in_schema=False)
    async def station_send(request: Request):
        """Admit one canonical user turn and dispatch it directly to local R39."""
        turn = None
        try:
            # Authentication happens before any state mutation.
            user_id_from_request(request)
            payload = await request.json()
            if not isinstance(payload, dict):
                return JSONResponse({"ok": False, "contract": CONTRACT, "code": "INVALID_JSON_OBJECT"}, status_code=400, headers=_headers())
            prompt = str(payload.get("prompt") or "").strip()
            if not prompt:
                return JSONResponse({"ok": False, "contract": CONTRACT, "code": "PROMPT_INVALID"}, status_code=400, headers=_headers())

            turn = begin_turn(request, payload)
            history, history_revision = canonical_history(request, thread_id=turn.thread_id, request_id=turn.request_id)
            admitted = dict(payload)
            admitted["history"] = history
            admitted["threadId"] = turn.thread_id
            admitted["requestId"] = turn.request_id
            admitted["stationIdentity"] = {
                "accountScope": turn.account_scope,
                "threadId": turn.thread_id,
                "requestId": turn.request_id,
                "userMessageId": turn.user_message_id,
                "assistantMessageId": turn.assistant_message_id,
            }

            # Reuse the already-installed resumable owner. With no upstream URL it
            # dispatches to the pre-deployed local R39 engine and owns generation
            # independently of this browser connection.
            chat = chat_extensions.chat
            normalized = chat._normalize_chat_request(admitted)
            response = chat._stream_response(normalized)
            if getattr(response, "status_code", 200) >= 400:
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
                async for chunk in original:
                    decoded = chunk.decode("utf-8", errors="replace") if isinstance(chunk, bytes) else str(chunk)
                    buffer += decoded
                    lines = buffer.split("\n")
                    buffer = lines.pop() or ""
                    for line in lines:
                        if not line.strip():
                            continue
                        try:
                            event = __import__("json").loads(line)
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

            active: list[dict[str, Any]] = []
            sessions = getattr(chat_extensions, "RESUMABLE_GENERATIONS", {})
            lock = getattr(chat_extensions, "RESUMABLE_GENERATION_LOCK", None)
            if lock is not None:
                with lock:
                    local = list(sessions.values())
            else:
                local = list(sessions.values())
            for session in sorted(local, key=lambda s: float(s.get("updatedAt") or 0), reverse=True):
                if bool(session.get("terminal")):
                    continue
                identity = session.get("identity") if isinstance(session.get("identity"), dict) else {}
                # Only expose a session when its durable turn identity belongs to this
                # account/thread.  Legacy sessions lacking identity stay hidden rather
                # than crossing account boundaries.
                session_thread = str(identity.get("threadId") or session.get("threadId") or "")
                session_scope = str(identity.get("accountScope") or session.get("accountScope") or "")
                if not session_scope or session_scope != account_scope:
                    continue
                view = _generation_view(session)
                view["threadId"] = session_thread
                active.append(view)
                if len(active) >= MAX_ACTIVE:
                    break

            primary = active[0] if active else None
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
                    "streamEndpoint": "/api/chat",
                    "strategy": "resume-existing-never-restart",
                },
            }, headers=_headers())
        except AuthenticationError as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "ACCOUNT_SESSION_INVALID", "detail": str(exc)}, status_code=401, headers=_headers())
        except Exception as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "LALM_STATION_SYNC_FAILED", "detail": f"{type(exc).__name__}: {exc}"}, status_code=503, headers=_headers())
