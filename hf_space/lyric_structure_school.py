"""Source-grounded abstract genre/form planning cues for original §wyrlz songs.

Only bounded patterns relevant to the user's creative request enter the small
700M prompt. No song text, artist examples, user archives or model weight update.
This supplements, not replaces, lyric_craft_school's existing owner.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import json
import re


_PATTERNS = Path(__file__).with_name("lyric_structure_patterns_v1.json")
_NO_CHORUS = re.compile(r"\b(?:no|without|avoid|skip|don't\s+(?:add|use|include))\s+(?:a\s+)?(?:chorus|hook|refrain)\b", re.I)


@lru_cache(maxsize=1)
def _structure_cards() -> tuple[dict, ...]:
    try:
        data = json.loads(_PATTERNS.read_text(encoding="utf-8"))
        if data.get("schema") != "swrlz-lyric-structure-patterns-v1":
            return ()
        cards = data.get("cards")
        if not isinstance(cards, list):
            return ()
        safe = []
        for card in cards[:32]:
            if not isinstance(card, dict):
                continue
            cue = card.get("cue")
            triggers = card.get("triggers")
            if (not isinstance(card.get("id"), str) or not isinstance(cue, str)
                    or not isinstance(triggers, list) or not (1 <= len(cue) <= 200)):
                continue
            safe.append({
                "id": card["id"],
                "cue": cue,
                "triggers": tuple(t.casefold() for t in triggers[:12] if isinstance(t, str) and t.strip()),
                "requiresChorus": bool(card.get("requiresChorus")),
            })
        return tuple(safe)
    except (OSError, ValueError, TypeError):
        # The public teaching bank is optional, not an availability dependency.
        return ()


def structure_teaching(prompt: str) -> str:
    """Return at most three short, copyright-safe form mechanisms.

    Called only AFTER existing creative-intent / lookup-intent gating.
    Negative section constraints override all positive style suggestions.
    """
    low = " ".join(str(prompt or "").casefold().split())
    if not low:
        return ""
    no_chorus = bool(_NO_CHORUS.search(low))
    ranked = []
    for order, card in enumerate(_structure_cards()):
        if no_chorus and card["requiresChorus"]:
            continue
        matches = sum(
            bool(re.search(r"(?<!\w)" + re.escape(trigger) + r"(?!\w)", low))
            for trigger in card["triggers"]
        )
        if matches:
            ranked.append((-matches, order, card))
    ranked.sort(key=lambda x: (x[0], x[1]))
    selected = [card for _, _, card in ranked[:3]]
    if not selected:
        return ""
    return "\nTARGETED FORM/GENRE MECHANICS: " + " ".join(
        card["id"] + ": " + card["cue"] for card in selected
    )
