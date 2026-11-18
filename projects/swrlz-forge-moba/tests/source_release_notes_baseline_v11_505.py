#!/usr/bin/env python3
"""Regression: the release-note baseline must preserve v11.504 history bytes."""
import copy,importlib.util,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sheep84_baseline',root/'patches/v11_84_sheep_build_routes.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
original=json.loads((root/'source-manifest.json').read_text('utf8'))
assert original['name']=='§wyrl§ Engine v11.504',original['name']
assert len(original['patches'])==481
a=module.release_notes(root,original)
candidate=copy.deepcopy(original)
candidate.update(name='§wyrl§ Engine v11.505')
candidate['patches'].append('patches/v11_505_action_prerequisites.py')
candidate['releaseNotesBaseline']={'version':'v11.504','patchCount':481}
b=module.release_notes(root,candidate)
assert json.dumps(a,ensure_ascii=False,separators=(',',':'))==json.dumps(b,ensure_ascii=False,separators=(',',':'))
without=copy.deepcopy(candidate);del without['releaseNotesBaseline']
assert module.release_notes(root,without)!=a
print('SE505_RELEASE_NOTES_BASELINE_PASS',json.dumps({'parent':'v11.504','patches':481,'stable':True}))
