"""Future versions derive notes and dismissal identity from the manifest."""
from pathlib import Path
import json,runpy,tempfile
root=Path(__file__).resolve().parents[1]
build_notes=runpy.run_path(str(root/'patches/v11_84_sheep_build_routes.py'))['release_notes']
known=json.loads((root/'runtime/engine_release_notes_v11_84.json').read_text())
assert build_notes(root,json.loads((root/'source-manifest.json').read_text()))==known
with tempfile.TemporaryDirectory() as folder:
    target=Path(folder);(target/'runtime').mkdir();(target/'patches').mkdir()
    (target/'runtime/engine_release_notes_v11_84.json').write_text(json.dumps(known))
    (target/'patches/v11_84.py').write_text('"""Current release."""')
    (target/'patches/v11_85.py').write_text('"""New future feature."""')
    future=build_notes(target,{'name':'§wyrl§ Engine v11.85','patches':['patches/v11_84.py','patches/v11_85.py']})
    assert future['version']=='v11.85' and future['changes']==['New future feature.']
    assert future['history'][0]['version']=='v11.84' and future['history'][0]['changes']==known['changes']
print('AUTOMATIC_FUTURE_MANIFEST_VERSION_AND_PATCH_HISTORY_PASS')
