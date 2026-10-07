"""Regression checks for full-lyrics retrieval semantics; no network calls."""
import importlib.util
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools
import model_router

FULL_PROMPT='Search the internet for the complete lyrics of “Amazing Grace” by John Newton. Return every verse you can verify from the original/public-domain hymn, not just the first verse. Do not summarize, shorten, or omit verses. Include the source URL you retrieved them from. Use real web retrieval rather than answering from memory.'

plan=online_tools.classify_online_request(FULL_PROMPT,[],{},None)
assert plan["contentMode"]=="lyrics-verification",plan
assert plan["requestedScope"]=="full-lyrics",plan
assert plan["subject"]=='"Amazing Grace" by John Newton',plan
assert plan["query"]=="Amazing Grace John Newton lyrics all verses",plan

spec=importlib.util.spec_from_file_location(
    "lyrics_reasoner_v151",
    ROOT/"accepted_runtime"/"research"/"online_research_reasoner.py",
)
reasoner=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(reasoner)

reasoner_plan={
    "requestedInformation":plan["query"],
    "target":plan["query"],
    "queries":[plan["query"]],
}
junk=(
    "Amazing Grace Lyrics | All Verses & Words by John Newton - Lines App\n"
    "Lines Blog Download Home Menu Privacy Terms Contact About Subscribe"
)
assert reasoner._sufficient({"extract":junk},reasoner_plan) is False

lyrics=(
    "Amazing grace! how sweet the sound\n"
    "That saved a wretch like me!\n"
    "I once was lost, but now am found,\n"
    "Was blind, but now I see.\n\n"
    "Twas grace that taught my heart to fear,\n"
    "And grace my fears relieved;\n"
    "How precious did that grace appear\n"
    "The hour I first believed.\n\n"
    "Through many dangers, toils and snares,\n"
    "I have already come;\n"
    "Tis grace hath brought me safe thus far,\n"
    "And grace will lead me home."
)
assert reasoner._sufficient({"extract":lyrics},reasoner_plan) is True

original=online_tools.run_online_research
def fake_research(_payload):
    return {
        "provider":"test-search",
        "researchId":"lyrics-v151",
        "errors":[],
        "evidence":[
            {
                "evidenceId":"e1","title":"Amazing Grace Lyrics | All Verses & Words",
                "url":"https://example.test/junk","finalUrl":"https://example.test/junk",
                "snippet":"All verses and words","extract":junk,"source":"example.test",
                "query":plan["query"],"rank":1,"status":200,"fetchedAt":1,
            },
            {
                "evidenceId":"e2","title":"Amazing Grace complete lyrics",
                "url":"https://example.test/lyrics","finalUrl":"https://example.test/lyrics",
                "snippet":"Complete lyrics","extract":lyrics,"source":"example.test",
                "query":plan["query"],"rank":2,"status":200,"fetchedAt":2,
            },
        ],
    }
try:
    online_tools.run_online_research=fake_research
    plan_with_id=dict(plan)
    plan_with_id["requestId"]="lyrics-v151"
    result=online_tools._search_bundle(plan_with_id)
finally:
    online_tools.run_online_research=original

verified=result["modelContext"]["verifiedLyrics"]
assert verified, result
assert verified["sourceUrl"]=="https://example.test/lyrics",verified
assert verified["requestedScope"]=="full-lyrics",verified
assert verified["subject"]=='"Amazing Grace" by John Newton',verified
assert "Download" not in verified["lyricExtract"],verified
assert "Amazing grace!" in verified["lyricExtract"],verified

rendered=model_router._lyrics_retrieval_payload(result,FULL_PROMPT)
assert rendered, result
assert "the complete lyrics" in rendered,rendered
assert '**"Amazing Grace" by John Newton**' in rendered,rendered
assert "Return every verse" not in rendered,rendered
assert "Do not summarize" not in rendered,rendered
assert "https://example.test/lyrics" in rendered,rendered

first_prompt='Search the internet for the lyrics of "Amazing Grace" by John Newton. Tell me where you found them, give me the link, and quote the first verse.'
first=online_tools.classify_online_request(first_prompt,[],{},None)
assert first["requestedScope"]=="first-verse",first
assert first["query"]=="Amazing Grace John Newton lyrics first verse",first

print("full-lyrics-retrieval-v151 PASS")
