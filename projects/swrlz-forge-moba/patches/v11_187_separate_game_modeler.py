"""§E v11.187: direct Modeler page, native tab switching and project-free draft."""
from pathlib import Path
import json

def once(s,old,new):
    count=s.count(old)
    if count!=1: raise AssertionError(('v11.187 anchor',old[:125],count))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    css=(root/'runtime/engine_separate_workspaces_v11_187.css').read_text(encoding='utf8')
    js=(root/'runtime/engine_separate_workspaces_v11_187.js').read_text(encoding='utf8')
    html=html.replace('</head>','<style id="se187SeparateWorkspaces">\n'+css+'\n</style>\n</head>',1)
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    # Make existing editor's *model data* optional; game scene/currentProject never
    # becomes a fake modeling project just to enter Modeler.
    html=once(html,
      "function model(){return currentProject?.kind==='model-atelier'?currentProject.modelAtelier:null;}",
      """function model(){
    if(window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.())
      return window.SWYRL_ENGINE_WORKSPACES.scratchModel();
    return currentProject?.kind==='model-atelier'?currentProject.modelAtelier:null;
  }""")
    old="""    if(currentProject&&typeof currentProject==='object')currentProject.modelAtelier.editedAt='local';
    // The workbench has its own part history; the parent project must still
    // register dirty state so Projects/Load won't silently discard model edits.
    if(typeof markDirty==='function')markDirty();"""
    new="""    const draft=window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()===true;
    if(draft)window.SWYRL_ENGINE_WORKSPACES.draftEdited();
    else{
      if(currentProject?.modelAtelier)currentProject.modelAtelier.editedAt='local';
      // Project-based Model Atelier edits still use the native save/dirty flow.
      if(typeof markDirty==='function')markDirty();
    }"""
    html=once(html,old,new)
    html=once(html,
      "status('Editable native project · '+model().parts.length+' parts. Save Project or export JSON to keep changes.');",
      "status(draft?'Untitled model draft · '+model().parts.length+' meshes · locally retained or export JSON.':'Editable native project · '+model().parts.length+' parts. Save Project or export JSON to keep changes.');")
    html=once(html,
      "if(data.parts.length<=1){status('Keep at least one mesh in the model.',true);return;}",
      "if(data.parts.length<=1&&!window.SWYRL_ENGINE_WORKSPACES?.isScratchModel?.(data)){status('Keep at least one mesh in the model.',true);return;}")
    html=once(html,
      "download('prism-jester.model.json',JSON.stringify({schema:'swyrl-model-atelier-v1',model:structuredClone(model())},null,2)+'\\n','application/json');",
      "download(window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()?'untitled-model.model.json':'prism-jester.model.json',JSON.stringify({schema:'swyrl-model-atelier-v1',model:structuredClone(model())},null,2)+'\\n','application/json');")
    html=once(html,
      "    const button=$m('Reopen');if(button)button.hidden=!model();",
      "    const button=$m('Reopen');if(button)button.hidden=currentProject?.kind!=='model-atelier'||window.SWYRL_ENGINE_WORKSPACES?.modelerActive?.()===true;")
    html=once(html,
      "  return Object.freeze({open,close,install,syncProject,status:()=>({active:!!model(),open:!!panel&&!panel.hidden,count:model()?.parts?.length||0,selected:selection})});",
      """  function resetScratch(){
    undo=[];redo=[];selection=null;
    if(panel&&!panel.hidden){renderParts();refreshList();refreshInspector();}
  }
  return Object.freeze({open,close,install,syncProject,resetScratch,status:()=>({active:!!model(),open:!!panel&&!panel.hidden,count:model()?.parts?.length||0,selected:selection})});""")
    # A new user-loaded model takes precedence over the untitled scratch mode.
    html=once(html,
      "  const result=modelAtelierPreviousLoad(...args);",
      "  const result=modelAtelierPreviousLoad(...args);\n  window.SWYRL_ENGINE_WORKSPACES?.onNativeLoad?.(args[0]);")
    # A direct modeler.html request does not restore/load a game scene first.
    # Returning to Game will initialize the normal default native world.
    html=once(html,
      "function se128LaunchStartupProject(){",
      """function se128LaunchStartupProject(){
 if(/\\/modeler\\.html$/i.test(location.pathname)&&!new URLSearchParams(location.search).has('project')){
  window.se128StartupPending=false;
  return;
 }""")
    # Native close can still work; controller adds two-way workspace tabs to the panel.
    html=once(html,
      "panel=document.createElement('section');panel.id='modelAtelierPanel';panel.className='model-atelier';",
      "panel=document.createElement('section');panel.id='modelAtelierPanel';panel.className='model-atelier se187-modeler-page';")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_186_FIRST_PAINT_WISP_BOOT','SWYRL_ENGINE_DEPLOY_MARKER: V11_187_GAME_MODELER_WORKSPACES'),
      ('ENGINE · MAKER v11.186','ENGINE · MAKER v11.187'),
      ('v11.186 · immediate glitch-wisp startup','v11.187 · Game Engine and Modeler workspaces'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.186'","window.SWRLZ_FORGE_BUILD={version:'v11.187'"),
      ('<title>§wyrl§ Engine · Maker v11.186</title>','<title>§wyrl§ Engine · Maker v11.187</title>'),
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Separate Game Engine and Modeler pages with independent untitled modeling',
      date='2026-10-31',changes=[
       'Provide two distinct routable pages: index.html for Game Engine and modeler.html for Modeler. The shared runtime switches in place via visible tabs; no reload or game scene replacement when switching.',
       'Modeler now opens without creating/loading a named project, using a real blank native model draft with Add, Export, Import, sculpt, geometry and transform tools.',
       'Keep the game scene/currentProject untouched while editing the untitled model. Native named model projects still use their existing project/dirty/save behavior.',
       'Retain draft on this browser with bounded localStorage and validation; provide Blank model and Export JSON. Export remains available when quota/storage fails.',
       'Direct modeler.html startup skips game default scene loading and can switch back to the game editor without a project-selection prerequisite.',
       'Preserve earlier VR, editor, chat, saved project defaults, menu routing and the first-paint glitch-wisp boot. Owner Android/Quest acceptance remains pending.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+count:]
