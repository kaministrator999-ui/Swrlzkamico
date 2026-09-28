from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any
import time

from api.durable_chat_contract import (
    ConflictError,
    LoreRecord,
    ProposalAuditRecord,
    ProposalRecord,
    UserProfileRecord,
    new_id,
)

POLICY_MODES = {"ASK", "AUTO_LOW_RISK", "SESSION_ONLY", "NEVER"}
PROPOSAL_CATEGORIES = {
    "USER_PROFILE",
    "COMPANION_PROFILE",
    "USER_FACT",
    "USER_LORE",
    "COMPANION_SELF_LORE",
    "SHARED_LORE",
}
PROFILE_STYLE_VALUES = {
    "communicationStyle": {"adaptive", "direct", "collaborative", "technical", "playful"},
    "outputStyle": {"adaptive", "compact", "structured", "deep"},
}
COMPANION_ENUM_VALUES = {
    "warmth": {"adaptive", "low", "medium", "high"},
    "directness": {"adaptive", "gentle", "direct", "very-direct"},
    "humor": {"adaptive", "low", "medium", "high"},
    "loreDensity": {"adaptive", "minimal", "balanced", "mythic"},
}
AUTO_LOW_RISK_OPERATIONS = {"USER_PROFILE_PATCH", "COMPANION_PROFILE_PATCH", "LORE_CREATE", "LORE_UPDATE"}


class ProposalPolicyError(ValueError):
    pass


class ProposalStateError(RuntimeError):
    pass


def normalized_policy_map(profile: UserProfileRecord) -> dict[str, str]:
    prefs = profile.preferences if isinstance(profile.preferences, dict) else {}
    raw = prefs.get("proposalPolicy") if isinstance(prefs.get("proposalPolicy"), dict) else {}
    return {
        category: (str(raw.get(category) or "ASK").upper() if str(raw.get(category) or "ASK").upper() in POLICY_MODES else "ASK")
        for category in sorted(PROPOSAL_CATEGORIES)
    }


def proposal_public(proposal: ProposalRecord) -> dict[str, Any]:
    return {
        "id": proposal.proposal_id,
        "category": proposal.category,
        "targetKind": proposal.target_kind,
        "targetId": proposal.target_id,
        "operation": proposal.operation,
        "payload": dict(proposal.payload),
        "rationale": proposal.rationale,
        "risk": proposal.risk,
        "sourceThreadId": proposal.source_thread_id,
        "sourceRequestId": proposal.source_request_id,
        "createdBy": proposal.created_by,
        "state": proposal.state,
        "targetVersion": proposal.target_version,
        "beforeSnapshot": dict(proposal.before_snapshot),
        "afterSnapshot": dict(proposal.after_snapshot),
        "version": proposal.version,
        "createdAt": int(proposal.created_at * 1000),
        "updatedAt": int(proposal.updated_at * 1000),
        "resolvedAt": int(proposal.resolved_at * 1000) if proposal.resolved_at else None,
    }


def audit_public(event: ProposalAuditRecord) -> dict[str, Any]:
    return {
        "proposalId": event.proposal_id,
        "seq": event.seq,
        "action": event.action,
        "actor": event.actor,
        "details": dict(event.details),
        "createdAt": int(event.created_at * 1000),
    }


def _audit(store, proposal: ProposalRecord, action: str, actor: str, details: dict[str, Any] | None = None) -> ProposalAuditRecord:
    return store.append_proposal_audit(
        ProposalAuditRecord(
            proposal_id=proposal.proposal_id,
            user_id=proposal.user_id,
            seq=0,
            action=action,
            actor=actor,
            details=dict(details or {}),
        )
    )


def _bounded_text(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _validate_category_operation(category: str, target_kind: str, operation: str) -> None:
    category = category.upper()
    target_kind = target_kind.upper()
    operation = operation.upper()
    if category not in PROPOSAL_CATEGORIES:
        raise ProposalPolicyError("unsupported proposal category")
    if operation == "USER_PROFILE_PATCH":
        if category != "USER_PROFILE" or target_kind != "USER_PROFILE":
            raise ProposalPolicyError("user profile proposal target mismatch")
        return
    if operation == "COMPANION_PROFILE_PATCH":
        if category != "COMPANION_PROFILE" or target_kind != "COMPANION_PROFILE":
            raise ProposalPolicyError("companion profile proposal target mismatch")
        return
    if operation in {"LORE_CREATE", "LORE_UPDATE", "LORE_DELETE"}:
        if target_kind != "LORE" or category not in {"USER_FACT", "USER_LORE", "COMPANION_SELF_LORE", "SHARED_LORE"}:
            raise ProposalPolicyError("lore proposal target mismatch")
        return
    raise ProposalPolicyError("unsupported proposal operation")


def _validate_user_profile_patch(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {"displayName", "pronouns", "role", "communicationStyle", "outputStyle"}
    patch = {key: payload[key] for key in allowed if key in payload}
    if not patch:
        raise ProposalPolicyError("user profile proposal has no supported fields")
    if "displayName" in patch:
        patch["displayName"] = _bounded_text(patch["displayName"], 120)
    if "pronouns" in patch:
        patch["pronouns"] = _bounded_text(patch["pronouns"], 80)
    if "role" in patch:
        patch["role"] = _bounded_text(patch["role"], 160)
    for key, values in PROFILE_STYLE_VALUES.items():
        if key in patch:
            value = str(patch[key] or "").strip()
            if value not in values:
                raise ProposalPolicyError(f"unsupported {key}")
            patch[key] = value
    return patch


def _validate_companion_patch(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {"name", "title", "form", "pronouns", "warmth", "directness", "humor", "loreDensity"}
    patch = {key: payload[key] for key in allowed if key in payload}
    if not patch:
        raise ProposalPolicyError("companion proposal has no supported fields")
    for key, limit in {"name": 120, "title": 160, "form": 120, "pronouns": 80}.items():
        if key in patch:
            patch[key] = _bounded_text(patch[key], limit)
    for key, values in COMPANION_ENUM_VALUES.items():
        if key in patch:
            value = str(patch[key] or "").strip()
            if value not in values:
                raise ProposalPolicyError(f"unsupported companion {key}")
            patch[key] = value
    return patch


def _lore_type_for_category(category: str) -> str:
    return {
        "USER_FACT": "USER_FACT",
        "USER_LORE": "USER_LORE",
        "COMPANION_SELF_LORE": "COMPANION_SELF_LORE",
        "SHARED_LORE": "SHARED_LORE",
    }[category]


def _validate_lore_payload(category: str, payload: dict[str, Any], *, current: LoreRecord | None = None) -> dict[str, Any]:
    title = _bounded_text(payload.get("title") if "title" in payload else (current.title if current else ""), 120)
    content = _bounded_text(payload.get("content") if "content" in payload else (current.content if current else ""), 24000)
    if not title or not content:
        raise ProposalPolicyError("lore proposal requires title and content")
    scope = str(payload.get("scope") if "scope" in payload else (current.scope if current else "GLOBAL")).upper()
    if scope not in {"GLOBAL", "PROJECT", "THREAD"}:
        raise ProposalPolicyError("unsupported lore scope")
    scope_id_raw = payload.get("scopeId") if "scopeId" in payload else (current.scope_id if current else None)
    scope_id = _bounded_text(scope_id_raw, 160) or None
    if scope == "GLOBAL":
        scope_id = None
    elif not scope_id:
        raise ProposalPolicyError("scoped lore proposal requires scopeId")
    active = bool(payload.get("active", current.active if current else True))
    return {
        "title": title,
        "content": content,
        "lore_type": _lore_type_for_category(category),
        "scope": scope,
        "scope_id": scope_id,
        "active": active,
    }


def _current_target_version(store, *, user_id: str, operation: str, target_id: str | None) -> int:
    if operation in {"USER_PROFILE_PATCH", "COMPANION_PROFILE_PATCH"}:
        return int(store.get_profile(user_id=user_id).version)
    if operation == "LORE_CREATE":
        return 0
    if not target_id:
        raise ProposalPolicyError("lore update/delete requires target id")
    lore = store.get_lore(user_id=user_id, lore_id=target_id)
    if lore is None:
        raise ProposalPolicyError("lore proposal target does not exist")
    return int(lore.version)


def _normalize_payload(store, *, user_id: str, category: str, operation: str, target_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    if operation == "USER_PROFILE_PATCH":
        return _validate_user_profile_patch(payload)
    if operation == "COMPANION_PROFILE_PATCH":
        return _validate_companion_patch(payload)
    current = None
    if operation in {"LORE_UPDATE", "LORE_DELETE"}:
        if not target_id:
            raise ProposalPolicyError("lore target id is required")
        current = store.get_lore(user_id=user_id, lore_id=target_id)
        if current is None:
            raise ProposalPolicyError("lore target does not exist")
        if current.lore_type != _lore_type_for_category(category):
            raise ProposalPolicyError("proposal category does not match lore target")
    if operation == "LORE_DELETE":
        return {}
    return _validate_lore_payload(category, payload, current=current)


def submit_ai_proposal(
    store,
    *,
    user_id: str,
    category: str,
    target_kind: str,
    operation: str,
    payload: dict[str, Any],
    rationale: str,
    risk: str = "MEDIUM",
    target_id: str | None = None,
    source_thread_id: str | None = None,
    source_request_id: str | None = None,
) -> dict[str, Any]:
    """Trusted server-side proposal entrypoint.

    This is intentionally not exposed as a browser POST route. LALM/tool code may call it
    after it has an authenticated account user_id. The configured policy decides whether
    durable proposal state is created or a low-risk proposal is auto-applied.
    """
    category = str(category or "").upper()
    target_kind = str(target_kind or "").upper()
    operation = str(operation or "").upper()
    risk = str(risk or "MEDIUM").upper()
    if risk not in {"LOW", "MEDIUM", "HIGH"}:
        raise ProposalPolicyError("unsupported proposal risk")
    _validate_category_operation(category, target_kind, operation)
    clean_payload = _normalize_payload(
        store,
        user_id=user_id,
        category=category,
        operation=operation,
        target_id=target_id,
        payload=dict(payload or {}),
    )
    profile = store.get_profile(user_id=user_id)
    policy = normalized_policy_map(profile)[category]
    if policy == "NEVER":
        return {"decision": "NEVER", "proposal": None}
    if policy == "SESSION_ONLY":
        return {"decision": "SESSION_ONLY", "proposal": None}
    target_version = _current_target_version(store, user_id=user_id, operation=operation, target_id=target_id)
    proposal = ProposalRecord(
        proposal_id=new_id("proposal"),
        user_id=user_id,
        category=category,
        target_kind=target_kind,
        target_id=target_id,
        operation=operation,
        payload=clean_payload,
        rationale=_bounded_text(rationale, 4000),
        risk=risk,
        target_version=target_version,
        source_thread_id=_bounded_text(source_thread_id, 160) or None,
        source_request_id=_bounded_text(source_request_id, 160) or None,
        created_by="ASSISTANT",
        state="PENDING",
    )
    proposal = store.put_proposal(proposal, expected_version=0)
    _audit(store, proposal, "CREATED", "ASSISTANT", {"policy": policy, "risk": risk, "operation": operation, "category": category})
    if policy == "AUTO_LOW_RISK" and risk == "LOW" and operation in AUTO_LOW_RISK_OPERATIONS:
        applied = apply_proposal(store, user_id=user_id, proposal_id=proposal.proposal_id, actor="SYSTEM", auto=True)
        return {"decision": "AUTO_APPLIED", "proposal": applied}
    return {"decision": "ASK", "proposal": proposal}


def edit_proposal(
    store,
    *,
    user_id: str,
    proposal_id: str,
    payload: dict[str, Any],
    rationale: str | None = None,
    expected_version: int | None = None,
) -> ProposalRecord:
    current = store.get_proposal(user_id=user_id, proposal_id=proposal_id)
    if current is None:
        raise ProposalStateError("proposal does not exist")
    if current.state != "PENDING":
        raise ProposalStateError("only pending proposals can be edited")
    clean_payload = _normalize_payload(
        store,
        user_id=user_id,
        category=current.category,
        operation=current.operation,
        target_id=current.target_id,
        payload=dict(payload or {}),
    )
    saved = store.put_proposal(
        replace(
            current,
            payload=clean_payload,
            rationale=_bounded_text(rationale, 4000) if rationale is not None else current.rationale,
        ),
        expected_version=current.version if expected_version is None else expected_version,
    )
    _audit(store, saved, "EDITED", "USER", {"version": saved.version, "fields": sorted(clean_payload.keys())})
    return saved


def _profile_snapshot(profile: UserProfileRecord, *, companion: bool) -> dict[str, Any]:
    if companion:
        return {"version": profile.version, "companionProfile": dict(profile.companion_profile)}
    user_profile = profile.preferences.get("profile") if isinstance(profile.preferences, dict) and isinstance(profile.preferences.get("profile"), dict) else {}
    return {
        "version": profile.version,
        "displayName": profile.display_name,
        "profile": dict(user_profile),
    }


def _apply_user_profile(store, proposal: ProposalRecord) -> tuple[dict[str, Any], dict[str, Any]]:
    current = store.get_profile(user_id=proposal.user_id)
    if proposal.target_version is not None and current.version != proposal.target_version:
        raise ConflictError("proposal target version conflict")
    patch = _validate_user_profile_patch(proposal.payload)
    before = _profile_snapshot(current, companion=False)
    prefs = dict(current.preferences)
    profile_values = dict(prefs.get("profile") if isinstance(prefs.get("profile"), dict) else {})
    for key in ("pronouns", "role", "communicationStyle", "outputStyle"):
        if key in patch:
            profile_values[key] = patch[key]
    prefs["profile"] = profile_values
    saved = store.put_profile(
        replace(
            current,
            display_name=patch.get("displayName", current.display_name),
            preferences=prefs,
        ),
        expected_version=current.version,
    )
    return before, _profile_snapshot(saved, companion=False)


def _apply_companion_profile(store, proposal: ProposalRecord) -> tuple[dict[str, Any], dict[str, Any]]:
    current = store.get_profile(user_id=proposal.user_id)
    if proposal.target_version is not None and current.version != proposal.target_version:
        raise ConflictError("proposal target version conflict")
    patch = _validate_companion_patch(proposal.payload)
    before = _profile_snapshot(current, companion=True)
    companion = dict(current.companion_profile)
    companion.update(patch)
    saved = store.put_profile(replace(current, companion_profile=companion), expected_version=current.version)
    return before, _profile_snapshot(saved, companion=True)


def _lore_snapshot(record: LoreRecord | None) -> dict[str, Any]:
    return asdict(record) if record is not None else {}


def _apply_lore(store, proposal: ProposalRecord) -> tuple[dict[str, Any], dict[str, Any]]:
    if proposal.operation == "LORE_CREATE":
        fields = _validate_lore_payload(proposal.category, proposal.payload)
        lore_id = proposal.target_id or new_id("lore")
        if store.get_lore(user_id=proposal.user_id, lore_id=lore_id) is not None:
            raise ConflictError("proposal lore create target already exists")
        now = time.time()
        created = store.put_lore(
            LoreRecord(
                lore_id=lore_id,
                user_id=proposal.user_id,
                title=fields["title"],
                content=fields["content"],
                lore_type=fields["lore_type"],
                source="assistant-proposal-approved",
                provenance={
                    "kind": "assistant-proposal",
                    "proposalId": proposal.proposal_id,
                    "sourceThreadId": proposal.source_thread_id,
                    "sourceRequestId": proposal.source_request_id,
                },
                confidence=1.0,
                scope=fields["scope"],
                scope_id=fields["scope_id"],
                authored_by="ASSISTANT",
                editable=True,
                active=fields["active"],
                version=1,
                created_at=now,
                updated_at=now,
            ),
            expected_version=0,
        )
        return {}, _lore_snapshot(created)
    if not proposal.target_id:
        raise ProposalPolicyError("lore proposal requires target id")
    current = store.get_lore(user_id=proposal.user_id, lore_id=proposal.target_id)
    if current is None:
        raise ConflictError("proposal lore target missing")
    if proposal.target_version is not None and current.version != proposal.target_version:
        raise ConflictError("proposal target version conflict")
    before = _lore_snapshot(current)
    if proposal.operation == "LORE_DELETE":
        store.delete_lore(user_id=proposal.user_id, lore_id=current.lore_id, expected_version=current.version)
        return before, {}
    fields = _validate_lore_payload(proposal.category, proposal.payload, current=current)
    saved = store.put_lore(
        replace(
            current,
            title=fields["title"],
            content=fields["content"],
            lore_type=fields["lore_type"],
            scope=fields["scope"],
            scope_id=fields["scope_id"],
            active=fields["active"],
        ),
        expected_version=current.version,
    )
    return before, _lore_snapshot(saved)


def apply_proposal(store, *, user_id: str, proposal_id: str, actor: str = "USER", auto: bool = False) -> ProposalRecord:
    current = store.get_proposal(user_id=user_id, proposal_id=proposal_id)
    if current is None:
        raise ProposalStateError("proposal does not exist")
    if current.state != "PENDING":
        raise ProposalStateError("proposal is not pending")
    try:
        if current.operation == "USER_PROFILE_PATCH":
            before, after = _apply_user_profile(store, current)
        elif current.operation == "COMPANION_PROFILE_PATCH":
            before, after = _apply_companion_profile(store, current)
        else:
            before, after = _apply_lore(store, current)
    except Exception as exc:
        _audit(store, current, "APPLY_FAILED", actor, {"errorType": type(exc).__name__})
        raise
    terminal = "AUTO_APPLIED" if auto else "APPLIED"
    saved = store.put_proposal(
        replace(
            current,
            state=terminal,
            before_snapshot=before,
            after_snapshot=after,
            resolved_at=time.time(),
        ),
        expected_version=current.version,
    )
    _audit(store, saved, terminal, actor, {"proposalVersion": saved.version, "targetVersion": after.get("version")})
    return saved


def decline_proposal(store, *, user_id: str, proposal_id: str, expected_version: int | None = None) -> ProposalRecord:
    current = store.get_proposal(user_id=user_id, proposal_id=proposal_id)
    if current is None:
        raise ProposalStateError("proposal does not exist")
    if current.state != "PENDING":
        raise ProposalStateError("proposal is not pending")
    saved = store.put_proposal(
        replace(current, state="DECLINED", resolved_at=time.time()),
        expected_version=current.version if expected_version is None else expected_version,
    )
    _audit(store, saved, "DECLINED", "USER", {"proposalVersion": saved.version})
    return saved


def _restore_profile(store, proposal: ProposalRecord, *, companion: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    current = store.get_profile(user_id=proposal.user_id)
    expected_after = int(proposal.after_snapshot.get("version") or -1)
    if current.version != expected_after:
        raise ConflictError("proposal revert target version conflict")
    if companion:
        before = _profile_snapshot(current, companion=True)
        restored = dict(proposal.before_snapshot.get("companionProfile") or {})
        saved = store.put_profile(replace(current, companion_profile=restored), expected_version=current.version)
        return before, _profile_snapshot(saved, companion=True)
    before = _profile_snapshot(current, companion=False)
    prefs = dict(current.preferences)
    prefs["profile"] = dict(proposal.before_snapshot.get("profile") or {})
    saved = store.put_profile(
        replace(current, display_name=proposal.before_snapshot.get("displayName"), preferences=prefs),
        expected_version=current.version,
    )
    return before, _profile_snapshot(saved, companion=False)


def _restore_lore(store, proposal: ProposalRecord) -> tuple[dict[str, Any], dict[str, Any]]:
    before_record = dict(proposal.before_snapshot or {})
    after_record = dict(proposal.after_snapshot or {})
    if proposal.operation == "LORE_CREATE":
        lore_id = str(after_record.get("lore_id") or "")
        current = store.get_lore(user_id=proposal.user_id, lore_id=lore_id) if lore_id else None
        if current is None:
            raise ConflictError("created lore record no longer exists")
        expected_version = int(after_record.get("version") or -1)
        if current.version != expected_version:
            raise ConflictError("proposal revert target version conflict")
        current_snapshot = _lore_snapshot(current)
        store.delete_lore(user_id=proposal.user_id, lore_id=lore_id, expected_version=current.version)
        return current_snapshot, {}
    if proposal.operation == "LORE_DELETE":
        lore_id = str(before_record.get("lore_id") or "")
        if not lore_id or store.get_lore(user_id=proposal.user_id, lore_id=lore_id) is not None:
            raise ConflictError("deleted lore id is unavailable for restore")
        restored = LoreRecord(**before_record)
        saved = store.put_lore(restored, expected_version=0)
        return {}, _lore_snapshot(saved)
    lore_id = str(after_record.get("lore_id") or proposal.target_id or "")
    current = store.get_lore(user_id=proposal.user_id, lore_id=lore_id) if lore_id else None
    if current is None:
        raise ConflictError("updated lore record no longer exists")
    expected_version = int(after_record.get("version") or -1)
    if current.version != expected_version:
        raise ConflictError("proposal revert target version conflict")
    current_snapshot = _lore_snapshot(current)
    restored = LoreRecord(**before_record)
    restored = replace(restored, version=current.version, updated_at=current.updated_at)
    saved = store.put_lore(restored, expected_version=current.version)
    return current_snapshot, _lore_snapshot(saved)


def revert_proposal(store, *, user_id: str, proposal_id: str) -> ProposalRecord:
    current = store.get_proposal(user_id=user_id, proposal_id=proposal_id)
    if current is None:
        raise ProposalStateError("proposal does not exist")
    if current.state not in {"APPLIED", "AUTO_APPLIED"}:
        raise ProposalStateError("only applied proposals can be reverted")
    if current.operation == "USER_PROFILE_PATCH":
        reverted_from, restored = _restore_profile(store, current, companion=False)
    elif current.operation == "COMPANION_PROFILE_PATCH":
        reverted_from, restored = _restore_profile(store, current, companion=True)
    else:
        reverted_from, restored = _restore_lore(store, current)
    saved = store.put_proposal(
        replace(current, state="REVERTED", resolved_at=time.time()),
        expected_version=current.version,
    )
    _audit(store, saved, "REVERTED", "USER", {
        "proposalVersion": saved.version,
        "revertedTargetVersion": reverted_from.get("version"),
        "restoredTargetVersion": restored.get("version"),
    })
    return saved
