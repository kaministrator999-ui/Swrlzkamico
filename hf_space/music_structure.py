"""Music structure cognition + deterministic presentation compiler for §wyrlz.

This module does not retrieve evidence and does not rewrite verified source lines.
It gives the 700M compact musical-form semantics and turns already-verified lyric
text into a structured document before Chat rendering.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

MUSIC_STRUCTURE_SCHEMA="swrlz-music-structure-v1"
MUSIC_PRESENTATION_SCHEMA="swrlz-music-presentation-v1"

# Markdown horizontal rule renders full-width in Chat. Internal lyric section
# separators stay deliberately shorter to create a mobile-first visual hierarchy.
LYRIC_OUTER_DIVIDER="---"
LYRIC_SECTION_DIVIDER="────────"

_SECTION_RE=re.compile(
    r"^\s*\[?\s*(?P<kind>"
    r"intro|outro|interlude|pre[-\s]?chorus|post[-\s]?chorus|chorus|hook|refrain|bridge|"
    r"verse(?:\s*(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten))?|"
    r"freestyle|cypher"
    r")\b(?P<tail>[^\]\n]{0,100})\]?\s*:?[\s]*$",
    re.I,
)

_MUSIC_CUES=re.compile(
    r"\b(?:music|song|rap|rapper|lyrics?|lyrical|verse|chorus|hook|refrain|bridge|"
    r"pre[-\s]?chorus|intro|outro|bars?|freestyle|cypher|battle\s+rap|flow|rhyme)\b",
    re.I,
)

_NUMBER_WORDS={
    "one":1,"two":2,"three":3,"four":4,"five":5,
    "six":6,"seven":7,"eight":8,"nine":9,"ten":10,
}


MUSIC_ONTOLOGY_PREFILL="""MUSIC STRUCTURE COGNITION (authoritative form semantics for relevant music turns):
- BAR has two contextual meanings: technically a musical measure; in rap slang it may mean a line/punchline. Never assume one newline equals one musical bar.
- VERSE is a main lyrical section made of lines/bars. A long verse does not become several verses merely because it is long.
- CHORUS is a recurring central section. HOOK is the memorable recurring phrase/section and may be shorter than a chorus.
- PRE-CHORUS leads into a chorus. REFRAIN is recurring material that may occur inside a verse instead of being a standalone chorus.
- BRIDGE is a contrasting section that interrupts the normal verse/chorus cycle. INTRO and OUTRO open/close the work. INTERLUDE is a distinct transitional section.
- FREESTYLE defaults to one continuous verse with natural line breaks and no invented Verse/Chorus/Bridge/Hook labels unless the user or source explicitly supplies another structure.
- CYPHER may contain consecutive verses by multiple performers; preserve performer boundaries when supplied.
- FULL SONG may contain intro, verses, pre-choruses, choruses/hooks, bridge/interlude, outro, repeats, and multiple performers.
- Explicit source/request section labels are authoritative. Preserve their order and wording. Infer a label only when confidence is high; otherwise leave the section unlabeled.
- Presentation may organize and label verified material, but must not paraphrase, reorder, invent, or silently 'correct' the underlying verified lyric lines."""


def music_model_policy(prompt: str) -> str:
    """Return compact ontology only for music-related turns."""
    return MUSIC_ONTOLOGY_PREFILL if _MUSIC_CUES.search(str(prompt or "")) else ""




# Only for user requests that CREATE a song using earlier lyrics as a guide.
# A reference can inform high-level craft without reusing copyrighted lines.
MUSIC_CREATIVE_REFERENCE_POLICY="""STRUCTURE-ONLY SONG STUDY (current user asks for a wholly NEW work):
- Study the PROVIDED song only as an abstract structural example: section sequence, section sizes, hook placement/repetition, relative line length, phrasing/cadence, rhyme positioning and variation.
- Do NOT reuse reference WORDS, catchphrases, hook language, title, plot, subject, images, slang, named people/places, or existing lyric lines. This includes the exact refrain and apparently generic but recognizable fragments.
- Select your OWN subject, title, vocabulary, hook, and rhyme words independently. Compose all fresh lines. Mirror structural mechanics where useful, not the previous writer's wording or persona.
- Sections and their line lengths are approximate scaffolding, not a mandate for mechanical copying. Maintain musical progression and natural phrasing.
- Write the finished requested song from its first section to a clean ending, with NO breakdown, instructional stage directions, or post-song analysis unless requested. Avoid padding with repeated chorus copies.
- Use a fenced Markdown code block for the complete new song; include its heading/sections inside the block."""

def creative_music_transform_request(prompt: str) -> bool:
    """Recognize a creation/transformation request that merely mentions lyrics.

    A lyric reference is input context, not evidence that the user asked to
    retrieve a song. This is intentionally limited to clear creative verbs and
    requested musical outputs; do not turn general lyric lookup into generation.
    """
    text=" ".join(str(prompt or "").split())
    # Explicit analysis of lyrics is not itself a song-writing request.
    if re.search(r"\b(?:write|create|compose|generate|draft|craft|make|rewrite|rework|adapt|transform|turn)\b"
                 r".{0,95}\b(?:review|summary|explanation|analysis)\s+(?:of|about)\b",text,re.I):
        return False
    return bool(re.search(
        r"\b(?:write|create|compose|generate|draft|craft|make|rewrite|rework|adapt|transform|turn)\b"
        r".{0,100}\b(?:original|new|rap|song|verse|chorus|hook|bars?|lyrics?|freestyle|cypher|track)\b"
        r"|\b(?:freestyle|rap)\s+(?:off|over|using|based\s+on)\b",
        text,re.I,
    ))


def creative_music_request(prompt: str) -> dict[str,Any]:
    """Classify requested creative form without asking the model to invent structure rules."""
    text=str(prompt or "")
    low=text.casefold()
    if "freestyle" in low:
        return {
            "schema":"swrlz-music-request-v1",
            "workType":"freestyle",
            "defaultStructure":"continuous_verse",
            "inventSectionLabels":False,
            "repeatedChorusByDefault":False,
            "reason":"explicit-freestyle-request",
        }
    if re.search(r"\bcypher\b",low):
        return {
            "schema":"swrlz-music-request-v1",
            "workType":"cypher",
            "defaultStructure":"consecutive_performer_verses",
            "inventSectionLabels":False,
            "repeatedChorusByDefault":False,
            "reason":"explicit-cypher-request",
        }
    if re.search(r"\b(?:full|complete)\s+(?:rap\s+)?song\b|\bsong\b",low):
        return {
            "schema":"swrlz-music-request-v1",
            "workType":"song",
            "defaultStructure":"song_sections",
            "inventSectionLabels":False,
            "repeatedChorusByDefault":False,
            "reason":"song-request",
        }
    if re.search(r"\b(?:verse|bars?)\b",low):
        return {
            "schema":"swrlz-music-request-v1",
            "workType":"verse",
            "defaultStructure":"single_verse",
            "inventSectionLabels":False,
            "repeatedChorusByDefault":False,
            "reason":"verse-or-bars-request",
        }
    return {
        "schema":"swrlz-music-request-v1",
        "workType":"music_text",
        "defaultStructure":"preserve-requested-form",
        "inventSectionLabels":False,
        "repeatedChorusByDefault":False,
        "reason":"generic-music-request",
    }


def _normalize_kind(raw: str) -> tuple[str,int|None]:
    low=" ".join(str(raw or "").strip().casefold().replace("-"," ").split())
    number=None
    if low.startswith("verse"):
        suffix=low[5:].strip()
        if suffix:
            if suffix.isdigit():
                number=int(suffix)
            else:
                number=_NUMBER_WORDS.get(suffix)
        return "verse",number
    aliases={
        "pre chorus":"pre_chorus",
        "post chorus":"post_chorus",
    }
    return aliases.get(low,low.replace(" ","_")),number


def parse_section_marker(line: str) -> dict[str,Any] | None:
    """Parse explicit musical markers and performer-only cues without inventing form."""
    raw=str(line or "").strip()
    match=_SECTION_RE.fullmatch(raw)
    if match:
        kind_raw=match.group("kind").strip()
        section_type,number=_normalize_kind(kind_raw)
        tail=str(match.group("tail") or "").strip()
        performer=""
        if tail.startswith(":"):
            performer=tail[1:].strip()
        elif ":" in tail:
            performer=tail.split(":",1)[1].strip()
        performer=performer.strip(" []:-")
        # Repeat counts may be authored either with or without a colon:
        # [Hook: x2], [Hook x2], [Outro 2x], [Chorus: repeat 2 times].
        # These are section metadata, never performer names. Keep rawLabel.
        repeat_source=performer or (tail if not ":" in tail else "")
        repeat_match=re.fullmatch(r"(?i)(?:x\s*(\d+)|(\d+)\s*x|repeat\s+(\d+)\s+times?)",repeat_source.strip())
        repeat_count=None
        if repeat_match:
            repeat_count=int(next(group for group in repeat_match.groups() if group is not None))
            performer=""
        return {
            "rawLabel":raw,
            "type":section_type,
            "number":number,
            "performer":performer or None,
            "repeatCount":repeat_count,
            "confidence":1.0,
            "basis":"explicit_source_marker",
        }

    performer_match=re.fullmatch(r"\[\s*([A-Za-z0-9][^\]\n:]{0,70})\s*:\s*\]",raw)
    if performer_match:
        performer=performer_match.group(1).strip()
        return {
            "rawLabel":raw,
            "type":"performer_cue",
            "number":None,
            "performer":performer or None,
            "confidence":1.0,
            "basis":"explicit_source_performer_marker",
        }
    return None




def creative_music_reference_projection(
    prompt: str, history: list[dict[str,Any]]
) -> tuple[list[dict[str,Any]], dict[str,Any] | None]:
    """Replace a previously displayed lyric body with a content-free structure sketch.

    Only the MODEL-facing history is transformed, never the stored chat log.
    Returning the original history when there is no explicit lyric-reference
    creation request preserves ordinary conversational continuity.
    """
    existing=list(history or [])
    if not creative_music_transform_request(prompt) or not re.search(
        r"\b(?:those|these|earlier|previous|provided|above|reference|study)\b",
        str(prompt or ""),re.I,
    ):
        return existing,None

    for i in range(len(existing)-1,-1,-1):
        message=existing[i]
        if not isinstance(message,dict) or message.get("role")!="assistant":
            continue
        body=str(message.get("content") or message.get("text") or "")
        if not re.search(r"(?i)\*\*lyrics source:\*\*",body):
            continue
        sections=[]
        current=None
        for raw_line in body.splitlines()[:500]:
            line=raw_line.strip()
            if re.match(r"(?i)^\*{0,2}(?:lyrics source|songwriters?|publisher|powered by|top lyrics|top artists)\b",line):
                break
            label=line.strip("* \t")
            parsed=parse_section_marker(label) if label.startswith("[") and label.endswith("]") else None
            if parsed and parsed.get("type")!="performer_cue":
                current={"type":parsed.get("type"),"number":parsed.get("number"),
                         "repeatCount":parsed.get("repeatCount"),"lengths":[],"endings":[]}
                sections.append(current)
                continue
            if current is None or not line or line.startswith(("---","──","**Lyrics source:")):
                continue
            words=re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*",line)
            if 1<=len(words)<=30 and len(line)<=210:
                current["lengths"].append(len(words))
                # Rough orthographic ending groups, NOT a phonetic claim.
                # Emit only abstract pattern labels, never the rhyme words.
                terminal=words[-1].casefold()
                ending_match=re.search(r"[aeiouy][a-z]{0,3}$",terminal)
                current["endings"].append(ending_match.group(0) if ending_match else "")
        if not sections:
            # Some verified pages have no Verse/Hook tags. Read ONLY the
            # rendered lyric-document region, not the introduction or credits.
            # An unlabeled song still must not expose its old words to the
            # creative model as raw history.
            in_body=False
            current={"type":"section","number":None,"repeatCount":None,
                     "lengths":[],"endings":[]}
            for raw_line in body.splitlines()[:500]:
                line=raw_line.strip()
                if line=="---":
                    if not in_body:
                        in_body=True
                        continue
                    break
                if not in_body:
                    continue
                if re.match(r"(?i)^\\*{0,2}(?:lyrics source|songwriters?|publisher|powered by|top lyrics|top artists)\\b",line):
                    break
                if line.startswith("──"):
                    if current["lengths"]:
                        sections.append(current)
                    current={"type":"section","number":None,"repeatCount":None,
                             "lengths":[],"endings":[]}
                    continue
                words=re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\\-]*",line)
                if 1<=len(words)<=30 and len(line)<=210:
                    current["lengths"].append(len(words))
                    term=words[-1].casefold()
                    ending_match=re.search(r"[aeiouy][a-z]{0,3}$",term)
                    current["endings"].append(ending_match.group(0) if ending_match else "")
            if current["lengths"]:
                sections.append(current)
        if not sections:
            continue
        abstract=[]
        for section in sections[:16]:
            lengths=section["lengths"]
            if not lengths:
                continue
            ordered=sorted(lengths)
            endings=section["endings"]
            repeated={ending for ending in endings if ending and endings.count(ending)>=2}
            group_labels={}
            for ending in endings:
                if ending in repeated and ending not in group_labels:
                    group_labels[ending]=chr(65+(len(group_labels)%26))
            abstract.append({
                "type":section["type"],"number":section["number"],
                "repeatCount":section["repeatCount"],
                "approxLineCount":len(lengths),
                "medianWordsPerLine":ordered[len(ordered)//2],
                "shortestWords":ordered[0],"longestWords":ordered[-1],
                "lineLengthContourWords":lengths[:24],
                "endRhymePlacementHint":["-" if ending not in repeated else group_labels[ending] for ending in endings[:24]],
            })
        if not abstract:
            continue
        plan={
            "schema":"swrlz-creative-structural-reference-v1",
            "sourceContentExcluded":True,
            "sectionSequence":[x["type"] for x in abstract],
            "sections":abstract,
            "usage":"Study form and line-length dynamics only. New topic, new vocabulary, new title, new refrain. No original lyric lines or distinctive phrases.",
        }
        projected=[dict(item) if isinstance(item,dict) else item for item in existing]
        replacement="Earlier assistant supplied a verified song as a STRUCTURAL reference. The actual words are intentionally excluded from creative-generation context. ABSTRACT FORM: "+str(plan)
        projected[i]["content"]=replacement
        if "text" in projected[i]:
            projected[i]["text"]=replacement
        if i>0 and isinstance(projected[i-1],dict) and projected[i-1].get("role")=="user":
            previous=str(projected[i-1].get("content") or projected[i-1].get("text") or "")
            if re.search(r"(?i)\blyrics?\b",previous):
                projected[i-1]["content"]="User requested an existing song as a structural study reference; title and artist are not part of the new song."
                if "text" in projected[i-1]:
                    projected[i-1]["text"]=projected[i-1]["content"]
        return projected,plan
    return existing,None

def _norm_line(value: str) -> str:
    return re.sub(r"\s+"," ",str(value or "").strip()).casefold()


def _blocks(text: str) -> list[list[str]]:
    out=[]
    for chunk in re.split(r"\n\s*\n+",str(text or "").strip()):
        lines=[line.rstrip() for line in chunk.splitlines() if line.strip()]
        if lines:
            out.append(lines)
    return out


def structure_verified_music(
    lyric_extract: str,
    page_extract: str = "",
    *,
    subject: str = "",
    requested_scope: str = "lyrics",
) -> dict[str,Any]:
    """Map verified text to source markers without changing its wording or order."""
    raw=str(lyric_extract or "").strip()
    blocks=_blocks(raw)
    page_lines=[line.rstrip() for line in str(page_extract or "").replace("\r\n","\n").replace("\r","\n").splitlines()]
    normalized_page=[_norm_line(line) for line in page_lines]
    cursor=0
    sections=[]

    for index,lines in enumerate(blocks,1):
        first=_norm_line(lines[0]) if lines else ""
        found=None
        if first:
            for pos in range(cursor,len(page_lines)):
                if normalized_page[pos]==first:
                    found=pos
                    break
        marker=None
        if found is not None:
            # Prefer the nearest explicit source marker before the first verified line.
            for pos in range(found-1,max(-1,cursor-12),-1):
                candidate=parse_section_marker(page_lines[pos])
                if candidate:
                    marker=candidate
                    break
            cursor=found+max(1,len(lines))
        if marker:
            section={**marker}
        else:
            section={
                "rawLabel":None,
                "type":"section",
                "number":None,
                "performer":None,
                "confidence":0.55,
                "basis":"unlabeled_verified_block",
            }
        section.update({
            "index":index,
            "lines":list(lines),
            "lineCount":len(lines),
            # A newline is presentation/text structure, not proof of a musical bar.
            "barCount":None,
            "barCountBasis":"not_inferred_from_line_breaks",
        })
        sections.append(section)

    explicit_musical=sum(1 for section in sections if section.get("basis")=="explicit_source_marker")
    explicit_performer=sum(1 for section in sections if section.get("basis")=="explicit_source_performer_marker")
    explicit=explicit_musical+explicit_performer
    work_type="song" if explicit or requested_scope in ("full-lyrics","first-verse") else "music_text"
    if explicit_musical:
        structure_basis="explicit_musical_source_markers"
    elif explicit_performer:
        structure_basis="explicit_performer_source_markers_without_invented_form"
    else:
        structure_basis="verified_text_blocks_without_invented_labels"
    return {
        "schema":MUSIC_STRUCTURE_SCHEMA,
        "subject":subject,
        "workType":work_type,
        "requestedScope":requested_scope,
        "structureBasis":structure_basis,
        "explicitSectionCount":explicit,
        "explicitMusicalSectionCount":explicit_musical,
        "explicitPerformerCueCount":explicit_performer,
        "sectionCount":len(sections),
        "sections":sections,
        "barSemantics":{
            "technical":"musical_measure",
            "rapSlang":"line_or_punchline_contextually",
            "newlineEqualsBar":False,
        },
        "sourceOrderPreserved":True,
        "textMutationAllowed":False,
    }


def compile_verified_music_presentation(
    document: dict[str,Any],
    *,
    source_title: str,
    source_url: str,
    intro: str = "",
) -> dict[str,Any]:
    """Compile already-verified text into render-ready Markdown without rewriting lines."""
    subject=str(document.get("subject") or "the requested song").strip()
    sections=document.get("sections") if isinstance(document.get("sections"),list) else []
    rendered=[]
    for section in sections:
        if not isinstance(section,dict):
            continue
        lines=[str(line) for line in (section.get("lines") or []) if str(line).strip()]
        if not lines:
            continue
        label=str(section.get("rawLabel") or "").strip()
        if label:
            rendered.append(f"**{label}**\n" + "\n".join(lines))
        else:
            rendered.append("\n".join(lines))
    body=(f"\n\n{LYRIC_SECTION_DIVIDER}\n\n").join(rendered).strip()
    if not intro:
        intro=f"Okay — here’s the verified lyric text for **{subject}**:"
    footer=f"**Lyrics source:** {source_title} — {source_url}".strip()

    parts=[]
    if intro:
        parts.append(intro)
    if body:
        parts.append(LYRIC_OUTER_DIVIDER)
        parts.append(body)
        parts.append(LYRIC_OUTER_DIVIDER)
    if footer:
        parts.append(footer)
    text="\n\n".join(parts).strip()
    return {
        "schema":MUSIC_PRESENTATION_SCHEMA,
        "subject":subject,
        "presentationText":text,
        "presentationChars":len(text),
        "presentationSha256":hashlib.sha256(text.encode("utf-8","replace")).hexdigest() if text else "",
        "sectionCount":len(rendered),
        "sourceOrderPreserved":True,
        "sourceTextRewritten":False,
        "dividerPresentation":{
            "outer":LYRIC_OUTER_DIVIDER,
            "inner":LYRIC_SECTION_DIVIDER,
            "outerMeaning":"lyric_document_boundary",
            "innerMeaning":"lyric_section_transition",
            "blankLinesAroundDividers":True,
            "mobileFirst":True,
        },
    }


def music_structure_debug(document: dict[str,Any], presentation: dict[str,Any] | None = None) -> dict[str,Any]:
    """Bounded export-safe summary; no lyric body text."""
    sections=[]
    for section in (document.get("sections") or [])[:24]:
        if not isinstance(section,dict):
            continue
        sections.append({
            "index":int(section.get("index") or 0),
            "rawLabel":str(section.get("rawLabel") or "")[:120],
            "type":str(section.get("type") or "section")[:40],
            "number":section.get("number") if isinstance(section.get("number"),int) else None,
            "performer":str(section.get("performer") or "")[:100],
            "repeatCount":section.get("repeatCount") if isinstance(section.get("repeatCount"),int) else None,
            "confidence":float(section.get("confidence") or 0.0),
            "basis":str(section.get("basis") or "")[:80],
            "lineCount":int(section.get("lineCount") or 0),
            "barCount":None,
        })
    return {
        "schema":"swrlz-music-structure-debug-v1",
        "workType":str(document.get("workType") or "")[:40],
        "requestedScope":str(document.get("requestedScope") or "")[:40],
        "structureBasis":str(document.get("structureBasis") or "")[:80],
        "sectionCount":int(document.get("sectionCount") or 0),
        "explicitSectionCount":int(document.get("explicitSectionCount") or 0),
        "explicitMusicalSectionCount":int(document.get("explicitMusicalSectionCount") or 0),
        "explicitPerformerCueCount":int(document.get("explicitPerformerCueCount") or 0),
        "sourceOrderPreserved":bool(document.get("sourceOrderPreserved")),
        "newlineEqualsBar":False,
        "sections":sections,
        "presentationChars":int((presentation or {}).get("presentationChars") or 0),
        "presentationSha256":str((presentation or {}).get("presentationSha256") or "")[:80],
        "dividerPresentation":(presentation or {}).get("dividerPresentation") if isinstance((presentation or {}).get("dividerPresentation"),dict) else None,
    }
