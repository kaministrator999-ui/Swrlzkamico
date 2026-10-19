// §E v11.47 — explicit MANUAL side-profile calibration.
// A second reference alone does not determine 3D depth: the user must choose
// a profile source, the projected front-plane origin and a unit scale.
// Only user-linked landmarks are adjusted; unlinked depths stay untouched.
function atelierFaceProfileDepth(guide,profileU){
 return (profileU-guide.originU)*guide.unitsPerU*guide.direction;
}
function atelierFaceProfileValid(part){
 if(part?.kind!=='faceSheet')return true;
 const v=part.faceSheet||{},guide=v.profileGuide;
 if(guide===undefined){
   return !(v.landmarks||[]).some(l=>l.profileU!==undefined);
 }
 if(!guide||typeof guide!=='object'||Array.isArray(guide)||
   Object.keys(guide).sort().join('|')!=='direction|originU|refId|unitsPerU'||
   typeof guide.refId!=='string'||!guide.refId||guide.refId.length>72||
   !Number.isFinite(guide.originU)||guide.originU<0||guide.originU>1||
   !Number.isFinite(guide.unitsPerU)||guide.unitsPerU<.05||guide.unitsPerU>2||
   ![-1,1].includes(guide.direction))return false;
 return (v.landmarks||[]).every(l=>l.profileU===undefined||
    Number.isFinite(l.profileU)&&l.profileU>=0&&l.profileU<=1&&
    Math.abs(l.depth-atelierFaceProfileDepth(guide,l.profileU))<.00001&&
    Math.abs(l.depth)<=.4);
}
function atelierFaceProfileRefresh(){
 const p=partById(selection),pane=$m('FaceProfileTools');
 if(!pane)return;
 pane.hidden=p?.kind!=='faceSheet';
 if(p?.kind!=='faceSheet')return;
 const m=model(),front=p.faceSheet.refId,g=p.faceSheet.profileGuide;
 const select=$m('FaceProfileReference');
 select.replaceChildren();
 for(const r of m.references||[]){
   if(r.id===front||!['left','right'].includes(r.angle))continue;
   const option=document.createElement('option');
   option.value=r.id;option.textContent=r.name+' · '+r.angle;
   select.append(option);
 }
 if(g){
   select.value=g.refId;
   $m('FaceProfileOrigin').value=String(g.originU);
   $m('FaceProfileScale').value=String(g.unitsPerU);
   $m('FaceProfileDirection').value=String(g.direction);
 }
 const name=$m('FaceLandmarkPreset').value,
     l=p.faceSheet.landmarks?.find(l=>l.name===name);
 if(l?.profileU!==undefined)$m('FaceProfilePoint').value=String(l.profileU);
 const present=g&&(m.references||[]).some(r=>r.id===g.refId&&r.id!==front);
 $m('FaceProfileStatus').textContent=
   (!g?'No side-profile depth calibration saved. ':
     present?'Profile '+g.refId+' saved. ':'Missing linked profile image. ')+
   (p.faceSheet.landmarks?.filter(l=>l.profileU!==undefined).length||0)+
   ' image-guided depth landmarks. Camera perspective is NOT automatically solved.';
}
function atelierFaceProfileInstall(){
 const id=k=>$m('FaceProfile'+k);
 id('Calibrate').addEventListener('click',()=>{
   const p=partById(selection),m=model();
   if(p?.kind!=='faceSheet')return;
   const refId=id('Reference').value,ref=m.references.find(x=>x.id===refId);
   if(!ref||!['left','right'].includes(ref.angle)||ref.id===p.faceSheet.refId){
      status('Import a different left/right profile image first.',true);return;
   }
   const guide={refId,originU:Number(id('Origin').value),
      unitsPerU:Number(id('Scale').value),
      direction:Number(id('Direction').value)};
   const landmarks=(p.faceSheet.landmarks||[]).map(l=>{
     if(l.profileU===undefined)return l;
     return {...l,depth:atelierFaceProfileDepth(guide,l.profileU)};
   });
   const candidate={...p,faceSheet:{...p.faceSheet,profileGuide:guide,landmarks}};
   if(!atelierFaceSheetValid(candidate)||!checkPart(candidate)){
      status('Profile calibration invalid or linked depth exceeds ±0.4 world units.',true);return;
   }
   checkpoint();p.faceSheet=candidate.faceSheet;
   signalEdited();select(p.id);
   status('Saved manual front-plane origin and profile units; recalculated only linked face depths. Undo available.');
 });
 id('Link').addEventListener('click',()=>{
   const p=partById(selection),g=p?.faceSheet?.profileGuide;
   if(!g){status('Save a valid profile calibration first.',true);return;}
   const name=$m('FaceLandmarkPreset').value,
     existing=p.faceSheet.landmarks?.find(l=>l.name===name),
     ref=model().references.find(r=>r.id===g.refId),
     profileU=Number(id('Point').value);
   if(!existing||!ref||!['left','right'].includes(ref.angle)||
     !Number.isFinite(profileU)||profileU<0||profileU>1){
      status('Select an existing front-face landmark and profile U (0–1).',true);return;
   }
   const depth=atelierFaceProfileDepth(g,profileU);
   const landmarks=p.faceSheet.landmarks.map(l=>l.name===name?
     {...l,profileU,depth}:l);
   const candidate={...p,faceSheet:{...p.faceSheet,landmarks}};
   if(!atelierFaceSheetValid(candidate)||!checkPart(candidate)){
      status('Image-derived depth invalid or beyond ±0.4; change scale/origin.',true);return;
   }
   checkpoint();p.faceSheet=candidate.faceSheet;
   signalEdited();select(p.id);
   $m('FaceLandmarkPreset').value=name;
   atelierFaceLandmarkRefresh();atelierFaceProfileRefresh();
   status('Profile-guided '+name+' depth '+depth.toFixed(4)+
     ' applied to real UV face vertices. Reversible native landmark edit.');
 });
 id('Unlink').addEventListener('click',()=>{
   const p=partById(selection);
   if(p?.kind!=='faceSheet')return;
   const name=$m('FaceLandmarkPreset').value,
     old=p.faceSheet.landmarks?.find(l=>l.name===name);
   if(!old||old.profileU===undefined)return;
   const landmarks=p.faceSheet.landmarks.map(l=>{
     if(l.name!==name)return l;
     const {profileU,...rest}=l;return rest;
   });
   const candidate={...p,faceSheet:{...p.faceSheet,landmarks}};
   if(!checkPart(candidate))return;
   checkpoint();p.faceSheet=candidate.faceSheet;
   signalEdited();select(p.id);
   status('Unlinked selected landmark from profile guide, retained its current depth.');
 });
 id('Clear').addEventListener('click',()=>{
   const p=partById(selection);
   if(p?.kind!=='faceSheet'||!p.faceSheet.profileGuide)return;
   const faceSheet={...p.faceSheet,
      landmarks:(p.faceSheet.landmarks||[]).map(l=>{
         const {profileU,...rest}=l;return rest;
      })};
   delete faceSheet.profileGuide;
   const candidate={...p,faceSheet};
   if(!checkPart(candidate))return;
   checkpoint();p.faceSheet=faceSheet;signalEdited();select(p.id);
   status('Cleared manual profile calibration; retained independent face depth sculpt.');
 });
}
