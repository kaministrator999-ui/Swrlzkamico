"""§E v11.435 — visible, actionable transform handles in the normal VR Grab tool."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_435_MODEL_VR_GRAB_GIZMO'
def one(html,old,new):
    assert html.count(old)==1,('v11.435 anchor',old[:110],html.count(old))
    return html.replace(old,new,1)
def apply(html):
    code=(ROOT/'runtime/model_vr_grab_gizmo_v11_435.js').read_text('utf8')
    assert 'SE435_MODEL_VR_GRAB_GIZMO_START' in code
    html=one(html,'installPerformanceSettings();se189InstallPerfUI();',code+'\ninstallPerformanceSettings();se189InstallPerfUI();')
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_434_SHEEP_CROWDED_VR',MARKER),
        ('ENGINE · MAKER v11.434','ENGINE · MAKER v11.435'),
        ('v11.434 · crowded Sheep Tag VR and faithful rendering','v11.435 · VR Grab gizmos and constrained axis grips'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.434'","window.SWRLZ_FORGE_BUILD={version:'v11.435'"),
        ('<title>§wyrl§ Engine · Maker v11.434</title>','<title>§wyrl§ Engine · Maker v11.435</title>')
    ]:html=one(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.434';source.version=11.434;"
    assert html.count(old)==5,('v11.435 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.435';source.version=11.435;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.434']
    notes['history'].insert(0,{'version':'v11.434','changes':notes.get('changes',[])})
    notes.update(version='v11.435',date='2026-11-12',title='VR Grab shows transform gizmos',changes=[
      'Selecting a model part now keeps visible XYZ Move handles at its selection pivot while Grab is active, rather than hiding the helper when Inspect hands off to Grab.',
      'A tracked controller Grip on an arrow constrains a native Move along that local axis, with native live preview, cancel and one-step Undo. Gripping outside the arrows retains free-form Grab with wrist rotation and stick scaling.',
      'Explicit Move, Rotate and uniform Scale gizmos, mobile touch handles, independent VR menus, object selection and saved geometry remain unchanged.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
