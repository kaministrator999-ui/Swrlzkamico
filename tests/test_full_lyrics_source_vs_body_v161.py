"""v161 regression: verified lyric source identity is distinct from verified lyric body."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools
import model_router

PROMPT="Can you provide lyrics for the song cold piece of work by tech n9ne"
plan=online_tools.classify_online_request(PROMPT,[],{},None)
assert plan["subject"]=='"cold piece of work" by tech n9ne',plan
assert plan["query"]=="cold piece of work tech n9ne lyrics",plan

blocked=online_tools._lyrics_source_identity({
    "pageTitle":"AZLyrics - request for access",
    "title":"Cold Piece Of Work Lyrics",
    "url":"https://b.azlyrics.com/",
},"cold piece of work" by tech n9ne")
assert blocked["verified"] is False,blocked

source_ok=online_tools._lyrics_source_identity({
    "pageTitle":"Tech N9ne – Cold Piece of Work lyrics",
    "title":"Tech N9ne – Cold Piece of Work | All The Lyrics",
    "url":"https://www.allthelyrics.com/lyrics/tech_n9ne-cold_piece_of_work",
},"cold piece of work" by tech n9ne")
assert source_ok["verified"] is True,source_ok

orig_research=online_tools.run_online_research

def fake_research(_payload):
    return {
        "provider":"test-search",
        "researchId":"lyrics-v161",
        "errors":[],
        "evidence":[{
            "evidenceId":"e1",
            "title":"Tech N9ne – Cold Piece of Work | All The Lyrics",
            "pageTitle":"Tech N9ne – Cold Piece of Work lyrics",
            "url":"https://www.allthelyrics.com/lyrics/tech_n9ne-cold_piece_of_work",
            "finalUrl":"https://www.allthelyrics.com/lyrics/tech_n9ne-cold_piece_of_work",
            "snippet":"Cold Piece of Work lyrics target-song search evidence with several informative words for discovery only",
            "extract":"This fetched page region does not contain a clean extractable lyric body.",
            "source":"www.allthelyrics.com",
            "query":plan["query"],
            "rank":1,
            "status":200,
            "fetchedAt":1,
        }],
        "candidatePool":[],
    }

try:
    online_tools.run_online_research=fake_research
    p=dict(plan); p["requestId"]="v161-source-only"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research

ctx=result["modelContext"]
assert ctx["verifiedLyrics"] is None,ctx
source=ctx["verifiedLyricsSource"]
assert source,ctx
assert source["url"]=="https://www.allthelyrics.com/lyrics/tech_n9ne-cold_piece_of_work",source
assert source["title"]=="Tech N9ne – Cold Piece of Work lyrics",source
assert result["lyricsFallbackExhausted"] is True,result

rendered=model_router._lyrics_source_only_payload(result)
assert rendered,rendered
assert "found and verified a lyrics source" in rendered.lower(),rendered
assert "couldn't verify a clean lyric-text extraction" in rendered.lower(),rendered
assert source["url"] in rendered,rendered
assert "This fetched page region" not in rendered,rendered

print("full-lyrics-source-vs-body-v161 PASS")
