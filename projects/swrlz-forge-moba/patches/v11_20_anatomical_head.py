"""Append section-built anatomical heads and native section authoring."""
from pathlib import Path
import json,re

def once(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parent.parent
 scene=json.loads((root/'scenes/model-atelier-festival-anatomy-v11-20.swyrl.json').read_text())
 encoded=json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 pattern=r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)'
 m=re.search(pattern,html,re.S);assert m
 html=html[:m.start()]+'const MODEL_ATELIER_CANONICAL_PROJECT='+encoded+';\n'+html[m.end():]
 html=once(html,'  function refreshList(){',(root/'runtime/model_atelier_anatomy_v11_20.js').read_text()+'\n  function refreshList(){')
 html=once(html,"if(s==='portrait'&&p.portraitFinish)","if(s==='portrait'&&p.headAnatomy)return atelierAnatomicalHead(p);if(s==='portrait'&&p.portraitFinish)")
 html=once(html,'  function checkPart(p){','  function checkPart(p){\n    if(!atelierHeadAnatomyValid(p))return false;')
 html=once(html,"if(key==='kind'){delete p.portraitFinish;","if(key==='kind'){delete p.headAnatomy;delete p.portraitFinish;")
 html=once(html,"if(p.kind==='sphere'&&values.surfaceStyle!=='portrait-head')values.portraitFinish=undefined;","if(p.kind==='sphere'&&values.surfaceStyle!=='portrait-head'){values.portraitFinish=undefined;values.headAnatomy=undefined;}")
 html=once(html,'atelierPortraitRefresh();','atelierPortraitRefresh();atelierHeadAnatomyRefresh();')
 html=once(html,'atelierPortraitInstall();','atelierPortraitInstall();atelierHeadAnatomyInstall();')
 deck='''<section id="modelAtelierHeadAnatomy" hidden><h3>Anatomical head sections</h3><label>Skull, cheeks, jaw and chin · [height, half-width, front, back]<textarea id="modelAtelierHeadSections" rows="8"></textarea></label><label>Facial plane<input id="modelAtelierHeadPlane" type="number" min="0" max="1" step=".05"></label><label>Nose projection<input id="modelAtelierHeadNose" type="number" min="0" max=".3" step=".01"></label><button id="modelAtelierHeadAnatomyApply">Apply anatomical head</button></section>'''
 html=once(html,'<section id="modelAtelierPortraitFinish"',deck+'<section id="modelAtelierPortraitFinish"')
 html=html.replace('v11.19 · portrait & body polish','v11.20 · anatomical head studio').replace('Maker v11.19','Maker v11.20').replace('MAKER v11.19','MAKER v11.20').replace("version:'v11.19'","version:'v11.20'").replace('version:11.19','version:11.20')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_19_PORTRAIT_BODY_POLISH','SWYRL_ENGINE_DEPLOY_MARKER: V11_20_ANATOMICAL_HEAD')
 return html
