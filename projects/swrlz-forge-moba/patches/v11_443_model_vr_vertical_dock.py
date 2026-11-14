"""§E v11.443: compact world-space vertical VR toolbar, right-side controls and foreground gizmo hits."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_443_VR_VERTICAL_TOOL_DOCK'

def one(html, old, new):
    n=html.count(old)
    if n!=1:
        raise AssertionError(('v11.443 anchor', old[:120], n))
    return html.replace(old,new,1)

def apply(html):
    dock=(ROOT/'runtime/model_vr_dock_v11_443.js').read_text(encoding='utf-8')
    assert 'SE443_MODEL_VR_VERTICAL_DOCK_START' in dock
    assert 'se374GizmoContact(record)' in dock
    html=one(html,'installPerformanceSettings();se189InstallPerfUI();',
             dock+'\ninstallPerformanceSettings();se189InstallPerfUI();')
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_442_SATCHEL_MOBILE_DIALOG',MARKER),
      ('ENGINE · MAKER v11.442','ENGINE · MAKER v11.443'),
      ('v11.442 · a movable satchel tutor for mobile browsers','v11.443 · VR vertical tool dock and slide-out settings'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.442'","window.SWRLZ_FORGE_BUILD={version:'v11.443'"),
      ('<title>§wyrl§ Engine · Maker v11.442</title>','<title>§wyrl§ Engine · Maker v11.443</title>')
    ]:
        html=one(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.442';source.version=11.442;"
    assert html.count(old)==5,('v11.443 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.443';source.version=11.443;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.442']
    notes['history'].insert(0,{'version':'v11.442','changes':notes.get('changes',[])})
    notes.update(version='v11.443',date='2026-11-14',
       title='Vertical VR tools with right-side contextual controls',
       changes=[
         'The existing world-space VR menu becomes a persistent narrow vertical tool dock. Selecting a tool expands the current native controls into an attached panel on its right, with an independent close control and brief slide motion.',
         'Existing VR ray hover, Trigger, Grip-driven whole-menu movement, native action dispatch, shortcuts, tutorial panels, menu placement and project save paths remain authoritative. Hidden panel targets cannot intercept model input.',
         'An explicit foreground transform-handle hit guard prioritizes active native Move, Rotate, Scale and Grab handles before meshes while preserving menu priority and native Grip transactions.',
         'This release changes VR presentation/input routing only, not persisted project/mesh descriptors or mobile Model Studio layout.'
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
