"""Build v11.121 candidate from the sealed v11.120 release for preflight."""
from pathlib import Path
import runpy,hashlib
root=Path(__file__).resolve().parents[1]
src=Path('/tmp/se-v11120-release/index.html').read_text(encoding='utf8')
out=runpy.run_path(str(root/'patches/v11_121_uncover_component_toolbar.py'))['apply'](src)
module=out.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path('/tmp/se-v11121.mjs').write_text(module,encoding='utf8')
print('SE_V11121_CANDIDATE_BYTES',len(out.encode()))
print('SE_V11121_CANDIDATE_SHA256',hashlib.sha256(out.encode()).hexdigest())
