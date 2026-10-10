"""One brief, original narrative outline for counted storytelling lyrics.

The same locally running LFM2 model invents its own plot details using a
small standalone planning prompt; no copyrighted examples or archive text
are provided. A missing/malformed plan does not reject an otherwise valid
lyric response. This planning advice is NOT a semantic quality verdict.
"""
from __future__ import annotations

import re
from typing import Any

from lyric_bounded_continuation import buffered_bounded_original_lyrics

FIELDS = ("incident", "clue_one", "clue_two", "false_lead", "cause", "outcome")
_STORY_INTENT = re.compile(
    r"\b(?:mystery|detective|investigat\w*|sleuth|whodunit|crime|"
    r"solv(?:e|es|ing|ed)\s+(?:a|the|this|that)\s+(?:case|mystery|puzzle)|"
    r"story|storytelling|narrative|plot\s+twist)\b", re.I
)
_UNSAFE = re.compile(
    r"(?i)(?:https?://|www\.|\b(?:ignore|disregard|override|system\s+prompt|"
    r"assistant\s+instructions|openai|chatgpt|copyright|refuse|cannot\s+comply)\b|"
    r"\x60\x60\x60|[\[\]{}<>])"
)
_GENERIC = re.compile(
    r"(?i)^\s*(?:the\s+)?(?:truth|secret|mystery|puzzle|answer|solution|"
    r"clue|criminal|thief|reason)\s+(?:is\s+)?(?:revealed|found|solved|"
    r"unknown|hidden|mysterious)?[.!]?\s*$"
)


def needs_story_spine(prompt: str, requested_lines: int | None) -> bool:
    """Affects explicit longer narrative creations, not generic music/retrieval."""
    return (
        isinstance(requested_lines, int)
        and not isinstance(requested_lines, bool)
        and requested_lines >= 24
        and bool(_STORY_INTENT.search(str(prompt or "")[:1400]))
    )


def parse_story_spine(text: str) -> tuple[tuple[str, str], ...] | None:
    """Accept exactly six brief ordered beats with no control instructions."""
    lines = [line.strip() for line in str(text or "").strip().splitlines()]
    if len(lines) != len(FIELDS):
        return None
    found = []
    for line, key in zip(lines, FIELDS):
        m = re.fullmatch(r"([a-z_]+)\s*:\s*(.+)", line)
        if not m or m.group(1) != key:
            return None
        val = " ".join(m.group(2).split()).strip(" .")
        if not (8 <= len(val) <= 115) or len(val.split()) > 19:
            return None
        if _UNSAFE.search(val) or _GENERIC.fullmatch(val):
            return None
        if val.casefold() in {x[1].casefold() for x in found}:
            return None
        found.append((key, val))
    if found[1][1].casefold() == found[2][1].casefold():
        return None
    return tuple(found)


def story_spine_directive(beats: tuple[tuple[str,str], ...], requested_lines: int) -> str:
    """One compact factual anchor; not output text and not an invented chorus."""
    if tuple(key for key, _ in beats) != FIELDS:
        return ""
    lines = ["\nSTORY CAUSALITY PLAN (private planning, do NOT print labels or explanation):"]
    for label, value in beats:
        lines.append(label.replace("_"," ") + ": " + value)
    lines.append(
        f"Turn these events into {requested_lines} ORIGINAL lyrical lines in sequence. "
        "Plant the physical evidence early; test the false lead; the named cause "
        "must explain BOTH clues; the ending must show an actual consequence, "
        "not say the mystery is solved or start another mystery. "
        "On rapid-fire lines link two internal sound pivots to actions, then "
        "follow with short, forceful payoff lines. Keep the user's structure."
    )
    return "\n".join(lines)


def generate_story_spine(
    model: Any,
    prompt: str,
    requested_lines: int,
) -> tuple[tuple[tuple[str, str], ...] | None, dict[str, Any]]:
    """At most ONE short extra local inference. No retries or external calls."""
    if not needs_story_spine(prompt, requested_lines):
        return None, {"status": "SKIPPED", "durationMs": 0}
    spec = (
        "Design a concrete original causal plot for a requested song. "
        "You are planning silently, NOT writing lyrics. "
        "Answer with EXACTLY six simple lowercase-key lines and absolutely "
        "nothing else; use invented physical objects, actions and motives. "
        "Follow this exact six-line label format, one per line:\\n"
        "incident: <specific event>\\nclue_one: <physical evidence>\\n"
        "clue_two: <different physical evidence>\\nfalse_lead: <wrong explanation>\\n"
        "cause: <the real action explaining the evidence>\\n"
        "outcome: <concrete irreversible consequence>. "
        "CAUSE must physically explain BOTH clues; outcome is irreversible. "
        "Each value 4 to 14 words, no generic 'secret found' or 'truth revealed'. "
        "No lyric quotations, no stage directions, no names of real artists. "
        "All details must honor any facts specified by the user."
    )
    raw, timing = buffered_bounded_original_lyrics(
        model,
        [
            {"role": "system", "content": spec},
            {"role": "user", "content": str(prompt or "")[:1100]},
        ],
        max_tokens=236,
        temperature=0.36,
        max_lines=6,
    )
    result = parse_story_spine(raw)
    receipt = {
        "status": "USABLE" if result else "UNUSABLE",
        "durationMs": timing.get("durationMs"),
        "fields": len(result or ()),
        "returnedLines": timing.get("returnedSegmentLines"),
    }
    return result, receipt
