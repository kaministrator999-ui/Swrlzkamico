// Native surface parameters participate in the existing whole-model history and JSON save.
let atelierDetailTarget=null;
function atelierSurfaceRefresh(){
 const p=partById(selection),deck=$m('SurfaceEditor');if(!deck)return;
 const portrait=p?.surfaceStyle==='portrait-head',cloth=p?.surfaceStyle==='tailored-panel';
 deck.hidden=!portrait&&!cloth;$m('SurfacePortrait').hidden=!portrait;$m('SurfaceCloth').hidden=!cloth;
 if(portrait)$m('JawTaper').value=String(p.jawTaper??.31);
 if(cloth){$m('PanelCamber').value=String(p.panelCamber??.085);$m('PanelPleat').value=String(p.panelPleat??.012);}
}
function atelierSurfaceInstall(){
 $m('SurfaceApply').addEventListener('click',()=>{
  const p=partById(selection);if(!p)return;let values;
  if(p.surfaceStyle==='portrait-head')values={jawTaper:Number($m('JawTaper').value)};
  else if(p.surfaceStyle==='tailored-panel')values={panelCamber:Number($m('PanelCamber').value),panelPleat:Number($m('PanelPleat').value)};
  else return;
  if(!checkPart({...p,...values})){status('Surface rejected: jaw 0–0.5, cloth curvature 0–0.25, folds 0–0.06.',true);return;}
  checkpoint();Object.assign(p,values);signalEdited();select(p.id);
 });
 $m('FrameSelected').addEventListener('click',()=>{
  const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);if(!mesh){status('Select a part to frame.');return;}
  const box=new THREE.Box3().setFromObject(mesh),size=box.getSize(new THREE.Vector3());atelierDetailTarget=box.getCenter(new THREE.Vector3());
  orbit.distance=Math.max(.7,Math.max(size.y,size.x/camera.aspect,size.z)*.78/Math.tan(camera.fov*Math.PI/360));cameraUpdate();
 });
}
