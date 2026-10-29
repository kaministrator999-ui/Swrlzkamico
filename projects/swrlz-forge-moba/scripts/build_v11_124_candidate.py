"""Build the v11.124 placement-only candidate against sealed v11.123."""
from pathlib import Path
import runpy,hashlib
root=Path(__file__).resolve().parents[1]
base=Path('/tmp/se-v11123-release/index.html').read_text(encoding='utf8')
html=runpy.run_path(str(root/'patches/v11_124_sheep_passable_placement.py'))['apply'](base)
Path('/tmp/se-v11124.html').write_text(html,encoding='utf8')
Path('/tmp/se-v11124.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0],encoding='utf8')
print('SE_V11124_CANDIDATE_BYTES',len(html.encode()))
print('SE_V11124_CANDIDATE_SHA256',hashlib.sha256(html.encode()).hexdigest())
