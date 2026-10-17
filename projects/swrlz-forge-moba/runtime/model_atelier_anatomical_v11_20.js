// Anatomical study: continuous stylized skull and shaped auricles.
// Opt-in only. Older project parts without anatomyStudy/earStudy are unchanged.
// The control values are native scene data; there is no hidden renderer state.
const atelierAnatomyDefaults={jaw:.54,malar:.58,orbit:.57,nose:.65,chin:.50,temple:.42};
const atelierEarDefaults={helix:.64,concha:.58,lobe:.43};
const atelierAnatomyBell=(x,y,sx,sy)=>Math.exp(-((x/sx)**2+(y/sy)**2));
const atelierAnatomyClamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const atelierAnatomySmooth=(a,b,v)=>THREE.MathUtils.smoothstep(v,a,b);
function atelierAnatomicalHead(part){
  const f={...atelierAnatomyDefaults,...part.anatomyStudy};
  const u=part.meshDensity?.u??192,v=part.meshDensity?.v??128;
  const positions=[],colors=[],indices=[],uv=[],skin=new THREE.Color(part.color);
  const pink=new THREE.Color('#df8f93'),warm=new THREE.Color('#d39b90');
  const finish=part.portraitFinish||{chinLift:0,noseDefinition:0,warmth:0};
  // A continuous section-by-section skull: broad cranial vault, zygomatic
  // arches, narrowing mandibular body and non-pointed sculpted chin.
  // The section curves, not the part count, determine the anatomy.
  for(let iy=0;iy<=v;iy++){
    const t=iy/v,phi=t*Math.PI;
    const y0=Math.cos(phi),rad=Math.sin(phi);
    const mandibular=atelierAnatomySmooth(.02,.92,-y0);
    const cheekY=atelierAnatomyBell(0,y0+.18,1,.28);
    const jawWidth=1-.26*(part.jawTaper??.32)/.32*mandibular
      +.085*f.malar*cheekY-.036*f.temple*atelierAnatomyBell(0,y0-.68,1,.25);
    const depthRatio=1-.12*mandibular+.045*atelierAnatomyBell(0,y0-.48,1,.32);
    for(let ix=0;ix<=u;ix++){
      const a=ix/u*Math.PI*2;
      const cx=Math.cos(a),cz=Math.sin(a);
      let x=rad*cx*jawWidth;
      let y=y0+(finish.chinLift??0)*atelierAnatomySmooth(.18,1,-y0);
      let z=rad*cz*depthRatio;
      const face=atelierAnatomySmooth(.05,.8,cz);
      let blush=0,nostril=0;
      if(cz>0){
        const absX=Math.abs(x);
        const cheek=atelierAnatomyBell(absX-.48,y0+.17,.24,.22);
        const orbit=atelierAnatomyBell(absX-.44,y0-.03,.27,.23);
        const temple=atelierAnatomyBell(absX-.78,y0-.30,.23,.32);
        const bridge=atelierAnatomyBell(x,y0+.04,.12,.32);
        const nasalTip=atelierAnatomyBell(x,y0+.31,.12,.115);
        const alae=atelierAnatomyBell(absX-.15,y0+.34,.08,.068);
        const philtrum=atelierAnatomyBell(x,y0+.48,.07,.075);
        const mouth=atelierAnatomyBell(x,y0+.53,.30,.09);
        const chinPad=atelierAnatomyBell(x,y0+.74,.29,.13);
        const jawCorner=atelierAnatomyBell(absX-.52,y0+.56,.20,.26);
        z+=face*(.075*f.malar*cheek-.072*f.orbit*orbit
           -.014*f.temple*temple
           +(.032+.032*(finish.noseDefinition??0))*f.nose*bridge
           +(.085+.024*(finish.noseDefinition??0))*f.nose*nasalTip
           +.025*f.nose*alae
           -.016*philtrum+.015*mouth+.026*f.chin*chinPad
           +.014*f.jaw*jawCorner);
        // Preserve eyelid/eyebrow plane; color is stored per vertex and is
        // deterministic across native JSON export/import.
        blush=cheek*face*(.09+.16*(finish.warmth??0));
        nostril=face*f.nose*atelierAnatomyBell(absX-.095,y0+.37,.035,.026);
      }
      positions.push(x,y,z);
      uv.push(ix/u,1-t);
      const color=skin.clone().lerp(pink,atelierAnatomyClamp(blush))
        .lerp(warm,atelierAnatomyClamp(nostril*.35));
      colors.push(color.r,color.g,color.b);
      if(iy<v&&ix<u){
        const k=iy*(u+1)+ix,b=k+u+1;
        indices.push(k,k+1,b,k+1,b+1,b);
      }
    }
  }
  const g=atelierHDMesh(positions,colors,indices,uv);
  const normals=g.attributes.normal;
  for(let iy=0;iy<=v;iy++){
    const i=iy*(u+1),j=i+u;
    const n=new THREE.Vector3().fromBufferAttribute(normals,i)
      .add(new THREE.Vector3().fromBufferAttribute(normals,j)).normalize();
    normals.setXYZ(i,n.x,n.y,n.z);normals.setXYZ(j,n.x,n.y,n.z);
  }
  return g;
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
