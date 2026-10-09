"""Deterministic checks for newly generated lyrics, not subjective grading.

Does not retrieve private/reference lyrics, rewrite bars or claim to verify rhyme,
storytelling, originality or real musical cadence.
"""
from __future__ import annotations
import re
from typing import Any

_COUNT = re.compile(r"(?<!\w)(\d{1,3})\s*(?:[-–—]\s*)?(?:line|bar)s?\b", re.I)
_SECTION = re.compile(
    r"^\s*(?:\[\s*)?(?:verse|chorus|hook|bridge|refrain|intro|outro|interlude|"
    r"pre[- ]?chorus|post[- ]?chorus|freestyle)\b[^\]]{0,28}(?:\])?\s*:?\s*$",re.I
)
_REFUSAL = re.compile(
    r"(?i)^\s*(?:i(?:'|’)m\s+sorry\b|i\s+cannot\s+(?:write|create|produce)|"
    r"i\s+can(?:not|'t)\s+(?:produce|write|create)|sorry,?\s+(?:but\s+)?i\s+can(?:not|'t))"
)
_META = re.compile(
    r"(?i)^\s*(?:\(?note\s*:|\(?disclaimer\s*:|\(?this\s+(?:version|song|verse|rap)\b|"
    r"\(?here(?:'s| is)\b|\(?i\s+(?:can|will)\s+(?:create|write|compose)\b|"
    r"\(?flow\s*(?:&|and)\s*feel\s*:|\(?writing\s+notes\s*:|\(?lyric\s+analysis\s*:)"
)

def lyric_shape_request(prompt: str) -> dict[str,Any]:
    """Called only after user intent is classified as original songwriting."""
    source=str(prompt or "")
    found=_COUNT.search(source)
    wanted=int(found.group(1)) if found else None
    if wanted is not None and not 4<=wanted<=120: wanted=None
    low=source.casefold()
    continuous=bool(re.search(r"\b(?:freestyle|continuous\s+(?:verse|rap|flow))\b",low))
    continuous=continuous and not bool(re.search(r"\b(?:sectioned\s+freestyle|freestyle\s+with\s+(?:chorus|hook))\b",low))
    no_chorus=bool(re.search(r"\b(?:no|without|skip|avoid|don't\s+(?:add|use|include))\s+(?:a\s+)?(?:chorus|hook|refrain)\b",low))
    return {"schema":"swrlz-original-lyric-shape-v1","requestedLines":wanted,
            "continuous":continuous,"noChorus":no_chorus,"creative":True}

def _extract_lines(text: str) -> tuple[list[str],list[str]]:
    """Observe existing lines only; never add or silently rewrite lyrical words."""
    raw=str(text or "").strip()
    if not raw: return [],["empty-lyric-candidate"]
    faults=[]
    fence=chr(96)*3
    if fence in raw:
        pattern=re.escape(fence)+r"[^\n]*\n([\s\S]*?)\n"+re.escape(fence)
        matches=list(re.finditer(pattern,raw))
        if len(matches)!=1: return [],["missing-or-multiple-lyric-containers"]
        match=matches[0]
        if (raw[:match.start()]+"\n"+raw[match.end():]).strip():
            faults.append("non-lyrical-preface-or-footer")
        body=match.group(1)
    else:
        body=raw
    lines=[line.strip() for line in body.splitlines()]
    while lines and not lines[0]: lines.pop(0)
    while lines and not lines[-1]: lines.pop()
    return lines,faults

def verify_original_lyrics(raw: str, request: dict[str,Any]) -> dict[str,Any]:
    """Enforce literal line count, section choices and absence of meta/refusal."""
    lines,faults=_extract_lines(raw)
    content=[line for line in lines if line and not _SECTION.fullmatch(line)]
    if not content: faults.append("no-lyrical-lines")
    if any(_REFUSAL.search(x) for x in content): faults.append("unrequested-refusal")
    if any(_META.search(x) for x in content): faults.append("instructional-preface-or-self-grading")
    if request.get("continuous") and any(_SECTION.fullmatch(x) for x in lines if x):
        faults.append("invented-section-labels")
    if request.get("continuous") and "" in lines:
        faults.append("continuous-verse-broken-into-stanzas")
    if request.get("noChorus") and any(
        re.search(r"(?i)\b(?:chorus|hook|refrain)\b",x)
        for x in lines if _SECTION.fullmatch(x)
    ):
        faults.append("unrequested-chorus")
    lyric_content=[line for line in content if not _REFUSAL.search(line) and not _META.search(line)]
    wanted=request.get("requestedLines")
    if wanted is not None and len(lyric_content)!=wanted:
        faults.append("wrong-explicit-lyric-line-count")
    return {"status":"REJECT" if faults else "PASS","reasons":list(dict.fromkeys(faults)),
            "requestedLyricLines":wanted,"observedLyricLines":len(lyric_content),
            "formalOnly":True,"semanticQualityVerified":False}

def clean_lyric_container(raw: str) -> str:
    """Wrap verified text in the UI's single copyable block without new words."""
    lines,_=_extract_lines(raw)
    fence=chr(96)*3
    return fence+"\n"+"\n".join(lines)+"\n"+fence if lines else ""
