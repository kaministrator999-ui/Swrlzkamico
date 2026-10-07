"""Regression for retry 4: provenance succeeds without research-chain explosion or source spam."""
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

research_calls=[]
search_calls=[]
fetch_calls=[]
orig_research=online_tools.run_online_research
orig_search=online_tools.canonical_online_research.search_public
orig_fetch=online_tools.canonical_online_research.fetch_public

def fake_research(payload):
    research_calls.append(str(payload.get("prompt") or ""))
    return {
        "provider":"test","researchId":"lyrics","errors":[],
        "evidence":[
            {
                "evidenceId":"junk1","title":"Grace Definition - Dictionary",
                "url":"https://dictionary.example/grace?utm_source=spam","finalUrl":"https://dictionary.example/grace?utm_source=spam",
                "snippet":"Definition of grace","extract":"Definition entry, not lyrics.","source":"dictionary.example",
                "query":plan["query"],"rank":1,"status":200,"fetchedAt":1,
            },
            {
                "evidenceId":"e1","title":"Amazing Grace Lyrics - All Verses by John Newton",
                "url":"https://lyrics.example/amazing-grace?utm_source=search","finalUrl":"https://lyrics.example/amazing-grace?utm_source=search",
                "snippet":"All verses","extract":page,"source":"lyrics.example",
                "query":plan["query"],"rank":2,"status":200,"fetchedAt":2,
            },
        ],
    }

def fake_search(query):
    search_calls.append(query)
    return [
        {
            "title":"Grace definition video",
            "url":"https://video.example/grace?utm_source=x",
            "snippet":"A video dictionary entry about grace.",
            "source":"video.example","query":query,"rank":1,"fetched_at":1,
        },
        {
            "title":"Amazing grace! (how sweet the sound)",
            "url":"https://hymnary.example/text/amazing_grace?utm_source=ddg&ref=tracking",
            "snippet":"John Newton. Original hymn text, published in six stanzas; later stanza history.",
            "source":"hymnary.example","query":query,"rank":2,"fetched_at":1,
        },
        {
            "title":"Amazing grace! (how sweet the sound)",
            "url":"https://hymnary.example/text/amazing_grace?utm_source=duplicate",
            "snippet":"John Newton six stanzas and later added stanza.",
            "source":"hymnary.example","query":query,"rank":3,"fetched_at":1,
        },
    ]

def fake_fetch(url):
    fetch_calls.append(url)
    assert "video.example" not in url,url
    return {
        "title":"Amazing grace! (how sweet the sound)",
        "finalUrl":"https://hymnary.example/text/amazing_grace?utm_source=final",
        "status":200,"fetchedAt":3,
        "extract":"Amazing grace, how sweet the sound. J. Newton. Olney Hymns, 1779, in 6 stanzas of 4 lines. For the spurious stanza When we've been there ten thousand years, see a later hymn source.",
    }

try:
    online_tools.run_online_research=fake_research
    online_tools.canonical_online_research.search_public=fake_search
    online_tools.canonical_online_research.fetch_public=fake_fetch
    p=dict(plan);p["requestId"]="v154"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research
    online_tools.canonical_online_research.search_public=orig_search
    online_tools.canonical_online_research.fetch_public=orig_fetch

verified=result["modelContext"]["verifiedLyrics"]
assert verified["originalStanzaCount"]==6,verified
assert len(research_calls)==1,research_calls
assert len(search_calls)<=2,search_calls
assert len(fetch_calls)==1,fetch_calls
assert result["modelContext"]["provenanceFetchCount"]==1,result["modelContext"]
assert len(result["sources"])==2,result["sources"]
assert all("dictionary.example" not in s["url"] and "video.example" not in s["url"] for s in result["sources"]),result["sources"]
assert all("utm_" not in s["url"] and "ref=" not in s["url"] for s in result["sources"]),result["sources"]

rendered=model_router._lyrics_retrieval_payload(result,PROMPT)
assert "**Original text attributed to John Newton (6 stanzas):**" in rendered,rendered
assert "**Additional stanza present in the lyrics source:**" in rendered,rendered
assert "**Attribution source:**" in rendered,rendered
assert "dictionary.example" not in rendered,rendered
assert "video.example" not in rendered,rendered

print("full-lyrics-source-hygiene-v154 PASS")
