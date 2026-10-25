"""Candidate §E v11.122 source and module for focused touch preflight."""
from pathlib import Path
import runpy,hashlib
root=Path(__file__).resolve().parents[1]
src=Path('/tmp/se-v11121-release/index.html').read_text(encoding='utf8')
patched=runpy.run_path(str(root/'patches/v11_122_sitewide_touch_guard.py'))['apply'](src)
Path('/tmp/se-v11122.html').write_text(patched,encoding='utf8')
Path('/tmp/se-v11122.mjs').write_text(patched.split('<script type="module">',1)[1].rsplit('</script>',1)[0],encoding='utf8')
print('SE_V11122_CANDIDATE_BYTES',len(patched.encode()))
print('SE_V11122_CANDIDATE_SHA256',hashlib.sha256(patched.encode()).hexdigest())
