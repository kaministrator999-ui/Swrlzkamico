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
