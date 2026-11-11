"""§E v11.413 — repair beginner tutorial + a stationary WebXR quest window.

Append-only source patch. v11.412 source stays untouched; no source starter
or unrelated chat, Sheep Tag, VR controller profile, or account component edits.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_413_SATCHEL_VR_TUTORIAL'

def one(source,old,new):
    n=source.count(old)
    if n!=1: raise AssertionError(('v11.413 source anchor',old[:105],n))
    return source.replace(old,new,1)

def improved_tutorial(js):
    rows=[
     ("title:'Shape a hollow opening',tool:'Topology · Face / Extrude'",
      "title:'Build real open-top walls',tool:'Meshes · Add box / Transform'"),
     ("task:'Turn the solid body into an open-top pouch. Select the top face, inset its boundary, then extrude the inner face downward; inspect inside from above.'",
      "task:'Resize the practice cube into a thin bottom slab. Add four separate thin box meshes for the front, back, left and right walls. Align their edges, but leave the top truly open.'"),
     ("why:'An inset creates an inner border. A downward extrusion makes an interior. A dark top surface alone is not a cavity.'",
      "why:'Four real walls around a thin floor create an actual empty volume. The current native Face Extrude works on selected triangle faces, not one-click insets of an entire solid cube.'"),
     ("hint:'Use the actual topology/face editing controls. If the chosen mesh cannot be inset yet, convert it to editable topology first. Do not mark this complete until you can see interior walls.'",
      "hint:'Select Practice cube and lower its Y height for the floor. Use Add Box four times; make each wall thin, place it around the floor and leave its top uncovered. Orbit above and look through the opening.'"),
     ("title:'Connect a shoulder strap',tool:'Meshes · Extrude / Transform'",
      "title:'Build a connected shoulder strap',tool:'Meshes · Add box / Move / Rotate'"),
     ("task:'Build a long thin strap from one side of the satchel, arc it over the shoulder path, and bring it back to the opposite side.'",
      "task:'Add narrow box strips, rotate successive segments into a gentle arch, and make their ends meet the two side walls. Keep the strap pieces as editable geometry.'"),
     ("hint:'Start with a narrow strip or several connected sections. Check front, side and back views so both ends meet the satchel.'",
      "hint:'Duplicate or add a thin box, rotate each new section slightly, then use Move to join their ends. Check front, side and back before marking complete.'"),
     ("function lessonNotice(message){const n=$('#se412Note');if(n)n.textContent=message;}",
      "function lessonNotice(message){for(const n of [$('#se412Note'),$('#se412LibraryNotice')])if(n)n.textContent=message;}"),
    ]
    for old,new in rows:js=one(js,old,new)
    diagrams=r""" function se413PaintDemo(panel,index){
  let host=$('#se413Examples',panel);
  if(!host){host=document.createElement('details');host.id='se413Examples';
   host.innerHTML='<summary>Visual examples · front / side / top</summary><div id="se413Views"></div><p>Concept diagrams only. Build and inspect actual editable parts in the viewport.</p>';
   $('#se412Note',panel).before(host);
  }
  const view=(label,kind)=>{
   const walls=index>0,flap=index>1,strap=index>2,buckle=index>3,paint=index>4;
   const base=kind==='top'
     ?(walls?'<path d="M20 16H104V69H20Z M36 29H88V56H36Z" fill-rule="evenodd" />':'<rect x="20" y="16" width="84" height="53" rx="4"/>')
     :walls?'<path d="M23 21V69H101V21M23 69H101" fill="none"/>':'<rect x="23" y="21" width="78" height="48" rx="3"/>';
   const lip=flap?(kind==='top'?'<path d="M23 16H101V35H23Z"/>':'<path d="M22 21H103V39H22Z"/>'):'';
   const arch=strap?(kind==='side'?'<path d="M25 49Q60 -9 100 49" stroke="#eabf82" stroke-width="7" fill="none"/>':'<path d="M27 48Q11 -4 99 19" stroke="#eabf82" stroke-width="6" fill="none"/>'):'';
   const clasp=buckle?'<rect x="57" y="32" width="15" height="13" fill="#e6c172" stroke="#4f314d"/>':'';
   return '<div><small>'+label+'</small><svg viewBox="0 0 124 87" aria-label="'+label+' silhouette diagram" role="img"><g stroke="'+(paint?'#6b3e29':'#a6dcf0')+'" stroke-width="3" fill="'+(paint?'#8e5d43':'#55456e')+'">'+base+lip+'</g>'+arch+clasp+'</svg></div>';
  };
  $('#se413Views',host).innerHTML=view('Front','front')+view('Side','side')+view('Top','top');
 }
"""
    js=one(js,' function display(){',diagrams+' function display(){')
    js=one(js,"  $('#se412Hint',panel).open=false;","  $('#se412Hint',panel).open=false;\n  se413PaintDemo(panel,current);")
    old="   bar.children[0].id='se412Prev';bar.children[2].id='se412Mark';bar.children[3].id='se412Next';"
    new=old+"""
   const toolLink=button('Open relevant native tools',()=>{
    const group=steps[current].tool.split(' · ')[0];
    const category=group==='Views'?'References':group;
    if(window.SWYRL_E_UNIFIED_TOOLS?.select){
     window.SWYRL_E_UNIFIED_TOOLS.select(category);
     lessonNotice('Opened '+category+' tools. Choose the indicated operation above; the three-view diagrams are examples, not generated geometry.');
    }else lessonNotice('Open the '+category+' category in the existing Model Studio tool rail.');
   },'se413-tool-link');
   bar.after(toolLink);"""
    js=one(js,old,new)
    old="window.SWYRL_ENGINE_TUTORIAL_412=Object.freeze({start:newLesson,resume,steps:()=>steps.map((s,i)=>({index:i,title:s.title,done:getDone().has(i)})),status:()=>({active:belongs(),projectId:belongs()?projectId():null,progress:belongs()?getDone().size:0})});"
    new="""window.SWYRL_ENGINE_TUTORIAL_412=Object.freeze({
 start:newLesson,resume,
 steps:()=>steps.map((s,i)=>({index:i,title:s.title,tool:s.tool,task:s.task,hint:s.hint,why:s.why,automatic:!!s.check,done:belongs()&&getDone().has(i)})),
 status:()=>({active:belongs(),projectId:belongs()?projectId():null,progress:belongs()?getDone().size:0,current}),
 choose:index=>{if(!belongs()||!Number.isInteger(index)||index<0||index>=steps.length)return false;current=index;display();return true;},
 mark:index=>{
  if(!belongs()||!Number.isInteger(index)||index<0||index>=steps.length)return {ok:false,message:'Open your saved satchel tutorial first.'};
  current=index;const done=getDone(),was=done.has(index);if(was)done.delete(index);else done.add(index);
  storeDone(done);display();
  return {ok:true,done:!was,message:was?'Objective reopened.':'Objective checked off. Progress saved on this device.'};
 },
 check:index=>{
  if(!belongs()||!Number.isInteger(index)||index<0||index>=steps.length)return {ok:false,message:'Open your saved satchel tutorial first.'};
  current=index;const result=assess(steps[index]);
  if(result.ok===true){const done=getDone();done.add(index);storeDone(done);}
  display();lessonNotice(result.message);return result;
 }
});"""
    js=one(js,old,new)
    return js

def apply(html):
    old=(ROOT/'runtime/model_satchel_tutorial_v11_412.js').read_text('utf8')
    vr=(ROOT/'runtime/model_satchel_vr_quest_v11_413.js').read_text('utf8')
    css=(ROOT/'runtime/model_satchel_tutorial_v11_413.css').read_text('utf8')
    assert 'SE410_MODEL_VR_ACCESSORY_WORKSHOP_START' in html
    html=one(html,old,improved_tutorial(old)+'\n'+vr)
    assert html.index('</head>')<html.index('<body')
    html=html.replace('</head>','<style id="se413LessonExamples">'+css+'</style>\n</head>',1)
    for old,new in [
     ('SWYRL_ENGINE_DEPLOY_MARKER: V11_412_APPRENTICE_SATCHEL_TUTORIAL',MARKER),
     ('ENGINE · MAKER v11.412','ENGINE · MAKER v11.413'),
     ('v11.412 · apprentice satchel guided modeling tutorial','v11.413 · satchel modeling plus VR quest'),
     ("window.SWRLZ_FORGE_BUILD={version:'v11.412'","window.SWRLZ_FORGE_BUILD={version:'v11.413'"),
     ('<title>§wyrl§ Engine · Maker v11.412</title>','<title>§wyrl§ Engine · Maker v11.413</title>')
    ]:html=one(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.412';source.version=11.412;"
    if html.count(old)!=5:raise AssertionError(('v11.413 source provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.413';source.version=11.413;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,{'version':'v11.412','changes':notes.get('changes',[])})
    notes.update(version='v11.413',date='2026-11-11',title='Apprentice Satchel in native Model VR',changes=[
      'Tutorial step 2 now builds a real hollow open-top bag from a floor and four wall meshes, rather than claiming a face-inset tool unavailable for solid boxes.',
      'A compact collapsible three-view illustration and Open native tools action clarify construction; these do not change the user model.',
      'Immersive Model VR adds a separate stationary world-space satchel quest window, controller-ray navigation, verification, checkoffs and progress shared with flat Model Studio.',
      'The VR panel is scene-owned, disposed at session end, repositioned only on explicit recenter and does not parent to the head, viewport orbit or model.',
      'Existing starter/project cloning, native save, history, controllers, VR pouch workshop and Sheep Tag remain owned by their original systems.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
