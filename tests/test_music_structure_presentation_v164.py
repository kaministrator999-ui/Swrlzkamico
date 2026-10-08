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
