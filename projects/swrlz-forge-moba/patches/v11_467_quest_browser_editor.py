"""§E v11.467 -- Quest browser pointer ownership, component picking and visible Extrude controls."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_467_QUEST_EDITOR_INPUT'
def once(s,old,new):
 n=s.count(old)
 assert n==1,('v11.467 anchor',old[:130],n)
 return s.replace(old,new,1)
def regex_once(s,pattern,replacement):
 out,n=re.subn(pattern,lambda match:match.expand(replacement),s,count=1,flags=re.MULTILINE)
 assert n==1,('v11.467 regex anchor',pattern[:120],n)
 return out
def apply(html):
 html=regex_once(html,
   r"if\s*\(atelierCameraTouches\.size===1\)\s*\{\s*const\s*\[id,pt\]=atelierCameraTouches\.entries\(\)\.next\(\)\.value;\s*if\s*\(atelierCameraConsumedTouches\.has\(id\)\)\s*\{\s*atelierCameraConsumedTouches\.delete\(id\);\s*pressed=\{x:pt\.x,y:pt\.y,yaw:orbit\.yaw,pitch:orbit\.pitch,moved:true\};\s*\}\s*\}",
   "// A pointer left after pinch stays consumed until its own release.\n  if(atelierCameraTouches.size===1)pressed=null;")
 html=regex_once(html,r"function atelierCameraPointerCancel\(e\)\s*\{\s*atelierCameraPointerUp\(e\);\s*pressed=null;\s*\}",
 """function atelierCameraPointerCancel(e){
  const tracked=atelierCameraTouches.has(e.pointerId);
  atelierCameraTouches.delete(e.pointerId);
  atelierCameraConsumedTouches.delete(e.pointerId);
  if(tracked){
   for(const id of atelierCameraTouches.keys())atelierCameraConsumedTouches.add(id);
   atelierCameraGesture=null;
  }
  if(atelierCameraMousePan?.id===e.pointerId)atelierCameraMousePan=null;
  pressed=null;
 }""")
 # Keep Quest's virtual-mouse silhouette target bounded and leave desktop exactness intact.
 html=once(html,
   "if(!triangle&&e.pointerType==='touch'&&['vertex','edge'].includes(atelierComponentMode)){",
   "if(!triangle&&(e.pointerType==='touch'||/OculusBrowser|Quest/i.test(navigator.userAgent))&&['vertex','edge'].includes(atelierComponentMode)){")
 html=once(html,
   "const tol=e.pointerType==='touch'?31:22;",
   "const tol=e.pointerType==='touch'?31:/OculusBrowser|Quest/i.test(navigator.userAgent)?28:22;")
 html=once(html,
   "if(Math.hypot(e.clientX-d.startX,e.clientY-d.startY)>5)d.moved=true;",
   "if(Math.hypot(e.clientX-d.startX,e.clientY-d.startY)>(/OculusBrowser|Quest/i.test(navigator.userAgent)?11:5))d.moved=true;")
 # Screen-space-aware point target that scales with zoom and viewport height.
 html=once(html,
   "raycaster.params.Points.threshold=.034;",
   """const se467Rect=renderer.domElement.getBoundingClientRect();
  const se467Radius=e.pointerType==='touch'?19:/OculusBrowser|Quest/i.test(navigator.userAgent)?17:11;
  const se467Depth=camera.position.distanceTo(atelierSculptOverlay.userData.vertexPoints.getWorldPosition(new THREE.Vector3()));
  const se467World=2*se467Depth*Math.tan(THREE.MathUtils.degToRad(camera.fov||44)/2)*se467Radius/Math.max(180,se467Rect.height);
  raycaster.params.Points.threshold=Math.min(.26,Math.max(.034,se467World));""")
 # Do not let a retained pointer capture click through a dialog on the canvas.
 html=regex_once(html,
   r"(function pointerDown\(e\)\{\s*)(if\(atelierComponentPointerDown\(e\)\))",
   r"\1if(!se467ViewportPointerAllowed(e))return;\n    \2")
 html=once(html,
   "if(!hit||!modelRoot)return;\n     const pos=point(e);",
   "if(!hit||!modelRoot||!se467ViewportPointerAllowed(e))return;\n     const pos=point(e);")
 js=(ROOT/'runtime/model_quest_browser_input_v11_467.js').read_text('utf8')
 html=once(html,'/* SE466_RING_UI_END */',js+'\n/* SE466_RING_UI_END */')
 html=once(html,'se430BeginnerInstall(panel);se466RingUIInstall(panel);',
  'se430BeginnerInstall(panel);se466RingUIInstall(panel);se467QuestInstall(panel);')
 html=once(html,
  "if(ring)ring.hidden=selection.mode!=='vertex';\n if(face)face.hidden=panel.querySelector('#modelAtelierWorkshopOperation')?.value!=='extrude';",
  """const se467Extrude=panel.querySelector('#modelAtelierWorkshopOperation')?.value==='extrude'||
   (typeof se430BeginnerTool==='function'&&se430BeginnerTool()==='extrude');
 if(ring)ring.hidden=selection.mode!=='vertex'&&!se467Extrude;
 if(face)face.hidden=!se467Extrude;
 if(se467Extrude){
  if(face&&!face.dataset.se467Opened){face.open=true;face.dataset.se467Opened='1';}
  if(ring&&!ring.dataset.se467Opened){ring.open=true;ring.dataset.se467Opened='1';}
 }""")
 # v11.465 erroneously hides every inspector tool at narrow dock widths.
 html=once(html,
  "[data-se464-inspector-focus=true]) .atelier-inspector>:not(.atelier-tool-handle):not(.se465-inspector-narrow-hint){",
  "[data-se464-inspector-focus=true]) .atelier-inspector>:not(.atelier-tool-handle):not(.se465-inspector-narrow-hint)[data-se467-never-hide]{")
 css=(ROOT/'runtime/model_quest_browser_input_v11_467.css').read_text('utf8')
 html=once(html,'</head>','<style id="se467QuestEditorStyles">\n'+css+'\n</style>\n</head>')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_466_RING_ARC_MODELING',MARKER)
 html=once(html,'ENGINE · MAKER v11.466','ENGINE · MAKER v11.467')
 html=once(html,'v11.466 · ring and arc modeling','v11.467 · Quest editor input and Extrude controls')
 html=once(html,"window.SWRLZ_FORGE_BUILD={version:'v11.466'","window.SWRLZ_FORGE_BUILD={version:'v11.467'")
 html=once(html,'<title>§wyrl§ Engine · Maker v11.466</title>','<title>§wyrl§ Engine · Maker v11.467</title>')
 prior=" source.engine='§wyrl§ Engine · Maker v11.466';source.version=11.466;"
 assert html.count(prior)==5,('v11.467 provenance',html.count(prior))
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.467';source.version=11.467;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,length=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[h for h in notes.get('history',[]) if h.get('version')!='v11.466']
 notes['history'].insert(0,{'version':'v11.466','changes':notes.get('changes',[])})
 notes.update(version='v11.467',date='2026-11-15',
  title='Quest controller editor interactions and accessible extrusion tools',
  changes=[
   'Quest browser gesture release no longer re-arms orbit after a pinch; interruption cancels stale camera input.',
   'The right inspector supports controller drag scrolling, gamepad axes where available, and wheel/key scrolling without viewport passthrough.',
   'Vertex hit tolerance adapts to Quest pointer targets and zoom while preserving native component selection and Undo.',
   'Narrow inspector docking no longer hides modeling controls; ring/radius/half-ring selectors and face extrusion settings are visible in the Extrude workflow.',
   'Account-backed studio asset isolation remains a separate release gate; Quest physical-device acceptance has not yet been verified.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+length:]
