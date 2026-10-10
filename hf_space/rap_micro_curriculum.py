"""Single focused rap-craft lesson; no borrowed song text or weight training."""
from __future__ import annotations
import os
import re

CUES = {
    "pocket": "Hear a two-bar beat pocket before choosing words. Place stresses where the groove lands; allow a pause. These are performable bars, not a nursery poem.",
    "flow": "Keep a steady rhythmic pocket. Contrast one rapid syllable cluster with a shorter hard-stressed landing or rest; speed must carry meaning.",
    "rhyme": "Find two nearby internal rhyme sounds by pronunciation, not spelling. Keep the image and meaning natural; change the sound family if needed.",
    "punch": "Set up a clear expectation in one bar, then pivot on an unexpected meaning in the next. Stop after the impact.",
    "story": "Make the next couple of bars advance the scene with a real action or consequence, while keeping a rap cadence.",
}
RAP = re.compile(r"\b(?:rap|rapping|rapper|hip[\s-]?hop|freestyle|bars?|cypher|chopper|spit)\b", re.I)
SONG = re.compile(r"\b(?:song|lyrics?|verse)\b", re.I)
FORM = re.compile(r"\b(?:rhyme|flow|cadence|punchline|double[\s-]?time)\b", re.I)
FOCUS = (
    ("flow", r"\b(?:chopper|double[\s-]?time|rapid[\s-]?fire|fast[\s-]?rap|flow[\s-]?switch|cadence)\b"),
    ("punch", r"\b(?:punchlines?|wordplay|double[\s-]?entendre|battle[\s-]?rap)\b"),
    ("rhyme", r"\b(?:internal[\s-]?rhymes?|multisyllabic|multi[\s-]?syllable|slant[\s-]?rhyme|rhyme[\s-]?family)\b"),
    ("story", r"\b(?:story|storytelling|narrative|mystery|plot|character)\b"),
)

def rap_micro_guidance(prompt: str) -> tuple[str, str]:
    """Call only after existing original-songwriting intent and safety gates."""
    if os.getenv("SWRLZ_RAP_MICROLESSON_ENABLED", "1").lower() in {"0","off","false"}:
        return "", "SKIPPED"
    text = " ".join(str(prompt or "").split())[:1600]
    if not (RAP.search(text) or (SONG.search(text) and FORM.search(text))):
        return "", "SKIPPED"
    focus = next((name for name, pattern in FOCUS if re.search(pattern, text, re.I)), "pocket")
    return ("\nONE RAP CRAFT FOCUS: " + CUES[focus] +
            " Respect the user's original subject, exact length, sections and negative constraints; compose original lyrics."), focus
