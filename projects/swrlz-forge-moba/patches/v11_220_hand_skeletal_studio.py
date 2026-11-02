"""§E v11.220 — genuine weighted skeletal hand, joint pose and keyframe studio.

Append-only integration of native SkinnedMesh into the existing Model Atelier
renderer. New hand starter ships 17 parented rest joints + editable animation;
no special renderer or mutation of saved projects, Quest, Sheep Tag or §C.
"""
from pathlib import Path
import json

def once(html, old, new):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.220 rig anchor',old[:160],count))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    core=(root/'runtime/model_atelier_skeletal_core_v11_220.js').read_text('utf8')
    ui=(root/'runtime/model_atelier_rig_studio_v11_220.js').read_text('utf8')
    html=once(html,"const se212Id='floating-hand-glove';",
              core+"\nconst se212Id='floating-hand-glove';")
    html=once(html,"  function refreshList(){",ui+"\n  function refreshList(){")
    # The native renderer builds real SkinnedMesh objects with per-vertex LBS
    # weights. Each selection/edit re-render rebuilds and re-binds the armature.
    html=once(html,"const mesh=new THREE.Mesh(atelierSculptApply(geometry(p),p),material(p));atelierViewModeApply(mesh,p);",
              "const mesh=se220RigMesh(p);atelierViewModeApply(mesh,p);")
    html=once(html,"    const current=partById(selection);",
              "    se220RigBind();se220RigRefresh();\n    const current=partById(selection);")
    html=once(html,"  function loop(){\n    if(!renderer)return;",
              "  function loop(){\n    if(!renderer)return;\n    se220RigFrame();")
    html=once(html,"    panel.addEventListener('keydown',e=>{",
              "    se220RigControlsInstall();\n    panel.addEventListener('keydown',e=>{")
    html=once(html,"  function close(){",
              "  function close(){\n    se220RigClose();")
    # Save and export: native project already includes rigging as model data.
    # Explicit import must verify rig metadata and restore it, too.
    html=once(html,"const frames=atelierValidatedFrameStore(source);",
              "const frames=atelierValidatedFrameStore(source);\n"
              "      if(source.rigging!=null&&!se220RigValidate(source.rigging))"
              "throw Error('Invalid rig hierarchy or animation frames.');")
    html=once(html,"model().poseFrames=frames.poseFrames;model().poseNeutral=frames.poseNeutral;",
              "model().poseFrames=frames.poseFrames;model().poseNeutral=frames.poseNeutral;\n"
              "      model().rigging=source.rigging?structuredClone(source.rigging):null;")
    # OBJ must export visible posed positions, not untouched bind geometry.
    old="const v=new THREE.Vector3().fromBufferAttribute(position,i).applyMatrix4(mesh.matrixWorld);"
    html=once(html,old,
              "const v=new THREE.Vector3().fromBufferAttribute(position,i);\n"
              "        if(mesh.isSkinnedMesh&&typeof mesh.applyBoneTransform==='function')mesh.applyBoneTransform(i,v);\n"
              "        v.applyMatrix4(mesh.matrixWorld);")
    html=once(html," delete m.assemblies;m.poseFrames=[];m.poseNeutral=null;m.editedAt='local';",
              " delete m.assemblies;m.poseFrames=[];m.poseNeutral=null;m.editedAt='local';\n"
              " m.rigging=se220CreateHandRig(digit);")
    html=once(html,
      " source.engine='§wyrl§ Engine · Maker v11.219';source.version=11.219;",
      " source.engine='§wyrl§ Engine · Maker v11.220';source.version=11.220;")
    css="""
.atelier-rig-studio{position:absolute;right:8px;top:7px;z-index:12;width:min(305px,80%);
 background:rgba(9,19,37,.97);color:#e9faff;border:1px solid #6486af;border-radius:10px;
 box-shadow:0 7px 24px #0008;max-height:70%;overflow:auto;overscroll-behavior:contain}
.atelier-rig-studio>summary{font-size:12px;font-weight:750;padding:9px;cursor:pointer;user-select:none}
.atelier-rig-body{display:grid;gap:8px;padding:8px 9px;font-size:11px}
.atelier-rig-body label{display:grid;gap:4px;font-size:11px}
.atelier-rig-body select,.atelier-rig-body button,.atelier-rig-body input[type=number]{
 width:100%;min-width:0;min-height:32px;padding:5px 7px;font-size:11px}
.atelier-rig-axes{display:grid;gap:5px}.atelier-rig-axes label{grid-template-columns:auto 1fr;align-items:center}
.atelier-rig-axes label input{grid-column:1/-1;min-height:24px;width:100%;accent-color:#cf55fc}
.atelier-rig-axes label span{text-align:right;font-variant-numeric:tabular-nums}
.atelier-rig-actions{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:4px}
.atelier-rig-actions button{padding:4px 2px;font-size:10px}
.atelier-rig-check{display:flex!important;flex-direction:row;gap:7px;align-items:center}
.atelier-rig-check input{min-height:0;width:auto}
.atelier-rig-timeline{display:grid;gap:5px;padding-top:5px;border-top:1px solid #405879}
.atelier-rig-timeline input[type=range]{width:100%;accent-color:#cf55fc}
.atelier-rig-undo{justify-self:start}
.atelier-rig-body small{font-size:10px;line-height:1.35;color:#b9cfe5}
@media(max-width:600px){.atelier-rig-studio{width:min(280px,77%);max-height:64%}
 .atelier-rig-studio>summary{padding:6px 8px}}
"""
    assert '</head>' in html
    html=html.replace('</head>','<style id="atelierRigStudioV11220">'+css+'</style>\n</head>',1)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_219_FINGER_RAIL_CONTACT',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_220_NATIVE_HAND_SKELETAL_STUDIO'),
      ('ENGINE · MAKER v11.219','ENGINE · MAKER v11.220'),
      ('v11.219 · Finger rail alignment under joint links',
       'v11.220 · Native hand rig, posing and keyframe studio'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.219'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.220'"),
      ('<title>§wyrl§ Engine · Maker v11.219</title>',
       '<title>§wyrl§ Engine · Maker v11.220</title>')
    ]:
        html=once(html,old,new)
    tag='const SE_RELEASE_NOTES='
    start=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Native armature: articulated Arcane Glove and keyframed posing studio',
     date='2026-11-02',changes=[
      'Rigged the new Arcane Glove starter with 17 connected, anatomically labeled wrist, palm, MCP/PIP/DIP and thumb CMC/MCP/IP bones, rest transforms and parent hierarchy in persisted Model Atelier project JSON.',
      'The connected hand topology and each separate armor/rune/finger cable mesh receive four-influence computed skin weights. WebGL SkinnedMesh / THREE.Skeleton performs actual joint-driven vertex deformation without rewriting neutral source geometry.',
      'Integrated a collapsible mobile-friendly Rig · Pose · Animate studio with bone picker, three rotational channels, skeleton helper visibility, open/fist/point/pinch poses, keyframe capture/deletion, timeline scrubbing, play/stop, looping and adjustable clip duration.',
      'Rig and keyframes are included in project saves and model JSON exports/imports; OBJ export applies the current skinned pose when supported. Rig state is validated on import. The older character pose-frame deck remains available for unrigged models.',
      'New hand starter only. Existing saved non-rigged hands are not silently modified; original glove mesh, thumb helix and finger rail design remain intact. Mobile and Quest real-device acceptance is owner-controlled.'
     ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+n:]
