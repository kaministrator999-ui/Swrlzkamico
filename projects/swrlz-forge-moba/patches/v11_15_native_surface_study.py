"""Native portrait and cloth controls; retained historical source and separate authored starter."""
from pathlib import Path
import json,re

def once(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b,1)

def apply(html):
    r=Path(__file__).resolve().parent.parent
    scene=json.loads((r/'scenes/model-atelier-festival-surface-v11-15.swyrl.json').read_text())
    enc=json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    pat=r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    match=re.search(pat,html,re.S);assert match
    html=html[:match.start()]+'const MODEL_ATELIER_CANONICAL_PROJECT='+enc+';\n'+html[match.end():]
    html=once(html,"if(part.material==='emissive')return new THREE.MeshBasicMaterial({color:col});","if(part.material==='emissive')return new THREE.MeshBasicMaterial({color:part.surfaceStyle==='split-dye-cap'?new THREE.Color('#ffffff'):col,vertexColors:part.surfaceStyle==='split-dye-cap'});")
    html=once(html,"color:part.kind==='loft'?new THREE.Color('#ffffff'):col","color:part.kind==='loft'||part.surfaceStyle==='split-dye-cap'?new THREE.Color('#ffffff'):col")
    html=once(html,"vertexColors:part.kind==='loft',side:THREE.DoubleSide","vertexColors:part.kind==='loft'||part.surfaceStyle==='split-dye-cap',side:THREE.DoubleSide")
    html=once(html,'  function refreshList(){',(r/'runtime/model_atelier_surface_v11_15.js').read_text()+'\n  function refreshList(){')
    html=once(html,"neutral!==undefined&&!atelierValidPoseFrame(neutral)","neutral!=null&&!atelierValidPoseFrame(neutral)")
    html=once(html,'  function checkPart(p){', '''  function checkPart(p){
    if(p&&p.dyeAccent!==undefined&&!/^#[0-9a-fA-F]{6}$/.test(p.dyeAccent))return false;
    for(const [key,limit] of [['jawTaper',.5],['panelCamber',.25],['panelPleat',.06]])
      if(p&&p[key]!==undefined&&(!Number.isFinite(p[key])||p[key]<0||p[key]>limit))return false;''')
    html=once(html,'function atelierReferenceGeometry(part){',"function atelierReferenceGeometry(part){\n  if(part.kind==='sphere'&&part.surfaceStyle==='tapered-muzzle')return atelierTaperedMuzzle();\n  if(part.kind==='sphere'&&part.surfaceStyle==='split-dye-cap')return atelierSplitDyeCap(part);")
    html=once(html,'1-.31*Math.pow((-y-.12)/.88,.65)','1-(part.jawTaper??.31)*Math.pow((-y-.12)/.88,.65)')
    html=once(html,'fold=Math.cos(u*Math.PI*3)*.012*Math.sin(t*Math.PI)','fold=Math.cos(u*Math.PI*3)*(part.panelPleat??.012)*Math.sin(t*Math.PI)')
    html=once(html,'fold-.055*u*u','fold-(part.panelCamber??.055)*u*u')
    html=once(html,'fold-.085*u*u','fold-(part.panelCamber??.085)*u*u')
    html=once(html,'    const sculpt=$m(\'SculptEditor\');','    atelierSurfaceRefresh();\n    const sculpt=$m(\'SculptEditor\');')
    html=once(html,'atelierPoseDeckInstall();atelierAssemblyInstall();','atelierPoseDeckInstall();atelierAssemblyInstall();atelierSurfaceInstall();')
    deck='''<section id="modelAtelierSurfaceEditor" hidden aria-label="Surface shaping"><h3>Surface shaping</h3><div id="modelAtelierSurfaceSphere"><label>Sculpted surface<select id="modelAtelierSurfacePreset"><option value="rounded">Rounded</option><option value="portrait-head">Portrait head</option><option value="tapered-muzzle">Tapered muzzle</option><option value="split-dye-cap">Split dye crown</option></select></label><label id="modelAtelierDyeAccentRow" hidden>Second dye color<input id="modelAtelierDyeAccent" type="color" value="#f65f60"></label></div><div id="modelAtelierSurfacePortrait"><label>Jaw taper<input id="modelAtelierJawTaper" type="number" min="0" max=".5" step=".01"></label></div><div id="modelAtelierSurfaceCloth"><label>Cloth curvature<input id="modelAtelierPanelCamber" type="number" min="0" max=".25" step=".005"></label><label>Fold depth<input id="modelAtelierPanelPleat" type="number" min="0" max=".06" step=".002"></label></div><button id="modelAtelierSurfaceApply">Apply surface shape</button></section>'''
    html=once(html,'<section id="modelAtelierLoftEditor"',deck+'<section id="modelAtelierLoftEditor"')
    html=once(html,'<button id="modelAtelierResetCamera">Reset view</button>','<button id="modelAtelierResetCamera">Reset view</button><button id="modelAtelierFrameSelected">Frame selected</button>')
    html=once(html,'function atelierSetPoseCamera(view){','function atelierSetPoseCamera(view){\n  atelierDetailTarget=null;')
    html=once(html,'const h=Math.cos(orbit.pitch),focusY=model()?.assemblies?2.8:2.35;', 'const h=Math.cos(orbit.pitch),focusY=model()?.assemblies?2.8:2.35,target=atelierDetailTarget||new THREE.Vector3(0,focusY,0);')
    html=once(html,'camera.position.set(orbit.distance*h*Math.sin(orbit.yaw),focusY+.1+orbit.distance*Math.sin(orbit.pitch),orbit.distance*h*Math.cos(orbit.yaw));','camera.position.set(target.x+orbit.distance*h*Math.sin(orbit.yaw),target.y+.1+orbit.distance*Math.sin(orbit.pitch),target.z+orbit.distance*h*Math.cos(orbit.yaw));')
    html=once(html,'camera.lookAt(0,focusY,0);','camera.lookAt(target);')
    html=once(html,"action('ResetCamera',()=>{orbit=", "action('ResetCamera',()=>{atelierDetailTarget=null;orbit=")
    html=once(html,"function onWheel(e){e.preventDefault();orbit.distance=Math.min(22,Math.max(3.7,", "function onWheel(e){e.preventDefault();orbit.distance=Math.min(22,Math.max(atelierDetailTarget?.4:3.7,")
    html=once(html,"action('ZoomIn',()=>{orbit.distance=Math.max(3.7,", "action('ZoomIn',()=>{orbit.distance=Math.max(atelierDetailTarget?.4:3.7,")
    html=once(html,"if(model()?.assemblies){orbit.distance=Math.max(orbit.distance,", "if(model()?.assemblies&&!atelierDetailTarget){orbit.distance=Math.max(orbit.distance,")
    html=once(html,'returnFocus=document.activeElement;panel.hidden=false;','returnFocus=document.activeElement;panel.hidden=false;atelierDetailTarget=null;')
    html=once(html,'back.position.set(-7,5,-5);world.add(back);','back.position.set(-7,5,-5);world.add(back);\n    if(model()?.assemblies){const fill=new THREE.DirectionalLight(0xffe9de,1.45);fill.position.set(-1,3,8);world.add(fill);}')
    html=once(html,'v11.14 · sculpted hair & silhouette refinement','v11.15 · native portrait & cloth shaping')
    html=html.replace('Maker v11.14','Maker v11.15').replace('MAKER v11.14','MAKER v11.15').replace("version:'v11.14'","version:'v11.15'").replace('version:11.14','version:11.15')
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_14_REFERENCE_REFINEMENT','SWYRL_ENGINE_DEPLOY_MARKER: V11_15_NATIVE_SURFACE_STUDY')
    return html
