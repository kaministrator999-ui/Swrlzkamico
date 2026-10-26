"""Inspect v11.126 against the exact v11.125 release without mutating the seal."""
from pathlib import Path
import hashlib,runpy,sys
root=Path(__file__).resolve().parents[1]
previous=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/se-v11125-release/index.html')
raw=previous.read_text(encoding='utf8')
apply=runpy.run_path(str(root/'patches/v11_126_centered_build_permanent_routes_skills.py'))['apply']
html=apply(raw)
dest=Path('/tmp/se-v11126.html')
dest.write_bytes(html.encode('utf8'))
start=html.index('<script type="module">')+len('<script type="module">')
end=html.rindex('</script>',start)
Path('/tmp/se-v11126.mjs').write_text(html[start:end],encoding='utf8')
print('SE_V11126_CANDIDATE_BYTES',len(html.encode('utf8')))
print('SE_V11126_CANDIDATE_SHA256',hashlib.sha256(html.encode('utf8')).hexdigest())
