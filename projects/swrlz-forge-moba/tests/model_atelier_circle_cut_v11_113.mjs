// §E v11.113: inspect actual geometry for reusable hand-placed circular cuts.
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from 'three';
const root='projects/swrlz-forge-moba/runtime/';
const js=fs.readFileSync(root+'model_atelier_precision_circle_v11_113.js','utf8');
const audit=fs.readFileSync(root+'model_atelier_topology_audit_v11_44.js','utf8');
const ctx={THREE,console,checkPart:()=>true};
vm.createContext(ctx);
vm.runInContext(audit+'\n'+js.split('function atelierPrecisionCircleInstall(){')[0],ctx);
ctx.atelierTopologyValid=p=>{
 const d=p.topologyMesh;
 return p.kind==='topologyMesh'&&d&&
  d.positions.length%3===0&&d.positions.length/3<=9000&&
  d.indices.length%3===0&&d.indices.length/3<=16000&&
  d.uvs.length===2*d.positions.length/3&&
  d.positions.every(Number.isFinite)&&d.uvs.every(Number.isFinite)&&
  d.indices.every(i=>Number.isInteger(i)&&i>=0&&i<d.positions.length/3);
};
function check(name,shape,axis,holes,radius){
 const made=ctx.atelierPrecisionCircleBuild(radius,[0,0,0],axis,holes,shape);
 if(!made.ok)throw Error(name+': '+made.reason);
 const a=ctx.atelierTopologyAudit(made.data);
 const info={scenario:name,vertices:made.vertices,triangles:made.triangles,boundary:a.boundaryEdges,nonmanifold:a.nonManifoldEdges,winding:a.oppositeWindingErrors,degenerates:a.zeroAreaFaces};
 console.log('PRECISION_CUT_MESH',JSON.stringify(info));
 if(!a.ok||a.boundaryEdges||a.nonManifoldEdges||a.oppositeWindingErrors||a.zeroAreaFaces)
  throw Error('Invalid manifold solid: '+JSON.stringify(info));
 if(!ctx.atelierBorePlanValid({kind:'topologyMesh',roundHolePlan:{
  ...shape,radius,center:[0,0,0],axis,holes}}))throw Error(name+': saved plan fails native validation');
 const [p0,p1]=[-.5,.5];
 if(shape.surface==='box'){
  for(let i=0;i<made.data.positions.length;i+=3){
   for(let k=0;k<3;k++)if(made.data.positions[i+k]<p0-1e-5||made.data.positions[i+k]>p1+1e-5)
    throw Error('Box extended outside its six original faces');
  }
 }
 if(shape.surface==='cylinder'){
  for(let i=0;i<made.data.positions.length;i+=3){
   const x=made.data.positions[i],y=made.data.positions[i+1],z=made.data.positions[i+2];
   if(Math.abs(y)>.50001||Math.hypot(x,z)>1.00001)throw Error('Cylinder exceeded original envelope');
  }
 }
 return made;
}
const H=(x,y,r=.065,depth=.30,cap=.8)=>({x,y,r,depth,cap});
const plane={surface:'box',halfU:.5,halfV:.5,halfDepth:.5};
const cyl={surface:'cylinder',halfU:.5,halfV:.5,halfDepth:.5};
const sph={surface:'sphere'};
check('sphere one handpicked',sph,[0,0,1],[H(0,0,.12,.35,.8)],1);
check('sphere three manual',sph,[0,0,1],[H(-.25,.22,.12,.35),H(.25,.22,.12,.35),H(0,-.35,.14,.38)],1);
check('box one centered flat-bottom',plane,[0,0,1],[H(0,0,.08,.18,0)],.5);
check('box three independently placed',plane,[0,0,1],[H(-.23,.17),H(.20,.18),H(0,-.20)],.5);
const six=[H(-.30,-.25,.05),H(0,-.25,.05),H(.30,-.25,.05),H(-.30,.25,.05),H(0,.25,.05),H(.30,.25,.05)];
check('box six manual sockets',plane,[0,0,1],six,.5);
check('cylinder top recessed cap',cyl,[0,1,0],[H(0,0,.17,.32,.9)],1);
check('cylinder four endcap vents',cyl,[0,1,0],[H(-.32,-.30,.11),H(.32,-.30,.11),H(-.32,.30,.11),H(.32,.30,.11)],1);
const fail=(name,shape,axis,holes,radius)=>{let r=ctx.atelierPrecisionCircleBuild(radius,[0,0,0],axis,holes,shape);if(r.ok)throw Error('Invalid geometry accepted: '+name);};
fail('overlapping box',plane,[0,0,1],[H(0,0,.10),H(.03,.02,.10)],.5);
fail('cut crosses face edge',plane,[0,0,1],[H(.45,0,.10)],.5);
fail('cut through solid',plane,[0,0,1],[H(0,0,.10,1.3)],.5);
fail('unsupported arbitrary imported mesh',{surface:'topologyMesh'},[0,0,1],[H(0,0)],1);
const saved={...plane,radius:.5,center:[0,0,0],axis:[0,0,1],holes:six};
const changed=JSON.parse(JSON.stringify(saved));changed.holes[2].r=.055;
if(!ctx.atelierBorePlanValid({kind:'topologyMesh',roundHolePlan:changed})||
 !ctx.atelierPrecisionCircleBuild(.5,[0,0,0],[0,0,1],changed.holes,changed).ok)
 throw Error('Cannot re-edit an individual saved feature');
if(!js.includes("surface==='box'")||!js.includes("surface==='cylinder'")||!js.includes("el('Relocate').checked")||js.includes("3 holes · bowling ball"))
 throw Error('UI source does not expose hand controlled generality');
console.log('SE_V11113_MANUAL_CIRCLE_CUT_GEOMETRY_PASS');
