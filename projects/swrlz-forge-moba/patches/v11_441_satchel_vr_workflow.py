"""§E v11.441 feature integration: a genuinely followable native VR satchel.

Includes the runtime release identity; the sealer owns manifest integrity.
It changes no source starter or save backend.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_441_SATCHEL_VR_WORKFLOW'

def one(source,old,new):
    count=source.count(old)
    if count!=1:raise AssertionError(('v11.441 source anchor',old[:110],count))
    return source.replace(old,new,1)

def section(source,start,end,edit):
    assert source.count(start)==source.count(end)==1,('v11.441 section',start)
    a=source.index(start);b=source.index(end,a)+len(end)
    return source[:a]+edit(source[a:b])+source[b:]

def function(source,name,replacement):
    # Known native source functions contain no unmatched braces in literals.
    start=' function '+name+'('
    assert source.count(start)==1,('v11.441 function',name)
    a=source.index(start);op=source.index('{',a);depth=1;i=op+1
    while depth:
        assert i<len(source),('v11.441 unclosed function',name)
        if source[i]=='{':depth+=1
        elif source[i]=='}':depth-=1
        i+=1
    return source[:a]+replacement+source[i:]

def tutorial(js):
    a=js.index(' const steps=[');b=js.index('\n ];',a)+len('\n ];')
    js=js[:a]+' const steps=window.SWYRL_E_SATCHEL_LESSON_441.steps;'+js[b:]
    js=one(js,"position:[0,1.5,0],rotation:[0,0,0],scale:[.65,.6,.45],color:'#987153'",
       "position:[0,1.5,0],rotation:[0,0,0],scale:[1.4,1,.65],color:'#987153'")
    js=one(js,"name:'Practice cube · shape into body'","name:'Satchel body · practice cube'")
    js=one(js,"   currentProject.se412Tutorial=LESSON;\n   lessonProject=projectId();",
       "   currentProject.se412Tutorial=LESSON;\n   currentProject.se441TutorialWorkflow='one-body-v1';\n   lessonProject=projectId();")
    js=one(js,'task:s.task,hint:s.hint,why:s.why,automatic:',
       'task:s.task,hint:s.hint,why:s.why,vrTask:s.vrTask,vrHint:s.vrHint,vrTool:s.vrTool,automatic:')
    js=one(js,'if(belongs()&&row?.data?.project)row.data.project.se412Tutorial=LESSON;',
       "if(belongs()&&row?.data?.project){row.data.project.se412Tutorial=LESSON;if(currentProject.se441TutorialWorkflow==='one-body-v1')row.data.project.se441TutorialWorkflow='one-body-v1';}")
    js=one(js,'if(belongs()&&data?.project)data.project.se412Tutorial=LESSON;',
       "if(belongs()&&data?.project){data.project.se412Tutorial=LESSON;if(currentProject.se441TutorialWorkflow==='one-body-v1')data.project.se441TutorialWorkflow='one-body-v1';}")
    js=one(js,"  currentProject.se412Tutorial=data?.project?.se412Tutorial===LESSON?LESSON:null;",
       "  currentProject.se412Tutorial=data?.project?.se412Tutorial===LESSON?LESSON:null;\n  currentProject.se441TutorialWorkflow=belongs()&&data?.project?.se441TutorialWorkflow==='one-body-v1'?'one-body-v1':null;")
    return js

def academy(js):
    js=function(js,'inspect',""" function inspect(index){
  if(!modelReady()||!Number.isInteger(index)||index<0||index>6)return {ok:false,message:'Open your independent Apprentice Satchel project first.'};
  return window.SWYRL_E_SATCHEL_LESSON_441.verify(index,parts());
 }""")
    js=one(js,'  clearHighlight();\n  const refs=window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414?.references(index)||[];',
       """  clearHighlight();
  const guided=window.SWYRL_E_SATCHEL_LESSON_441?.showMe(index,vr);
  if(guided){
   const {element,...response}=guided;
   if(element)highlight={index,element,key:guided.key};
   else if(guided.action)highlight={vr:true,index,action:guided.action};
   return response;
  }
  const refs=window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414?.references(index)||[];""")
    js=function(js,'refreshGhost',""" function refreshGhost(){
  disposeGhost();
  const modelRoot=window.SWYRL_E_SATCHEL_NATIVE_416?.root?.(); // SE441_NATIVE_GHOST_ROOT
  if(!ghostEnabled||!modelReady()||!modelRoot||typeof THREE==='undefined'||!modelRoot.isObject3D)return;
  const index=current()?.current||0,group=new THREE.Group();
  group.name='Satchel lesson reference · not editable';group.userData.editorOnly=true;
  window.SWYRL_E_SATCHEL_LESSON_441.makeGhost(group,index);
  ghost=group;ghostFor=index;modelRoot.add(group);
 }""")
    return js

def references(js):
    js=one(js,"  scale:{name:'Scale'",
       """  draw:{name:'Draw outline',flat:'#modelAtelierPanel [data-vr-only-draw]',vr:'draw',vrName:'Draw outline'},
  thicken:{name:'Thicken outline',flat:'#modelAtelierPanel [data-vr-only-thicken]',vr:'extrude',vrName:'Thicken outline'},
  grab:{name:'Grab',flat:'#se320ModelTransform [data-se320-transform="move"]',vr:'grab',vrName:'Grab'},
  sphere:{name:'Sphere',flat:'#atelierContextProxy_modelAtelierPrimitiveKind',vr:'create-sphere',vrName:'Sphere'},
  scale:{name:'Scale'""")
    js=one(js,"  ['duplicate','move'],['material','color'],['views','save']",
       "  ['add','shape','move'],['material','color'],['views','save']")
    js=one(js," function references(index){return (byStep[index]||[]).map(key=>({key,...tools[key]}));}",
       """ const vrByStep=[['grab','scale'],['convert','inset','extrude'],['draw','thicken','grab'],['draw','thicken','grab'],['sphere','grab'],['material','color'],['views','save']];
 function references(index,vr=false){return ((vr?vrByStep:byStep)[index]||[]).map(key=>({key,...tools[key]}));}""")
    js=one(js,']:references(step.index);',']:references(step.index,true);')
    return js

def apply(html):
    assert 'SE440_NATIVE_OUTLINE_ROUTE' in html and 'SE440_TOUCH_COMPONENT_BORDER' in html
    addon=(ROOT/'runtime/model_satchel_lesson_v11_441.js').read_text('utf8')
    checker=(ROOT/'runtime/model_satchel_workflow_v11_441.js').read_text('utf8')
    html=one(html,'(function se412SatchelTutorial(){',addon+'\n(function se412SatchelTutorial(){')
    html=one(html,'/* SE416_SATCHEL_ACADEMY_START',checker+'\n/* SE416_SATCHEL_ACADEMY_START')
    html=section(html,'(function se412SatchelTutorial(){','/* SE413_SATCHEL_VR_QUEST_START',tutorial)
    html=section(html,'/* SE416_SATCHEL_ACADEMY_START','/* SE416_SATCHEL_ACADEMY_END */',academy)
    html=section(html,'/* SE414_SATCHEL_NATIVE_TOOL_REFERENCES_START','/* SE414_SATCHEL_NATIVE_TOOL_REFERENCES_END */',references)
    html=one(html,"const rows=api.steps(),st=api.status(),index=Math.min(6,Math.max(0,box.index)),step=rows[index];",
       "const rows=api.steps(),st=api.status(),index=Math.min(6,Math.max(0,box.index)),rawStep=rows[index],step=rawStep?{...rawStep,task:rawStep.vrTask||rawStep.task,hint:rawStep.vrHint||rawStep.hint,tool:rawStep.vrTool||rawStep.tool}:null;")
    # Guide and Materials share the same physical row. Three raycasting does
    # not honor Object3D.visible, so hidden controls must never own its input.
    html=one(html,"const targets=box.folded?box.buttons.filter(o=>o.visible):[...box.buttons,box.panel];",
       "const targets=(box.folded?box.buttons:[...box.buttons,box.panel]).filter(o=>o.visible!==false); // SE441_VISIBLE_QUEST_INPUT")
    # The quest is UI even when its world-space plane overlaps the model.
    # Match the hover/trigger menu authority instead of a nearer geometry hit.
    html=one(html,"const box=quest(),hit=box&&se340Hit(record,false);",
       "const box=quest(),hit=box&&se360MenuContact(record); // SE441_QUEST_GRIP_INPUT")
    html=section(html,'/* SE413_SATCHEL_VR_QUEST_START','/* SE413_SATCHEL_VR_QUEST_END */',
       lambda js:one(js,'const found=se340Hit(record,false);',
         'const found=se360MenuContact(record); // SE441_QUEST_TRIGGER_INPUT'))
    html=section(html,'/* SE413_SATCHEL_VR_QUEST_START','/* SE413_SATCHEL_VR_QUEST_END */',
       lambda js:one(js,'box.root.position.copy(viewer.position).addScaledVector(forward,1.13).addScaledVector(right,.56);',
         'box.root.position.copy(viewer.position).addScaledVector(forward,1.25).addScaledVector(right,1.40); // SE441_QUEST_SIDE_PLACEMENT'))
    html=one(html,"s.se430Operation=operation;s.se430Amount=se430VRDefaults[operation];",
       "s.se430Operation=operation;s.se430Amount=window.SWYRL_E_SATCHEL_LESSON_441?.amountFor(operation)??se430VRDefaults[operation];")
    html=one(html,"drawBegin({normal:localNormal.toArray(),name:'VR outline'})",
       "drawBegin({normal:localNormal.toArray(),name:window.SWYRL_E_SATCHEL_LESSON_441?.drawName()||'VR outline'})")
    html=section(html,'/* SE436_SATCHEL_CAVITY_START */','/* SE436_SATCHEL_CAVITY_END */',
       lambda js:one(js,'{depth:-.35}','{depth:-.75}'))
    return release_identity(html)

def release_identity(html):
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_440_MODEL_TOOLS_VALIDATION',MARKER),
      ('ENGINE · MAKER v11.440','ENGINE · MAKER v11.441'),
      ('v11.440 · checked VR and touch modeling tools','v11.441 · one connected satchel from real VR tools'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.440'","window.SWRLZ_FORGE_BUILD={version:'v11.441'"),
      ('<title>§wyrl§ Engine · Maker v11.440</title>','<title>§wyrl§ Engine · Maker v11.441</title>')
    ]:html=one(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.440';source.version=11.440;"
    assert html.count(old)==5,('v11.441 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.441';source.version=11.441;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.440']
    notes['history'].insert(0,{'version':'v11.440','changes':notes.get('changes',[])})
    notes.update(version='v11.441',date='2026-11-13',title='A followable one-body satchel workshop in VR',changes=[
      'Start with one ordinary bag-proportioned cube. Make it editable, Inset the top and Extrude inward to create the connected cavity yourself; no separate floor/wall boxes or generated bag.',
      'Short VR tasks name the real Draw outline, Thicken outline and Grab tools for a separate flap and a U-shaped strap with an empty middle. A simple clasp comes before its metal material.',
      'Show Me opens or highlights the current native tool; the cavity step suggests a visible negative Extrude depth without applying geometry automatically.',
      'Verify inspects actual connected body, thickened flap/strap and fitted clasp geometry; the body itself cannot count as a strap. Materials and saved-project visual review remain distinct.',
      'Hidden tutorial/guide/material controls cannot intercept the active visible row. The quest starts beside the model and stays independently movable with Grip. Quest Trigger and Grip share visible-menu ownership across nearer geometry. Existing local checkpoints, Undo, native saving and supported learner projects remain compatible.',
      'Reference ghosts remain non-editable examples. Sculpted/posed parts and exact seam contact request visual review rather than false automatic approval. Physical Quest comfort remains owner testing.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
