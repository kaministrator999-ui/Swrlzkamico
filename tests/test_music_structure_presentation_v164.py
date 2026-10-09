"""v164 regression: music ontology + pre-chat structure/presentation compiler."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

from music_structure import (
    MUSIC_ONTOLOGY_PREFILL,
    creative_music_request,
    music_model_policy,
    parse_section_marker,
    structure_verified_music,
    compile_verified_music_presentation,
    music_structure_debug,
)
import model_router

PAGE="""Example Artist – Test Signal lyrics
Album: Demo Record
[Intro]
Signal intro opens softly
Copper pulse begins the motion
[Verse 1: Alpha]
First line of the first verse
Second line of the first verse
Third line of the first verse
Fourth line of the first verse
[Pre-Chorus: Alpha]
Pressure rises toward the hook
Cadence tightens for the turn
[Chorus: Alpha]
Hook line one returns
Hook line two returns
Hook line three returns
Hook line four returns
[Verse 2: Beta]
First line of the second verse
Second line of the second verse
Third line of the second verse
Fourth line of the second verse
[Bridge: Beta]
Bridge changes the perspective
Bridge changes the motion
"""

# This mirrors the verified extractor output: exact source lines, blank lines
# between accepted source sections, source markers omitted from raw extraction.
VERIFIED="""Signal intro opens softly
Copper pulse begins the motion

First line of the first verse
Second line of the first verse
Third line of the first verse
Fourth line of the first verse

Pressure rises toward the hook
Cadence tightens for the turn

Hook line one returns
Hook line two returns
Hook line three returns
Hook line four returns

First line of the second verse
Second line of the second verse
Third line of the second verse
Fourth line of the second verse

Bridge changes the perspective
Bridge changes the motion"""

marker=parse_section_marker("[Verse 2: Beta]")
assert marker,marker
assert marker["type"]=="verse",marker
assert marker["number"]==2,marker
assert marker["performer"]=="Beta",marker
assert marker["basis"]=="explicit_source_marker",marker

doc=structure_verified_music(
    VERIFIED,
    PAGE,
    subject='"Test Signal" by Example Artist',
    requested_scope="full-lyrics",
)
assert doc["workType"]=="song",doc
assert doc["sourceOrderPreserved"] is True,doc
assert doc["barSemantics"]["newlineEqualsBar"] is False,doc
assert doc["sectionCount"]==6,doc
assert doc["explicitSectionCount"]==6,doc

expected=[
    ("intro",None,None),
    ("verse",1,"Alpha"),
    ("pre_chorus",None,"Alpha"),
    ("chorus",None,"Alpha"),
    ("verse",2,"Beta"),
    ("bridge",None,"Beta"),
]
actual=[(s["type"],s["number"],s["performer"]) for s in doc["sections"]]
assert actual==expected,(actual,expected)
assert all(s["barCount"] is None for s in doc["sections"]),doc

presentation=compile_verified_music_presentation(
    doc,
    source_title="Example Artist – Test Signal Lyrics",
    source_url="https://example.test/test-signal",
)
text=presentation["presentationText"]
assert "**[Intro]**" in text,text
assert "**[Verse 1: Alpha]**" in text,text
assert "**[Pre-Chorus: Alpha]**" in text,text
assert "**[Chorus: Alpha]**" in text,text
assert "**[Verse 2: Beta]**" in text,text
assert "**[Bridge: Beta]**" in text,text
assert text.index("**[Intro]**") < text.index("**[Verse 1: Alpha]**") < text.index("**[Chorus: Alpha]**") < text.index("**[Bridge: Beta]**"),text
for line in VERIFIED.replace("\n\n","\n").splitlines():
    assert line in text,(line,text)
assert presentation["sourceTextRewritten"] is False,presentation

debug=music_structure_debug(doc,presentation)
assert debug["newlineEqualsBar"] is False,debug
assert debug["sectionCount"]==6,debug
assert debug["explicitSectionCount"]==6,debug
assert debug["presentationChars"]==len(text),debug
assert len(debug["presentationSha256"])==64,debug
assert all("lines" not in section for section in debug["sections"]),debug

# Chat/Model Router must render the upstream-compiled payload verbatim rather
# than trying to rediscover song structure itself.
result={
    "modelContext":{
        "verifiedLyrics":{
            "presentationText":text,
            "requestedScope":"full-lyrics",
            "lyricExtract":VERIFIED,
            "subject":'"Test Signal" by Example Artist',
            "sourceUrl":"https://example.test/test-signal",
            "sourceTitle":"Example Artist – Test Signal Lyrics",
        }
    }
}
rendered=model_router._lyrics_retrieval_payload(result,"give me the full lyrics")
assert rendered==text,(rendered,text)

freestyle=creative_music_request("Hit a boom bap freestyle")
assert freestyle["workType"]=="freestyle",freestyle
assert freestyle["defaultStructure"]=="continuous_verse",freestyle
assert freestyle["inventSectionLabels"] is False,freestyle
assert freestyle["repeatedChorusByDefault"] is False,freestyle

song=creative_music_request("Write a complete rap song")
assert song["workType"]=="song",song
assert song["defaultStructure"]=="song_sections",song

policy=music_model_policy("write me a freestyle with hard bars")
assert policy==MUSIC_ONTOLOGY_PREFILL,policy
assert "Never assume one newline equals one musical bar." in policy,policy
assert "FREESTYLE defaults to one continuous verse" in policy,policy
assert "BRIDGE is a contrasting section" in policy,policy

print("music-structure-presentation-v164 PASS")

# v177 Dragon Chat (26), refined by user's explicit correction:
# Previous song = FORM study only. Nothing in the model's messages should
# contain the reference song's actual vocabulary, hook, artist or title.
from music_structure import (
    creative_music_reference_projection, creative_music_transform_request,
    MUSIC_CREATIVE_REFERENCE_POLICY,
)
CREATIVE_FOLLOWUP="Now can you use those lyrics as something to study and write me a whole new rap song"
FORM_HISTORY=[
    {"role":"user","content":"Can you provide lyrics to Test Signal by Example Artist"},
    {"role":"assistant","content":"""Okay — here is verified lyric text:

**[Verse 1]**
Silver leviathans climb through the evening
Magnetic lanterns are humming beneath us
Scarlet compasses spin in the harbor
Obsidian comets fly over the water

────────

**[Hook x2]**
Cobalt umbrellas glow under the rainfall
Tangerine rockets return to the rooftop

────────

**[Outro x2]**
Paper constellations float over the highway
Velvet horizons illuminate dawn
Songwriters: Distinct Writer
Publisher: Example Publishing
Powered by LyricFind
Top Lyrics
**Lyrics source:** Example Artist — https://example.test/example
"""},
]
snapshot=[dict(x) for x in FORM_HISTORY]
projection,template=creative_music_reference_projection(CREATIVE_FOLLOWUP,FORM_HISTORY)
assert template and template["sourceContentExcluded"] is True,template
assert template["sectionSequence"]==["verse","hook","outro"],template
assert [x["approxLineCount"] for x in template["sections"]]==[4,2,2],template
assert [x["repeatCount"] for x in template["sections"]]==[None,2,2],template
assert template["sections"][0]["lineLengthContourWords"]==[6,6,6,6],template
assert len(template["sections"][0]["endRhymePlacementHint"])==4,template
assert all(label=="-" or label in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for section in template["sections"] for label in section["endRhymePlacementHint"]),template
assert 5<=template["sections"][0]["medianWordsPerLine"]<=12,template
assert len(projection)==len(FORM_HISTORY)==2,projection
assert "STRUCTURAL reference" in projection[1]["content"],projection
for forbidden in ["Silver leviathans","Magnetic lanterns","Cobalt umbrellas","Tangerine rockets","Distinct Writer","Test Signal","Example Artist"]:
    assert forbidden not in str(projection),(forbidden,projection)
    assert forbidden not in str(template),(forbidden,template)
assert FORM_HISTORY==snapshot,"Projection modified durable original chat log"
assert "Do NOT reuse reference WORDS" in MUSIC_CREATIVE_REFERENCE_POLICY
assert "section sequence" in MUSIC_CREATIVE_REFERENCE_POLICY
assert creative_music_transform_request(CREATIVE_FOLLOWUP)
assert creative_music_reference_projection("What do those lyrics mean?",FORM_HISTORY)[1] is None
assert creative_music_reference_projection("Write an unrelated new song",FORM_HISTORY)[1] is None
print("structure-only-reference-no-lexical-borrowing-v177 PASS")

UNLABELED_HISTORY=[
    {"role":"user","content":"Provide lyrics for a reference song"},
    {"role":"assistant","content":"""Here are verified lyrics:
---
Purple lanterns drift past the doorway
Each silver comet falls through the rain

────────

The copper river glows in the darkness
Our hidden compass points into dawn
---
**Lyrics source:** Source — https://example.test/lyric
"""},
]
unlabeled_projection,unlabeled_plan=creative_music_reference_projection(CREATIVE_FOLLOWUP,UNLABELED_HISTORY)
assert unlabeled_plan and unlabeled_plan["sourceContentExcluded"],unlabeled_plan
assert [section["type"] for section in unlabeled_plan["sections"]]==["section","section"],unlabeled_plan
assert [section["approxLineCount"] for section in unlabeled_plan["sections"]]==[2,2],unlabeled_plan
assert "Purple lanterns" not in str(unlabeled_projection),unlabeled_projection
assert "copper river" not in str(unlabeled_projection).lower(),unlabeled_projection
print("unlabeled-song-structure-only-projection-v177 PASS")


