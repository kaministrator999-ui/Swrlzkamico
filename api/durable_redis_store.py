from __future__ import annotations

import json
import os
import time
import requests
from dataclasses import asdict, replace
from typing import Any

from api.chat_client_debug import _lockdown as _chat_lockdown
from api.durable_chat_contract import (
    ConflictError,
    DurableChatStore,
    GenerationCreateResult,
    GenerationEventRecord,
    GenerationJobRecord,
    LoreRecord,
    MessageRecord,
    ProposalAuditRecord,
    ProposalRecord,
    RapportControlRecord,
    RapportRecord,
    ThreadRecord,
    UserIdentityRecord,
    UserProfileRecord,
    UserRecord,
    assert_owned,
    new_id,
)


_CREATE_PROPOSAL_LUA = r"""
if redis.call('EXISTS', KEYS[1]) == 1 then
  return 0
end
redis.call('SET', KEYS[1], ARGV[1])
redis.call('ZADD', KEYS[2], ARGV[2], ARGV[3])
return 1
"""

_CAS_PROPOSAL_LUA = r"""
local raw = redis.call('GET', KEYS[1])
if not raw then
  return -1
end
local current = cjson.decode(raw)
if tonumber(current.version or 0) ~= tonumber(ARGV[1]) then
  return 0
end
redis.call('SET', KEYS[1], ARGV[2])
redis.call('ZADD', KEYS[2], ARGV[3], ARGV[4])
return 1
"""


class DurableStoreUnavailable(RuntimeError):
    pass


def _loads_record(cls, raw: str | bytes | None):
    if raw is None:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    value = json.loads(raw)
    return cls(**value)


def _env_first(*names: str) -> str:
    """Return the first configured environment value without exposing it.

    SWRLZ-specific names remain authoritative overrides. Vercel/Upstash KV REST
    names are accepted as a zero-copy compatibility path so credentials do not
    need to be duplicated into additional project secrets.
    """
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


class RedisRestChatStore(DurableChatStore):
    """Durable Redis-compatible REST implementation.

    Preferred environment variables:
      SWRLZ_REDIS_REST_URL
      SWRLZ_REDIS_REST_TOKEN

    Compatible Vercel/Upstash integration variables:
      KV_REST_API_URL
      KV_REST_API_TOKEN

    SWRLZ-specific variables win when both are configured. The implementation
    uses ordinary Redis commands over the provider REST boundary and never
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
            _env_first("SWRLZ_REDIS_REST_URL", "KV_REST_API_URL"),
            _env_first("SWRLZ_REDIS_REST_TOKEN", "KV_REST_API_TOKEN"),
            prefix=os.environ.get("SWRLZ_REDIS_PREFIX", "swrlz:v1").strip() or "swrlz:v1",
        )

    @classmethod
    def configured(cls) -> bool:
        return bool(
            _env_first("SWRLZ_REDIS_REST_URL", "KV_REST_API_URL")
            and _env_first("SWRLZ_REDIS_REST_TOKEN", "KV_REST_API_TOKEN")
        )

    def _key(self, *parts: str) -> str:
        return ":".join([self.prefix, *[str(p).replace(":", "_") for p in parts]])

    def _command(self, *command: Any, sensitive: bool = False) -> Any:
        started_ns=time.perf_counter_ns()
        op=str(command[0] if command else "")[:64].upper()
        safe_command=[str(value)[:16000] for value in command]
        if sensitive:
            safe_command=[
                str(command[0])[:64] if command else "",
                str(command[1])[:512] if len(command) > 1 else "",
                *([f"[redacted:{len(str(value))} chars]" for value in command[2:]] if len(command) > 2 else []),
            ]
        _chat_lockdown("redis-command-enter", operation=op, argumentCount=len(command), command=safe_command, sensitive=sensitive)
        try:
            response=requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "User-Agent": "swrlz-durable-chat/2",
                },
                data=json.dumps(list(command), ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
                timeout=(3,15),
            )
            _chat_lockdown("redis-http-response", operation=op, durationNs=time.perf_counter_ns()-started_ns, httpStatus=response.status_code, responseBytes=len(response.content))
            response.raise_for_status()
            payload=response.json()
        except (requests.RequestException, ValueError, json.JSONDecodeError) as exc:
            _chat_lockdown("redis-command-error", operation=op, durationNs=time.perf_counter_ns()-started_ns, errorType=type(exc).__name__, error=str(exc)[:2000])
            raise DurableStoreUnavailable(f"durable Redis REST request failed: {type(exc).__name__}") from exc
        if not isinstance(payload, dict) or payload.get("error"):
            _chat_lockdown("redis-command-rejected", operation=op, durationNs=time.perf_counter_ns()-started_ns, error=str(payload.get("error") if isinstance(payload,dict) else "invalid response")[:2000])
            raise DurableStoreUnavailable(str(payload.get("error") if isinstance(payload, dict) else "invalid Redis REST response"))
        result=payload.get("result")
        if sensitive:
            if result is None:
                result_log = None
            elif isinstance(result, (list, tuple)):
                result_log = {"redacted": True, "kind": "list", "items": len(result)}
            else:
                result_log = {"redacted": True, "kind": type(result).__name__, "chars": len(str(result))}
        else:
            result_log = str(result)[:16000]
        _chat_lockdown("redis-command-exit", operation=op, durationNs=time.perf_counter_ns()-started_ns, result=result_log, sensitive=sensitive)
        return result

    def _set_json(self, key: str, value: Any, *, sensitive: bool = False) -> None:
        self._command("SET", key, json.dumps(asdict(value), ensure_ascii=False, separators=(",", ":")), sensitive=sensitive)

    def _get_json(self, key: str, cls, *, sensitive: bool = False):
        return _loads_record(cls, self._command("GET", key, sensitive=sensitive))

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
            email_verified=email_verified,
            claims_updated_at=now,
        )
        self._set_json(self._key("identity_record", provider, subject), identity)
        return user, identity

    def get_profile(self, *, user_id: str) -> UserProfileRecord:
        key = self._key("profile", user_id)
        profile = self._get_json(key, UserProfileRecord, sensitive=True)
        if profile is not None:
            assert_owned(user_id, profile.user_id)
            return profile
        profile = UserProfileRecord(user_id=user_id)
        self._set_json(key, profile, sensitive=True)
        return profile

    def get_or_create_profile(self, user_id: str) -> UserProfileRecord:
        return self.get_profile(user_id=user_id)

    def put_profile(self, profile: UserProfileRecord, *, expected_version: int | None = None) -> UserProfileRecord:
        current = self.get_profile(user_id=profile.user_id)
        if expected_version is not None and current.version != expected_version:
            raise ConflictError("profile version conflict")
        saved = replace(profile, version=current.version + 1, updated_at=time.time())
        self._set_json(self._key("profile", profile.user_id), saved, sensitive=True)
        return saved

    def get_lore(self, *, user_id: str, lore_id: str) -> LoreRecord | None:
        lore = self._get_json(self._key("lore", user_id, lore_id), LoreRecord, sensitive=True)
        if lore is not None:
            assert_owned(user_id, lore.user_id)
        return lore

    def list_lore(self, *, user_id: str, limit: int = 300) -> list[LoreRecord]:
        bounded=max(1,min(int(limit or 300),500))
        ids=self._command("ZREVRANGE", self._key("lore_index", user_id), 0, bounded - 1, sensitive=True) or []
        out: list[LoreRecord] = []
        for lore_id in ids:
            lore=self.get_lore(user_id=user_id, lore_id=str(lore_id))
            if lore is not None:
                out.append(lore)
        return out

    def put_lore(self, lore: LoreRecord, *, expected_version: int | None = None) -> LoreRecord:
        assert_owned(lore.user_id, lore.user_id)
        key=self._key("lore", lore.user_id, lore.lore_id)
        current=self.get_lore(user_id=lore.user_id, lore_id=lore.lore_id)
        now=time.time()
        if current is None:
            if expected_version not in (None, 0):
                raise ConflictError("lore version conflict")
            saved=replace(lore, version=1, created_at=now, updated_at=now)
            claimed=self._command(
                "SET",
                key,
                json.dumps(asdict(saved), ensure_ascii=False, separators=(",", ":")),
                "NX",
                sensitive=True,
            )
            if claimed is None:
                raise ConflictError("lore create conflict")
        else:
            assert_owned(lore.user_id, current.user_id)
            if expected_version is not None and current.version != expected_version:
                raise ConflictError("lore version conflict")
            saved=replace(lore, version=current.version + 1, created_at=current.created_at, updated_at=now)
            self._set_json(key, saved, sensitive=True)
        self._command("ZADD", self._key("lore_index", lore.user_id), saved.updated_at, saved.lore_id, sensitive=True)
        return saved

    def delete_lore(self, *, user_id: str, lore_id: str, expected_version: int | None = None) -> bool:
        current=self.get_lore(user_id=user_id, lore_id=lore_id)
        if current is None:
            return False
        if expected_version is not None and current.version != expected_version:
            raise ConflictError("lore version conflict")
        self._command("DEL", self._key("lore", user_id, lore_id), sensitive=True)
        self._command("ZREM", self._key("lore_index", user_id), lore_id, sensitive=True)
        return True

    def get_rapport_control(self, *, user_id: str) -> RapportControlRecord:
        key=self._key("rapport_control", user_id)
        control=self._get_json(key, RapportControlRecord, sensitive=True)
        if control is not None:
            assert_owned(user_id, control.user_id)
            return control
        control=RapportControlRecord(user_id=user_id)
        self._set_json(key, control, sensitive=True)
        return control

    def put_rapport_control(self, control: RapportControlRecord, *, expected_version: int | None = None) -> RapportControlRecord:
        current=self.get_rapport_control(user_id=control.user_id)
        if expected_version is not None and current.version != expected_version:
            raise ConflictError("rapport control version conflict")
        saved=replace(control, version=current.version + 1, updated_at=time.time())
        self._set_json(self._key("rapport_control", control.user_id), saved, sensitive=True)
        return saved

    def get_rapport(self, *, user_id: str, rapport_id: str) -> RapportRecord | None:
        record=self._get_json(self._key("rapport", user_id, rapport_id), RapportRecord, sensitive=True)
        if record is not None:
            assert_owned(user_id, record.user_id)
        return record

    def list_rapport(self, *, user_id: str, limit: int = 300, include_history: bool = False) -> list[RapportRecord]:
        bounded=max(1,min(int(limit or 300),500))
        control=self.get_rapport_control(user_id=user_id)
        ids=self._command("ZREVRANGE", self._key("rapport_index", user_id), 0, bounded - 1, sensitive=True) or []
        out: list[RapportRecord] = []
        for rapport_id in ids:
            record=self.get_rapport(user_id=user_id, rapport_id=str(rapport_id))
            if record is None:
                continue
            if include_history or record.generation == control.current_generation:
                out.append(record)
        return out

    def put_rapport(self, rapport: RapportRecord, *, expected_version: int | None = None) -> RapportRecord:
        assert_owned(rapport.user_id, rapport.user_id)
        key=self._key("rapport", rapport.user_id, rapport.rapport_id)
        current=self.get_rapport(user_id=rapport.user_id, rapport_id=rapport.rapport_id)
        now=time.time()
        if current is None:
            if expected_version not in (None, 0):
                raise ConflictError("rapport version conflict")
            saved=replace(rapport, version=1, created_at=now, updated_at=now)
            claimed=self._command(
                "SET",
                key,
                json.dumps(asdict(saved), ensure_ascii=False, separators=(",", ":")),
                "NX",
                sensitive=True,
            )
            if claimed is None:
                raise ConflictError("rapport create conflict")
        else:
            assert_owned(rapport.user_id, current.user_id)
            if expected_version is not None and current.version != expected_version:
                raise ConflictError("rapport version conflict")
            saved=replace(rapport, version=current.version + 1, created_at=current.created_at, updated_at=now)
            self._set_json(key, saved, sensitive=True)
        self._command("ZADD", self._key("rapport_index", rapport.user_id), saved.updated_at, saved.rapport_id, sensitive=True)
        return saved

    def delete_rapport(self, *, user_id: str, rapport_id: str, expected_version: int | None = None) -> bool:
        current=self.get_rapport(user_id=user_id, rapport_id=rapport_id)
        if current is None:
            return False
        if expected_version is not None and current.version != expected_version:
            raise ConflictError("rapport version conflict")
        self._command("DEL", self._key("rapport", user_id, rapport_id), sensitive=True)
        self._command("ZREM", self._key("rapport_index", user_id), rapport_id, sensitive=True)
        return True

    def get_proposal(self, *, user_id: str, proposal_id: str) -> ProposalRecord | None:
        proposal = self._get_json(self._key("proposal", user_id, proposal_id), ProposalRecord, sensitive=True)
        if proposal is not None:
            assert_owned(user_id, proposal.user_id)
        return proposal

    def list_proposals(self, *, user_id: str, limit: int = 200, include_resolved: bool = True) -> list[ProposalRecord]:
        bounded=max(1,min(int(limit or 200),500))
        ids=self._command("ZREVRANGE", self._key("proposal_index", user_id), 0, bounded - 1, sensitive=True) or []
        out: list[ProposalRecord] = []
        for proposal_id in ids:
            proposal=self.get_proposal(user_id=user_id, proposal_id=str(proposal_id))
            if proposal is None:
                continue
            if include_resolved or proposal.state == "PENDING":
                out.append(proposal)
        return out

    def put_proposal(self, proposal: ProposalRecord, *, expected_version: int | None = None) -> ProposalRecord:
        assert_owned(proposal.user_id, proposal.user_id)
        key=self._key("proposal", proposal.user_id, proposal.proposal_id)
        index_key=self._key("proposal_index", proposal.user_id)
        current=self.get_proposal(user_id=proposal.user_id, proposal_id=proposal.proposal_id)
        now=time.time()
        if current is None:
            if expected_version not in (None, 0):
                raise ConflictError("proposal version conflict")
            saved=replace(proposal, version=1, created_at=now, updated_at=now)
            claimed=int(self._command(
                "EVAL",
                _CREATE_PROPOSAL_LUA,
                2,
                key,
                index_key,
                json.dumps(asdict(saved), ensure_ascii=False, separators=(",", ":")),
                str(saved.updated_at),
                saved.proposal_id,
                sensitive=True,
            ) or 0)
            if claimed != 1:
                raise ConflictError("proposal create conflict")
            return saved
        assert_owned(proposal.user_id, current.user_id)
        expected=current.version if expected_version is None else int(expected_version)
        if current.version != expected:
            raise ConflictError("proposal version conflict")
        saved=replace(proposal, version=current.version + 1, created_at=current.created_at, updated_at=now)
        updated=int(self._command(
            "EVAL",
            _CAS_PROPOSAL_LUA,
            2,
            key,
            index_key,
            str(expected),
            json.dumps(asdict(saved), ensure_ascii=False, separators=(",", ":")),
            str(saved.updated_at),
            saved.proposal_id,
            sensitive=True,
        ) or 0)
        if updated != 1:
            raise ConflictError("proposal version conflict")
        return saved

    def append_proposal_audit(self, event: ProposalAuditRecord) -> ProposalAuditRecord:
        proposal=self.get_proposal(user_id=event.user_id, proposal_id=event.proposal_id)
        if proposal is None:
            raise DurableStoreUnavailable("proposal audit references missing proposal")
        assert_owned(event.user_id, proposal.user_id)
        seq=int(self._command("INCR", self._key("proposal_audit_seq", event.user_id, event.proposal_id), sensitive=True) or 0)
        saved=replace(event, seq=seq, created_at=time.time())
        key=self._key("proposal_audit", event.user_id, event.proposal_id, str(seq))
        self._set_json(key, saved, sensitive=True)
        self._command("ZADD", self._key("proposal_audit_index", event.user_id, event.proposal_id), seq, str(seq), sensitive=True)
        return saved

    def list_proposal_audit(self, *, user_id: str, proposal_id: str) -> list[ProposalAuditRecord]:
        proposal=self.get_proposal(user_id=user_id, proposal_id=proposal_id)
        if proposal is None:
            return []
        seqs=self._command("ZRANGE", self._key("proposal_audit_index", user_id, proposal_id), 0, -1, sensitive=True) or []
        out: list[ProposalAuditRecord] = []
        for seq in seqs:
            event=self._get_json(self._key("proposal_audit", user_id, proposal_id, str(seq)), ProposalAuditRecord, sensitive=True)
            if event is not None:
                assert_owned(user_id, event.user_id)
                out.append(event)
        return out

    def create_thread(self, thread: ThreadRecord) -> ThreadRecord:
        assert_owned(thread.user_id, thread.user_id)
        key = self._key("thread", thread.user_id, thread.thread_id)
        if self._command("SET", key, json.dumps(asdict(thread), separators=(",", ":")), "NX") is None:
            raise ConflictError("thread already exists")
        self._command("ZADD", self._key("thread_index", thread.user_id), thread.updated_at, thread.thread_id)
        return thread

    def get_thread(self, user_id: str, thread_id: str) -> ThreadRecord | None:
        thread = self._get_json(self._key("thread", user_id, thread_id), ThreadRecord)
        if thread is not None:
            assert_owned(user_id, thread.user_id)
        return thread

    def list_threads(self, user_id: str, *, limit: int = 50) -> list[ThreadRecord]:
        ids = self._command("ZREVRANGE", self._key("thread_index", user_id), 0, max(0, limit - 1)) or []
        out: list[ThreadRecord] = []
        for thread_id in ids:
            thread = self.get_thread(user_id, str(thread_id))
            if thread is not None:
                out.append(thread)
        return out

    def create_generation(self, job: GenerationJobRecord, user_message: MessageRecord, assistant_message: MessageRecord) -> GenerationCreateResult:
        assert_owned(job.user_id, user_message.user_id, assistant_message.user_id)
        assert_owned(job.thread_id, user_message.thread_id, assistant_message.thread_id)
        job_key = self._key("job", job.user_id, job.request_id)
        existing = self._get_json(job_key, GenerationJobRecord)
        if existing is not None:
            return GenerationCreateResult(job=existing, created=False)
        thread = self.get_thread(job.user_id, job.thread_id)
        if thread is None:
            raise DurableStoreUnavailable("generation references missing thread")
        user_key = self._key("message", job.user_id, user_message.message_id)
        assistant_key = self._key("message", job.user_id, assistant_message.message_id)
        if self._command("EXISTS", user_key) or self._command("EXISTS", assistant_key):
            raise ConflictError("message id already exists")
        self._set_json(user_key, user_message)
        self._command("ZADD", self._key("message_index", job.user_id, job.thread_id), user_message.created_at, user_message.message_id)
        self._set_json(assistant_key, assistant_message)
        self._command("ZADD", self._key("message_index", job.user_id, job.thread_id), assistant_message.created_at, assistant_message.message_id)
        self._set_json(job_key, job)
        self._command("SADD", self._key("active_jobs", job.user_id), job.request_id)
        thread = replace(thread, updated_at=max(thread.updated_at, user_message.created_at, assistant_message.created_at))
        self._set_json(self._key("thread", job.user_id, job.thread_id), thread)
        self._command("ZADD", self._key("thread_index", job.user_id), thread.updated_at, job.thread_id)
        return GenerationCreateResult(job=job, created=True)

    def get_generation(self, user_id: str, request_id: str) -> GenerationJobRecord | None:
        job = self._get_json(self._key("job", user_id, request_id), GenerationJobRecord)
        if job is not None:
            assert_owned(user_id, job.user_id)
        return job

    def update_generation(self, job: GenerationJobRecord) -> GenerationJobRecord:
        existing = self.get_generation(job.user_id, job.request_id)
        if existing is None:
            raise DurableStoreUnavailable("generation job does not exist")
        self._set_json(self._key("job", job.user_id, job.request_id), job)
        if str(job.state or "").upper() in {"QUEUED", "RUNNING", "STREAMING"}:
            self._command("SADD", self._key("active_jobs", job.user_id), job.request_id)
        else:
            self._command("SREM", self._key("active_jobs", job.user_id), job.request_id)
        return job

    def append_event(self, event: GenerationEventRecord) -> GenerationEventRecord:
        assert_owned(event.user_id, event.user_id)
        key = self._key("event", event.user_id, event.request_id, str(event.seq))
        if self._command("SET", key, json.dumps(asdict(event), separators=(",", ":")), "NX") is None:
            raise ConflictError("event sequence already exists")
        self._command("ZADD", self._key("event_index", event.user_id, event.request_id), event.seq, str(event.seq))
        return event

    def list_events(self, user_id: str, request_id: str, *, after_seq: int = -1) -> list[GenerationEventRecord]:
        seqs = self._command("ZRANGEBYSCORE", self._key("event_index", user_id, request_id), f"({after_seq}", "+inf") or []
        out: list[GenerationEventRecord] = []
        for seq in seqs:
            event = self._get_json(self._key("event", user_id, request_id, str(seq)), GenerationEventRecord)
            if event is not None:
                assert_owned(user_id, event.user_id)
                out.append(event)
        return out

    def update_message(self, message: MessageRecord) -> MessageRecord:
        existing = self._get_json(self._key("message", message.user_id, message.message_id), MessageRecord)
        if existing is None:
            raise DurableStoreUnavailable("message does not exist")
        assert_owned(message.user_id, existing.user_id)
        self._set_json(self._key("message", message.user_id, message.message_id), message)
        return message

    def list_messages(self, user_id: str, thread_id: str, *, limit: int = 200) -> list[MessageRecord]:
        ids = self._command("ZRANGE", self._key("message_index", user_id, thread_id), max(0, -limit), -1) or []
        out: list[MessageRecord] = []
        for message_id in ids:
            message = self._get_json(self._key("message", user_id, str(message_id)), MessageRecord)
            if message is not None:
                assert_owned(user_id, message.user_id)
                out.append(message)
        return out

    def list_active_generations(self, user_id: str) -> list[GenerationJobRecord]:
        request_ids = self._command("SMEMBERS", self._key("active_jobs", user_id)) or []
        out: list[GenerationJobRecord] = []
        for request_id in request_ids:
            job = self.get_generation(user_id, str(request_id))
            if job is not None:
                out.append(job)
        return out
