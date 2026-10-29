"""Validate exact removal of only the provider's HTML insertions."""
from pathlib import Path
import runpy

root=Path(__file__).resolve().parents[1]
normalize=runpy.run_path(str(root/"scripts/normalize_hf_static_html.py"))["normalize_served_html"]
raw=b'<html><head><title>Original</title><meta name="viewport" content="width=device-width"></head><body>Original</body></html>'
script=b'<script>window.huggingface={variables:{}};</script>'
social=('<meta property="og:title" content="§wyrl§ Engine v11.59">'
        '<meta property="og:description" content="Maul, Sheep Tag, Model Atelier and Dragon Den">'
        '<meta property="og:image" content="https://cdn-thumbnails.huggingface.co/social-thumbnails/spaces/kamiloki/swrlz-forge-moba.png">'
        '<meta name="twitter:card" content="summary_large_image">'
        '<meta name="twitter:image" content="https://cdn-thumbnails.huggingface.co/social-thumbnails/spaces/kamiloki/swrlz-forge-moba.png">').encode()
assert len(social)==462
served=raw.replace(b'<head>',b'<head>'+script).replace(b'<meta name="viewport"',social+b'<meta name="viewport"')
assert normalize(served)==raw
assert normalize(raw)==raw
assert normalize(served.replace(social,social+social))!=raw
assert normalize(raw+b'<meta property="og:title" content="owner">')!=raw
try: normalize("not bytes")
except TypeError: pass
else: raise AssertionError("Not bytes")
print("HF_STATIC_HTML_PROVIDER_METADATA_NORMALIZATION_PASS")
