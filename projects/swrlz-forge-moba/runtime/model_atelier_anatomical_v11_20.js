// Anatomical study: continuous stylized skull and shaped auricles.
// Opt-in only. Older project parts without anatomyStudy/earStudy are unchanged.
// The control values are native scene data; there is no hidden renderer state.
const atelierAnatomyDefaults={jaw:.54,malar:.58,orbit:.57,nose:.65,chin:.50,temple:.42};
const atelierEarDefaults={helix:.64,concha:.58,lobe:.43};
const atelierAnatomyBell=(x,y,sx,sy)=>Math.exp(-((x/sx)**2+(y/sy)**2));
const atelierAnatomyClamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const atelierAnatomySmooth=(a,b,v)=>THREE.MathUtils.smoothstep(v,a,b);
// Front/side multi-view fitting: y is normalized head height, x = outer
// half-width from the FRONT, z = nose/face depth seen from the SIDE.
// Ratios are hand-estimated from the owner-provided cyan/coral turnaround
// (not a calibrated depth scan). Multiple views constrain one shared mesh.
function atelierReferenceSample(points,y){
  if(y<=points[0][0])return points[0][1];
  for(let i=1;i<points.length;i++)if(y<=points[i][0]){
    const a=points[i-1],b=points[i],t=(y-a[0])/(b[0]-a[0]);
    return THREE.MathUtils.lerp(a[1],b[1],t*t*(3-2*t));
  }
  return points[points.length-1][1];
}
function atelierReferenceFitValid(f){
  if(f===undefined)return true;
  if(!f||typeof f!=='object'||Array.isArray(f)
      ||Object.keys(f).sort().join('|')!=='front|profile|strength')return false;
  if(!Number.isFinite(f.strength)||f.strength<0||f.strength>1)return false;
  for(const [key,max] of [['front',1.25],['profile',1.4]]){
    const rows=f[key];
    if(!Array.isArray(rows)||rows.length<5||rows.length>24)return false;
    let prev=-2;
    for(const pt of rows){
      if(!Array.isArray(pt)||pt.length!==2||!pt.every(Number.isFinite)
          ||pt[0]<=prev||pt[0]<-1||pt[0]>1||pt[1]<=0||pt[1]>max)return false;
      prev=pt[0];
    }
    if(rows[0][0]>-.95||rows[rows.length-1][0]<.95)return false;
  }
  return true;
}
// Use v11.19 sculpt as a vertex/topology starting surface, NOT as a shape
// constraint: each latitude's front width is truly remapped, rear vault depth
// is compressed and the forward face follows the side view projection target.
// Existing editability, per-vertex colors, UVs and live morph controls remain.
function atelierAnatomicalHead(part){
  const f={...atelierAnatomyDefaults,...part.anatomyStudy},fit=part.referenceFit;
  const original=atelierPortraitFinish({...part,anatomyStudy:undefined,referenceFit:undefined});
  const pos=original.attributes.position,col=original.attributes.color;
  const bell=atelierAnatomyBell,smooth=atelierAnatomySmooth;
  const blush=new THREE.Color('#df8f93'),tone=new THREE.Color();
  const base={jaw:.5,malar:.5,orbit:.5,nose:.5,chin:.5,temple:.5};
  const [jaw,malar,orbit,nose,chin,temple]=Object.keys(base).map(k=>(f[k]-base[k])*2);
  for(let i=0;i<pos.count;i++){
    let x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i);
    if(fit&&fit.strength>0){
      // The owner's OBJ is a layered Blender character: distinct front
      // facial surfaces and rear volumes, rather than one uniformly round
      // skull. Reconstruct that *principle*, not the unrelated OBJ likeness.
      // The cyan/coral turnaround determines these FRONT outline sections.
      const originalWidth=Math.sqrt(Math.max(.000001,1-y*y))
        *(1-(part.jawTaper??.32)*smooth(.12,1,-y));
      const targetWidth=atelierReferenceSample(fit.front,y);
      const ratio=atelierAnatomyClamp(targetWidth/Math.max(.028,originalWidth),.48,1.14);
      const poleFade=smooth(-.997,-.83,y)*(1-smooth(.83,.997,y));
      const malarBand=bell(Math.abs(x)-.70,y+.15,.27,.22);
      // Full circumferential taper: a shaped jaw/sides/back, never just
      // squeezing the visible front vertices into a pasted-on face.
      x*=1+(ratio-1)*fit.strength*poleFade;
      x*=1+.018*fit.strength*malarBand;
      if(z<0){
        // Compress the occiput across the rear hemisphere. This targets the
        // round ball silhouette seen in the owner's mobile side screenshots.
        // Fade at z=0 to preserve front/back seam and ear attachment.
        const back=smooth(.04,.70,-z);
        const vault=bell(0,y-.05,1,.68);
        z*=1-fit.strength*back*(.27+.125*vault);
      }else{
        const frontal=smooth(.08,.74,z),absX=Math.abs(x);
        // The cheek, eye socket, nose and mouth must form connected surface
        // planes. Side-depth samples constrain the centerline projection,
        // while neighboring zones transition smoothly across the cranium.
        const profileTarget=atelierReferenceSample(fit.profile,y);
        const desired=atelierAnatomyClamp(profileTarget-z,-.045,.235);
        const midline=bell(x,y+.22,.235,.43);
        z+=fit.strength*frontal*midline*desired;
        const cheek=bell(absX-.49,y+.18,.22,.24);
        const orbit=bell(absX-.43,y-.045,.235,.155);
        const cheekToJaw=bell(absX-.60,y+.53,.27,.22);
        // Soft zygomatic prominence with actual orbital recession.
        z+=fit.strength*frontal*(.048*cheek-.056*orbit-.030*cheekToJaw);
        // Stylized continuous nasal anatomy and lip/chin plane. A broad
        // glabellar root blends to a narrow bridge, distinct rounded tip,
        // subtle two-sided alae, philtrum and soft labiomental indentation.
        z+=fit.strength*frontal*(
          .022*bell(x,y-.065,.17,.18)
          +.027*bell(x,y+.135,.102,.25)
          +.054*bell(x,y+.318,.098,.078)
          +.018*bell(absX-.145,y+.35,.076,.062)
          -.009*bell(absX-.086,y+.400,.043,.029)
          +.023*bell(x,y+.465,.20,.068)
          -.031*bell(x,y+.655,.28,.095)
          +.032*bell(x,y+.815,.265,.12)
        );
      }
    }
    const low=smooth(.16,.89,-y);
    x*=1-.045*jaw*low+.026*malar*bell(Math.abs(x)-.54,y+.12,.28,.24);
    if(z>0){
      const front=smooth(.12,.72,z),absX=Math.abs(x);
      const cheeks=bell(absX-.47,y+.17,.24,.23),sockets=bell(absX-.43,y-.095,.23,.18);
      const bridge=bell(x,y+.105,.105,.27),tip=bell(x,y+.31,.112,.09);
      const wings=bell(absX-.14,y+.32,.068,.055);
      const chinPlane=bell(x,y+.74,.31,.15),jawPlane=bell(absX-.53,y+.56,.23,.23);
      const temporal=bell(absX-.78,y-.26,.20,.25);
      z+=front*(.027*malar*cheeks-.025*orbit*sockets
        +nose*(.020*bridge+.041*tip+.010*wings)
        +.014*chin*chinPlane+.013*jaw*jawPlane-.010*temple*temporal);
      const color=tone.setRGB(col.getX(i),col.getY(i),col.getZ(i));
      color.lerp(blush,atelierAnatomyClamp((.07*Math.max(0,malar)+.055*(fit?.strength??0))*cheeks*front));
      col.setXYZ(i,color.r,color.g,color.b);
    }
    pos.setXYZ(i,x,y,z);
  }
  original.computeVertexNormals();original.computeBoundingSphere();
  const normals=original.attributes.normal,u=part.meshDensity?.u??192,v=part.meshDensity?.v??128;
  if(pos.count===(u+1)*(v+1))for(let row=0;row<=v;row++){
    const a=row*(u+1),b=a+u;
    const n=new THREE.Vector3().fromBufferAttribute(normals,a)
      .add(new THREE.Vector3().fromBufferAttribute(normals,b)).normalize();
    normals.setXYZ(a,n.x,n.y,n.z);normals.setXYZ(b,n.x,n.y,n.z);
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
  if(!atelierReferenceFitValid(p.referenceFit))return false;
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
