from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Iterable, Literal, Protocol
import time
import uuid

MessageRole = Literal["USER", "ASSISTANT", "SYSTEM"]
MessageState = Literal["COMMITTED", "STREAMING", "COMPLETE", "FAILED", "CANCELLED"]
JobState = Literal["QUEUED", "RUNNING", "COMPLETE", "FAILED", "CANCELLED"]


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


@dataclass(frozen=True)
class UserRecord:
    user_id: str
    created_at: float
    updated_at: float


@dataclass(frozen=True)
class UserIdentityRecord:
    user_id: str
    provider: str
    provider_subject: str
    email: str | None = None
    email_verified: bool = False
    claims_updated_at: float | None = None


@dataclass(frozen=True)
class UserProfileRecord:
    user_id: str
    display_name: str | None = None
    preferences: dict[str, Any] = field(default_factory=dict)
    model_preferences: dict[str, Any] = field(default_factory=dict)
    ui_preferences: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    updated_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ThreadRecord:
    thread_id: str
    user_id: str
    title: str
    created_at: float
    updated_at: float
    archived_at: float | None = None


@dataclass(frozen=True)
class MessageRecord:
    message_id: str
    thread_id: str
    user_id: str
    role: MessageRole
    received_text: str | None
    committed_text: str
    provenance: dict[str, Any] = field(default_factory=dict)
    interpretation: dict[str, Any] = field(default_factory=dict)
    state: MessageState = "COMMITTED"
    request_id: str | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class GenerationJobRecord:
    request_id: str
    user_id: str
    thread_id: str
    user_message_id: str
    assistant_message_id: str
    state: JobState
    last_seq: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    completed_at: float | None = None


@dataclass(frozen=True)
class GenerationEventRecord:
    request_id: str
    user_id: str
    seq: int
    event_type: str
    payload: dict[str, Any]
    created_at: float = field(default_factory=time.time)


@dataclass(frozen=True)
class GenerationCreateResult:
    job: GenerationJobRecord
    user_message: MessageRecord
    assistant_message: MessageRecord
    created: bool


class DurableChatStore(Protocol):
    """Authoritative per-user state boundary.

    Implementations must be durable across process/instance replacement. `/tmp`, module globals,
    browser localStorage, and in-memory dictionaries do not satisfy this protocol for production.
    """

    def resolve_identity(
        self,
        *,
        provider: str,
        provider_subject: str,
        email: str | None,
        email_verified: bool,
    ) -> tuple[UserRecord, UserIdentityRecord]: ...

    def get_profile(self, *, user_id: str) -> UserProfileRecord: ...
    def put_profile(self, profile: UserProfileRecord, *, expected_version: int | None = None) -> UserProfileRecord: ...

    def list_threads(self, *, user_id: str, include_archived: bool = False) -> list[ThreadRecord]: ...
    def get_thread(self, *, user_id: str, thread_id: str) -> ThreadRecord | None: ...
    def put_thread(self, thread: ThreadRecord) -> ThreadRecord: ...

    def list_messages(self, *, user_id: str, thread_id: str, after_message_id: str | None = None) -> list[MessageRecord]: ...
    def get_message(self, *, user_id: str, message_id: str) -> MessageRecord | None: ...
    def put_message(self, message: MessageRecord) -> MessageRecord: ...

    def create_generation(
        self,
        *,
        request_id: str,
        user_id: str,
        thread_id: str,
        received_text: str,
        provenance: dict[str, Any],
        interpretation: dict[str, Any],
    ) -> GenerationCreateResult: ...

    def get_generation(self, *, user_id: str, request_id: str) -> GenerationJobRecord | None: ...
    def list_active_generations(self, *, user_id: str) -> list[GenerationJobRecord]: ...
    def update_generation(self, job: GenerationJobRecord) -> GenerationJobRecord: ...

    def append_generation_event(self, event: GenerationEventRecord) -> GenerationEventRecord: ...
    def replay_generation_events(self, *, user_id: str, request_id: str, after_seq: int = 0) -> list[GenerationEventRecord]: ...


class OwnershipError(PermissionError):
    pass


class ConflictError(RuntimeError):
    pass


def assert_owned(record_user_id: str, user_id: str) -> None:
    if not record_user_id or record_user_id != user_id:
        raise OwnershipError("resource is not owned by the authenticated user")


def event_from_stream(*, user_id: str, request_id: str, event: dict[str, Any]) -> GenerationEventRecord:
    seq = event.get("seq")
    if isinstance(seq, bool) or not isinstance(seq, int) or seq < 1:
        raise ValueError("stream event requires a positive integer seq")
    return GenerationEventRecord(
        request_id=request_id,
        user_id=user_id,
        seq=seq,
        event_type=str(event.get("type") or "STATUS"),
        payload=dict(event),
    )


def public_profile(profile: UserProfileRecord) -> dict[str, Any]:
    return asdict(profile)
