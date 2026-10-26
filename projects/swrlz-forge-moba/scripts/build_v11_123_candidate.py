"""Measure v11.123 on the exact sealed v11.122 source."""
import hashlib,re,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
old=Path('/tmp/se-v11122-release/index.html').read_text(encoding='utf8')
for marker in ['function stCanBuild(', 'stCanBuild = function(', 'stCanBuild=function(', 'building already', 'snappedX', 'stLanesSnapHouse', 'function stLanesSnapHouse', 'ST_LANE_GAP', 'window.SWRLZ_FORGE_BUILD=']:
 pos=old.find(marker)
 print('SE_V11123_SOURCE_ANCHOR',marker,pos,repr(old[max(0,pos-340):pos+240]) if pos>=0 else '')
html=runpy.run_path(str(root/'patches/v11_123_sheep_lanes_toolbar_controls.py'))['apply'](old)
out=Path('/tmp/se-v11123.html');out.write_text(html,encoding='utf8')
Path('/tmp/se-v11123.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0],encoding='utf8')
print('SE_V11123_CANDIDATE_BYTES',len(html.encode()))
print('SE_V11123_CANDIDATE_SHA256',hashlib.sha256(html.encode()).hexdigest())
for key in ('Projects</','Projects','playBtn','pauseBtn','simulateBtn','<header class="topbar"', 'class="topbar"'):
 k=html.find(key)
 if k>=0:
  print('SE_V11123_TOPBAR_LOOKUP',key,repr(html[max(0,k-400):k+560][:960]))
