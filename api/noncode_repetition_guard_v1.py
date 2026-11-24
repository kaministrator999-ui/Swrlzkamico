"""Bounded, text-only detector for runaway model repetition.

Only complete nonempty lines count. Token chunk boundaries do not count as
repetition, and normal recurring choruses separated by verses remain valid.
Never logs or stores source text.
"""
from __future__ import annotations
import re

_SPACE = re.compile(r"\s+")


class RepetitionWatch:
    """Per-candidate finite rolling text window, no persistent history."""

    def __init__(self, max_chars: int = 32000) -> None:
        self.max_chars = max_chars
        self.buffer = ""
        self.detected = None

    def reset(self) -> None:
        self.buffer = ""
        self.detected = None

    def observe(self, fragment: str):
        if self.detected:
            return self.detected
        self.buffer = (self.buffer + str(fragment or ""))[-self.max_chars:]
        # Do not count half a streaming token line as a completed line.
        completed = self.buffer.rsplit("\n", 1)[0] if "\n" in self.buffer else ""
        lines = []
        in_fence = False
        for raw in completed.splitlines():
            value = raw.strip()
            if value.startswith("```"):
                in_fence = not in_fence
                lines.clear()
                continue
            if in_fence:
                continue
            norm = _SPACE.sub(" ", value).lower().strip(" ,.;:!?")
            if not (len(norm) >= 24 and len(norm.split()) >= 5):
                if value:
                    lines.clear()  # headings or prose break an adjacent run
                continue
            lines.append(norm)
        for unit, cycles in ((1, 5), (2, 4), (3, 3), (4, 3)):
            if len(lines) < unit * cycles:
                continue
            tail = lines[-unit * cycles:]
            template = tail[:unit]
            if unit > 1 and len(set(template)) != unit:
                continue
            if tail == template * cycles:
                self.detected = {"blockSize": unit, "cycles": cycles}
                return self.detected
        return None


def guard_eligible(payload) -> bool:
    if not isinstance(payload, dict):
        return False
    if payload.get("githubSourceChangeTask") or payload.get("sourceChangeMode"):
        return False
    programming = payload.get("programming") or {}
    generation = payload.get("generation") or {}
    if isinstance(programming, dict) and programming.get("codingTask"):
        return False
    if isinstance(generation, dict) and generation.get("codingTask"):
        return False
    if str(payload.get("presentationIntent") or "").upper() in {"CODE", "HTML", "ARTIFACT"}:
        return False
    # Explicit repetitions are user-directed rather than model degeneration.
    prompt = str(payload.get("prompt") or "")
    if re.search(r"(?i)\b(?:repeat|repeating|loop)\b.{0,42}\b(?:times|repetitions|iterations)\b", prompt):
        return False
    return True


# Decision-stall detection catches semantically repetitive engineering plans
# that are not exact-line repetitions. It is a narrow additional signal:
# no model/tool mutations, no inferred approvals, no unbounded self-retries.
_PLAN_STEP = re.compile(r"(?im)^\s*(?:#{1,4}\s*)?(?:(?:revised|better|alternative|corrected|final|actual)\s+)*(?:plan|solution|approach|option|correction|wait\b|however\b|but\b)\s*(?:[:.\-]|\b)")
_CANONICAL = (
    (re.compile(r"\b(?:cdn|jsdelivr|unpkg|remote|external)\b"), "remote"),
    (re.compile(r"\b(?:bundle|bundling|bundled|inline|inlining|inlined)\b"), "bundle"),
    (re.compile(r"\b(?:local|relative|self-host|serve)\b"), "local"),
    (re.compile(r"\b(?:csp|content security|sandbox|policy)\b"), "policy"),
)
_CODE_FENCE = re.compile(r"(?s)^\s*\x60{3}.*?^\s*\x60{3}", re.M)


class DecisionStallWatch:
    """Bounded per-turn monitor for repeated planning with no execution evidence.

    This is deliberately not a general semantic similarity classifier. It only
    recognizes several successive explicit plan resets covering the same
    technical alternatives, and only on grounded project repair requests.
    """

    def __init__(self, max_chars=32000):
        self.buffer = ""
        self.max_chars = max_chars
        self.detected = None

    def reset(self):
        self.buffer = ""
        self.detected = None

    def observe(self, fragment):
        if self.detected:
            return self.detected
        self.buffer = (self.buffer + str(fragment or ""))[-self.max_chars:]
        completed = self.buffer.rsplit("\n", 1)[0] if "\n" in self.buffer else ""
        prose = _CODE_FENCE.sub("", completed)
        headings = list(_PLAN_STEP.finditer(prose))
        if len(headings) < 4:
            return None
        sections = []
        for i, match in enumerate(headings):
            end = headings[i + 1].start() if i + 1 < len(headings) else len(prose)
            body = prose[match.end():end]
            if len(body.strip()) < 18:
                continue
            concepts = frozenset(
                name for expression, name in _CANONICAL if expression.search(body))
            if len(concepts) >= 2:
                sections.append((match.start(), concepts))
        if len(sections) < 4:
            return None
        last = sections[-4:]
        shared = set.intersection(*(set(concepts) for _, concepts in last))
        coverage = set.union(*(set(concepts) for _, concepts in last))
        if len(shared) >= 2 and len(coverage) <= 4:
            self.detected = {
                "cycles": len(last), "sharedConcepts": sorted(shared),
                "reason": "Repeated engineering alternatives without execution"}
        return self.detected


def decision_guard_eligible(payload):
    """Only source-grounded repair discussions; never a code artifact or free prose."""
    if not guard_eligible(payload):
        return False
    prompt = str(payload.get("receivedText") or payload.get("prompt") or "")
    active = payload.get("activeHtmlProject")
    source = payload.get("projectFileEvidence")
    if not isinstance(active, dict) or not isinstance(source, str):
        return False
    if "VERIFIED OWNER GITHUB HTML PROJECT SOURCE" not in source:
        return False
    return bool(re.search(r"\b(?:fix|repair|debug|diagnos\w*|redeploy|broken|stuck|loading|not work\w*)\b", prompt, re.I))
