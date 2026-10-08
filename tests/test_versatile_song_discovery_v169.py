"""v169 regression: ambiguous song titles escalate through bounded generic source-family discovery."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools

PROMPT="Now can you provide the lyrics to rack city by tyga"
plan=online_tools.classify_online_request(PROMPT,[],{},None)
assert plan["contentMode"]=="lyrics-verification",plan
assert plan["subject"]=='"rack city" by tyga',plan
assert plan["requestedScope"]=="full-lyrics",plan

plans=online_tools._lyrics_rescue_query_plan(plan["subject"])
assert len(plans)<=online_tools.LYRICS_MAX_RESCUE_SEARCHES,plans
assert plans[0]["strategy"]=="exact-title-artist",plans
assert any(x["strategy"]=="source-family-disambiguation" for x in plans),plans
assert all("rack city" in x["query"].lower() for x in plans),plans
assert all("tyga" in x["query"].lower() for x in plans),plans

PAGE="""Rack City lyrics
Tyga
[Intro]
Opening signal starts the track
Second opening line stays intact
[Verse 1: Tyga]
Alpha rhythm moves through downtown
Beta cadence keeps the beat strong
Gamma motion crosses the skyline
Delta ending closes the verse
[Chorus: Tyga]
City signal keeps returning
City signal keeps returning
City signal keeps returning
City signal keeps returning
[Verse 2: Tyga]
Second rhythm moves through downtown
Another cadence keeps the beat strong
Final motion crosses the skyline
Closing ending stops the song
"""

SNIPPET="Rack City Tyga lyrics Alpha rhythm moves through downtown Beta cadence keeps the beat strong Gamma motion crosses the skyline Delta ending closes the verse"

orig_research=online_tools.run_online_research
orig_search=online_tools.canonical_online_research.search_public
orig_fetch=online_tools.canonical_online_research.fetch_public
orig_prov=online_tools._lyrics_provenance_lookup
search_calls=[]
fetch_calls=[]

def fake_research(_payload):
    # Reproduce the live failure mode: search returned results, but every one
    # was rejected as retail/dictionary ambiguity, so no candidate survived.
    return {
        "provider":"test-provider",
        "researchId":"v169-ambiguous-title",
        "errors":[],
        "evidence":[],
        "candidatePool":[],
        "candidateAdmissionDebug":[
            {
                "query":"rack city tyga lyrics",
                "title":"Nordstrom Rack : Shop Clothes, Shoes, Jewelry, Beauty and Home",
                "url":"https://retail.example/rack",
                "source":"retail.example",
                "rank":1,
                "allowed":False,
                "reason":"INSUFFICIENT_SUBJECT_TERM_MATCH",
                "neededHits":2,
                "matchedTerms":["rack"],
                "coreTerms":["rack","city","tyga"],
                "snippetPreview":"Rack sale and clothing",
            }
        ],
    }

def fake_search(query):
    search_calls.append(query)
    # Both broad exact queries remain ambiguous, matching the live log.
    if len(search_calls)<=2:
        return [
            {
                "title":"Nordstrom Rack : Shop Clothes, Shoes, Jewelry, Beauty and Home",
                "url":"https://retail.example/rack",
                "snippet":"Rack sale and clothing",
                "source":"retail.example",
                "rank":1,
            }
        ]
    # A later generic source-family-disambiguated query finds a relevant page.
    return [
        {
            "title":"Tyga - Rack City Lyrics",
            "url":"https://lyrics.example/tyga/rack-city",
            "snippet":SNIPPET,
            "source":"lyrics.example",
            "rank":1,
        }
    ]

def fake_fetch(url):
    fetch_calls.append(url)
    return {
        "finalUrl":url,
        "status":200,
        "title":"Tyga - Rack City Lyrics",
        "extract":PAGE,
        "fetchedAt":1,
    }

def fake_prov(_subject,_lyrics,_progress=None):
    return {"originalStanzaCount":None,"sourceTitle":"","sourceUrl":"","evidence":[],"queries":[],"fetchCount":0,"claimExcerpt":"","httpStatus":None,"fetchedAt":None}

try:
    online_tools.run_online_research=fake_research
    online_tools.canonical_online_research.search_public=fake_search
    online_tools.canonical_online_research.fetch_public=fake_fetch
    online_tools._lyrics_provenance_lookup=fake_prov
    p=dict(plan);p["requestId"]="v169-versatile"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research
    online_tools.canonical_online_research.search_public=orig_search
    online_tools.canonical_online_research.fetch_public=orig_fetch
    online_tools._lyrics_provenance_lookup=orig_prov

assert len(search_calls)==3,search_calls
assert any(token in search_calls[2].lower() for token in ("site:genius.com","site:azlyrics.com","site:musixmatch.com")),search_calls
assert fetch_calls==["https://lyrics.example/tyga/rack-city"],fetch_calls
assert result["lyricsSourceAttemptCount"]==1,result
assert result["modelContext"]["verifiedLyrics"],result
assert result["modelContext"]["verifiedLyrics"]["sourceUrl"]=="https://lyrics.example/tyga/rack-city",result

rescue=result["lyricsRescueSearchDebug"]
assert len(rescue)==3,rescue
assert rescue[0]["strategy"]=="exact-title-artist",rescue
assert rescue[1]["strategy"]=="artist-title-song",rescue
assert rescue[2]["strategy"]=="source-family-disambiguation",rescue
assert rescue[0]["admittedCount"]==0 and rescue[1]["admittedCount"]==0,rescue
assert rescue[2]["admittedCount"]==1,rescue

camera=online_tools.online_camera(result)
assert camera["songIdentity"],camera
assert camera["songDiscoveryPlan"],camera
assert camera["lyricsRescueSearchDebug"][2]["strategy"]=="source-family-disambiguation",camera
assert len(camera["lyricsRescueSearchDebug"])<=online_tools.LYRICS_MAX_RESCUE_SEARCHES,camera
assert result["lyricsMaxPageAttempts"]==3,result

print("versatile-song-discovery-v169 PASS")
