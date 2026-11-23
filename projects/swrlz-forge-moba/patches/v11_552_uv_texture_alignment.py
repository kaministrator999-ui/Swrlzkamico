"""Append v11.552 independent UV alignment UI after sealed history."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def apply(html):
 anchor='const se356BaseEnsurePanel=ensurePanel;'
 assert html.count(anchor)==1
 assert 'function se552Open()' not in html
 return html.replace(anchor,(ROOT/'runtime/uv_texture_alignment_v11_552.js').read_text('utf8')+'\n'+anchor,1)
