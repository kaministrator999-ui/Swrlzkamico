/* SE483_RING_DETAIL_STUDIO_START */
// Contextual precision topology and transform controls inside the existing
// se466 Ring inspector. Preview/Apply/Cancel always use native se430 workshop.
(function se483RingDetailStudio(){
 'use strict';
 const native=()=>window.SWYRL_ENGINE_MODEL_WORKSHOP;
 const progression=()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.();
 const fail=reason=>({ok:false,reason,error:reason});
 let ui=null,previewOwned=false,previewKind='',metadata=null;
 let initialized=false,selectedRing='all',lastSelectionPart='',lastCount=-1;
 const id=name=>ui?.querySelector('[data-se483="'+name+'"]');
 const number=name=>Number(id(name)?.value);
 const plane=()=>document.getElementById('se466RingPlane')?.value||'xz';
 const axes=()=>plane()==='xy'?[0,1,2]:plane()==='yz'?[1,2,0]:[0,2,1];
 function choice(){
  const state=progression(),part=partById(selection);
  if(!state?.operation||state.selectionType!=='vertex'||
   !['ring','fill'].includes(state.shape)||atelierComponentMode!=='vertex'||
   part?.kind!=='topologyMesh'||atelierComponentPartId!==selection||
   !atelierComponentIds.length)return null;
  const mesh=atelierComponentMesh(),top=mesh&&atelierComponentTopology(mesh);
  if(!mesh||!top)return null;
  const positions=top.vertices.map(v=>[
   mesh.geometry.attributes.position.getX(v),
   mesh.geometry.attributes.position.getY(v),
   mesh.geometry.attributes.position.getZ(v)]);
  const ids=[...new Set(atelierComponentIds)]
   .filter(i=>Number.isInteger(i)&&i>=0&&i<top.vertices.length);
  if(!ids.length)return null;
  const unique=new Set(ids.map(i=>positions[i].map(n=>Math.round(n*100000)).join(',')));
  return {part,mesh,top,positions,slots:ids,count:unique.size,shape:state.shape};
 }
 function stateCenter(c){
  if(c.part.se483Rings?.center?.length===3)return [...c.part.se483Rings.center];
  // Editable model local geometric bounds, not an unstable pointer pixel.
  const ax=axes(),ps=c.positions,center=[0,1,2].map(k=>(
   Math.min(...ps.map(p=>p[k]))+Math.max(...ps.map(p=>p[k])))*.5);
  if(selectedRing!=='all'&&c.part.se483Rings?.center)return [...c.part.se483Rings.center];
  return center;
 }
 function radius(c,center){
  const ax=axes(),dist=p=>Math.hypot(p[ax[0]]-center[ax[0]],p[ax[1]]-center[ax[1]]);
  return Math.max(...c.slots.map(i=>dist(c.positions[i])));
 }
 function getParams(c,action){
  const center=stateCenter(c);
  return {action,plane:plane(),center,
   radius:radius(c,center),
   target:Math.max(3,Math.round(number('density'))),
   innerRings:Math.round(number('inner')),
   spacing:id('spacing').value};
 }
 function controlsValid(){
  const c=choice();
  if(!c)return fail('Select a ring or Filled Ring on a converted editable mesh.');
  if(native()?.inspect?.()?.preview?.active&&!previewOwned)
   return fail('Apply or Cancel the current native preview first.');
  if(window.SWYRL_ENGINE_RING_HEIGHT_478?.inspect?.()?.previewOwned)
   return fail('Apply or Cancel the Ring Height preview first.');
  return {ok:true,choice:c};
 }
 function note(text,error=false){
  const label=id('message');
  if(label&&label.textContent!==text)label.textContent=text;
  if(label)label.dataset.error=String(error);
  if(error)status(text,true);
 }
 function previewDetail(action){
  const check=controlsValid();if(!check.ok){note(check.reason,true);return check;}
  const opts=getParams(check.choice,action);
  if(action==='internal'&&check.choice.shape!=='fill')
   return fail('Choose Filled Vertex Ring before adding internal rings.');
  if(action==='internal'&&(!Number.isInteger(opts.innerRings)||opts.innerRings<1||opts.innerRings>8))
   return fail('Choose 1–8 internal rings.');
  if(action==='density'&&(!Number.isInteger(opts.target)||opts.target<3||opts.target>256))
   return fail('Choose 3–256 vertices per ring.');
  const result=native()?.preview?.('ringDetail',opts);
  if(result?.ok){
   previewOwned=true;previewKind='ringDetail';metadata=opts;
   note((action==='internal'?'Internal rings':'Ring density')+
    ' preview · '+result.stats?.verticesBefore+' → '+result.stats?.verticesAfter+
    ' vertices. Apply or Cancel.');refresh();
  }else note(result?.reason||result?.error||'Topology preview unavailable.',true);
  return result;
 }
 function transformParams(c){
  const offset=['x','y','z'].map(v=>number('move'+v)),tilt=['x','y','z'].map(v=>number('rot'+v));
  const pivotMode=id('pivot').value;
  const selected=c.slots.map(i=>c.positions[i]);
  const selectionPivot=[0,1,2].map(k=>selected.reduce((s,p)=>s+p[k],0)/selected.length);
  const pivot=pivotMode==='circle'?stateCenter(c):
   pivotMode==='custom'?['x','y','z'].map(v=>number('pivot'+v)):selectionPivot;
  return {offset,tilt,pivot,plane:plane(),
   scale:number('scale'),falloff:Math.round(number('falloff')),twist:number('twist')};
 }
 function previewTransform(){
  const check=controlsValid();if(!check.ok){note(check.reason,true);return check;}
  const params=transformParams(check.choice);
  const result=native()?.preview?.('ringTransform',params);
  if(result?.ok){
   previewOwned=true;previewKind='ringTransform';metadata=null;
   note('Ring transform preview · '+check.choice.slots.length+
    ' selected vertices. Apply to save one Undo step.');refresh();
  }else note(result?.reason||result?.error||'Transform refused. Try smaller values.',true);
  return result;
 }
 function apply(){
  if(!previewOwned)return fail('Preview a detail or transform first.');
  const result=native()?.apply?.();
  if(result?.ok){
   previewOwned=false;previewKind='';metadata=null;
   note('Applied to mesh. Undo can restore the previous topology and UVs.');
   refresh();
  }else note(result?.reason||result?.error||'Could not apply this preview.',true);
  return result;
 }
 function cancel(){
  if(!previewOwned)return fail('There is no Ring detail preview to cancel.');
  const result=native()?.cancel?.();
  previewOwned=false;previewKind='';metadata=null;
  note('Canceled. Original geometry and painted UVs unchanged.');
  refresh();return result;
 }
 function selectRing(level){
  const c=choice(),saved=c?.part?.se483Rings;
  if(!c||!saved)return fail('First add internal rings to a Filled Ring selection.');
  if(native()?.inspect?.()?.preview?.active)return fail('Apply or Cancel the current preview first.');
  if(level==='all'){
   const rim=window.SWYRL_ENGINE_RIM_VISIBILITY_479;
   const seed=window.SWYRL_ENGINE_GEOMETRIC_RING_482?.inspect()?.last?.seed;
   if(!Number.isInteger(seed))return fail('Tap a Filled Ring rim again to reselect the entire area.');
   const result=rim.selectRim(seed);
   if(result?.ok){selectedRing='all';refresh();}
   return result;
  }
  const radius=level==='outer'?saved.outerRadius:saved.radii?.[Number(level)];
  if(!Number.isFinite(radius))return fail('This ring does not exist in the selected model.');
  const ax=saved.plane==='xy'?[0,1,2]:saved.plane==='yz'?[1,2,0]:[0,2,1];
  const visible=window.SWYRL_ENGINE_RIM_VISIBILITY_479;
  const tolerance=Math.max(.00008,saved.outerRadius*.007);
  const ids=[];
  const memberIndices=level==='outer'?saved.outerMembers:saved.members?.[Number(level)];
  const physicalKeys=new Set((memberIndices||[]).map(id=>{
   const ps=c.part.topologyMesh.positions;
   return [0,1,2].map(k=>Math.round(ps[id*3+k]*100000)).join(',');
  }));
  for(let i=0;i<c.positions.length;i++){
   const p=c.positions[i];
   const physical=p.map(n=>Math.round(n*100000)).join(',');
   const d=Math.hypot(p[ax[0]]-saved.center[ax[0]],p[ax[1]]-saved.center[ax[1]]);
   if((physicalKeys.size?physicalKeys.has(physical):Math.abs(d-radius)<=tolerance)&&
      (!visible?.inspect()?.frontOnly||visible.isVisibleSlot(i)))ids.push(i);
  }
  if(!ids.length)return fail('No visible vertices on that ring. Orbit the camera or turn off Visible Side Only.');
  atelierComponentMode='vertex';atelierComponentPartId=selection;atelierComponentIds=ids;
  atelierComponentGesture=null;atelierComponentDrag=null;atelierComponentRefresh();
  selectedRing=String(level);
  note((level==='outer'?'Outer ring':'Internal ring '+(Number(level)+1))+
   ' · '+ids.length+' selected vertices. Move, rotate, scale or refine independently.');
  refresh();window.SWYRL_ENGINE_RING_HEIGHT_478?.sync?.();
  return {ok:true,selectedCount:ids.length,radius};
 }
 function mount(){
  const block=document.querySelector('#se466RingControls');
  if(!block)return false;
  if(ui?.isConnected)return true;
  ui=document.createElement('section');ui.id='se483RingDetailStudio';
  ui.innerHTML=
   '<strong>Ring geometry & transforms</strong>'+
   '<nav class="se483-tabs" aria-label="Ring modeling mode">'+
    '<button type="button" data-se483="tabDetail" aria-pressed="true">Detail</button>'+
    '<button type="button" data-se483="tabTransform" aria-pressed="false">Transform</button></nav>'+
   '<div data-se483="detailPane" class="se483-pane">'+
    '<label>Vertices around ring <input type="number" min="3" max="256" step="1" data-se483="density" value="16"></label>'+
    '<div class="se483-row"><button data-se483="minus" type="button">− Vertices</button>'+
    '<button data-se483="plus" type="button">+ Vertices</button>'+
    '<button data-se483="previewDensity" type="button">Preview density</button></div>'+
    '<label>New rings inside fill <input type="number" min="1" max="8" step="1" value="2" data-se483="inner"></label>'+
    '<label>Ring spacing <select data-se483="spacing"><option value="even">Even</option>'+
    '<option value="inner">Tighter near center</option><option value="outer">Tighter near outer rim</option></select></label>'+
    '<button type="button" data-se483="previewInner">Preview new internal rings</button>'+
    '<label>Select subring <select data-se483="subring"><option value="all">All filled vertices</option></select></label>'+
    '<p class="se483-explain">Adds connected vertices and faces with interpolated original UVs. Reducing density only collapses safe, unchanged midpoint detail.</p>'+
   '</div>'+
   '<div data-se483="transformPane" class="se483-pane" hidden>'+
    '<fieldset><legend>Position · local XYZ</legend><label>X<input data-se483="movex" type="number" step=".01" value="0"></label>'+
    '<label>Y<input data-se483="movey" type="number" step=".01" value="0"></label>'+
    '<label>Z<input data-se483="movez" type="number" step=".01" value="0"></label></fieldset>'+
    '<fieldset><legend>Rotation · degrees</legend><label>X<input data-se483="rotx" type="number" step="1" value="0"></label>'+
    '<label>Y<input data-se483="roty" type="number" step="1" value="0"></label>'+
    '<label>Z<input data-se483="rotz" type="number" step="1" value="0"></label></fieldset>'+
    '<div class="se483-row"><label>Scale<input type="number" data-se483="scale" step=".01" min=".02" max="8" value="1"></label>'+
    '<label>Falloff · edge rows<input type="number" data-se483="falloff" min="0" max="8" step="1" value="0"></label></div>'+
    '<label>Progressive twist · center-to-edge °<input data-se483="twist" type="number" step="1" min="-180" max="180" value="0"></label>'+
    '<label>Pivot <select data-se483="pivot"><option value="selection">Selected vertices</option>'+
     '<option value="circle">Ring/circle center</option><option value="custom">Custom XYZ</option></select></label>'+
    '<fieldset data-se483="customPivot" hidden><legend>Custom pivot · local XYZ</legend>'+
     '<label>X<input data-se483="pivotx" type="number" step=".05" value="0"></label>'+
     '<label>Y<input data-se483="pivoty" type="number" step=".05" value="0"></label>'+
     '<label>Z<input data-se483="pivotz" type="number" step=".05" value="0"></label></fieldset>'+
    '<button type="button" data-se483="previewTransform">Preview selected-ring transform</button>'+
    '<p class="se483-explain">Each selected ring moves as one group. Falloff blends adjacent vertices; twist progressively rotates filled rings.</p>'+
   '</div>'+
   '<div class="se483-actions"><button type="button" data-se483="apply" disabled>Apply</button>'+
    '<button type="button" data-se483="cancel" disabled>Cancel</button></div>'+
   '<output data-se483="message" role="status" aria-live="polite"></output>';
  // The existing se466 native controls remain available for arc/boundary
  // operations, but don't duplicate the new selected-ring UI by default.
  const circle=document.getElementById('se482CircleControl');
  if(circle)circle.after(ui);else block.prepend(ui);
  const actions={
   minus:()=>{const n=number('density');id('density').value=String(Math.max(3,Math.floor(n)-1));},
   plus:()=>{const n=number('density');id('density').value=String(Math.min(256,Math.floor(n)+1));},
   previewDensity:()=>previewDetail('density'),
   previewInner:()=>previewDetail('internal'),
   previewTransform,
   apply,cancel
  };
  for(const [name,fn]of Object.entries(actions))id(name).addEventListener('click',()=>{
   const result=fn();if(result?.ok===false)note(result.reason||'Operation rejected.',true);
  });
  const select=id('subring');select.addEventListener('change',()=>{
   const result=selectRing(select.value);
   if(result?.ok===false)note(result.reason,true);
  });
  for(const pane of ['Detail','Transform'])id('tab'+pane).addEventListener('click',()=>{
   id('detailPane').hidden=pane!=='Detail';id('transformPane').hidden=pane!=='Transform';
   id('tabDetail').setAttribute('aria-pressed',String(pane==='Detail'));
   id('tabTransform').setAttribute('aria-pressed',String(pane==='Transform'));
  });
  id('pivot').addEventListener('change',()=>{
   id('customPivot').hidden=id('pivot').value!=='custom';
  });
  // Existing Face and legacy duplicate Ring controls stay available when
  // this contextual mode is not active.
  refresh();return true;
 }
 function refresh(){
  if(!ui?.isConnected)return;
  const c=choice(),pending=native()?.inspect?.()?.preview;
  if(previewOwned&&(!pending?.active||
    !['ringTransform','ringDetail'].includes(pending.operation))){
   previewOwned=false;previewKind='';metadata=null;
  }
  const visible=!!c||(previewOwned&&pending?.active);
  ui.hidden=!visible;
  if(!visible)return;
  if(c?.part.id!==lastSelectionPart){lastSelectionPart=c?.part.id||'';
   lastCount=-1;selectedRing='all';}
  if(c&&!previewOwned&&lastCount!==c.count){
   lastCount=c.count;
   if(document.activeElement!==id('density'))id('density').value=String(c.count);
  }
  const s=c?.part?.se483Rings,sub=id('subring');
  if(s&&s.partId===c.part.id){
   const previous=sub.value;
   const entries=[['all','All filled vertices'],
    ...s.radii.map((r,i)=>[String(i),'Internal '+(i+1)+' · radius '+r.toFixed(3)]),
    ['outer','Outer boundary']];
   const same=entries.length===sub.options.length&&entries.every((entry,i)=>
    sub.options[i].value===entry[0]);
   if(!same){
    sub.replaceChildren();
    for(const [value,label]of entries){const option=document.createElement('option');
     option.value=value;option.textContent=label;sub.append(option);}
   }
   sub.value=entries.some(([value])=>value===selectedRing)?selectedRing:'all';
   sub.disabled=false;
  }else if(sub.options.length!==1){
   sub.replaceChildren();const option=document.createElement('option');
   option.value='all';option.textContent='No inserted rings yet';sub.append(option);sub.disabled=true;
  }
  id('previewInner').disabled=c?.shape!=='fill'||!!pending?.active&&!previewOwned;
  id('previewDensity').disabled=!!pending?.active&&!previewOwned;
  id('previewTransform').disabled=!!pending?.active&&!previewOwned;
  id('apply').disabled=!previewOwned;id('cancel').disabled=!previewOwned;
  // Disable the legacy duplicate ring transform/refine buttons only while
  // our specialist controls are active. Face controls remain untouched.
  const old=document.querySelectorAll('#se466RingControls > details');
  for(const pane of old)pane.hidden=!!c;
 }
 function install(){
  if(!initialized){
   initialized=true;
   window.addEventListener('swrlz:model-workshop-change',refresh);
  }
  mount();refresh();
 }
 const previous=se430BeginnerInstall;
 se430BeginnerInstall=function(...args){
  const result=previous.apply(this,args);queueMicrotask(install);return result;
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
 else install();
 window.SWYRL_ENGINE_RING_DETAIL_483=Object.freeze({
  inspect:()=>({visible:!!ui&&!ui.hidden,selected:choice()?.slots.length||0,
   previewOwned,previewKind,subring:selectedRing,hasInternalRings:!!choice()?.part?.se483Rings}),
  previewDetail,previewTransform,selectRing,apply,cancel,refresh:install
 });
})();
/* SE483_RING_DETAIL_STUDIO_END */