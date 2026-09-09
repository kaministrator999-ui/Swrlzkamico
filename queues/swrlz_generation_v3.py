from __future__ import annotations

import time
from dataclasses import replace
from typing import Any

from vercel.queue import subscribe

from api.durable_chat_contract import GenerationEventRecord
from api.durable_redis_store import RedisRestChatStore

TERMINAL = {"COMPLETED", "FAILED", "CANCELLED"}
CONTRACT = "swrlz_llm_stream_v2"


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
    data = dict(payload or {})
    user_id, request_id, thread_id = (str(data.get(k) or "") for k in ("userId", "requestId", "threadId"))
    if not user_id or not request_id or not thread_id:
        raise ValueError("durable generation payload is missing identity")

    store = RedisRestChatStore.from_env()
    job = store.get_generation(user_id=user_id, request_id=request_id)
    if job is None:
        raise ValueError("generation job does not exist")
    if job.state in {"COMPLETE", "FAILED", "CANCELLED"}:
        return

    # At-least-once delivery is safe because the persisted job is the idempotency boundary.
    job = store.update_generation(replace(job, state="RUNNING"))
    assistant = store.get_message(user_id=user_id, message_id=job.assistant_message_id)
    if assistant is None:
        raise ValueError("assistant placeholder is missing")

    from runtime_hot import r39_engine_v35 as engine

    history: list[dict[str, str]] = []
    for item in store.list_messages(user_id=user_id, thread_id=thread_id):
        if item.message_id == job.user_message_id:
            break
        if item.role in {"USER", "ASSISTANT"} and item.committed_text:
            history.append({"role": item.role, "text": item.committed_text[-12000:]})

    profile = store.get_profile(user_id=user_id)
    if profile.display_name or profile.preferences or profile.model_preferences:
        import json
        history.insert(0, {"role": "SYSTEM", "text": "USER_PROFILE_EVIDENCE " + json.dumps({
            "displayName": profile.display_name,
            "preferences": profile.preferences,
            "modelPreferences": profile.model_preferences,
        }, ensure_ascii=False, separators=(",", ":"))})

    engine_payload = {
        "protocolVersion": 2, "requestId": request_id,
        "prompt": str(data.get("prompt") or ""), "receivedText": str(data.get("prompt") or ""),
        "history": history[-32:],
        "inputProvenance": data.get("inputProvenance") if isinstance(data.get("inputProvenance"), dict) else {},
        "presentationIntent": str(data.get("presentationIntent") or "PROSE"),
        "generation": data.get("generation") if isinstance(data.get("generation"), dict) else {},
        "profileId": str(data.get("profileId") or "AUTO"),
        "responseDirective": "Answer the current user directly and truthfully. Preserve received user wording as the receipt. Stream only committed assistant text as DELTA.",
    }

    def cancelled() -> bool:
        current = store.get_generation(user_id=user_id, request_id=request_id)
        return current is None or current.state == "CANCELLED"

    seq, committed, last_type = int(job.last_seq), assistant.committed_text, "FAILED"
    started = time.time()
    try:
        for raw in engine.generate_events(engine_payload, cancelled):
            if not isinstance(raw, dict):
                continue
            seq += 1
            event = _wire(raw, seq=seq, request_id=request_id, engine=engine)
            _append(store, user_id=user_id, request_id=request_id, event=event)
            last_type = str(event["type"])
            if last_type == "DELTA":
                committed += str(event["text"])
            if last_type in TERMINAL:
                break
        if last_type not in TERMINAL:
            seq += 1
            last_type = "CANCELLED" if cancelled() else "FAILED"
            event = _wire({"type": last_type, "phase": "CANCELLED" if last_type == "CANCELLED" else "ERROR", "reason": "Generation cancelled." if last_type == "CANCELLED" else "Generation ended without a terminal event.", "totalLatencyMs": int((time.time()-started)*1000)}, seq=seq, request_id=request_id, engine=engine)
            _append(store, user_id=user_id, request_id=request_id, event=event)
    except Exception as exc:
        seq += 1
        last_type = "FAILED"
        event = _wire({"type": "FAILED", "phase": "ERROR", "reason": f"{type(exc).__name__}: {exc}", "totalLatencyMs": int((time.time()-started)*1000)}, seq=seq, request_id=request_id, engine=engine)
        _append(store, user_id=user_id, request_id=request_id, event=event)
        raise
    finally:
        state = "COMPLETE" if last_type == "COMPLETED" else "CANCELLED" if last_type == "CANCELLED" else "FAILED"
        store.put_message(replace(assistant, committed_text=committed, state=state, updated_at=time.time()))
        current = store.get_generation(user_id=user_id, request_id=request_id)
        if current is not None:
            store.update_generation(replace(current, state=state, last_seq=seq, completed_at=time.time()))
