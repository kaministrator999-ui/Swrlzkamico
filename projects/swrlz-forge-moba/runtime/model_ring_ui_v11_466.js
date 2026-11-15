/* SE466_RING_UI_START */
// Preserve all later extrusion control enhancements, changing only the numeric range.
const se466OriginalBeginnerAmount=se430BeginnerAmount;
se430BeginnerAmount=function(operation){
 const config=se466OriginalBeginnerAmount(operation);
 return operation==='extrude'&&config?{...config,min:-30,max:30,label:'Depth · signed local units (up to 30)'}:config;
};

// Native Model Studio controls: single source of geometry/history via se430ModelWorkshop.
function se466RingUIInstall(panel){
 if(!panel||panel.dataset.se466RingUI)return;
 const anchor=panel.querySelector('#se430SelectionContext'),native=panel.querySelector('#modelAtelierTopologyWorkshop');
 if(!anchor||!native)return;
 panel.dataset.se466RingUI='1';
 const block=document.createElement('details');block.id='se466RingControls';block.className='se466-ring-controls';
 block.innerHTML='<summary>Ring / arc modeling · select, shape, refine</summary>'+
  '<div class="se466-row"><button type="button" data-ring="anchor">Use selected vertex as center</button>'+
  '<button type="button" data-ring="select">Select ring / arc</button></div>'+
  '<div class="se466-row"><label>Selection<select id="se466RingMode"><option value="outline">Ring outline</option><option value="fill">Filled radius</option></select></label>'+
  '<label>Expand rings<input id="se466RingSteps" type="number" min="0" max="40" step="1" value="2"></label><label>Radius slider<input id="se466StepsSlider" type="range" min="0" max="40" step="1" value="2"></label>'+
  '<label>Plane<select id="se466RingPlane"><option value="xz">XZ (horizontal)</option><option value="xy">XY</option><option value="yz">YZ</option></select></label></div>'+
  '<div class="se466-row"><label>Arc start °<input id="se466ArcStart" type="number" min="-360" max="360" step="5" value="0"></label>'+
  '<label>Arc width °<input id="se466ArcSweep" type="number" min="1" max="360" step="5" value="360"></label><label>Arc slider<input id="se466ArcSlider" type="range" min="1" max="360" step="1" value="360"></label>'+
  '<button type="button" data-ring="half">Half-ring 180°</button>'+
  '<button type="button" data-ring="full">Full 360°</button>'+
  '<button type="button" data-ring="shrink">− Radius</button><button type="button" data-ring="grow">+ Radius</button></div>'+
  '<details open><summary>Move, scale and rotate selected vertices</summary>'+
  '<div class="se466-row"><label>Move X<input id="se466MoveX" type="number" step=".05" min="-30" max="30" value="0"></label>'+
  '<label>Move Y<input id="se466MoveY" type="number" step=".05" min="-30" max="30" value="0"></label>'+
  '<label>Move Z<input id="se466MoveZ" type="number" step=".05" min="-30" max="30" value="0"></label></div>'+
  '<div class="se466-row"><label>Scale<input id="se466Scale" type="number" step=".05" min=".02" max="8" value="1"></label>'+
  '<label>Left<input id="se466ScaleLeft" type="number" step=".05" min=".02" max="8" value="1"></label>'+
  '<label>Right<input id="se466ScaleRight" type="number" step=".05" min=".02" max="8" value="1"></label></div>'+
  '<div class="se466-row"><label>Tilt X °<input id="se466TiltX" type="number" min="-180" max="180" step="5" value="0"></label>'+
  '<label>Tilt Y °<input id="se466TiltY" type="number" min="-180" max="180" step="5" value="0"></label>'+
  '<label>Tilt Z °<input id="se466TiltZ" type="number" min="-180" max="180" step="5" value="0"></label>'+
  '<label>Soft falloff · rows<input id="se466Falloff" type="number" min="0" max="8" step="1" value="0"></label></div>'+
  '<div class="se466-row"><button type="button" data-ring="transform">Preview ring transform</button></div></details>'+
  '<details><summary>Build new geometry from selection</summary>'+
  '<p>Edge refinement adds real connected vertices. Ring extrusion requires one complete open boundary loop; interior crown sections use Face Inset / Extrude.</p>'+
  '<div class="se466-row"><label>Extrude distance<input id="se466Depth" type="number" step=".1" min="-30" max="30" value=".25"></label>'+
  '<label>Axis<select id="se466Axis"><option value="y">Y</option><option value="x">X</option><option value="z">Z</option></select></label></div>'+
  '<div class="se466-row"><button type="button" data-ring="extrude">Preview boundary extrusion</button>'+
  '<button type="button" data-ring="refine">Preview subdivide selected edges</button></div></details>'+
  '<div class="se466-row se466-commit"><button type="button" data-ring="apply">Apply preview</button>'+
  '<button type="button" data-ring="cancel">Cancel preview</button></div>'+
  '<output id="se466RingStatus" role="status" aria-live="polite">Select a vertex and set the ring center.</output>';
 anchor.after(block);
 const face=document.createElement('details');face.id='se466FaceExtrude';face.className='se466-face-extrude';
 face.innerHTML='<summary>Extrude shape · scale, offset, tilt</summary>'+
  '<p>Controls the newly extruded face in the existing Preview / Apply workflow. Zero offset and 1× scale preserve the original extrusion behavior.</p>'+
  '<div class="se466-row"><label>Scale<input id="modelAtelierWorkshopExtrudeScale" type="number" min=".02" max="8" step=".05" value="1"></label>'+
  '<label>Left<input id="modelAtelierWorkshopExtrudeLeft" type="number" min=".02" max="8" step=".05" value="1"></label>'+
  '<label>Right<input id="modelAtelierWorkshopExtrudeRight" type="number" min=".02" max="8" step=".05" value="1"></label></div><div class="se466-row"><label>Quick cap scale<input id="se466FaceScaleSlider" type="range" min=".02" max="8" step=".01" value="1"></label></div>'+
  '<div class="se466-row"><label>Offset X<input id="modelAtelierWorkshopExtrudeX" type="number" min="-30" max="30" step=".05" value="0"></label>'+
  '<label>Offset Y<input id="modelAtelierWorkshopExtrudeY" type="number" min="-30" max="30" step=".05" value="0"></label>'+
  '<label>Offset Z<input id="modelAtelierWorkshopExtrudeZ" type="number" min="-30" max="30" step=".05" value="0"></label></div>'+
  '<div class="se466-row"><label>Tilt X °<input id="modelAtelierWorkshopExtrudeTiltX" type="number" min="-180" max="180" step="5" value="0"></label>'+
  '<label>Tilt Y °<input id="modelAtelierWorkshopExtrudeTiltY" type="number" min="-180" max="180" step="5" value="0"></label>'+
  '<label>Tilt Z °<input id="modelAtelierWorkshopExtrudeTiltZ" type="number" min="-180" max="180" step="5" value="0"></label></div>';
 block.after(face);
 const value=id=>Number(panel.querySelector('#'+id)?.value),action=()=>{
  return {scale:value('se466Scale'),leftScale:value('se466ScaleLeft'),rightScale:value('se466ScaleRight'),
   offset:['X','Y','Z'].map(a=>value('se466Move'+a)),tilt:['X','Y','Z'].map(a=>value('se466Tilt'+a)),
   falloff:value('se466Falloff')};
 };
 const show=result=>{
  const out=panel.querySelector('#se466RingStatus');
  if(out)out.textContent=result?.ok?result.message||'Operation ready. Review the preview, then Apply or Cancel.':
   result?.reason||result?.error||'No result returned.';
  se466RingUIRefresh(panel);return result;
 };
 block.addEventListener('click',event=>{
  const button=event.target.closest('button[data-ring]');if(!button)return;
  const op=button.dataset.ring,api=se430ModelWorkshop,opts=action();
  if(op==='anchor')return show(api.setRingAnchor());
  if(op==='half'||op==='full'){panel.querySelector('#se466ArcSweep').value=op==='half'?'180':'360';return;}
  if(op==='shrink'||op==='grow'){const node=panel.querySelector('#se466RingSteps');node.value=Math.max(0,Math.min(40,Number(node.value)+(op==='grow'?1:-1)));return show(api.selectRing({steps:value('se466RingSteps'),mode:panel.querySelector('#se466RingMode').value,
    arcStart:value('se466ArcStart'),arcSweep:value('se466ArcSweep'),plane:panel.querySelector('#se466RingPlane').value}));}
  if(op==='select')return show(api.selectRing({steps:value('se466RingSteps'),mode:panel.querySelector('#se466RingMode').value,
   arcStart:value('se466ArcStart'),arcSweep:value('se466ArcSweep'),plane:panel.querySelector('#se466RingPlane').value}));
  if(op==='transform')return show(api.preview('ringTransform',opts));
  if(op==='refine')return show(api.preview('ringRefine',{}));
  if(op==='extrude')return show(api.preview('ringExtrude',{...opts,amount:value('se466Depth'),axis:panel.querySelector('#se466Axis').value}));
  if(op==='apply')return show(api.apply());
  if(op==='cancel')return show(api.cancel());
 });
 const faceParams=()=>({amount:value('modelAtelierWorkshopAmount'),
  scale:value('modelAtelierWorkshopExtrudeScale'),leftScale:value('modelAtelierWorkshopExtrudeLeft'),
  rightScale:value('modelAtelierWorkshopExtrudeRight'),
  offset:['X','Y','Z'].map(a=>value('modelAtelierWorkshopExtrude'+a)),
  tilt:['X','Y','Z'].map(a=>value('modelAtelierWorkshopExtrudeTilt'+a))});
 const faceScale=face.querySelector('#modelAtelierWorkshopExtrudeScale'),faceSlider=face.querySelector('#se466FaceScaleSlider');
 const liveFace=()=>{
  const state=se430ModelWorkshop.inspect();
  if(state.preview.active&&state.preview.operation==='extrude')show(se430ModelWorkshop.preview('extrude',faceParams()));
 };
 for(const input of face.querySelectorAll('input')){
  input.addEventListener('input',()=>{
   if(input===faceSlider)faceScale.value=faceSlider.value;
   else if(input===faceScale)faceSlider.value=faceScale.value;
   liveFace();
  });
 }
 const selectParams=()=>({steps:value('se466RingSteps'),mode:panel.querySelector('#se466RingMode').value,
  arcStart:value('se466ArcStart'),arcSweep:value('se466ArcSweep'),plane:panel.querySelector('#se466RingPlane').value});
 const updateRing=()=>{
  const state=se430ModelWorkshop.inspect();
  if(state.ring?.centered&&!state.preview.active)show(se430ModelWorkshop.selectRing(selectParams()));
 };
 for(const id of ['se466RingSteps','se466ArcSweep','se466ArcStart','se466RingMode','se466RingPlane']){
  panel.querySelector('#'+id)?.addEventListener('change',updateRing);
 }
 const stepSlider=panel.querySelector('#se466StepsSlider'),arcSlider=panel.querySelector('#se466ArcSlider');
 stepSlider.addEventListener('input',()=>{panel.querySelector('#se466RingSteps').value=stepSlider.value;updateRing();});
 arcSlider.addEventListener('input',()=>{panel.querySelector('#se466ArcSweep').value=arcSlider.value;updateRing();});
 panel.querySelector('#se466RingSteps').addEventListener('change',()=>{stepSlider.value=panel.querySelector('#se466RingSteps').value;});
 panel.querySelector('#se466ArcSweep').addEventListener('change',()=>{arcSlider.value=panel.querySelector('#se466ArcSweep').value;});
 for(const id of ['se466MoveX','se466MoveY','se466MoveZ','se466Scale','se466ScaleLeft','se466ScaleRight','se466TiltX','se466TiltY','se466TiltZ','se466Falloff']){
  panel.querySelector('#'+id).addEventListener('input',()=>{
   if(se430ModelWorkshop.inspect().preview.operation==='ringTransform')
    show(se430ModelWorkshop.preview('ringTransform',action()));
  });
 }
 panel.querySelector('#se466Depth').addEventListener('input',()=>{
  if(se430ModelWorkshop.inspect().preview.operation==='ringExtrude')
   show(se430ModelWorkshop.preview('ringExtrude',{...action(),amount:value('se466Depth'),axis:panel.querySelector('#se466Axis').value}));
 });
 window.addEventListener('swrlz:model-workshop-change',()=>se466RingUIRefresh(panel));
 panel.querySelector('#modelAtelierWorkshopOperation')?.addEventListener('change',()=>se466RingUIRefresh(panel));
 se466RingUIRefresh(panel);
}
function se466RingUIRefresh(panel){
 if(!panel?.isConnected)return;
 let state;try{state=se430ModelWorkshop.inspect();}catch{return;}
 const selection=state.selection,ring=panel.querySelector('#se466RingControls'),face=panel.querySelector('#se466FaceExtrude');
 if(ring)ring.hidden=selection.mode!=='vertex';
 if(face)face.hidden=panel.querySelector('#modelAtelierWorkshopOperation')?.value!=='extrude';
 if(!ring)return;
 for(const b of ring.querySelectorAll('button[data-ring]')){
  const type=b.dataset.ring;
  b.disabled=type==='apply'?!state.preview.active:type==='cancel'?!state.preview.active:
   type==='anchor'?!selection.ids.length||selection.mode!=='vertex':
   ['select','shrink','grow'].includes(type)?!state.ring?.centered||state.preview.active:
   ['transform','refine','extrude'].includes(type)?!selection.ids.length||state.preview.active:false;
 }
 const status=ring.querySelector('#se466RingStatus');
 if(status&&state.ring?.centered&&status.textContent==='Select a vertex and set the ring center.')status.textContent='Center stored. Choose an outline, filled radius, or arc and select.';
}
/* SE466_RING_UI_END */