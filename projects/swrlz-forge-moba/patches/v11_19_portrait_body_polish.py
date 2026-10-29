"""Append the owner-requested portrait and upper-body polish without changing history."""
from pathlib import Path
import json,re

def once(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    scene=json.loads((root/'scenes/model-atelier-festival-polish-v11-19.swyrl.json').read_text())
    encoded=json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    pattern=r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    m=re.search(pattern,html,re.S);assert m
    html=html[:m.start()]+'const MODEL_ATELIER_CANONICAL_PROJECT='+encoded+';\n'+html[m.end():]
    html=once(html,'  function refreshList(){',(root/'runtime/model_atelier_portrait_v11_19.js').read_text()+'\n  function refreshList(){')
    html=once(html,"if(s==='crown')return atelierReferenceCrown(p);", "if(s==='portrait'&&p.portraitFinish)return atelierPortraitFinish(p);if(s==='crown')return atelierReferenceCrown(p);")
    html=once(html,'  function checkPart(p){', '''  function checkPart(p){
    if(p?.portraitFinish!==undefined){const f=p.portraitFinish;if(p.kind!=='sphere'||p.surfaceStyle!=='portrait-head'||p.hdFinish?.style!=='portrait'||!f||typeof f!=='object'||Array.isArray(f)||Object.keys(f).length!==3||!['chinLift','noseDefinition','warmth'].every(k=>Number.isFinite(f[k])&&f[k]>=0&&f[k]<=(k==='chinLift'?.2:1)))return false;}''')
    html=once(html,"if(key==='kind'){delete p.legAnatomy;", "if(key==='kind'){delete p.portraitFinish;delete p.legAnatomy;")
    html=once(html,"  if(p.kind==='sphere'&&p.hdFinish?.style==='crown'", "  if(p.kind==='sphere'&&values.surfaceStyle!=='portrait-head')values.portraitFinish=undefined;\n  if(p.kind==='sphere'&&p.hdFinish?.style==='crown'")
    html=once(html,'atelierReferenceLegRefresh();','atelierReferenceLegRefresh();atelierPortraitRefresh();')
    html=once(html,'atelierReferenceLegInstall();','atelierReferenceLegInstall();atelierPortraitInstall();')
    deck='''<section id="modelAtelierPortraitFinish" hidden><h3>Portrait finish</h3><label>Shorter, softer chin<input id="modelAtelierChinLift" type="number" min="0" max=".2" step=".01"></label><label>Nose definition<input id="modelAtelierNoseDefinition" type="number" min="0" max="1" step=".05"></label><label>Skin warmth<input id="modelAtelierSkinWarmth" type="number" min="0" max="1" step=".05"></label><button id="modelAtelierPortraitApply">Apply portrait finish</button></section><section id="modelAtelierFaceFitDeck" hidden><h3>Fit facial contour</h3><label>Surface offset<input id="modelAtelierFaceFitOffset" type="number" min="0" max=".01" step=".0005" value=".001"></label><button id="modelAtelierFaceFit">Fit contour to head</button></section>'''
    html=once(html,'<section id="modelAtelierLegAnatomy"',deck+'<section id="modelAtelierLegAnatomy"')
    html=once(html,'v11.18 · corrected legs & reference portrait','v11.19 · portrait & body polish')
    html=html.replace('Maker v11.18','Maker v11.19').replace('MAKER v11.18','MAKER v11.19').replace("version:'v11.18'","version:'v11.19'").replace('version:11.18','version:11.19')
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_18_LEG_REFERENCE_CORRECTION','SWYRL_ENGINE_DEPLOY_MARKER: V11_19_PORTRAIT_BODY_POLISH')
    return html
