// Anatomical study: continuous stylized skull and shaped auricles.
// Opt-in only. Older project parts without anatomyStudy/earStudy are unchanged.
// The control values are native scene data; there is no hidden renderer state.
const atelierAnatomyDefaults={jaw:.54,malar:.58,orbit:.57,nose:.65,chin:.50,temple:.42};
const atelierEarDefaults={helix:.64,concha:.58,lobe:.43};
const atelierAnatomyBell=(x,y,sx,sy)=>Math.exp(-((x/sx)**2+(y/sy)**2));
const atelierAnatomyClamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const atelierAnatomySmooth=(a,b,v)=>THREE.MathUtils.smoothstep(v,a,b);
// Keep the historically approved v11.19 sculpt and its vertex ordering.
// Anatomical sliders add restrained, local *deltas* to that surface rather
// than replacing the actual skull with a new ellipsoid. Neutral sliders have
// exactly the same geometry, colors and contact planes as the original portrait.
function atelierAnatomicalHead(part){
  const f={...atelierAnatomyDefaults,...part.anatomyStudy};
  const original=atelierPortraitFinish({...part,anatomyStudy:undefined});
  const pos=original.attributes.position,col=original.attributes.color;
  const base={jaw:.50,malar:.50,orbit:.50,nose:.50,chin:.50,temple:.50};
  const bell=atelierAnatomyBell,smooth=atelierAnatomySmooth;
  const blush=new THREE.Color('#df8f93'),tone=new THREE.Color();
  const [jaw,malar,orbit,nose,chin,temple]=Object.keys(base)
    .map(k=>(f[k]-base[k])*2);
  for(let i=0;i<pos.count;i++){
    let x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i);
    // Preserve the sculpted forehead, broad malar arc, tapered mandible and
    // side-view nasal bridge authored in v11.19; adjust only local planes.
    const low=smooth(.16,.89,-y),mandible=bell(Math.abs(x)-.55,y+.56,.30,.23);
    x*=1-.045*jaw*low+.026*malar*bell(Math.abs(x)-.54,y+.12,.28,.24);
    if(z>0){
      const front=smooth(.12,.72,z),ax=Math.abs(x);
      const cheeks=bell(ax-.47,y+.17,.24,.23);
      const sockets=bell(ax-.43,y-.095,.23,.18);
      const bridge=bell(x,y+.105,.105,.27);
      const tip=bell(x,y+.31,.112,.09);
      const wings=bell(ax-.14,y+.32,.068,.055);
      const chinPlane=bell(x,y+.74,.31,.15);
      const jawPlane=bell(ax-.53,y+.56,.23,.23);
      const temporal=bell(ax-.78,y-.26,.20,.25);
      z+=front*(.027*malar*cheeks-.025*orbit*sockets
        +nose*(.020*bridge+.041*tip+.010*wings)
        +.014*chin*chinPlane+.013*jaw*jawPlane
        -.010*temple*temporal);
      const color=tone.setRGB(col.getX(i),col.getY(i),col.getZ(i));
      color.lerp(blush,atelierAnatomyClamp(.07*Math.max(0,malar)*cheeks*front));
      col.setXYZ(i,color.r,color.g,color.b);
    }
    pos.setXYZ(i,x,y,z);
  }
  original.computeVertexNormals();original.computeBoundingSphere();
  // UV SphereGeometry duplicates two longitudinal seam vertices. Merge
  // normals only, retaining UVs, vertex indices and export topology.
  const normals=original.attributes.normal,u=part.meshDensity?.u??192,v=part.meshDensity?.v??128;
  if(pos.count===(u+1)*(v+1))for(let row=0;row<=v;row++){
    const a=row*(u+1),b=a+u;
    const normal=new THREE.Vector3().fromBufferAttribute(normals,a)
      .add(new THREE.Vector3().fromBufferAttribute(normals,b)).normalize();
    normals.setXYZ(a,normal.x,normal.y,normal.z);
    normals.setXYZ(b,normal.x,normal.y,normal.z);
  }
  return original;
}
function atelierAnatomicalEar(part){
  const f={...atelierEarDefaults,...part.earStudy};
  const n=96,rings=18,positions=[],colors=[],indices=[],uv=[];
  const skin=new THREE.Color(part.color),shade=new THREE.Color('#c68187');
  // Full 3D auricle with asymmetric helix, antihelix, concave concha and
  // inferior lobule. Not a flattened SphereGeometry or an applied decal.
  for(let face=0;face<2;face++)for(let i=0;i<=rings;i++){
    const r=i/rings;
    for(let j=0;j<=n;j++){
      const a=j/n*Math.PI*2,c=Math.cos(a),s=Math.sin(a);
      const upper=Math.max(0,s),lower=Math.max(0,-s);
      const outerX=c*(.88+.12*upper-.18*lower)
        +.12*upper*Math.sin(a*2);
      const outerY=s*(1+.13*upper-.22*lower)
        +.04*c*upper;
      const x=r*outerX,y=r*outerY;
      const bowl=Math.exp(-Math.pow((r-.38)/.30,2));
      const helix=Math.exp(-Math.pow((r-.80)/.095,2));
      const antihelix=Math.exp(-Math.pow((r-.57)/.11,2))*(.4+.6*upper);
      const depth=face===0
        ? .12+.25*f.helix*helix+.11*f.helix*antihelix
          -.30*f.concha*bowl-.07*f.lobe*lower*(1-r)
        : -.16-.06*f.lobe*lower;
      positions.push(x,y,depth);
      uv.push((x+1)/2,(y+1)/2);
      const c0=skin.clone().lerp(shade,face===0
        ? .38*f.concha*bowl+.09*antihelix : .14);
      colors.push(c0.r,c0.g,c0.b);
      if(i<rings&&j<n){
        const k=face*(rings+1)*(n+1)+i*(n+1)+j,b=k+n+1;
        if(face===0)indices.push(k,b,k+1,k+1,b,b+1);
        else indices.push(k,k+1,b,k+1,b+1,b);
      }
    }
  }
  const base=(rings+1)*(n+1);
  for(let j=0;j<n;j++){
    const a=rings*(n+1)+j,b=a+1,c=base+a,d=base+b;
    indices.push(a,c,b,b,c,d);
  }
  return atelierHDMesh(positions,colors,indices,uv);
}
function atelierAnatomyValid(p){
  const valid=(obj,fields)=>obj&&typeof obj==='object'
    &&!Array.isArray(obj)&&Object.keys(obj).length===fields.length
    &&fields.every(k=>Number.isFinite(obj[k])&&obj[k]>=0&&obj[k]<=1);
  if(p.anatomyStudy!==undefined&&
    (p.kind!=='sphere'||p.surfaceStyle!=='portrait-head'||
     p.hdFinish?.style!=='portrait'||!valid(p.anatomyStudy,Object.keys(atelierAnatomyDefaults))))return false;
  if(p.earStudy!==undefined&&
    (p.kind!=='sphere'||p.hdFinish?.style!=='ear'||
     !valid(p.earStudy,Object.keys(atelierEarDefaults))))return false;
  return true;
}
function atelierAnatomyRefresh(){
  const p=partById(selection),head=!!(p?.surfaceStyle==='portrait-head'&&p.hdFinish?.style==='portrait'),
    ear=!!(p?.kind==='sphere'&&p.hdFinish?.style==='ear');
  const deck=$m('AnatomyEditor');if(!deck)return;
  deck.hidden=!head&&!ear;
  $m('AnatomyHead').hidden=!head;$m('AnatomyEar').hidden=!ear;
  if(head)for(const k of Object.keys(atelierAnatomyDefaults))
    $m('Anatomy'+k).value=p.anatomyStudy?.[k]??atelierAnatomyDefaults[k];
  if(ear)for(const k of Object.keys(atelierEarDefaults))
    $m('Anatomy'+k).value=p.earStudy?.[k]??atelierEarDefaults[k];
}
function atelierAnatomyInstall(){
  const apply=(kind,fields)=>{
    const p=partById(selection);if(!p)return;
    const data={};for(const key of Object.keys(fields)){
      const n=Number($m('Anatomy'+key).value);
      if(!Number.isFinite(n)||n<0||n>1){status('Anatomy controls must be between 0 and 1.',true);return;}
      data[key]=n;
    }
    const next={...p,[kind]:data};
    if(!checkPart(next)){status('Select a compatible native anatomical surface.',true);return;}
    checkpoint();Object.assign(p,next);signalEdited();select(p.id);
    status('Saved '+kind+' on a native editable mesh. Undo/Redo and JSON export remain available.');
  };
  $m('AnatomyHeadApply').addEventListener('click',()=>apply('anatomyStudy',atelierAnatomyDefaults));
  $m('AnatomyEarApply').addEventListener('click',()=>apply('earStudy',atelierEarDefaults));
}
