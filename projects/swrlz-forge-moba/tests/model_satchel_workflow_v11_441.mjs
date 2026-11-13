// Real native Draw/Thicken and mesh-kernel candidates, not a bag generator.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
assert(process.argv[2],'Pass installed Three r169 ESM');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const read=n=>fs.readFileSync(path.join(ROOT,'runtime',n),'utf8'),clone=structuredClone;
const sandbox=vm.createContext({THREE,window:{},console});
vm.runInContext(read('model_mesh_operations_v11_430.js')+'\nthis.ops=se430MeshOps;\n'+read('se436_satchel_cavity.js')+'\n'+read('model_satchel_workflow_v11_441.js'),sandbox);
const ops=sandbox.ops,check=sandbox.window.SWYRL_E_SATCHEL_WORKFLOW_441;
// Reuse the existing native surface/editor fixture for actual Draw,
// extrusion and Undo. Primitive sphere dimensions are checked separately
// against the real native geometry factory below, not that fixture's sphere.
const fixtureSource=fs.readFileSync(path.join(ROOT,'tests/model_vr_sculpt_draw_v11_350.mjs'),'utf8');
const a=fixtureSource.indexOf('const source=name=>'),b=fixtureSource.indexOf('const positions=f=>',a);
assert(a>=0&&b>a);const fixtures=vm.createContext({assert,fs,path,vm,THREE,ROOT,console});
vm.runInContext(fixtureSource.slice(a,b)+'\nthis.make=fixture;',fixtures);
function draw(points,depth,id){
 const f=fixtures.make();assert.equal(f.api.drawBegin({normal:[0,0,1],name:id}).ok,true);
 for(const point of points)assert.equal(f.api.drawUpdate(point).ok,true);
 const created=f.api.drawEnd();assert.equal(created.ok,true,created.reason);
 const initial=clone(f.document());assert.equal(f.api.extrudeBegin(created.id).ok,true);
 assert.equal(f.api.extrudeUpdate(depth).ok,true);assert.deepEqual(clone(f.document()),initial,'Thickness preview is uncommitted');
 assert.equal(f.api.extrudeEnd(true).changed,true);const part=clone(f.document().parts.find(p=>p.id===created.id));part.id=id;
 part.material='matte';part.color='#916b48';return part;
}
function body(){
 const g=new THREE.BoxGeometry(1,1,1);const d=ops.convert(g);g.dispose();assert.equal(d.ok,true);
 const top=Array.from({length:d.data.indices.length/3},(_,i)=>i).find(f=>{
  const [a,b,c]=d.data.indices.slice(f*3,f*3+3).map(i=>new THREE.Vector3(...d.data.positions.slice(i*3,i*3+3)));
  return b.sub(a).cross(c.sub(a)).normalize().y>.99;
 });
 const region=ops.region(d.data,[top],{expand:true}),rim=ops.inset(d.data,region.triangleIds,{fraction:.18}),cavity=ops.extrude(rim.data,rim.selectedFaces,{depth:-.75});
 assert.equal(cavity.ok,true,cavity.reason);
 return {id:'model-seed',name:'Practice body',kind:'topologyMesh',position:[0,1.5,0],rotation:[0,0,0],scale:[1.4,1,.65],material:'matte',color:'#916b48',topologyMesh:clone(cavity.data)};
}
const flapPoints=[[-.65,1.95,.36],[.65,1.95,.36],[.57,1.55,.36],[0,1.43,.36],[-.57,1.55,.36]];
const strapPoints=[[-.72,1.65,.32],[-.72,2.80,.32],[-.50,3.05,.32],[.50,3.05,.32],[.72,2.80,.32],[.72,1.65,.32],[.56,1.65,.32],[.56,2.73,.32],[.43,2.90,.32],[-.43,2.90,.32],[-.56,2.73,.32],[-.56,1.65,.32]];
const claspPoints=[[-.10,1.68,.405],[0,1.79,.405],[.10,1.68,.405],[0,1.57,.405]];
const model=[body(),draw(flapPoints,.04,'flap'),draw(strapPoints,.035,'strap'),draw(claspPoints,.03,'clasp')];
const primitiveSource=read('model_atelier.js').match(/  function geometry\(part\)\{[\s\S]*?\n  \}/)?.[0];
assert.ok(primitiveSource,'Use the actual native primitive geometry factory');
const primitiveContext=vm.createContext({THREE});
vm.runInContext(primitiveSource+'\nthis.nativeGeometry=geometry;',primitiveContext);
function sphereClasp(radius,z){
 return {id:'sphere-clasp',kind:'sphere',name:'Small clasp',position:[0,1.68,z],rotation:[0,0,0],scale:[radius,radius,radius],material:'matte',color:'#c9a56c'};
}
function nativeSphereBounds(part){
 const geometry=primitiveContext.nativeGeometry(part);
 geometry.applyMatrix4(new THREE.Matrix4().compose(new THREE.Vector3(...part.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)),new THREE.Vector3(...part.scale)));
 geometry.computeBoundingBox();const box=geometry.boundingBox.clone();geometry.dispose();return box;
}
let groups=0;
{
 const before=JSON.stringify(model),r=check.inspect(model);
 for(const stage of ['body','flap','strap','clasp'])assert.equal(r[stage].ok,true,stage+': '+r[stage].message);
 assert.equal(r.clasp.partId,'clasp');assert.equal(r.materials.ok,false,'Metal belongs to the later materials step');
 assert.equal(JSON.stringify(model),before,'Read-only inspection must preserve every descriptor');assert.equal(r.visualReviewRequired,true);groups++;
}
{
 const p=clone(model);p[3].material='metal';const r=check.inspect(p);assert.equal(r.ok,true,JSON.stringify(r));assert.equal(r.materials.ok,true);groups++;
}
{
 const p=clone(model);p[3]=sphereClasp(.08,.48);const before=JSON.stringify(p),native=nativeSphereBounds(p[3]),r=check.inspect(p);
 assert.equal(r.clasp.ok,true,r.clasp.message);assert.equal(r.clasp.partId,p[3].id);
 for(const bound of ['min','max'])for(let axis=0;axis<3;axis++)assert.ok(Math.abs(r.clasp.bounds[bound][axis]-native[bound].getComponent(axis))<1e-6,'Recognized sphere bounds must match actual native radius-1 geometry');
 assert.ok(Math.abs(native.min.z-.40)<1e-6,'The actual sphere back contacts the thickened flap front');
 assert.equal(JSON.stringify(p),before,'Sphere inspection preserves the ordinary saved descriptor');
 p[3]=sphereClasp(.02,.42);assert.equal(check.inspect(p).clasp.ok,true,'A genuinely small native sphere clasp must not be measured at half size and fail the lower bound');groups++;
}
{
 const p=clone(model);p[3]=sphereClasp(.24,.46);const native=nativeSphereBounds(p[3]);
 assert.ok(native.getSize(new THREE.Vector3()).y>.4,'This real sphere is oversized for the clasp');
 assert.equal(check.inspect(p).clasp.ok,false,'An oversized native sphere must not pass by being measured at half size');groups++;
}
{
 const p=clone(model);p[3]=sphereClasp(.06,.60);const native=nativeSphereBounds(p[3]);
 assert.ok(native.min.z>.53,'The actual sphere floats clearly beyond the flap front');
 assert.equal(check.inspect(p).clasp.ok,false,'A floating native sphere clasp must not complete the fitting step');groups++;
}
{
 const r=check.inspect([model[0]]);assert.equal(r.body.ok,true);assert.equal(r.flap.ok,false);assert.equal(r.strap.ok,false);assert.equal(r.clasp.ok,false,'The body must not count as any separate component');groups++;
}
{
 const p=clone(model),plate=draw([[-.72,1.65,.32],[-.72,3.05,.32],[.72,3.05,.32],[.72,1.65,.32]],.035,'filled-plate');
 p[2]=plate;assert.equal(check.inspect(p).strap.ok,false,'A filled rectangle must not qualify as a U-shaped strap, including a sample on its triangulation diagonal');groups++;
}
{
 const p=clone(model);p[2].position[2]+=2;assert.equal(check.inspect(p).strap.ok,false,'A floating arch far from the bag is not attached');
 const f=clone(model);f[1].position[2]+=2;assert.equal(check.inspect(f).flap.ok,false,'A floating flap must not pass');groups++;
}
{
 const p=clone(model);p[2].topologyMesh.indices=p[2].topologyMesh.indices.slice(3);assert.equal(check.inspect(p).strap.ok,false,'An open strap surface must gain native thickness');
 const f=clone(model);f[1].topologyMesh.indices[0]=999999;assert.equal(check.inspect(f).flap.ok,false,'Malformed topology must not pass');groups++;
}
{
 const p=clone(model),turn=new THREE.Matrix4().compose(new THREE.Vector3(2,-.3,1),new THREE.Quaternion().setFromEuler(new THREE.Euler(.25,.65,-.15)),new THREE.Vector3(1.25,1.25,1.25));
 for(const part of p){
  const m=new THREE.Matrix4().compose(new THREE.Vector3(...part.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)),new THREE.Vector3(...part.scale));
  const pos=new THREE.Vector3(),q=new THREE.Quaternion(),scale=new THREE.Vector3();turn.clone().multiply(m).decompose(pos,q,scale);
  part.position=pos.toArray();part.rotation=new THREE.Euler().setFromQuaternion(q).toArray().slice(0,3);part.scale=scale.toArray();
 }
 assert.equal(check.inspect(p).clasp.ok,true);assert.equal(check.inspect(p).flap.ok,true);assert.equal(check.inspect(p).strap.ok,true,'Common translation/rotation/uniform scaling must preserve body-relative recognition');groups++;
}
{
 const p=clone(model);p[0].scale[0]=-1;assert.equal(check.inspect(p,{allowLegacy:false}).body.ok,false);
 const duplicate=clone(model);duplicate[1].id=duplicate[0].id;assert.equal(check.inspect(duplicate).ok,false);assert.match(check.inspect(duplicate).message,/unique/);groups++;
}
{
 const p=clone(model);p[0].topologyMesh=clone(ops.convert(new THREE.BoxGeometry(1,1,1)).data);
 assert.equal(check.inspect(p,{bodyPartId:'model-seed',allowLegacy:false}).body.ok,false,'An explicit body ID cannot bypass a real cavity');groups++;
}
{
 const box=(id,position,scale,rotation=[0,0,0])=>({id,kind:'box',name:id,position,scale,rotation,color:'#916b48',material:'matte'});
 const old=[box('floor',[0,1.09,0],[1.4,.10,.65]),box('front',[0,1.52,.30],[1.4,.76,.07]),box('back',[0,1.52,-.30],[1.4,.76,.07]),box('left',[-.66,1.52,0],[.07,.76,.54]),box('right',[.66,1.52,0],[.07,.76,.54]),box('old-flap',[0,1.99,.22],[1.35,.07,.47],[-.28,0,0]),box('old-left',[-.66,2.37,.1],[.08,.98,.06]),box('old-right',[.66,2.37,.1],[.08,.98,.06]),box('old-top',[0,2.84,.1],[1.32,.08,.06]),box('old-clasp',[0,1.83,.40],[.2,.16,.07])];
 const r=check.inspect(old);assert.equal(r.body.ok,true,JSON.stringify(r));assert.equal(r.body.legacy,true);assert.equal(r.flap.ok,true);assert.equal(r.strap.ok,true);assert.equal(r.clasp.ok,true);assert.equal(check.inspect(old,{allowLegacy:false}).body.ok,false);groups++;
}
{
 const p=clone(model);p[3].material='metal';p[1].material='metal';assert.equal(check.inspect(p).materials.ok,false,'A metal clasp alone does not prove leather on the actual flap');groups++;
}
{
 assert.equal(check.inspect(null).ok,false);assert.equal(check.inspect(model,null).clasp.ok,true);
 const p=clone(model);p[3].position[2]+=.22;assert.equal(check.inspect(p).clasp.ok,false,'A floating clasp well in front of the flap must not pass');groups++;
}
{
 const g=new THREE.SphereGeometry(.5,64,64),d=ops.convert(g);g.dispose();assert.equal(d.ok,true);
 const p=clone(model);for(let i=0;i<11;i++)p.push({...clone(model[0]),id:'dense-'+i,topologyMesh:clone(d.data)});
 const r=check.inspect(p);assert.equal(r.ok,false);assert.equal(r.budget.exceeded,true);assert.match(r.message,/inspection budget/);groups++;
}
{
 const p=clone(model);p[0].sculptVertexEdits=[{indices:[0],delta:[.1,0,0],resolution:[0,0]}];
 const r=check.inspect(p,{allowLegacy:false});assert.equal(r.body.ok,false);assert.ok(r.manualReviewParts.includes('model-seed'));assert.match(r.body.message,/deformation layers/);groups++;
}
// The lesson config/navigation must never construct or apply learner geometry.
const lessonState={active:true,current:1},actions=[],highlights=[];
sandbox.currentProject={se412Tutorial:'satchel-001',se441TutorialWorkflow:'one-body-v1',modelAtelier:{parts:clone(model)}};
sandbox.window.SWYRL_ENGINE_TUTORIAL_412={status:()=>lessonState};
sandbox.se340XR={session:true,se430Manual:false,page:'tools',paletteVisible:true,helpVisible:false,se413Quest:{coachMode:'guide'},ui:{highlightTutorialAction:action=>highlights.push(action)}};
let nativeSelection={selection:{partId:'model-seed',faceIds:[]},convert:{available:true},preview:{active:false}};
sandbox.ModelAtelier={workshop:{inspect:()=>nativeSelection,convert:()=>{throw Error('SHOW must not convert geometry');},apply:()=>{throw Error('SHOW must not Apply geometry');}}};
sandbox.se340ModelXRAction=action=>{actions.push(action);if(action==='manual-mesh')sandbox.se340XR.se430Manual=true;};
sandbox.se340SyncUI=()=>{};sandbox.se340Publish=()=>{};
vm.runInContext(read('model_satchel_lesson_v11_441.js'),sandbox);
const lesson=sandbox.window.SWYRL_E_SATCHEL_LESSON_441;
{
 assert.equal(lesson.steps.length,7);for(const step of lesson.steps){assert.ok(step.vrTask.length<=175);assert.ok(step.vrHint.length<=125);}
 assert.ok(lesson.steps[1].vrTask.includes('Inset .20'));assert.ok(lesson.steps[1].vrTask.includes('Extrude −.75'));
 assert.ok(lesson.steps[3].vrTask.includes('OUTER U'));assert.ok(lesson.steps[3].vrTask.includes('INNER U'));groups++;
}
{
 lessonState.current=1;assert.equal(lesson.amountFor('extrude'),-.75);assert.equal(lesson.amountFor('inset'),null);
 lessonState.current=2;assert.equal(lesson.amountFor('extrude'),null);assert.equal(lesson.drawName(),'Satchel flap');
 lessonState.current=3;assert.equal(lesson.drawName(),'Satchel strap');lessonState.current=4;assert.equal(lesson.drawName(),'Satchel clasp');
 lessonState.active=false;assert.equal(lesson.drawName(),'VR outline');assert.equal(lesson.amountFor('extrude'),null);lessonState.active=true;groups++;
}
{
 const p=clone(model);assert.equal(lesson.verify(4,p).ok,true,'Clasp geometry must precede metal');assert.equal(lesson.verify(5,p).ok,false);
 p[3].material='metal';assert.equal(lesson.verify(5,p).ok,true);assert.equal(lesson.verify(6,p).ok,null,'Geometry/counts cannot auto-complete saving');assert.match(lesson.verify(6,p).message,/reopen My Projects/);
 assert.equal(lesson.verify(3,[p[0]]).ok,false);groups++;
}
{
 lessonState.current=1;const p=clone(model[0]);delete p.topologyMesh;p.kind='box';sandbox.currentProject.modelAtelier.parts=[p];const before=JSON.stringify(sandbox.currentProject);
 nativeSelection={selection:{partId:'model-seed',faceIds:[]},convert:{available:true},preview:{active:false}};sandbox.se340XR.se430Manual=false;actions.length=0;
 const response=lesson.showMe(1,true);assert.equal(response.action,'manual-convert');assert.equal(sandbox.se340XR.page,'manual-mesh');assert.deepEqual(actions,['manual-mesh']);assert.equal(JSON.stringify(sandbox.currentProject),before);groups++;
}
{
 const before=JSON.stringify(sandbox.currentProject);nativeSelection={selection:{partId:'model-seed',faceIds:[]},convert:{available:false},preview:{active:false}};
 actions.length=0;assert.equal(lesson.showMe(1,true).action,'manual-pick');assert.equal(actions.length,0);
 nativeSelection.preview.active=true;assert.equal(lesson.showMe(1,true).action,'manual-apply');assert.equal(sandbox.se340XR.page,'manual-operation');assert.equal(JSON.stringify(sandbox.currentProject),before);groups++;
}
{
 sandbox.currentProject.modelAtelier.parts=clone(model);nativeSelection.preview.active=false;nativeSelection.selection.faceIds=[2,3];actions.length=0;
 const before=JSON.stringify(sandbox.currentProject);assert.equal(lesson.showMe(1,true).action,'focus');assert.deepEqual(actions,['tools']);assert.equal(JSON.stringify(sandbox.currentProject),before,'Completed cavity must not receive another extrusion from SHOW');
 lessonState.current=5;assert.equal(lesson.showMe(5,true).ok,true);assert.equal(sandbox.se340XR.se413Quest.coachMode,'material');assert.equal(JSON.stringify(sandbox.currentProject),before);groups++;
}
{
 const before=JSON.stringify(sandbox.currentProject);
 for(let index=0;index<5;index++){
  const group=new THREE.Group();assert.equal(lesson.makeGhost(group,index),true);assert.equal(group.children.length,1,'One noneditable example per stage, including single cavity and single U strip');
  assert.equal(group.children[0].userData.editorOnly,true);assert.equal(group.children[0].raycast(),undefined);
  group.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});
 }
 assert.equal(JSON.stringify(sandbox.currentProject),before);groups++;
}
{
 const g=new THREE.BoxGeometry(1,1,1),converted=ops.convert(g);g.dispose();const d=converted.data;
 const top=Array.from({length:d.indices.length/3},(_,f)=>f).find(f=>{const [a,b,c]=d.indices.slice(f*3,f*3+3).map(i=>new THREE.Vector3(...d.positions.slice(i*3,i*3+3)));return b.sub(a).cross(c.sub(a)).normalize().y>.99;});
 const region=ops.region(d,[top],{expand:true}),inset=ops.inset(d,region.triangleIds,{fraction:.2});assert.equal(inset.ok,true);
 const p=clone(model[0]);p.topologyMesh=clone(inset.data);sandbox.currentProject.modelAtelier.parts=[p];lessonState.current=1;
 nativeSelection={selection:{partId:'model-seed',faceIds:[...inset.selectedFaces]},convert:{available:false},preview:{active:false}};sandbox.se340XR.se430Manual=true;actions.length=0;
 const before=JSON.stringify(sandbox.currentProject);assert.equal(lesson.showMe(1,true).action,'manual-preview');assert.deepEqual(actions,['manual-extrude']);assert.equal(lesson.amountFor('extrude'),-.75);assert.equal(JSON.stringify(sandbox.currentProject),before);groups++;
}
{
 const p=clone(model);p[1]={id:'flat-flap',kind:'box',name:'Flap',position:[0,1.70,.38],rotation:[0,0,0],scale:[1.25,.45,.05],material:'matte',color:'#916b48'};
 assert.equal(check.inspect(p,{allowLegacy:false}).flap.ok,true,'The same one-body lesson remains achievable with ordinary flat-editor thin-box sizing');groups++;
}
{
 const material=new THREE.MeshBasicMaterial({side:THREE.DoubleSide});
 const geometry=new THREE.PlaneGeometry(1,1),guide=new THREE.Mesh(geometry,material),finish=new THREE.Mesh(geometry,material);
 guide.visible=false;guide.name='hidden SHOW';finish.name='visible Leather';
 guide.updateMatrixWorld();finish.updateMatrixWorld();
 const ray=new THREE.Raycaster(new THREE.Vector3(0,0,1),new THREE.Vector3(0,0,-1)),buttons=[guide,finish];
 assert.equal(ray.intersectObjects(buttons,false)[0].object,guide,'Three still intersects hidden quest controls');
 assert.equal(ray.intersectObjects(buttons.filter(o=>o.visible!==false),false)[0].object,finish,'Only the visible quest row may own input');
 assert.match(fs.readFileSync(path.join(ROOT,'patches/v11_441_satchel_vr_workflow.py'),'utf8'),/SE441_VISIBLE_QUEST_INPUT/);
 geometry.dispose();material.dispose();groups++;
}
// Run the actual coach closure with the exact replacement declared by 441.
// Real Three rays place the quest behind nearer body geometry, reproducing
// the UI-ownership conflict without inventing a separate drag handler.
const integration=fs.readFileSync(path.join(ROOT,'patches/v11_441_satchel_vr_workflow.py'),'utf8');
const coachEdit=integration.match(/html=one\(html,("const box=quest\(\),hit=box&&se340Hit\(record,false\);"),\s*("const box=quest\(\),hit=box&&se360MenuContact\(record\); \/\/ SE441_QUEST_GRIP_INPUT")\)/);
assert.ok(coachEdit,'Exercise the exact released quest-grip patch');
const coachBefore=JSON.parse(coachEdit[1]),coachAfter=JSON.parse(coachEdit[2]),coachSource=read('model_satchel_vr_coach_v11_416.js');
assert.equal(coachSource.split(coachBefore).length,2,'The native coach anchor is unique');
const patchedCoach=coachSource.replace(coachBefore,coachAfter);
function coachFixture(){
 const scene=new THREE.Scene(),root=new THREE.Group(),panel=new THREE.Mesh(new THREE.PlaneGeometry(.8,.6),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
 root.position.set(-.3,1.4,-1.5);root.add(panel);scene.add(root);
 const bodyMesh=new THREE.Mesh(new THREE.BoxGeometry(.8,.6,.25),new THREE.MeshBasicMaterial());
 bodyMesh.position.set(-.3,1.4,-1);scene.add(bodyMesh);scene.updateMatrixWorld(true);
 const ray=new THREE.Raycaster(new THREE.Vector3(-.3,1.4,0),new THREE.Vector3(0,0,-1));
 const parts=clone(model),history={undo:['earlier native edit'],redo:['preserved native redo']},selection=['model-seed'];
 const untouched=JSON.stringify({parts,history,selection,bodyMatrix:bodyMesh.matrixWorld.toArray()});
 const record={gripTracked:true,held:true},pose={position:new THREE.Vector3(-.3,1.4,0)},box={root,folded:false,drag:null,signature:'before',message:''};
 const state={visible:true,contact:'quest'},calls={begin:0,update:0,finish:0,cleanup:0,highlight:0,worldHit:0,menuHit:0};
 const ctx=vm.createContext({THREE,window:{SWYRL_E_SATCHEL_ACADEMY_416:{clearHighlight:()=>calls.highlight++}},se340XR:{se413Quest:box,gesture:null},
  se340BeginGesture:()=>{calls.begin++;return 'native begin';},se340UpdateGesture:()=>{calls.update++;return 'native update';},
  se340FinishGesture:()=>{calls.finish++;return 'native finish';},se340Cleanup:()=>{calls.cleanup++;return 'native cleanup';},
  se340Hit:()=>{calls.worldHit++;const hit=ray.intersectObjects([bodyMesh,panel],false)[0];return hit?.object===bodyMesh?{id:'model-seed',distance:hit.distance}:{quest:true,ui:true,...hit};},
  se360MenuContact:()=>{calls.menuHit++;if(state.contact==='ordinary')return {ui:true,action:'grab'};if(state.contact!=='quest')return null;const hit=ray.intersectObject(panel,false)[0];return hit?{quest:true,ui:true,...hit}:null;},
  se340GripPose:r=>r.gripTracked?{position:pose.position.clone(),quaternion:new THREE.Quaternion()}:null,
  se340VisibleSession:()=>state.visible});
 vm.runInContext(patchedCoach,ctx);
 return {ctx,root,box,record,pose,state,calls,
  preserved:()=>assert.equal(JSON.stringify({parts,history,selection,bodyMatrix:bodyMesh.matrixWorld.toArray()}),untouched,'Moving the scene-owned quest must preserve editable parts, native Undo/Redo, selection and model pose'),
  dispose:()=>{panel.geometry.dispose();panel.material.dispose();bodyMesh.geometry.dispose();bodyMesh.material.dispose();}};
}
{
 const f=coachFixture(),origin=f.root.position.clone();
 assert.equal(f.ctx.se340Hit(f.record,false).id,'model-seed','The overlapping native body is nearer than the quest plane');
 assert.equal(f.ctx.se360MenuContact(f.record).quest,true,'UI ownership still belongs to the visible quest');
 const hitsBefore=f.calls.worldHit;
 assert.equal(f.ctx.se340BeginGesture(f.record,'grab'),true);assert.equal(f.box.drag.record,f.record);assert.equal(f.calls.begin,0,'Quest drag must consume Grip instead of delegating a model grab');
 assert.equal(f.calls.worldHit,hitsBefore,'The patched coach must not replace menu ownership with a fresh nearer-body hit');
 f.pose.position.add(new THREE.Vector3(.22,.11,-.05));assert.equal(f.ctx.se340UpdateGesture(),'native update');
 assert.ok(f.root.position.distanceTo(origin.clone().add(new THREE.Vector3(.22,.11,-.05)))<1e-10,'The real coach updates the world-space quest position');
 const placed=f.root.position.clone();f.record.held=false;assert.equal(f.ctx.se340FinishGesture(f.record),true);assert.equal(f.box.drag,null);assert.equal(f.calls.finish,0);
 f.pose.position.add(new THREE.Vector3(.2,.2,.2));f.ctx.se340UpdateGesture();assert.ok(f.root.position.equals(placed),'Release keeps the quest at its placed world-space pose');
 f.preserved();f.dispose();groups++;
}
{
 for(const loss of ['tracking','visibility']){
  const f=coachFixture();assert.equal(f.ctx.se340BeginGesture(f.record,'grab'),true);f.pose.position.x+=.1;f.ctx.se340UpdateGesture();
  const last=f.root.position.clone();if(loss==='tracking')f.record.gripTracked=false;else f.state.visible=false;
  f.pose.position.x+=.5;f.ctx.se340UpdateGesture();assert.equal(f.box.drag,null);assert.ok(f.root.position.equals(last),'Tracking/session loss must stop further panel motion');
  assert.match(f.box.message,/canceled/);f.preserved();f.dispose();
 }
 groups++;
}
{
 for(const mode of ['folded','ordinary','miss','no-quest']){
  const f=coachFixture();if(mode==='folded')f.box.folded=true;else if(mode==='no-quest')f.ctx.se340XR.se413Quest=null;else f.state.contact=mode==='ordinary'?'ordinary':null;
  const origin=f.root.position.clone();assert.equal(f.ctx.se340BeginGesture(f.record,'pan'),'native begin',mode+' keeps the native fallback');
  assert.equal(f.calls.begin,1);assert.equal(f.box.drag,null);f.pose.position.x+=.3;f.ctx.se340UpdateGesture();assert.ok(f.root.position.equals(origin));
  assert.equal(f.ctx.se340FinishGesture(f.record),'native finish');assert.equal(f.calls.finish,1);f.preserved();f.dispose();
 }
 groups++;
}
{
 const f=coachFixture();assert.equal(f.ctx.se340BeginGesture(f.record,'grab'),true);
 assert.equal(f.ctx.se340Cleanup(),'native cleanup');assert.equal(f.box.drag,null);assert.equal(f.calls.cleanup,1);assert.equal(f.calls.highlight,1);
 f.preserved();f.dispose();groups++;
}
const triggerEdit=integration.match(/('const found=se340Hit\(record,false\);'),\s*('const found=se360MenuContact\(record\); \/\/ SE441_QUEST_TRIGGER_INPUT')/);
assert.ok(triggerEdit,'Exercise the exact released quest-trigger patch');
const triggerBefore=triggerEdit[1].slice(1,-1),triggerAfter=triggerEdit[2].slice(1,-1),questSource=read('model_satchel_vr_quest_v11_413.js');
assert.equal(questSource.split(triggerBefore).length,2,'The native quest trigger anchor is unique');
const interaction421=fs.readFileSync(path.join(ROOT,'patches/v11_421_vr_tutorial_menu_interaction.py'),'utf8');
const currentPlace=interaction421.match(/new="""( function place\(\)\{[\s\S]*?\n \})"""/)?.[1],originalPlace=questSource.match(/ function place\(\)\{[\s\S]*?\n \}/)?.[0];
assert.ok(currentPlace?.includes('box.positioned||box.userPositioned')&&originalPlace,'Use the actual current 421 anchored/viewer placement, not the historical 413 console offset');
const questDimensions=interaction421.match(/html=quest\(html,\s*("const LESSON='satchel-001', W=\.70,H=\.525,PX=1024,PY=768;"),\s*("const LESSON='satchel-001', W=\.87,H=\.653,PX=1024,PY=768;")\)/);
assert.ok(questDimensions,'Use the actual enlarged current quest dimensions');
const currentQuest=questSource.replace(originalPlace,currentPlace).replace(JSON.parse(questDimensions[1]),JSON.parse(questDimensions[2]));
const placementEdit=integration.match(/('box\.root\.position\.copy\(viewer\.position\)\.addScaledVector\(forward,1\.13\)\.addScaledVector\(right,\.56\);'),\s*('box\.root\.position\.copy\(viewer\.position\)\.addScaledVector\(forward,[\d.]+\)\.addScaledVector\(right,[\d.]+\); \/\/ SE441_QUEST_SIDE_PLACEMENT')/);
assert.ok(placementEdit,'Exercise the exact released quest side-placement patch');
const placementBefore=placementEdit[1].slice(1,-1),placementAfter=placementEdit[2].slice(1,-1);
assert.equal(currentQuest.split(placementBefore).length,2,'The current native quest placement anchor is unique');
const placementDistances=placementAfter.match(/addScaledVector\(forward,([\d.]+)\)\.addScaledVector\(right,([\d.]+)\)/).slice(1).map(Number);
const patchedQuest=currentQuest.replace(triggerBefore,triggerAfter).replace(placementBefore,placementAfter),[questWidth,questHeight]=patchedQuest.match(/W=([\d.]+),H=([\d.]+)/).slice(1).map(Number);
function questTriggerFixture(){
 const scene=new THREE.Scene(),root=new THREE.Group(),panel=new THREE.Mesh(new THREE.PlaneGeometry(questWidth,questHeight),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
 root.position.set(0,1.4,-1.5);root.add(panel);scene.add(root);
 const verify=new THREE.Mesh(new THREE.PlaneGeometry(.15,.058),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));
 verify.position.set(-.112,-.193,.009);verify.userData.se340Action='se413-check';root.add(verify);
 const bodyMesh=new THREE.Mesh(new THREE.BoxGeometry(.8,.6,.25),new THREE.MeshBasicMaterial());bodyMesh.position.set(0,1.4,-1);scene.add(bodyMesh);scene.updateMatrixWorld(true);
 const point=verify.getWorldPosition(new THREE.Vector3()),ray=new THREE.Raycaster(new THREE.Vector3(point.x,point.y,0),new THREE.Vector3(0,0,-1));
 const parts=clone(model),history={undo:['previous native edit'],redo:['preserved redo']},state={ordinary:null,visible:true,selected:'flap'},calls={check:[],trigger:0,worldHit:0,pulses:0};
 const untouched=JSON.stringify({parts,history,selected:state.selected});
 const paint={measureText:s=>({width:String(s).length*12})};for(const method of ['beginPath','roundRect','fill','clearRect','strokeRect','fillText'])paint[method]=()=>{};
 const box={root,panel,buttons:[verify],owned:[],index:1,folded:false,positioned:false,userPositioned:false,message:'',signature:'',canvas:{getContext:()=>paint},texture:{needsUpdate:false}};
 const record={targetTracked:true,blockTrigger:false},steps=lesson.steps.map(s=>({...s,done:false}));
 const ctx=vm.createContext({THREE,window:{SWYRL_ENGINE_TUTORIAL_412:{status:()=>({active:true,current:1,projectId:'native-guest'}),steps:()=>steps,
  check:index=>{calls.check.push(index);return check.inspect(parts).body;}}},se340XR:{se413Quest:box,scene,frameCount:0},
  se340MakeStage:()=>{},se340Recenter:()=>{},se340ModelXRAction:()=>false,se340ModelXRFrameCore:()=>{},se340Cleanup:()=>{},
  se340Hit:()=>{calls.worldHit++;const hit=ray.intersectObjects([bodyMesh,panel],false)[0];return hit?{id:hit.object===bodyMesh?'model-seed':'panel',distance:hit.distance}:null;},
  se360MenuContact:()=>state.ordinary,se340Trigger:()=>{calls.trigger++;state.selected='model-seed';return 'native trigger';},
  se340Cast:()=>ray,se340VisibleSession:()=>state.visible,se340Pulse:()=>calls.pulses++});
 vm.runInContext(patchedQuest,ctx);
 return {ctx,box,record,ray,state,calls,
  preserved:()=>assert.equal(JSON.stringify({parts,history,selected:state.selected}),untouched,'Quest VERIFY must not select the overlapping body or mutate editable geometry/native Undo'),
  sourcePreserved:()=>assert.equal(JSON.stringify({parts,history}),JSON.stringify({parts:model,history:{undo:['previous native edit'],redo:['preserved redo']}})),
  dispose:()=>{for(const mesh of [verify,panel,bodyMesh]){mesh.geometry.dispose();mesh.material.dispose();}}};
}
{
 const f=questTriggerFixture();assert.equal(f.ctx.se340Hit(f.record,false).id,'model-seed','The actual native hit wrapper still sees nearer body geometry');
 const contact=f.ctx.se360MenuContact(f.record);assert.equal(contact.quest,true);assert.equal(contact.action,'se413-check');
 const before=f.calls.worldHit;f.ctx.se340Trigger(f.record);
 assert.deepEqual(f.calls.check,[1],'Trigger on visible VERIFY must invoke the lesson check for this objective');
 assert.equal(f.calls.trigger,0,'VERIFY consumes the Trigger instead of selecting the body');assert.equal(f.calls.worldHit,before,'Quest Trigger must preserve menu ownership instead of recasting against the nearer body');
 assert.equal(f.record.hit.action,'se413-check');assert.equal(f.calls.pulses,1);assert.match(f.box.message,/connected inset rim/);f.preserved();f.dispose();groups++;
}
{
 for(const mode of ['ordinary','miss']){
  const f=questTriggerFixture();if(mode==='ordinary')f.state.ordinary={ui:true,action:'grab',distance:.2};else f.ray.ray.direction.set(0,0,1);
  assert.equal(f.ctx.se340Trigger(f.record),'native trigger',mode+' retains native Trigger dispatch');assert.equal(f.calls.trigger,1);assert.equal(f.state.selected,'model-seed');assert.deepEqual(f.calls.check,[]);
  f.sourcePreserved();f.dispose();
 }
 groups++;
}
{
 for(const guard of ['tracking','blocked','visibility']){
  const f=questTriggerFixture();if(guard==='tracking')f.record.targetTracked=false;else if(guard==='blocked')f.record.blockTrigger=true;else f.state.visible=false;
  f.ctx.se340Trigger(f.record);assert.deepEqual(f.calls.check,[]);assert.equal(f.calls.trigger,0);f.preserved();f.dispose();
 }
 groups++;
}
{
 const f=questTriggerFixture(),consoleRoot=new THREE.Group();consoleRoot.position.set(-.365,1.488,-1.598);consoleRoot.rotation.y=-.46;consoleRoot.updateMatrixWorld(true);
 f.ctx.se340XR.ui={root:consoleRoot};f.ctx.se340Recenter();assert.equal(f.box.root.visible,false,'No quest is shown before a real anchored viewer is known');assert.equal(f.box.positioned,false);
 const viewer={position:new THREE.Vector3(0,1.65,0),forward:new THREE.Vector3(0,0,-1)};f.ctx.se340XR.anchored=true;f.ctx.se340XR.lastViewer=viewer;f.ctx.se340Recenter();
 const expected=viewer.position.clone().addScaledVector(viewer.forward,placementDistances[0]).add(new THREE.Vector3(placementDistances[1],-.04,0));
 assert.ok(f.box.root.position.distanceTo(expected)<1e-10,'Actual 421 place() applies the exact 441 clear-side offset from the anchored viewer');assert.equal(f.box.positioned,true);assert.equal(f.box.root.visible,true);
 const towardViewer=viewer.position.clone().sub(expected).normalize(),panelNormal=new THREE.Vector3(0,0,1).applyQuaternion(f.box.root.quaternion);
 assert.ok(panelNormal.distanceTo(towardViewer)<1e-10,'Placement preserves native lookAt orientation toward the anchored viewer');
 assert.equal(f.box.panel.geometry.parameters.width,.87);assert.equal(f.box.panel.geometry.parameters.height,.653,'Placement must preserve the current enlarged readable quest');
 const panelPoints=[],position=f.box.panel.geometry.attributes.position;
 for(let i=0;i<position.count;i++)panelPoints.push(f.box.panel.localToWorld(new THREE.Vector3().fromBufferAttribute(position,i)));
 const body=new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(.19,1.43,-1.12),new THREE.Vector3(.72,.514,.334));
 // Include the taller U strap's approximate full lateral silhouette, not
 // just the starter cube, in the canonical saved learner presentation.
 body.union(new THREE.Box3(new THREE.Vector3(.19-.37,1.43,-1.287),new THREE.Vector3(.19+.37,2.23,-.953)));
 const bodyPoints=[];for(const x of [body.min.x,body.max.x])for(const y of [body.min.y,body.max.y])for(const z of [body.min.z,body.max.z])bodyPoints.push(new THREE.Vector3(x,y,z));
 for(const eyeX of [-.032,.032]){
  const camera=new THREE.PerspectiveCamera(90,1,.01,10);camera.position.set(eyeX,1.65,0);camera.updateMatrixWorld(true);
  const panelLeft=Math.min(...panelPoints.map(p=>p.clone().project(camera).x)),bodyRight=Math.max(...bodyPoints.map(p=>p.clone().project(camera).x));
  assert.ok(panelLeft>bodyRight,'The full projected quest clears body/strap bounds from each eye');
  const panelAngle=Math.min(...panelPoints.map(p=>Math.atan2(p.x-eyeX,-p.z))),bodyAngle=Math.max(...bodyPoints.map(p=>Math.atan2(p.x-eyeX,-p.z)));
  assert.ok(THREE.MathUtils.radToDeg(panelAngle-bodyAngle)>3,'Both eyes retain useful clearance with the actual enlarged 421 quest, rather than a touching edge');
 }
 const fixedPosition=f.box.root.position.clone(),fixedRotation=f.box.root.quaternion.clone();
 consoleRoot.position.x-=.1;consoleRoot.updateMatrixWorld(true);
 for(let i=0;i<16;i++){
  f.ctx.se340XR.frameCount=i;f.ctx.se340XR.lastViewer={position:new THREE.Vector3(Math.sin(i)*.15,1.6,-.1),forward:new THREE.Vector3(Math.sin(i),0,-1).normalize()};
  f.ctx.se340ModelXRFrameCore(i*14,null);
 }
 assert.ok(f.box.root.position.equals(fixedPosition));assert.ok(f.box.root.quaternion.equals(fixedRotation),'Head movement and ordinary frames must not auto-follow or recenter the world-space quest');
 f.ctx.se340Recenter();assert.ok(f.box.root.position.equals(fixedPosition),'Ordinary recenter preserves an already-positioned world-space quest');
 f.box.positioned=false;f.box.userPositioned=true;f.box.root.position.add(new THREE.Vector3(-.1,.04,.1));const userPose=f.box.root.position.clone();
 f.ctx.se340Recenter();assert.ok(f.box.root.position.equals(userPose),'The independent userPositioned guard preserves a Grip-arranged quest');
 f.preserved();f.dispose();groups++;
}
// The Academy lives outside Model Atelier's private lexical scope. Run its
// real refresh/set/dispose lifecycle with only the native root getter exposed;
// lesson.makeGhost alone cannot catch a missing private-root lookup.
const academyReplacement=integration.match(/js=function\(js,'refreshGhost',"""([\s\S]*?)"""\)/)?.[1];
assert.ok(academyReplacement?.includes('SE441_NATIVE_GHOST_ROOT'),'Use the actual 441 Academy refresh replacement');
const academySource=read('model_satchel_academy_v11_416.js'),academyStart=academySource.indexOf(' function refreshGhost(){'),academyEnd=academySource.indexOf(' function renderFlat(',academyStart);
assert.ok(academyStart>=0&&academyEnd>academyStart);
const patchedAcademy=academySource.slice(0,academyStart)+academyReplacement+'\n'+academySource.slice(academyEnd);
function academyGhostFixture(){
 const root=new THREE.Group(),nativeGeometry=new THREE.BoxGeometry(1,1,1),nativeMaterial=new THREE.MeshStandardMaterial(),nativeMesh=new THREE.Mesh(nativeGeometry,nativeMaterial);
 nativeMesh.userData.atelierId='model-seed';root.add(nativeMesh);
 const project={instanceId:'native-ghost-guest',kind:'model-atelier',se412Tutorial:'satchel-001',se441TutorialWorkflow:'one-body-v1',modelAtelier:{parts:clone(model)}},history={undo:['preserved native edit'],redo:['preserved redo']};
 const untouched=JSON.stringify({project,history}),state={current:1,root,rootCalls:0},disposed={native:0};nativeGeometry.addEventListener('dispose',()=>disposed.native++);
 const ctx=vm.createContext({THREE,structuredClone,currentProject:project,se340XR:{},localStorage:{getItem:()=>null,setItem:()=>{}},
  se175Snapshot:()=>({data:{project:{}}}),projectData:()=>({project:{}}),
  window:{SWYRL_E_SATCHEL_NATIVE_416:{root:()=>{state.rootCalls++;return state.root;}},SWYRL_ENGINE_TUTORIAL_412:{status:()=>({active:true,current:state.current,projectId:project.instanceId})}}});
 vm.runInContext(read('model_mesh_operations_v11_430.js')+'\n'+read('se436_satchel_cavity.js')+'\n'+read('model_satchel_lesson_v11_441.js')+'\n'+patchedAcademy,ctx);
 assert.equal(vm.runInContext('typeof modelRoot',ctx),'undefined','The native root is deliberately unavailable as an Academy/global variable');
 return {ctx,root,nativeMesh,state,disposed,api:ctx.window.SWYRL_E_SATCHEL_ACADEMY_416,
  preserved:()=>{assert.equal(JSON.stringify({project,history}),untouched,'Ghost lifecycle must not alter editable source or native Undo/Redo');assert.equal(disposed.native,0,'Only the disposable ghost owns its geometry/materials');assert.equal(nativeMesh.parent,root);},
  dispose:()=>{ctx.window.SWYRL_E_SATCHEL_ACADEMY_416.setGhost(false);nativeGeometry.dispose();nativeMaterial.dispose();}};
}
{
 const f=academyGhostFixture();assert.equal(f.api.setGhost(true),true);assert.ok(f.state.rootCalls>0,'Academy resolves the private native root through its API');
 assert.equal(f.root.children.length,2);const first=f.root.children.find(o=>o!==f.nativeMesh);assert.equal(first.userData.editorOnly,true);assert.equal(first.children.length,1,'The cavity reference is one connected, noneditable example');
 const mesh=first.children[0];assert.equal(mesh.userData.editorOnly,true);assert.equal(mesh.raycast(),undefined);assert.equal(mesh.userData.atelierId,undefined,'Reference meshes are not native editable parts');assert.equal(f.api.inspect().ghostMeshes,1);
 let geometryDisposals=0,materialDisposals=0;mesh.geometry.addEventListener('dispose',()=>geometryDisposals++);mesh.material.addEventListener('dispose',()=>materialDisposals++);
 f.state.current=2;f.api.onNativeRender();assert.equal(first.parent,null);assert.equal(geometryDisposals,1);assert.equal(materialDisposals,1);assert.equal(f.root.children.length,2,'Refresh replaces the ghost instead of accumulating references');
 const replacement=f.root.children.find(o=>o!==f.nativeMesh);assert.equal(replacement.children.length,1);replacement.children[0].geometry.addEventListener('dispose',()=>geometryDisposals++);replacement.children[0].material.addEventListener('dispose',()=>materialDisposals++);
 assert.equal(f.api.setGhost(false),false);assert.equal(replacement.parent,null);assert.equal(f.root.children.length,1);assert.equal(geometryDisposals,2);assert.equal(materialDisposals,2);assert.equal(f.api.inspect().ghostMeshes,0);
 f.api.setGhost(false);assert.equal(geometryDisposals,2,'Repeated disable must not dispose the same ghost twice');f.preserved();f.dispose();groups++;
}
{
 for(const absence of ['null','invalid','missing-api']){
  const f=academyGhostFixture();if(absence==='missing-api')delete f.ctx.window.SWYRL_E_SATCHEL_NATIVE_416;else f.state.root=absence==='null'?null:{};
  assert.doesNotThrow(()=>f.api.setGhost(true),'An unavailable private native root must not end VR');assert.equal(f.root.children.length,1);assert.equal(f.api.inspect().ghostMeshes,0);
  assert.doesNotThrow(()=>f.api.refreshGhost());assert.equal(f.api.setGhost(false),false);f.preserved();f.dispose();
 }
 groups++;
}
console.log('MODEL_SATCHEL_WORKFLOW_441_PASS',JSON.stringify({groups,three:THREE.REVISION,body:'one connected native cavity',flapAndStrap:'actual native Draw plus thickness',readOnly:true,transformedDescriptors:true,stageAppropriateMaterials:true,legacySaves:true,physicalHeadsetTested:false}));
