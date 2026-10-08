"""v170 regression: one failed source + one blocked family must leave the last bounded attempt for another provider."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools
from song_identity import song_identity, diversify_candidates, source_family

PROMPT="Can you provide lyrics for rack city by tyga"
plan=online_tools.classify_online_request(PROMPT,[],{},None)
assert plan["contentMode"]=="lyrics-verification",plan
assert plan["subject"]=='"rack city" by tyga',plan

identity=song_identity(plan["subject"])
pool=[
    {"title":"Tyga - Rack City Lyrics | AZLyrics.com","url":"https://www.azlyrics.com/lyrics/tyga/rackcity.html","snippet":"Tyga Lyrics Rack City rack rack city Mustard on the beat","source":"www.azlyrics.com","rank":2},
    {"title":"Tyga - Rack City Lyrics | AZLyrics.com","url":"https://www.azlyrics.com/lyrics/tyga/rackcity242457.html","snippet":"Rack City Tyga lyrics rack rack city Mustard on the beat","source":"www.azlyrics.com","rank":3},
    {"title":"Tyga - Rack City lyrics | Musixmatch","url":"https://www.musixmatch.com/lyrics/Tyga-3/rack-city","snippet":"Lyrics for Rack City by Tyga Rack rack city Mustard on the beat","source":"www.musixmatch.com","rank":4},
    {"title":"Tyga - Rack City lyrics | LyricsFreak","url":"https://www.lyricsfreak.com/t/tyga/rack+city_20984331.html","snippet":"Tyga Rack City Lyrics Rack rack city Mustard on the beat","source":"www.lyricsfreak.com","rank":6},
]
diverse=diversify_candidates(pool,identity)
families=[source_family(item) for item in diverse]
assert families[:3]==["azlyrics.com","musixmatch.com","lyricsfreak.com"],families
assert families[-1]=="azlyrics.com",families

GOOD_PAGE="""Rack City lyrics
[Intro]
Rack city opening signal
Mustard starts the city rhythm
[Verse 1: Tyga]
Rack city line one is moving
Rack city line two keeps moving
Rack city line three keeps moving
Rack city line four keeps moving
[Chorus: Tyga]
Rack city hook one returns
Rack city hook two returns
Rack city hook three returns
Rack city hook four returns
"""
GOOD_SNIPPET="Rack City Tyga lyrics Rack city line one is moving Rack city line two keeps moving Rack city line three keeps moving Rack city line four keeps moving"

orig_research=online_tools.run_online_research
orig_fetch=online_tools.canonical_online_research.fetch_public
orig_prov=online_tools._lyrics_provenance_lookup
fetch_calls=[]

def fake_research(_payload):
    return {
        "provider":"test-search",
        "researchId":"v170",
        "errors":[],
        "candidateAdmissionDebug":[],
        "evidence":[{
            "evidenceId":"e1",
            "title":"Tyga - Rack City Lyrics - Genius",
            "pageTitle":"Tyga - Rack City Lyrics - Genius",
            "url":"https://genius.com/Tyga-rack-city-lyrics",
            "finalUrl":"https://genius.com/Tyga-rack-city-lyrics",
            "snippet":"Rack City Tyga lyrics",
            "extract":"",
            "source":"genius.com",
            "query":plan["query"],
            "rank":1,
        }],
        "fetchFailures":[{
            "url":"https://genius.com/Tyga-rack-city-lyrics",
            "title":"Tyga - Rack City Lyrics - Genius",
            "source":"genius.com",
            "query":plan["query"],
            "rank":1,
            "errorType":"HTTPError",
        }],
        "candidatePool":pool,
    }

def fake_fetch(url):
    fetch_calls.append(url)
    if "azlyrics.com" in url:
        return {
            "finalUrl":"https://b.azlyrics.com/?u=%2Flyrics%2Ftyga%2Frackcity.html",
            "status":200,
            "title":"AZLyrics - request for access",
            "extract":"Our systems have detected unusual activity. Please check the box below to regain access.",
            "fetchedAt":2,
        }
    if "musixmatch.com" in url:
        return {
            "finalUrl":url,
            "status":200,
            "title":"Tyga - Rack City lyrics | Musixmatch",
            "extract":GOOD_PAGE,
            "fetchedAt":3,
        }
    raise AssertionError("unexpected fetch family: "+url)

def fake_prov(_subject,_lyrics,_progress=None):
    return {"originalStanzaCount":None,"sourceTitle":"","sourceUrl":"","evidence":[],"queries":[],"fetchCount":0,"claimExcerpt":"","httpStatus":None,"fetchedAt":None}

# Give the successful Musixmatch candidate the longer corroborating snippet.
pool[2]["snippet"]=GOOD_SNIPPET

try:
    online_tools.run_online_research=fake_research
    online_tools.canonical_online_research.fetch_public=fake_fetch
    online_tools._lyrics_provenance_lookup=fake_prov
    p=dict(plan);p["requestId"]="v170-diverse-budget"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research
    online_tools.canonical_online_research.fetch_public=orig_fetch
    online_tools._lyrics_provenance_lookup=orig_prov

assert result["lyricsSourceAttemptCount"]==3,result
attempts=result["modelContext"]["lyricsSourceAttempts"]
assert attempts[0]["origin"]=="reasoner-fetch" and attempts[0]["outcome"]=="FETCH_ERROR",attempts
assert "genius.com" in attempts[0]["url"],attempts
assert "azlyrics.com" in attempts[1]["url"],attempts
assert "musixmatch.com" in attempts[2]["url"],attempts
assert all("rackcity242457" not in call for call in fetch_calls),fetch_calls
assert fetch_calls==[
    "https://www.azlyrics.com/lyrics/tyga/rackcity.html",
    "https://www.musixmatch.com/lyrics/Tyga-3/rack-city",
],fetch_calls

verified=result["modelContext"]["verifiedLyrics"]
assert verified, result
assert "musixmatch.com" in verified["sourceUrl"],verified
assert result["modelContext"]["blockedLyricsSourceFamilies"]==["azlyrics.com"],result["modelContext"]
assert result["lyricsFallbackExhausted"] is False,result

print("diverse-lyric-fetch-budget-v170 PASS")
