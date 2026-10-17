"""Correct the native leg profile and refine the supplied portrait/hair-wrap reference."""
from pathlib import Path
import json,re

def once(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b,1)

def apply(html):
    r=Path(__file__).resolve().parent.parent
    scene=json.loads((r/'scenes/model-atelier-festival-reference-v11-18.swyrl.json').read_text())
    encoded=json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    pattern=r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    m=re.search(pattern,html,re.S);assert m
    html=html[:m.start()]+'const MODEL_ATELIER_CANONICAL_PROJECT='+encoded+';\n'+html[m.end():]
    html=once(html,'  function refreshList(){',(r/'runtime/model_atelier_reference_v11_18.js').read_text()+'\n  function refreshList(){')
    html=once(html,"const atelierHDSampling={portrait:","atelierHDStyles.crown=['sphere'];atelierHDStyles.knot=['sphere'];\nconst atelierHDSampling={crown:[128,80],knot:[96,64],portrait:")
    html=once(html,"if(s==='iris')return atelierHDIris(p);", "if(s==='crown')return atelierReferenceCrown(p);if(s==='knot')return atelierReferenceKnot(p);if(s==='iris')return atelierHDIris(p);")
    html=once(html,"const dark=new THREE.Color('#32243d'),amber=new THREE.Color('#f4b956'),rose=new THREE.Color('#ad4c6b');", "const [dark,amber,rose]=atelierReferenceIrisPalette(p);")
    html=once(html,'  function checkPart(p){', '''  function checkPart(p){
    if(p?.irisPigments!==undefined){const c=p.irisPigments;if(p.kind!=='sphere'||!c||typeof c!=='object'||Array.isArray(c)||Object.keys(c).length!==2||!['upper','lower'].every(k=>/^#[0-9a-fA-F]{6}$/.test(c[k])))return false;}
    if(p?.hdFinish?.style==='crown'&&p.surfaceStyle!=='split-dye-cap')return false;''')
    html=once(html,'    if(p?.irisPigments!==undefined)', '''    if(p?.legAnatomy!==undefined){const a=p.legAnatomy;if(p.kind!=='loft'||p.surfaceStyle!=='anatomy-smooth'||p.path?.length!==6||p.hdFinish?.style!=='skin'||!a||typeof a!=='object'||Array.isArray(a)||Object.keys(a).length!==2||!Number.isFinite(a.calfFullness)||a.calfFullness<0||a.calfFullness>.12||!Number.isFinite(a.shinTaper)||a.shinTaper<0||a.shinTaper>.04)return false;}
    if(p?.irisPigments!==undefined)''')
    html=once(html,'positions.push(v.x,v.y,v.z);uv.push(j/rings,t);', 'if(style===\'skin\'&&p.legAnatomy)v.add(atelierReferenceLegContour(p,center,f,s,c));positions.push(v.x,v.y,v.z);uv.push(j/rings,t);')
    html=once(html,"if(key==='kind'){delete p.hdFinish;", "if(key==='kind'){delete p.legAnatomy;delete p.irisPigments;delete p.hdFinish;")
    html=once(html,"  if(!checkPart({...p,...values}))", "  if(p.kind==='sphere'&&p.hdFinish?.style==='crown'&&values.surfaceStyle!=='split-dye-cap')values.hdFinish=undefined;\n  if(!checkPart({...p,...values}))")
    html=once(html,'checkpoint();Object.assign(p,values);signalEdited();select(p.id);',"checkpoint();Object.assign(p,values);for(const key of Object.keys(values))if(values[key]===undefined)delete p[key];signalEdited();select(p.id);")
    html=once(html,"cloth=p?.surfaceStyle==='tailored-panel'", "cloth=['tailored-panel','fabric-panel'].includes(p?.surfaceStyle)")
    html=once(html,"else if(p.surfaceStyle==='tailored-panel')values=", "else if(['tailored-panel','fabric-panel'].includes(p.surfaceStyle))values=")
    html=once(html,"p.panelCamber??(p.panelAxis==='depth'?.055:.085)","p.panelCamber??(p.surfaceStyle==='fabric-panel'?.035:p.panelAxis==='depth'?.055:.085)")
    html=once(html,'p.panelPleat??.012','p.panelPleat??(p.surfaceStyle===\'fabric-panel\'?.008:.012)')
    html=once(html,'atelierHDRefresh();','atelierHDRefresh();atelierReferenceFinishRefresh();atelierReferenceLegRefresh();')
    html=once(html,'atelierHDInstall();','atelierHDInstall();atelierReferenceFinishInstall();atelierReferenceLegInstall();')
    html=once(html,'<option value="wrap">Braided fabric wrap</option>','<option value="wrap">Braided fabric wrap</option><option value="knot">Knotted hair wrap</option><option value="crown">Swept split-dye crown</option>')
    leg_deck='<section id="modelAtelierLegAnatomy" hidden><h3>Leg anatomy</h3><label>Posterior calf fullness<input id="modelAtelierCalfFullness" type="number" min="0" max="0.12" step="0.005" value="0"></label><label>Front shin taper<input id="modelAtelierShinTaper" type="number" min="0" max="0.04" step="0.002" value="0"></label><button id="modelAtelierLegApply">Apply leg contours</button></section>'
    deck=leg_deck+'<section id="modelAtelierIrisPigments" hidden><h3>Iris pigments</h3><label>Upper iris<input id="modelAtelierIrisUpper" type="color" value="#ad4c6b"></label><label>Lower iris<input id="modelAtelierIrisLower" type="color" value="#f4b956"></label><button id="modelAtelierIrisApply">Apply iris pigments</button></section>'
    html=once(html,'<section id="modelAtelierDensityEditor"',deck+'<section id="modelAtelierDensityEditor"')
    html=once(html,'v11.17 · HD character sculpt & studio','v11.18 · corrected legs & reference portrait')
    html=html.replace('Maker v11.17','Maker v11.18').replace('MAKER v11.17','MAKER v11.18').replace("version:'v11.17'","version:'v11.18'").replace('version:11.17','version:11.18')
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_17_HD_CHARACTER_SCULPT','SWYRL_ENGINE_DEPLOY_MARKER: V11_18_LEG_REFERENCE_CORRECTION')
    return html
