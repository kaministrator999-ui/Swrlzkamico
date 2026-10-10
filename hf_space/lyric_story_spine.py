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


_LABELS = {
    "incident": "incident",
    "clue_one": "clue_one", "clue_1": "clue_one", "clue 1": "clue_one",
    "first clue": "clue_one", "clue two": "clue_two", "clue 2": "clue_two",
    "clue_two": "clue_two", "clue_2": "clue_two", "second clue": "clue_two",
    "false lead": "false_lead", "false_lead": "false_lead",
    "cause": "cause", "real cause": "cause",
    "outcome": "outcome", "ending": "outcome", "consequence": "outcome",
}


def inspect_story_spine(text: str) -> tuple[tuple[tuple[str, str], ...] | None, str]:
    """Parse model-authored beats; return one privacy-safe failure category.

    This is format hygiene, not semantic proof. A small model may use numbered
    labels, a code fence, or human-readable underscores; none grants prompt
    instruction authority and no invented story facts are added.
    """
    raw = str(text or "").strip()
    if not raw:
        return None, "empty"
    if len(raw) > 1200:
        return None, "too-long"
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if lines and lines[0].startswith("```") and lines[-1] == "```":
        lines = lines[1:-1]
    if lines and re.fullmatch(r"(?i)(?:story[ -]?plan|outline|plot[ -]?plan)\s*:?", lines[0]):
        lines = lines[1:]
    if len(lines) != len(FIELDS):
        return None, "line-count"
    found = []
    for line, key in zip(lines, FIELDS):
        line = re.sub(r"^(?:[-*]\s*|\d+[.)]\s*)", "", line)
        match = re.fullmatch(r"([A-Za-z_0-9 ]{3,35})\s*:\s*(.+)", line)
        if not match:
            return None, "label-format"
        label = re.sub(r"\s+", " ", match.group(1).strip().casefold())
        if _LABELS.get(label) != key:
            return None, "label-order"
        val = " ".join(match.group(2).split()).strip(" .")
        if _UNSAFE.search(val):
            return None, "unsafe"
        if not (5 <= len(val) <= 145) or len(val.split()) > 23:
            return None, "field-length"
        if _GENERIC.fullmatch(val):
            return None, "generic-field"
        if val.casefold() in {x[1].casefold() for x in found}:
            return None, "duplicate-field"
        found.append((key, val))
    return tuple(found), "ok"


def parse_story_spine(text: str) -> tuple[tuple[str, str], ...] | None:
    """Backward-compatible model-derived original beat parser."""
    beats, _ = inspect_story_spine(text)
    return beats


def narrative_fallback_craft(requested_lines: int) -> str:
    """Strong structure-first writing route when the micro-plan is unusable.

    No hardcoded characters, incidents, source lyrics or recycled words; the
    model must invent concrete story facts itself from the actual user request.
    """
    if not isinstance(requested_lines, int) or requested_lines < 24:
        return ""
    return (
        "\nUNPLANNED NARRATIVE SONG CRAFT: Invent one specific event and a "
        "verifiable cause while writing. Give the first fifth a physical "
        "incident, the second fifth two distinct observable clues, the middle "
        "a reasonable but false suspicion, the next fifth a cause that explains "
        "both clues, and the final fifth a real irreversible outcome. "
        "Do not repeat generic images or empty slogans "
        "as a replacement for new facts. Make fast internal rhymes carry "
        "actions and alternate with short earned punchlines. The last line "
        "must FINISH the event rather than reopen it. "
        "Respect the user's requested exact number of lines and sections."
    )

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
        "Return ONLY the following six newlines with short concrete values; "
        "one field per line and no other text: "
        "incident: (event)\n"
        "clue_one: (first physical trace)\n"
        "clue_two: (second physical trace)\n"
        "false_lead: (plausible wrong explanation)\n"
        "cause: (single action explaining both traces)\n"
        "outcome: (irreversible consequence). "
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
    result, failure_code = inspect_story_spine(raw)
    receipt = {
        "failureCode": None if result else failure_code,
        "status": "USABLE" if result else "UNUSABLE",
        "durationMs": timing.get("durationMs"),
        "fields": len(result or ()),
        "returnedLines": timing.get("returnedSegmentLines"),
    }
    return result, receipt
