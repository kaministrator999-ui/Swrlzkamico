from __future__ import annotations

import hashlib
import json
import threading
import time
from collections.abc import Iterator
from typing import Any

from fastapi.responses import StreamingResponse

SESSION_TTL_SECONDS = 30 * 60
MAX_SESSION_EVENTS = 4096


def install(chat_extensions) -> None:
    """Detach local R39 generation from an individual browser stream.

    A requestId owns one generation session. Reconnecting clients resubscribe with
    resumeAfterSeq and receive only later events. The generation thread continues
    independently of any one StreamingResponse subscriber while the worker lives.
    """
    chat = chat_extensions.chat
    base_normalize = chat._normalize_chat_request
    base_stream_response = chat._stream_response

    lock = threading.RLock()
    sessions: dict[str, dict[str, Any]] = {}

    def normalize(payload: dict[str, Any]) -> dict[str, Any]:
        normalized = base_normalize(payload)
        try:
            normalized["resumeAfterSeq"] = max(0, int(payload.get("resumeAfterSeq") or 0))
        except (TypeError, ValueError):
            normalized["resumeAfterSeq"] = 0
        return normalized

    def canonical_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in payload.items() if k != "resumeAfterSeq"}

    def fingerprint(payload: dict[str, Any]) -> str:
        raw = json.dumps(canonical_payload(payload), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def prune() -> None:
        cutoff = time.time() - SESSION_TTL_SECONDS
        with lock:
            stale = [rid for rid, session in sessions.items() if session.get("terminal") and float(session.get("updatedAt") or 0) < cutoff]
            for rid in stale:
                sessions.pop(rid, None)

    def append_event(session: dict[str, Any], event: dict[str, Any]) -> None:
        encoded = chat._encode_event(event)
        condition: threading.Condition = session["condition"]
        with condition:
            session["events"].append((int(event["seq"]), encoded))
            if len(session["events"]) > MAX_SESSION_EVENTS:
                session["events"] = session["events"][-MAX_SESSION_EVENTS:]
            session["lastSeq"] = int(event["seq"])
            session["updatedAt"] = time.time()
            if event.get("terminal"):
                session["terminal"] = True
                session["terminalType"] = str(event.get("type") or "")
            condition.notify_all()

    def run_generation(session: dict[str, Any], payload: dict[str, Any]) -> None:
        request_id = payload["requestId"]
        chat_extensions.LOCAL_CANCELLED.discard(request_id)
        seq = 1
        append_event(session, chat._bridge_event(seq, "STARTED", request_id, phase="ANALYZING_REQUEST", reason="Request admitted by the resumable local R39 generation owner."))
        seq += 1
        try:
            engine, source = chat_extensions._engine()
            source_events = engine.generate_events(payload, lambda: request_id in chat_extensions.LOCAL_CANCELLED)
            try:
                for raw in chat_extensions._heartbeat_events(source_events):
                    if raw.get("type") == "ROUTE":
                        chat_extensions.LOCAL_READINESS.update({
                            "checked": True,
                            "oneTokenReady": True,
                            "interactiveReady": True,
                            "ok": True,
                            "engineId": str(engine.ENGINE_ID),
                            "engineSource": source,
                        })
                    event = chat_extensions._event_payload(seq, request_id, raw)
                    append_event(session, event)
                    seq += 1
                    if event.get("terminal"):
                        return
            except RuntimeError as exc:
                if "StopIteration" not in str(exc):
                    raise
            if not session.get("terminal"):
                append_event(session, chat._bridge_event(seq, "FAILED", request_id, phase="ERROR", reason="The local generation owner ended without a terminal model event.", categories=["LOCAL_GENERATION_ENDED_WITHOUT_TERMINAL"], terminal=True))
        except Exception as exc:
            if not session.get("terminal"):
                append_event(session, chat._bridge_event(seq, "FAILED", request_id, phase="ERROR", reason=f"The local generation owner failed ({type(exc).__name__}).", categories=["LOCAL_GENERATION_OWNER_FAILED"], terminal=True))
        finally:
            chat_extensions.LOCAL_CANCELLED.discard(request_id)
            session["updatedAt"] = time.time()

    def get_or_start(payload: dict[str, Any]) -> dict[str, Any]:
        prune()
        request_id = payload["requestId"]
        clean = canonical_payload(payload)
        fp = fingerprint(clean)
        with lock:
            existing = sessions.get(request_id)
            if existing is not None:
                if existing.get("fingerprint") != fp:
                    raise chat.BridgeError(409, "REQUEST_ID_REUSE_MISMATCH", "This requestId already owns a different generation payload.")
                return existing
            condition = threading.Condition(threading.RLock())
            session: dict[str, Any] = {
                "requestId": request_id,
                "fingerprint": fp,
                "condition": condition,
                "events": [],
                "lastSeq": 0,
                "terminal": False,
                "terminalType": "",
                "createdAt": time.time(),
                "updatedAt": time.time(),
            }
            sessions[request_id] = session
            thread = threading.Thread(target=run_generation, args=(session, clean), name=f"swrlz-generation-{request_id[-20:]}", daemon=True)
            session["thread"] = thread
            thread.start()
            return session

    def session_stream(session: dict[str, Any], after_seq: int) -> Iterator[bytes]:
        cursor = max(0, int(after_seq))
        condition: threading.Condition = session["condition"]
        while True:
            with condition:
                available = [(seq, encoded) for seq, encoded in session["events"] if seq > cursor]
                terminal = bool(session.get("terminal"))
                last_seq = int(session.get("lastSeq") or 0)
                if not available and not (terminal and cursor >= last_seq):
                    condition.wait(timeout=8.5)
                    continue
            for seq, encoded in available:
                cursor = seq
                yield encoded
            if terminal and cursor >= last_seq:
                return

    def stream_response(payload: dict[str, Any]):
        if chat._raw_upstream_url():
            return base_stream_response(payload)
        after_seq = max(0, int(payload.get("resumeAfterSeq") or 0))
        session = get_or_start(payload)
        replay_through = int(session.get("lastSeq") or 0)
        headers = chat._no_store_headers()
        headers.update({
            "X-SWRLZ-Stream-Contract": chat.STREAM_CONTRACT,
            "X-SWRLZ-Request-Id": payload["requestId"],
            "X-SWRLZ-Generation-Session": "resumable-v1",
            "X-SWRLZ-Resume-After-Seq": str(after_seq),
            "X-SWRLZ-Replay-Through-Seq": str(replay_through),
            "X-Accel-Buffering": "no",
        })
        return StreamingResponse(session_stream(session, after_seq), media_type="application/x-ndjson", headers=headers)

    chat._normalize_chat_request = normalize
    chat._stream_response = stream_response
    chat_extensions.RESUMABLE_GENERATIONS = sessions
    chat_extensions.RESUMABLE_GENERATION_LOCK = lock
    chat_extensions.RESUMABLE_GENERATION_TTL_SECONDS = SESSION_TTL_SECONDS
    chat_extensions.RESUMABLE_GENERATION_CONTRACT = "resumable-v1"
