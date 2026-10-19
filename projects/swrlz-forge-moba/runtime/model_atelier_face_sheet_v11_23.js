// §E Model Atelier v11.23: opt-in UV-preserving reference-face starter.
// This is a real sculptable triangulated part, NOT an imported OBJ or automatic
// full head. Its original reference remains separate and is saved in the project.
MODEL_ATELIER_KINDS.push('faceSheet');
const atelierFaceSheetTextures=new Map();
const atelierFaceSheetMaxCells=12000;
const atelierFaceLandmarkNames=['browLeft','browRight','eyeLeft','eyeRight',
 'noseBridge','noseTip','cheekLeft','cheekRight','mouthLeft','mouthRight','chin','jaw'];
function atelierFaceLandmarksValid(v){
 if(v.landmarks===undefined)return true;
 if(!Array.isArray(v.landmarks)||v.landmarks.length>atelierFaceLandmarkNames.length)return false;
 const names=new Set();
 return v.landmarks.every(l=>{
   if(!l||typeof l!=='object'||Array.isArray(l)||
     !['depth|name|radius|uv','depth|name|profileU|radius|uv'].includes(Object.keys(l).sort().join('|'))||
     !atelierFaceLandmarkNames.includes(l.name)||names.has(l.name)||
     !Array.isArray(l.uv)||l.uv.length!==2||
     !l.uv.every(a=>Number.isFinite(a)&&a>=0&&a<=1)||
     !Number.isFinite(l.depth)||Math.abs(l.depth)>.4||
     (l.profileU!==undefined&&(!Number.isFinite(l.profileU)||l.profileU<0||l.profileU>1))||
     !Number.isFinite(l.radius)||l.radius<.02||l.radius>.4)return false;
   names.add(l.name);return true;
 });
}
// Opt-in manual control-point displacement using original reference UVs.
// Radius is in normalized image-UV coordinates, not screen pixels. Original
// image and UV mapping are preserved, and a zero/empty list is legacy-identical.
function atelierFaceLandmarkSculpt(g,part){
 const landmarks=part.faceSheet.landmarks;
 if(!landmarks?.length)return g;
 const a=g.attributes.position,uv=g.attributes.uv;
 for(let i=0;i<a.count;i++){
   const u=uv.getX(i),v=uv.getY(i);
   let z=a.getZ(i);
   for(const l of landmarks){
     const d=Math.hypot(u-l.uv[0],v-l.uv[1])/l.radius;
     if(d>=1)continue;
     const w=(1-d*d)**2;
     z+=l.depth*w;
   }
   a.setZ(i,Math.max(-.6,Math.min(.6,z)));
 }
 a.needsUpdate=true;g.computeVertexNormals();
 return g;
}
function atelierFaceContourValid(v){
 if(v.contour===undefined)return true;
 return v.shape==='oval'&&Array.isArray(v.contour)&&v.contour.length===12&&
   v.contour.every(x=>typeof x==='number'&&Number.isFinite(x)&&x>=.35&&x<=1);
}
function atelierFaceContourRadius(v,theta){
 if(!v.contour)return 1;
 const step=2*Math.PI/12,cycle=((theta%(2*Math.PI))+(2*Math.PI))%(2*Math.PI),
   i=Math.floor(cycle/step)%12,t=cycle/step-i;
 return v.contour[i]*(1-t)+v.contour[(i+1)%12]*t;
}
function atelierFaceSheetValid(part){
 if(part.kind!=='faceSheet')return part.faceSheet===undefined;
 const v=part.faceSheet;
 if(!v||typeof v!=='object'||Array.isArray(v)
   ||!['crop','gridU','gridV','refId','shape'].every(key=>Object.hasOwn(v,key))
   ||Object.keys(v).some(key=>!['crop','gridU','gridV','refId','shape',
      'headDepth','landmarks','contour','profileGuide','cutout'].includes(key))
   ||typeof v.refId!=='string'||v.refId.length>72
   ||!['oval','rectangle'].includes(v.shape)
   ||!Number.isInteger(v.gridU)||v.gridU<8||v.gridU>128
   ||!Number.isInteger(v.gridV)||v.gridV<4||v.gridV>128
   ||v.gridU*v.gridV>atelierFaceSheetMaxCells
   ||!atelierFaceLandmarksValid(v)||!atelierFaceContourValid(v)
   ||(v.cutout!==undefined&&(typeof atelierCutoutValid!=='function'||!atelierCutoutValid(v.cutout)))
   ||!(typeof atelierFaceProfileValid==='function'?
      atelierFaceProfileValid(part):
      v.profileGuide===undefined&&!(v.landmarks||[]).some(l=>l.profileU!==undefined))
   ||(v.headDepth!==undefined&&(!Number.isFinite(v.headDepth)||v.headDepth<0||v.headDepth>2||v.shape!=='oval'&&v.headDepth>0))
   ||!Array.isArray(v.crop)||v.crop.length!==4||!v.crop.every(Number.isFinite))return false;
 const [x,y,w,h]=v.crop;
 return x>=0&&y>=0&&w>.03&&h>.03&&x+w<=1.0000001&&y+h<=1.0000001;
}
function atelierFaceSheetGeometry(p){
 const v=p.faceSheet;
 if(!atelierFaceSheetValid(p))return new THREE.PlaneGeometry(1,1,8,8);
 const [cx,cy,cw,ch]=v.crop;
 let g;
 if(v.shape==='rectangle'){
   g=new THREE.PlaneGeometry(1,1,v.gridU,v.gridV);
   const u=g.attributes.uv;
   for(let i=0;i<u.count;i++)u.setXY(i,cx+u.getX(i)*cw,cy+u.getY(i)*ch);
   u.needsUpdate=true;
 }else{
   // Silhouette-conforming triangulation: concentric oval rings, radial
   // segments and a center fan, no jagged clipped grid boundary.
   const seg=v.gridU,rings=v.gridV,xyz=[0,0,0],uvs=[cx+cw*.5,cy+ch*.5],indices=[];
   for(let ring=1;ring<=rings;ring++)for(let j=0;j<seg;j++){
     const theta=2*Math.PI*j/seg,r=ring/rings*atelierFaceContourRadius(v,theta);
     const sx=Math.sin(theta)*.5*r,sy=Math.cos(theta)*.5*r;
     xyz.push(sx,sy,0);
     uvs.push(cx+cw*(sx+.5),cy+ch*(sy+.5));
   }
   for(let i=0;i<seg;i++)indices.push(0,1+(i+1)%seg,1+i);
   for(let r=1;r<rings;r++)for(let j=0;j<seg;j++){
     const q=(j+1)%seg,lo=1+(r-1)*seg,hi=1+r*seg;
     indices.push(lo+j,hi+q,hi+j,lo+j,lo+q,hi+q);
   }
   g=new THREE.BufferGeometry();
   g.setAttribute('position',new THREE.Float32BufferAttribute(xyz,3));
   g.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));
   g.setIndex(indices);
   g.computeVertexNormals();
 }
 atelierFaceLandmarkSculpt(g,p);
 if(v.headDepth>0)g=atelierFaceVolumeClose(g,p);
 g.computeBoundingSphere();g.computeBoundingBox();
 return g;
}
function atelierFaceSheetMaterial(p){
 const ref=model()?.references?.find(r=>r.id===p.faceSheet?.refId);
 if(!ref)return new THREE.MeshBasicMaterial({
   color:0xffb777,side:THREE.DoubleSide,transparent:true,opacity:.65
 });
 let cached=atelierFaceSheetTextures.get(ref.id);
 if(!cached||cached.source!==ref.data){
   if(cached)cached.texture.dispose();
   const texture=new THREE.TextureLoader().load(ref.data);
   texture.colorSpace=THREE.SRGBColorSpace;
   texture.anisotropy=4;
   texture.wrapS=THREE.ClampToEdgeWrapping;
   texture.wrapT=THREE.ClampToEdgeWrapping;
   cached={source:ref.data,texture};
   atelierFaceSheetTextures.set(ref.id,cached);
 }
 return new THREE.MeshBasicMaterial({
   map:cached.texture,
   alphaMap:typeof atelierCutoutTexture==='function'?atelierCutoutTexture(p):null,
   transparent:true,side:THREE.DoubleSide,
   depthWrite:true,alphaTest:.03,color:0xffffff
 });
}
function atelierFaceSheetRefresh(){
 const part=partById(selection),pane=$m('FaceSheetControls');
 if(!pane)return;
 pane.hidden=part?.kind!=='faceSheet';
 if(!part||part.kind!=='faceSheet')return;
 const v=part.faceSheet;
 $m('FaceSheetShape').value=v.shape;
 $m('FaceSheetGridU').value=String(v.gridU);
 $m('FaceSheetGridV').value=String(v.gridV);
 const letters=['X','Y','W','H'];
 for(let i=0;i<4;i++)$m('FaceSheetCrop'+letters[i]).value=v.crop[i].toFixed(4);
 const ref=model()?.references?.find(r=>r.id===v.refId);
 $m('FaceSheetInfo').textContent=(ref?'Source image: '+ref.name:'Source image missing! Restore reference image.')
   +' · grid '+v.gridU+' × '+v.gridV
   +' · UVs track the image as the surface is sculpted.';
 atelierFaceVolumeRefresh();
 atelierFaceLandmarkRefresh();
 if(typeof atelierCutoutRefresh==='function')atelierCutoutRefresh();
 if($m('FaceContourValues'))$m('FaceContourValues').value=
   (v.contour||Array(12).fill(1)).map(x=>x.toFixed(2)).join(', ');
}
function atelierFaceContourInstall(){
 const apply=$m('FaceContourApply');if(!apply)return;
 apply.addEventListener('click',()=>{
   const p=partById(selection);
   if(p?.kind!=='faceSheet'||p.faceSheet.shape!=='oval'){
     status('Contour applies to an oval-derived image face sheet only.',true);return;
   }
   const raw=$m('FaceContourValues').value.split(',').map(x=>x.trim());
   // Reject blank and nonnumeric entries rather than treating empty as zero.
   const contour=raw.map(x=>x===''?NaN:Number(x));
   const candidate={...p,faceSheet:{...p.faceSheet,contour}};
   if(!atelierFaceSheetValid(candidate)||!checkPart(candidate)){
     status('Custom contour rejected: exactly 12 numeric radii, each 0.35–1.00.',true);
     return;
   }
   if(JSON.stringify(p.faceSheet.contour||Array(12).fill(1))===JSON.stringify(contour))return;
   checkpoint();p.faceSheet=candidate.faceSheet;delete p.sculptVertexEdits;
   signalEdited();select(p.id);
   status('Saved 12-point image silhouette. UVs follow the resized boundary; original photo is preserved.');
 });
 $m('FaceContourReset').addEventListener('click',()=>{
   const p=partById(selection);if(p?.kind!=='faceSheet'||!p.faceSheet.contour)return;
   checkpoint();delete p.faceSheet.contour;delete p.sculptVertexEdits;
   signalEdited();select(p.id);status('Restored original oval contour.');
 });
}
function atelierFaceLandmarkRefresh(){
 const p=partById(selection);
 const panel=$m('FaceLandmarkTools');
 if(!panel)return;
 panel.hidden=p?.kind!=='faceSheet';
 if(!p||p.kind!=='faceSheet')return;
 const key=$m('FaceLandmarkPreset').value;
 const item=p.faceSheet.landmarks?.find(x=>x.name===key);
 if(item){
   $m('FaceLandmarkU').value=String(item.uv[0]);
   $m('FaceLandmarkV').value=String(item.uv[1]);
   $m('FaceLandmarkRadius').value=String(item.radius);
   $m('FaceLandmarkDepth').value=String(item.depth);
 }
 $m('FaceLandmarkStatus').textContent=(p.faceSheet.landmarks?.length||0)+
   ' saved features. UV 0–1 maps directly onto the source image; positive depth raises the face, negative recesses it. '+
   'Choose Front/Side in References to compare actual profile manually.';
}
// Tap-to-place maps an untransformed object-fit:contain image's actual
// displayed pixel rect to native bottom-up UV coordinates. Never silently
// interpret panned/rotated/mirrored image pixels as source image positions.
function atelierFacePickAtReference(e){
 const toggle=$m('FaceLandmarkPick');
 if(!toggle?.checked)return false;
 const p=partById(selection),r=atelierRefCurrent();
 if(p?.kind!=='faceSheet'||!r||p.faceSheet.refId!==r.id){
   status('Select the image face sheet matching the active reference.',true);return true;
 }
 if(r.zoom!==1||r.offsetX!==0||r.offsetY!==0||r.rotation!==0||r.mirror){
   status('Reset reference zoom/pan/rotation/mirroring before tapping to place UV landmarks.',true);
   return true;
 }
 const img=$m('ReferenceImage'),frame=$m('ReferenceImageFrame');
 if(!img?.naturalWidth||!img?.naturalHeight||!frame){
   status('Reference image has not finished loading.',true);return true;
 }
 const rect=frame.getBoundingClientRect(),natural=img.naturalWidth/img.naturalHeight;
 const width=Math.min(rect.width,rect.height*natural),
   height=Math.min(rect.height,rect.width/natural);
 const left=rect.left+(rect.width-width)/2,top=rect.top+(rect.height-height)/2;
 const u=(e.clientX-left)/width,v=1-(e.clientY-top)/height;
 if(u<0||u>1||v<0||v>1){
   status('Tap inside the actual image, not its letterbox margin.',true);return true;
 }
 $m('FaceLandmarkU').value=u.toFixed(5);
 $m('FaceLandmarkV').value=v.toFixed(5);
 // Reuse exactly the same native validation + checkpoint as numerical Apply.
 $m('FaceLandmarkApply').click();
 status('Placed '+$m('FaceLandmarkPreset').value+' at source-image UV ('+
   u.toFixed(3)+', '+v.toFixed(3)+') and rebuilt actual face geometry.');
 return true;
}
function atelierFaceLandmarkInstall(){
 const id=k=>$m('FaceLandmark'+k);
 id('Preset').addEventListener('change',atelierFaceLandmarkRefresh);
 id('Apply').addEventListener('click',()=>{
   const p=partById(selection);if(p?.kind!=='faceSheet')return;
   const name=id('Preset').value,
     uv=[Number(id('U').value),Number(id('V').value)],
     radius=Number(id('Radius').value),depth=Number(id('Depth').value);
   const item={name,uv,radius,depth};
   const landmarks=(p.faceSheet.landmarks||[]).filter(x=>x.name!==name);
   landmarks.push(item);
   const candidate={...p,faceSheet:{...p.faceSheet,landmarks}};
   if(!atelierFaceSheetValid(candidate)||!checkPart(candidate)){
     status('Face landmark rejected: UV 0–1, radius .02–.4, depth ±.4, finite values only.',true);return;
   }
   checkpoint();p.faceSheet=candidate.faceSheet;
   signalEdited();select(p.id);
   id('Preset').value=name;atelierFaceLandmarkRefresh();
   status('Saved manual '+name+' landmark; recomputed actual UV face mesh. Undo/Redo and native JSON remain available.');
 });
 id('Remove').addEventListener('click',()=>{
   const p=partById(selection);if(p?.kind!=='faceSheet')return;
   const name=id('Preset').value;
   if(!p.faceSheet.landmarks?.some(x=>x.name===name))return;
   const landmarks=p.faceSheet.landmarks.filter(x=>x.name!==name);
   const candidate={...p,faceSheet:{...p.faceSheet,landmarks}};
   if(!checkPart(candidate))return;
   checkpoint();p.faceSheet=candidate.faceSheet;signalEdited();select(p.id);
   id('Preset').value=name;atelierFaceLandmarkRefresh();
   status('Removed feature deformation. Original UV image and mesh source preserved.');
 });
}
function atelierFaceSheetCreate(){
 const m=model(),ref=atelierRefCurrent();
 if(!m||!ref){status('Import or select a face reference image first.',true);return;}
 if(m.parts.length>=MODEL_ATELIER_LIMIT){status('Mesh part limit reached.',true);return;}
 const part={
   id:'face-sheet-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,6),
   name:'Editable image face sheet · '+ref.name.slice(0,40),
   group:'Reference modeling',
   kind:'faceSheet',faceSheet:{
     refId:ref.id,shape:'oval',gridU:48,gridV:20,crop:[0,0,1,1],headDepth:0
   },
   material:'matte',color:'#ffffff',
   position:[0,2.85,1.25],rotation:[0,0,0],scale:[.56,.72,.56]
 };
 if(!checkPart(part)){status('Face sheet settings rejected.',true);return;}
 checkpoint();m.parts.push(part);signalEdited();select(part.id);
 status('Created a triangulated, UV-mapped face sheet from the selected reference. Use brush/lasso and side camera to extrude; original head and source image preserved.');
}
function atelierFaceSheetInstall(){
 atelierFaceVolumeInstall();
 if(typeof atelierCutoutInstall==='function')atelierCutoutInstall();
 atelierFaceLandmarkInstall();atelierFaceContourInstall();
 $m('FaceSheetCreate').addEventListener('click',atelierFaceSheetCreate);
 const kind=$m('Kind');
 if(kind&&!kind.querySelector('option[value="faceSheet"]')){
   const opt=document.createElement('option');
   opt.value='faceSheet';opt.textContent='Face image sheet (UV)';opt.disabled=true;
   kind.append(opt);
 }
 $m('FaceSheetApply').addEventListener('click',()=>{
   const p=partById(selection);
   if(!p||p.kind!=='faceSheet')return;
   const shape=$m('FaceSheetShape').value;
   const gridU=Number($m('FaceSheetGridU').value),gridV=Number($m('FaceSheetGridV').value);
   const crop=['X','Y','W','H'].map(k=>Number($m('FaceSheetCrop'+k).value));
   const headDepth=Number($m('FaceSheetHeadDepth').value);
   const candidate={...p,faceSheet:{...p.faceSheet,shape,gridU,gridV,crop,headDepth}};
   if(!atelierFaceSheetValid(candidate)||!checkPart(candidate)){
     status('Face image settings invalid: cells ≤12k; crop must remain within 0–1.',true);return;
   }
   checkpoint();p.faceSheet=candidate.faceSheet;
   // Source-index vertex moves are bound to old topology; never silently
   // remap them to unrelated new image-grid vertices.
   delete p.sculptVertexEdits;
   signalEdited();select(p.id);
   status('UV image sheet resolution/crop updated. Original image preserved.');
 });
}
