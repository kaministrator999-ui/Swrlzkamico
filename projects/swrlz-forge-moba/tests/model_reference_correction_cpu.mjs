import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const root=new URL('../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root),'utf8');
const html=fs.readFileSync(process.env.SWYRL_REFERENCE_HTML||'dist/swrlz-forge-moba/index.html','utf8');
const model=JSON.parse(html.match(/const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n\/\/ §wyrl§ Engine Model Atelier v11.3/s)[1]).project.modelAtelier;
const previous=JSON.parse(read('scenes/model-atelier-festival-hd-v11-17.swyrl.json')).project.modelAtelier;
const reference=read('runtime/model_atelier_reference_v11_13.js'),leaf=reference.slice(reference.indexOf('function atelierReferenceLeaf('),reference.indexOf('function atelierValidateAssemblies('));
const from=html.indexOf('// Native HD finishes:'),to=html.indexOf('// §E v11.52: camera-plane-exact pixel brush sizing',from);
assert.ok(from>0&&to>from);const ctx=vm.createContext({THREE,console,model:()=>model,atelierSculptApply:(geometry,part)=>{assert.ok(!part?.sculptBrushes?.length&&!part?.sculptVertexEdits?.length,'Historical anatomy fixture must have no native sculpt edits');return geometry;}});
vm.runInContext(read('runtime/model_atelier_density_v11_16.js')+'\n'+leaf+'\n'+html.slice(from,to),ctx);
const byId=id=>model.parts.find(p=>p.id===id),oldId=id=>previous.parts.find(p=>p.id===id);
const maxKink=p=>Math.max(...p.path.slice(1,-1).map((v,i)=>{const a=new THREE.Vector3(...v).sub(new THREE.Vector3(...p.path[i])).normalize(),b=new THREE.Vector3(...p.path[i+2]).sub(new THREE.Vector3(...v)).normalize();return a.angleTo(b);}));
for(const side of ['left','right']){
 const id='atelier-v118-'+side+'-leg',p=byId(id),g=ctx.atelierHDGeometry(p),a=g.attributes.position;
 assert.ok(maxKink(p)<.10,'Neutral knee must not reverse abruptly');
 const curve=new THREE.CatmullRomCurve3(p.path.map(q=>new THREE.Vector3(...q)),false,'centripetal');
 let last=Infinity;for(let i=0;i<=256;i++){const q=curve.getPoint(i/256);assert.ok(q.y<last||i===0,'Leg folds back upward');last=q.y;}
 for(const key of ['position','normal'])for(const v of g.attributes[key].array)assert.ok(Number.isFinite(v));
 const plain=ctx.atelierHDGeometry({...p,legAnatomy:undefined}).attributes.position;
 assert.equal(a.count,plain.count,'Anatomy must retain sampling controls');
 const n=p.meshDensity.u,rings=p.meshDensity.v,posterior=[],anterior=[];
 for(let i=0;i<=n;i++){
  const back=i*(rings+1)+Math.round(rings*.75),front=i*(rings+1)+Math.round(rings*.25);
  posterior.push({y:plain.getY(back),extra:plain.getZ(back)-a.getZ(back)});
  anterior.push({y:plain.getY(front),inset:plain.getZ(front)-a.getZ(front)});
  if(curve.getPoint(i/n).y>=(p.path[2][1]+p.path[3][1])/2||i===n)for(let j=0;j<=rings;j++){
   const k=i*(rings+1)+j;assert.ok(new THREE.Vector3().fromBufferAttribute(a,k).distanceTo(new THREE.Vector3().fromBufferAttribute(plain,k))<1e-6,JSON.stringify({id,i,j,n,rings,center:curve.getPoint(i/n).toArray(),a:[a.getX(k),a.getY(k),a.getZ(k)],plain:[plain.getX(k),plain.getY(k),plain.getZ(k)]}));
  }
 }
 const peak=posterior.reduce((a,b)=>b.extra>a.extra?b:a),shin=anterior.reduce((a,b)=>b.inset>a.inset?b:a);
 assert.ok(peak.y>1.08&&peak.y<1.36&&peak.extra>.055,'Posterior calf must peak below the knee, above mid-shin');
 assert.ok(shin.inset>.008&&shin.inset<.02,'Front shin must stay restrained rather than inherit the calf bulge');
 assert.ok(posterior.filter(q=>q.y<.7).every(q=>q.extra<.006),'Calf must taper into the Achilles and fixed ankle');
 assert.ok(posterior.filter(q=>q.y>1.5).every(q=>q.extra<.008),'Calf must blend smoothly beneath the knee');
 console.log('REFERENCE_POSTERIOR_CALF_SHIN_AND_ACHILLES_PASS',side,peak,shin);
 for(const prefix of ['sock','shoe','heel','sole'])assert.deepEqual(byId(prefix+'-'+side),oldId(prefix+'-'+side),'Foot assembly moved during knee correction');
 assert.deepEqual(p.path[5],oldId(id).path[5],'Ankle must remain attached to its sock');
 console.log('REFERENCE_LEG_PROFILE_PASS',side,maxKink(oldId(id)),maxKink(p),a.count);
}
assert.ok(maxKink(oldId('atelier-v118-right-leg'))>.3,'Regression fixture must contain the reported knee kink');
for(const id of ['hair-cap','hair-bun--1','hair-bun-1']){
 const p=byId(id),g=ctx.atelierHDGeometry(p),a=g.attributes.position;
 assert.ok(a.count>1000);for(const key of ['position','normal','color'])for(const v of g.attributes[key].array)assert.ok(Number.isFinite(v),id+' invalid '+key);
 for(const n of g.index.array)assert.ok(n>=0&&n<a.count,id+' invalid triangle');
 if(p.hdFinish.style==='knot')for(let i=0;i<a.count;i++)assert.ok(Math.hypot(a.getX(i),a.getY(i))>.40,'Knotted wrap must retain its real opening');
 if(p.hdFinish.style==='crown'){const base=ctx.atelierDetailSphere(p);assert.notDeepEqual(Array.from(a.array),Array.from(base.attributes.position.array),'Crown grooves must alter real vertices');}
 const lighter=ctx.atelierHDGeometry({...p,meshDensity:{u:16,v:10}});assert.ok(lighter.index.count<g.index.count/2,'New finishes must respect the lighter native sampling preset');
 console.log('REFERENCE_HAIR_GEOMETRY_PASS',id,a.count,g.index.count/3);
}
const iris=byId('left-iris'),warm=ctx.atelierHDIris(iris),legacy=ctx.atelierHDIris({...iris,irisPigments:undefined});
assert.deepEqual(Array.from(warm.attributes.position.array),Array.from(legacy.attributes.position.array));
assert.notDeepEqual(Array.from(warm.attributes.color.array),Array.from(legacy.attributes.color.array),'Saved pigments must change generated iris colors');
const oldCtx=vm.createContext({THREE,console,model:()=>model});vm.runInContext(read('runtime/model_atelier_hd_v11_17.js'),oldCtx);
const original=oldCtx.atelierHDIris({...iris,irisPigments:undefined});assert.deepEqual(Array.from(original.attributes.color.array),Array.from(legacy.attributes.color.array),'Unannotated historical iris palette changed');
console.log('REFERENCE_SAVED_IRIS_COLORS_AND_HISTORICAL_DEFAULT_PASS');
const coral=byId('chest-coral'),flat=ctx.atelierHDCloth(coral),bulged=ctx.atelierHDCloth({...coral,panelCamber:.035});
assert.notDeepEqual(Array.from(flat.attributes.position.array),Array.from(bulged.attributes.position.array),'Fabric-panel curvature must change the actual cloth mesh');
assert.equal(byId('chest-gold').hdFinish.style,'skin');assert.equal(byId('chest-gold').path.length,33);assert.equal(byId('bodice-stitch-0').path.length,33);
console.log('REFERENCE_FABRIC_CURVATURE_AND_FITTED_BODICE_TRIM_PASS');
