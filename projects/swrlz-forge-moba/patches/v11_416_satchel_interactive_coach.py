"""§E v11.416 · interactive Apprentice Satchel academy.

Append-only integration of read-only native-button highlights, non-editable
native mesh ghosts, geometry inspection, reversible local checkpoints, lesson
progress in ordinary account-save documents, and headset material + panel
controls. No second renderer, backend, head-follow UI, or starter mutation.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_416_SATCHEL_INTERACTIVE_COACH'

def one(src,old,new):
    n=src.count(old)
    if n!=1:raise AssertionError(('v11.416 source anchor',old[:110],n))
    return src.replace(old,new,1)

def apply(html):
    bridge=(ROOT/'runtime/model_satchel_native_bridge_v11_416.js').read_text('utf8')
    academy=(ROOT/'runtime/model_satchel_academy_v11_416.js').read_text('utf8')
    vr=(ROOT/'runtime/model_satchel_vr_coach_v11_416.js').read_text('utf8')
    css=(ROOT/'runtime/model_satchel_academy_v11_416.css').read_text('utf8')
    assert 'SE414_SATCHEL_NATIVE_TOOL_REFERENCES_START' in html
    # Native geometry editing internals are private to ModelAtelier. Only the
    # validated bridge can invoke checkpoint/signalEdited/modelRoot.
    html=one(html,'/* ATELIER_BRIDGE_END */',bridge+'\n/* ATELIER_BRIDGE_END */')
    # Seven-step legacy quest keeps its identity and progress keys.
    old="function getDone(){try{const a=JSON.parse(recall(key())||'[]');return Array.isArray(a)?new Set(a.filter(n=>Number.isInteger(n)&&n>=0&&n<steps.length)):new Set();}catch(_){return new Set();}}"
    new="""function getDone(){try{
  const local=JSON.parse(recall(key())||'[]'),localTime=Number(recall(key()+':updatedAt'))||0;
  const remote=currentProject?.se415TutorialState;
  const data=remote?.schema==='se416-quest-progress-v1'&&remote.lesson===LESSON&&Number(remote.updatedAt)>=localTime?remote.done:local;
  return Array.isArray(data)?new Set(data.filter(n=>Number.isInteger(n)&&n>=0&&n<steps.length)):new Set();
 }catch(_){return new Set();}}"""
    html=one(html,old,new)
    html=one(html,"function storeDone(done){remember(key(),JSON.stringify([...done].sort((a,b)=>a-b)));}",
      "function storeDone(done){const values=[...done].sort((a,b)=>a-b);remember(key(),JSON.stringify(values));window.SWYRL_E_SATCHEL_ACADEMY_416?.progressUpdate(values);}")
    html=one(html,' function assess(step){',
      ' function assess(step){\n  const result=window.SWYRL_E_SATCHEL_ACADEMY_416?.verify(steps.indexOf(step));if(result)return result;')
    html=one(html,
      "  window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414?.renderFlat(panel,current,step);",
      "  window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414?.renderFlat(panel,current,step);\n  window.SWYRL_E_SATCHEL_ACADEMY_416?.renderFlat(panel,current,step);")
    html=one(html," start:newLesson,resume,\n steps:",
      """ start:newLesson,resume,
 applyProgress:indices=>{
  if(!belongs()||!Array.isArray(indices))return false;
  storeDone(new Set(indices.filter(n=>Number.isInteger(n)&&n>=0&&n<steps.length)));
  display();return true;
 },
 steps:""")
    html=one(html,
      "  currentProject.se412Tutorial=data?.project?.se412Tutorial===LESSON?LESSON:null;",
      "  currentProject.se412Tutorial=data?.project?.se412Tutorial===LESSON?LESSON:null;\n  currentProject.se415TutorialState=belongs()&&data?.project?.se415TutorialState?.schema==='se416-quest-progress-v1'?structuredClone(data.project.se415TutorialState):null;")
    # Native VR card highlights work through the existing icon/canvas painter,
    # not a second copied palette.
    html=one(html,
      "  if(!item.id)return;const disabled=!enabled(item.id),on=active(item),over=hoveredItem===item,down=pressedItem===item;",
      "  if(!item.id)return;const disabled=!enabled(item.id),on=active(item),over=hoveredItem===item,down=pressedItem===item,tutorialOn=state.tutorialHighlight===item.id;")
    html=one(html,
      "key=JSON.stringify([item.id,text,sub,disabled,on,over,down,!!wheelKind,",
      "key=JSON.stringify([item.id,text,sub,disabled,on,over,down,tutorialOn,!!wheelKind,")
    html=one(html,
      "edge=disabled?'#485168':down?'#b5fff0':over?'#a7f6df':on?'#eed5a0':",
      "edge=disabled?'#485168':down?'#b5fff0':tutorialOn?'#e7ff74':over?'#a7f6df':on?'#eed5a0':")
    html=one(html,'c.lineWidth=down||over||on?3.5:2;c.stroke();',
             'c.lineWidth=down||over||on||tutorialOn?4.4:2;c.stroke();')
    html=one(html,
      "return Object.freeze({root,targets,drawGuideIcon:(ctx,action,x,y,size,color)=>icon(ctx,iconType(action),x,y,size,color),",
      "return Object.freeze({root,targets,drawGuideIcon:(ctx,action,x,y,size,color)=>icon(ctx,iconType(action),x,y,size,color),highlightTutorialAction:action=>update({tutorialHighlight:action}),")
    html=one(html,
      ' function iconType(id){\n',
      " function iconType(id){\n   if(id==='se416-leather')return 'leather';if(id==='se416-metal')return 'detail';if(id==='se416-shade-plus')return 'star';if(id==='se416-shade-minus')return 'leather';\n")
    # The flat editor retains real Material/Color fields; VR reference chips
    # point instead to the headset-specific quest material row.
    html=one(html,
      '  const refs=references(step.index);',
      """  const refs=step.index===5?[
   {vr:'se416-leather',vrName:'Leather'},
   {vr:'se416-metal',vrName:'Metal'},
   {vr:'se416-shade-plus',vrName:'Shade'}
  ]:references(step.index);""")
    # Reuse the original quest's scene, controller rays, frame loop, disposal.
    html=one(html,
      "const signature=JSON.stringify([box.folded,index,rows.map(r=>r.done),box.message,st.projectId]);",
      "const signature=JSON.stringify([box.folded,index,rows.map(r=>r.done),box.message,st.projectId,box.coachMode,box.confirmRestore,window.SWYRL_E_SATCHEL_ACADEMY_416?.ghost?.()]);")
    html=one(html,
      "  for(const btn of box.buttons)btn.visible=!box.folded||btn.userData.se340Action==='se413-fold';",
      """  for(const btn of box.buttons){
   const mode=btn.userData.se415Coach;
   btn.visible=box.folded?btn.userData.se340Action==='se413-fold':
    mode?mode==='mode'?index===5:mode===(box.coachMode==='material'&&index===5?'material':'guide'):true;
  }""")
    html=one(html,
      "   c.fillStyle='#a8e8c3';c.font='bold 24px system-ui';\n   wrap(c,truncate(box.message,180),32,626,944,28,2);",
      "   c.fillStyle='#a8e8c3';c.font='bold 19px system-ui';\n   wrap(c,truncate(box.message,100),32,218,944,24,1);")
    html=one(html,
      "  const buttons=[['se413-prev','PREV',34,657,185],",
      "  window.SWYRL_E_SATCHEL_VR_COACH_416?.draw(c,box,index);\n  const buttons=[['se413-prev','PREV',34,657,185],")
    html=one(html,
      "  makeButton(box,'se413-next',765,657,224,85);",
      "  makeButton(box,'se413-next',765,657,224,85);\n  window.SWYRL_E_SATCHEL_VR_COACH_416?.install(box,makeButton);")
    html=one(html,
      "   api.choose(box.index);box.message='';",
      "   api.choose(box.index);box.message='';box.coachMode='guide';box.confirmRestore=false;window.SWYRL_E_SATCHEL_ACADEMY_416?.clearHighlight?.();")
    html=one(html,
      "  if(found?.quest){record.hit=found;activate(found.action,record);return;}",
      "  if(found?.quest){record.hit=found;if(!activate(found.action,record))window.SWYRL_E_SATCHEL_VR_COACH_416?.action(found.action,record);return;}")
    html=one(html,
      "  if(String(action).startsWith('se413-'))return activate(action,record);",
      "  if(String(action).startsWith('se413-'))return activate(action,record);\n  if(String(action).startsWith('se416-'))return window.SWYRL_E_SATCHEL_VR_COACH_416?.action(action,record)||false;")
    # Execute both modules alongside the existing host-level tutorial (after
    # the native bridge was installed inside the ModelAtelier closure).
    html=one(html,'if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(',
      academy+'\n'+vr+'\nif(ALLOWED_PARENTS.has(location.origin))queueMicrotask(')
    assert html.index('</head>')<html.index('<body')
    html=html.replace('</head>','<style id="se415SatchelAcademy">'+css+'</style>\n</head>',1)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_415_MODEL_VR_ICONOGRAPHY',MARKER),
      ('ENGINE · MAKER v11.415','ENGINE · MAKER v11.416'),
      ('v11.415 · clearer Model VR icons','v11.416 · interactive satchel modeling coach'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.415'","window.SWRLZ_FORGE_BUILD={version:'v11.416'"),
      ('<title>§wyrl§ Engine · Maker v11.415</title>','<title>§wyrl§ Engine · Maker v11.416</title>')
    ]:html=one(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.415';source.version=11.415;"
    if html.count(old)!=5:raise AssertionError(('v11.416 provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.416';source.version=11.415;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,{'version':'v11.415','changes':notes.get('changes',[])})
    notes.update(version='v11.416',date='2026-11-11',title='Interactive Apprentice Satchel Academy',changes=[
      'Show Me points to the actual flat editor button or persists a highlighted action on the existing native VR console; it never creates duplicate tool controls.',
      'A toggleable wireframe ghost demonstrates target dimensions for the body, floor + four walls, flap, strap arch and clasp as scene-owned, non-raycastable, non-editable geometry.',
      'Structure verification inspects real editable boxes for a thin base, left/right/front/back walls, flap, multiple strap segments, details and leather/metal materials, with manual review for complex topology or final saving.',
      'Users can store up to seven bounded checkpoints of validated native model parts per independent tutorial project and confirm a safe one-step native-Undo restoration. Checkpoint geometry remains device-local.',
      'Quest completion state is preserved in native project/account-save data, so a deliberate Save to Account carries checkoffs to a second device; no new account backend or automatic upload is introduced.',
      'VR quest has a contextual coach action row, a Material/Color tool row with native Undo and selected-part validation, and deliberate grip-drag to reposition the independent world-space window without parenting it to the camera.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
