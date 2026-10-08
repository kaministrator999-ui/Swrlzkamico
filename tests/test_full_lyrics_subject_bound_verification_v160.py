"""v160 regressions: natural song subject parsing + false-positive lyric rejection."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools

PROMPT="Can you provide lyrics for the song cold piece of work by tech n9ne"
plan=online_tools.classify_online_request(PROMPT,[],{},None)
assert plan["contentMode"]=="lyrics-verification",plan
assert plan["subject"]=='"cold piece of work" by tech n9ne',plan
assert plan["query"]=="cold piece of work tech n9ne lyrics",plan

BAD_PAGE="""Cold Piece of Work Lyrics
The Pretender
Foo Fighters

The Modern Age
The Strokes

There Is a Light That Never Goes Out
The Smiths

I Will Survive
Gloria Gaynor

Chart Watch
Popular Tech N9ne Collabos Lyrics

On the Record
Strange Reign Deluxe Edition Tracklist

Miley Sets Billboard Record With Album Fall
Justin Timberlake Offers an Apology
Dakota Cohen Turns Chairs on The Voice
Brian May Says Queen Will Not Tour Again
Metallica Bring Devils Dance Back
"""

GOOD_PAGE="""Cold Piece of Work Lyrics
[Verse 1: Example Artist]
Signal ember moves through midnight
Copper rhythm marks the station
Silver engines cross the skyline
Quiet circuits hold formation

[Chorus: Example Artist]
Signal ember keeps returning
Copper rhythm stays in motion
Silver engines cross the skyline
Quiet circuits hold formation
"""

TARGET_SNIPPET="Cold Piece of Work lyrics. Signal ember moves through midnight Copper rhythm marks the station Silver engines cross the skyline Quiet circuits hold formation"

# The observed false-positive shape must not pass snippet/body consistency.
bad_extract=online_tools._lyrics_extract_candidate(BAD_PAGE,"lyrics",plan["subject"])
assert bad_extract,bad_extract
consistent,overlap,total=online_tools._lyrics_snippet_consistent(TARGET_SNIPPET,bad_extract,plan["subject"])
assert consistent is False,(overlap,total,bad_extract)

good_extract=online_tools._lyrics_extract_candidate(GOOD_PAGE,"lyrics",plan["subject"])
assert good_extract,good_extract
consistent,overlap,total=online_tools._lyrics_snippet_consistent(TARGET_SNIPPET,good_extract,plan["subject"])
assert consistent is True,(overlap,total,good_extract)

FIRST="https://example.test/chrome"
SECOND="https://example.test/real"
orig_research=online_tools.run_online_research
orig_fetch=online_tools.canonical_online_research.fetch_public
orig_provenance=online_tools._lyrics_provenance_lookup

def fake_research(_payload):
    return {
        "provider":"test-search",
        "researchId":"lyrics-v160",
        "errors":[],
        "evidence":[{
            "evidenceId":"e1",
            "title":"Cold Piece of Work Lyrics",
            "url":FIRST,
            "finalUrl":FIRST,
            "snippet":TARGET_SNIPPET,
            "extract":BAD_PAGE,
            "source":"example.test",
            "query":plan["query"],
            "rank":1,
            "status":200,
            "fetchedAt":1,
        }],
        "candidatePool":[
            {"title":"Tech N9ne - Cold Piece of Work Lyrics","url":FIRST,"snippet":"Tech N9ne "+TARGET_SNIPPET,"source":"example.test","query":plan["query"],"rank":1,"relevanceScore":20},
            {"title":"Tech N9ne - Cold Piece of Work Lyrics alternate","url":SECOND,"snippet":"Tech N9ne "+TARGET_SNIPPET,"source":"example.test","query":plan["query"],"rank":2,"relevanceScore":19},
        ],
    }

def fake_fetch(url):
    assert url==SECOND,url
    return {"title":"Tech N9ne - Cold Piece of Work Lyrics alternate","finalUrl":url,"status":200,"fetchedAt":2,"extract":GOOD_PAGE}

def fake_provenance(_subject,_lyrics,_progress=None):
    return {"originalStanzaCount":None,"sourceTitle":"","sourceUrl":"","evidence":[],"queries":[],"fetchCount":0,"claimExcerpt":"","httpStatus":None,"fetchedAt":None}

try:
    online_tools.run_online_research=fake_research
    online_tools.canonical_online_research.fetch_public=fake_fetch
    online_tools._lyrics_provenance_lookup=fake_provenance
    p=dict(plan);p["requestId"]="v160-subject-bound"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research
    online_tools.canonical_online_research.fetch_public=orig_fetch
    online_tools._lyrics_provenance_lookup=orig_provenance

verified=result["modelContext"]["verifiedLyrics"]
assert verified, result
assert verified["sourceUrl"]==SECOND,verified
assert result["lyricsSourceAttemptCount"]==2,result
assert result["lyricsFallbackExhausted"] is False,result
attempts=result["lyricsSourceAttempts"]
assert attempts[0]["outcome"]=="REJECTED",attempts
assert attempts[1]["outcome"]=="VERIFIED",attempts
assert attempts[0]["snippetOverlapCount"] < attempts[1]["snippetOverlapCount"],attempts

# Unresolved subject must not treat arbitrary "... Lyrics" navigation labels as anchors.
no_subject_anchor=online_tools._lyrics_best_anchor([
    "Home","Popular Tech N9ne Collabos Lyrics","The Pretender","Foo Fighters","Chart Watch"
],"")
assert no_subject_anchor is None,no_subject_anchor

print("full-lyrics-subject-bound-verification-v160 PASS")
