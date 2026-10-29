#!/usr/bin/env python3
"""Guard fast §E CI path routing against weakened source-validation coverage."""
from pathlib import Path
import json
import re
import fnmatch

root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'source-manifest.json').read_text())
prefix='projects/swrlz-forge-moba/'
patches={prefix+p for p in manifest['patches']}
assert len(patches)==94 and 'projects/swrlz-forge-moba/patches/v11_62_mobile_adaptive.py' in patches, 'Every governed production patch must remain covered'

workflows={
 'verify-character-detail.yml': [
  'authoring/festival_anatomy_authoring_v11_20.mjs',
  'tests/model_head_anatomy_cpu.mjs',
  'scenes/v11_20_original.swyrl.json',
  'assets/character.png'
 ],
 'verify-model-atelier-v115.yml':[],
 'verify-engine-v1110-profiler.yml':['runtime/model_atelier_metrics_v11_10.js'],
 'verify-engine-v1111-pose.yml':['runtime/model_atelier_pose_frames_v11_11.js'],
 'verify-engine-v1112-grounded-poses.yml':['runtime/model_atelier_grounded_poses_v11_12.js'],
}
def triggered(path,globs):
 return any(fnmatch.fnmatchcase(path,pattern) for pattern in globs)
for name,features in workflows.items():
 path=root.parent.parent/'.github/workflows'/name
 source=path.read_text()
 assert source.startswith('name: '),name
 assert '  workflow_dispatch:' in source,('No full manual verification path',name)
 assert '  cancel-in-progress: true' in source,name
 assert '  pull_request:\n' in source,name
 scope=source.split('  pull_request:\n',1)[1].split('  workflow_dispatch:',1)[0]
 assert '    paths:\n' in scope,name
 globs=re.findall(r"^      - '([^']+)'$",scope,re.MULTILINE)
 assert globs,('Missing pull request paths',name)
 for dependency in [prefix+'source-manifest.json',prefix+'build_space.py',prefix+'payload/part-01.txt',*patches]:
  assert triggered(dependency,globs),(name,'missing sealed dependency',dependency)
 for incidental in [
  prefix+'ROADMAP.md',
  prefix+'reports/PRECISION_ATELIER_ACCEPTANCE_LEDGER_V11_29.md',
  prefix+'patches/v11_21_vertex_sphere_brush_preview.py',
  prefix+'runtime/model_atelier_reference_studio_v11_22.js',
  prefix+'tests/model_atelier_ref_dock_browser_v11_32.mjs']:
  assert not triggered(incidental,globs),(name,'unnecessary historical test',incidental)
 for item in features:
  assert triggered(prefix+item,globs),(name,'missing relevant suite input',item)
 print('ROUTING_PASS',name,'protected_inputs',len(globs))
print('V1162_CI_94_GOVERNED_PATCH_ROUTES_NO_PREVIEW_OR_DOCS_REDUCED_REBUILDS_PASS')
