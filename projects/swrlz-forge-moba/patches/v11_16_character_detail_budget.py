"""Saved native mesh density, continuous facial contours and separately measured heroine budget."""
from pathlib import Path
import json,re

def once(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    scene=json.loads((root/'scenes/model-atelier-festival-detail-v11-16.swyrl.json').read_text())
    encoded=json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    pattern=r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    match=re.search(pattern,html,re.S);assert match
    html=html[:match.start()]+'const MODEL_ATELIER_CANONICAL_PROJECT='+encoded+';\n'+html[match.end():]
    html=once(html,'  function refreshList(){',(root/'runtime/model_atelier_density_v11_16.js').read_text()+'\n  function refreshList(){')
    html=once(html,'  function checkPart(p){', '''  function checkPart(p){
    if(p?.meshDensity!==undefined){const d=p.meshDensity;if(!d||typeof d!=='object'||Array.isArray(d)||Object.keys(d).some(k=>!['u','v'].includes(k))||!Number.isInteger(d.u)||d.u<6||d.u>96||!Number.isInteger(d.v)||d.v<4||d.v>64||!['sphere','loft'].includes(p.kind)||['paper-plume','paper-leaf','fabric-panel'].includes(p.surfaceStyle))return false;}
    if(p?.faceSculpt!==undefined){const f=p.faceSculpt;if(p.surfaceStyle!=='portrait-head'||!p.meshDensity||!f||typeof f!=='object'||Array.isArray(f)||Object.keys(f).length!==3||!['nose','socket','cheek'].every(k=>Number.isFinite(f[k])&&f[k]>=0&&f[k]<=(k==='nose'?.25:k==='socket'?.15:.12)))return false;}''')
    html=once(html,'  function geometry(part){','  function geometry(part){\n    if(part.kind===\'sphere\'&&part.meshDensity)return atelierDetailSphere(part);')
    html=once(html,"  if(!checkPart({...p,...values}))", "  if(p.kind==='sphere'&&values.surfaceStyle!=='portrait-head')values.faceSculpt=undefined;\n  if(!checkPart({...p,...values}))")
    html=once(html,'    if(index!==null)p[key][index]=next;else p[key]=next;', "    if(key==='kind'){if(!['sphere','loft'].includes(next))delete p.meshDensity;if(next!=='sphere')delete p.faceSculpt;}\n    if(index!==null)p[key][index]=next;else p[key]=next;")
    html=once(html,'const lengthSegments=Math.min(100,Math.max(12,Math.round(part.segments||48)));','const lengthSegments=part.meshDensity?.u??Math.min(100,Math.max(12,Math.round(part.segments||48)));')
    html=once(html,'const rings=Math.min(24,Math.max(8,Math.round(part.radialSegments||12)));','const rings=part.meshDensity?.v??Math.min(24,Math.max(8,Math.round(part.radialSegments||12)));')
    html=once(html,'const n=32,rings=12,base=new THREE.Color(part.color);','const n=part.meshDensity?.u??32,rings=part.meshDensity?.v??12,base=new THREE.Color(part.color);')
    html=once(html,'base=new THREE.Color(part.color),rows=32,cols=8;','base=new THREE.Color(part.color),rows=part.meshDensity?.u??32,cols=part.meshDensity?.v??8;')
    html=html.replace("part.surfaceStyle==='split-dye-cap'?new THREE.Color('#ffffff')", "(part.surfaceStyle==='split-dye-cap'||part.faceSculpt)?new THREE.Color('#ffffff')")
    html=html.replace("vertexColors:part.surfaceStyle==='split-dye-cap'", "vertexColors:part.surfaceStyle==='split-dye-cap'||!!part.faceSculpt")
    html=once(html,"vertexColors:part.kind==='loft'||part.surfaceStyle==='split-dye-cap',", "vertexColors:part.kind==='loft'||part.surfaceStyle==='split-dye-cap'||!!part.faceSculpt,")
    html=once(html,'    atelierSurfaceRefresh();','    atelierSurfaceRefresh();atelierDensityRefresh();')
    html=once(html,'atelierAssemblyInstall();atelierSurfaceInstall();','atelierAssemblyInstall();atelierSurfaceInstall();atelierDensityInstall();')
    html=once(html,'assemblyStatus:atelierAssemblyStatus,view:', 'density:atelierDensityMeasured,assemblyStatus:atelierAssemblyStatus,view:')
    html=once(html,'metrics:()=>ModelAtelier.metrics(),view:', 'metrics:()=>ModelAtelier.metrics(),density:()=>ModelAtelier.density(),view:')
    global_deck='''<details id="modelAtelierDetailBudget"><summary>Mesh detail &amp; triangle budget</summary><p id="modelAtelierDensityReadout" aria-live="polite"></p><label>Heroine quality<select id="modelAtelierDensityPreset"><option value="mobile">Mobile · around 27k triangles</option><option value="portrait" selected>Close-up · higher detail</option></select></label><button id="modelAtelierDensityPresetApply">Apply heroine detail</button><label style="display:flex;align-items:center;gap:8px"><input id="modelAtelierTopologyView" type="checkbox" style="width:20px;height:20px;margin:0"> Show triangle edges</label><p>Hair and clothes count toward the heroine budget. The two ferrets and bunny are measured separately.</p></details>'''
    html=once(html,'<section id="modelAtelierSurfaceEditor"',global_deck+'<section id="modelAtelierSurfaceEditor"')
    local_deck='''<section id="modelAtelierDensityEditor" hidden><h3>Selected mesh detail</h3><label><span id="modelAtelierDensityLabelU">Around the surface</span><input id="modelAtelierDensityU" type="number" min="6" max="96" step="1"></label><label><span id="modelAtelierDensityLabelV">Vertical rings</span><input id="modelAtelierDensityV" type="number" min="4" max="64" step="1"></label><div id="modelAtelierFaceContours" hidden><h3>Facial contours</h3><label>Nose bridge<input id="modelAtelierFaceNose" type="number" min="0" max=".25" step=".005"></label><label>Eye socket depth<input id="modelAtelierFaceSocket" type="number" min="0" max=".15" step=".005"></label><label>Cheek fullness<input id="modelAtelierFaceCheek" type="number" min="0" max=".12" step=".005"></label></div><button id="modelAtelierDensityApply">Apply mesh detail</button></section>'''
    html=once(html,'<section id="modelAtelierLoftEditor"',local_deck+'<section id="modelAtelierLoftEditor"')
    html=once(html,'v11.15 · native portrait & cloth shaping','v11.16 · facial contours & mobile mesh detail')
    html=html.replace('Maker v11.15','Maker v11.16').replace('MAKER v11.15','MAKER v11.16').replace("version:'v11.15'","version:'v11.16'").replace('version:11.15','version:11.16')
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_15_NATIVE_SURFACE_STUDY','SWYRL_ENGINE_DEPLOY_MARKER: V11_16_CHARACTER_DETAIL_BUDGET')
    return html
