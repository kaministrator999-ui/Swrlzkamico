"""Original lyric-craft guidance for the §wyrlz 700M route.

Learn from source-independent *relationships*, not verbatim favorite songs.
The larger public curriculum and private archive are never injected wholesale.
No prompt guidance here changes GGUF model weights.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import hashlib
import json
import re


_CRAFT_REQUEST = re.compile(
    r"\b(?:write|make|create|compose|generate|craft|draft|perform|spit|give\s+me|hit\s+(?:me\s+)?with)\b"
    r".{0,110}\b(?:song|rap|freestyle|lyrics?|verse|bars?|cypher|track|hook|chorus)\b"
    r"|\b(?:freestyle|spit\s+(?:some\s+)?bars?|next\s+(?:song|track)|another\s+(?:song|rap|freestyle))\b",
    re.I | re.S,
)
_ANALYSIS_ONLY = re.compile(
    r"^\s*(?:analy[sz]e|review|explain|critique|compare|find|search|fetch|look\s+up|quote|transcribe|retrieve|what\s+(?:are|is)|who\s+(?:made|wrote))\b",
    re.I,
)
_ANALYSIS_WRITING = re.compile(
    r"^\s*(?:write|draft|create|make|give\s+me)\s+(?:me\s+)?(?:an?\s+)?"
    r"(?:analysis|review|critique|summary|explanation|report|essay|comparison|breakdown)\b",
    re.I,
)

LYRIC_CRAFT_SCHOOL = (
    "ORIGINAL LYRIC CRAFT (abstract technique, not quoted examples): "
    "Follow the user's specified topic, form, length, tone and negative constraints first. "
    "If unspecified, choose a specific, surprising scenario instead of defaulting to crowns, glitches, fire, wealth or generic streets. "
    "Build full, performable verses that advance a scene, argument or joke every few lines; avoid four-line fragments and filler. "
    "Develop deliberate end-rhyme families and internal multi-syllable pockets, then change the sound pattern before it becomes mechanical; never sacrifice meaning for forced rhymes. "
    "Vary breath length: mix rolling double-time clusters with short accented punches and natural pauses. "
    "Make hooks catchy through rhythmic shape, a clear idea and selective recurrence, not repeated padding; do not invent a hook for an unrequested continuous freestyle. "
    "For emotional tracks, use concrete details and evolving stakes before an earned turn. "
    "For comedy or battle tracks, build a comprehensible setup, misdirection and payoff that lands at performance speed. "
    "Use callbacks with changed meaning, fresh subject-specific vocabulary and coherent escalation. "
    "Never recycle earlier songs' wording, hooks, titles, signature imagery or rhyme words to reproduce their feel. "
    "Deliver complete lyrics directly with intentional line breaks and no preamble or post-song analysis unless requested."
)

_CATALOG_FILE = Path(__file__).with_name("lyric_craft_catalog_v2.json")
_FORM_FILE = Path(__file__).with_name("lyric_form_cues_v4.json")
_DEFAULT_AXES = ("narrative", "internal-rhyme", "tempo", "comedy", "emotional", "high-speed", "metaphor", "melodic")


@lru_cache(maxsize=1)
def _catalog() -> tuple[dict, ...]:
    """Load bounded public craft cues, not private archive excerpts."""
    try:
        raw = json.loads(_CATALOG_FILE.read_text(encoding="utf-8"))
        if raw.get("schema") != "swrlz-lyric-craft-router-catalog-v2":
            return ()
        cards = raw.get("cards")
        if not isinstance(cards, list):
            return ()
        safe = []
        for card in cards:
            if not isinstance(card, dict):
                continue
            if not isinstance(card.get("compactCue"), str):
                continue
            if not isinstance(card.get("axis"), str) or not isinstance(card.get("role"), str):
                continue
            safe.append({
                "axis": card["axis"],
                "role": card["role"],
                "cue": card["compactCue"][:260],
                "triggers": tuple(x for x in (card.get("triggers") or []) if isinstance(x, str))[:10],
            })
        return tuple(safe[:96])
    except (OSError, ValueError, TypeError):
        # A missing/invalid teaching catalog must not break song generation.
        return ()


@lru_cache(maxsize=1)
def _form_cards() -> tuple[dict, ...]:
    """Read only short owner-authored form guidance; never load song text."""
    try:
        raw = json.loads(_FORM_FILE.read_text(encoding="utf-8"))
        if raw.get("schema") != "swrlz-lyric-ocean-form-cue-v4":
            return ()
        cards = raw.get("cards", [])
        if not isinstance(cards, list):
            return ()
        return tuple(
            {"id": c["id"], "cue": c["cue"][:300],
             "triggers": tuple(t.casefold() for t in c.get("triggers", [])[:8] if isinstance(t, str))}
            for c in cards[:16]
            if isinstance(c, dict) and isinstance(c.get("id"), str) and isinstance(c.get("cue"), str)
        )
    except (OSError, ValueError, TypeError, KeyError):
        return ()


def _specific_form_cue(text: str) -> str:
    low = " ".join(str(text or "").casefold().split())
    for card in _form_cards():
        if any(t and re.search(r"(?<!\\w)" + re.escape(t) + r"(?!\\w)", low) for t in card["triggers"]):
            return card["cue"]
    return ""


def _focused_teaching(prompt: str, *, structural_reference: bool = False) -> str:
    cards = _catalog()
    if not cards:
        return ""
    text = " ".join(str(prompt or "").casefold().split())
    axes = {}
    for card in cards:
        if card["axis"] in axes:
            continue
        count = sum(
            1 for term in card["triggers"]
            if term and re.search(r"(?<!\w)" + re.escape(term.casefold()) + r"(?!\w)", text)
        )
        if count:
            axes[card["axis"]] = count
    if axes:
        selected_axes = [axis for axis, _ in sorted(axes.items(), key=lambda pair: (-pair[1], pair[0]))[:2]]
    else:
        # Rotate source-free *mechanisms* across diverse topics. Stable for a
        # given request, no random state and no archive words to memorize.
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
        selected_axes = [
            _DEFAULT_AXES[seed % len(_DEFAULT_AXES)],
            _DEFAULT_AXES[(seed // 7 + 3) % len(_DEFAULT_AXES)],
        ]
        if selected_axes[0] == selected_axes[1]:
            selected_axes[1] = _DEFAULT_AXES[(_DEFAULT_AXES.index(selected_axes[0]) + 1) % len(_DEFAULT_AXES)]
    selected = []
    for i, axis in enumerate(selected_axes):
        role = "build" if i == 0 else "perform"
        card = next((c for c in cards if c["axis"] == axis and c["role"] == role), None)
        if card:
            selected.append(card["axis"] + ": " + card["cue"])
    form_tip = _specific_form_cue(text)
    if form_tip:
        selected.append("Form: " + form_tip)
    # Structure-only source references remain abstract; never inject examples.
    if structural_reference and selected:
        selected.append("Reference boundary: learn only the abstract musical form; every new image, title and word must be independent.")
    # Bounded targeted hints; the whole lesson bank never enters 700M prefill.
    return "\nFOCUSED ORIGINAL SONGWRITING TOOLS: " + " ".join(selected) if selected else ""


def lyric_craft_policy(prompt: str, *, structural_reference: bool = False) -> str:
    """Original creation only; lookup, critique and explanation remain inert."""
    text = " ".join(str(prompt or "").split())
    if not structural_reference:
        if not text or _ANALYSIS_ONLY.search(text) or _ANALYSIS_WRITING.search(text):
            return ""
        if not _CRAFT_REQUEST.search(text):
            return ""
    return LYRIC_CRAFT_SCHOOL + _focused_teaching(text, structural_reference=structural_reference)
