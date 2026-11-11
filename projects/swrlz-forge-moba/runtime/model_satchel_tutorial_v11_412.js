/* §E v11.412: apprentice satchel, an actual independent Model Studio lesson. */
(function se412SatchelTutorial(){
 'use strict';
 const LESSON='satchel-001', TITLE='Tutorial 001 · Apprentice Satchel';
 const LAST='se412:satchel:last';
 const steps=[
  {title:'Block out the pouch body',tool:'Meshes · Scale / Transform',task:'Start with the single practice cube. Scale it wider than it is deep, then make it tall enough to hold supplies.',why:'A blockout establishes the silhouette before adding detail. Use X for width, Y for height and Z for depth.',hint:'Select Practice cube in the mesh list. Change its size with Scale or its X/Y/Z values. Try width at least 1.2, height 0.85, depth 0.35.',check:'body'},
  {title:'Shape a hollow opening',tool:'Topology · Face / Extrude',task:'Turn the solid body into an open-top pouch. Select the top face, inset its boundary, then extrude the inner face downward; inspect inside from above.',why:'An inset creates an inner border. A downward extrusion makes an interior. A dark top surface alone is not a cavity.',hint:'Use the actual topology/face editing controls. If the chosen mesh cannot be inset yet, convert it to editable topology first. Do not mark this complete until you can see interior walls.'},
  {title:'Build the closing flap',tool:'Meshes · Add / Move / Scale',task:'Create a separate thin piece above the opening, extend it toward the front and shape the free end downward.',why:'Keeping the flap separate makes it easier to adjust and later rig or animate.',hint:'Add a new box or a planar shape, make it wide and thin, and name it Flap. Look from the side to check that it covers the opening.'},
  {title:'Connect a shoulder strap',tool:'Meshes · Extrude / Transform',task:'Build a long thin strap from one side of the satchel, arc it over the shoulder path, and bring it back to the opposite side.',why:'This is an actual strip of geometry, not a drawn line floating in front of the pouch.',hint:'Start with a narrow strip or several connected sections. Check front, side and back views so both ends meet the satchel.'},
  {title:'Add buckle and finishing details',tool:'Meshes · Duplicate / Move',task:'Make a small metal clasp and at least one seam, loop or stitched detail. Group related pieces if helpful.',why:'Small details read best after the main volume and strap are proportionally sound.',hint:'Use a narrow metal-colored mesh for the buckle. Zoom in, then inspect its attachment to the flap.'},
  {title:'Apply leather and metal materials',tool:'Appearance · Materials / Color',task:'Give the pouch and flap a leather-like matte finish and the clasp a contrasting metallic material.',why:'Rough leather and reflective metal communicate different materials even with simple geometry.',hint:'Select each part, choose its material and color, then orbit under the light to judge the result.',check:'material'},
  {title:'Inspect and save your creation',tool:'Views · Orbit / Projects · Save Project',task:'Check the model from front, side, back and top; correct obvious gaps, then use Save Project. Export is optional and is not a substitute for saving.',why:'Native Save Project preserves your editable geometry in My Projects without changing the starter.',hint:'Use Projects → Save Project; if signed in, choose Save to Account separately for cross-device access.'}
 ];
 let lessonProject='', folded=false, busy=false, current=0;
 const $=(s,r=document)=>r.querySelector(s);
 function remember(k,v){try{localStorage.setItem(k,v);}catch(_){}}
 function recall(k){try{return localStorage.getItem(k);}catch(_){return null;}}
 function projectId(){return currentProject?.instanceId||'';}
 function belongs(){return currentProject?.se412Tutorial===LESSON&&!!projectId();}
 function key(){return 'se412:satchel:progress:'+projectId();}
 function getDone(){try{const a=JSON.parse(recall(key())||'[]');return Array.isArray(a)?new Set(a.filter(n=>Number.isInteger(n)&&n>=0&&n<steps.length)):new Set();}catch(_){return new Set();}}
 function storeDone(done){remember(key(),JSON.stringify([...done].sort((a,b)=>a-b)));}
 function meshParts(){return currentProject?.kind==='model-atelier'&&Array.isArray(currentProject?.modelAtelier?.parts)?currentProject.modelAtelier.parts:[];}
 function assess(step){
  const parts=meshParts();
  if(step.check==='body'){
   const p=parts.find(x=>x.id==='model-seed')||parts.find(x=>/body|pouch|satchel|practice/i.test(x.name||''));
   if(p?.kind==='box'&&Array.isArray(p.scale)&&p.scale[0]>=1.2&&p.scale[1]>=.85&&p.scale[2]>=.35)
    return {ok:true,message:'Body proportion check passed. Inspect the silhouette before continuing.'};
   return {ok:false,message:'The starting body needs a box shape at least 1.2 wide, 0.85 tall and 0.35 deep. Adjust your actual mesh first.'};
  }
  if(step.check==='material'){
   const leather=parts.some(p=>['matte','silk'].includes(p.material)&&p.color&&p.color.toLowerCase()!=='#ffffff');
   const metal=parts.some(p=>p.material==='metal');
   return {ok:leather&&metal,message:leather&&metal?'Leather-like and metal material assignments detected.':'Assign a matte/silk color to leather pieces AND a metal material to at least one buckle piece.'};
  }
  return {ok:null,message:'This shape needs visual inspection. Compare your real mesh from multiple angles, then mark the step complete yourself.'};
 }
 function button(label,handler,cls=''){const el=document.createElement('button');el.type='button';el.textContent=label;if(cls)el.className=cls;el.addEventListener('click',handler);return el;}
 function lessonNotice(message){const n=$('#se412Note');if(n)n.textContent=message;}
 function display(){
  const panel=$('#se412Panel');if(!panel||!belongs())return;
  const done=getDone();current=Math.min(steps.length-1,Math.max(0,current));
  const step=steps[current];
  $('#se412Count',panel).textContent=done.size+'/'+steps.length+' objectives';
  $('#se412Meter',panel).style.width=(100*done.size/steps.length)+'%';
  $('#se412Step',panel).textContent='STEP '+(current+1)+' / '+steps.length+' · '+step.title;
  $('#se412Tool',panel).textContent=step.tool;
  $('#se412Task',panel).textContent=step.task;
  $('#se412Why',panel).textContent=step.why;
  $('#se412HintText',panel).textContent=step.hint;
  $('#se412Hint',panel).open=false;
  const checklist=$('#se412Checks',panel);checklist.replaceChildren();
  steps.forEach((item,index)=>{
   const row=button((done.has(index)?'☑ ':'☐ ')+(index+1)+'. '+item.title,()=>{current=index;display();});
   row.className='se412-check'+(index===current?' active':'');row.setAttribute('aria-current',String(index===current));
   checklist.append(row);
  });
  $('#se412Mark',panel).textContent=done.has(current)?'Reopen objective':'Mark objective complete';
  $('#se412Prev',panel).disabled=current===0;
  $('#se412Next',panel).disabled=current===steps.length-1;
  $('#se412Victory',panel).hidden=done.size!==steps.length;
 }
 function attachPanel(){
  const scene=$('#modelAtelierPanel .atelier-scene');if(!scene||!belongs())return;
  let panel=$('#se412Panel');
  if(!panel){
   panel=document.createElement('aside');panel.id='se412Panel';panel.setAttribute('aria-label','Apprentice Satchel tutorial');
   panel.innerHTML='<header id="se412Drag"><strong>✦ Apprentice Satchel</strong><span id="se412Count"></span><button id="se412Fold" type="button" aria-label="Collapse quest panel">−</button></header>'+
    '<div class="se412-content"><div class="se412-bar"><div id="se412Meter"></div></div><nav id="se412Checks" aria-label="Quest objectives"></nav>'+
    '<h3 id="se412Step"></h3><small id="se412Tool"></small><p id="se412Task"></p><p class="se412-why" id="se412Why"></p>'+
    '<details id="se412Hint"><summary>Explain and show a hint</summary><p id="se412HintText"></p></details>'+
    '<p id="se412Note" role="status" aria-live="polite"></p><div class="se412-actions" id="se412ActionBar"></div>'+
    '<p id="se412Victory" hidden>Quest complete. Save your editable satchel in My Projects.</p></div>';
   const bar=$('#se412ActionBar',panel);
   bar.append(button('←',()=>{current--;lessonNotice('');display();},'se412-prev'),
    button('Check my work',()=>{const result=assess(steps[current]);lessonNotice(result.message);if(result.ok===true){const done=getDone();done.add(current);storeDone(done);display();lessonNotice(result.message);}},'se412-assess'),
    button('Mark objective complete',()=>{const done=getDone();if(done.has(current))done.delete(current);else done.add(current);storeDone(done);display();},'se412-mark'),
    button('→',()=>{current++;lessonNotice('');display();},'se412-next'));
   bar.children[0].id='se412Prev';bar.children[2].id='se412Mark';bar.children[3].id='se412Next';
   $('#se412Fold',panel).addEventListener('click',()=>{folded=!folded;panel.classList.toggle('collapsed',folded);$('#se412Fold',panel).textContent=folded?'+':'−';});
   // Drag via header only with the active pointer; viewport interactions remain native.
   let drag=null;
   $('#se412Drag',panel).addEventListener('pointerdown',e=>{
    if(e.target.closest('button')||e.button!==0)return;
    const box=panel.getBoundingClientRect(),host=scene.getBoundingClientRect();
    drag={id:e.pointerId,x:e.clientX,y:e.clientY,left:box.left-host.left,top:box.top-host.top};
    e.currentTarget.setPointerCapture(e.pointerId);e.preventDefault();
   });
   $('#se412Drag',panel).addEventListener('pointermove',e=>{
    if(!drag||drag.id!==e.pointerId)return;
    const x=Math.max(0,Math.min(scene.clientWidth-panel.offsetWidth,drag.left+e.clientX-drag.x));
    const y=Math.max(0,Math.min(scene.clientHeight-50,drag.top+e.clientY-drag.y));
    panel.style.left=x+'px';panel.style.top=y+'px';panel.style.right='auto';
   });
   const finish=()=>{drag=null;};
   $('#se412Drag',panel).addEventListener('pointerup',finish);
   $('#se412Drag',panel).addEventListener('pointercancel',finish);
  }
  if(panel.parentElement!==scene)scene.append(panel);
  panel.hidden=false;display();
 }
 function hidePanel(){const p=$('#se412Panel');if(p)p.hidden=true;}
 async function newLesson(){
  if(busy||playing||simulating)return;busy=true;
  try{
   if(typeof loadCourierProject!=='function'||typeof se371Clone!=='function')throw Error('Native blank-model or safe clone tools unavailable.');
   if(!loadCourierProject(true,false))return;
   ModelAtelier.close();
   const seed=meshParts()[0];if(!seed)throw Error('Practice cube was not created.');
   Object.assign(seed,{id:'model-seed',name:'Practice cube · shape into body',kind:'box',group:'Satchel',
    position:[0,1.5,0],rotation:[0,0,0],scale:[.65,.6,.45],color:'#987153',material:'matte'});
   await se371Clone(TITLE);
   currentProject.se412Tutorial=LESSON;
   lessonProject=projectId();
   await se175Store([se175Snapshot()]);
   remember(LAST,lessonProject);current=0;storeDone(new Set());
   attachPanel();document.getElementById('projectHub')?.classList.remove('show');
   lessonNotice('Editable tutorial copy created in My Projects. Shape the practice cube to begin.');
  }catch(error){lessonNotice('Could not start tutorial: '+error.message);if(typeof toast==='function')toast('Tutorial start failed: '+error.message);}
  finally{busy=false;}
 }
 async function resume(){
  if(busy||playing||simulating)return;
  if(belongs()){window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');ModelAtelier.open();attachPanel();document.getElementById('projectHub')?.classList.remove('show');return;}
  const savedId=recall(LAST);if(!savedId){lessonNotice('Create the tutorial first, or open your saved tutorial from My Projects.');return;}
  busy=true;
  try{
   if(dirty&&!confirm('Open your saved tutorial and discard unsaved changes in this workspace?'))return;
   const row=await se175Read(savedId);
   if(row?.data?.project?.se412Tutorial!==LESSON)throw Error('Saved tutorial copy was not found on this device.');
   ModelAtelier.close();loadProject(structuredClone(row.data),{workspaceLocal:true});
   se175StampProject(savedId,row.name||TITLE,row.starterId||'blank-model');
   workspaceLocalAllowed=true;initializeHistory('Resumed satchel tutorial');markSaved();
   currentProject.se412Tutorial=LESSON;lessonProject=savedId;
   window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');ModelAtelier.syncProject();ModelAtelier.open();
   attachPanel();document.getElementById('projectHub')?.classList.remove('show');
  }catch(error){lessonNotice('Resume failed: '+error.message);}
  finally{busy=false;}
 }
 // Keep the marker with native local and account project documents; never alter starter identity.
 const beforeSnapshot=se175Snapshot;
 se175Snapshot=function(...args){const row=beforeSnapshot.apply(this,args);if(belongs()&&row?.data?.project)row.data.project.se412Tutorial=LESSON;return row;};
 const beforeProjectData=projectData;
 projectData=function(...args){const data=beforeProjectData.apply(this,args);if(belongs()&&data?.project)data.project.se412Tutorial=LESSON;return data;};
 const beforeLoad=loadProject;
 loadProject=function(data,...args){const result=beforeLoad.call(this,data,...args);
  currentProject.se412Tutorial=data?.project?.se412Tutorial===LESSON?LESSON:null;
  if(belongs()){lessonProject=projectId();remember(LAST,lessonProject);requestAnimationFrame(attachPanel);}else hidePanel();
  return result;
 };
 function installLibrary(){
  const hub=$('#projectHub'),tabs=$('#projectHub .se170-hub-tabs'),starter=$('#se170-pane-starter');
  if(!hub||!tabs||!starter)return;
  if($('#se412Tab'))return;
  const pane=document.createElement('section');pane.className='se170-hub-pane';pane.id='se412Tutorials';pane.hidden=true;
  pane.innerHTML='<h3>Modeling tutorials</h3><p>Build the Apprentice Satchel yourself, one real modeling operation at a time. A separate project is saved in My Projects, never into the original starter.</p><div class="se412-library-actions" id="se412LibraryActions"></div><p id="se412LibraryNotice" role="status"></p>';
  $('#se412LibraryActions',pane).append(button('Start new satchel quest',()=>void newLesson()),button('Resume satchel quest',()=>void resume()));
  starter.after(pane);
  const tab=button('Tutorials',()=>{
   tabs.querySelectorAll('[role="tab"]').forEach(b=>{b.setAttribute('aria-selected','false');b.tabIndex=-1;});
   tab.setAttribute('aria-selected','true');tab.tabIndex=0;
   hub.querySelectorAll('.se170-hub-pane').forEach(p=>{p.hidden=p!==pane;});
  });
  tab.id='se412Tab';tab.setAttribute('role','tab');tab.setAttribute('aria-controls',pane.id);tab.setAttribute('aria-selected','false');tab.tabIndex=-1;
  pane.setAttribute('role','tabpanel');pane.setAttribute('aria-labelledby',tab.id);
  tabs.append(tab);
  tabs.addEventListener('click',e=>{
   if(e.target===tab||tab.contains(e.target))return;
   if(e.target.closest('button[role="tab"]')){pane.hidden=true;tab.setAttribute('aria-selected','false');tab.tabIndex=-1;}
  },true);
  tab.addEventListener('keydown',e=>{
   if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight')return;e.preventDefault();
   const other=tabs.querySelector('button[role="tab"]:not(#se412Tab)');other?.focus();other?.click();
  });
 }
 function schedule(){installLibrary();if(belongs())attachPanel();}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',schedule,{once:true});else queueMicrotask(schedule);
 document.addEventListener('click',e=>{if(e.target.closest('#projectBtn,#se320ModelProjects,#modelAtelierPanel .atelier-head'))requestAnimationFrame(schedule);},true);
 window.addEventListener('swrlz:project-loaded',()=>requestAnimationFrame(schedule));
 window.SWYRL_ENGINE_TUTORIAL_412=Object.freeze({start:newLesson,resume,steps:()=>steps.map((s,i)=>({index:i,title:s.title,done:getDone().has(i)})),status:()=>({active:belongs(),projectId:belongs()?projectId():null,progress:belongs()?getDone().size:0})});
})();