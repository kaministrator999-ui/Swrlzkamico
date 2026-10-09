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
MUSIC_CREATIVE_REFERENCE_POLICY="""STRUCTURE-ONLY SONG STUDY (the user asks for a wholly NEW work, including follow-up requests for another one):
- Study the PROVIDED song only as an abstract structural example: section sequence, section sizes, hook placement/repetition, relative line length, phrasing/cadence, rhyme positioning and variation.
- Do NOT reuse reference WORDS, catchphrases, hook language, title, plot, subject, images, slang, named people/places, or existing lyric lines. This includes the exact refrain and apparently generic but recognizable fragments.
- Select your OWN subject, title, vocabulary, hook, and rhyme words independently. Compose all fresh lines. Mirror structural mechanics where useful, not the previous writer's wording or persona.
- Sections and their line lengths are approximate scaffolding, not a mandate for mechanical copying. Maintain musical progression and natural phrasing.
- Write the finished requested song from its first section to a clean ending, with NO breakdown, instructional stage directions, or post-song analysis unless requested. Avoid padding with repeated chorus copies.
- The reference source and any earlier attempts MUST NOT be named, quoted, recalled or alluded to anywhere in the output. Do not write a tribute, homage, vibe description or source comparison.
- For a repeat request, invent a distinctly different original topic, scenario, rhyme vocabulary, and title instead of continuing or rewriting your last song.
- Use the independently selected creative premise as a concrete non-reference subject. Avoid generic urban, nightlife, status or wealth tropes unless the user explicitly asks for them.
- Preserve abstract approximate lyric-line totals, repetition density and phrase contours. Do not replace a long unlabeled song study with the conventional short four-line verse/pre-chorus/bridge template.
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





_CREATIVE_REFERENCE_POINTER=re.compile(
    r"(?i)\b(?:those|these|earlier|previous|provided|above|reference|study|from\s+that)\b"
)
_CREATIVE_MORE_REQUEST=re.compile(
    r"(?i)^\s*(?:(?:do|make|write|create|give(?:\s+me)?)\s+)?"
    r"(?:another|one\s+more)(?:\s+(?:one|song|rap|verse|track|version))?"
    r"(?:\s+(?:please|for\s+me))?\s*[.!?]*\s*$"
)
_CREATIVE_SOURCE_FOOTER=re.compile(r"(?i)\*\*lyrics source:\*\*")
_CREATIVE_FORM_WORDS=re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-]*")
# Novel, source-independent scenes prevent tiny CPU models from falling back
# on familiar rap topics. Source text only helps avoid lexical collisions.
_ORIGINAL_RAP_PREMISES=(
    "an astronomer rebuilding a remote observatory after an ice storm",
    "a beekeeper recovering an orchard through changing seasons",
    "an antique clockmaker restoring a watch stopped during an eclipse",
    "a marine biologist exploring a silent underwater cave",
    "a chef learning breadmaking from a village baker on a distant island",
    "a wildlife photographer tracking a rare bird in a mountain forest",
    "a ceramic artist mastering the heat of a traditional pottery kiln",
    "an inventor preparing a solar-powered glider for its maiden flight",
    "an archivist decoding a forgotten expedition journal",
    "a gardener reviving a greenhouse after a harsh winter",
    "a violin maker restoring an instrument found in an attic",
    "a mathematician solving a puzzle on a long train journey",
)
_REFERENCE_COMMON_WORDS={
    "about","again","also","and","are","been","but","can","for","from",
    "have","her","here","his","into","just","like","more","not","our",
    "that","the","their","them","then","there","these","they","this",
    "those","through","was","were","what","when","where","which","while",
    "who","will","with","would","you","your","verse","hook","chorus",
    "lyrics","source","song","title","another","original","write",
}


def _creative_premise(source_text: str, prior_creative: int) -> str:
    """Pick a wholly new subject with minimal reference-vocabulary overlap."""
    source={x for x in _CREATIVE_FORM_WORDS.findall(str(source_text).casefold())
            if len(x)>=4 and x not in _REFERENCE_COMMON_WORDS}
    ranked=[]
    for i,premise in enumerate(_ORIGINAL_RAP_PREMISES):
        words={x for x in _CREATIVE_FORM_WORDS.findall(premise.casefold()) if len(x)>=4}
        ranked.append((len(source.intersection(words)),i,premise))
    minimum=min(x[0] for x in ranked)
    candidates=[x[2] for x in ranked if x[0]==minimum]
    return candidates[prior_creative % len(candidates)]


_CREATIVE_POST_SOURCE_META=re.compile(r"(?i)^\s*(?:songwriters?|publishers?|powered\s+by|top\s+(?:lyrics|artists|songs)|writers?|copyright)\b")
_CREATIVE_CODE_FRAGMENT=re.compile(
    r"(?i)(?:^\s*[:@]?(?:class|style|id|v-if|v-for)\s*=|"
    r"^\s*[A-Za-z_$][A-Za-z0-9_$.\[\]]*\s*=\s*[^=]|"
    r"^\s*[}{}]\s*(?:else|if|$)|"
    r"^\s*(?:if|else\s+if|while|function)\s*\(|"
    r"=>|^\s*[^<>]*[{}]\s*$|"
    r"^\s*(?:artists?|albums?|genres?)\s*:)"
)


def _creative_display_form(body: str) -> list[dict[str,Any]]:
    """Compute song mechanics from the rendered lyric region; NEVER export words.

    Both formatted section-labelled songs and older plain lyric responses are
    supported. Page UI code, breadcrumb labels, titles and footer prose cannot
    become lyric-reference structure.
    """
    head=_CREATIVE_SOURCE_FOOTER.split(str(body or ""),1)[0]
    if not head.strip():
        return []
    lines=head.splitlines()
    region=[]
    if sum(1 for line in lines if line.strip()=="---")>=2:
        entered=False
        for raw in lines:
            line=raw.strip()
            if line=="---":
                if entered:
                    break
                entered=True
                continue
            if entered:
                region.append(raw)
    else:
        # Legacy v179 message was rendered without outer Markdown dividers.
        # Its intro precedes a blank line; everything thereafter is candidate
        # song body, NOT verified lyrics until filtered as an actual line.
        start=next((i+1 for i,x in enumerate(lines) if not x.strip()),len(lines))
        region=lines[start:]
    blocks=[]
    current=[]
    label_type="section"
    label_number=None
    label_repeat=None

    def flush():
        nonlocal current,label_type,label_number,label_repeat
        if len(current)>=2:
            blocks.append({
                "type":label_type,"number":label_number,
                "repeatCount":label_repeat,"lines":current[:64]
            })
        current=[]
        label_type="section"
        label_number=None
        label_repeat=None

    for raw in region[:500]:
        line=raw.strip()
        if _CREATIVE_POST_SOURCE_META.match(line):
            break
        if _CREATIVE_CODE_FRAGMENT.search(line):
            continue
        if not line or line.startswith("──"):
            flush()
            continue
        label=line.strip("* \t")
        parsed=parse_section_marker(label) if re.fullmatch(r"\[[^\]\n]+\]",label) else None
        if parsed and parsed.get("type")!="performer_cue":
            flush()
            label_type=str(parsed.get("type") or "section")
            label_number=parsed.get("number")
            label_repeat=parsed.get("repeatCount")
            continue
        if line.startswith(("**","http://","https://")):
            continue
        words=_CREATIVE_FORM_WORDS.findall(line)
        if 2<=len(words)<=24 and len(line)<=180:
            current.append(words)
    flush()
    return blocks[:16]


def _creative_form_sketch(blocks: list[dict[str,Any]]) -> dict[str,Any]:
    abstract=[]
    for block in blocks[:16]:
        word_lines=block["lines"]
        lengths=[len(words) for words in word_lines]
        if not lengths:
            continue
        endings=[]
        for words in word_lines:
            terminal=words[-1].casefold()
            m=re.search(r"[aeiouy][a-z]{0,3}$",terminal)
            endings.append(m.group(0) if m else "")
        repeated={e for e in endings if e and endings.count(e)>=2}
        labels={}
        for ending in endings:
            if ending in repeated and ending not in labels:
                labels[ending]=chr(65+len(labels)%26)
        ordered=sorted(lengths)
        abstract.append({
            "type":block["type"],"number":block["number"],
            "repeatCount":block["repeatCount"],
            "approxLineCount":len(lengths),
            "medianWordsPerLine":ordered[len(ordered)//2],
            "shortestWords":ordered[0],"longestWords":ordered[-1],
            "lineLengthContourWords":lengths[:32],
            "endRhymePlacementHint":[labels.get(e,"-") for e in endings[:32]],
        })
    # Repeated *positions*, never words: unlabeled lyric pages commonly put
    # the chorus and verse in one 50-60-line block without section markers.
    # This recurrence profile provides more useful mechanics than guessing a
    # conventional song template from the "section" placeholder.
    from collections import Counter
    all_lines=[tuple(word.casefold() for word in line)
               for block in blocks for line in block.get("lines",[])]
    counts=Counter(all_lines)
    recurrent=[i+1 for i,line in enumerate(all_lines)
               if len(line)>=2 and counts[line]>=3]
    runs=[]
    for pos in recurrent:
        if runs and pos==runs[-1][-1]+1:
            runs[-1].append(pos)
        else:
            runs.append([pos])
    bands=[{"fromLine":v[0],"toLine":v[-1],"lines":len(v)} for v in runs[:20]]
    return {
        "schema":"swrlz-creative-structural-reference-v3",
        "sourceContentExcluded":True,
        "sectionSequence":[x["type"] for x in abstract],
        "sections":abstract,
        "approxTotalLyricLines":len(all_lines),
        "recurringLineBands":bands,
        "usage":"Study abstract section placement, approximate lyric-line count, repetition density and rhyme positions. Invent every title, scene, image, hook and word independently. A continuous unlabeled song may contain recurring refrain bands; do not impose arbitrary pop section headings.",
    }


def creative_music_reference_projection(
    prompt: str, history: list[dict[str,Any]]
) -> tuple[list[dict[str,Any]], dict[str,Any] | None]:
    """Source-free model history for original-song requests AND 'another one'.

    Displayed chat and durable history are untouched. The inference-facing
    context must never include the referenced song *or earlier imitations*;
    either can accidentally anchor the 700M to the old hook and topic.
    """
    existing=list(history or [])
    source_idx=None
    for i in range(len(existing)-1,-1,-1):
        item=existing[i]
        if not isinstance(item,dict) or item.get("role")!="assistant":
            continue
        body=str(item.get("content") or item.get("text") or "")
        if _CREATIVE_SOURCE_FOOTER.search(body):
            source_idx=i
            break
    if source_idx is None:
        return existing,None

    explicit=bool(
        creative_music_transform_request(prompt)
        and _CREATIVE_REFERENCE_POINTER.search(str(prompt or ""))
    )
    continued=bool(
        _CREATIVE_MORE_REQUEST.fullmatch(str(prompt or ""))
        and any(
            isinstance(item,dict) and item.get("role")=="user"
            and creative_music_transform_request(str(item.get("content") or item.get("text") or ""))
            for item in existing[source_idx+1:]
        )
    )
    if not (explicit or continued):
        return existing,None

    source_body=str(existing[source_idx].get("content") or existing[source_idx].get("text") or "")
    structure=_creative_form_sketch(_creative_display_form(source_body))
    prior_creative=sum(1 for item in existing[source_idx+1:]
                       if isinstance(item,dict) and item.get("role")=="assistant")
    structure["originalCreativePremise"]=_creative_premise(source_body,prior_creative)
    structure["continuationNewComposition"]=continued
    structure["sourceHistoryExcluded"]=True
    structure["previousGeneratedLyricsExcluded"]=continued
    projected=[]
    for i,item in enumerate(existing):
        if not isinstance(item,dict):
            continue
        copy=dict(item)
        role=copy.get("role")
        if i==source_idx:
            replacement="Earlier assistant supplied a song as a STRUCTURAL reference. The source song's words and subject are hidden. ABSTRACT FORM ONLY: "+str(structure)
        elif i==source_idx-1 and role=="user":
            replacement="User supplied a previously existing song only as an abstract structural reference. Its identity and text must never be used in a new work."
        elif i>source_idx and continued and role=="assistant":
            replacement="An earlier original rap was already composed. Its words, title, subject and refrain are excluded. Compose ANOTHER distinctly new rap, using only the abstract form reference."
        elif i>source_idx and role=="user" and creative_music_transform_request(str(copy.get("content") or copy.get("text") or "")):
            replacement="User requested a brand-new rap using only the abstract mechanics of the earlier song, independently creating all words and subject matter."
        else:
            replacement=None
        if replacement is not None:
            copy["content"]=replacement
            if "text" in copy:
                copy["text"]=replacement
        projected.append(copy)
    return projected,structure


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
