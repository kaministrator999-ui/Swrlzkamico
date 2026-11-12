"""§E v11.420 · Quest 2 menu placement, ray interaction and legibility.

Append-only repairs to the existing source-sealed UI. The tutorial stays
directly parented to the native VR scene, never the model rig or camera.
Do not mutate historical v11.413/v11.416 source.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_420_VR_TUTORIAL_MENU_INTERACTION'

def once(html,old,new):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.420 anchor',old[:150],n))
    return html.replace(old,new,1)

def scoped(src,start,end,old,new):
    a=src.index(start);b=src.index(end,a)+len(end)
    return src[:a]+once(src[a:b],old,new)+src[b:]

def quest(src,old,new):
    return scoped(src,'/* SE413_SATCHEL_VR_QUEST_START','/* SE413_SATCHEL_VR_QUEST_END */',old,new)

def coach(src,old,new):
    return scoped(src,'/* SE416_SATCHEL_VR_COACH_START','/* SE416_SATCHEL_VR_COACH_END */',old,new)

def menu(src,old,new):
    return scoped(src,'/* SE360_MODEL_VR_UI_START */','/* SE360_MODEL_VR_UI_END */',old,new)

def apply(html):
    assert 'SE413_SATCHEL_VR_QUEST_START' in html
    assert 'SE416_SATCHEL_VR_COACH_START' in html
    assert 'SE415_MODEL_VR_ICONOGRAPHY' in html
    runtime=(ROOT/'runtime/model_vr_menu_stability_v11_420.js').read_text('utf8')

    # The initial makeStage runs BEFORE a headset viewer position is known.
    # Hide the quest until the native workbench has explicitly calibrated.
    # Place it opposite the native tool console, at an accessible physical
    # distance, ONCE. Camera orbit and subsequent ordinary recenter do not
    # overwrite a user-arranged menu.
    old=""" function place(){
  const box=q(),ui=se340XR.ui;if(!box||!ui?.root)return;
  ui.root.updateWorldMatrix(true,true);
  // Deliberately offset in WORLD SPACE. Reposition only on explicit recenter.
  box.root.position.copy(ui.root.localToWorld(new THREE.Vector3(1.02,.07,.02)));
  box.root.quaternion.copy(ui.root.quaternion);
  box.root.updateWorldMatrix(true,true);
 }"""
    new=""" function place(){
  const box=q(),s=se340XR;if(!box||!s.ui?.root)return;
  if(box.positioned||box.userPositioned)return;
  // Initial native XR stage has no viewer pose: avoid showing a menu at the
  // model origin. Only native se340Recenter(viewer) supplies a real anchor.
  const viewer=s.lastViewer||s.anchor;
  if(!s.anchored||!viewer?.position||!viewer?.forward){
   box.root.visible=false;return;
  }
  const forward=viewer.forward.clone();forward.y=0;
  if(forward.lengthSq()<.001)forward.set(0,0,-1);forward.normalize();
  const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
  box.root.position.copy(viewer.position).addScaledVector(forward,1.13).addScaledVector(right,.56);
  box.root.position.y=THREE.MathUtils.clamp(viewer.position.y-.04,.9,1.80);
  box.root.lookAt(viewer.position);
  box.positioned=true;box.root.visible=true;
  box.root.updateWorldMatrix(true,true);
 }"""
    html=quest(html,old,new)
    html=quest(html,"const LESSON='satchel-001', W=.70,H=.525,PX=1024,PY=768;",
      "const LESSON='satchel-001', W=.87,H=.653,PX=1024,PY=768;")
    html=quest(html,"  const root=new THREE.Group();root.name='Apprentice Satchel · fixed world-space quest';",
      "  const root=new THREE.Group();root.name='Apprentice Satchel · fixed world-space quest';root.visible=false;")
    html=quest(html,
      "  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;",
      "  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;texture.minFilter=THREE.LinearMipmapLinearFilter;texture.magFilter=THREE.LinearFilter;texture.anisotropy=8;texture.generateMipmaps=true;")
    html=quest(html,
      "  const material=new THREE.MeshBasicMaterial({map:texture,transparent:true,side:THREE.DoubleSide,\n   depthTest:false,depthWrite:false});",
      "  const material=new THREE.MeshBasicMaterial({map:texture,transparent:true,side:THREE.DoubleSide,\n   depthTest:false,depthWrite:false,toneMapped:false});")
    html=quest(html,
      "  mesh.userData.se340Action=id;mesh.userData.editorOnly=true;",
      "  mesh.userData.se340Action=id;mesh.userData.editorOnly=true;mesh.userData.se340UI=true;")
    html=quest(html,
      "   index:Math.max(0,Math.min(6,Number(lesson()?.status()?.current)||0)),folded:false,message:'',signature:''};",
      "   index:Math.max(0,Math.min(6,Number(lesson()?.status()?.current)||0)),folded:false,message:'',signature:'',positioned:false,userPositioned:false,hoverAction:null,pressedAction:null};")

    # Native menu text is legible when it occupies adequate visual angle;
    # anisotropic filtering improves oblique viewing on mobile WebXR.
    html=menu(html,
      "root.name='Model Studio · spatial console';",
      "root.name='Model Studio · spatial console';root.scale.setScalar(1.16);")
    html=menu(html,
      "texture.generateMipmaps=true;texture.anisotropy=2;textures.add(texture);",
      "texture.generateMipmaps=true;texture.anisotropy=8;textures.add(texture);")

    # Preserve the original draw pipeline and native ray actions. Draw a
    # focused border on the *same canvas buttons* when an actual XR ray hovers.
    html=quest(html,
      "const signature=JSON.stringify([box.folded,index,rows.map(r=>r.done),box.message,st.projectId,box.coachMode,box.confirmRestore,window.SWYRL_E_SATCHEL_ACADEMY_416?.ghost?.()]);",
      "const signature=JSON.stringify([box.folded,index,rows.map(r=>r.done),box.message,st.projectId,box.coachMode,box.confirmRestore,window.SWYRL_E_SATCHEL_ACADEMY_416?.ghost?.(),box.hoverAction,box.pressedAction]);")
    html=quest(html,
      "   c.fillText(label,x+w/2,y+53);c.textAlign='left';",
      """   if(box.hoverAction===action||box.pressedAction===action){
    c.strokeStyle=box.pressedAction===action?'#dcffad':'#91f8ee';
    c.lineWidth=6;c.strokeRect(x+4,y+4,w-8,77);
   }
   c.fillText(label,x+w/2,y+53);c.textAlign='left';""")
    html=coach(html,
      "   c.fillText(text,x+52,y+29);",
      """   c.fillText(text,x+52,y+29);
   if(box.hoverAction===action||box.pressedAction===action){
    c.strokeStyle=box.pressedAction===action?'#dcffad':'#91f8ee';
    c.lineWidth=5;c.strokeRect(x+3,y+3,w-6,h-6);
   }""")
    html=coach(html,
      "   c.fillText(mode==='guide'?'MATERIALS':'GUIDE',807,66);c.textAlign='left';",
      """   c.fillText(mode==='guide'?'MATERIALS':'GUIDE',807,66);c.textAlign='left';
   if(box.hoverAction==='se416-mode'){
    c.strokeStyle='#91f8ee';c.lineWidth=5;c.strokeRect(742,21,131,76);
   }""")

    # The existing native controller grip hooks already dispatch into the
    # tutorial. Complete that implementation with rotation and a durable
    # 'user positioned' flag so ordinary orbit/recenter never reattaches it.
    html=coach(html,
      "    box.drag={record,origin:box.root.position.clone(),hand:pose.position.clone()};",
      "    box.drag={record,origin:box.root.position.clone(),hand:pose.position.clone(),originQuat:box.root.quaternion.clone(),handQuat:pose.quaternion.clone()};")
    html=coach(html,
      "  box.root.position.copy(drag.origin).add(delta);\n  box.root.updateWorldMatrix(true,true);",
      """  box.root.position.copy(drag.origin).add(delta);
  if(pose.quaternion&&drag.handQuat&&drag.originQuat)
   box.root.quaternion.copy(pose.quaternion).multiply(drag.handQuat.clone().invert()).multiply(drag.originQuat);
  box.root.updateWorldMatrix(true,true);""")
    html=coach(html,
      "   box.drag=null;box.message='Quest window placed independently in world space.';",
      "   box.drag=null;box.userPositioned=true;box.message='Quest window placed independently in world space.';")

    # Installed after existing se413 and se416 hooks; it reuses the same
    # tracked-target ray and event pipeline, never creating a second XR loop.
    html=once(html,'if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(',
      runtime+'\nif(ALLOWED_PARENTS.has(location.origin))queueMicrotask(')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_419_SHEEP_CONGESTION_BUDGET',MARKER),
      ('ENGINE · MAKER v11.419','ENGINE · MAKER v11.420'),
      ('v11.419 · bounded Sheep Tag congestion','v11.420 · reliable and readable Model VR tutorial menus'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.419'","window.SWRLZ_FORGE_BUILD={version:'v11.420'"),
      ('<title>§wyrl§ Engine · Maker v11.419</title>','<title>§wyrl§ Engine · Maker v11.420</title>')
    ]:html=once(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.419';source.version=11.419;"
    if html.count(old)!=5:raise AssertionError(('v11.420 provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.420';source.version=11.420;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,{'version':'v11.419','changes':notes.get('changes',[])})
    notes.update(version='v11.420',date='2026-11-11',
      title='Quest 2: stable, readable and selectable tutorial panel',changes=[
       'Correct the source of the satchel menu appearing near the cube: defer placement until headset recenter has an actual viewer pose; place it opposite the native tool console, once, as an independent world-space scene object.',
       'Preserve grip-dragged position and rotation of the quest menu; neither camera orbit nor normal recenter reattaches it to the model, camera or native menu. Keep model manipulation and its tool window separate.',
       'Fix tutorial buttons being unselectable beyond the 1.2 metre XR default hit point: prioritize actual quest ray intersections over the empty-space fallback while respecting nearer native tool and model hits.',
       'Show controller ray hover and press borders on the real lesson actions and retain native haptics and XR input mapping without a second event loop.',
       'Enlarge both VR menus physically and use stronger anisotropic texture filtering and untone-mapped canvas labels for improved Quest 2 legibility.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
