"""Authenticated canonical Chat turn status for Mask reconciliation.

This endpoint exposes durable Redis terminal state for one request ID. It does not
perform cognition and does not infer completion from browser timing. The Mask may
use it only to align a locally streaming/reconnecting response with the server-owned
canonical turn state.
"""
from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import canonical_redis_state
from api.google_account import AuthenticationError, user_id_from_request

APP_VERSION = "1.0.0"
CONTRACT = "swrlz-chat-turn-status-v1"
app = FastAPI(title="SWRLZ Chat Turn Status", version=APP_VERSION, docs_url=None, redoc_url=None, openapi_url=None)


def _headers() -> dict[str, str]:
    return {"Cache-Control": "no-store, no-transform", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer"}


def _error(status: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse({"ok": False, "contract": CONTRACT, "code": code, "detail": detail}, status_code=status, headers=_headers())


def _redis_authoritative() -> bool:
    requested = os.environ.get("SWRLZ_CHAT_CANONICAL_BACKEND", "auto").strip().lower() or "auto"
    return canonical_redis_state.configured() and requested in {"auto", "redis"}


@app.get("/api/chat_turn_status", include_in_schema=False)
async def get_turn_status(request: Request):
    try:
        user_id = user_id_from_request(request)
        request_id = str(request.query_params.get("requestId") or "").strip()[:128]
        if not request_id:
            return _error(400, "CHAT_TURN_STATUS_REQUEST_ID_REQUIRED", "requestId is required")
        if not _redis_authoritative():
            return _error(503, "CHAT_TURN_STATUS_REDIS_NOT_AUTHORITATIVE", "Canonical Redis turn state is not authoritative.")
        redis = canonical_redis_state.store()
        job = redis.get_generation(user_id=user_id, request_id=request_id)
        if job is None:
            return _error(404, "CHAT_TURN_STATUS_NOT_FOUND", "Canonical turn was not found.")
        assistant = redis.get_message(user_id=user_id, message_id=job.assistant_message_id)
        if assistant is None:
            return _error(503, "CHAT_TURN_STATUS_ASSISTANT_MISSING", "Canonical assistant record is missing.")
        terminal = str(job.state or "").upper() in {"COMPLETE", "FAILED", "CANCELLED"} and str(assistant.state or "").upper() in {"COMPLETE", "FAILED", "CANCELLED"}
        terminal_type = {"COMPLETE": "COMPLETED", "FAILED": "FAILED", "CANCELLED": "CANCELLED"}.get(str(assistant.state or "").upper(), "")
        provenance: dict[str, Any] = assistant.provenance if isinstance(assistant.provenance, dict) else {}
        return JSONResponse({
            "ok": True,
            "contract": CONTRACT,
            "authority": "canonical-redis",
            "requestId": request_id,
            "threadId": job.thread_id,
            "assistantMessageId": job.assistant_message_id,
            "jobState": job.state,
            "assistantState": assistant.state,
            "terminal": terminal,
            "terminalType": terminal_type,
            "text": assistant.committed_text if terminal else "",
            "updatedAt": int(max(float(job.updated_at or 0), float(assistant.updated_at or 0)) * 1000),
            "completedAt": int(float(job.completed_at or 0) * 1000) if job.completed_at else 0,
            "terminalReason": str(provenance.get("terminalReason") or "")[:2000],
        }, headers=_headers())
    except AuthenticationError as exc:
        return _error(401, "ACCOUNT_SESSION_INVALID", str(exc))
    except Exception as exc:
        return _error(503, "CHAT_TURN_STATUS_FAILED", f"{type(exc).__name__}: {exc}")
