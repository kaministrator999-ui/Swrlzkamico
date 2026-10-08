"""v166 regression: Bing /ck/a search wrappers normalize to destination URLs before evidence/fetch."""
import base64
import html
import sys
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from api import online_research as research

DEST="https://www.azlyrics.com/lyrics/techn9ne/coldpieceofwork.html"
payload=base64.urlsafe_b64encode(DEST.encode("utf-8")).decode("ascii").rstrip("=")
wrapped=(
    "https://www.bing.com/ck/a?%21=&p=testhash&ptn=3&ver=2&"
    "u=a1"+payload+"&ntb=1"
)

assert research._bing_target(wrapped)==DEST
assert research._search_target(wrapped)==DEST
assert research._bing_target("https://example.com/direct")== "https://example.com/direct"

# Unresolved Bing tracking wrappers are not valid evidence destinations.
assert research._bing_target("https://www.bing.com/ck/a?p=x&ntb=1")==""
assert research._bing_target("https://www.bing.com/ck/a?u=a1not-valid-base64")==""

# Recreate the v165 Bing HTML result shape without DNS/network.
original_validate=research._validate_public_url
try:
    research._validate_public_url=lambda url: url
    page=f"""
    <ol id="b_results">
      <li class="b_algo">
        <h2><a href="{html.escape(wrapped,quote=True)}">JL, Tech N9ne, Joey Cool &amp; Jay Trilogy - Cold Piece Of Work Lyrics</a></h2>
        <p>Cold Piece Of Work lyric source result.</p>
      </li>
    </ol>
    """
    results,anchors=research._parse_bing_html("cold piece of work tech n9ne lyrics",page)
finally:
    research._validate_public_url=original_validate

assert anchors==1,(anchors,results)
assert len(results)==1,results
item=results[0]
assert item["url"]==DEST,item
assert item["source"]=="www.azlyrics.com",item
assert "bing.com/ck/a" not in item["url"],item

print("bing-redirect-canonicalization-v166 PASS")
