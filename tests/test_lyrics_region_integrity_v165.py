"""v165 regression: reject recommendation-body false positives, preserve performer cues, and prefer structured sources."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools
from music_structure import structure_verified_music, compile_verified_music_presentation

PROMPT="Can you provide the lyrics to test signal by example artist"
plan=online_tools.classify_online_request(PROMPT,[],{},None)
assert plan["contentMode"]=="lyrics-verification",plan
assert plan["requestedScope"]=="full-lyrics",plan
assert plan["subject"]=='"test signal" by example artist',plan

PERFORMER_PAGE="""Test Signal lyrics
Example Artist Lyrics
"Test Signal"
[Alpha:]

Signal opens in the midnight

Current runs beneath the station

Every circuit holds the cadence

Noisy sparks become the motion

[Beta:]

Second voice enters the pattern

Another current crosses over

Final signal keeps on moving

Closing current ends the motion

Writer(s): Example Writer
Krizz Example - "Wrong Recommendation" This unrelated song should never become the requested body
Wrong line one
Wrong line two
Wrong line three
"""

SNIPPET="Example Artist Test Signal lyrics Signal opens in the midnight Current runs beneath the station Every circuit holds the cadence Noisy sparks become the motion"

extracted=online_tools._lyrics_extract_candidate(PERFORMER_PAGE,"full-lyrics",plan["subject"])
assert extracted,extracted
assert "Signal opens in the midnight" in extracted,extracted
assert "Second voice enters the pattern" in extracted,extracted
assert "Wrong Recommendation" not in extracted,extracted
assert "Wrong line one" not in extracted,extracted
assert online_tools._lyrics_sequence_span(SNIPPET,extracted,plan["subject"])>=4

# Recreate the live v164 false-positive shape: an unrelated recommendation body
# can share a few words, but must fail because there is no contiguous lyric sequence.
WRONG_BODY="""Krizz Example - "Wrong Recommendation"
Signal machine in another song
Current artist makes another motion
Every station has some cadence
Unrelated body keeps going"""
consistent,overlap,total=online_tools._lyrics_snippet_consistent(SNIPPET,WRONG_BODY,plan["subject"])
assert consistent is False,(consistent,overlap,total)
assert online_tools._lyrics_sequence_span(SNIPPET,WRONG_BODY,plan["subject"])<4

doc=structure_verified_music(extracted,PERFORMER_PAGE,subject=plan["subject"],requested_scope="full-lyrics")
assert doc["explicitPerformerCueCount"]==2,doc
assert doc["explicitMusicalSectionCount"]==0,doc
assert [s["performer"] for s in doc["sections"]]==["Alpha","Beta"],doc
assert all(s["type"]=="performer_cue" for s in doc["sections"]),doc
assert all(s["barCount"] is None for s in doc["sections"]),doc
present=compile_verified_music_presentation(doc,source_title="Test Signal lyrics",source_url="https://example.test/performer")
assert "**[Alpha:]**" in present["presentationText"],present
assert "**[Beta:]**" in present["presentationText"],present

STRUCTURED_PAGE="""Test Signal lyrics
[Intro]
Signal opens in the midnight
Current runs beneath the station
[Verse 1: Alpha]
Every circuit holds the cadence
Noisy sparks become the motion
Second current keeps the rhythm
Fourth line closes the verse
[Chorus: Alpha]
Signal returns to the station
Current returns to the motion
Signal returns to the station
Current returns to the motion
[Verse 2: Beta]
Second voice enters the pattern
Another current crosses over
Final signal keeps on moving
Closing current ends the motion
Submitted by Guest
"""

STRUCTURED_SNIPPET="Test Signal lyrics [Verse 1: Alpha] Every circuit holds the cadence Noisy sparks become the motion Second current keeps the rhythm Fourth line closes the verse"

orig_research=online_tools.run_online_research
orig_fetch=online_tools.canonical_online_research.fetch_public
orig_prov=online_tools._lyrics_provenance_lookup
fetch_calls=[]

def fake_research(_payload):
    return {
        "provider":"test-search",
        "researchId":"v165",
        "errors":[],
        "candidateAdmissionDebug":[],
        "evidence":[{
            "evidenceId":"e1",
            "title":"Example Artist - Test Signal Lyrics",
            "pageTitle":"Example Artist - Test Signal Lyrics",
            "url":"https://example.test/performer",
            "finalUrl":"https://example.test/performer",
            "snippet":SNIPPET,
            "extract":PERFORMER_PAGE,
            "source":"example.test",
            "query":plan["query"],
            "rank":1,
            "status":200,
            "fetchedAt":1,
        }],
        "candidatePool":[
            {
                "title":"Example Artist - Test Signal (Original) Lyrics",
                "url":"https://example.test/original",
                "snippet":"Test Signal Original lyrics",
                "source":"example.test",
                "rank":2,
            },
            {
                "title":"Example Artist - Test Signal Lyrics",
                "url":"https://structured.example/test-signal",
                "snippet":STRUCTURED_SNIPPET,
                "source":"structured.example",
                "rank":5,
            },
        ],
    }

def fake_fetch(url):
    fetch_calls.append(url)
    if "structured.example" in url:
        return {
            "finalUrl":url,
            "status":200,
            "title":"Example Artist - Test Signal Lyrics",
            "extract":STRUCTURED_PAGE,
            "fetchedAt":2,
        }
    return {
        "finalUrl":url,
        "status":200,
        "title":"Example Artist - Test Signal (Original) Lyrics",
        "extract":PERFORMER_PAGE,
        "fetchedAt":2,
    }

def fake_prov(_subject,_lyrics,_progress=None):
    return {"originalStanzaCount":None,"sourceTitle":"","sourceUrl":"","evidence":[],"queries":[],"fetchCount":0,"claimExcerpt":"","httpStatus":None,"fetchedAt":None}

try:
    online_tools.run_online_research=fake_research
    online_tools.canonical_online_research.fetch_public=fake_fetch
    online_tools._lyrics_provenance_lookup=fake_prov
    p=dict(plan);p["requestId"]="v165-structured-preference"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research
    online_tools.canonical_online_research.fetch_public=orig_fetch
    online_tools._lyrics_provenance_lookup=orig_prov

# Initial performer-only source may verify, but bounded fallback should prefer
# the structurally richer candidate before Chat presentation.
assert fetch_calls==["https://structured.example/test-signal"],fetch_calls
assert result["lyricsSourceAttemptCount"]==2,result
assert result["lyricsSourceAttempts"][0]["outcome"]=="VERIFIED",result
assert result["lyricsSourceAttempts"][0]["musicalSectionCount"]==0,result
assert result["lyricsSourceAttempts"][0]["performerCueCount"]==2,result
assert result["lyricsSourceAttempts"][1]["outcome"]=="VERIFIED",result
assert result["lyricsSourceAttempts"][1]["musicalSectionCount"]>=4,result

verified=result["modelContext"]["verifiedLyrics"]
assert verified["sourceUrl"]=="https://structured.example/test-signal",verified
assert verified["requestedScope"]=="full-lyrics",verified
assert verified["presentationText"],verified
assert "**[Verse 1: Alpha]**" in verified["presentationText"],verified["presentationText"]
assert "**[Chorus: Alpha]**" in verified["presentationText"],verified["presentationText"]
assert "**[Verse 2: Beta]**" in verified["presentationText"],verified["presentationText"]

debug=result["musicStructureDebug"]
assert debug["explicitMusicalSectionCount"]>=4,debug
assert debug["newlineEqualsBar"] is False,debug
assert debug["presentationChars"]>0,debug

camera=online_tools.online_camera(result)
assert camera["contract"]=="swrlz-online-camera-v1",camera
assert str(camera.get("observabilityRevision") or "").startswith("v"),camera
assert camera["lyricsFetchDebug"][0]["performerCueCount"]==2,camera
assert camera["lyricsFetchDebug"][0]["snippetSequenceSpan"]>=4,camera
assert camera["lyricsFetchDebug"][0]["fetchedContent"]["performerMarkers"]==["[Alpha:]","[Beta:]"],camera

print("lyrics-region-integrity-v165 PASS")

# v174 Dragon Chat (23) real-shape continuation: the fetched lyric text was
# verified, but a directory 'Back to: Artist Lyrics' line and subsequent site
# navigation leaked into the last rendered section. The source section's x2
# marker is a repeat annotation, never a performer credit.
from music_structure import parse_section_marker

POST_SONG_PAGE="""Test Signal Lyrics
[Intro:]
Signal begins tonight
Copper waves move along
[Verse 1:]
The circuits start to glow
Our listeners hum along
The sky turns into light
The rhythm carries on
[Hook: x2]
A bright refrain returns
Its echo circles home
[Outro: x2]
The pattern fades away
The final notes remain
Back to: Example Artist Lyrics
Top Hits /
One Hit Wonders /
TV Themes /
Song Quotes /
Test Music Site
"""
post_analysis=online_tools._lyrics_extract_analysis(POST_SONG_PAGE,"full-lyrics",plan["subject"])
pd=post_analysis["diagnostics"]
assert pd["decision"]=="ACCEPTED",pd
assert pd["terminalBoundaryKind"]=="POST_SONG_META_BOUNDARY",pd
assert pd["terminalBoundaryLine"]=="Back to: Example Artist Lyrics",pd
assert "The final notes remain" in post_analysis["text"]
assert "Back to:" not in post_analysis["text"],post_analysis["text"]
assert "Top Hits" not in post_analysis["text"],post_analysis["text"]
post_doc=structure_verified_music(
    post_analysis["text"],POST_SONG_PAGE,subject=plan["subject"],requested_scope="full-lyrics"
)
assert [section["type"] for section in post_doc["sections"]]==["intro","verse","hook","outro"],post_doc
repeats=[sec for sec in post_doc["sections"] if sec["type"] in {"hook","outro"}]
assert [sec["repeatCount"] for sec in repeats]==[2,2],repeats
assert all(sec["performer"] is None for sec in repeats),repeats
assert parse_section_marker("[Verse 1: Alpha]")["performer"]=="Alpha"
assert parse_section_marker("[Chorus: x3]")["repeatCount"]==3
assert parse_section_marker("[Chorus: 2x]")["repeatCount"]==2
assert parse_section_marker("[Chorus: repeat 2 times]")["repeatCount"]==2
post_present=compile_verified_music_presentation(
    post_doc,source_title="Test Signal",source_url="https://example.test/test-signal"
)
assert "**[Hook: x2]**" in post_present["presentationText"]
assert "**[Outro: x2]**" in post_present["presentationText"]
assert "Back to:" not in post_present["presentationText"],post_present

# v174 behavior remains required, but later releases legitimately advance the
# online camera revision; do not pin the predecessor string in this regression.
assert int(online_tools.ONLINE_OBSERVABILITY_REVISION.split("-",1)[0].lstrip("v"))>=174

print("lyrics-page-footer-repeat-metadata-v174 PASS")

# v177 Dragon Chat (26): a page with authentic section markers is accepted,
# but publisher/site footer text MUST NOT become an extended last section.
SOURCE_CREDITS_PAGE="""Test Signal Lyrics
[Verse 1]
Our copper circuits awaken
Another soft signal rises
A distant lighthouse keeps shining
The midnight engines are humming
[Hook x2]
The ocean calls us onward
The distant shore is waiting
[Verse 2]
A painted sunset keeps moving
The quiet wheels are turning
The distant stars are singing
The shadow sails are lifting
[Outro x2]
The bright horizon grows wider
Another journey begins now
Songwriters: Example Writer / Another Writer
Publisher: Lyrics © Example Publishing
Powered by LyricFind
Top Lyrics
Other Musician - Unrelated Song lyrics
Top Artists
Someone Else lyrics
LyricsMania.com - Copyright © 2026 - All Rights Reserved Privacy Policy
"""
source_analysis=online_tools._lyrics_extract_analysis(SOURCE_CREDITS_PAGE,"full-lyrics",plan["subject"])
sc=source_analysis["diagnostics"]
assert sc["decision"]=="ACCEPTED",sc
assert sc["terminalBoundaryKind"]=="POST_SONG_META_BOUNDARY",sc
assert sc["terminalBoundaryLine"].startswith("Songwriters:"),sc
assert "The bright horizon grows wider" in source_analysis["text"]
for marker_text in ["Songwriters:","Publisher:","Powered by","Top Lyrics","Top Artists","Unrelated Song"]:
    assert marker_text not in source_analysis["text"],(marker_text,source_analysis["text"])
source_doc=structure_verified_music(
    source_analysis["text"],SOURCE_CREDITS_PAGE,subject=plan["subject"],requested_scope="full-lyrics"
)
assert [x["type"] for x in source_doc["sections"]]==["verse","hook","verse","outro"],source_doc
assert [x.get("repeatCount") for x in source_doc["sections"]]==[None,2,None,2],source_doc
source_present=compile_verified_music_presentation(source_doc,source_title="Source",source_url="https://example.test/song")
for marker_text in ["Songwriters:","Publisher:","Top Lyrics","Top Artists"]:
    assert marker_text not in source_present["presentationText"],source_present
assert parse_section_marker("[Hook x2]")["repeatCount"]==2
assert parse_section_marker("[Outro x2]")["repeatCount"]==2
assert parse_section_marker("[Hook: x2]")["repeatCount"]==2
assert parse_section_marker("[Verse 1: Alpha]")["performer"]=="Alpha"
print("songwriter-publisher-boundary-and-noncolon-repeats-v177 PASS")


