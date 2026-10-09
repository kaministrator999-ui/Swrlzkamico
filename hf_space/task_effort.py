"""Deterministic, bounded task-effort hints for §wyrlz; never acceptance authority.

This module performs no I/O, does not mutate caller state, and never authorizes
side effects, adds tool calls, or replaces the programming-intent owner.
"""
from __future__ import annotations

import re
from typing import Any

SCHEMA = "swrlz-task-effort-plan-v1"


def _has(text: str, expression: str) -> bool:
    return re.search(expression, text, re.IGNORECASE) is not None


def task_effort_plan(prompt: str, programming: dict[str, Any] | None = None) -> dict[str, Any]:
    """Estimate work scale and verification obligation, never model capability.

    Conservative with high-consequence changes; light for explanations and
    ordinary greetings. No numeric confidence: these are inspectable hints.
    """
    text = str(prompt or "").strip()[:32768]
    p = re.sub(r"\s+", " ", text).lower()
    coding = programming if isinstance(programming, dict) else {}
    reasons: list[str] = []
    tier = 1

    def raise_to(value: int, reason: str) -> None:
        nonlocal tier
        tier = max(tier, value)
        if reason not in reasons:
            reasons.append(reason)

    if not p:
        return {
            "schema": SCHEMA, "tier": 1, "level": "INSTANT",
            "reasonCodes": ["empty-or-whitespace"], "verification": "none",
            "priorityHint": "short", "needsEvidence": False,
            "requiresAuthorization": False, "automaticToolPermission": False,
        }

    inquiry = _has(p, r"^(?:what\s+(?:is|are|does)|why\s+(?:does|is)|how\s+(?:does|do|can)|explain|define|describe|compare|tell me about|can you explain)\b")
    action = _has(p, r"\b(?:implement|build|create|write|change|modify|update|fix|repair|debug|refactor|migrate|upgrade|integrate|install|deploy|publish|delete|remove|revert|rollback|merge|commit|ship|push|run|execute|audit|test|validate|verify|configure|replace)\b")
    informational = inquiry and not _has(p, r"\b(?:for me|in our repo|in the repository|on github|our project|right now|actually|go ahead|make the change|commit it|push it|deploy it)\b")
    mutation = action and not informational

    if _has(p, r"\b(?:explain|define|summarize|rewrite|translate|draft|compare|describe|brainstorm|outline|give (?:me )?(?:an? )?example)\b"):
        raise_to(2, "focused-instruction")
    if coding.get("codingTask") or _has(p, r"\b(?:function|bug|compile|runtime error|code|script|javascript|python|kotlin|typescript|rust)\b"):
        raise_to(2, "programming-domain")
    if mutation:
        raise_to(2, "requested-action")
    if _has(p, r"\b(?:research|investigate|diagnos(?:e|is)|trace|find (?:the )?cause|root cause|compare sources|check (?:current|latest))\b"):
        raise_to(3, "evidence-or-diagnosis")
    if _has(p, r"\b(?:several files|multiple files|multiple modules|cross[- ]module|end[- ]to[- ]end|across (?:the )?(?:repository|app|system)|entire (?:system|codebase|architecture)|all dependencies|full integration|architecture redesign)\b"):
        raise_to(4, "cross-boundary-scope")
    if _has(p, r"\b(?:migration|schema migration|database migration|rollback strategy|production deployment|release pipeline|authentication flow|payment processing|encrypted storage|security boundary|data loss)\b") and mutation:
        raise_to(4, "high-consequence-change")
    if _has(p, r"\b(?:production|live database|private credentials|secrets|payment|medical|legal|security|authentication|authorization|user data|personal data|delete accounts)\b") and mutation:
        raise_to(4, "sensitive-surface")
    if _has(p, r"\b(?:deploy|publish|ship|release|push to production|delete (?:(?:\w+\s+){0,3})(?:database|users|accounts)|drop (?:database|table)|rotate (?:keys|secrets))\b") and mutation and _has(p, r"\b(?:production|live|database|customer|user|payment|secret|keys|server|system|space)\b"):
        raise_to(5, "production-or-destructive-action")
    if _has(p, r"\b(?:roll out|rollout|migration|migrate|backfill)\b") and mutation and _has(p, r"\b(?:production|live|database|customer data)\b"):
        raise_to(5, "critical-migration")
    if coding.get("failureEvidence") or coding.get("needsFailureEvidence"):
        raise_to(3, "failure-evidence-contract")
    if _has(p, r"\b(?:must preserve|do not change|without changing|no regression|keep existing|backwards compatible|backward compatible|existing behavior)\b") and mutation:
        raise_to(3, "preservation-contract")
    if len(text) > 7000:
        raise_to(3, "large-input")

    labels = {1: "INSTANT", 2: "FOCUSED", 3: "STRUCTURED", 4: "DEEP", 5: "CRITICAL"}
    verify = {1: "none", 2: "proportional", 3: "targeted-evidence", 4: "cross-boundary", 5: "independent-gate"}[tier]
    # Do not create a task scheduler or priority queue inside the semantic Brain.
    # The Workstation may apply short-first + aging independently if warranted.
    return {
        "schema": SCHEMA, "tier": tier, "level": labels[tier],
        "reasonCodes": reasons[:12] or ["bounded-default"],
        "verification": verify,
        "priorityHint": "short" if tier <= 2 else "normal" if tier == 3 else "heavy",
        "needsEvidence": tier >= 3,
        "requiresAuthorization": tier == 5,
        "automaticToolPermission": False,
    }
