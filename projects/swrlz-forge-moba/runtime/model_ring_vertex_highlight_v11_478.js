/* SE478_RING_VERTEX_HIGHLIGHT_START */
// Native ModelAtelier scope: one authoritative component selection and one
// topology-aware ring kernel; no second picker, geometry copy or Undo entry.
(function se478RingVertexHighlight(){
 'use strict';
 const previousChoose=atelierComponentChoose;
 const workshop=()=>window.SWYRL_ENGINE_MODEL_WORKSHOP;
 function selectedShape(){
  const state=window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.();
  if(!state?.operation||state.selectionType!=='vertex')return null;
  return state.shape==='ring'?'outline':state.shape==='fill'?'fill':null;
 }
 function options(mode){
  const value=id=>Number(panel?.querySelector('#'+id)?.value);
  const steps=value('se466RingSteps'),start=value('se466ArcStart'),sweep=value('se466ArcSweep');
  return {mode,steps:Number.isFinite(steps)?steps:2,
   arcStart:Number.isFinite(start)?start:0,arcSweep:Number.isFinite(sweep)?sweep:360,
   plane:panel?.querySelector('#se466RingPlane')?.value||'xz'};
 }
 function selectCenter(slot){
  const mode=selectedShape();
  if(!mode)return {ok:false,reason:'Choose Vertex ring or Filled vertex ring first.'};
  const mesh=atelierComponentMesh(),top=mesh&&atelierComponentTopology(mesh),part=partById(selection);
  if(!Number.isInteger(slot)||slot<0||slot>=(top?.vertices?.length||0))
   return {ok:false,reason:'Tap a visible vertex to choose the ring center.'};
  if(part?.kind!=='topologyMesh')
   return {ok:false,reason:'Convert this primitive to editable topology before using connected vertex rings.'};
  if(atelierComponentMode!=='vertex'||!atelierComponentSupported())
   return {ok:false,reason:'Select an editable topology mesh in Vertex mode.'};
  // A new tap replaces the previous ring, even if the native Multi toggle is on.
  // This single center is consumed by the existing audited se466 ring kernel.
  atelierComponentPartId=selection;
  atelierComponentIds=[slot];
  atelierComponentGesture=null;
  atelierComponentDrag=null;
  atelierComponentRefresh();
  const anchor=workshop()?.setRingAnchor?.();
  if(!anchor?.ok)return anchor||{ok:false,reason:'Could not set the ring center.'};
  const result=workshop()?.selectRing?.(options(mode));
  return result||{ok:false,reason:'The ring selection was unavailable.'};
 }
 atelierComponentChoose=function(slot){
  if(selectedShape()&&atelierComponentMode==='vertex'&&Number.isInteger(slot)){
   const result=selectCenter(slot);
   if(result?.ok)return;
   status(result?.reason||result?.error||'Ring selection needs a connected topology center.',true);
   // Native single-point selection remains usable even if the model cannot
   // support rings, but do not mistake it for a successful ring selection.
   if(partById(selection)?.kind!=='topologyMesh')return previousChoose.apply(this,arguments);
   return;
  }
  return previousChoose.apply(this,arguments);
 };
 window.SWYRL_ENGINE_RING_HIGHLIGHT_478=Object.freeze({
  selectCenter,
  inspect:()=>{
   const overlay=atelierComponentOverlay?.children?.find(node=>node.userData?.se478SelectedVertices);
   const selected=atelierComponentMode==='vertex'?[...new Set(atelierComponentIds)]:[];
   return {shape:selectedShape(),partId:selection||null,selectedCount:selected.length,
    highlightedCount:overlay?.geometry?.attributes?.position?.count||0,
    highlighted:!!overlay,pointColor:overlay?.material?.color?.getHex?.()??null,
    selectedSlots:[...selected]};
  }
 });
})();
/* SE478_RING_VERTEX_HIGHLIGHT_END */
