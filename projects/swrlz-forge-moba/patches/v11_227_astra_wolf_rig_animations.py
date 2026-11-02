"""§E v11.227 — Astra wolf appearance, weighted native rig and Sheep Tag clips.

Single shared Wolf pose source for game + modeler. No gameplay rules or
network state changes. Only fresh wolf-model starter is rebuilt in memory.
"""
from pathlib import Path
import json

def once(html,old,new):
    n=html.count(old)
    if n!=1:
        raise AssertionError(('v11.227 wolf patch anchor',old[:160],n))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    runtime=root/'runtime'
    shared=(runtime/'wolf_rig_motions_v11_224.js').read_text('utf8')
    fidelity=(runtime/'wolf_visual_fidelity_v11_224.js').read_text('utf8')
    studio=(runtime/'model_atelier_wolf_studio_v11_224.js').read_text('utf8')
    game=(runtime/'sheep_tag_wolf_animation_v11_224.js').read_text('utf8')

    # Functional motion/visual sources are available at startup to both
    # engine/world code and the Model Atelier lexical scope.
    html=once(html,'ModelAtelier.install();',
              shared+'\n'+fidelity+'\nModelAtelier.install();')
    # Furred Astra's optimized game template keeps its existing coat + gear;
    # overlay parts are physically parented to head, moving jaw, and body.
    html=once(html,
        "if(type==='st-wolf')return ModelAtelier.createCourierHunter();",
        "if(type==='st-wolf')return se224WolfGameVisual(ModelAtelier.createCourierHunter());")

    html=once(html,
      "async function loadAnimalProject(species,force=false,rebuild=false){",
      """async function loadAnimalProject(species,force=false,rebuild=false){
 window.SWYRL_WOLF_LOAD_AUDIT={stage:'entered',species};""")
    # The stock wolf-model loads the actual Astra scene (not a blank model).
    # New starter gets editable detail parts, real rig and native authored
    # keyframes; saved user copies are never silently rewritten.
    # The wolf-model card historically fetched Fen while its label described
    # Astra. Load the actual furred Astra that Sheep Tag uses by default.
    html=once(html,
      "fetch('scenes/model-atelier-organic-'+species+'-v11-87.swyrl.json')",
      "fetch(species==='wolf'?'scenes/model-atelier-furred-astra-v11-90.swyrl.json':'scenes/model-atelier-organic-sheep-v11-87.swyrl.json')")
    html=once(html,
      "if(species==='sheep')data.project.modelAtelier.sheepAnimations=se222SheepClips();",
      """if(species==='sheep')data.project.modelAtelier.sheepAnimations=se222SheepClips();
 if(species==='wolf'){
  window.SWYRL_WOLF_LOAD_AUDIT={stage:'pre',species,rawName:data.project.modelAtelier?.name,rawParts:data.project.modelAtelier?.parts?.length};
  se224WolfEnhanceModel(data.project.modelAtelier);
  window.SWYRL_WOLF_LOAD_AUDIT.stage='prepared';
  window.SWYRL_WOLF_LOAD_AUDIT.preparedParts=data.project.modelAtelier.parts.length;
  window.SWYRL_WOLF_LOAD_AUDIT.preparedRig=!!data.project.modelAtelier.wolfRig;
  data.project.modelAtelier.wolfRig=se224WolfRigSpec();
  data.project.modelAtelier.wolfAnimations=se224WolfClips();
 }""")
    # ModelAtelier's loadProject wrapper can normalize legacy scene metadata.
    # Ensure the active project—not only the fetched JSON—receives the new
    # authored wolf rig and details before ModelAtelier.open() renders it.
    loader_start=html.index("async function loadAnimalProject(species,")
    loader_end=html.index("const atelierAnimalTemplateBase=",loader_start)
    before=html[loader_start:loader_end]
    assert before.count("ModelAtelier.close();loadProject(data,{workspaceLocal:true});initializeHistory")==1
    after=before.replace("ModelAtelier.close();loadProject(data,{workspaceLocal:true});initializeHistory",
      """ModelAtelier.close();loadProject(data,{workspaceLocal:true});
 if(species==='wolf'&&currentProject?.kind==='model-atelier'){
  se224WolfEnhanceModel(currentProject.modelAtelier);
  currentProject.modelAtelier.wolfRig=se224WolfRigSpec();
  currentProject.modelAtelier.wolfAnimations=se224WolfClips();
  window.SWYRL_WOLF_LOAD_AUDIT.stage='assigned';
  window.SWYRL_WOLF_LOAD_AUDIT.activeName=currentProject.modelAtelier?.name;
  window.SWYRL_WOLF_LOAD_AUDIT.activeParts=currentProject.modelAtelier?.parts?.length;
  window.SWYRL_WOLF_LOAD_AUDIT.activeRig=!!currentProject.modelAtelier?.wolfRig;
 }
 initializeHistory""")
    html=html[:loader_start]+after+html[loader_end:]
    # The user-facing Model Atelier loader must carry rig metadata through
    # any later legacy project-normalization before the editor is re-rendered.
    # Only an explicit fresh wolf request gets this repair; saved scenes
    # and all other model starters are never migrated.
    html=once(html,
      "loadAnimal:(species,options={})=>loadAnimalProject(species,!!options.force,!!options.rebuild),",
      """loadAnimal:async(species,options={})=>{
 const ok=await loadAnimalProject(species,!!options.force,!!options.rebuild);
 if(ok&&species==='wolf'&&currentProject?.kind==='model-atelier'){
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
 }
 return ok;
},""")
    # User-facing Wolf Model card and URL deep link share the proven public
    # rigged loader path, not the older unrigged internal starter path.
    html=once(html,
      "return loadAnimalProject(template==='sheep-model'?'sheep':'wolf',force).catch(e=>{toast(e.message);return false;});",
      "return (template==='sheep-model'?loadAnimalProject('sheep',force):window.SWYRL_ENGINE_MODEL_ATELIER.loadAnimal('wolf',{force})).catch(e=>{toast(e.message);return false;});")
    html=once(html,
      "queueMicrotask(()=>loadAnimalProject(new URLSearchParams(location.search).get('project')==='sheep-model'?'sheep':'wolf',true).catch(e=>toast(e.message)))",
      "queueMicrotask(()=>(new URLSearchParams(location.search).get('project')==='sheep-model'?loadAnimalProject('sheep',true):window.SWYRL_ENGINE_MODEL_ATELIER.loadAnimal('wolf',{force:true})).catch(e=>toast(e.message)))")
    html=once(html,'  function refreshList(){',studio+'\n  function refreshList(){')
    html=once(html,'const mesh=se220RigMesh(p);','const mesh=se224WolfRigMesh(p);')
    html=once(html,'se220RigBind();se220RigRefresh();',
        'se220RigBind();se224WolfRigBind();se220RigRefresh();')
    html=once(html,
      'se220RigControlsInstall();se221StudioInstall();se222SheepStudioInstall();',
      'se220RigControlsInstall();se221StudioInstall();se222SheepStudioInstall();se224WolfStudioInstall();')
    html=once(html,
      'se220RigFrame();se222SheepPreviewFrame();',
      'se220RigFrame();se222SheepPreviewFrame();se224WolfPreviewFrame();')
    html=once(html,
      'se222SheepPreviewClose();se220RigClose();',
      'se224WolfPreviewClose();se222SheepPreviewClose();se220RigClose();')

    # Import metadata is bounded and validated. Do not allow imported JSON
    # to inject unknown bone names, arbitrary links, invalid clips or NaNs.
    html=once(html,
      'model().parts=structuredClone(source.parts);',
      """model().parts=structuredClone(source.parts);
       if(source.wolfRig||source.wolfAnimations){
        if(!se224WolfRigValid(source.wolfRig)||!se224WolfClipsValid(source.wolfAnimations))
         throw Error('Invalid wolf armature or clip keys.');
        model().wolfRig=structuredClone(source.wolfRig);
        model().wolfAnimations=structuredClone(source.wolfAnimations);
       }""")

    # Render-only wolf pose overlay runs after existing Sheep Tag animation
    # and particle FX, using the current game tick only.
    html=once(html,'window.SWRLZ_FORGE_BUILD=',game+'\nwindow.SWRLZ_FORGE_BUILD=')

    css="""
.atelier-wolf-studio{background:rgba(10,23,37,.96);border:1px solid #7b9b8b;
 border-radius:9px;color:#e8edf1;max-width:100%;padding:5px 8px;
 font-size:11px;position:relative;z-index:auto;flex:0 0 auto;
 max-height:none;overflow:visible;box-shadow:0 5px 14px #0007}
.atelier-wolf-studio[hidden]{display:none!important}
.atelier-wolf-studio summary{cursor:pointer;font-weight:750;padding:5px 0}
.atelier-wolf-panel{display:grid;gap:7px;min-width:0;padding:4px 0}
.atelier-wolf-panel label{display:grid;gap:3px;font-size:11px}
.atelier-wolf-panel select,.atelier-wolf-panel button{min-height:34px;max-width:100%;font-size:11px}
.atelier-wolf-panel input[type=range]{width:100%;min-height:24px;accent-color:#efb75c}
.atelier-wolf-panel output{text-align:right;color:#f0c77c}
.atelier-wolf-actions{display:flex;gap:5px}.atelier-wolf-actions button{flex:1}
.atelier-wolf-axes{display:grid;gap:3px;grid-template-columns:repeat(3,minmax(0,1fr))}
.atelier-wolf-axes label{min-width:0;word-break:normal}
.atelier-wolf-check{display:flex!important;flex-direction:row;align-items:center;gap:6px}
.atelier-wolf-panel small{color:#a8bcc6;line-height:1.35}
@media(max-width:640px){.atelier-wolf-studio{max-width:100%;padding:4px 6px}
 .atelier-wolf-axes{grid-template-columns:1fr}}
"""
    assert '</head>' in html
    html=html.replace('</head>','<style id="se224WolfStudio">'+css+'</style>\n</head>',1)

    html=once(html,
      " source.engine='§wyrl§ Engine · Maker v11.226';source.version=11.226;",
      " source.engine='§wyrl§ Engine · Maker v11.227';source.version=11.227;")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_226_SHEEP_BUILDING_MODEL_STARTERS',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_227_ASTRA_WOLF_RIG_SHEEP_TAG'),
      ('ENGINE · MAKER v11.226','ENGINE · MAKER v11.227'),
      ('v11.226 · five sheep-faction building model starters',
       'v11.227 · Astra wolf rig and Sheep Tag animations'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.226'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.227'"),
      ('<title>§wyrl§ Engine · Maker v11.226</title>',
       '<title>§wyrl§ Engine · Maker v11.227</title>')
    ]:
        html=once(html,old,new)
    tag='const SE_RELEASE_NOTES='
    start=html.index(tag)+len(tag)
    notes,size=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Astra Wolf · refined appearance, rigged model and Sheep Tag motions',
      date='2026-11-02',changes=[
        'Astra keeps its original organic furred body, courier equipment, comet tail and 4K texture maps. Added mirrored expressive brows, layered cheek/neck fur, cream muzzle highlighting, sculpted nose and moving jaw with small canine teeth. Details are native editable topology pieces in the wolf starter.',
        'The freshly loaded Wolf Model starter now has an actual 14-bone hierarchy (root, spine, neck, head, jaw, tail, and upper/lower pivots for all four legs) driving four-influence GPU skinning, including the continuous torso and sculpted attachments.',
        'Model Atelier Wolf Rig & Motion panel can preview, scrub and edit ten animations and individual bone rotations, show skeleton pivots and save animation keys to exported model JSON.',
        'Sheep Tag wolves share the same pose source for Idle, Sniff, Stalk, Walk, Run, Pounce, Bite, Howl, Alert and Victory. The game uses its proven optimized mesh/pivots and a new articulated jaw; all animation changes are cosmetic and ride the existing update tick.',
        'The native wolf headstart, collisions, pathfinding, attacks, fog, camera, LAN messages, Sheep Tag economy and Clover animations remain unchanged. Existing saved user models and clips are preserved.'
      ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
