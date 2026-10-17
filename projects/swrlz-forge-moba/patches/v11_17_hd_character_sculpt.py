"""Native HD surface construction, physical finish and clean 2k render export."""
from pathlib import Path
import json,re

def once(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b,1)

def apply(html):
    r=Path(__file__).resolve().parent.parent
    scene=json.loads((r/'scenes/model-atelier-festival-hd-v11-17.swyrl.json').read_text())
    encoded=json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    pat=r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)';m=re.search(pat,html,re.S);assert m
    html=html[:m.start()]+'const MODEL_ATELIER_CANONICAL_PROJECT='+encoded+';\n'+html[m.end():]
    html=once(html,'  function material(part){','  function atelierPreviousMaterial(part){')
    html=once(html,'  function refreshList(){',(r/'runtime/model_atelier_hd_v11_17.js').read_text()+'\n  function refreshList(){')
    html=once(html,'  function geometry(part){','  function geometry(part){\n    const hd=atelierHDGeometry(part);if(hd)return hd;')
    html=once(html,'mesh.geometry?.dispose();mesh.material?.dispose();',"mesh.geometry?.dispose();if(!mesh.material?.userData?.atelierHDMaterial)mesh.material?.dispose();")
    html=once(html,'wipeModel();world?.traverse',"wipeModel();for(const m of atelierHDMaterials.values())m.dispose();atelierHDMaterials.clear();world?.traverse")
    html=once(html,'renderer.render(world,camera);raf=requestAnimationFrame(loop);', 'if(!atelierHDEnabled||atelierHDDirty||atelierAssemblyPlaying){renderer.render(world,camera);atelierHDDirty=false;}raf=requestAnimationFrame(loop);')
    html=once(html,'    camera.lookAt(target);\n  }\n  function point','    camera.lookAt(target);atelierHDDirty=true;\n  }\n  function point')
    html=once(html,'camera.aspect=w/h;camera.updateProjectionMatrix();','camera.aspect=w/h;camera.updateProjectionMatrix();atelierHDDirty=true;')
    html=once(html,'Math.min(.08,Math.max(0,(now-atelierAssemblyLast)/1000))','atelierHDFrameDelta(now,atelierAssemblyLast)')
    html=once(html,'function atelierApplyAssemblyTime(time){','function atelierApplyAssemblyTime(time){\n  atelierHDDirty=true;')
    html=once(html,'function atelierDensityRefresh(){','function atelierDensityRefresh(){\n atelierHDDirty=true;')
    html=once(html,'  function checkPart(p){', '''  function checkPart(p){
    if(p?.hdFinish!==undefined){const f=p.hdFinish;if(!f||typeof f!=='object'||Array.isArray(f)||Object.keys(f).length!==2||typeof f.style!=='string'||!Object.hasOwn(atelierHDStyles,f.style)||!atelierHDStyles[f.style].includes(p.kind)||!Number.isFinite(f.relief)||f.relief<0||f.relief>1||p.kind==='loft'&&(!Array.isArray(p.path)||!Array.isArray(p.radii))||f.style==='portrait'&&p.surfaceStyle!=='portrait-head'||f.style==='paper'&&p.surfaceStyle!=='paper-plume')return false;}''')
    html=once(html,'d.u>96','d.u>256');html=once(html,'d.v>64','d.v>192')
    html=once(html,'n<.001||n>5','n<.00025||n>5')
    html=once(html,'equal-length radii from 0.025 to 5.','equal-length radii from 0.00025 to 5.')
    html=html.replace('whole-number samples (6–96, 4–64)','whole-number samples (6–256, 4–192)')
    html=once(html,'id="modelAtelierDensityU" type="number" min="6" max="96"','id="modelAtelierDensityU" type="number" min="6" max="256"')
    html=once(html,'id="modelAtelierDensityV" type="number" min="4" max="64"','id="modelAtelierDensityV" type="number" min="4" max="192"')
    html=once(html,'atelierSurfaceRefresh();atelierDensityRefresh();','atelierSurfaceRefresh();atelierDensityRefresh();atelierHDRefresh();')
    html=once(html,'atelierSurfaceInstall();atelierDensityInstall();','atelierSurfaceInstall();atelierDensityInstall();atelierHDInstall();')
    html=once(html,"const high=$m('DensityPreset').value==='portrait';", "const choice=$m('DensityPreset').value;if(choice==='hd'){atelierHDRestoreSampling();signalEdited();status('Authored HD sampling restored.');return;}const high=choice==='portrait';")
    html=once(html,'<option value="mobile">Mobile · around 27k triangles</option><option value="portrait" selected>Close-up · higher detail</option>','<option value="hd" selected>HD sculpt</option><option value="mobile">Lighter preview</option><option value="portrait">Standard detail</option>')
    html=once(html,"if(key==='kind'){", "if(key==='kind'){delete p.hdFinish;")
    html=once(html,"if(p.kind==='sphere'&&values.surfaceStyle!=='portrait-head')values.faceSculpt=undefined;", "if(p.kind==='sphere'&&values.surfaceStyle!=='portrait-head'){values.faceSculpt=undefined;if(p.hdFinish?.style==='portrait')values.hdFinish=undefined;}")
    choices=[('none','Original surface'),('portrait','Sculpted portrait'),('eye','Almond eye'),('iris','Radial iris'),('ear','Ear cartilage'),('wrap','Braided fabric wrap'),('hair','Swept hair strands'),('skin','Smooth anatomy'),('lip','Sculpted lip'),('cloth','Embroidered silk'),('sock','Ribbed draped sock'),('leather','Polished leather'),('bow','Folded satin bow'),('paper','Layered crepe paper'),('leaf','Creased paper leaf')]
    opts=''.join(f'<option value="{a}">{b}</option>' for a,b in choices)
    deck='<section id="modelAtelierHDEditor" hidden><h3>HD surface finish</h3><label>Construction<select id="modelAtelierHDStyle">'+opts+'</select></label><label>Relief strength<input id="modelAtelierHDRelief" type="number" min="0" max="1" step=".05" value=".7"></label><label style="display:flex;align-items:center;gap:8px"><input id="modelAtelierHDSampling" type="checkbox" checked style="width:20px;height:20px;margin:0"> Use HD sampling</label><button id="modelAtelierHDApply">Apply HD finish</button><button id="modelAtelierHDMatch">Apply to matching spline surfaces</button></section>'
    trim='<details><summary>Fit trim to cloth</summary><label>Cloth panel<select id="modelAtelierHDTrimPanel"></select></label><label>Across panel (−1 left, +1 right)<input id="modelAtelierHDTrimU" type="number" min="-1" max="1" step=".05" value="1"></label><label>Start along panel<input id="modelAtelierHDTrimStart" type="number" min="0" max=".4" step=".02" value=".12"></label><label>Trim radius<input id="modelAtelierHDTrimRadius" type="number" min=".0005" max=".02" step=".0005" value=".003"></label><button id="modelAtelierHDFitTrim">Fit selected spline to cloth</button></details>'
    deck=deck.replace('</section>',trim+'</section>')
    html=once(html,'<section id="modelAtelierDensityEditor"',deck+'<section id="modelAtelierDensityEditor"')
    html=once(html,'<button id="modelAtelierOBJ">Export mesh OBJ</button>','<button id="modelAtelierOBJ">Export mesh OBJ</button><button id="modelAtelierRenderPNG">Render PNG · 2k</button>')
    html=once(html,'v11.16 · facial contours & mobile mesh detail','v11.17 · HD character sculpt & studio')
    html=html.replace('Maker v11.16','Maker v11.17').replace('MAKER v11.16','MAKER v11.17').replace("version:'v11.16'","version:'v11.17'").replace('version:11.16','version:11.17')
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_16_CHARACTER_DETAIL_BUDGET','SWYRL_ENGINE_DEPLOY_MARKER: V11_17_HD_CHARACTER_SCULPT')
    return html
