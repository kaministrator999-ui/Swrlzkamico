"""v162 regression: section-marker blocks survive no blank lines and fetch debug reaches Online Camera."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools

PROMPT="Can you provide full lyrics for the song Test Signal by Example Artist"
plan=online_tools.classify_online_request(PROMPT,[],{},None)
assert plan["contentMode"]=="lyrics-verification",plan
assert plan["requestedScope"]=="full-lyrics",plan
assert plan["subject"]=='"Test Signal" by Example Artist',plan

PAGE="""Home
Lyrics
Test Signal Lyrics
Album: Demo Record
[Intro]
Signal intro opens softly
Copper pulse begins the motion
[Verse 1: Example Artist]
Alpha current moves through midnight
Beta lantern marks the station
Gamma signals cross the skyline
Delta engines hold formation
[Pre-Chorus: Example Artist]
Echo rises through the harbor
Foxtrot keeps the cadence steady
[Chorus: Example Artist]
Golden rhythm keeps returning
Harbor lights remain in motion
Indigo circuits cross the skyline
Jade receivers hold formation
[Verse 2: Example Artist]
Kilo current moves through morning
Lima lantern marks the station
Mike signals cross the skyline
November engines hold formation
Submitted by Guest
Top Example Artist songs
"""

SNIPPET="Test Signal lyrics Alpha current moves through midnight Beta lantern marks the station Gamma signals cross the skyline Delta engines hold formation"

# No blank lines exist between sections: explicit markers must define blocks.
assert "\n\n" not in PAGE
extracted=online_tools._lyrics_extract_candidate(PAGE,"full-lyrics",plan["subject"])
assert extracted,extracted
assert "Alpha current moves through midnight" in extracted,extracted
assert "Kilo current moves through morning" in extracted,extracted
assert "Submitted by Guest" not in extracted,extracted
assert len(extracted.split("\n\n"))>=3,extracted

orig_research=online_tools.run_online_research
orig_provenance=online_tools._lyrics_provenance_lookup

def fake_research(_payload):
    return {
        "provider":"test-search",
        "researchId":"lyrics-v162",
        "errors":[],
        "evidence":[{
            "evidenceId":"e1",
            "title":"Test Signal Lyrics",
            "pageTitle":"Example Artist – Test Signal lyrics",
            "url":"https://example.test/example_artist-test_signal",
            "finalUrl":"https://example.test/example_artist-test_signal",
            "snippet":SNIPPET,
            "extract":PAGE,
            "source":"example.test",
            "query":plan["query"],
            "rank":1,
            "status":200,
            "fetchedAt":1,
        }],
        "candidatePool":[],
    }

def fake_provenance(_subject,_lyrics,_progress=None):
    return {"originalStanzaCount":None,"sourceTitle":"","sourceUrl":"","evidence":[],"queries":[],"fetchCount":0,"claimExcerpt":"","httpStatus":None,"fetchedAt":None}

try:
    online_tools.run_online_research=fake_research
    online_tools._lyrics_provenance_lookup=fake_provenance
    p=dict(plan);p["requestId"]="v162-debug"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research
    online_tools._lyrics_provenance_lookup=orig_provenance

verified=result["modelContext"]["verifiedLyrics"]
assert verified, result
assert result["lyricsSourceAttemptCount"]==1,result
debug=result["lyricsFetchDebug"]
assert len(debug)==1,debug
entry=debug[0]
assert entry["outcome"]=="VERIFIED",entry
assert entry["rejectionReason"]=="VERIFIED",entry
assert entry["fetchedContent"]["chars"]==len(PAGE),entry
assert len(entry["fetchedContent"]["sha256"])==64,entry
assert entry["fetchedContent"]["preview"],entry
assert entry["fetchedContent"]["sectionMarkers"],entry
assert entry["extractorOutput"]["chars"]>0,entry

camera=online_tools.online_camera(result)
assert camera["observabilityRevision"]=="v162-fetch-debug-section-blocks",camera
assert len(camera["lyricsFetchDebug"])==1,camera
cam=camera["lyricsFetchDebug"][0]
assert cam["fetchedContent"]["preview"],cam
assert cam["fetchedContent"]["previewLimit"]==600,cam
assert cam["extractorOutput"]["preview"],cam
assert cam["rejectionReason"]=="VERIFIED",cam

print("full-lyrics-fetch-debug-section-blocks-v162 PASS")
