"""Regression for v155: provenance claims must come from fetched body, not search snippets."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools
import model_router

PROMPT='Search the internet for the full lyrics of "Amazing Grace" by John Newton. Please provide all the verses, not just the first verse, and give me the source link. Use a real web search rather than answering from memory.'
plan=online_tools.classify_online_request(PROMPT,[],{},None)

page="""Copy Lyrics
Amazing grace! How sweet the sound
That saved a wretch like me!
I once was lost, but now am found;
Was blind, but now I see.

'Twas grace that taught my heart to fear,
And grace my fears relieved;
How precious did that grace appear
The hour I first believed.

Through many dangers, toils, and snares,
I have already come;
'Tis grace hath brought me safe thus far,
And grace will lead me home.

The Lord has promised good to me,
His Word my hope secures;
He will my Shield and Portion be,
As long as life endures.

Yea, when this flesh and heart shall fail,
And mortal life shall cease,
I shall possess, within the veil,
A life of joy and peace.

The earth shall soon dissolve like snow,
The sun forbear to shine;
But God, who called me here below,
Will be forever mine.

When we've been there ten thousand years,
Bright shining as the sun,
We've no less days to sing God's praise
Than when we'd first begun.
"""

orig_research=online_tools.run_online_research
orig_search=online_tools.canonical_online_research.search_public
orig_fetch=online_tools.canonical_online_research.fetch_public
fetches=[]

def fake_research(payload):
    return {
        "provider":"test","researchId":"lyrics","errors":[],
        "evidence":[{
            "evidenceId":"e1",
            "title":"Amazing Grace Lyrics - All Verses by John Newton",
            "url":"https://lyrics.example/amazing-grace",
            "finalUrl":"https://lyrics.example/amazing-grace",
            "snippet":"All verses","extract":page,"source":"lyrics.example",
            "query":plan["query"],"rank":1,"status":200,"fetchedAt":1,
        }],
    }

def fake_search(query):
    return [
        {
            "title":"Amazing Grace history by John Newton",
            "url":"https://bad.example/amazing-grace",
            "snippet":"The original hymn was published in six stanzas.",
            "source":"bad.example","query":query,"rank":1,"fetched_at":1,
        },
        {
            "title":"Amazing Grace history by John Newton",
            "url":"https://good.example/amazing-grace",
            "snippet":"Historical hymn text and stanza history.",
            "source":"good.example","query":query,"rank":2,"fetched_at":1,
        },
    ]

def fake_fetch(url):
    fetches.append(url)
    if "bad.example" in url:
        return {
            "title":"Amazing Grace history by John Newton",
            "finalUrl":url,"status":200,"fetchedAt":2,
            "extract":"This fetched page contains no stanza count and no later-stanza claim.",
        }
    return {
        "title":"Amazing Grace history by John Newton",
        "finalUrl":url,"status":200,"fetchedAt":3,
        "extract":"The original text was published in six stanzas. A later stanza is commonly appended.",
    }

try:
    online_tools.run_online_research=fake_research
    online_tools.canonical_online_research.search_public=fake_search
    online_tools.canonical_online_research.fetch_public=fake_fetch
    p=dict(plan);p["requestId"]="v155"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research
    online_tools.canonical_online_research.search_public=orig_search
    online_tools.canonical_online_research.fetch_public=orig_fetch

verified=result["modelContext"]["verifiedLyrics"]
assert len(fetches)>=2,fetches
assert verified["originalStanzaCount"]==6,verified
assert verified["attributionSourceUrl"]=="https://good.example/amazing-grace",verified
assert "six stanzas" in verified["attributionClaimExcerpt"].lower(),verified
assert verified["sourceDisplayTitle"]=="Amazing Grace lyrics page",verified

rendered=model_router._lyrics_retrieval_payload(result,PROMPT)
assert "complete lyric set" not in rendered,rendered
assert "full lyric text I could verify from the fetched source" in rendered,rendered
assert "Amazing Grace Lyrics - All Verses by John Newton" not in rendered,rendered
assert "**Attribution evidence:**" in rendered,rendered
assert "six stanzas" in rendered.lower(),rendered

print("full-lyrics-fetched-body-provenance-v155 PASS")
