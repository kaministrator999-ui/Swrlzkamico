from __future__ import annotations

from typing import Any

from api.account_proposals import submit_ai_proposal

SIGNAL_TYPE = "ACCOUNT_PROPOSAL"
SIGNAL_CONTRACT = "swrlz-account-proposal-signal-v1"
_ALLOWED_FIELDS = {"category", "targetKind", "operation", "payload", "rationale", "risk", "targetId"}
_REQUIRED_FIELDS = {"category", "targetKind", "operation", "payload", "rationale"}


class StructuredProposalSignalError(ValueError):
    pass


def is_structured_proposal_event(raw: Any) -> bool:
    return (
        isinstance(raw, dict)
        and str(raw.get("type") or "").upper() == SIGNAL_TYPE
        and str(raw.get("contract") or "") == SIGNAL_CONTRACT
    )


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
    proposal = _proposal_object(raw)
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
    )
    saved = result.get("proposal")
    return {
        "contract": SIGNAL_CONTRACT,
        "decision": str(result.get("decision") or "ASK"),
        "proposalId": str(getattr(saved, "proposal_id", "") or ""),
        "state": str(getattr(saved, "state", "") or ""),
        "category": str(proposal.get("category") or "").upper(),
        "operation": str(proposal.get("operation") or "").upper(),
        "risk": str(proposal.get("risk") or "MEDIUM").upper(),
        "version": int(getattr(saved, "version", 0) or 0),
    }
