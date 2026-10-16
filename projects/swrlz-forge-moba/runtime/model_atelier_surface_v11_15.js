// Native surface parameters participate in the existing whole-model history and JSON save.
let atelierDetailTarget=null;
function atelierSurfaceRefresh(){
 const p=partById(selection),deck=$m('SurfaceEditor');if(!deck)return;
 const portrait=p?.surfaceStyle==='portrait-head',cloth=p?.surfaceStyle==='tailored-panel',sphere=p?.kind==='sphere';
 deck.hidden=!sphere&&!cloth;$m('SurfaceSphere').hidden=!sphere;if(sphere)$m('SurfacePreset').value=['portrait-head','tapered-muzzle','split-dye-cap'].includes(p.surfaceStyle)?p.surfaceStyle:'rounded';$m('SurfacePortrait').hidden=!portrait;$m('SurfaceCloth').hidden=!cloth;
 $m('DyeAccentRow').hidden=p?.surfaceStyle!=='split-dye-cap';$m('DyeAccent').value=p?.dyeAccent||'#f65f60';
 if(portrait)$m('JawTaper').value=String(p.jawTaper??.31);
 if(cloth){$m('PanelCamber').value=String(p.panelCamber??(p.panelAxis==='depth'?.055:.085));$m('PanelPleat').value=String(p.panelPleat??.012);}
}
function atelierSurfaceInstall(){
 $m('SurfacePreset').addEventListener('change',()=>{$m('DyeAccentRow').hidden=$m('SurfacePreset').value!=='split-dye-cap';});
 $m('SurfaceApply').addEventListener('click',()=>{
  const p=partById(selection);if(!p)return;let values;
  if(p.kind==='sphere'){const preset=$m('SurfacePreset').value;values={surfaceStyle:preset==='rounded'?undefined:preset};if(preset==='portrait-head')values.jawTaper=p.surfaceStyle==='portrait-head'?Number($m('JawTaper').value):(p.jawTaper??.31);if(preset==='split-dye-cap')values.dyeAccent=$m('DyeAccent').value;}
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

// The positive local X end tapers to a real narrow snout; rotate it with native transforms.
function atelierTaperedMuzzle(){
 const g=new THREE.SphereGeometry(1,24,16),a=g.attributes.position;
 for(let i=0;i<a.count;i++){const x=a.getX(i),t=(x+1)*.5,taper=1-.68*t*t;a.setXYZ(i,x,a.getY(i)*taper,a.getZ(i)*taper);}
 g.computeVertexNormals();g.computeBoundingSphere();return g;
}

function atelierSplitDyeCap(part){
 const g=new THREE.SphereGeometry(1,24,16),a=g.attributes.position,colors=[],left=new THREE.Color(part.color),right=new THREE.Color(part.dyeAccent||'#f65f60');
 for(let i=0;i<a.count;i++){const c=a.getX(i)<0?left:right;colors.push(c.r,c.g,c.b);}
 g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));return g;
}
