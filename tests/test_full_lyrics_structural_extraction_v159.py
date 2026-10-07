"""v159 regressions for menu-heavy and structurally marked lyric pages; no network calls."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))
sys.path.insert(0,str(ROOT))

import online_tools
from api import online_research as canonical_online_research

assert canonical_online_research.MAX_PAGE_EXTRACT_CHARS >= 24000
assert online_tools.LYRICS_PAGE_TEXT_CHARS >= 24000

PUBLIC_DOMAIN_BODY="""Auld Lang Syne Lyrics

1. Should old acquaintance be forgot,
and never brought to mind?
Should old acquaintance be forgot,
and days of auld lang syne?

For days of auld lang syne,
for days of auld lang syne,
we'll take a cup of kindness yet,
for days of auld lang syne.

2. And surely you'll buy your pint cup!
and surely I'll buy mine!
And we'll take a cup o' kindness yet,
for days of auld lang syne.

3. We two have run about the slopes,
and picked the daisies fine;
We've wandered many a weary foot,
since days of auld lang syne.

Karaoke Video with Lyrics
Did you like this post? Rate it!
You Might Also Like
"""

menu_prefix="\n".join(f"Navigation Item {i} Example Section" for i in range(420))
assert len(menu_prefix)>6000
menu_heavy_page=menu_prefix+"\nPrintable Auld Lang Syne Lyrics PDF\nDownload the PDF below\n"+PUBLIC_DOMAIN_BODY

extracted=online_tools._lyrics_extract_candidate(menu_heavy_page,"full-lyrics",'"Auld Lang Syne."')
assert extracted, extracted
assert "Should old acquaintance be forgot" in extracted, extracted
assert "We two have run about the slopes" in extracted, extracted
assert "Karaoke Video" not in extracted, extracted
assert "You Might Also Like" not in extracted, extracted
assert "Navigation Item" not in extracted, extracted

modern_page="""Home
Music
Test Signal Lyrics
[Verse 1: Example Artist]
Alpha current moves through midnight
Beta lantern marks the station
Gamma signals cross the skyline
Delta engines keep their cadence

[Chorus: Example Artist]
Echo returns across the harbor
Foxtrot keeps the rhythm steady
Golf remains beside the signal
Hotel closes out the measure

Related Posts
Another Song Lyrics
"""
modern=online_tools._lyrics_extract_candidate(modern_page,"full-lyrics",'"Test Signal" by Example Artist')
assert modern, modern
assert "Alpha current moves through midnight" in modern, modern
assert "Hotel closes out the measure" in modern, modern
assert "Related Posts" not in modern, modern
assert "[Verse 1" not in modern, modern

PROMPT='Search the internet for the full lyrics of "Auld Lang Syne.". Please provide all the verses, not just the first verse, and give me the source link. Use a real web search rather than answering from memory.'
plan=online_tools.classify_online_request(PROMPT,[],{},None)
assert plan["contentMode"]=="lyrics-verification",plan
assert plan["requestedScope"]=="full-lyrics",plan

orig_research=online_tools.run_online_research
orig_provenance=online_tools._lyrics_provenance_lookup

def fake_research(_payload):
    return {
        "provider":"test-search",
        "researchId":"lyrics-v159",
        "errors":[],
        "evidence":[{
            "evidenceId":"e1",
            "title":"Auld Lang Syne Lyrics - Free PDF To Save And Print",
            "url":"https://example.test/auld-lang-syne",
            "finalUrl":"https://example.test/auld-lang-syne",
            "snippet":"Auld Lang Syne lyrics",
            "extract":menu_heavy_page,
            "source":"example.test",
            "query":plan["query"],
            "rank":1,
            "status":200,
            "fetchedAt":1,
        }],
        "candidatePool":[],
    }

def fake_provenance(_subject,_lyrics,_progress=None):
    return {
        "originalStanzaCount":None,
        "sourceTitle":"",
        "sourceUrl":"",
        "evidence":[],
        "queries":[],
        "fetchCount":0,
        "claimExcerpt":"",
        "httpStatus":None,
        "fetchedAt":None,
    }

try:
    online_tools.run_online_research=fake_research
    online_tools._lyrics_provenance_lookup=fake_provenance
    p=dict(plan); p["requestId"]="v159-menu-heavy"
    result=online_tools._search_bundle(p)
finally:
    online_tools.run_online_research=orig_research
    online_tools._lyrics_provenance_lookup=orig_provenance

verified=result["modelContext"]["verifiedLyrics"]
assert verified, result
assert verified["sourceUrl"]=="https://example.test/auld-lang-syne",verified
assert "Should old acquaintance be forgot" in verified["lyricExtract"],verified
assert result["lyricsSourceAttemptCount"]==1,result
assert result["lyricsFallbackExhausted"] is False,result

print("full-lyrics-structural-extraction-v159 PASS")
