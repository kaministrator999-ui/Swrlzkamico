from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import asdict, replace
from typing import Any

from api.durable_chat_contract import (
    ConflictError,
    DurableChatStore,
    GenerationCreateResult,
    GenerationEventRecord,
    GenerationJobRecord,
    MessageRecord,
    ThreadRecord,
    UserIdentityRecord,
    UserProfileRecord,
    UserRecord,
    assert_owned,
    new_id,
)


class DurableStoreUnavailable(RuntimeError):
    pass


def _loads_record(cls, raw: str | bytes | None):
    if raw is None:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    value = json.loads(raw)
    return cls(**value)


class RedisRestChatStore(DurableChatStore):
    """Durable Redis-compatible REST implementation.

    Expected environment variables:
      SWRLZ_REDIS_REST_URL
      SWRLZ_REDIS_REST_TOKEN

    The implementation uses ordinary Redis commands over the provider REST boundary and never
    treats Vercel /tmp or process memory as authoritative user state.
    """

    def __init__(self, url: str, token: str, *, prefix: str = "swrlz:v1") -> None:
        self.url = url.rstrip("/")
        self.token = token.strip()
        self.prefix = prefix.strip(":")
        if not self.url.startswith("https://") or not self.token:
            raise DurableStoreUnavailable("durable Redis REST configuration is incomplete")

    @classmethod
    def from_env(cls) -> "RedisRestChatStore":
        return cls(
            os.environ.get("SWRLZ_REDIS_REST_URL", "").strip(),
            os.environ.get("SWRLZ_REDIS_REST_TOKEN", "").strip(),
            prefix=os.environ.get("SWRLZ_REDIS_PREFIX", "swrlz:v1").strip() or "swrlz:v1",
        )

    @classmethod
    def configured(cls) -> bool:
        return bool(os.environ.get("SWRLZ_REDIS_REST_URL", "").strip() and os.environ.get("SWRLZ_REDIS_REST_TOKEN", "").strip())

    def _key(self, *parts: str) -> str:
        return ":".join([self.prefix, *[str(p).replace(":", "_") for p in parts]])

    def _command(self, *command: Any) -> Any:
        request = urllib.request.Request(
            self.url,
            data=json.dumps(list(command), ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "swrlz-durable-chat/1",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                payload = json.loads(response.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise DurableStoreUnavailable(f"durable Redis REST request failed: {type(exc).__name__}") from exc
        if not isinstance(payload, dict) or payload.get("error"):
            raise DurableStoreUnavailable(str(payload.get("error") if isinstance(payload, dict) else "invalid Redis REST response"))
        return payload.get("result")

    def _set_json(self, key: str, value: Any) -> None:
        self._command("SET", key, json.dumps(asdict(value), ensure_ascii=False, separators=(",", ":")))

    def _get_json(self, key: str, cls):
        return _loads_record(cls, self._command("GET", key))

    def resolve_identity(self, *, provider: str, provider_subject: str, email: str | None, email_verified: bool) -> tuple[UserRecord, UserIdentityRecord]:
        provider = provider.lower().strip()
        subject = provider_subject.strip()
        if not provider or not subject:
            raise ValueError("provider and provider_subject are required")
        identity_key = self._key("identity", provider, subject)
        existing_user_id = self._command("GET", identity_key)
        now = time.time()
        if existing_user_id:
            user_id = str(existing_user_id)
            user = self._get_json(self._key("user", user_id), UserRecord)
            if user is None:
                raise DurableStoreUnavailable("identity points to a missing user record")
            user = replace(user, updated_at=now)
        else:
            user_id = new_id("user")
            claimed = self._command("SET", identity_key, user_id, "NX")
            if claimed is None:
                user_id = str(self._command("GET", identity_key))
                user = self._get_json(self._key("user", user_id), UserRecord)
                if user is None:
                    raise DurableStoreUnavailable("identity race resolved to a missing user")
            else:
                user = UserRecord(user_id=user_id, created_at=now, updated_at=now)
        self._set_json(self._key("user", user.user_id), user)
        identity = UserIdentityRecord(
            user_id=user.user_id,
            provider=provider,
            provider_subject=subject,
            email=email,
            email_verified=bool(email_verified),
            claims_updated_at=now,
        )
        self._set_json(self._key("userIdentity", user.user_id, provider), identity)
        if self._command("EXISTS", self._key("profile", user.user_id)) != 1:
            self._set_json(self._key("profile", user.user_id), UserProfileRecord(user_id=user.user_id))
        return user, identity

    def get_profile(self, *, user_id: str) -> UserProfileRecord:
        profile = self._get_json(self._key("profile", user_id), UserProfileRecord)
        if profile is None:
            profile = UserProfileRecord(user_id=user_id)
            self._set_json(self._key("profile", user_id), profile)
        return profile

    def put_profile(self, profile: UserProfileRecord, *, expected_version: int | None = None) -> UserProfileRecord:
        current = self.get_profile(user_id=profile.user_id)
        if expected_version is not None and current.version != expected_version:
            raise ConflictError("profile version changed")
        next_profile = replace(profile, version=current.version + 1, updated_at=time.time())
        self._set_json(self._key("profile", profile.user_id), next_profile)
        return next_profile

    def list_threads(self, *, user_id: str, include_archived: bool = False) -> list[ThreadRecord]:
        ids = self._command("ZRANGE", self._key("threads", user_id), 0, -1, "REV") or []
        out: list[ThreadRecord] = []
        for thread_id in ids:
            record = self.get_thread(user_id=user_id, thread_id=str(thread_id))
            if record and (include_archived or record.archived_at is None):
                out.append(record)
        return out

    def get_thread(self, *, user_id: str, thread_id: str) -> ThreadRecord | None:
        record = self._get_json(self._key("thread", user_id, thread_id), ThreadRecord)
        if record:
            assert_owned(record.user_id, user_id)
        return record

    def put_thread(self, thread: ThreadRecord) -> ThreadRecord:
        assert_owned(thread.user_id, thread.user_id)
        self._set_json(self._key("thread", thread.user_id, thread.thread_id), thread)
        self._command("ZADD", self._key("threads", thread.user_id), float(thread.updated_at), thread.thread_id)
        return thread

    def list_messages(self, *, user_id: str, thread_id: str, after_message_id: str | None = None) -> list[MessageRecord]:
        thread = self.get_thread(user_id=user_id, thread_id=thread_id)
        if thread is None:
            return []
        ids = self._command("ZRANGE", self._key("messages", user_id, thread_id), 0, -1) or []
        out: list[MessageRecord] = []
        passed = after_message_id is None
        for message_id in ids:
            mid = str(message_id)
            if not passed:
                if mid == after_message_id:
                    passed = True
                continue
            record = self.get_message(user_id=user_id, message_id=mid)
            if record and record.thread_id == thread_id:
                out.append(record)
        return out

    def get_message(self, *, user_id: str, message_id: str) -> MessageRecord | None:
        record = self._get_json(self._key("message", user_id, message_id), MessageRecord)
        if record:
            assert_owned(record.user_id, user_id)
        return record

    def put_message(self, message: MessageRecord) -> MessageRecord:
        assert_owned(message.user_id, message.user_id)
        self._set_json(self._key("message", message.user_id, message.message_id), message)
        self._command("ZADD", self._key("messages", message.user_id, message.thread_id), float(message.created_at), message.message_id)
        return message

    def create_generation(self, *, request_id: str, user_id: str, thread_id: str, received_text: str, provenance: dict[str, Any], interpretation: dict[str, Any]) -> GenerationCreateResult:
        existing = self.get_generation(user_id=user_id, request_id=request_id)
        if existing:
            user_message = self.get_message(user_id=user_id, message_id=existing.user_message_id)
            assistant_message = self.get_message(user_id=user_id, message_id=existing.assistant_message_id)
            if not user_message or not assistant_message:
                raise DurableStoreUnavailable("generation record is incomplete")
            return GenerationCreateResult(existing, user_message, assistant_message, False)
        thread = self.get_thread(user_id=user_id, thread_id=thread_id)
        if thread is None:
            raise ValueError("thread does not exist")
        now = time.time()
        user_message = MessageRecord(
            message_id=new_id("message"), thread_id=thread_id, user_id=user_id, role="USER",
            received_text=received_text, committed_text=received_text, provenance=dict(provenance), interpretation=dict(interpretation),
            state="COMPLETE", request_id=request_id, created_at=now, updated_at=now,
        )
        assistant_message = MessageRecord(
            message_id=new_id("message"), thread_id=thread_id, user_id=user_id, role="ASSISTANT",
            received_text=None, committed_text="", state="STREAMING", request_id=request_id,
            created_at=now + 0.000001, updated_at=now,
        )
        job = GenerationJobRecord(
            request_id=request_id, user_id=user_id, thread_id=thread_id,
            user_message_id=user_message.message_id, assistant_message_id=assistant_message.message_id,
            state="QUEUED", created_at=now, updated_at=now,
        )
        self.put_message(user_message)
        self.put_message(assistant_message)
        self._set_json(self._key("job", user_id, request_id), job)
        self._command("SADD", self._key("activeJobs", user_id), request_id)
        self.put_thread(replace(thread, updated_at=now))
        return GenerationCreateResult(job, user_message, assistant_message, True)

    def get_generation(self, *, user_id: str, request_id: str) -> GenerationJobRecord | None:
        record = self._get_json(self._key("job", user_id, request_id), GenerationJobRecord)
        if record:
            assert_owned(record.user_id, user_id)
        return record

    def list_active_generations(self, *, user_id: str) -> list[GenerationJobRecord]:
        ids = self._command("SMEMBERS", self._key("activeJobs", user_id)) or []
        out: list[GenerationJobRecord] = []
        for request_id in ids:
            record = self.get_generation(user_id=user_id, request_id=str(request_id))
            if record and record.state in {"QUEUED", "RUNNING"}:
                out.append(record)
            elif record:
                self._command("SREM", self._key("activeJobs", user_id), str(request_id))
        return sorted(out, key=lambda x: x.created_at)

    def update_generation(self, job: GenerationJobRecord) -> GenerationJobRecord:
        assert_owned(job.user_id, job.user_id)
        current = self.get_generation(user_id=job.user_id, request_id=job.request_id)
        if current is None:
            raise ValueError("generation does not exist")
        job = replace(job, updated_at=time.time())
        self._set_json(self._key("job", job.user_id, job.request_id), job)
        if job.state in {"COMPLETE", "FAILED", "CANCELLED"}:
            self._command("SREM", self._key("activeJobs", job.user_id), job.request_id)
        else:
            self._command("SADD", self._key("activeJobs", job.user_id), job.request_id)
        return job

    def append_generation_event(self, event: GenerationEventRecord) -> GenerationEventRecord:
        job = self.get_generation(user_id=event.user_id, request_id=event.request_id)
        if job is None:
            raise ValueError("generation does not exist")
        event_key = self._key("event", event.user_id, event.request_id, str(event.seq))
        payload = json.dumps(asdict(event), ensure_ascii=False, separators=(",", ":"))
        inserted = self._command("SET", event_key, payload, "NX")
        if inserted is not None:
            self._command("ZADD", self._key("events", event.user_id, event.request_id), event.seq, event.seq)
            if event.seq > job.last_seq:
                self.update_generation(replace(job, last_seq=event.seq))
        return event

    def replay_generation_events(self, *, user_id: str, request_id: str, after_seq: int = 0) -> list[GenerationEventRecord]:
        job = self.get_generation(user_id=user_id, request_id=request_id)
        if job is None:
            return []
        seqs = self._command("ZRANGEBYSCORE", self._key("events", user_id, request_id), f"({int(after_seq)}", "+inf") or []
        out: list[GenerationEventRecord] = []
        for seq in seqs:
            record = self._get_json(self._key("event", user_id, request_id, str(seq)), GenerationEventRecord)
            if record:
                out.append(record)
        return out
