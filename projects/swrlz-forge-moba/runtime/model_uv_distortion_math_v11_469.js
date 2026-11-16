// SE469_UV_DISTORTION_MATH_START
// Mesh-space UV Jacobians measured both before and after the current mesh transform.
// Measurements are opt-in; this does not alter positions, UVs, or materials.
const se469Math=(()=>{
 const EPS=1e-12;
 function measure(geometry,matrixWorld,maxFaces=6000){
  const uv=geometry?.getAttribute?.('uv'),position=geometry?.getAttribute?.('position');
  const indices=geometry?.getIndex?.();
  if(!uv||!position||uv.count!==position.count)throw Error('Selected mesh needs matching UV and position attributes.');
  const faceCount=Math.floor((indices?.count||position.count)/3);
  if(faceCount<1||faceCount>180000)throw Error('UV preview supports 1–180,000 triangles.');
  const m=matrixWorld?.elements;
  if(!m||m.length!==16||!Array.from(m).every(Number.isFinite))throw Error('Mesh world transform is invalid.');
  const out=[],stride=Math.max(1,Math.ceil(faceCount/maxFaces));
  let valid=0,degenerate=0,worldU=0,worldV=0,localU=0,localV=0,peak=1,veryStretched=0;
  const len2=v=>v[0]*v[0]+v[1]*v[1]+v[2]*v[2];
  const dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
  const transform=v=>[m[0]*v[0]+m[4]*v[1]+m[8]*v[2],
                      m[1]*v[0]+m[5]*v[1]+m[9]*v[2],
                      m[2]*v[0]+m[6]*v[1]+m[10]*v[2]];
  for(let f=0;f<faceCount;f+=stride){
   const ids=[0,1,2].map(k=>indices?indices.getX(f*3+k):f*3+k);
   const u=ids.map(i=>uv.getX(i)),v=ids.map(i=>uv.getY(i));
   if(![...u,...v].every(Number.isFinite)){degenerate++;continue;}
   const p=ids.map(i=>[position.getX(i),position.getY(i),position.getZ(i)]);
   const edge=k=>p[k].map((c,i)=>c-p[0][i]);
   const a=edge(1),b=edge(2),du1=u[1]-u[0],dv1=v[1]-v[0],du2=u[2]-u[0],dv2=v[2]-v[0];
   const det=du1*dv2-du2*dv1;
   if(Math.abs(det)<EPS){degenerate++;continue;}
   const tU=a.map((q,i)=>(q*dv2-b[i]*dv1)/det);
   const tV=a.map((q,i)=>(b[i]*du1-q*du2)/det);
   const wU=transform(tU),wV=transform(tV);
   const localULen=len2(tU),localVLen=len2(tV),wULen=len2(wU),wVLen=len2(wV);
   if(Math.min(localULen,localVLen,wULen,wVLen)<EPS){degenerate++;continue;}
   const g11=wULen,g22=wVLen,g12=dot(wU,wV),tr=g11+g22;
   const delta=Math.hypot(g11-g22,2*g12);
   const ratio=Math.sqrt((tr+delta)/Math.max(EPS,tr-delta));
   const weight=Math.abs(det);
   localU+=weight*localULen;localV+=weight*localVLen;
   worldU+=weight*wULen;worldV+=weight*wVLen;
   peak=Math.max(peak,ratio);
   if(ratio>2)veryStretched++;
   out.push({uv:[u[0],v[0],u[1],v[1],u[2],v[2]],ratio:Number.isFinite(ratio)?ratio:1});
   valid++;
  }
  if(!valid||localU<EPS||localV<EPS)throw Error('No valid, noncollapsed UV triangles to measure.');
  const scaleU=Math.sqrt(worldU/localU),scaleV=Math.sqrt(worldV/localV);
  const common=Math.max(scaleU,scaleV);
  const clamp=n=>Math.min(4,Math.max(.15,n));
  return {triangles:faceCount,sampled:valid,skipped:degenerate,highStretch:veryStretched,
   peakRatio:peak,scaleU,scaleV,
   // Keep the widest untouched axis at repeat=1; compress sampling on the shorter
   // axis to compensate for *mesh transform* anisotropy. Never infer a new unwrap.
   suggested:[clamp(scaleU/common),clamp(scaleV/common)],faces:out};
 }
 function anchoredOffset(oldOffset,oldRepeat,newRepeat,anchor){
  return [0,1].map(i=>oldOffset[i]+(anchor[i]-.5)*(oldRepeat[i]-newRepeat[i]));
 }
 return Object.freeze({measure,anchoredOffset});
})();
// SE469_UV_DISTORTION_MATH_END
