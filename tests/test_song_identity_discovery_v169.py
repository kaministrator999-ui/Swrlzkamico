"""v169 regression: SongIdentity + ambiguity-aware query ladder + candidate scoring."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))
sys.path.insert(0,str(ROOT/"accepted_runtime"/"research"))

import online_tools
import online_research_reasoner
from song_identity import song_identity, query_ladder, candidate_score, rank_candidates

# Ambiguous/common-word title should become an exact entity query immediately.
rack= song_identity('"Rack City" by Tyga')
assert rack["title"]=="Rack City",rack
assert rack["primaryArtist"]=="Tyga",rack
assert rack["ambiguity"]["level"]=="high",rack
assert rack["ambiguity"]["quotedTitleRequired"] is True,rack
assert set(rack["ambiguity"]["commonWordCollision"])=={"rack","city"},rack

rack_plan=query_ladder(rack,8)
assert rack_plan[0]["strategy"]=="exact-title-artist",rack_plan
assert rack_plan[0]["query"]=='"Rack City" "Tyga" lyrics',rack_plan
assert len(rack_plan)<=8,rack_plan
assert any(x["strategy"]=="source-family-disambiguation" and "site:genius.com" in x["query"] for x in rack_plan),rack_plan

# Punctuation/version handling should not require special per-song code.
dna=song_identity('"DNA." by Kendrick Lamar')
assert dna["title"]=="DNA.",dna
assert dna["primaryArtist"]=="Kendrick Lamar",dna
xo=song_identity('"XO TOUR Llif3" by Lil Uzi Vert')
assert xo["title"]=="XO TOUR Llif3",xo
hello=song_identity('"Hello" by Adele')
assert hello["ambiguity"]["level"]=="high",hello
work=song_identity('"Work" by Rihanna feat. Drake')
assert work["primaryArtist"]=="Rihanna",work
assert work["featuredArtists"]==["Drake"],work
remix=song_identity('"Ignition (Remix)" by R. Kelly')
assert remix["title"]=="Ignition",remix
assert remix["requestedVersion"]=="Remix",remix

# Candidate scoring must prefer the song entity and reject commerce intent.
shopping={
    "title":"Nordstrom Rack | Shop Clothes, Shoes & More",
    "url":"https://www.nordstromrack.com/",
    "snippet":"Shop Rack deals in your city with sale prices.",
    "source":"www.nordstromrack.com",
    "rank":1,
}
lyrics={
    "title":"Tyga – Rack City Lyrics",
    "url":"https://genius.com/Tyga-rack-city-lyrics",
    "snippet":"Rack City Tyga lyrics [Verse 1] ... [Chorus] ...",
    "source":"genius.com",
    "rank":5,
}
shop_score=candidate_score(shopping,rack)
lyric_score=candidate_score(lyrics,rack)
assert shop_score["allowed"] is False,shop_score
assert shop_score["reason"] in {"ARTIST_MISMATCH","NON_LYRIC_RESULT","AMBIGUOUS_TITLE_WEAK_MATCH"},shop_score
assert lyric_score["allowed"] is True,lyric_score
assert lyric_score["exactTitle"] is True,lyric_score
assert lyric_score["exactArtist"] is True,lyric_score
assert lyric_score["lyricDomain"] is True,lyric_score
assert lyric_score["score"]>shop_score["score"],(lyric_score,shop_score)
ranked=rank_candidates([shopping,lyrics],rack)
assert ranked[0]["url"]==lyrics["url"],ranked

# Wrong/unrequested version receives a penalty/rejection.
original_identity=song_identity('"Test Signal" by Example Artist')
wrong_version={
    "title":"Example Artist – Test Signal (Remix) Lyrics",
    "url":"https://lyrics.example/test-signal-remix",
    "snippet":"Test Signal Remix lyrics by Example Artist",
    "rank":1,
}
wrong_score=candidate_score(wrong_version,original_identity)
assert wrong_score["versionMismatch"] is True,wrong_score
assert wrong_score["allowed"] is False,wrong_score
assert wrong_score["reason"]=="VERSION_MISMATCH",wrong_score

# online_tools: high ambiguity gets exact quoted primary search immediately.
rack_prompt="Can you provide lyrics to rack city by tyga"
rack_request=online_tools.classify_online_request(rack_prompt,[],{},None)
assert rack_request["contentMode"]=="lyrics-verification",rack_request
assert rack_request["query"]=='"rack city" "tyga" lyrics',rack_request
assert rack_request["songIdentity"]["ambiguity"]["level"]=="high",rack_request

# Medium/low ambiguity titles preserve compact legacy search shape to avoid
# unnecessary ranking changes to already-working cases.
cold_prompt="Can you provide lyrics for cold piece of work by tech n9ne"
cold_request=online_tools.classify_online_request(cold_prompt,[],{},None)
assert cold_request["query"]=="cold piece of work tech n9ne lyrics",cold_request

# First reasoner admission gate: quoted title+artist prevents "rack city"
# commerce results from consuming the first page-fetch attempt.
payload={
    "requestId":"v169-rack",
    "prompt":rack_request["query"],
    "researchPlan":{
        "intent":"web-search",
        "target":rack_request["query"],
        "requestedInformation":rack_request["query"],
        "targetConfidence":0.99,
        "queries":[rack_request["query"]],
        "constraints":["bounded-public-web-evidence"],
    },
}
fetch_calls=[]
def fake_fetch(url):
    fetch_calls.append(url)
    return {
        "title":"Tyga - Rack City Lyrics",
        "extract":"[Verse 1]\nOne lyric line here\nSecond lyric line here\nThird lyric line here\nFourth lyric line here\n[Chorus]\nHook line one here\nHook line two here\nHook line three here\nHook line four here",
        "finalUrl":url,
        "status":200,
        "fetchedAt":1,
    }
bundle=online_research_reasoner.research(payload,{
    "search":lambda _q:[shopping,lyrics],
    "fetch":fake_fetch,
    "provider":"test-provider",
})
assert len(bundle["candidateAdmissionDebug"])==2,bundle
assert bundle["candidateAdmissionDebug"][0]["allowed"] is False,bundle
assert bundle["candidateAdmissionDebug"][0]["reason"]=="ARTIST_MISMATCH",bundle
assert bundle["candidateAdmissionDebug"][1]["allowed"] is True,bundle
assert bundle["candidateAdmissionDebug"][1]["reason"]=="EXACT_SONG_ENTITY_MATCH",bundle
assert fetch_calls==[lyrics["url"]],fetch_calls

print("song-identity-discovery-v169 PASS")
