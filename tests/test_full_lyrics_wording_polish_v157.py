"""Regression for v157 lyric-response grammar polishing."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import model_router

def render(stanzas, original_count):
    result={
        "modelContext":{
            "verifiedLyrics":{
                "requestedScope":"full-lyrics",
                "subject":'"Amazing Grace" by John Newton',
                "sourceTitle":"Amazing Grace Lyrics - All Verses by John Newton",
                "sourceDisplayTitle":"Amazing Grace lyrics page",
                "sourceUrl":"https://lyrics.example/amazing-grace",
                "lyricExtract":"\n\n".join(stanzas),
                "originalStanzaCount":original_count,
                "attributionSourceTitle":"Historical source",
                "attributionSourceUrl":"https://history.example/amazing-grace",
                "attributionClaimExcerpt":"The original text was published in six stanzas.",
                "candidateSources":[],
            }
        }
    }
    return model_router._lyrics_retrieval_payload(result,"prompt")

base=[
    "a1\na2\na3\na4",
    "b1\nb2\nb3\nb4",
    "c1\nc2\nc3\nc4",
    "d1\nd2\nd3\nd4",
    "e1\ne2\ne3\ne4",
    "f1\nf2\nf3\nf4",
]

single=render(base+["g1\ng2\ng3\ng4"],6)
assert "**Original text attributed to John Newton (6 stanzas):**" in single,single
assert "**Additional stanza present in the lyrics source:**" in single,single
assert "stanza(s)" not in single,single
assert "identifies 6 stanzas as the original text attributed to John Newton" in single,single
assert "The additional stanza above is kept separate" in single,single

plural=render(base+["g1\ng2\ng3\ng4","h1\nh2\nh3\nh4"],6)
assert "**Additional stanzas present in the lyrics source:**" in plural,plural
assert "The additional stanzas above are kept separate" in plural,plural

print("full-lyrics-wording-polish-v157 PASS")
