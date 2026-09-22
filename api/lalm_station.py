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

from api.google_account import AuthenticationError, user_id_from_request
from api.chat_state import _read_state, _state_value, _headers
from api.chat_transcript_store import STORE
from api.canonical_redis_state import store as canonical_redis_store, _canonical_messages_compatible
import api.chat as chat
from api import chat_turn_state

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
            # Internal forwarding does not traverse the outer canonical-turn
            # middleware. Claim the authenticated durable turn here before inference
            # so first-message thread creation is Workstation-owned and immediately
            # visible to account-scoped sync.
            turn = chat_turn_state.begin_turn(request, payload)
            payload["threadId"] = turn.thread_id
            payload["messageId"] = turn.user_message_id
            payload["assistantMessageId"] = turn.assistant_message_id
            history, _history_revision = chat_turn_state.canonical_history(
                request, thread_id=turn.thread_id, request_id=turn.request_id, limit=32
            )
            payload["history"] = history
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

    @app.get("/api/lalm_station/sync", include_in_schema=False)
    async def station_sync(request: Request):
        try:
            user_id = user_id_from_request(request)
            account_scope = hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:24]
            value = _read_state(user_id)
            revision, state, _ = _state_value(value)
            state = state or {"version": 1, "currentId": "", "threads": []}
            # Canonical Redis is the conversation authority. chat_state is metadata
            # only (current selection, title/pin overrides, tombstones). The Station
            # projects durable threads/messages into one account snapshot for the Mask.
            metadata_threads = {str(t.get("id") or ""): t for t in state.get("threads", []) if isinstance(t, dict)}
            tombstones = {str(t.get("threadId") or "") for t in (value or {}).get("tombstones", []) if isinstance(t, dict)}
            redis = canonical_redis_store()
            threads: list[dict[str, Any]] = []
            for record in redis.list_threads(user_id, limit=80):
                thread_id = str(record.thread_id)
                if not thread_id or thread_id in tombstones:
                    continue
                meta = metadata_threads.get(thread_id, {})
                durable_messages, _legacy_count = _canonical_messages_compatible(redis, user_id=user_id, thread_id=thread_id, limit=1000)
                rendered_messages: list[dict[str, Any]] = []
                for message in durable_messages:
                    role = str(message.role or "").upper()
                    if role not in {"USER", "ASSISTANT"}:
                        continue
                    text = str(message.committed_text or "")
                    # Streaming assistant placeholders are generation state, not
                    # committed conversation messages.
                    if role == "ASSISTANT" and (not text or str(message.state or "").upper() == "STREAMING"):
                        continue
                    rendered_messages.append({
                        "id": str(message.message_id),
                        "role": role.lower(),
                        "text": text,
                        "createdAt": int(float(message.created_at or 0) * 1000),
                        "state": str(message.state or "").lower(),
                        "pinned": bool(meta.get("pinned", False)),
                        "meta": {"requestId": str(message.request_id or ""), "authority": "workstation"},
                    })
                threads.append({
                    "id": thread_id,
                    "title": str(meta.get("title") or record.title or "New conversation"),
                    "createdAt": int(float(record.created_at or 0) * 1000),
                    "updatedAt": int(float(record.updated_at or 0) * 1000),
                    "pinned": bool(meta.get("pinned", False)),
                    "messages": rendered_messages,
                })

            # If the first canonical turn created a durable thread before metadata
            # knew about it, promote that thread into account metadata here. This keeps
            # the Workstation authoritative while making the new thread immediately
            # eligible for drawer population and later metadata actions.
            durable_ids = {str(t.get("id") or "") for t in threads}
            metadata_ids = set(metadata_threads)
            missing_metadata = durable_ids - metadata_ids
            if missing_metadata:
                from api.chat_state import _write_state
                stamp = int(time.time() * 1000)
                state_threads = list(state.get("threads") or [])
                by_id = {str(t.get("id") or ""): t for t in threads}
                for thread_id in missing_metadata:
                    projected = by_id[thread_id]
                    state_threads.insert(0, {
                        "id": thread_id,
                        "title": str(projected.get("title") or "New conversation"),
                        "createdAt": int(projected.get("createdAt") or stamp),
                        "updatedAt": stamp,
                        "pinned": False,
                        "messages": [],
                    })
                revision += 1
                state = {"version": 1, "currentId": next(iter(missing_metadata)), "threads": state_threads}
                _write_state(user_id, {
                    "contract": "swrlz-chat-account-state-v1",
                    "mutationContract": "swrlz-chat-account-mutation-v1",
                    "userId": user_id,
                    "revision": revision,
                    "updatedAt": stamp,
                    "state": state,
                    "tombstones": list((value or {}).get("tombstones") or []),
                })

            current_id = str(state.get("currentId") or "")
            if current_id not in {str(t.get("id") or "") for t in threads}:
                current_id = str(threads[0].get("id") or "") if threads else ""
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
