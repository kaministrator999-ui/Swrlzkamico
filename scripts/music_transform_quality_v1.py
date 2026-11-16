"""Reusable §C songwriting transformations: intent, compact craft contract, structural QA.

Operates on lyric text only; never fetches, persists or logs reference lyrics.
The checks are deliberately conservative: they detect observable defects, not
musical taste, melody, meter or copyrighted-source identity.
"""
from __future__ import annotations
from collections import Counter
import re

_WORD = re.compile(r"[\w']+", re.UNICODE)
_SECTION = re.compile(
    r"^\s*(?:#{1,3}\s*)?(?:\*{1,2})?\s*\[?\s*"
    r"(?P<kind>verse|chorus|hook|refrain|bridge|intro|outro|pre[- ]?chorus|"
    r"post[- ]?chorus|interlude|freestyle|cypher)"
    r"(?:\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten))?"
    r"(?:\s*[:\-]\s*[^\]]+)?\s*\]?(?:\s*\*{1,2})?\s*:?(?:\s*)$",
    re.I,
)
_MODES = [
    ("parody",r"\b(?:parod(?:y|ies)|parodic|satiri[sz]e|satirical\s+(?:song|version))\b"),
    ("remaster",r"\b(?:remaster|polish\s+(?:up\s+)?(?:the\s+)?(?:lyrics?|song)|refine\s+(?:the\s+)?(?:lyrics?|song))\b"),
    ("mashup",r"\b(?:mash[ -]?up|blend\s+(?:two|these)\s+songs?)\b"),
    ("remix",r"\b(?:remix|re[- ]?mix|flip\s+(?:the|this|that)\s+(?:song|track|verse|lyrics?))\b"),
    ("paraphrase",r"\b(?:rewrite|re[- ]?write|rework|reimagine|reinterpret|make\s+a\s+new\s+version)\b"),
    ("adaptation",r"\b(?:adapt|genre[- ]?swap|convert\s+(?:this|the)\s+song|turn\s+(?:this|the)\s+song\s+into)\b"),
    ("cover",r"\b(?:make|write|create|compose|arrange)\s+(?:a\s+|an\s+)?(?:new\s+)?cover\b"),
]
_SONG_CUE = re.compile(r"\b(?:song|track|lyrics?|verse|rap|rhyme|hook|chorus|music|beat|bars?|freestyle|parody|remix|remaster|mashup)\b",re.I)
_NON_CREATIVE = re.compile(
    r"^\s*(?:what|when|where|who|why|how|explain|research|look\s+up|"
    r"search|find|tell\s+me\s+about|compare|analy[sz]e|review|"
    r"can\s+you\s+explain|could\s+you\s+research)\b",re.I)
_CREATE = re.compile(r"\b(?:make|create|write|compose|craft|generate|do|give|turn|"
                     r"rewrite|rework|remix|remaster|parody|adapt|reimagine|flip|produce)\b",re.I)
_LYRIC = re.compile(r"^(?:\s*\x60{3}[^\n]*\n|\s*\x60{3}\s*$)",re.I)
_PREFACE = re.compile(r"^(?:sure[,! ]|alright[,! ]|here(?:'s| is)\s+(?:a|the|your)\b|"
                      r"hope\s+you\s+like|feel\s+free\s+to|let(?:'s| us)\b)",re.I)

def transformation_contract(prompt: str, *, reference_available: bool = False) -> dict | None:
    """Parse an explicit lyrical operation; avoid hijacking lookup or explanation."""
    text=" ".join(str(prompt or "").split()).strip()
    if not text or _NON_CREATIVE.match(text):
        # "Can you remix this song" is an operation; "Can you explain remixing" isn't.
        if not re.match(r"(?i)^\s*(?:can|could|would)\s+you\s+(?:please\s+)?"
                        r"(?:remix|remaster|parody|rewrite|rework|reimagine|adapt|make|create|write)\b",text):
            return None
    match=next(((name,m) for name,pattern in _MODES
                if (m:=re.search(pattern,text,re.I))),None)
    if not match:
        return None
    kind,hit=match
    # Music terms are required except when the current thread has a documented
    # song reference and an explicitly creative transform verb.
    if not _SONG_CUE.search(text) and not reference_available:
        return None
    if kind=="paraphrase" and not (_CREATE.search(text) or reference_available):
        return None
    # Research-first requests may still research, then transform. This parser
    # does not assert any search was performed.
    user_authored=bool(re.search(r"\b(?:my|our|i\s+wrote|i\s+made|we\s+wrote)\s+"
                                 r"(?:own\s+)?(?:song|lyrics?|verse|track|rap)\b",text,re.I))
    source_intent="user-authored" if user_authored else ("reference-abstract" if reference_available else "unspecified")
    preserve=bool(re.search(r"\b(?:keep|retain|preserve|unchanged|same)\b",text,re.I))
    return {"schema":"swrlz-music-transform-v1","mode":kind,
            "referenceAvailable":bool(reference_available),
            "sourceIntent":source_intent,"explicitPreservation":preserve}

def transformation_directive(contract: dict) -> str:
    mode=contract["mode"]
    actions={
        "remix":"Create fresh verses, new imagery and a genuinely new hook while adapting ABSTRACT structural/rhythmic ideas from the reference.",
        "parody":"Choose a concrete transformed comic or critical premise. Make the joke develop through setup, escalation and payoff; write independent lyrics, not near-copy with a few substitutions.",
        "remaster":"Polish lyric craft, narrative and phrasing. Preserve the user's supplied original song identity, sections, story and explicitly protected lines when authorized. Never promise audio mastering from a text-only operation.",
        "mashup":"Combine contrasting themes, sections and genre mechanics into ONE coherent original narrative. Do not stitch copyrighted words from separate recordings.",
        "paraphrase":"Rewrite as a purposeful new version. Honor explicitly preserved user-authored lines; avoid cosmetic synonym swaps and keep a complete arc.",
        "adaptation":"Translate the story and musical structure into the requested genre or perspective with original phrasing and appropriately changed meter.",
        "cover":"If the original is a published recording, write a new original interpretation rather than reproducing the original song's copyrighted lyrics.",
    }
    return (
        "\nSONG TRANSFORMATION CONTRACT ("+mode.upper()+"):\n"+
        actions[mode]+
        "\nReference identity, artists, credits and lyric fragments are not compositional material. "
        "Do not imitate a specific performer's signature wording or invent performer attributions. "
        "If a reference structure is verified, adapt the abstract section sequence, verse sizes, hook cadence and density; do NOT replace it with a generic 3-verse format unless the user requests that. "
        "Give different verses different concrete events, imagery, vocabulary and rhyme schemes. "
        "A returning chorus may repeat intentionally; a non-chorus verse may NOT be duplicated verbatim, lightly reworded or padded with one line repeated over and over. "
        "Write a distinct opening, progression, meaningful turn and closing. "
        "Prefer deliberate internal/end-rhyme and varied line lengths over stock phrases or filler. "
        "Keep the user's explicit constraints on verse count, sections, perspective, theme and preserved authored hooks. "
        "Use a copyable lyric block with section labels only where the requested form calls for them. "
        "Deliver the finished creative artifact without an assistant preface, commentary or unsupported claims of research. "
        "An audio remaster requires audio and an audio-processing workflow; a text request can only revise the composition/lyrics."
    )

def _line(value: str) -> str:
    return " ".join(_WORD.findall(value.casefold())).strip()

def _segments(text: str) -> tuple[list[tuple[str,list[str]]],list[str]]:
    """Retain repetitions only where they are structurally justified."""
    sections=[]
    current_kind="unlabeled"
    current=[]
    all_lines=[]
    def flush():
        nonlocal current
        if current: sections.append((current_kind,current));current=[]
    for raw in str(text or "").splitlines():
        stripped=raw.strip()
        if not stripped or stripped.startswith("\x60\x60\x60"):
            continue
        if re.match(r"(?i)^\s*(?:#{1,3}\s*)?(?:\*{1,2})?\s*title\s*:",stripped):
            continue
        label=_SECTION.match(stripped)
        if label:
            flush()
            current_kind=label.group("kind").casefold().replace(" ","-")
            continue
        if stripped.startswith(("---","___")):
            flush();continue
        normalized=_line(stripped)
        if not normalized:continue
        current.append(normalized)
        all_lines.append(normalized)
    flush()
    return sections,all_lines

def quality_review(text: str, *, allow_aab: bool = False) -> dict:
    """Return only observable defects; chorus repetition is not a defect."""
    sections,all_lines=_segments(text)
    faults=[]
    verse_bodies=[v for k,v in sections if k in ("verse","freestyle","cypher") and len(v)>=4]
    seen={}
    for idx,verse in enumerate(verse_bodies):
        token=tuple(verse)
        if token in seen:
            faults.append("duplicated-nonchorus-verse")
            break
        seen[token]=idx
    # Near-copy: line intersection / smaller verse length; meaningful variation
    # must exist in at least half of the lines, not just a changed label.
    for a in range(len(verse_bodies)):
        for b in range(a+1,len(verse_bodies)):
            x,y=verse_bodies[a],verse_bodies[b]
            ratio=sum((Counter(x)&Counter(y)).values())/max(1,min(len(x),len(y)))
            if ratio>=0.70:
                if "duplicated-nonchorus-verse" not in faults:
                    faults.append("near-duplicate-nonchorus-verses")
                break
    for kind,verse in sections:
        if kind in ("chorus","hook","refrain","intro","outro") or len(verse)<5:
            continue
        freq=Counter(verse)
        repeats=sum(c-1 for c in freq.values() if c>=2)
        # AAB deliberate doubled lines are a valid blues convention.
        if repeats>=max(3,(len(verse)+2)//3) and not allow_aab:
            faults.append("repetitive-nonchorus-padding")
            break
    lines=[x.strip() for x in str(text or "").splitlines() if x.strip()]
    if lines and _PREFACE.match(lines[0]):
        faults.append("assistant-preface-in-song")
    if lines and _PREFACE.match(lines[-1]):
        faults.append("assistant-outro-in-song")
    if len(all_lines)<3:
        faults.append("insufficient-lyric-content")
    return {"schema":"swrlz-music-quality-v1","status":"REJECT" if faults else "PASS",
            "reasons":list(dict.fromkeys(faults)),"sectionCount":len(sections),
            "verseCount":len(verse_bodies),"lyricLineCount":len(all_lines)}

def repair_directive(reasons: list[str], mode: str) -> str:
    return (
        "SONG QUALITY REWRITE ("+str(mode).upper()+"): The draft failed: "+
        ", ".join(str(x) for x in reasons[:5])+". "
        "Write the COMPLETE song again, not the evaluation. Keep all explicit user "
        "constraints and source separation. Make each non-chorus verse different "
        "in scene, event, rhyme/cadence and wording; do not just change labels. "
        "Only a chorus/refrain may repeat unchanged, unless the user explicitly "
        "requested a valid AAB or other deliberate repeating structure. "
        "Do not include an introduction or afterword. Output only the lyrics."
    )
