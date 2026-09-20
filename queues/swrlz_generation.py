from __future__ import annotations

import json
import time
from dataclasses import replace
from typing import Any

from vercel.queue import Message, Topic, subscribe

from api.durable_chat_contract import GenerationEventRecord
from api.durable_redis_store import RedisRestChatStore

TOPIC = Topic[dict[str, object]]("swrlz-generation")
STREAM_CONTRACT = "swrlz_llm_stream_v2"
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED"}


def _wire_event(raw: dict[str, Any], *, seq: int, request_id: str, engine) -> dict[str, Any]:
    event_type = str(raw.get("type") or "STATUS").upper()
    if event_type not in {"STARTED", "STATUS", "ROUTE", "DELTA", "RESET", "COMPLETED", "FAILED", "CANCELLED"}:
        event_type = "STATUS"
    identity = dict(raw.get("identity") or {})
    identity.update(
        {
            "streamId": "durable:" + request_id,
            "requestId": request_id,
            "route": identity.get("route") or "LOCAL_R39_DURABLE",
            "access": "ACCOUNT",
            "runtimeId": "swrlz_durable_generation_v1",
            "engineId": identity.get("engineId") or str(getattr(engine, "ENGINE_ID", "")),
            "modelSha256": identity.get("modelSha256") or str(getattr(engine, "MODEL_SHA256", "")),
        }
    )
    terminal = event_type in TERMINAL
    return {
        "protocolVersion": 2,
        "schemaVersion": 2,
        "contractId": STREAM_CONTRACT,
        "seq": seq,
        "type": event_type,
        "identity": identity,
        "text": str(raw.get("text") or "") if event_type == "DELTA" else "",
        "reason": str(raw.get("reason") or ""),
        "categories": list(raw.get("categories") or [])[:16],
        "phase": str(raw.get("phase") or ("COMPLETE" if event_type == "COMPLETED" else "GENERATING")),
        "ingress": "DURABLE_ACCOUNT_CHAT",
        "answerState": "COMPLETE" if event_type == "COMPLETED" else "STREAMING" if event_type == "DELTA" else "NOT_STARTED",
        "terminal": terminal,
        **({"firstDeltaLatencyMs": int(raw["firstDeltaLatencyMs"])} if raw.get("firstDeltaLatencyMs") is not None else {}),
        **({"totalLatencyMs": int(raw["totalLatencyMs"])} if raw.get("totalLatencyMs") is not None else {}),
    }


def _engine_module():
    # v35 pins the proven v34 source commit. This keeps detached jobs on the same reasoning
    # contract as the account-aware chat path instead of depending on instance-local hot files.
    from runtime_hot import r39_engine_v35

    return r39_engine_v35


@subscribe(topic=TOPIC, retry_after=30, max_attempts=3, max_concurrency=2)
async def generate_swrlz_response(message: Message[dict[str, object]]) -> None:
    payload = dict(message.payload)
    user_id = str(payload.get("userId") or "")
    request_id = str(payload.get("requestId") or "")
    thread_id = str(payload.get("threadId") or "")
    if not user_id or not request_id or not thread_id:
        raise ValueError("durable generation payload is missing identity")

    store = RedisRestChatStore.from_env()
    job = store.get_generation(user_id=user_id, request_id=request_id)
    if job is None:
        raise ValueError("generation job does not exist")
    if job.state in {"COMPLETE", "FAILED", "CANCELLED"}:
        return

    started = time.time()
    job = store.update_generation(replace(job, state="RUNNING"))
    assistant = store.get_message(user_id=user_id, message_id=job.assistant_message_id)
    if assistant is None:
        raise ValueError("assistant placeholder is missing")

    messages = store.list_messages(user_id=user_id, thread_id=thread_id)
    history: list[dict[str, str]] = []
    for item in messages:
        if item.message_id == job.user_message_id:
            break
        if item.role in {"USER", "ASSISTANT"} and item.committed_text:
            history.append({"role": item.role, "text": item.committed_text[-12000:]})
    profile = store.get_profile(user_id=user_id)
    profile_evidence = {
        "displayName": profile.display_name,
        "preferences": profile.preferences,
        "modelPreferences": profile.model_preferences,
    }
    if any(value for value in profile_evidence.values()):
        history.insert(
            0,
            {
                "role": "SYSTEM",
                "text": "USER_PROFILE_EVIDENCE " + json.dumps(profile_evidence, ensure_ascii=False, separators=(",", ":")),
            },
        )

    engine = _engine_module()
    engine_payload = {
        "protocolVersion": 2,
        "requestId": request_id,
        "prompt": str(payload.get("prompt") or ""),
        "receivedText": str(payload.get("prompt") or ""),
        "history": history[-32:],
        "inputProvenance": payload.get("inputProvenance") if isinstance(payload.get("inputProvenance"), dict) else {},
        "presentationIntent": str(payload.get("presentationIntent") or "PROSE"),
        "generation": payload.get("generation") if isinstance(payload.get("generation"), dict) else {},
        "profileId": str(payload.get("profileId") or "AUTO"),
        "responseDirective": (
            "Answer the current user directly and truthfully. Preserve the received user text as the receipt. "
            "Use contextual repair only when semantic evidence warrants it. Stream only committed assistant text as DELTA."
        ),
    }

    def cancelled() -> bool:
        current = store.get_generation(user_id=user_id, request_id=request_id)
        return current is None or current.state == "CANCELLED"

    seq = int(job.last_seq)
    committed = assistant.committed_text
    terminal_seen = False
    last_wire: dict[str, Any] | None = None

    try:
        for raw in engine.generate_events(engine_payload, cancelled):
            if not isinstance(raw, dict):
                continue
            seq += 1
            wire = _wire_event(raw, seq=seq, request_id=request_id, engine=engine)
            last_wire = wire
            store.append_generation_event(
                GenerationEventRecord(
                    request_id=request_id,
                    user_id=user_id,
                    seq=seq,
                    event_type=wire["type"],
                    payload=wire,
                )
            )
            if wire["type"] == "DELTA":
                committed += wire["text"]
            if wire["type"] in TERMINAL:
                terminal_seen = True
                break

        current = store.get_generation(user_id=user_id, request_id=request_id)
        cancelled_state = current is not None and current.state == "CANCELLED"
        if not terminal_seen:
            seq += 1
            raw_type = "CANCELLED" if cancelled_state else "FAILED"
            wire = _wire_event(
                {
                    "type": raw_type,
                    "phase": "CANCELLED" if cancelled_state else "ERROR",
                    "reason": "Generation was cancelled." if cancelled_state else "Detached generation ended without a terminal event.",
                    "totalLatencyMs": int((time.time() - started) * 1000),
                },
                seq=seq,
                request_id=request_id,
                engine=engine,
            )
            last_wire = wire
            store.append_generation_event(GenerationEventRecord(request_id=request_id, user_id=user_id, seq=seq, event_type=wire["type"], payload=wire))

        final_type = str((last_wire or {}).get("type") or "FAILED")
        message_state = "COMPLETE" if final_type == "COMPLETED" else "CANCELLED" if final_type == "CANCELLED" else "FAILED"
        store.put_message(replace(assistant, committed_text=committed, state=message_state, updated_at=time.time()))
        final_job = store.get_generation(user_id=user_id, request_id=request_id) or job
        final_state = "COMPLETE" if final_type == "COMPLETED" else "CANCELLED" if final_type == "CANCELLED" else "FAILED"
        store.update_generation(replace(final_job, state=final_state, last_seq=seq, completed_at=time.time()))
    except Exception as exc:
        current = store.get_generation(user_id=user_id, request_id=request_id) or job
        if current.state != "CANCELLED":
            seq = max(seq, current.last_seq) + 1
            wire = _wire_event(
                {
                    "type": "FAILED",
                    "phase": "ERROR",
                    "reason": f"Detached generation failed ({type(exc).__name__}).",
                    "categories": ["DURABLE_GENERATION_RUNTIME_FAILED"],
                    "totalLatencyMs": int((time.time() - started) * 1000),
                },
                seq=seq,
                request_id=request_id,
                engine=engine,
            )
            store.append_generation_event(GenerationEventRecord(request_id=request_id, user_id=user_id, seq=seq, event_type="FAILED", payload=wire))
            store.put_message(replace(assistant, committed_text=committed, state="FAILED", updated_at=time.time()))
            store.update_generation(replace(current, state="FAILED", last_seq=seq, completed_at=time.time()))
        raise
