"""§E v11.516 — precise per-vertex/seam skin targeting in existing 2D and
WebXR weight studios. Preserve source, skeleton, menu ownership and history.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_516_RIG_PRECISION'
def one(s,old,new,why):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.516',why,n,old[:140]))
 return s.replace(old,new,1)
def scope(html,start,end,edit):
 i=html.index(start);j=html.index(end,i)
 return html[:i]+edit(html[i:j])+html[j:]
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_515_XR_MENU_CONTROLLER_CLARITY' in html
 helper=(ROOT/'runtime/model_rig_precision_v11_516.js').read_text('utf8')
 assert 'SE516_RIG_PRECISION_END' in helper
 html=one(html,
  'function se220RigBind(){\n se220Bones=null;se220Skeleton=null;se220BoneOverlay=null;',
  '''function se220RigBind(){
 // Rebinding after hierarchy/rest edits must detach previous bone roots and
 // SkeletonHelper; otherwise old roots accumulate and invert bind transforms.
 if(modelRoot){
  for(const previous of Object.values(se220Bones||{}))
   if(previous?.isBone&&previous.parent===modelRoot)previous.removeFromParent();
  if(se220BoneOverlay?.parent===modelRoot){
   se220BoneOverlay.removeFromParent();
   se220BoneOverlay.geometry?.dispose?.();
   se220BoneOverlay.material?.dispose?.();
  }
 }
 se220Bones=null;se220Skeleton=null;se220BoneOverlay=null;''',
  'clean old skeleton before arbitrary rig rebind')
 html=one(html,'/* SE513_RIG_WEIGHT_STUDIO_START',
              helper+'\n/* SE513_RIG_WEIGHT_STUDIO_START','generic precision math')

 def edit2d(s):
  s=one(s,"let armed=false,mode='add',radius=.18,strength=.16,drag=null,installedPanel=null;",
        "let armed=false,mode='add',selection='region',radius=.18,strength=.16,drag=null,installedPanel=null;",
        '2D target state')
  s=one(s,
   "'<div class=\"se513WeightActions\"><button type=\"button\" id=\"se513PaintMode\">Mode: Add influence</button>'+",
   "'<div class=\"se513WeightActions\"><button type=\"button\" id=\"se516TargetMode\">Target: Region</button><button type=\"button\" id=\"se513PaintMode\">Mode: Add influence</button>'+",
   '2D target toggle in current Rigging controls')
  s=one(s,"$('se513PaintArm').addEventListener('click',()=>arm(!armed));",
   """$('se516TargetMode').addEventListener('click',()=>{
    if(drag)cancel();selection=selection==='region'?'vertex':'region';
    $('se516TargetMode').textContent='Target: '+(selection==='region'?'Region':'Single vertex');
    info(selection==='region'?'Region brush uses smooth falloff.':'Vertex target affects the nearest vertex and its UV seam duplicates only.');
   });
   $('se513PaintArm').addEventListener('click',()=>arm(!armed));""",
   '2D target state update')
  s=one(s,
   "idx.needsUpdate=true;w.needsUpdate=true;\n  mesh.skeleton?.update();\n  return true;",
   """idx.needsUpdate=true;w.needsUpdate=true;
  mesh.skeleton?.update();
  // Keep existing selected-bone influence colors live without a second GUI.
  const now=performance.now();
  if(!session.overlayRefreshAt||now-session.overlayRefreshAt>=100){
   session.overlayRefreshAt=now;
   $('se500RefreshVertices')?.click();
  }
  return true;""",
   'throttled live 2D weight visualization')
  s=one(s,'const result=se513SkinMath.region(','const result=se516SkinPrecision.region(',
        '2D target algorithm')
  s=one(s,'point.toArray(),radius,session.boneIndex,change,session.rig.bones.length,pose);',
        'point.toArray(),radius,session.boneIndex,change,session.rig.bones.length,pose,session.selection);',
        '2D precise selection')
  s=one(s,'boneId:se220Joint,boneIndex,vertices:data.vertices,positions:data.positions,initial,',
        'boneId:se220Joint,boneIndex,vertices:data.vertices,positions:data.positions,selection,initial,',
        '2D selection lock per undo stroke')
  s=one(s,"active:!!drag,updates:drag?.changed||0})",
        "active:!!drag,selection,updates:drag?.changed||0})",
        '2D status')
  return s
 html=scope(html,'/* SE513_RIG_WEIGHT_STUDIO_START','/* SE513_RIG_WEIGHT_STUDIO_END',edit2d)

 def editVR(s):
  s=one(s,"let handles=null,drag=null,lastRig=null,lastRoot=null;",
        "let handles=null,drag=null,lastRig=null,lastRoot=null,weightViz=null;",
        'XR weight visual state')
  s=one(s," function dispose(){",
   """ function clearWeightViz(){
  if(!weightViz)return;
  weightViz.points.removeFromParent();
  weightViz.points.geometry.dispose();
  weightViz.points.material.dispose();
  weightViz=null;
 }
 function syncWeightViz(){
  if(!handles?.group?.visible||!isMode()){clearWeightViz();return;}
  const target=skinTarget(),rig=se220Rig(),
   boneIndex=rig?.bones?.findIndex(b=>b.id===se220Joint);
  if(!target||boneIndex<0){clearWeightViz();return;}
  const {mesh,vertices,idx,w}=target,version=idx.version+'/'+w.version;
  const stale=!weightViz||weightViz.mesh!==mesh||weightViz.bone!==boneIndex||
   weightViz.version!==version||weightViz.count!==vertices;
  if(stale){
   clearWeightViz();
   const entries=[],max=1200;
   for(let i=0;i<vertices;i++){
    let influence=0;
    for(let k=0;k<4;k++)if(idx.getComponent(i,k)===boneIndex)
     influence+=w.getComponent(i,k);
    if(influence>=.015)entries.push({index:i,weight:influence});
   }
   const stride=Math.max(1,Math.ceil(entries.length/max));
   const samples=entries.filter((e,i)=>i%stride===0).slice(0,max);
   const g=new THREE.BufferGeometry(),colors=new Float32Array(samples.length*3);
   for(let i=0;i<samples.length;i++){
    const amount=samples[i].weight;
    colors[3*i]=.18+.82*amount;
    colors[3*i+1]=.94-.65*amount;
    colors[3*i+2]=1-.35*amount;
   }
   g.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(samples.length*3),3));
   g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
   const points=new THREE.Points(g,new THREE.PointsMaterial({
    size:.011,sizeAttenuation:true,vertexColors:true,
    depthTest:false,depthWrite:false,opacity:.92,transparent:true
   }));
   points.name='Selected bone weighted vertices';
   points.renderOrder=9100;points.frustumCulled=false;
   points.userData.editorOnly=true;points.raycast=()=>{};
   handles.group.add(points);
   weightViz={mesh,bone:boneIndex,version,count:vertices,points,samples};
  }
  if(se340XR.frameCount%4!==0&&!stale)return;
  handles.group.updateMatrixWorld(true);
  mesh.updateMatrixWorld(true);
  const toGroup=handles.group.matrixWorld.clone().invert();
  const pos=mesh.geometry.getAttribute('position');
  const dest=weightViz.points.geometry.getAttribute('position');
  for(let i=0;i<weightViz.samples.length;i++){
   const vertex=weightViz.samples[i].index;
   const p=tempA.fromBufferAttribute(pos,vertex);
   if(typeof mesh.applyBoneTransform==='function')mesh.applyBoneTransform(vertex,p);
   p.applyMatrix4(mesh.matrixWorld).applyMatrix4(toGroup);
   dest.setXYZ(i,p.x,p.y,p.z);
  }
  dest.needsUpdate=true;
  if(dest.count)weightViz.points.geometry.computeBoundingSphere();
 }
 function dispose(){
  clearWeightViz();""",
   'reuse existing XR joint gizmo scene for live color-weighted vertices')
  s=one(s,"   handles.group.updateWorldMatrix(true,true);\n  }\n  function choose(id){",
        "   handles.group.updateWorldMatrix(true,true);\n   syncWeightViz();\n  }\n  function choose(id){",
        'animate influence preview along actual skinned bone deformation')
  s=one(s,"let paintMode='add',radius=.18,strength=.16,undoStack=[],previous=new Map();",
        "let paintMode='add',selection='region',radius=.18,strength=.16,undoStack=[],previous=new Map();",
        'native XR target state')
  s=one(s,'rigPaintMode:paintMode,rigRadius:radius,rigStrength:strength,',
        'rigPaintMode:paintMode,rigTarget:selection,rigRadius:radius,rigStrength:strength,',
        'publish mode to existing menu')
  s=one(s,'const result=se513SkinMath.region(','const result=se516SkinPrecision.region(',
        'XR generic brush')
  s=one(s,'session.target.rig.bones.length,pose);',
        'session.target.rig.bones.length,pose,session.selection);',
        'XR single vertex and region')
  s=one(s,'drag={record,target,index,id:se220Joint,mode:paintMode,initial:old,',
        'drag={record,target,index,id:se220Joint,mode:paintMode,selection,initial:old,',
        'lock selection for stroke')
  s=one(s,"if(!valid()||!isMode()||s.mode!=='rig-weight'||se220Rig()!==session.target.rig||",
        "if(!valid()||!isMode()||s.mode!=='rig-weight'||se220Joint!==session.id||se220Rig()!==session.target.rig||",
        'cancel on bone switch')
  s=one(s,"else if(command==='rig-weight-add'||command==='rig-weight-erase'){",
        """else if(command==='rig-select-mode'){
    cancelPaint();selection=selection==='region'?'vertex':'region';
    message('Weight target: '+(selection==='region'?'smooth region':'nearest vertex and UV seam'));
   }
   else if(command==='rig-weight-add'||command==='rig-weight-erase'){""",
        'native action without new controller loop')
  return s
 html=scope(html,'/* SE514_NATIVE_XR_RIG_START','/* SE514_NATIVE_XR_RIG_END',editVR)

 def editUI(s):
  s=one(s,"'rig-radius-plus':'Larger brush influence region',",
        "'rig-radius-plus':'Larger brush influence region',\n   'rig-select-mode':'Switch between region brush and one UV-seam-safe vertex',",
        'native existing help')
  s=one(s,"if(id.startsWith('rig-weight')||id.startsWith('rig-radius')||id.startsWith('rig-strength'))",
        "if(id==='rig-select-mode'||id.startsWith('rig-weight')||id.startsWith('rig-radius')||id.startsWith('rig-strength'))",
        'reuse native tool icon')
  s=one(s,
   "['rig-undo','Undo rig edit'],['rig','Bone posing'],['exit','Exit VR']",
   "['rig-undo','Undo rig edit'],['rig','Bone posing'],['rig-select-mode','Target: region / vertex']",
   '12 slot native weight page')
  return s
 html=scope(html,'/* SE360_MODEL_VR_UI_START','/* SE360_MODEL_VR_UI_END',editUI)

 def editStage(s):
  s=one(s,"['rig-undo','Undo rig edit'],['rig-weight-stop','Stop painting'],['rig','Bone posing']],",
        "['rig-undo','Undo rig edit'],['rig-weight-stop','Stop painting'],['rig','Bone posing'],\n    ['rig-select-mode','Target: Region / Vertex']],",
        '12th operation on actual 3-stage XR menu')
  s=one(s,"action.startsWith('rig-radius-')||action.startsWith('rig-strength-')",
        "action==='rig-select-mode'||action.startsWith('rig-radius-')||action.startsWith('rig-strength-')",
        'keep selection within native rig-weight page')
  return s
 html=scope(html,'/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END',editStage)
 html=one(html,"'rig-pose-z-minus','rig-pose-z-plus']",
        "'rig-pose-z-minus','rig-pose-z-plus','rig-select-mode']",
        'scene action registry')
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_515_XR_MENU_CONTROLLER_CLARITY',MARKER),
  ('ENGINE · MAKER v11.515','ENGINE · MAKER v11.516'),
  ('v11.515 · stable XR menus and precise controller button guides',
   'v11.516 · precise per-vertex and region rig weight editing'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.515'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.516'"),
  ('<title>§wyrl§ Engine · Maker v11.515</title>',
   '<title>§wyrl§ Engine · Maker v11.516</title>')
 ]:html=one(html,before,after,'release identity')
 prior=" source.engine='§wyrl§ Engine · Maker v11.515';source.version=11.515;"
 assert html.count(prior)==5,('v11.516 provenance',html.count(prior))
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.516';source.version=11.516;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.515']
 notes['history'].insert(0,{'version':'v11.515','changes':notes.get('changes',[])})
 notes.update(version='v11.516',date='2026-11-18',
  title='Precise single-vertex and region rig weight painting',
  changes=[
   'The existing 2D Rigging weight editor now switches between a smooth region brush and precise nearest-vertex targeting. Welded UV seam duplicates are edited together without spilling onto adjacent vertices.',
   'Immersive WebXR Rigging reuses the existing three-stage spatial menu, adding a Target: Region / Vertex operation. Right Trigger continues to paint the actual skinned mesh using normalized four-bone weights and the current selected joint.',
   'Bone changes invalidate active VR brush strokes rather than applying a stale influence to the previous selection. Per-stroke mode is fixed until release, preserving Undo/project checkpoints.',
   'No starter-specific topology, rest skeleton, existing project history, UVs, core menu renderer or controller routing is replaced. Quest 2 physical acceptance remains pending.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
