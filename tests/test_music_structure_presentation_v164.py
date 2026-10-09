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



# v180 Dragon Chat (29) triple-turn regression: an unlabeled verified source
# is displayed without "---" separators and has page JS prefix; first rap
# copies source words; "Do another one" then imitates that previous answer.
# Model-facing history MUST contain NEITHER the source words NOR generated
# previous imitations, while preserving durable chat history unchanged.
UNFORMATTED_SOURCE="""Okay — here is the full source I fetched:

peakY = y;
showHeader = false;
} else if (y 20) {
:class="showHeader ? 'translate-y-0' : '-translate-y-full md:translate-y-0'"
Artists: E /
Test Signal

Distant copper ships float to the sunrise
The midnight lighthouse spins above the shore
The emerald oceans whisper by the lantern
Our velvet signals echo through the rain

Hollow winter engines cross the station
Silver morning railway carries hidden secrets
Bright mossy planets weave beneath the water
Cobalt window shadows move into the hills

Distant copper ships float to the sunrise
The midnight lighthouse spins above the shore

**Lyrics source:** Example Artist — https://example.test/verified-song
"""
LIVE_29=[
    {"role":"user","content":"Can you provide lyrics to Test Signal by Example Artist"},
    {"role":"assistant","content":UNFORMATTED_SOURCE},
]
live_original=[dict(x) for x in LIVE_29]
fresh_projected,fresh_form=creative_music_reference_projection(CREATIVE_FOLLOWUP,LIVE_29)
assert fresh_form and fresh_form["sourceContentExcluded"] is True,fresh_form
assert fresh_form["sectionSequence"]==["section","section","section"],fresh_form
assert [x["approxLineCount"] for x in fresh_form["sections"]]==[4,4,2],fresh_form
assert len(fresh_projected)==2
assert LIVE_29==live_original
for bad in ["Test Signal","Example Artist","Distant copper","midnight lighthouse","peakY","showHeader","emeralD oceans","lyric source"]:
    assert bad.lower() not in str(fresh_projected).lower(),(bad,fresh_projected)
    assert bad.lower() not in str(fresh_form).lower(),(bad,fresh_form)

FIRST_DRAFT="""My new creative work inspired by Test Signal by Example Artist:
**Title: The Test Signal Awakens**
The midnight lighthouse spins above the shore
We found the ocean, copper and more
**Chorus:** Test Signal never stops.
**Flow & Feel:** Source-inspired writing."""
FULL_29=[
    *LIVE_29,
    {"role":"user","content":CREATIVE_FOLLOWUP},
    {"role":"assistant","content":FIRST_DRAFT},
]
before=[dict(x) for x in FULL_29]
second_projected,second_form=creative_music_reference_projection("Do another one",FULL_29)
assert second_form and second_form["continuationNewComposition"] is True,second_form
assert second_form["sourceContentExcluded"] and second_form["previousGeneratedLyricsExcluded"],second_form
assert second_form["sections"]==fresh_form["sections"],(second_form,fresh_form)
for bad in ["Test Signal","Example Artist","midnight lighthouse","copper","ocean","source-inspired","peakY","Flow & Feel:"]:
    assert bad.lower() not in str(second_projected).lower(),(bad,second_projected)
assert len(second_projected)==len(FULL_29)==4,second_projected
assert FULL_29==before,"Creative projection altered persisted history"
assert creative_music_reference_projection("What was the old song title?",FULL_29)[1] is None
print("live-29-first-and-another-one-source-isolation-v180 PASS")
