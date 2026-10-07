"""Regression checks for the v152 full-lyrics cleanup + attribution pass."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools
import model_router

PROMPT='Search the internet for the full lyrics of "Amazing Grace" by John Newton. Please provide all the verses, not just the first verse, and give me the source link. Use a real web search rather than answering from memory.'

plan=online_tools.classify_online_request(PROMPT,[],{},None)
assert plan["requestedScope"]=="full-lyrics",plan
assert plan["subject"]=='"Amazing Grace" by John Newton',plan

page="""Related Hymns
Holy, Holy, Holy
Come Thou Fount of Every Blessing
It Is Well With My Soul
Best Memory Techniques for Singers and Performers
How to Memorize a Long Song: A Step-by-Step Method That Sticks
The Science of Musical Memory: Why Songs Stick
Get the Lines app!
Practice and memorize your favorite songs with our iOS app.
Copy Lyrics
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

clean=online_tools._lyrics_extract_candidate(page,"full-lyrics")
assert "Related Hymns" not in clean,clean
assert "Get the Lines app" not in clean,clean
assert "And grace will lead me home." in clean,clean
stanzas=[x.strip() for x in clean.split("\n\n") if x.strip()]
assert len(stanzas)==7,stanzas

calls=[]
searches=[]
fetches=[]
original=online_tools.run_online_research
original_search=online_tools.canonical_online_research.search_public
original_fetch=online_tools.canonical_online_research.fetch_public

def fake_research(payload):
    query=str(payload.get("prompt") or "")
    calls.append(query)
    return {
        "provider":"test",
        "researchId":"lyrics",
        "errors":[],
        "evidence":[{
            "evidenceId":"e1","title":"Amazing Grace Lyrics - All Verses by John Newton",
            "url":"https://lyrics.example/amazing-grace","finalUrl":"https://lyrics.example/amazing-grace",
            "snippet":"All verses","extract":page,"source":"lyrics.example",
            "query":query,"rank":1,"status":200,"fetchedAt":1,
        }],
    }

def fake_search(query):
    searches.append(query)
    return [{
        "title":"Amazing Grace historical text",
        "url":"https://history.example/amazing-grace",
        "snippet":"John Newton original hymn text published in six stanzas.",
        "source":"history.example","query":query,"rank":1,"fetched_at":2,
    }]

def fake_fetch(url):
    fetches.append(url)
    return {
        "title":"Amazing Grace historical text",
        "finalUrl":"https://history.example/amazing-grace",
        "status":200,"fetchedAt":3,
        "extract":"The original text attributed to John Newton was published in six stanzas.",
    }

try:
    online_tools.run_online_research=fake_research
    online_tools.canonical_online_research.search_public=fake_search
    online_tools.canonical_online_research.fetch_public=fake_fetch
    p=dict(plan);p["requestId"]="v152"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=original
    online_tools.canonical_online_research.search_public=original_search
    online_tools.canonical_online_research.fetch_public=original_fetch

verified=result["modelContext"]["verifiedLyrics"]
assert verified["originalStanzaCount"]==6,verified
assert verified["attributionSourceUrl"]=="https://history.example/amazing-grace",verified
assert verified["attributionHttpStatus"]==200,verified
assert "six stanzas" in verified["attributionClaimExcerpt"].lower(),verified
assert len(calls)==1,calls
assert len(searches)==1,searches
assert len(fetches)==1,fetches

rendered=model_router._lyrics_retrieval_payload(result,PROMPT)
assert rendered, result
assert "Related Hymns" not in rendered,rendered
assert "Get the Lines app" not in rendered,rendered
assert "And grace will lead me home." in rendered,rendered
assert "**Original attributed text (6 stanzas):**" in rendered,rendered
assert "**Additional stanza(s) present in the lyrics source:**" in rendered,rendered
assert "ten thousand years" in rendered,rendered
assert "**Attribution source:**" in rendered,rendered
assert "**Attribution evidence:**" in rendered,rendered
assert "All Verses by John Newton" not in rendered,rendered
assert "full lyric text I could verify from the fetched source" in rendered,rendered

print("full-lyrics-clean-attribution-v152 PASS")
