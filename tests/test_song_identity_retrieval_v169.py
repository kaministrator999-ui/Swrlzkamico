"""v169 regression: SongIdentity generalizes ambiguous song retrieval before fetch."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))
sys.path.insert(0,str(ROOT/"accepted_runtime"/"research"))

from song_identity import song_identity, query_ladder, candidate_score, rank_candidates
import online_tools
import online_research_reasoner

# Ambiguous/common-word title: exact entity query must be first.
rack=song_identity('"Rack City" by Tyga')
assert rack["title"]=="Rack City",rack
assert rack["primaryArtist"]=="Tyga",rack
assert rack["ambiguity"]["level"]=="high",rack
assert set(rack["ambiguity"]["commonWordCollision"])=={"rack","city"},rack
ladder=query_ladder(rack,8)
assert ladder,ladder
assert ladder[0]["strategy"]=="exact-title-artist",ladder
assert ladder[0]["query"]=='"Rack City" "Tyga" lyrics',ladder
assert any("site:genius.com" in x["query"] for x in ladder),ladder

# Common-word shopping/dictionary collisions must lose to a lyric entity.
shopping={
    "title":"Nordstrom Rack | Shop Shoes, Clothing & More",
    "url":"https://www.nordstromrack.com/",
    "snippet":"Shop racks, sale prices, clothing and products.",
    "rank":1,
}
right={
    "title":"Tyga – Rack City Lyrics",
    "url":"https://genius.com/Tyga-rack-city-lyrics",
    "snippet":"Rack City lyrics by Tyga [Verse 1] ...",
    "rank":6,
}
wrong_artist={
    "title":"Rack City Lyrics",
    "url":"https://lyrics.example/rack-city",
    "snippet":"Rack City lyrics by Example Artist",
    "rank":2,
}
s_shop=candidate_score(shopping,rack)
s_right=candidate_score(right,rack)
s_wrong=candidate_score(wrong_artist,rack)
assert s_shop["allowed"] is False,s_shop
assert s_shop["reason"] in {"TITLE_MISMATCH","ARTIST_MISMATCH","NON_LYRIC_RESULT","AMBIGUOUS_TITLE_WEAK_MATCH"},s_shop
assert s_right["allowed"] is True,s_right
assert s_right["exactTitle"] is True,s_right
assert s_right["artistHits"]>=1,s_right
assert s_wrong["allowed"] is False,s_wrong
assert s_wrong["reason"]=="ARTIST_MISMATCH",s_wrong
ranked=rank_candidates([shopping,wrong_artist,right],rack)
assert ranked[0]["url"]==right["url"],ranked

# Punctuation and stylized titles still normalize as one entity.
dna=song_identity('"DNA." by Kendrick Lamar')
assert dna["title"]=="DNA.",dna
assert dna["titleFolded"]=="dna",dna
assert dna["primaryArtistFolded"]=="kendrick lamar",dna

xo=song_identity('"XO TOUR Llif3" by Lil Uzi Vert')
assert xo["titleFolded"]=="xo tour llif3",xo
assert xo["artistTokens"]==["lil","uzi","vert"],xo

# Featured artist parsing is identity metadata, not loose query prose.
feat=song_identity('"Signal" by Alpha feat. Beta & Gamma')
assert feat["primaryArtist"]=="Alpha",feat
assert feat["featuredArtists"]==["Beta","Gamma"],feat

# Version behavior: requested remix must match; unrequested live/remix conflicts reject.
base=song_identity('"Home" by Example Artist')
live_result={
    "title":"Example Artist – Home (Live) Lyrics",
    "url":"https://genius.com/example-artist-home-live-lyrics",
    "snippet":"Home live lyrics Example Artist",
    "rank":1,
}
base_live=candidate_score(live_result,base)
assert base_live["allowed"] is False,base_live
assert base_live["reason"]=="VERSION_MISMATCH",base_live

remix=song_identity('"Home (Remix)" by Example Artist')
assert remix["requestedVersion"]=="Remix",remix
remix_result={
    "title":"Example Artist – Home Remix Lyrics",
    "url":"https://genius.com/example-artist-home-remix-lyrics",
    "snippet":"Home Remix lyrics Example Artist",
    "rank":1,
}
s_remix=candidate_score(remix_result,remix)
assert s_remix["allowed"] is True,s_remix
assert s_remix["versionMatch"] is True,s_remix

# "Original" is a soft page label, not automatically a different arrangement.
original_label={
    "title":"Example Artist – Home Original Lyrics",
    "url":"https://lyrics.example/example-artist-home",
    "snippet":"Home original lyrics by Example Artist",
    "rank":2,
}
s_original=candidate_score(original_label,base)
assert s_original["allowed"] is True,s_original
assert s_original["versionMismatch"] is False,s_original

# Route integration: natural prompt becomes SongIdentity-aware search.
plan=online_tools.classify_online_request(
    "Can you provide the lyrics to Rack City by Tyga",
    [],{},None
)
assert plan["contentMode"]=="lyrics-verification",plan
assert plan["requestedScope"]=="full-lyrics",plan
assert plan["subject"]=='"Rack City" by Tyga',plan
assert plan["songIdentity"]["ambiguity"]["level"]=="high",plan
assert plan["query"]=='"Rack City" "Tyga" lyrics',plan

# Runtime-hot reasoner: exact quoted song entity rejects the shopping collision
# before any page fetch and admits the actual song entity.
payload={
    "requestId":"v169-reasoner",
    "prompt":plan["query"],
    "researchPlan":{
        "intent":"web-search",
        "target":plan["query"],
        "requestedInformation":plan["query"],
        "targetConfidence":0.99,
        "queries":[plan["query"]],
        "constraints":["bounded-public-web-evidence"],
    },
}
fetches=[]
bundle=online_research_reasoner.research(payload,{
    "search":lambda _q:[shopping,right],
    "fetch":lambda url: fetches.append(url) or {
        "title":"Tyga – Rack City Lyrics",
        "finalUrl":url,
        "status":200,
        "fetchedAt":1,
        "extract":"[Verse 1]\nAlpha signal moves tonight\nBeta rhythm crosses town\nGamma cadence keeps on moving\nDelta motion settles down\n\n[Chorus]\nEcho signal keeps returning\nFoxtrot rhythm circles round\nGolf cadence keeps on moving\nHotel motion settles down",
    },
    "provider":"test-provider",
})
debug=bundle["candidateAdmissionDebug"]
assert len(debug)==2,debug
assert debug[0]["allowed"] is False,debug
assert debug[0]["reason"]=="TITLE_PHRASE_MISMATCH",debug
assert debug[1]["allowed"] is True,debug
assert debug[1]["reason"]=="EXACT_SONG_ENTITY_MATCH",debug
assert fetches==[right["url"]],fetches

print("song-identity-retrieval-v169 PASS")
