// Refine the saved Astra design with the editor's welded volume tool.
// Traveling gear, ears, eyes, ruff and the complete comet tail stay intact.
function atelierRefineCourierProject(original=COMET_COURIER_PROJECT){
 const project=structuredClone(original),model=project.project.modelAtelier,parts=model.parts;
 const smooth=(a,b,k)=>{const h=Math.max(0,k-Math.abs(a-b))/k;return Math.min(a,b)-h*h*k*.25;};
 const ell=(x,y,z,c,r)=>{const v=[x-c[0],y-c[1],z-c[2]],a=Math.hypot(...v.map((n,i)=>n/r[i])),b=Math.hypot(...v.map((n,i)=>n/(r[i]*r[i])));return b?a*(a-1)/b:-Math.min(...r);};
 const fuse=(masses,k)=>(x,y,z)=>{let d=10;for(const [c,r] of masses)d=smooth(d,ell(x,y,z,c,r),k);return d;};
 const replace=(part,field,bounds,step,region)=>{part.kind='topologyMesh';part.position=[0,0,0];part.rotation=[0,0,0];part.scale=[1,1,1];delete part.loft;delete part.meshDensity;part.topologyMesh=atelierAnimalWeld(atelierAnimalSurface(field,bounds,step));
  // Close microscopic triangular holes left by the volume tool's area cutoff.
  const edges=new Map(),mesh=part.topologyMesh;for(let i=0;i<mesh.indices.length;i+=3){const t=mesh.indices.slice(i,i+3);for(let j=0;j<3;j++){const a=t[j],b=t[(j+1)%3],key=a<b?a+':'+b:b+':'+a;const edge=edges.get(key);if(edge)edge.count++;else edges.set(key,{a,b,count:1});}}
  const boundary=[...edges.values()].filter(e=>e.count===1);for(const e of boundary){if(e.used)continue;const f=boundary.find(f=>!f.used&&f.a===e.b),g=f&&boundary.find(g=>!g.used&&g.a===f.b&&g.b===e.a);if(f&&g){mesh.indices.push(e.b,e.a,f.b);e.used=f.used=g.used=true;}}
  part.organicSurface={species:'courier',region};return part;};
 const body=parts.find(p=>p.id==='model-seed');body.name='Astra · continuous ribcage, shoulders, tucked waist and haunches';
 const bodyField=fuse([[[0,1.38,-.12],[.46,.55,.75]],[[-.34,1.04,-.60],[.29,.43,.32]],[[.34,1.04,-.60],[.29,.43,.32]],[[-.28,1.55,.23],[.20,.36,.28]],[[.28,1.55,.23],[.20,.36,.28]],[[0,1.91,.22],[.29,.39,.30]]],.14);
 replace(body,(x,y,z)=>bodyField(x,y,z)+.025*Math.exp(-(((z+.15)/.28)**2+((y-1.03)/.25)**2)),[[-.72,.49,-1.04],[.72,2.35,.76]],.033,'body');
 const skull=parts.find(p=>p.name==='Fox · cranial planes');skull.name='Astra · sculpted brow, cheekbones and tapered jaw';
 const head=fuse([[[0,2.43,.44],[.43,.365,.365]],[[-.245,2.33,.60],[.19,.21,.23]],[[.245,2.33,.60],[.19,.21,.23]],[[0,2.20,.66],[.235,.12,.23]]],.07);
 replace(skull,(x,y,z)=>head(x,y,z)+.012*Math.exp(-(((Math.abs(x)-.25)/.10)**2+((y-2.46)/.085)**2+((z-.76)/.08)**2)),[[-.52,2.03,.015],[.52,2.86,.94]],.019,'face');
 const muzzle=parts.find(p=>p.name==='Fox · nasal bridge');muzzle.name='Astra · continuous tapered muzzle and upper lip';
 const muzzleField=fuse([[[0,2.33,.75],[.22,.17,.31]],[[-.105,2.27,.87],[.17,.115,.23]],[[.105,2.27,.87],[.17,.115,.23]]],.07);
 replace(muzzle,(x,y,z)=>muzzleField(x,y,z)+.008*Math.exp(-((x/.018)**2+((y-2.19)/.04)**2+((z-1.02)/.15)**2)),[[-.33,2.10,.38],[.33,2.54,1.14]],.017,'muzzle');
 const removed=new Set(parts.filter(p=>p.name.startsWith('Fox · haunch')||p.name.startsWith('Fox · muzzle lobe')).map(p=>p.id));
 model.parts=parts.filter(p=>!removed.has(p.id));for(const group of model.meshGroups)group.members=group.members.filter(id=>!removed.has(id));
 for(const part of model.parts)if(/^Fox · (foreleg|hock)/.test(part.name)){part.meshDensity={u:64,v:40};part.name=part.name.replace('Fox ·','Astra · sculpted');}
 model.name='Astra · Comet Courier · Organic';model.editedAt='local';project.engine='§wyrl§ Engine · Maker v11.88';Object.assign(project.project,{name:model.name,canonicalId:'wolf-model',template:'wolf-model'});return project;
}
const atelierOriginalWolfLoader=loadAnimalProject;
loadAnimalProject=async function(species,force=false,rebuild=false){
 if(species!=='wolf')return atelierOriginalWolfLoader(species,force,rebuild);
 if(dirty&&!force&&!confirm('Open Astra and discard unsaved changes?'))return false;
 const ticket=++atelierAnimalLoading;toast('Opening Astra · Comet Courier…');
 const response=await fetch('scenes/model-atelier-original-wolf-organic-v11-88.swyrl.json');if(!response.ok)throw Error('Astra starter could not load.');
 const data=rebuild?atelierRefineCourierProject():await response.json();if(ticket!==atelierAnimalLoading)return false;
 ModelAtelier.close();loadProject(data,{workspaceLocal:true});initializeHistory('Opened original Astra organic refinement');markSaved();document.getElementById('projectHub')?.classList.remove('show');ModelAtelier.syncProject();ModelAtelier.open();const panel=document.getElementById('modelAtelierPanel'),studio=document.getElementById('modelAtelierCourierStudio');panel.classList.add('courier-studio');studio.hidden=false;studio.textContent='Edit model';studio.setAttribute('aria-pressed','true');requestAnimationFrame(()=>requestAnimationFrame(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('three')));return true;
};
