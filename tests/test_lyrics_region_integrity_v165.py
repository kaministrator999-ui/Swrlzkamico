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
