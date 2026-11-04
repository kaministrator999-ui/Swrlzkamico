// §E v11.252 · inserted inside the existing ModelAtelier closure.
// Editor-only high-triangle specimen; never appended to model().parts.
let se252StressMesh=null;
let se252StressTriangles=0;
function se252ModelStop(){
 if(se252StressMesh){
  se252StressMesh.removeFromParent();
  se252StressMesh.geometry?.dispose();
  se252StressMesh.material?.dispose();
  se252StressMesh=null;
 }
 se252StressTriangles=0;
 return {active:false,triangles:0};
}
function se252ModelApply(requested){
 if(!panel||panel.hidden||!world||!renderer)return {error:'Open Model Atelier before running a model test.'};
 const target=Math.round(Number(requested));
 if(!Number.isSafeInteger(target)||target<100||target>1000000)return {error:'Choose 100–1,000,000 model triangles.'};
 // Indexed SphereGeometry produces 2 * width * (height - 1) triangles.
 const width=Math.max(8,Math.floor(Math.sqrt(target/2)));
 const height=Math.max(6,Math.round(target/(2*width))+1);
 let geometry=null,material=null,mesh=null;
 try{
  geometry=new THREE.SphereGeometry(1.72,width,height);
  material=new THREE.MeshNormalMaterial({side:THREE.FrontSide});
  mesh=new THREE.Mesh(geometry,material);
  mesh.name='Diagnostic high-poly specimen (temporary, unsaved)';
  mesh.userData.se252Diagnostic=true;
  mesh.position.set(0,2.35,0);
  // Only replace the former diagnostic after the new allocation succeeds.
  se252ModelStop();
  world.add(mesh);
  se252StressMesh=mesh;
  se252StressTriangles=Math.floor(geometry.getIndex().count/3);
  return {active:true,triangles:se252StressTriangles,
   vertices:geometry.getAttribute('position').count,
   calls:renderer.info?.render?.calls||0};
 }catch(error){
  if(mesh)mesh.removeFromParent();
  geometry?.dispose();material?.dispose();
  return {error:'Model test allocation failed: '+String(error?.message||error).slice(0,90)};
 }
}
window.SWYRL_ENGINE_MODEL_STRESS_252=Object.freeze({
 apply:se252ModelApply,stop:se252ModelStop,
 inspect:()=>({active:!!se252StressMesh&&!!se252StressMesh.parent,
  triangles:se252StressTriangles,
  calls:renderer?.info?.render?.calls||0,
  drawnTriangles:renderer?.info?.render?.triangles||0,
  open:!!panel&&!panel.hidden})
});
