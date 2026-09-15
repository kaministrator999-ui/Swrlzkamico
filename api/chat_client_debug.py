from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
from threading import Lock

_RECENT = deque(maxlen=500)
_LOCK = Lock()
_RUNTIME_WEB_TOKEN = Path("/tmp/swrlz-admin/runtime/web-chat-token.txt")
_TERMINAL = {"COMPLETED", "CANCELLED", "FAILED"}


def _clean(value, depth=0):
    if depth > 4:
        return "[depth-limit]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:2000]
    if isinstance(value, list):
        return [_clean(v, depth + 1) for v in value[:40]]
    if isinstance(value, dict):
        return {str(k)[:80]: _clean(v, depth + 1) for k, v in list(value.items())[:40]}
    return str(value)[:2000]


def _valid_token(value: str) -> bool:
    return 16 <= len(value) <= 512 and not any(ord(char) < 32 or ord(char) == 127 for char in value)


def _expected_web_token() -> str:
    try:
        runtime_token = _RUNTIME_WEB_TOKEN.read_text("utf-8").strip()
    except OSError:
        runtime_token = ""
    if _valid_token(runtime_token):
        return runtime_token
    configured = os.environ.get("SWRLZ_WEB_CHAT_TOKEN", "").strip()
    return configured if _valid_token(configured) else ""


def _authorized_chat_ingress(request) -> bool:
    expected = _expected_web_token()
    supplied = request.headers.get("x-swrlz-chat-token", "")
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


def _account_scope(request) -> str:
    try:
        from api.google_account import user_id_from_request
        user_id = user_id_from_request(request)
    except Exception:
        return ""
    return hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:24]


def _message_receipt(payload: dict, request) -> dict | None:
    prompt = str(payload.get("prompt") or "").strip()
    if not prompt:
        return None
    request_id = str(payload.get("requestId") or "").strip()[:128]
    thread_id = str(payload.get("threadId") or "").strip()[:128]
    supplied_message_id = str(payload.get("messageId") or "").strip()[:160]
    derived = hashlib.sha256((request_id + "\x00" + thread_id + "\x00" + prompt).encode("utf-8")).hexdigest()[:24]
    return {
        "eventType": "CHAT_MESSAGE_ACCEPTED",
        "receivedAt": datetime.now(timezone.utc).isoformat(),
        "accountScope": _account_scope(request),
        "threadId": thread_id,
        "messageId": supplied_message_id or ("ingress:" + derived),
        "requestId": request_id,
        "role": "user",
        "text": prompt[:16000],
        "textBytes": len(prompt.encode("utf-8")),
        "persistence": "PENDING_SERVER_COMMIT",
        "generationStarted": False,
    }


def _turn_log(event: dict) -> None:
    print("SWRLZ_CHAT_TURN " + json.dumps(event, separators=(",", ":"), ensure_ascii=True), flush=True)


def _stream_event(line: str) -> dict | None:
    try:
        value = json.loads(line)
    except (TypeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def install(server) -> None:
    from fastapi import Request
    from fastapi.responses import JSONResponse

    app = getattr(server, "app", server)

    async def chat_client_debug_post(request: Request):
        try:
            raw = await request.json()
        except Exception:
            raw = {}
        event = _clean(raw if isinstance(raw, dict) else {})
        record = {
            "receivedAt": datetime.now(timezone.utc).isoformat(),
            "event": event,
        }
        with _LOCK:
            _RECENT.append(record)
        print("SWRLZ_CHAT_CLIENT_DEBUG " + json.dumps(record, separators=(",", ":"), ensure_ascii=True), flush=True)
        return JSONResponse({"ok": True}, headers={"Cache-Control": "no-store"})

    async def chat_client_debug_get(request: Request):
        try:
            limit = int(request.query_params.get("limit", "120") or 120)
        except (TypeError, ValueError):
            limit = 120
        safe_limit = max(1, min(limit, 500))
        with _LOCK:
            rows = list(_RECENT)[-safe_limit:]
        return JSONResponse({"ok": True, "count": len(rows), "events": rows}, headers={"Cache-Control": "no-store"})

    # Vercel's function destination path is /api/chat.py. The public diagnostic
    # route is marked by vercel.json with a private query flag, so intercept it
    # before FastAPI route matching. This avoids depending on Vercel's internal
    # ASGI pathname semantics while keeping api/chat.py as the single owner.
    @app.middleware("http")
    async def chat_client_debug_middleware(request: Request, call_next):
        if request.query_params.get("__swrlz_client_debug") == "1":
            if request.method == "POST":
                return await chat_client_debug_post(request)
            if request.method == "GET":
                return await chat_client_debug_get(request)
            return JSONResponse({"ok": False, "detail": "Method Not Allowed"}, status_code=405, headers={"Cache-Control": "no-store"})

        turn = None
        raw: dict = {}
        action = request.query_params.get("action", "stream").strip().lower()
        canonical_candidate = request.method == "POST" and action == "stream" and _authorized_chat_ingress(request)
        if canonical_candidate:
            try:
                parsed = await request.json()
                raw = parsed if isinstance(parsed, dict) else {}
            except Exception:
                raw = {}

            prompt = str(raw.get("prompt") or "").strip()
            request_id = str(raw.get("requestId") or "").strip()
            if prompt and request_id:
                accepted = _message_receipt(raw, request)
                if accepted is not None:
                    _turn_log(accepted)
                try:
                    from api.chat_turn_state import begin_turn, canonical_history
                    from api.google_account import AuthenticationError
                    turn = begin_turn(request, raw)
                    history, history_revision = canonical_history(
                        request,
                        thread_id=turn.thread_id,
                        request_id=turn.request_id,
                    )
                    # The downstream Chat route still owns schema validation and
                    # stream transport. Replace only the browser-supplied history
                    # with the authenticated server account's canonical history.
                    raw["history"] = history
                    request._body = json.dumps(raw, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                    request._json = raw
                    _turn_log(
                        {
                            "eventType": "CHAT_MESSAGE_COMMITTED",
                            "receivedAt": datetime.now(timezone.utc).isoformat(),
                            "accountScope": turn.account_scope,
                            "threadId": turn.thread_id,
                            "messageId": turn.user_message_id,
                            "assistantMessageId": turn.assistant_message_id,
                            "requestId": turn.request_id,
                            "role": "user",
                            "text": prompt[:16000],
                            "textBytes": len(prompt.encode("utf-8")),
                            "persistence": "PRIVATE_ACCOUNT_BLOB",
                            "stateRevision": turn.user_revision,
                            "generationStarted": False,
                        }
                    )
                    _turn_log(
                        {
                            "eventType": "CHAT_HISTORY_CANONICALIZED",
                            "receivedAt": datetime.now(timezone.utc).isoformat(),
                            "accountScope": turn.account_scope,
                            "threadId": turn.thread_id,
                            "requestId": turn.request_id,
                            "historyMessages": len(history),
                            "historyRevision": history_revision,
                            "authority": "PRIVATE_ACCOUNT_BLOB",
                            "clientHistoryAuthoritative": False,
                        }
                    )
                except AuthenticationError:
                    _turn_log(
                        {
                            "eventType": "CHAT_MESSAGE_SERVER_STATE_SKIPPED",
                            "receivedAt": datetime.now(timezone.utc).isoformat(),
                            "threadId": str(raw.get("threadId") or "")[:128],
                            "requestId": request_id[:128],
                            "reason": "ACCOUNT_SESSION_UNAVAILABLE",
                            "persistence": "CLIENT_COMPATIBILITY_ONLY",
                        }
                    )
                except Exception as exc:
                    _turn_log(
                        {
                            "eventType": "CHAT_MESSAGE_COMMIT_FAILED",
                            "receivedAt": datetime.now(timezone.utc).isoformat(),
                            "accountScope": _account_scope(request),
                            "threadId": str(raw.get("threadId") or "")[:128],
                            "requestId": request_id[:128],
                            "error": f"{type(exc).__name__}: {exc}"[:1200],
                            "generationStarted": False,
                        }
                    )
                    return JSONResponse(
                        {"ok": False, "code": "CHAT_MESSAGE_COMMIT_FAILED", "detail": "The server could not durably commit this message and canonicalize its history, so generation was not started."},
                        status_code=503,
                        headers={"Cache-Control": "no-store"},
                    )

        try:
            response = await call_next(request)
        except BaseException as exc:
            if turn is not None:
                try:
                    from api.chat_turn_state import finish_turn
                    revision = finish_turn(turn, text="", terminal_type="FAILED", reason=f"ROUTE_EXCEPTION:{type(exc).__name__}")
                    _turn_log(
                        {
                            "eventType": "CHAT_GENERATION_TERMINAL",
                            "receivedAt": datetime.now(timezone.utc).isoformat(),
                            "accountScope": turn.account_scope,
                            "threadId": turn.thread_id,
                            "messageId": turn.assistant_message_id,
                            "requestId": turn.request_id,
                            "terminalType": "FAILED",
                            "stateRevision": revision,
                            "reason": f"ROUTE_EXCEPTION:{type(exc).__name__}",
                        }
                    )
                except Exception as commit_exc:
                    _turn_log({"eventType": "CHAT_ASSISTANT_COMMIT_FAILED", "requestId": turn.request_id, "error": f"{type(commit_exc).__name__}: {commit_exc}"[:1200]})
            raise

        if turn is None:
            return response

        if response.status_code == 409 and response.headers.get("X-SWRLZ-Continuity-Handoff") == "non-terminal-v1":
            # A resumable generation may legitimately belong to another worker.
            # That owner handoff is continuity, not a model terminal. The original
            # generation owner remains responsible for the terminal canonical
            # assistant commit while the browser follows the shared transcript.
            _turn_log(
                {
                    "eventType": "CHAT_GENERATION_CONTINUITY_HANDOFF",
                    "receivedAt": datetime.now(timezone.utc).isoformat(),
                    "accountScope": turn.account_scope,
                    "threadId": turn.thread_id,
                    "messageId": turn.assistant_message_id,
                    "requestId": turn.request_id,
                    "stateRevision": turn.user_revision,
                    "httpStatus": 409,
                    "terminal": False,
                    "persistence": "UNCHANGED",
                    "reason": "GENERATION_SESSION_REMOTE_OWNER",
                }
            )
            return response

        if response.status_code >= 400:
            try:
                from api.chat_turn_state import finish_turn
                revision = finish_turn(turn, text="", terminal_type="FAILED", reason=f"HTTP_{response.status_code}")
                _turn_log(
                    {
                        "eventType": "CHAT_GENERATION_TERMINAL",
                        "receivedAt": datetime.now(timezone.utc).isoformat(),
                        "accountScope": turn.account_scope,
                        "threadId": turn.thread_id,
                        "messageId": turn.assistant_message_id,
                        "requestId": turn.request_id,
                        "terminalType": "FAILED",
                        "stateRevision": revision,
                        "reason": f"HTTP_{response.status_code}",
                    }
                )
            except Exception as exc:
                _turn_log({"eventType": "CHAT_ASSISTANT_COMMIT_FAILED", "requestId": turn.request_id, "error": f"{type(exc).__name__}: {exc}"[:1200]})
            return response

        original_iterator = getattr(response, "body_iterator", None)
        if original_iterator is None:
            return response

        response.headers["X-SWRLZ-Canonical-Turn"] = "swrlz-chat-canonical-turn-v1"
        response.headers["X-SWRLZ-State-Revision"] = str(turn.user_revision)
        _turn_log(
            {
                "eventType": "CHAT_GENERATION_STARTED",
                "receivedAt": datetime.now(timezone.utc).isoformat(),
                "accountScope": turn.account_scope,
                "threadId": turn.thread_id,
                "messageId": turn.assistant_message_id,
                "requestId": turn.request_id,
                "stateRevision": turn.user_revision,
                "generationStarted": True,
            }
        )

        async def tracked_stream():
            buffer = ""
            answer = ""
            terminal_seen = False

            async def persist_terminal(terminal_type: str, reason: str) -> None:
                nonlocal terminal_seen
                if terminal_seen:
                    return
                from api.chat_turn_state import finish_turn
                revision = finish_turn(turn, text=answer, terminal_type=terminal_type, reason=reason)
                terminal_seen = True
                _turn_log(
                    {
                        "eventType": "CHAT_GENERATION_TERMINAL",
                        "receivedAt": datetime.now(timezone.utc).isoformat(),
                        "accountScope": turn.account_scope,
                        "threadId": turn.thread_id,
                        "messageId": turn.assistant_message_id,
                        "requestId": turn.request_id,
                        "role": "assistant",
                        "terminalType": terminal_type,
                        "text": answer[:16000],
                        "textBytes": len(answer.encode("utf-8")),
                        "persistence": "PRIVATE_ACCOUNT_BLOB",
                        "stateRevision": revision,
                    }
                )

            def observe(text: str) -> tuple[str | None, str]:
                nonlocal buffer, answer
                terminal_type = None
                terminal_reason = ""
                buffer += text
                lines = buffer.split("\n")
                buffer = lines.pop()
                for line in lines:
                    if not line.strip():
                        continue
                    event = _stream_event(line)
                    if not event:
                        continue
                    event_type = str(event.get("type") or "").upper()
                    if event_type == "RESET":
                        answer = ""
                    elif event_type == "DELTA" and isinstance(event.get("text"), str):
                        answer += event["text"]
                    if event_type in _TERMINAL:
                        terminal_type = event_type
                        terminal_reason = str(event.get("reason") or "")[:2000]
                return terminal_type, terminal_reason

            try:
                async for chunk in original_iterator:
                    if isinstance(chunk, bytes):
                        decoded = chunk.decode("utf-8", errors="replace")
                    elif isinstance(chunk, str):
                        decoded = chunk
                    else:
                        decoded = bytes(chunk).decode("utf-8", errors="replace")
                    terminal_type, terminal_reason = observe(decoded)
                    if terminal_type and not terminal_seen:
                        try:
                            await persist_terminal(terminal_type, terminal_reason)
                        except Exception as exc:
                            _turn_log(
                                {
                                    "eventType": "CHAT_ASSISTANT_COMMIT_FAILED",
                                    "receivedAt": datetime.now(timezone.utc).isoformat(),
                                    "accountScope": turn.account_scope,
                                    "threadId": turn.thread_id,
                                    "messageId": turn.assistant_message_id,
                                    "requestId": turn.request_id,
                                    "error": f"{type(exc).__name__}: {exc}"[:1200],
                                }
                            )
                            raise RuntimeError("CHAT_ASSISTANT_COMMIT_FAILED") from exc
                    yield chunk
                if not terminal_seen:
                    await persist_terminal("FAILED", "STREAM_ENDED_WITHOUT_TERMINAL")
            except BaseException as exc:
                if not terminal_seen:
                    terminal_type = "CANCELLED" if isinstance(exc, asyncio.CancelledError) else "FAILED"
                    try:
                        await persist_terminal(terminal_type, f"STREAM_EXCEPTION:{type(exc).__name__}")
                    except Exception as commit_exc:
                        _turn_log({"eventType": "CHAT_ASSISTANT_COMMIT_FAILED", "requestId": turn.request_id, "error": f"{type(commit_exc).__name__}: {commit_exc}"[:1200]})
                raise

        response.body_iterator = tracked_stream()
        return response

    capabilities = getattr(server, "CAPABILITIES", None)
    if isinstance(capabilities, dict):
        capabilities["chat-client-debug"] = {
            "kind": "diagnostics",
            "ready": True,
            "path": "/api/chat/client-debug",
            "detail": "Bounded browser boot checkpoints are emitted to Vercel runtime logs and retained briefly in-process for direct inspection.",
        }
        capabilities["chat-canonical-turn-state"] = {
            "kind": "durable-user-state",
            "ready": True,
            "contract": "swrlz-chat-canonical-turn-v1",
            "authority": "server",
            "commitBeforeGeneration": True,
            "assistantCommitAtTerminal": True,
            "historyAuthority": "server-account-state",
            "clientHistoryAuthoritative": False,
            "continuityHandoffNonTerminal": True,
            "continuityHandoffHeader": "X-SWRLZ-Continuity-Handoff: non-terminal-v1",
            "detail": "Authenticated Chat turns are committed to private server state before inference; LALM history is rebuilt from that canonical state; assistant output is committed at the terminal boundary. Cross-worker owner handoffs do not create false terminal assistant failures. The browser remains a presentation/cache surface.",
        }
