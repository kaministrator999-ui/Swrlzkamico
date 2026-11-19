"""§E v11.521 — permanent Labs/Projects/Display rail, contextual lab tools,
Transform grouping and per-document append-only, lab-scoped edit history.
Append-only source patch. Never reset user project revision lineage.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_521_LABS_PROJECT_JOURNAL'
def one(s,old,new,label):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.521',label,n,old[:120]))
 return s.replace(old,new,1)
def section(s,start,end,fn):
 a=s.index(start);b=s.index(end,a)
 return s[:a]+fn(s[a:b])+s[b:]
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_520_QUEST_SCULPT_TRIGGER_MENUS' in html
 j=(ROOT/'runtime/model_edit_journal_v11_521.js').read_text('utf8')
 vr=(ROOT/'runtime/model_vr_labs_v11_521.js').read_text('utf8')
 assert 'SE521_PERSISTENT_EDIT_JOURNAL_END' in j and 'SE521_MODEL_VR_LABS_END' in vr
 # This lives inside the existing ModelAtelier closure, where the authored
 # project document, native checkpoint and rendering functions are visible.
 html=one(html,'/* SE340_MODEL_VR_BRIDGE_END */',
   '/* SE340_MODEL_VR_BRIDGE_END */\n'+j,'native project-scoped journal')
 html=one(html,'installPerformanceSettings();se189InstallPerfUI();',
   vr+'\ninstallPerformanceSettings();se189InstallPerfUI();','single native XR lab action router')
 # Retire only the temporary 50-entry model undo/redo stack. Old projects
 # retain their authored data; new edits begin a durable document journal.
 html=one(html,
  'function checkpoint(){if(!model())return;undo.push(modelSnapshot());if(undo.length>50)undo.shift();redo=[];}',
  'function checkpoint(){se521Journal.before();}',
  'native authoring checkpoint')
 import re
 a=html.index('function historyStep(backward){')
 match=re.search(r'function historyStep\(backward\)\{[\s\S]{0,1500}?\n   \}',html[a:])
 assert match, 'Could not safely isolate legacy model history function'
 b=a+match.end()
 html=html[:a]+"""function historyStep(backward){
    const result=se521Journal.step(backward);
    status(result.changed?(backward?'Undid':'Redid')+' '+result.lab+' edit.':
     result.error||result.reason||'No eligible history action.');
    return result;
   }
   """+html[b:]
 html=one(html,'function signalEdited(){',
   "function signalEdited(){\n    se521Journal.touched();",
   'record committed authored changes before autosaving')
 html=one(html,"$m('Undo').disabled=!undo.length;$m('Redo').disabled=!redo.length;",
   "const steps=se521Journal.depths();$m('Undo').disabled=!steps.canUndo;$m('Redo').disabled=!steps.canRedo;",
   'native model buttons use journal depth')
 html=one(html,"function syncProject(){\n     const button=",
   "function syncProject(){\n     se521Journal.bind();\n     const button=",
   'bind saved document history on project changes')
 # The native XR bridge previously gated Undo against the obsolete temporary
 # stack. Its own wrapper must use the same immutable project journal.
 def bridge(s):
  s=one(s,
   "if (!(backward ? undo : redo).length) return {ok: true, changed: false};\n     historyStep(backward); identity(); hideNativeHelpers(); lastError = '';",
   "const result=se521Journal.step(backward);\n     if(!result.changed)return result;\n     identity(); hideNativeHelpers(); lastError = '';",
   'immersive history backed by native project journal')
  s=one(s,
   "selectedId: selection, canUndo: undo.length > 0, canRedo: redo.length > 0,\n         undoDepth: undo.length, redoDepth: redo.length,",
   "selectedId: selection, ...se521Journal.depths(),",
   'native XR button enabled state follows current lab')
  return s
 html=section(html,'/* SE340_MODEL_VR_BRIDGE_START','/* SE340_MODEL_VR_BRIDGE_END',bridge)
 # Lab-specific authoring including rig poses/keyframes produces the same
 # persistent journal without treating animation playback as an authored edit.
 html=one(html,
   "function se220RigTouched(message){\n  const m=model();if(m)m.editedAt='local';",
   "function se220RigTouched(message){\n  se521Journal.touched('',message);\n  const m=model();if(m)m.editedAt='local';",
   'rig and animation touch notifications persist authoring deltas')
 def stage(s):
  s=one(s,'  const presets={',
   """  const presets={
   labs:[['lab-model','Modeling Lab'],['lab-rig','Rigging Lab'],
    ['lab-animate','Animation Lab'],['lab-texture','Texture & Materials Lab']],
   'transform-menu':[['move','Move'],['rotate','Rotate'],['scale','Scale'],
    ['grab','Grab (freehand)'],['precision','Precision'],['snap','Snap'],
    ['delete-selected','Delete selected']],
""",'lab and transform submenu categories')
  a=s.index('  const entries=[')
  b=s.index('  function row(',a)
  s=s[:a]+"""  const labMenus={
   model:[['inspect','Select','selector'],['transform-menu','Transform','mesh'],
    ['sculpt','Sculpt','sculpt'],['create-menu','Create','create'],
    ['draw','Draw','draw'],['objects','Objects','objects'],
    ['manual-mesh','Face Tools','manual-mesh']],
   rig:[['rig','Bones','rig'],['rig-weights','Weight Paint','rig-weights'],
    ['objects','Objects','objects'],['rig-prev','Previous Bone',null],
    ['rig-next','Next Bone',null]],
   animate:[['animation-play','Play / Stop',null],['animation-key','Key Pose',null],
    ['animation-prev','Previous Key',null],['animation-next','Next Key',null],
    ['animation-time-minus','Time −',null],['animation-time-plus','Time +',null],
    ['animation-loop','Loop On / Off',null]],
   texture:[['texture-uv','UV Mapping','views'],['texture-material','Materials','views'],
    ['texture-paint','Texture Paint','views'],
    ['texture-placement','Texture Placement','views'],
    ['objects','Objects','objects'],['display-textured','Textured',null],
    ['display-wireframe','Wireframe',null]]
  };
  const entries=[
   ['labs','Labs','labs'],['projects','Projects','projects'],['views','Display','views'],
   ...labMenus.model
  ];
  let activeLab='';
""" +s[b:]
  s=one(s,
   "const item=row(rail,action,label,.302-i*.047,.174,'primary');",
   "const item=row(rail,action,label,i<3?.302-i*.047:.124-(i-3)*.047,.174,'primary');",
   'space top three and central modeling tools')
  s=one(s,
   "const quick=[['undo','Undo'],['redo','Redo'],['save-local','Save']];",
   "const quick=[['undo','Undo'],['redo','Redo']];",
   'only lab-scoped undo/redo pinned to bottom')
  s=one(s,
   "const item=paintMesh(rail,'Quick '+label,.055,.052,(i-1)*.058,-.356,()=>{},.053);",
   "const item=paintMesh(rail,'Quick '+label,.084,.054,(i-.5)*.090,-.356,()=>{},.053);",
   'wider two-button bottom row')
  s=one(s,"  const subHead=paintMesh(submenu,",
   """  paintMesh(rail,'Navigation divider',.174,.002,0,.165,(c,w,h)=>{
   c.fillStyle='#759b9a';c.fillRect(0,0,w,h);
  },.050).paint();
  paintMesh(rail,'History divider',.174,.002,0,-.246,(c,w,h)=>{
   c.fillStyle='#759b9a';c.fillRect(0,0,w,h);
  },.050).paint();
  const subHead=paintMesh(submenu,""",
   'visual navigation and history separators')
  s=one(s,'for(let i=0;i<11;i++){','for(let i=0;i<12;i++){',
   'full 12-slot rig weight operation visibility')
  s=one(s,'  function setCategory(action){',
   """  function renderLab(next){
   if(!Object.hasOwn(labMenus,next)||next===activeLab)return;
   activeLab=next;category=null;submenuOpen=false;detailsOpen=false;
   const rows=labMenus[next];
   for(let i=3;i<primaryRows.length;i++){
    const item=primaryRows[i],entry=rows[i-3];
    item.action=entry?.[0]||'';item.label=entry?.[1]||'';item.page=entry?.[2]??null;
    item.active=false;item.mesh.userData.se340Action=item.action||null;
    item.mesh.visible=!!entry;item.paint();
   }
  }
  function setCategory(action){""",
   'change only middle tools while preserving navigation and history')
  s=one(s,'  function choosePage(action){',
   """  function choosePage(action){
   if(action==='transform-menu')return 'mesh';
   if(action==='labs'||action.startsWith('lab-'))return 'tools';
   if(action.startsWith('animation-'))return 'rig';
   if(action.startsWith('texture-'))return 'views';""",
   'map new workspace operations to native controls')
  s=one(s,
   "  function update(next){\n   lastState=next||{};",
   "  function update(next){\n   renderLab(se340XR.se521Lab||model()?.editorWorkspace?.vrLab||'model');\n   lastState=next||{};",
   'refresh lab tool rail after project/lab changes')
  s=one(s,'   if(secondary){chooseOperation(secondary);return true;}',
   """   if(secondary){
    if(secondary.action.startsWith('lab-')){
     renderLab(secondary.action.slice(4));return true;
    }
    chooseOperation(secondary);return true;
   }""",
   'lab selection changes primary rail without extra panel')
  s=one(s,'  sync();\n  return Object.freeze({...ui,update,hitTest,press,hover,tick,openWheel,dispose,',
   """  renderLab(se340XR.se521Lab||model()?.editorWorkspace?.vrLab||'model');
  sync();
  return Object.freeze({...ui,update,hitTest,press,hover,tick,openWheel,dispose,""",
   'initial world-space lab rail state')
  s=one(s,"inspect:()=>({...oldInspect(),dock:'vertical',menuHierarchy:'primary > operation > modifiers',",
   "inspect:()=>({...oldInspect(),dock:'vertical',activeLab,menuHierarchy:'primary > operation > modifiers',",
   'native menu inspect exposes current lab')
  return s
 html=section(html,'/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END',stage)
 # Project loading in the same WebXR session restores the newly loaded
 # project's lab; it must not carry the previous project's history or tools.
 html=one(html,
   "se340XR.mode='inspect';se340XR.page='projects';",
   "se340XR.mode='inspect';se340XR.page='projects';\n   se340XR.se521Lab=model()?.editorWorkspace?.vrLab||'model';",
   'reset active XR lab to the loaded project')
 for old,new in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_520_QUEST_SCULPT_TRIGGER_MENUS',MARKER),
  ('ENGINE · MAKER v11.520','ENGINE · MAKER v11.521'),
  ('v11.520 · textured sculpt, real 2D mesh picking, trigger-held moves and facing menus',
   'v11.521 · native labs, clean VR tool rail and persistent project edit journal'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.520'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.521'"),
  ('<title>§wyrl§ Engine · Maker v11.520</title>',
   '<title>§wyrl§ Engine · Maker v11.521</title>'),
 ]:html=one(html,old,new,'runtime version/marker')
 old=" source.engine='§wyrl§ Engine · Maker v11.520';source.version=11.520;"
 assert html.count(old)==5,('v11.521 source provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.521';source.version=11.521;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.520']
 notes['history'].insert(0,{'version':'v11.520','changes':notes.get('changes',[])})
 notes.update(version='v11.521',date='2026-11-19',
  title='Labs within Model Studio and append-only, project-scoped edit history',
  changes=[
   'Immersive Model Studio menu: fixed Labs / Projects / Display at top, seven contextual Modeling tool categories in the middle, and only Undo / Redo at the bottom; user Grip placement and original three-column native ray menu remain.',
   'Transform groups Move, Rotate, Scale, freehand Grab, Precision, Snap and guarded Delete. Trigger interacts with native gizmos and selected model; Grip manipulates the current selection. Save remains in the Projects tools, not on the permanent rail.',
   'Labs switch the middle menu between Modeling, Rigging, Animation and Texture & Materials. Rigging/Animation reuse real existing skeleton, weight and timeline functions; Texture & Materials provides navigation scaffolding while advanced immersive UV/paint controls are planned for subsequent submenu passes.',
   'Each saved project model carries its own append-only editJournal with incremental reversible edits, explicit undo/redo log events and lab scopes. Switching projects reloads its history rather than reusing the last project temporary Undo stack; successive Undo/Redo act on successive eligible edits, not on their own journal records.',
   'Authoring changes in different labs are checked for dependencies before reversing. Incompatible cross-lab changes fail safely instead of overwriting later authored geometry. Existing projects retain old saves and start an independent journal from this release; no historical actions are fabricated.',
   'No duplicate XR scene, event dispatcher, independent workbench or Vercel host was added. Native face tools, UV materials, rig/animation assets, saves and earlier Quest fixes remain intact. Physical Quest acceptance is pending.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\\/')+html[at+n:]
