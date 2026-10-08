"""v168 regression: Chat renders standalone --- as full-width lyric document boundary."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/"chat"/"§wyrlz"/"index.html").read_text(encoding="utf-8")

assert 'if(/^\\s*---\\s*$/.test(line))' in html
assert 'document.createElement("hr")' in html
assert 'hr.className="lyric-document-divider"' in html
assert '.lyric-document-divider{display:block;width:100%' in html
assert 'LYRIC_SECTION_DIVIDER="────────"' in (ROOT/"hf_space"/"music_structure.py").read_text(encoding="utf-8")
assert 'LYRIC_OUTER_DIVIDER="---"' in (ROOT/"hf_space"/"music_structure.py").read_text(encoding="utf-8")

print("full-width-lyric-boundary-rendering-v168 PASS")
