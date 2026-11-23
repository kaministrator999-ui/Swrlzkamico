"""Append UV island workspace after immutable v11.550 source."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def apply(html):
 anchor='const se356BaseEnsurePanel=ensurePanel;'
 assert html.count(anchor)==1
 js=(ROOT/'runtime/uv_island_workspace_v11_551.js').read_text('utf8')
 assert 'function se551Install()' not in html
 return html.replace(anchor,js+'\n'+anchor,1)
