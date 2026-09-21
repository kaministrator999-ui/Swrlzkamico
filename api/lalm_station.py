"""Unified server-owned Chat/LALM station synchronization boundary.

The station gives a Chat client one coherent account snapshot: thread list, current
thread, current messages, and active generation state/status.  The browser is a
renderer/subscriber; it is never conversation or generation authority.
"""
from __future__ import annotations

import time
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from api.google_account import AuthenticationError, user_id_from_request
from api.chat_state import _read_blob, _state_value, _headers
from api.chat_transcript_store import STORE

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

    @app.get("/api/lalm_station/sync", include_in_schema=False)
    async def station_sync(request: Request):
        try:
            user_id = user_id_from_request(request)
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
                if session_thread and current_id and session_thread != current_id:
                    continue
                if not session_thread and not session_scope:
                    continue
                active.append(_generation_view(session))
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
