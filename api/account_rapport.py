from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any
import time

from api.durable_chat_contract import RapportControlRecord, RapportRecord

RAPPORT_KINDS = {"VOCABULARY", "CALLBACK", "CONVENTION"}
RAPPORT_SCOPES = {"GLOBAL", "PROJECT", "THREAD"}


class RapportValidationError(ValueError):
    pass


def rapport_public(record: RapportRecord) -> dict[str, Any]:
    return {
        "id": record.rapport_id,
        "kind": record.kind,
        "label": record.label,
        "cue": record.cue,
        "meaning": record.meaning,
        "preferredResponse": record.preferred_response,
        "source": record.source,
        "provenance": dict(record.provenance),
        "scope": record.scope,
        "scopeId": record.scope_id,
        "authoredBy": record.authored_by,
        "active": record.active,
        "generation": record.generation,
        "version": record.version,
        "createdAt": int(record.created_at * 1000),
        "updatedAt": int(record.updated_at * 1000),
    }


def rapport_control_public(control: RapportControlRecord) -> dict[str, Any]:
    return {
        "paused": control.paused,
        "currentGeneration": control.current_generation,
        "version": control.version,
        "updatedAt": int(control.updated_at * 1000),
        "lastResetAt": int(control.last_reset_at * 1000) if control.last_reset_at else None,
    }


def validate_rapport_fields(
    body: dict[str, Any],
    *,
    current: RapportRecord | None = None,
    default_scope_id: str | None = None,
) -> dict[str, Any]:
    kind = str(body.get("kind") if "kind" in body else (current.kind if current else "")).strip().upper()
    if kind not in RAPPORT_KINDS:
        raise RapportValidationError("unsupported rapport kind")
    label = str(body.get("label") if "label" in body else (current.label if current else "")).strip()[:120]
    cue = str(body.get("cue") if "cue" in body else (current.cue if current else "")).strip()[:500]
    meaning = str(body.get("meaning") if "meaning" in body else (current.meaning if current else "")).strip()[:4000]
    preferred_response = str(
        body.get("preferredResponse")
        if "preferredResponse" in body
        else (current.preferred_response if current else "")
    ).strip()[:4000]
    if not label or not cue or not meaning:
        raise RapportValidationError("rapport label, cue, and meaning are required")
    scope = str(body.get("scope") if "scope" in body else (current.scope if current else "GLOBAL")).strip().upper()
    if scope not in RAPPORT_SCOPES:
        raise RapportValidationError("unsupported rapport scope")
    raw_scope_id = (
        body.get("scopeId")
        if "scopeId" in body
        else (current.scope_id if current else default_scope_id)
    )
    scope_id = str(raw_scope_id or "").strip()[:160] or None
    if scope == "GLOBAL":
        scope_id = None
    elif not scope_id:
        raise RapportValidationError("scoped rapport requires scopeId")
    active = bool(body.get("active", current.active if current else True))
    return {
        "kind": kind,
        "label": label,
        "cue": cue,
        "meaning": meaning,
        "preferred_response": preferred_response,
        "scope": scope,
        "scope_id": scope_id,
        "active": active,
    }


def rapport_snapshot(record: RapportRecord | None) -> dict[str, Any]:
    return asdict(record) if record is not None else {}


def reset_rapport_generation(store, *, user_id: str, expected_version: int | None = None) -> RapportControlRecord:
    current = store.get_rapport_control(user_id=user_id)
    expected = current.version if expected_version is None else int(expected_version)
    return store.put_rapport_control(
        replace(
            current,
            current_generation=max(1, int(current.current_generation)) + 1,
            last_reset_at=time.time(),
        ),
        expected_version=expected,
    )


def set_rapport_paused(
    store,
    *,
    user_id: str,
    paused: bool,
    expected_version: int | None = None,
) -> RapportControlRecord:
    current = store.get_rapport_control(user_id=user_id)
    expected = current.version if expected_version is None else int(expected_version)
    return store.put_rapport_control(
        replace(current, paused=bool(paused)),
        expected_version=expected,
    )
