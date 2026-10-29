// §E v11.55 — owner-authored, alpha-feather photographic UV cutout.
// The source image/UV, optional closed head, and 283-part starter are immutable.
// This is an honest render-time alpha mask, not claimed mesh re-topologization.
const atelierCutoutMaxPoints=32,atelierCutoutResolution=256;
const atelierCutoutTextures=new Map();
let atelierCutoutDraft=null;
function atelierCutoutValid(v){
 if(!v||typeof v!=='object'||Array.isArray(v)||
   Object.keys(v).sort().join('|')!=='feather|points'||
   !Number.isFinite(v.feather)||v.feather<0||v.feather>.12||
   !Array.isArray(v.points)||v.points.length<3||v.points.length>atelierCutoutMaxPoints||
   v.points.some(p=>!Array.isArray(p)||p.length!==2||
    !p.every(n=>Number.isFinite(n)&&n>=0&&n<=1)))return false;
 const p=v.points,n=p.length;
 const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
 const segments=(a,b,c,d)=>Math.min(a[0],b[0])<=Math.max(c[0],d[0])+1e-9&&
  Math.min(c[0],d[0])<=Math.max(a[0],b[0])+1e-9&&
  Math.min(a[1],b[1])<=Math.max(c[1],d[1])+1e-9&&
  Math.min(c[1],d[1])<=Math.max(a[1],b[1])+1e-9&&
  cross(a,b,c)*cross(a,b,d)<=0&&cross(c,d,a)*cross(c,d,b)<=0;
 let area=0;
 for(let i=0;i<n;i++){
  const a=p[i],c=p[(i+1)%n];
  if(Math.hypot(a[0]-c[0],a[1]-c[1])<.003)return false;
  area+=a[0]*c[1]-a[1]*c[0];
  for(let j=i+1;j<n;j++){
   if(j===i+1||(i===0&&j===n-1))continue;
   if(segments(a,c,p[j],p[(j+1)%n]))return false;
  }
 }
 return Math.abs(area)>.0002;
}
function atelierCutoutWeight(uv,mask){
 if(!mask)return 1;
 const p=mask.points,n=p.length;
 let inside=false,minSq=Infinity;
 for(let i=0,j=n-1;i<n;j=i++){
  const a=p[j],b=p[i],vx=b[0]-a[0],vy=b[1]-a[1];
  const t=Math.max(0,Math.min(1,((uv[0]-a[0])*vx+(uv[1]-a[1])*vy)/
    (vx*vx+vy*vy+1e-18)));
  minSq=Math.min(minSq,(uv[0]-a[0]-vx*t)**2+(uv[1]-a[1]-vy*t)**2);
  if((a[1]>uv[1])!==(b[1]>uv[1])&&uv[0]<
    (b[0]-a[0])*(uv[1]-a[1])/(b[1]-a[1])+a[0])inside=!inside;
 }
 if(mask.feather===0)return inside?1:0;
 const signed=Math.sqrt(minSq)*(inside?1:-1);
 const t=Math.max(0,Math.min(1,.5+signed/mask.feather));
 return t*t*(3-2*t);
}
function atelierCutoutTexture(part){
 const mask=part.faceSheet?.cutout;
 if(!mask)return null;
 const id=part.id,key=JSON.stringify(mask),cached=atelierCutoutTextures.get(id);
 if(cached?.key===key)return cached.texture;
 if(typeof document==='undefined')return null;
 const cvs=document.createElement('canvas');
 cvs.width=cvs.height=atelierCutoutResolution;
 const ctx=cvs.getContext('2d',{willReadFrequently:false});
 if(!ctx)return null;
 const pixels=ctx.createImageData(atelierCutoutResolution,atelierCutoutResolution);
 for(let y=0;y<atelierCutoutResolution;y++)for(let x=0;x<atelierCutoutResolution;x++){
  const alpha=Math.round(255*atelierCutoutWeight(
   [(x+.5)/atelierCutoutResolution,1-(y+.5)/atelierCutoutResolution],mask));
  const i=(y*atelierCutoutResolution+x)*4;
  // Three.js alphaMap samples GREEN, not the alpha channel.
  pixels.data[i]=pixels.data[i+1]=pixels.data[i+2]=alpha;
  pixels.data[i+3]=255;
 }
 ctx.putImageData(pixels,0,0);
 const texture=new THREE.CanvasTexture(cvs);
 texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;
 texture.magFilter=THREE.LinearFilter;
 texture.minFilter=THREE.LinearFilter;
 if(cached)cached.texture.dispose();
 atelierCutoutTextures.set(id,{key,texture});
 return texture;
}
function atelierCutoutForm(){
 const p=partById(selection);
 if(p?.kind!=='faceSheet')return null;
 const raw=String($m('FaceCutoutPoints').value).trim();
 const pair=raw.split(';').map(v=>v.trim());
 if(pair.length<3||pair.length>atelierCutoutMaxPoints)return null;
 const points=pair.map(v=>{
  const bits=v.split(',').map(q=>q.trim());
  if(bits.length!==2||bits.some(q=>q===''))return [NaN,NaN];
  return bits.map(Number);
 });
 const cutout={points,feather:Number($m('FaceCutoutFeather').value)};
 return atelierCutoutValid(cutout)?cutout:null;
}
function atelierCutoutRefresh(){
 const p=partById(selection),active=p?.kind==='faceSheet';
 const panel=$m('FaceCutoutTools');if(!panel)return;
 panel.hidden=!active;
 if(!active){atelierCutoutDraft=null;return;}
 const mask=p.faceSheet.cutout;
 $m('FaceCutoutPoints').value=mask?.points.map(a=>a.join(', ')).join('; ')||'';
 $m('FaceCutoutFeather').value=String(mask?.feather??.025);
 $m('FaceCutoutInfo').textContent=(mask?mask.points.length+' saved UV vertices, feather '+mask.feather.toFixed(3):'No alpha cutout')+
  ' · original local image is preserved. Mask changes visible pixels, not mesh topology.';
}
function atelierCutoutCommit(mask){
 const p=partById(selection);
 if(p?.kind!=='faceSheet'||!atelierCutoutValid(mask))return false;
 const next={...p,faceSheet:{...p.faceSheet,cutout:mask}};
 if(!checkPart(next))return false;
 checkpoint();p.faceSheet=next.faceSheet;
 const id=p.id;signalEdited();select(id);
 return true;
}
function atelierCutoutTap(e){
 if(!atelierCutoutDraft)return;
 const p=partById(selection),ref=atelierRefCurrent();
 if(p?.kind!=='faceSheet'||!ref||p.faceSheet.refId!==ref.id){
  status('Select the face sheet belonging to the active image first.',true);return;
 }
 if(ref.zoom!==1||ref.offsetX!==0||ref.offsetY!==0||ref.rotation!==0||ref.mirror){
  status('Reset zoom, pan, rotation and mirroring before sampling source UV.',true);return;
 }
 const frame=$m('ReferenceImageFrame'),img=$m('ReferenceImage');
 if(!frame||!img?.naturalWidth||!img?.naturalHeight)return;
 const rect=frame.getBoundingClientRect(),ratio=img.naturalWidth/img.naturalHeight;
 const width=Math.min(rect.width,rect.height*ratio),height=Math.min(rect.height,rect.width/ratio);
 const left=rect.left+(rect.width-width)/2,top=rect.top+(rect.height-height)/2;
 const u=(e.clientX-left)/width,v=1-(e.clientY-top)/height;
 if(u<0||u>1||v<0||v>1)return;
 if(atelierCutoutDraft.length>=atelierCutoutMaxPoints){
  status('Maximum 32 UV mask points. Finish or cancel.',true);return;
 }
 const last=atelierCutoutDraft.at(-1);
 if(last&&Math.hypot(last[0]-u,last[1]-v)<.003)return;
 atelierCutoutDraft.push([Number(u.toFixed(5)),Number(v.toFixed(5))]);
 $m('FaceCutoutPoints').value=atelierCutoutDraft.map(p=>p.join(', ')).join('; ');
 status('Captured '+atelierCutoutDraft.length+' source-image mask vertices. Tap around the face then Finish.');
}
function atelierCutoutInstall(){
 const id=k=>$m('FaceCutout'+k);
 id('Apply').addEventListener('click',()=>{
  const cutout=atelierCutoutForm();
  if(!cutout||!atelierCutoutCommit(cutout)){
   status('Cutout rejected: 3–32 UV points (0–1), no crossings, area >.0002, feather 0–.12.',true);return;
  }
  atelierCutoutDraft=null;status('Saved alpha-feathered face image mask. Undo available; source photo untouched.');
 });
 id('Start').addEventListener('click',()=>{
  const p=partById(selection);if(p?.kind!=='faceSheet')return;
  atelierCutoutDraft=[];id('Points').value='';
  status('Tap the actual front image around the facial silhouette (3–32 positions), then Finish.');
 });
 id('Finish').addEventListener('click',()=>{
  if(!atelierCutoutDraft)return;
  const c={points:atelierCutoutDraft.slice(),feather:Number(id('Feather').value)};
  if(!atelierCutoutCommit(c)){status('Cutout polygon invalid (crossed, too small or incomplete).',true);return;}
  atelierCutoutDraft=null;status('Saved hand-traced UV alpha cutout in one Undo transaction.');
 });
 id('Cancel').addEventListener('click',()=>{
  atelierCutoutDraft=null;atelierCutoutRefresh();status('Cutout trace cancelled; saved mask unchanged.');
 });
 id('Clear').addEventListener('click',()=>{
  const p=partById(selection);if(p?.kind!=='faceSheet'||!p.faceSheet.cutout)return;
  const next={...p,faceSheet:{...p.faceSheet}};delete next.faceSheet.cutout;
  if(!checkPart(next))return;
  checkpoint();p.faceSheet=next.faceSheet;signalEdited();select(p.id);
  status('Removed alpha cutout (Undo restores it). Original photo remains.');
 });
 const frame=$m('ReferenceImageFrame');
 // Capture before the existing reference-gesture and landmark handlers.
 frame?.addEventListener('click',e=>{
  if(!atelierCutoutDraft)return;
  e.preventDefault();e.stopImmediatePropagation();atelierCutoutTap(e);
 },true);
}
