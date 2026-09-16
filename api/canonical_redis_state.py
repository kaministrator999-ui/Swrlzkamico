"""Redis-backed canonical Chat turn state.

This module is an adapter between the existing browser/server canonical Chat IDs and
the record-oriented durable Redis store. It does not select itself as production
backend; chat_turn_state owns that policy boundary.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, replace
from typing import Any

from api.durable_chat_contract import GenerationJobRecord, MessageRecord, ThreadRecord
from api.durable_redis_store import DurableStoreUnavailable
from api.durable_redis_atomic import AtomicRedisRestChatStore


_BEGIN_CANONICAL_TURN_LUA = r'''
-- KEYS: job, user-message, assistant-message, message-index, active-jobs,
--       thread, thread-index
-- ARGV: job-json, user-json, assistant-json, user-score, assistant-score,
--       request-id, thread-json, thread-score, thread-id
if redis.call('EXISTS', KEYS[1]) == 1 then
  return 0
end
if redis.call('EXISTS', KEYS[2]) == 1 or redis.call('EXISTS', KEYS[3]) == 1 then
  return -1
end
redis.call('SET', KEYS[2], ARGV[2])
redis.call('ZADD', KEYS[4], ARGV[4], cjson.decode(ARGV[2]).message_id)
redis.call('SET', KEYS[3], ARGV[3])
redis.call('ZADD', KEYS[4], ARGV[5], cjson.decode(ARGV[3]).message_id)
redis.call('SET', KEYS[1], ARGV[1])
redis.call('SADD', KEYS[5], ARGV[6])
redis.call('SET', KEYS[6], ARGV[7])
redis.call('ZADD', KEYS[7], ARGV[8], ARGV[9])
return 1
'''

_FINISH_CANONICAL_TURN_LUA = r'''
-- KEYS: job, assistant-message, active-jobs
-- ARGV: assistant-json, job-json, request-id
if redis.call('EXISTS', KEYS[1]) ~= 1 then
  return -1
end
redis.call('SET', KEYS[2], ARGV[1])
redis.call('SET', KEYS[1], ARGV[2])
redis.call('SREM', KEYS[3], ARGV[3])
return 1
'''


def configured() -> bool:
    return AtomicRedisRestChatStore.configured()


def store() -> AtomicRedisRestChatStore:
    return AtomicRedisRestChatStore.from_env()


def begin_canonical_turn(
    *, user_id: str, thread_id: str, request_id: str, user_message_id: str,
    assistant_message_id: str, prompt: str, title: str,
    user_created_at_ms: int, assistant_created_at_ms: int, turn_contract: str,
) -> None:
    redis = store()
    existing_job = redis.get_generation(user_id=user_id, request_id=request_id)
    if existing_job is not None:
        _verify_existing(redis, existing_job, thread_id, user_message_id, assistant_message_id, prompt)
        return

    now = time.time()
    user_at = user_created_at_ms / 1000.0
    assistant_at = assistant_created_at_ms / 1000.0
    existing_thread = redis.get_thread(user_id=user_id, thread_id=thread_id)
    thread = existing_thread or ThreadRecord(
        thread_id=thread_id, user_id=user_id, title=title or "New conversation",
        created_at=user_at, updated_at=now,
    )
    if existing_thread is not None:
        thread = replace(
            existing_thread,
            title=(title if existing_thread.title == "New conversation" and title else existing_thread.title),
            updated_at=now,
        )

    provenance = {"authority": "server", "turnContract": turn_contract, "commitPhase": "PRE_GENERATION"}
    user_message = MessageRecord(
        message_id=user_message_id, thread_id=thread_id, user_id=user_id, role="USER",
        received_text=prompt, committed_text=prompt, provenance=provenance,
        interpretation={}, state="COMPLETE", request_id=request_id,
        created_at=user_at, updated_at=now,
    )
    assistant_message = MessageRecord(
        message_id=assistant_message_id, thread_id=thread_id, user_id=user_id, role="ASSISTANT",
        received_text=None, committed_text="", provenance={"authority": "server", "turnContract": turn_contract},
        interpretation={}, state="STREAMING", request_id=request_id,
        created_at=assistant_at, updated_at=now,
    )
    job = GenerationJobRecord(
        request_id=request_id, user_id=user_id, thread_id=thread_id,
        user_message_id=user_message_id, assistant_message_id=assistant_message_id,
        state="QUEUED", created_at=now, updated_at=now,
    )
    keys = [
        redis._key("job", user_id, request_id), redis._key("message", user_id, user_message_id),
        redis._key("message", user_id, assistant_message_id), redis._key("messages", user_id, thread_id),
        redis._key("activeJobs", user_id), redis._key("thread", user_id, thread_id), redis._key("threads", user_id),
    ]
    args = [
        json.dumps(asdict(job), ensure_ascii=False, separators=(",", ":")),
        json.dumps(asdict(user_message), ensure_ascii=False, separators=(",", ":")),
        json.dumps(asdict(assistant_message), ensure_ascii=False, separators=(",", ":")),
        str(user_at), str(assistant_at), request_id,
        json.dumps(asdict(thread), ensure_ascii=False, separators=(",", ":")), str(thread.updated_at), thread_id,
    ]
    result = int(redis._command("EVAL", _BEGIN_CANONICAL_TURN_LUA, len(keys), *keys, *args) or 0)
    if result == -1:
        raise ValueError("CHAT_TURN_MESSAGE_ID_CONFLICT")
    if result == 0:
        winner = redis.get_generation(user_id=user_id, request_id=request_id)
        if winner is None:
            raise DurableStoreUnavailable("canonical Redis claim lost without durable winner")
        _verify_existing(redis, winner, thread_id, user_message_id, assistant_message_id, prompt)


def _verify_existing(redis: AtomicRedisRestChatStore, job: GenerationJobRecord, thread_id: str, user_message_id: str, assistant_message_id: str, prompt: str) -> None:
    if job.thread_id != thread_id or job.user_message_id != user_message_id or job.assistant_message_id != assistant_message_id:
        raise ValueError("CHAT_TURN_REQUEST_ID_MESSAGE_CONFLICT")
    message = redis.get_message(user_id=job.user_id, message_id=user_message_id)
    if message is None or message.committed_text != prompt or message.role != "USER":
        raise ValueError("CHAT_TURN_MESSAGE_ID_CONTENT_CONFLICT")


def canonical_history(*, user_id: str, thread_id: str, request_id: str, limit: int = 32) -> list[dict[str, str]]:
    redis = store()
    history: list[dict[str, str]] = []
    for message in redis.list_messages(user_id=user_id, thread_id=thread_id):
        if message.request_id == request_id or message.role not in {"USER", "ASSISTANT"}:
            continue
        text = message.committed_text.strip()
        if not text or message.state in {"STREAMING", "FAILED", "CANCELLED"}:
            continue
        history.append({"role": message.role, "text": text[:2000]})
    return history[-max(1, min(int(limit), 32)):]


def finish_canonical_turn(*, user_id: str, request_id: str, assistant_message_id: str, text: str, terminal_type: str, reason: str, turn_contract: str) -> None:
    redis = store()
    job = redis.get_generation(user_id=user_id, request_id=request_id)
    if job is None or job.assistant_message_id != assistant_message_id:
        raise ValueError("CHAT_TURN_GENERATION_NOT_FOUND")
    assistant = redis.get_message(user_id=user_id, message_id=assistant_message_id)
    if assistant is None:
        raise DurableStoreUnavailable("canonical Redis assistant record is missing")

    terminal = str(terminal_type or "FAILED").upper()
    message_state = {"COMPLETED": "COMPLETE", "CANCELLED": "CANCELLED", "FAILED": "FAILED"}.get(terminal, "FAILED")
    job_state = {"COMPLETED": "COMPLETE", "CANCELLED": "CANCELLED", "FAILED": "FAILED"}.get(terminal, "FAILED")
    now = time.time()
    assistant = replace(
        assistant, committed_text=str(text or "")[:200000], state=message_state, updated_at=now,
        provenance={**assistant.provenance, "authority": "server", "turnContract": turn_contract,
                    "commitPhase": "TERMINAL", "terminalType": terminal, "terminalReason": str(reason or "")[:2000]},
    )
    job = replace(job, state=job_state, updated_at=now, completed_at=now)
    keys = [redis._key("job", user_id, request_id), redis._key("message", user_id, assistant_message_id), redis._key("activeJobs", user_id)]
    args = [json.dumps(asdict(assistant), ensure_ascii=False, separators=(",", ":")), json.dumps(asdict(job), ensure_ascii=False, separators=(",", ":")), request_id]
    result = int(redis._command("EVAL", _FINISH_CANONICAL_TURN_LUA, len(keys), *keys, *args) or 0)
    if result != 1:
        raise DurableStoreUnavailable("canonical Redis terminal commit failed")
