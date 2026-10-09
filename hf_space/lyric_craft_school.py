"""Original songwriting-craft prefill for §wyrlz's 700M route.

Abstracted from the user's private song-review archive without publishing raw
lyrics, personal history or borrowed reference lines. Prompt guidance only:
this module does not modify or train any model weights.
"""
from __future__ import annotations

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


def lyric_craft_policy(prompt: str, *, structural_reference: bool = False) -> str:
    """Only original-creation turns receive craft guidance; factual lookups do not."""
    text = " ".join(str(prompt or "").split())
    if structural_reference:
        return LYRIC_CRAFT_SCHOOL
    if not text or _ANALYSIS_ONLY.search(text):
        return ""
    return LYRIC_CRAFT_SCHOOL if _CRAFT_REQUEST.search(text) else ""
