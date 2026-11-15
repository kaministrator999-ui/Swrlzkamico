#!/usr/bin/env python3
"""Read-only audit of the built v11.463 model render and mobile layout sources."""
import subprocess,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'_audit_v11_463_source'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
s=(out/'index.html').read_text('utf8')
patterns=[
 'function atelierViewModeApply(', 'function atelierViewRebuild(', 'function atelierViewModeFor(',
 "mode==='xray'", "mode==='wireframe'", 'const atelierViewModes=', 'function atelierMeshToolbarRefresh(',
 'function atelierComponentOverlay', 'function atelierMeshGizmo', 'function cameraUpdate(',
 'new THREE.AmbientLight(', 'new THREE.DirectionalLight(', 'new THREE.HemisphereLight(',
 "function se251", 'function se320RefreshTransformAccess(',
 ".atelier-inspector{", ".atelier-inspector {",
 'SE462_MODEL_WIRE_CLARITY_START','SE463'
]
for p in patterns:
 matches=list(re.finditer(re.escape(p),s))
 print('\nAUDIT',repr(p),'count',len(matches))
 for x in matches[:3]:
  start=max(0,x.start()-380);end=min(len(s),x.start()+(4200 if 'atelierViewModeApply' in p or 'cameraUpdate' in p else 2200))
  print(s[start:end].replace('\\r','').replace('\\0','')[:4500])
print('AUDIT_OK')
