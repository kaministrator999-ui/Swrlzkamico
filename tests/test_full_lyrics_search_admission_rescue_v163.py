"""v163 regression: expose 8->0 admission collapse and use at most two subject-bound rescue searches."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))
sys.path.insert(0,str(ROOT/"accepted_runtime"/"research"))

import online_tools
import online_research_reasoner

PROMPT="Can you provide full lyrics for the song Test Signal by Example Artist"
plan=online_tools.classify_online_request(PROMPT,[],{},None)
assert plan["contentMode"]=="lyrics-verification",plan
assert plan["subject"]=='"Test Signal" by Example Artist',plan

# Reasoner-level admission diagnostics: provider results can exist while every
# candidate is rejected for insufficient subject-term match.
payload={
    "requestId":"v163-admission",
    "prompt":"Test Signal Example Artist lyrics",
    "researchPlan":{
        "intent":"web-search",
        "target":"Test Signal Example Artist lyrics",
        "requestedInformation":"Test Signal Example Artist lyrics",
        "targetConfidence":0.9,
        "queries":["Test Signal Example Artist lyrics"],
        "constraints":["bounded-public-web-evidence"],
    },
}
provider_results=[
    {"title":f"Unrelated result {i}","url":f"https://irrelevant{i}.example/page","snippet":"different subject entirely","source":f"irrelevant{i}.example","rank":i}
    for i in range(1,9)
]
reasoner_bundle=online_research_reasoner.research(payload,{
    "search":lambda _q:list(provider_results),
    "fetch":lambda _u: (_ for _ in ()).throw(AssertionError("rejected results must not be fetched")),
    "provider":"test-provider",
})
assert reasoner_bundle["resultCount"]==0,reasoner_bundle
assert len(reasoner_bundle["candidateAdmissionDebug"])==8,reasoner_bundle
assert all(not x["allowed"] for x in reasoner_bundle["candidateAdmissionDebug"]),reasoner_bundle
assert all(x["reason"]=="INSUFFICIENT_SUBJECT_TERM_MATCH" for x in reasoner_bundle["candidateAdmissionDebug"]),reasoner_bundle
assert reasoner_bundle["budget"]["searchCandidatesRejected"]==8,reasoner_bundle

PAGE="""Test Signal Lyrics
[Verse 1: Example Artist]
Alpha current moves through midnight
Beta lantern marks the station
Gamma signals cross the skyline
Delta engines hold formation
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
"""

orig_research=online_tools.run_online_research
orig_search=online_tools.canonical_online_research.search_public
orig_fetch=online_tools.canonical_online_research.fetch_public
orig_prov=online_tools._lyrics_provenance_lookup
search_calls=[]
fetch_calls=[]

def fake_research(_payload):
    return {
        "provider":"test-provider",
        "researchId":"v163-empty-admission",
        "errors":[],
        "evidence":[],
        "candidatePool":[],
        "candidateAdmissionDebug":reasoner_bundle["candidateAdmissionDebug"],
    }

def fake_search(query):
    search_calls.append(query)
    if len(search_calls)==1:
        return [
            {"title":"Another unrelated page","url":"https://wrong.example/page","snippet":"not the requested song","source":"wrong.example","rank":1}
        ]
    return [
        {"title":"Example Artist – Test Signal Lyrics","url":"https://lyrics.example/test-signal","snippet":"Test Signal Example Artist lyrics Alpha current moves through midnight Beta lantern marks the station","source":"lyrics.example","rank":1}
    ]

def fake_fetch(url):
    fetch_calls.append(url)
    return {
        "finalUrl":url,
        "status":200,
        "title":"Example Artist – Test Signal Lyrics",
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
    p=dict(plan);p["requestId"]="v163-rescue"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research
    online_tools.canonical_online_research.search_public=orig_search
    online_tools.canonical_online_research.fetch_public=orig_fetch
    online_tools._lyrics_provenance_lookup=orig_prov

assert len(search_calls)==2,search_calls
assert all('Test Signal' in q for q in search_calls),search_calls
assert len(fetch_calls)==1,fetch_calls
assert fetch_calls[0]=="https://lyrics.example/test-signal",fetch_calls
assert result["modelContext"]["verifiedLyrics"],result
assert result["lyricsSourceAttemptCount"]==1,result

rescue=result["lyricsRescueSearchDebug"]
assert len(rescue)==2,rescue
assert rescue[0]["resultCount"]==1 and rescue[0]["admittedCount"]==0,rescue
assert rescue[1]["resultCount"]==1 and rescue[1]["admittedCount"]==1,rescue

camera=online_tools.online_camera(result)
assert camera["candidateAdmissionDebug"],camera
assert camera["lyricsRescueSearchDebug"],camera
assert len(camera["candidateAdmissionDebug"])==8,camera
assert all(not x["allowed"] for x in camera["candidateAdmissionDebug"]),camera
assert len(camera["lyricsRescueSearchDebug"])==2,camera
assert camera["lyricsRescueSearchDebug"][1]["admittedCount"]==1,camera
assert camera["lyricsFetchDebug"][0]["outcome"]=="VERIFIED",camera

print("full-lyrics-search-admission-rescue-v163 PASS")
