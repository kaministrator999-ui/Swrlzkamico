from __future__ import annotations

from typing import Any
import hashlib
import re

from api.account_proposals import submit_ai_proposal

SIGNAL_TYPE = "ACCOUNT_PROPOSAL"
SIGNAL_CONTRACT = "swrlz-account-proposal-signal-v1"
_ALLOWED_FIELDS = {"category", "targetKind", "operation", "payload", "rationale", "risk", "targetId"}
_REQUIRED_FIELDS = {"category", "targetKind", "operation", "payload", "rationale"}
_SIGNAL_ID = re.compile(r"^[A-Za-z0-9._:-]{1,160}$")


class StructuredProposalSignalError(ValueError):
    pass


def is_structured_proposal_event(raw: Any) -> bool:
    return (
        isinstance(raw, dict)
        and str(raw.get("type") or "").upper() == SIGNAL_TYPE
        and str(raw.get("contract") or "") == SIGNAL_CONTRACT
    )


def build_structured_proposal_event(
    *,
    signal_id: str,
    category: str,
    target_kind: str,
    operation: str,
    payload: dict[str, Any],
    rationale: str,
    risk: str = "MEDIUM",
    target_id: str | None = None,
) -> dict[str, Any]:
    """Trusted producer helper. This constructs metadata; it performs no durable write."""
    signal_id = str(signal_id or "").strip()
    if not _SIGNAL_ID.fullmatch(signal_id):
        raise StructuredProposalSignalError("structured proposal signalId is invalid")
    proposal = {
        "category": str(category or ""),
        "targetKind": str(target_kind or ""),
        "operation": str(operation or ""),
        "payload": dict(payload or {}),
        "rationale": str(rationale or ""),
        "risk": str(risk or "MEDIUM"),
    }
    if target_id:
        proposal["targetId"] = str(target_id)
    return {"type": SIGNAL_TYPE, "contract": SIGNAL_CONTRACT, "signalId": signal_id, "proposal": proposal}


def _signal_id(raw: dict[str, Any]) -> str:
    value = str(raw.get("signalId") or "").strip()
    if not _SIGNAL_ID.fullmatch(value):
        raise StructuredProposalSignalError("structured proposal signalId is required and must be a bounded identifier")
    return value


def _proposal_object(raw: dict[str, Any]) -> dict[str, Any]:
    proposal = raw.get("proposal")
    if not isinstance(proposal, dict):
        raise StructuredProposalSignalError("structured proposal signal requires a proposal object")
    unknown = sorted(set(proposal) - _ALLOWED_FIELDS)
    if unknown:
        raise StructuredProposalSignalError("structured proposal signal has unsupported fields: " + ", ".join(unknown))
    missing = sorted(key for key in _REQUIRED_FIELDS if key not in proposal)
    if missing:
        raise StructuredProposalSignalError("structured proposal signal is missing fields: " + ", ".join(missing))
    if not isinstance(proposal.get("payload"), dict):
        raise StructuredProposalSignalError("structured proposal payload must be an object")
    return proposal


def consume_structured_proposal_event(
    store,
    *,
    user_id: str,
    thread_id: str,
    request_id: str,
    raw: dict[str, Any],
) -> dict[str, Any]:
    """Consume one exact trusted engine/tool proposal signal.

    This function never inspects generated prose. Source thread/request identity comes
    from the authoritative Workstation job and cannot be overridden by signal payload.
    """
    if not is_structured_proposal_event(raw):
        raise StructuredProposalSignalError("event is not the structured proposal contract")
    signal_id = _signal_id(raw)
    proposal = _proposal_object(raw)
    stable_id = "proposal_signal_" + hashlib.sha256(f"{request_id}:{signal_id}".encode("utf-8")).hexdigest()[:32]
    result = submit_ai_proposal(
        store,
        user_id=user_id,
        category=str(proposal.get("category") or ""),
        target_kind=str(proposal.get("targetKind") or ""),
        operation=str(proposal.get("operation") or ""),
        payload=dict(proposal.get("payload") or {}),
        rationale=str(proposal.get("rationale") or ""),
        risk=str(proposal.get("risk") or "MEDIUM"),
        target_id=str(proposal.get("targetId") or "").strip() or None,
        source_thread_id=thread_id,
        source_request_id=request_id,
        proposal_id=stable_id,
    )
    saved = result.get("proposal")
    return {
        "contract": SIGNAL_CONTRACT,
        "signalId": signal_id,
        "decision": str(result.get("decision") or "ASK"),
        "proposalId": str(getattr(saved, "proposal_id", "") or ""),
        "state": str(getattr(saved, "state", "") or ""),
        "category": str(proposal.get("category") or "").upper(),
        "operation": str(proposal.get("operation") or "").upper(),
        "risk": str(proposal.get("risk") or "MEDIUM").upper(),
        "version": int(getattr(saved, "version", 0) or 0),
    }
