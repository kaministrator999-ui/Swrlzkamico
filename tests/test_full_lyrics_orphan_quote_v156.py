"""Regression for retry 6: attribution excerpts must not begin with orphan closing quotes."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools

RAW='” The well-known final stanza, “When we’ve been there ten thousand years,” wasn’t part of Newton’s original text.'
clean=online_tools._lyrics_provenance_claim_excerpt(RAW)

assert clean.startswith("The well-known final stanza"),clean
assert not clean.startswith(("”","’","»","›",'" ')),clean
assert "“When we’ve been there ten thousand years,”" in clean,clean
assert clean.endswith("original text."),clean

# Preserve legitimate internal quotation marks while trimming only the orphan edge mark.
RAW2='” A later note says “this stanza was added later,” and identifies it as a later stanza.'
clean2=online_tools._lyrics_provenance_claim_excerpt(RAW2)
assert clean2.startswith("A later note"),clean2
assert "“this stanza was added later,”" in clean2,clean2

print("full-lyrics-orphan-quote-v156 PASS")
