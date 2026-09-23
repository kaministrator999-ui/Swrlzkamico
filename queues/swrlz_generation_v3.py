from __future__ import annotations

import json
import time
from dataclasses import replace
from typing import Any

from vercel.queue import subscribe

from api.durable_chat_contract import GenerationEventRecord
from api.durable_redis_store import RedisRestChatStore

TERMINAL = {"COMPLETED", "FAILED", "CANCELLED"}
CONTRACT = "swrlz_llm_stream_v2"


def _camera(stage: str, *, request_id: str = "", **fields: Any) -> None:
    """Emit one durable-subscriber boundary camera line for Vercel runtime logs."""
    record = {
        "camera": "SWRLZ_WORKSTATION_SUBSCRIBER",
        "stage": stage,
        "requestId": request_id,
        "ts": time.time(),
        **fields,
    }
    try:
        print(json.dumps(record, ensure_ascii=False, separators=(",", ":"), default=str), flush=True)
    except Exception:
        # Diagnostics must never become a generation dependency.
        print(f"SWRLZ_WORKSTATION_SUBSCRIBER stage={stage} requestId={request_id}", flush=True)


def _wire(raw: dict[str, Any], *, seq: int, request_id: str, engine) -> dict[str, Any]:
    kind = str(raw.get("type") or "STATUS").upper()
    if kind not in {"STARTED", "STATUS", "ROUTE", "DELTA", "RESET", "COMPLETED", "FAILED", "CANCELLED"}:
        kind = "STATUS"
    identity = dict(raw.get("identity") or {})
    identity.update({
        "streamId": "durable:" + request_id,
        "requestId": request_id,
        "route": identity.get("route") or "LOCAL_R39_DURABLE",
        "access": "ACCOUNT",
        "runtimeId": "swrlz_durable_generation_v2",
        "engineId": identity.get("engineId") or str(getattr(engine, "ENGINE_ID", "")),
        "modelSha256": identity.get("modelSha256") or str(getattr(engine, "MODEL_SHA256", "")),
    })
    event = {
        "protocolVersion": 2, "schemaVersion": 2, "contractId": CONTRACT, "seq": seq,
        "type": kind, "identity": identity,
        "text": str(raw.get("text") or "") if kind == "DELTA" else "",
        "reason": str(raw.get("reason") or ""), "categories": list(raw.get("categories") or [])[:16],
        "phase": str(raw.get("phase") or ("COMPLETE" if kind == "COMPLETED" else "GENERATING")),
        "ingress": "DURABLE_ACCOUNT_CHAT",
        "answerState": "COMPLETE" if kind == "COMPLETED" else "STREAMING" if kind == "DELTA" else "NOT_STARTED",
        "terminal": kind in TERMINAL,
    }
    if raw.get("firstDeltaLatencyMs") is not None:
        event["firstDeltaLatencyMs"] = int(raw["firstDeltaLatencyMs"])
    if raw.get("totalLatencyMs") is not None:
        event["totalLatencyMs"] = int(raw["totalLatencyMs"])
    return event


def _append(store, *, user_id: str, request_id: str, event: dict[str, Any]) -> None:
    store.append_generation_event(GenerationEventRecord(
        request_id=request_id, user_id=user_id, seq=int(event["seq"]),
        event_type=str(event["type"]), payload=event,
    ))


@subscribe(topic="swrlz-generation")
async def generate_swrlz_response(payload) -> None:
    raw_payload = getattr(payload, "payload", payload)
    data = dict(raw_payload or {})
    user_id, request_id, thread_id = (str(data.get(k) or "") for k in ("userId", "requestId", "threadId"))
    invocation_started = time.time()
    _camera(
        "subscriber-entry",
        request_id=request_id,
        threadId=thread_id,
        hasUserId=bool(user_id),
    )
    if not user_id or not request_id or not thread_id:
        _camera("identity-invalid", request_id=request_id, threadId=thread_id)
        raise ValueError("durable generation payload is missing identity")

    store = RedisRestChatStore.from_env()
    job = store.get_generation(user_id=user_id, request_id=request_id)
    if job is None:
        _camera("job-missing", request_id=request_id, threadId=thread_id)
        raise ValueError("generation job does not exist")
    _camera(
        "job-read",
        request_id=request_id,
        threadId=thread_id,
        jobState=job.state,
        lastSeq=int(job.last_seq),
    )
    if job.state in {"COMPLETE", "FAILED", "CANCELLED"}:
        _camera("subscriber-skip-terminal", request_id=request_id, jobState=job.state)
        return

    # At-least-once delivery is safe because the persisted job is the idempotency boundary.
    job = store.update_generation(replace(job, state="RUNNING", updated_at=time.time()))
    _camera("job-claimed-running", request_id=request_id, lastSeq=int(job.last_seq))
    assistant = next((m for m in store.list_messages(user_id=user_id, thread_id=thread_id) if m.message_id == job.assistant_message_id), None)
    if assistant is None:
        raise ValueError("assistant placeholder is missing")

    # Prompt-size bring-up proved the raw turn is compact (for example, "Hey"
    # reached R39 as 10 tokens). Restore the prepared/hot R39 lineage now so the
    # already-proven native matvec + batched prefill kernels execute again.
    # Keep prompt/token/prefill cameras below to verify the restored path live.
    from api.hot_loader import get_engine
    _camera("engine-load-enter", request_id=request_id)
    engine, _engine_source = get_engine()
    _camera(
        "engine-load-exit",
        request_id=request_id,
        engineSource=str(_engine_source),
        engineId=str(getattr(engine, "ENGINE_ID", "")),
    )

    # R39 bring-up: isolate raw turn -> tokenizer -> model -> decode.
    # Do not inject transcript/profile machinery while proving baseline inference.
    # Reintroduce each source later behind an explicit bounded context budget.
    history: list[dict[str, str]] = []

    engine_payload = {
        "protocolVersion": 2, "requestId": request_id,
        "prompt": str(data.get("prompt") or ""), "receivedText": str(data.get("prompt") or ""),
        "history": history[-32:],
        "inputProvenance": data.get("inputProvenance") if isinstance(data.get("inputProvenance"), dict) else {},
        "presentationIntent": str(data.get("presentationIntent") or "PROSE"),
        "generation": data.get("generation") if isinstance(data.get("generation"), dict) else {},
        "profileId": str(data.get("profileId") or "AUTO"),
        "responseDirective": "",
    }

    def cancelled() -> bool:
        current = store.get_generation(user_id=user_id, request_id=request_id)
        return current is None or current.state == "CANCELLED"

    seq, committed, last_type = int(job.last_seq), assistant.committed_text, "FAILED"
    started = time.time()
    _camera(
        "generate-events-enter",
        request_id=request_id,
        historyCount=len(history[-32:]),
        promptChars=len(str(data.get("prompt") or "")),
    )
    try:
        for raw in engine.generate_events(engine_payload, cancelled):
            if not isinstance(raw, dict):
                continue
            seq += 1
            event = _wire(raw, seq=seq, request_id=request_id, engine=engine)
            _camera(
                "model-event",
                request_id=request_id,
                seq=seq,
                eventType=str(event["type"]),
                phase=str(event["phase"]),
                elapsedMs=int((time.time() - started) * 1000),
                textChars=len(str(event.get("text") or "")),
            )
            if str(raw.get("phase") or "") in {"PROMPT_DIAGNOSTIC", "PREFILL_COMPLETE"}:
                _camera(
                    "r39-inference-metrics",
                    request_id=request_id,
                    phase=str(raw.get("phase") or ""),
                    reason=str(raw.get("reason") or "")[:1000],
                )
            if str(raw.get("phase") or "") == "MODEL_LOAD_DIAGNOSTIC":
                # The stream contract intentionally drops engine-private fields.
                # Emit bounded diagnostic evidence at the subscriber boundary,
                # without logging prompts, history, credentials, or full payloads.
                _camera(
                    "model-load-diagnostic",
                    request_id=request_id,
                    checkpoint=str(raw.get("checkpoint") or "")[:100],
                    reason=str(raw.get("reason") or "")[:1600],
                    categories=[str(item)[:100] for item in (raw.get("categories") or [])[:8]],
                    errorTraceback=str(raw.get("traceback") or "")[-4000:],
                )
            _append(store, user_id=user_id, request_id=request_id, event=event)
            # Every emitted model event renews the Workstation lease and advances
            # the durable snapshot independently of any connected Chat client.
            current_job = store.get_generation(user_id=user_id, request_id=request_id)
            if current_job is not None and current_job.state not in {"COMPLETE", "FAILED", "CANCELLED"}:
                store.update_generation(replace(current_job, state="RUNNING", last_seq=seq, updated_at=time.time()))
            last_type = str(event["type"])
            if last_type == "DELTA":
                committed += str(event["text"])
            if last_type in TERMINAL:
                _camera(
                    "model-terminal-event",
                    request_id=request_id,
                    seq=seq,
                    eventType=last_type,
                    elapsedMs=int((time.time() - started) * 1000),
                )
                break
        _camera(
            "generate-events-return",
            request_id=request_id,
            lastType=last_type,
            seq=seq,
            elapsedMs=int((time.time() - started) * 1000),
        )
        if last_type not in TERMINAL:
            seq += 1
            last_type = "CANCELLED" if cancelled() else "FAILED"
            event = _wire({"type": last_type, "phase": "CANCELLED" if last_type == "CANCELLED" else "ERROR", "reason": "Generation cancelled." if last_type == "CANCELLED" else "Generation ended without a terminal event.", "totalLatencyMs": int((time.time()-started)*1000)}, seq=seq, request_id=request_id, engine=engine)
            _append(store, user_id=user_id, request_id=request_id, event=event)
    except Exception as exc:
        _camera(
            "subscriber-exception",
            request_id=request_id,
            errorType=type(exc).__name__,
            error=str(exc)[:1000],
            seq=seq,
            elapsedMs=int((time.time() - started) * 1000),
        )
        seq += 1
        last_type = "FAILED"
        event = _wire({"type": "FAILED", "phase": "ERROR", "reason": f"{type(exc).__name__}: {exc}", "totalLatencyMs": int((time.time()-started)*1000)}, seq=seq, request_id=request_id, engine=engine)
        _append(store, user_id=user_id, request_id=request_id, event=event)
        raise
    finally:
        state = "COMPLETE" if last_type == "COMPLETED" else "CANCELLED" if last_type == "CANCELLED" else "FAILED"
        _camera(
            "subscriber-finally-enter",
            request_id=request_id,
            finalState=state,
            lastType=last_type,
            seq=seq,
            committedChars=len(committed),
            generationElapsedMs=int((time.time() - started) * 1000),
            invocationElapsedMs=int((time.time() - invocation_started) * 1000),
        )
        store.update_message(replace(assistant, committed_text=committed, state=state, updated_at=time.time()))
        current = store.get_generation(user_id=user_id, request_id=request_id)
        if current is not None:
            store.update_generation(replace(current, state=state, last_seq=seq, completed_at=time.time()))
        _camera(
            "subscriber-finally-exit",
            request_id=request_id,
            finalState=state,
            seq=seq,
            committedChars=len(committed),
            invocationElapsedMs=int((time.time() - invocation_started) * 1000),
        )
