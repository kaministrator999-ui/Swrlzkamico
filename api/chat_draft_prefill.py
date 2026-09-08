"""Speculative Chat draft-prefill bridge for Server 2.2.7.

The browser may submit an unsent composer draft after a short idle window. The hot
R39 engine owns the actual recurrent-state clone/prefill mechanics; this module owns
request authentication, normalization, bounded execution, and a stable HTTP contract.
Draft prefill never creates a conversation turn and never generates assistant text.
"""
from __future__ import annotations

import time
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

import api.chat as chat
from api.hot_loader import get_engine

MAX_DRAFT_CHARS = 16_000
MAX_HISTORY_TURNS = 32


def _text(value: Any, maximum: int) -> str:
    return str(value or "").strip()[:maximum]


def _normalize(payload: dict[str, Any]) -> dict[str, Any]:
    draft = _text(payload.get("draft"), MAX_DRAFT_CHARS + 1)
    if not draft or len(draft) > MAX_DRAFT_CHARS:
        raise ValueError("draft must be 1..16000 characters")
    thread_id = _text(payload.get("threadId"), 128)
    if not thread_id:
        raise ValueError("threadId is required")
    history_raw = payload.get("history") or []
    if not isinstance(history_raw, list):
        raise ValueError("history must be an array")
    history: list[dict[str, str]] = []
    for turn in history_raw[-MAX_HISTORY_TURNS:]:
        if not isinstance(turn, dict):
            continue
        role = _text(turn.get("role"), 16).lower()
        text = _text(turn.get("text"), 2_000)
        if role in {"user", "assistant"} and text:
            history.append({"role": role.upper(), "text": text})
    return {
        "threadId": thread_id,
        "draft": draft,
        "history": history,
        "profileId": _text(payload.get("profileId"), 96),
    }


def install(server) -> None:
    @chat.app.post("/draft-prefill", include_in_schema=False)
    async def draft_prefill(request: Request):
        try:
            chat._require_web_token(request)
            body = await request.body()
            if len(body) > chat.MAX_REQUEST_BYTES:
                raise ValueError("request exceeds chat request bound")
            import json
            raw = json.loads(body or b"{}")
            if not isinstance(raw, dict):
                raise ValueError("JSON object required")
            payload = _normalize(raw)
            engine, source = get_engine()
            fn = getattr(engine, "prefill_draft", None)
            if not callable(fn):
                return JSONResponse(
                    {"ok": False, "code": "DRAFT_PREFILL_UNSUPPORTED", "detail": "Loaded R39 hot engine does not expose speculative draft prefill."},
                    status_code=409,
                    headers=chat._no_store_headers(),
                )
            started = time.perf_counter()
            result = fn(payload)
            if not isinstance(result, dict):
                raise RuntimeError("draft prefill engine returned a non-object result")
            result.setdefault("elapsedMs", int((time.perf_counter() - started) * 1000))
            result.setdefault("engineSource", source)
            return JSONResponse(result, status_code=200 if result.get("ok") else 409, headers=chat._no_store_headers())
        except chat.BridgeError as exc:
            return chat._json_error(exc.status, exc.code, exc.detail)
        except (ValueError, TypeError) as exc:
            return chat._json_error(400, "DRAFT_PREFILL_INVALID", str(exc))
        except Exception as exc:
            return chat._json_error(500, "DRAFT_PREFILL_FAILED", f"{type(exc).__name__}: {exc}")

    server.CAPABILITIES["chat-draft-prefill"] = {
        "kind": "speculative-runtime-execution",
        "ready": True,
        "path": "/api/chat/draft-prefill",
        "authoritativeMutation": False,
        "assistantGeneration": False,
        "requiresHotEngineSupport": True,
        "detail": "Prefills an unsent composer draft from the conversation cursor without committing a turn; final send must exact-prefix validate before promotion.",
    }
