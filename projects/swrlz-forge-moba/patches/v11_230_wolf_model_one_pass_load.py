"""§E v11.230 — load the active Astra wolf once, with its rig ready before rendering.

The v11.88 wolf-loader override remained authoritative after v11.227 edited
the obsolete v11.87 branch. The public wrapper reopened the detailed wolf
after its first (unrigged) render, causing wasted WebGL allocations and an
unreliable mobile starter load. Preserve saved projects and the original game.
"""
from pathlib import Path
import json

def once(s, old, new, context):
    count=s.count(old)
    if count!=1:
        raise AssertionError(("v11.230 wolf loader anchor",context,old[:140],count))
    return s.replace(old,new,1)

def apply(html):
    # The effective wolf loader was assigned by v11.88 and has its fetch
    # rewritten by v11.90. Limit replacements to this actual live function.
    start=html.index("const atelierOriginalWolfLoader=loadAnimalProject;")
    end=html.index("ModelAtelier.install();",start)
    active=html[start:end]
    active=once(active,
        "ModelAtelier.close();loadProject(data,{workspaceLocal:true});initializeHistory('Opened original Astra organic refinement');",
        """ModelAtelier.close();loadProject(data,{workspaceLocal:true});
 if(currentProject?.kind!=='model-atelier'||!currentProject.modelAtelier)
  throw Error('Wolf project did not activate.');
 const wolf=currentProject.modelAtelier;
 se224WolfEnhanceModel(wolf);
 wolf.wolfRig=se224WolfRigSpec();
 wolf.wolfAnimations=se224WolfClips();
 window.SWYRL_WOLF_LOAD_AUDIT={stage:'active-attached',species,parts:wolf.parts.length,
  rig:se224WolfRigValid(wolf.wolfRig),clips:wolf.wolfAnimations.clips.length};
 initializeHistory('Opened rigged Astra wolf starter');""",
        'active loader rig before first open')
    active=once(active,
        "panel.classList.add('courier-studio');studio.hidden=false;studio.textContent='Edit model';studio.setAttribute('aria-pressed','true');",
        "panel.classList.remove('courier-studio');studio.hidden=false;studio.textContent='Studio view';studio.setAttribute('aria-pressed','false');",
        'wolf rig controls visible on first open')
    html=html[:start]+active+html[end:]

    # v11.227 public API used to render once unrigged, close, rebuild and
    # render again. It now only audits the already-rigged first open.
    public_start=html.index("loadAnimal:async(species,options={})=>{")
    public_end=html.index(" return ok;\n},",public_start)
    block=html[public_start:public_end]
    old="""if(ok&&species==='wolf'&&currentProject?.kind==='model-atelier'){
  ModelAtelier.close();
  const active=currentProject.modelAtelier;
  se224WolfEnhanceModel(active);
  active.wolfRig=se224WolfRigSpec();
  active.wolfAnimations=se224WolfClips();
  markSaved();ModelAtelier.syncProject();ModelAtelier.open();
  // The historic courier 'Studio view' intentionally hides the inspector.
  // A rigged Wolf Model opens in editable mode so bone sliders remain usable.
  document.getElementById('modelAtelierPanel')?.classList.remove('courier-studio');
  const viewSwitch=document.getElementById('modelAtelierCourierStudio');
  if(viewSwitch){viewSwitch.textContent='Studio view';viewSwitch.setAttribute('aria-pressed','false');}
  window.SWYRL_WOLF_LOAD_AUDIT={stage:'public-attached',species,parts:active.parts.length,rig:!!active.wolfRig};
 }"""
    new="""if(ok&&species==='wolf'&&currentProject?.kind==='model-atelier'){
  const active=currentProject.modelAtelier;
  window.SWYRL_WOLF_LOAD_AUDIT={stage:'public-attached',species,
   parts:active.parts.length,rig:se224WolfRigValid(active.wolfRig),
   clips:active.wolfAnimations?.clips?.length||0};
 }"""
    block=once(block,old,new,'public loader duplicate reopen')
    html=html[:public_start]+block+html[public_end:]

    old=" source.engine='§wyrl§ Engine · Maker v11.229';source.version=11.229;"
    assert html.count(old)==2,('wolf loader source provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.230';source.version=11.230;")
    for a,b in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_229_SHEEP_HOUSE_NATIVE_LOAD_REPAIR',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_230_WOLF_MODEL_ONE_PASS_LOAD'),
      ('ENGINE · MAKER v11.229','ENGINE · MAKER v11.230'),
      ('v11.229 · Sheep Tag house model load validation repair',
       'v11.230 · Wolf Model single-pass rigged load repair'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.229'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.230'"),
      ('<title>§wyrl§ Engine · Maker v11.229</title>',
       '<title>§wyrl§ Engine · Maker v11.230</title>')
    ]:
        html=once(html,a,b,'v11.230 release identity')
    tag='const SE_RELEASE_NOTES='
    start=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Astra wolf starter: single-pass native rig loading',
      date='2026-11-02',changes=[
        'Fix the active Astra wolf-model loader override bypassing the v11.227 setup. Attach the 14-joint armature and all ten authored motion clips before the first model viewport render.',
        'Remove the redundant second Model Atelier close/reopen and GPU mesh reconstruction. Keep editable Wolf Rig & Motion controls visible when the wolf opens.',
        'Preserve original Astra fur, equipment and authoring geometry, native Sheep Tag wolves and gameplay, other starters and previously saved owner models. No forced migration of saved models.',
        'Targeted release checks cover active wolf loader linkage and a single render path; physical Android and Quest acceptance remains with the owner.'
      ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+n:]
