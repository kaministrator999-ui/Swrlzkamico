"""Deterministic checks for newly generated lyrics, not subjective grading.

Does not retrieve private/reference lyrics, rewrite bars or claim to verify rhyme,
storytelling, originality or real musical cadence.
"""
from __future__ import annotations
import re
from typing import Any

_COUNT = re.compile(
    r"(?<!\w)(\d{1,3})\s*(?:[-–—]\s*)?"
    r"(?:(?:original|new|fresh|rap|freestyle|chopper|technical|bouncy|"
    r"funny|lyrical|rhyming|hip[- ]hop|hard[- ]hitting)\s+){0,4}"
    r"(?:lyric\s+)?(?:line|bar)s?\b", re.I
)
_SECTION = re.compile(
    # Match a real musical section label, not a lyric beginning "Chorus ...".
    r"^\s*(?:\[\s*)?(?:pre[- ]?chorus|post[- ]?chorus|verse|chorus|hook|"
    r"bridge|refrain|intro|outro|interlude|freestyle)\b"
    r"(?:\s*(?:\d{1,2}|[IVX]{1,5}|x\d{1,2}|\(\s*(?:repeat|reprise)\s*\)))?"
    r"(?:\s*[-–—]\s*\d{1,3}\s*bars?)?"
    r"\s*(?:\])?\s*:?\s*[*_]{0,3}\s*$",re.I
)
_REFUSAL = re.compile(
    r"(?i)^\s*(?:i(?:'|’)m\s+sorry\b|i\s+cannot\s+(?:write|create|produce)|"
    r"i\s+can(?:not|'t)\s+(?:produce|write|create)|sorry,?\s+(?:but\s+)?i\s+can(?:not|'t)|"
    r"i\s+can(?:not|'t)\s+(?:do|deliver|complete)\s+(?:(?:a|the|this|that)\s+)?"
    r"(?:(?:\d{1,3}|forty)\s*[-–—]?\s*(?:line|bar)s?\s+)?"
    r"(?:freestyle|rap|song|verse|lyrics?)\b)"
)
_META = re.compile(
    r"(?i)^\s*(?:\(?note\s*:|\(?disclaimer\s*:|\(?this\s+(?:version|song|verse|rap)\b|"
    r"\(?here(?:'s| is)\b|\(?i\s+(?:can|will)\s+(?:create|write|compose)\b|"
    r"\(?flow\s*(?:&|and)\s*feel\s*:|\(?writing\s+notes\s*:|\(?lyric\s+analysis\s*:)"
)

def _normalized_label(line: str) -> str:
    """Remove superficial Markdown heading/emphasis from validator inspection.

    Never rewrite or remove the user's original lyric text. This only lets
    structural checks see **Chorus**, **Note:** and ## Chorus like plain labels.
    """
    text=str(line or "").strip()
    text=re.sub(r"^#{1,6}\s+", "", text)
    return re.sub(r"^(?:\*{1,3}|_{1,3})", "", text).strip()


def _is_section_label(line: str) -> bool:
    return bool(_SECTION.fullmatch(_normalized_label(line)))


def _is_meta_label(line: str) -> bool:
    return bool(_META.search(_normalized_label(line)))


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
    content=[line for line in lines if line and not _is_section_label(line)]
    if not content: faults.append("no-lyrical-lines")
    if any(_REFUSAL.search(x) for x in content): faults.append("unrequested-refusal")
    if any(_is_meta_label(x) for x in content): faults.append("instructional-preface-or-self-grading")
    if request.get("continuous") and any(_is_section_label(x) for x in lines if x):
        faults.append("invented-section-labels")
    if request.get("continuous") and "" in lines:
        faults.append("continuous-verse-broken-into-stanzas")
    if request.get("noChorus") and any(
        re.search(r"(?i)\b(?:chorus|hook|refrain)\b",x)
        for x in lines if _is_section_label(x)
    ):
        faults.append("unrequested-chorus")
    lyric_content=[line for line in content if not _REFUSAL.search(line) and not _is_meta_label(line)]
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


_TITLE = re.compile(r"(?i)^\s*(?:title|song\s+title)\s*:")

def recoverable_continuous_lines(raw: str, request: dict[str,Any]) -> list[str] | None:
    """Keep model-authored lyric WORDS; remove only empty stanza separators.

    Reject summaries, refusals, title/section labels and non-lyrical prose.
    Empty lines can be removed in an explicitly continuous verse because the
    user's negative constraint outranks the model's arbitrary stanza spacing.
    This is presentation normalization, not inventing missing bars.
    """
    if not request.get("continuous"):
        return None
    all_lines,faults=_extract_lines(raw)
    if faults:
        return None
    words=[line for line in all_lines if line]
    if not words or len(words)>120:
        return None
    if any(_REFUSAL.search(line) or _is_meta_label(line) or _TITLE.search(line)
           or _is_section_label(line) for line in words):
        return None
    if request.get("noChorus") and any(
        _is_section_label(line) and re.search(r"(?i)\b(?:chorus|hook|refrain)\b",line)
        for line in words
    ):
        return None
    # Keep each authored line intact, in its original order.
    return words


def extend_continuous_lyrics(prefix: list[str], new_raw: str,
                            request: dict[str,Any]) -> list[str] | None:
    """Accept bounded authored continuation, never auto-pad or silently truncate."""
    desired=request.get("requestedLines")
    if not isinstance(desired,int) or desired<=0 or len(prefix)>=desired:
        return None
    suffix=recoverable_continuous_lines(new_raw,request)
    if not suffix or len(suffix)>desired-len(prefix):
        return None
    original_set={line.casefold().strip() for line in prefix}
    if any(line.casefold().strip() in original_set for line in suffix):
        return None
    if len({line.casefold().strip() for line in suffix}) != len(suffix):
        return None
    return list(prefix)+suffix


def continuation_shape_receipt(prefix: list[str], raw: str,
                               request: dict[str,Any]) -> dict[str,Any]:
    """Privacy-safe diagnostics for an unaccepted model-authored suffix.

    Return reason codes and counts ONLY; never store user lyric words.
    """
    total=request.get("requestedLines")
    missing=max(0,total-len(prefix)) if isinstance(total,int) else None
    full,syntax_faults=_extract_lines(raw)
    nonempty=[line for line in full if line]
    recoverable=recoverable_continuous_lines(raw,request)
    codes=list(syntax_faults)
    if not nonempty:
        codes.append("empty-continuation")
    if recoverable is None and not syntax_faults and nonempty:
        if not request.get("continuous"):
            codes.append("unsupported-noncontinuous-continuation")
        if any(_REFUSAL.search(line) for line in nonempty):
            codes.append("refusal-in-continuation")
        if any(_is_meta_label(line) or _TITLE.search(line) for line in nonempty):
            codes.append("explanation-or-title-in-continuation")
        if any(_is_section_label(line) for line in nonempty):
            codes.append("section-label-in-continuation")
        if not codes:
            codes.append("unusable-continuation-format")
    if recoverable is not None:
        if missing is not None and len(recoverable)>missing:
            codes.append("too-many-continuation-lines")
        seen={line.casefold().strip() for line in prefix}
        if any(line.casefold().strip() in seen for line in recoverable):
            codes.append("prior-lyric-line-repeated")
        if len({line.casefold().strip() for line in recoverable})!=len(recoverable):
            codes.append("duplicate-new-lyric-lines")
    if not codes:
        codes.append("continuation-not-accepted")
    return {
        "status":"REJECT",
        "reasons":list(dict.fromkeys(codes)),
        "requestedLyricLines":total,
        "observedLyricLines":len(prefix),
        "observedSuffixNonemptyLines":len(nonempty),
        "remainingLyricLines":missing,
        "formalOnly":True,
        "semanticQualityVerified":False,
    }
