/* §E v11.542 — prevent a conical-model UV tool from damaging this humanoid.
   v11.503 front/back/brim projection is a limited beta; its elongated cone
   charts are not an unwrap for arms, hands, hips or feet. Keep the existing
   accurate native UV guide, distortion heatmap and image import available. */
function se542IsHumanoidUV(){
 const p=se503Target()?.part;
 return p?.id==='humanoid-body-unified'&&p?.kind==='topologyMesh';
}
const se542PreviousCandidate=se503Candidate;
se503Candidate=function(){
 if(se542IsHumanoidUV())throw Error(
  'This humanoid already has its own relaxed, non-overlapping UV atlas. '+
  'Front/back/brim projection is for simple conical shapes and would '+
  'stretch its fingers, torso and legs. Export the CURRENT UV Guide or '+
  'Surface/Distortion view instead; do not apply the experimental candidate.');
 return se542PreviousCandidate.apply(this,arguments);
};
const se542PreviousRefresh=se503Refresh;
se503Refresh=function(){
 const result=se542PreviousRefresh.apply(this,arguments);
 if(!se542IsHumanoidUV())return result;
 se503Preview=null;
 const root=document.getElementById('se503AtlasTool');
 if(root){
  for(const id of ['se503AtlasPrepare','se503AtlasApply','se503AtlasExport'])
   {const b=root.querySelector('#'+id);if(b)b.disabled=true;}
  const info=root.querySelector('#se503AtlasStatus');
  if(info)info.textContent='Humanoid-specific UV atlas already applied. '+
    'This experimental front/back/brim projection is incompatible with '+
    'full-body anatomy. Use the Current UV Guide, painted texture preview, '+
    'or UV distortion heatmap for this selected body.';
 }
 return result;
};
window.SWYRL_ENGINE_HUMANOID_UV_GUARD_542=Object.freeze({
 blocked:()=>se542IsHumanoidUV()});
/* SE542_HUMANOID_UV_GUARD_END */
