"""Regression for v158: lyrics verification retries ranked alternate pages, bounded to three total attempts."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools

PROMPT='Search the internet for the full lyrics of "Test Song". Please provide all the verses, not just the first verse, and give me the source link. Use a real web search rather than answering from memory.'
plan=online_tools.classify_online_request(PROMPT,[],{},None)
assert plan["contentMode"]=="lyrics-verification",plan
assert plan["requestedScope"]=="full-lyrics",plan

BAD_PAGE="""Lyrics
Home Menu Privacy Terms Contact
"""
GOOD_PAGE="""Verse 1
Alpha river carries softly
Beta lantern burns at night
Gamma road keeps winding onward
Delta stars remain in sight

Verse 2
Epsilon morning opens slowly
Zeta bells begin to ring
Eta footsteps cross the valley
Theta voices start to sing
"""

FIRST_URL="https://first.example/test-song"
SECOND_URL="https://second.example/test-song"
THIRD_URL="https://third.example/test-song"
FOURTH_URL="https://fourth.example/test-song"

def research_bundle():
    return {
        "provider":"test-search",
        "researchId":"lyrics-v158",
        "errors":[],
        "evidence":[{
            "evidenceId":"e1",
            "title":"Test Song lyrics",
            "url":FIRST_URL,
            "finalUrl":FIRST_URL,
            "snippet":"Test Song lyrics",
            "extract":BAD_PAGE,
            "source":"first.example",
            "query":plan["query"],
            "rank":1,
            "status":200,
            "fetchedAt":1,
        }],
        "candidatePool":[
            {"title":"Test Song lyrics","url":FIRST_URL,"snippet":"lyrics","source":"first.example","query":plan["query"],"rank":1,"relevanceScore":20},
            {"title":"Test Song lyrics mirror","url":SECOND_URL,"snippet":"lyrics","source":"second.example","query":plan["query"],"rank":2,"relevanceScore":19},
            {"title":"Test Song complete lyrics","url":THIRD_URL,"snippet":"complete lyrics","source":"third.example","query":plan["query"],"rank":3,"relevanceScore":18},
            {"title":"Test Song another mirror","url":FOURTH_URL,"snippet":"lyrics","source":"fourth.example","query":plan["query"],"rank":4,"relevanceScore":17},
        ],
    }

orig_research=online_tools.run_online_research
orig_fetch=online_tools.canonical_online_research.fetch_public

# Success on the third total page attempt: initial page + two alternates.
fetches=[]
events=[]
def fake_research(_payload):
    return research_bundle()

def fake_fetch_success(url):
    fetches.append(url)
    if url==SECOND_URL:
        return {"title":"Test Song lyrics mirror","finalUrl":url,"status":200,"fetchedAt":2,"extract":BAD_PAGE}
    if url==THIRD_URL:
        return {"title":"Test Song complete lyrics","finalUrl":url,"status":200,"fetchedAt":3,"extract":GOOD_PAGE}
    raise AssertionError("fallback exceeded success boundary: "+url)

try:
    online_tools.run_online_research=fake_research
    online_tools.canonical_online_research.fetch_public=fake_fetch_success
    p=dict(plan);p["requestId"]="v158-success"
    result=online_tools._search_bundle(p,events.append)
finally:
    online_tools.run_online_research=orig_research
    online_tools.canonical_online_research.fetch_public=orig_fetch

verified=result["modelContext"]["verifiedLyrics"]
assert verified, result
assert verified["sourceUrl"]==THIRD_URL,verified
assert fetches==[SECOND_URL,THIRD_URL],fetches
assert result["lyricsSourceAttemptCount"]==3,result
assert result["lyricsMaxPageAttempts"]==3,result
assert result["lyricsFallbackExhausted"] is False,result
assert [x["outcome"] for x in result["lyricsSourceAttempts"]]==["REJECTED","REJECTED","VERIFIED"],result["lyricsSourceAttempts"]
assert FOURTH_URL not in fetches,fetches
phases=[event.get("phase") for event in events]
assert "LYRICS_FALLBACK_FETCH" in phases,phases
assert "LYRICS_SOURCE_VERIFIED" in phases,phases
# Rejection-only source bodies do not need a new provider search; v178
# last-slot rescue is reserved for actual upstream HTTP/network failures.
assert "LYRICS_RESCUE_SEARCH" not in phases,phases

# Exhaustion: after three total attempts, a fourth candidate must never be fetched.
fetches=[]
def fake_fetch_exhausted(url):
    fetches.append(url)
    if url==FOURTH_URL:
        raise AssertionError("fourth page must not be fetched")
    return {"title":"Unusable lyrics page","finalUrl":url,"status":200,"fetchedAt":4,"extract":BAD_PAGE}

try:
    online_tools.run_online_research=fake_research
    online_tools.canonical_online_research.fetch_public=fake_fetch_exhausted
    p=dict(plan);p["requestId"]="v158-exhausted"
    exhausted=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research
    online_tools.canonical_online_research.fetch_public=orig_fetch

assert exhausted["modelContext"]["verifiedLyrics"] is None,exhausted
assert exhausted["lyricsSourceAttemptCount"]==3,exhausted
assert exhausted["lyricsMaxPageAttempts"]==3,exhausted
assert exhausted["lyricsFallbackExhausted"] is True,exhausted
assert fetches==[SECOND_URL,THIRD_URL],fetches
assert FOURTH_URL not in fetches,fetches

print("full-lyrics-bounded-fallback-v158 PASS")
