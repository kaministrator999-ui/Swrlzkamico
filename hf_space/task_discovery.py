"""Pure, provenance-gated task-effort reconciliation after source inspection.

Experimental v183 candidate ONLY. The Workstation must authenticate discovery
receipts and invoke this function with trusted=True; there is NO HTTP route or
automatic ingestion of model-, user-, or search-provided JSON. Never grants
permissions or mutates canonical state. No raw prompts, files or secrets retained.
"""
from __future__ import annotations

from typing import Any

from task_effort import SCHEMA as FIRST_HOP_SCHEMA

SCHEMA = "swrlz-task-discovery-plan-v1"
LEVELS = {1: "INSTANT", 2: "FOCUSED", 3: "STRUCTURED", 4: "DEEP", 5: "CRITICAL"}
VERIFICATION = {1: "none", 2: "proportional", 3: "targeted-evidence", 4: "cross-boundary", 5: "independent-gate"}
RISK_TAGS = frozenset({
    "authentication", "authorization", "user-data", "personal-data",
    "persistence", "schema-migration", "data-loss", "financial",
    "secrets", "production-release", "destructive", "active-credentials",
})
CRITICAL_TAGS = frozenset({"production-release", "destructive", "active-credentials", "data-loss"})


def _bounded_count(evidence: dict[str, Any], key: str) -> int:
    value = evidence.get(key)
    return min(1000, value) if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0


def _bounded_tags(evidence: dict[str, Any]) -> list[str]:
    value = evidence.get("riskTags")
    if not isinstance(value, list):
        return []
    return sorted({tag for tag in value[:64] if isinstance(tag, str) and tag in RISK_TAGS})


def reconcile_after_discovery(
    first_hop: dict[str, Any],
    evidence: dict[str, Any] | None = None,
    *,
    trusted: bool = False,
) -> dict[str, Any]:
    """Escalate effort, never silently downgrade risk or authorize any action.

    trusted=True must come from an authoritative Workstation calling context,
    not an end-user or model flag inside evidence. This function itself cannot
    prove trust; it is deliberately NOT exposed as an HTTP endpoint.
    """
    if not isinstance(first_hop, dict) or first_hop.get("schema") != FIRST_HOP_SCHEMA:
        raise ValueError("An actual versioned first-hop effort plan is required")
    level = first_hop.get("tier")
    if not isinstance(level, int) or isinstance(level, bool) or not 1 <= level <= 5:
        raise ValueError("First-hop effort tier must be an integer 1..5")
    original = level
    reasons: list[str] = []
    safe_summary: dict[str, Any] = {}
    evidence_state = "UNVERIFIED_NOT_APPLIED"

    if trusted and isinstance(evidence, dict):
        evidence_state = "VERIFIED_BY_CALLER"
        files = _bounded_count(evidence, "affectedFiles")
        owners = _bounded_count(evidence, "affectedOwners")
        edges = _bounded_count(evidence, "dependencyEdges")
        failures = _bounded_count(evidence, "failingTests")
        tags = _bounded_tags(evidence)
        safe_summary = {
            "affectedFiles": files, "affectedOwners": owners,
            "dependencyEdges": edges, "failingTests": failures,
            "riskTags": tags,
        }

        def raise_to(tier: int, code: str) -> None:
            nonlocal level
            level = max(level, tier)
            if code not in reasons:
                reasons.append(code)

        if files >= 3 or edges >= 2 or failures:
            raise_to(3, "verified-scope-or-test-evidence")
        if files >= 6 or owners >= 2 or edges >= 5:
            raise_to(4, "verified-cross-boundary-impact")
        if tags:
            raise_to(4, "verified-sensitive-state-boundary")
        if "schema-migration" in tags and "production-release" in tags:
            raise_to(5, "verified-live-migration")
        if any(tag in CRITICAL_TAGS for tag in tags):
            raise_to(5, "verified-privileged-or-destructive-impact")

    return {
        "schema": SCHEMA, "initialTier": original, "tier": level,
        "level": LEVELS[level], "escalated": level > original,
        "evidenceState": evidence_state, "evidenceSummary": safe_summary,
        "reasonCodes": reasons[:8] or ["first-hop-tier-preserved"],
        "verification": VERIFICATION[level],
        "priorityHint": "short" if level <= 2 else "normal" if level == 3 else "heavy",
        "needsEvidence": level >= 3,
        "requiresAuthorization": bool(first_hop.get("requiresAuthorization")) or level == 5,
        "automaticToolPermission": False,
    }
