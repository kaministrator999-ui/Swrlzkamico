"""§E v11.341: Model VR hover cost and model-centered joystick orbit."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def one(html,old,new):
    assert html.count(old)==1, ("v11.341 source anchor",old[:80],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    for old,new in [
        ('runtime/model_vr_workspace_v11_340.js','runtime/model_vr_workspace_v11_341.js'),
        ('runtime/model_studio_vr_ui_v11_340.js','runtime/model_studio_vr_ui_v11_341.js'),
    ]:
        html=one(html,(ROOT/old).read_text('utf8'),(ROOT/new).read_text('utf8'))
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_340_IMMERSIVE_MODEL_STUDIO','SWYRL_ENGINE_DEPLOY_MARKER: V11_341_MODEL_VR_HOVER_ORBIT'),
        ('ENGINE · MAKER v11.340','ENGINE · MAKER v11.341'),
        ('v11.340 · immersive Model Studio and controller authoring','v11.341 · faster XR picking and smooth model orbit'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.340'","window.SWRLZ_FORGE_BUILD={version:'v11.341'"),
        ('<title>§wyrl§ Engine · Maker v11.340</title>','<title>§wyrl§ Engine · Maker v11.341</title>'),
    ]:html=one(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.340';source.version=11.340;"
    assert html.count(old)==3
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.341';source.version=11.341;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(item.get('version')=='v11.340' for item in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.340','changes':notes.get('changes',[])})
    notes.update(version='v11.341',title='Smooth model orbit and optimized VR hover',date='2026-11-08',changes=[
        'Native Model VR throttles idle hover picking, reuses one per-frame model projection, caches part bounds and culls ray misses before triangle tests. Trigger selection and grip remain immediate.',
        'Left stick pans the workbench, right stick orbits the model smoothly on both axes. Hold right stick click plus vertical movement to zoom. Precision mode reduces navigation speed.',
        'Recenter resets orbit pitch and zoom. Native mesh, rig, transformations and undo history remain authoritative.',
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
