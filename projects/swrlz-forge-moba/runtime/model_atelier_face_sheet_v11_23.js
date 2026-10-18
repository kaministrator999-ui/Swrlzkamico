// §E Model Atelier v11.23: opt-in UV-preserving reference-face starter.
// This is a real sculptable triangulated part, NOT an imported OBJ or automatic
// full head. Its original reference remains separate and is saved in the project.
MODEL_ATELIER_KINDS.push('faceSheet');
const atelierFaceSheetTextures=new Map();
const atelierFaceSheetMaxCells=12000;
function atelierFaceSheetValid(part){
 if(part.kind!=='faceSheet')return part.faceSheet===undefined;
 const v=part.faceSheet;
 if(!v||typeof v!=='object'||Array.isArray(v)
   ||Object.keys(v).sort().join('|')!=='crop|gridU|gridV|refId|shape'
   ||typeof v.refId!=='string'||v.refId.length>72
   ||!['oval','rectangle'].includes(v.shape)
   ||!Number.isInteger(v.gridU)||v.gridU<8||v.gridU>128
   ||!Number.isInteger(v.gridV)||v.gridV<4||v.gridV>128
   ||v.gridU*v.gridV>atelierFaceSheetMaxCells
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
     const theta=2*Math.PI*j/seg,r=ring/rings;
     const sx=Math.sin(theta)*.5*r,sy=Math.cos(theta)*.5*r;
     xyz.push(sx,sy,0);
     uvs.push(cx+cw*(sx+.5),cy+ch*(sy+.5));
   }
   for(let i=0;i<seg;i++)indices.push(0,1+i,1+(i+1)%seg);
   for(let r=1;r<rings;r++)for(let j=0;j<seg;j++){
     const q=(j+1)%seg,lo=1+(r-1)*seg,hi=1+r*seg;
     indices.push(lo+j,hi+j,hi+q,lo+j,hi+q,lo+q);
   }
   g=new THREE.BufferGeometry();
   g.setAttribute('position',new THREE.Float32BufferAttribute(xyz,3));
   g.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));
   g.setIndex(indices);
   g.computeVertexNormals();
 }
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
   map:cached.texture,transparent:true,side:THREE.DoubleSide,
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
     refId:ref.id,shape:'oval',gridU:48,gridV:20,crop:[0,0,1,1]
   },
   material:'matte',color:'#ffffff',
   position:[0,2.85,1.25],rotation:[0,0,0],scale:[.56,.72,.56]
 };
 if(!checkPart(part)){status('Face sheet settings rejected.',true);return;}
 checkpoint();m.parts.push(part);signalEdited();select(part.id);
 status('Created a triangulated, UV-mapped face sheet from the selected reference. Use brush/lasso and side camera to extrude; original head and source image preserved.');
}
function atelierFaceSheetInstall(){
 $m('FaceSheetCreate').addEventListener('click',atelierFaceSheetCreate);
 const kind=$m('Kind');
 if(kind&&!kind.querySelector('option[value="faceSheet"]')){
   const opt=document.createElement('option');
   opt.value='faceSheet';opt.textContent='Face image sheet (UV)';
   kind.append(opt);
 }
 $m('FaceSheetApply').addEventListener('click',()=>{
   const p=partById(selection);
   if(!p||p.kind!=='faceSheet')return;
   const shape=$m('FaceSheetShape').value;
   const gridU=Number($m('FaceSheetGridU').value),gridV=Number($m('FaceSheetGridV').value);
   const crop=['X','Y','W','H'].map(k=>Number($m('FaceSheetCrop'+k).value));
   const candidate={...p,faceSheet:{...p.faceSheet,shape,gridU,gridV,crop}};
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
