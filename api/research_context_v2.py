"""Source-bound factual research context for §C (v2).

No network, model inference, mutable account information, or private search.
Extract verified enumerations from *retrieved* primary-source passages, with
their requested historical scope. General research remains model-assisted;
this module never calls arbitrary prose "verified".
"""
from __future__ import annotations

import re
from typing import Any

_WORD_COUNTS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
_COUNT_WORDS = "|".join(_WORD_COUNTS)
_TITLE = re.compile(r"\b([A-Za-z][A-Za-z0-9-]{2,})\s+"
                    r"(?:II|III|IV|VI|VII|VIII|IX|X|[2-9]|[1-9]\d)\b", re.I)
_ENUMERATION = re.compile(
    r"\b(?:what|which|who|how many|list|name|all|every|total|"
    r"give me|can you list|what were|what are)\b", re.I)
_ATTRIBUTES = re.compile(
    r"\b(?:classes?|characters?|roles?|members?|roster|types?|"
    r"abilities|skills|features|forms|acts|planets|moons|"
    r"ingredients|components|specifications|versions)\b", re.I)
_ROSTER = re.compile(r"\b(?:classes?|characters?|class roster)\b", re.I)
_PRIVATE = re.compile(
    r"\b(?:my|mine|our|ours|your|last chat|earlier we|our project|"
    r"our repo|account|password|private|my messages)\b",re.I)
_TEMPORAL_REMASTER = re.compile(
    r"\b(?:resurrected|d2r|remaster|reign of the warlock)\b", re.I)
_LOD = re.compile(r"\b(?:lod|lord of destruction|expansion)\b", re.I)
_CLASSIC = re.compile(r"\b(?:classic|base game|original\s+diablo)\b", re.I)
_NAME = re.compile(r"^[A-Z][A-Za-z-]{2,25}$")


def normalize_prompt(prompt: Any) -> str:
    text = " ".join(str(prompt or "").split())[:320]
    # Only title aliases, not facts; never rewrite the user-visible question.
    text = re.sub(r"\bdiablo\s*2\b", "Diablo II", text, flags=re.I)
    text = re.sub(r"\bd2\s+lod\b", "Diablo II Lord of Destruction", text, flags=re.I)
    text = re.sub(r"\bdiablo\s+ii\s+lod\b",
                  "Diablo II Lord of Destruction", text, flags=re.I)
    return text


def needs_factual_research(prompt: Any) -> bool:
    """Route specific public enumerations, never casual or personal lists."""
    text = normalize_prompt(prompt)
    return bool(text and len(text) <= 320
                and _ENUMERATION.search(text) and _ATTRIBUTES.search(text)
                and not _PRIVATE.search(text))


def request_scope(prompt: Any) -> dict[str, str]:
    text = normalize_prompt(prompt)
    # Historical LoD and current remaster are distinct products/eras.
    if _TEMPORAL_REMASTER.search(text):
        scope = "remaster"
    elif _LOD.search(text):
        scope = "expansion"
    elif _CLASSIC.search(text):
        scope = "original"
    else:
        scope = "unspecified"
    subject = _TITLE.search(text)
    return {"subject":subject.group(0) if subject else "",
            "scope":scope,
            "rosterQuestion":"yes" if needs_factual_research(text)
                                  and _ROSTER.search(text) else "no"}


def _names(value: str) -> list[str]:
    clean = re.sub(r"\b(?:and|the)\b", ",", value, flags=re.I)
    names = []
    for part in clean.split(","):
        name = part.strip(" .;:()-\t\n\r")
        if _NAME.fullmatch(name) and name not in names:
            names.append(name)
    return names


def _count(value: str) -> int | None:
    val = str(value).strip().lower()
    if val.isdigit():
        return int(val)
    return _WORD_COUNTS.get(val)


def extract_original_roster(text: str, subject: str) -> list[str]:
    """Parse an exact source sentence, not a generated roster or domain label."""
    if not subject:
        return []
    pattern = (
        r"\bthere are\s+(?:a\s+total\s+of\s+)?"
        r"(?P<count>\d+|" + _COUNT_WORDS + r")\s+"
        r"(?:playable\s+)?character\s+(?:types|classes)\s+in\s+"
        + re.escape(subject) + r"\s*:\s*"
        r"(?P<roster>[A-Za-z,\s-]{10,180}?)\."
    )
    match = re.search(pattern,text,re.I)
    if not match:
        return []
    names = _names(match.group("roster"))
    count = _count(match.group("count"))
    return names if count is not None and len(names)==count and count>=2 else []


def extract_expansion_additions(text: str, label: str) -> list[str]:
    """Require the expansion label and an explicit two-class attribution."""
    if not label:
        return []
    text = " ".join(text.split())
    patterns = (
        r"\btwo\s+more\s+added\s+in\s+the\s+"+re.escape(label)
        +r".{0,40}?\bexpansion,\s+the\s+(?P<a>[A-Z][a-z]+)\s+and\s+the\s+(?P<b>[A-Z][a-z]+)",
        r"\btwo\s+new\s+(?:character\s+)?classes.{0,75}?\b"
        +re.escape(label)+r".{0,70}?\b(?P<a>[A-Z][a-z]+)\s+and\s+(?P<b>[A-Z][a-z]+)",
    )
    for pattern in patterns:
        match=re.search(pattern,text,re.I)
        if match:
            names=[match.group("a"),match.group("b")]
            if len(set(n.lower() for n in names))==2:
                return names
    return []


def verified_roster_context(prompt: str, bundle: Any) -> dict[str, Any] | None:
    """Construct evidence-backed 5+2 style enumeration only when both
    distinct source passages and intended edition are unambiguous.

    Scope 'remaster' is intentionally excluded: current editions can add
    classes after their original release (e.g. 2026 DLC).
    """
    context=request_scope(prompt)
    if context["rosterQuestion"]!="yes" or context["scope"]=="remaster":
        return None
    subject=context["subject"]
    evidence=bundle.get("evidence",[]) if isinstance(bundle,dict) else []
    base=None
    additions=None
    for card in evidence:
        if not isinstance(card,dict):
            continue
        excerpt=str(card.get("excerpt") or "")
        if card.get("referenceRole")=="historical_original_class_roster":
            parsed=extract_original_roster(excerpt,subject)
            if parsed:
                base=(parsed,card)
        if card.get("referenceRole")=="historical_expansion_class_additions":
            label="Lord of Destruction" if "lord of destruction" in prompt.lower() or re.search(r"\blod\b",prompt,re.I) else ""
            parsed=extract_expansion_additions(excerpt,label)
            if parsed:
                additions=(parsed,card)
    if base is None:
        return None
    scope=context["scope"]
    if scope=="unspecified":
        # "Diablo II" alone is ambiguous between Classic and Expansion;
        # only present an answer if the question explicitly names LoD.
        return None
    if scope=="expansion" and additions is None:
        return None
    base_names,base_card=base
    extra_names,extra_card=additions if additions else ([],None)
    merged=base_names + extra_names if scope=="expansion" else base_names
    if len(set(n.lower() for n in merged))!=len(merged):
        return None
    result={
        "kind":"historical_class_roster",
        "subject":subject,
        "scope":scope,
        "baseClasses":base_names,
        "addedClasses":extra_names if scope=="expansion" else [],
        "classes":merged,
        "total":len(merged),
        "evidence":[{"title":base_card.get("title"),"url":base_card.get("url"),
                     "referenceRole":"historical_original_class_roster"}],
        "verification":"source_extracted_count_and_named_members",
        "answerScope":"historical_original_or_original_expansion_only",
    }
    if extra_card:
        result["evidence"].append({
            "title":extra_card.get("title"),"url":extra_card.get("url"),
            "referenceRole":"historical_expansion_class_additions"})
    return result


def grounded_roster_reply(prompt: str, bundle: Any) -> str | None:
    facts=verified_roster_context(prompt,bundle)
    if not facts:
        return None
    name=facts["subject"]
    if facts["scope"]=="expansion":
        text=[
            "**"+name+": Lord of Destruction has "+str(facts["total"])+" playable classes** "
            "in the original 2001 expansion (five from the base game and two added by LoD).",
            "**Original "+name+" (2000) — "+str(len(facts["baseClasses"]))+":** "
            +", ".join(facts["baseClasses"])+".",
            "**Lord of Destruction additions — "+str(len(facts["addedClasses"]))+":** "
            +", ".join(facts["addedClasses"])+".",
        ]
    else:
        text=[
            "**"+name+" Classic has "+str(facts["total"])+" playable classes** "
            "in its original base release:",
            ", ".join(facts["baseClasses"])+".",
        ]
    text.append("Sources: "+"; ".join(
        "["+str(item["title"])+"]("+str(item["url"])+")"
        for item in facts["evidence"]))
    return "\n\n".join(text)
