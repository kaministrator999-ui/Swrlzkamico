from __future__ import annotations

import json
import time
from dataclasses import asdict, replace
from typing import Any

from api.durable_chat_contract import (
    GenerationCreateResult,
    GenerationJobRecord,
    MessageRecord,
    new_id,
)
from api.durable_redis_store import DurableStoreUnavailable, RedisRestChatStore


_CREATE_GENERATION_LUA = r'''
-- KEYS:
-- 1 job, 2 user-message, 3 assistant-message, 4 message-index,
-- 5 active-jobs, 6 thread, 7 thread-index
-- ARGV:
-- 1 job-json, 2 user-json, 3 assistant-json, 4 user-score,
-- 5 assistant-score, 6 request-id, 7 thread-json, 8 thread-score, 9 thread-id
if redis.call('EXISTS', KEYS[1]) == 1 then
  return 0
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


class AtomicRedisRestChatStore(RedisRestChatStore):
    """Redis Chat store whose canonical generation creation is one atomic Redis transaction.

    The request-id job key is the idempotency claim. Redis executes the Lua script atomically,
    so a concurrent retry either creates the complete canonical pre-generation state or observes
    the already-created job; it cannot expose a half-created user/assistant/job tuple.
    """

    def create_generation(
        self,
        *,
        request_id: str,
        user_id: str,
        thread_id: str,
        received_text: str,
        provenance: dict[str, Any],
        interpretation: dict[str, Any],
    ) -> GenerationCreateResult:
        existing = self.get_generation(user_id=user_id, request_id=request_id)
        if existing:
            return self._existing_generation_result(user_id=user_id, job=existing)

        thread = self.get_thread(user_id=user_id, thread_id=thread_id)
        if thread is None:
            raise ValueError("thread does not exist")

        now = time.time()
        user_message = MessageRecord(
            message_id=new_id("message"),
            thread_id=thread_id,
            user_id=user_id,
            role="USER",
            received_text=received_text,
            committed_text=received_text,
            provenance=dict(provenance),
            interpretation=dict(interpretation),
            state="COMPLETE",
            request_id=request_id,
            created_at=now,
            updated_at=now,
        )
        assistant_message = MessageRecord(
            message_id=new_id("message"),
            thread_id=thread_id,
            user_id=user_id,
            role="ASSISTANT",
            received_text=None,
            committed_text="",
            state="STREAMING",
            request_id=request_id,
            created_at=now + 0.000001,
            updated_at=now,
        )
        job = GenerationJobRecord(
            request_id=request_id,
            user_id=user_id,
            thread_id=thread_id,
            user_message_id=user_message.message_id,
            assistant_message_id=assistant_message.message_id,
            state="QUEUED",
            created_at=now,
            updated_at=now,
        )
        updated_thread = replace(thread, updated_at=now)

        keys = [
            self._key("job", user_id, request_id),
            self._key("message", user_id, user_message.message_id),
            self._key("message", user_id, assistant_message.message_id),
            self._key("messages", user_id, thread_id),
            self._key("activeJobs", user_id),
            self._key("thread", user_id, thread_id),
            self._key("threads", user_id),
        ]
        args = [
            json.dumps(asdict(job), ensure_ascii=False, separators=(",", ":")),
            json.dumps(asdict(user_message), ensure_ascii=False, separators=(",", ":")),
            json.dumps(asdict(assistant_message), ensure_ascii=False, separators=(",", ":")),
            str(user_message.created_at),
            str(assistant_message.created_at),
            request_id,
            json.dumps(asdict(updated_thread), ensure_ascii=False, separators=(",", ":")),
            str(updated_thread.updated_at),
            thread_id,
        ]
        result = self._command("EVAL", _CREATE_GENERATION_LUA, len(keys), *keys, *args)
        if int(result or 0) == 1:
            return GenerationCreateResult(job, user_message, assistant_message, True)

        winner = self.get_generation(user_id=user_id, request_id=request_id)
        if winner is None:
            raise DurableStoreUnavailable("atomic generation claim lost without a durable winner")
        return self._existing_generation_result(user_id=user_id, job=winner)

    def _existing_generation_result(self, *, user_id: str, job: GenerationJobRecord) -> GenerationCreateResult:
        user_message = self.get_message(user_id=user_id, message_id=job.user_message_id)
        assistant_message = self.get_message(user_id=user_id, message_id=job.assistant_message_id)
        if not user_message or not assistant_message:
            raise DurableStoreUnavailable("atomic generation record is incomplete")
        return GenerationCreateResult(job, user_message, assistant_message, False)
