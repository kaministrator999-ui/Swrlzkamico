"""§E v11.11: facial tuning and native bendable pose/camera frame editor."""
import json,re
from pathlib import Path

def once(source,old,new):
    n=source.count(old)
    if n!=1:raise AssertionError(f"v11.11 expected one anchor; got {n}: {old[:95]!r}")
    return source.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    source=json.loads((root/'scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json').read_text('utf8'))
    data=source['project']['modelAtelier']
    parts=data['parts']
    assert len(parts)==811 and len({p['id'] for p in parts})==811
    byid={p['id']:p for p in parts}
    face={
        'model-0001':{'scale':[.312,.398,.287]},
        'model-0025':{'scale':[.126,.108,.044],'position':[-.158,3.978,.297]},
        'model-0042':{'scale':[.126,.108,.044],'position':[.158,3.978,.297]},
        'model-0026':{'scale':[.077,.081,.023],'position':[-.156,3.974,.344]},
        'model-0043':{'scale':[.077,.081,.023],'position':[.156,3.974,.344]},
        'model-0027':{'scale':[.034,.051,.012],'position':[-.154,3.975,.370]},
        'model-0044':{'scale':[.034,.051,.012],'position':[.154,3.975,.370]},
        'model-0028':{'scale':[.092,.038,.014],'position':[-.257,3.788,.287]},
        'model-0045':{'scale':[.092,.038,.014],'position':[.257,3.788,.287]},
        'model-0046':{'scale':[.136,.013,.017],'position':[.016,3.744,.321],'rotation':[0,0,.095]},
        'model-0047':{'scale':[.037,.042,.038],'position':[0,3.858,.333]},
        'atelier-v117-0421':{'scale':[.17,.018,.032],'position':[-.155,4.128,.333],'rotation':[0,0,-.10]},
        'atelier-v117-0438':{'scale':[.17,.018,.032],'position':[.155,4.128,.333],'rotation':[0,0,.10]}
    }
    for key,changes in face.items():
        assert key in byid
        byid[key].update(changes)
    source['version']=11.11
    source['project']['name']='Festival Jester v11.11 · refined face, native pose studio'
    # The v11.9 source asset stays byte-identical: only the new default project
    # embedded in the generated editor is authored here.
    pat=r'const MODEL_ATELIER_CANONICAL_PROJECT=.*?;\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    replacement='const MODEL_ATELIER_CANONICAL_PROJECT='+json.dumps(source,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'
    html,n=re.subn(pat,lambda _:replacement,html,count=1,flags=re.DOTALL)
    assert n==1,'native starter scene anchor missing'
    code=(root/'runtime/model_atelier_pose_frames_v11_11.js').read_text('utf8')
    assert 'V11_11_FACE_POSE_FRAMES' in code
    html=once(html,'  function refreshList(){',code+'\n  function refreshList(){')
    deck="""<details id="modelAtelierPoseDeck" class="atelier-pose-deck">
      <summary>✦ Pose & camera frames</summary>
      <div class="atelier-pose-controls">
        <label>Pose <select id="modelAtelierPoseSelect" aria-label="Choose pose"></select></label>
        <button type="button" id="modelAtelierPoseApply">Apply pose</button>
        <label>Frame name <input id="modelAtelierPoseName" maxlength="36" placeholder="My victory frame" aria-label="Name custom pose frame"></label>
        <div class="atelier-pose-actions"><button type="button" id="modelAtelierPoseSave">Save frame</button><button type="button" id="modelAtelierPoseDelete">Delete saved</button></div>
        <label>Camera <select id="modelAtelierPoseView" aria-label="Camera view"><option value="three">3/4</option><option value="front">Front</option><option value="left">Left</option><option value="right">Right</option><option value="back">Back</option><option value="hero">Hero</option></select></label>
        <button type="button" id="modelAtelierPoseViewApply">Apply view</button>
        <small>Editable spline knee bends, not skeletal skinning. Save Project / JSON to retain frames.</small>
      </div>
    </details>"""
    html=once(html,'<div class="atelier-viewport-controls">',''.join(deck.splitlines())+'<div class="atelier-viewport-controls">')
    html=once(html,"    $m('ImportFile').addEventListener('change',e=>importJSON(e.target.files?.[0]));",
      "    $m('ImportFile').addEventListener('change',e=>importJSON(e.target.files?.[0]));\n    atelierPoseDeckInstall();")
    html=once(html,'    resize();renderParts();refreshList();refreshInspector();loop();',
      '    resize();renderParts();refreshList();refreshInspector();atelierRefreshPoseChoices();loop();')
    html=once(html,
      "checkpoint();model().parts=structuredClone(source.parts);selection=null;signalEdited();status('Validated model imported. You can undo this import.');",
      "const frames=atelierValidatedFrameStore(source);\n      checkpoint();model().parts=structuredClone(source.parts);\n      model().poseFrames=frames.poseFrames;model().poseNeutral=frames.poseNeutral;\n      selection=null;signalEdited();atelierRefreshPoseChoices();status('Validated model and saved frames imported. You can undo the part import.');")
    css="""
/* §E v11.11: pose controls collapse to one tiny handle over the modeling viewport. */
.atelier-pose-deck{position:absolute;top:10px;right:10px;z-index:3;width:min(264px,62%);max-height:72%;overflow:auto;border:1px solid #6584a7;border-radius:9px;background:rgba(15,24,45,.94);color:#edfaff;box-shadow:0 3px 12px #080e1c80}
.atelier-pose-deck>summary{cursor:pointer;padding:9px;font-size:12px;font-weight:700}
.atelier-pose-controls{display:grid;gap:6px;padding:8px}
.atelier-pose-controls label{display:grid;gap:3px;font-size:11px}
.atelier-pose-controls input,.atelier-pose-controls select,.atelier-pose-controls button{width:100%;min-height:34px;box-sizing:border-box;border:1px solid #6484a1;border-radius:5px;padding:5px;background:#1d2d48;color:#fff;font-size:12px}
.atelier-pose-actions{display:grid;grid-template-columns:1fr 1fr;gap:5px}
.atelier-pose-controls small{font-size:10px;line-height:1.3;opacity:.8}
@media (max-width:600px){.atelier-pose-deck{width:min(235px,68%);max-height:60%}}
"""
    html=once(html,'/* v11.8 procedural sculpt tools:',css+'/* v11.8 procedural sculpt tools:')
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_10_MEASURED_GEOMETRY_PROFILER',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_11_FACE_POSE_FRAMES')
    html=html.replace('Maker v11.10','Maker v11.11').replace('MAKER v11.10','MAKER v11.11')
    html=html.replace("version:'v11.10'","version:'v11.11'").replace('version:11.10','version:11.11')
    html=once(html,'v11.10 · measured geometry and figure atelier','v11.11 · expressive face and pose frame studio')
    return html
