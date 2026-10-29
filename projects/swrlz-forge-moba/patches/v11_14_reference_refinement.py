"""Append-only visual refinement; preserve older authored models and attachment behavior."""
from pathlib import Path
import json,re

def once(s,a,b):
 assert s.count(a)==1,(a[:80],s.count(a))
 return s.replace(a,b,1)

def apply(html):
 r=Path(__file__).resolve().parent.parent
 scene=json.loads((r/'scenes/model-atelier-festival-refined-v11-14.swyrl.json').read_text())
 enc=json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 pat=r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)'
 match=re.search(pat,html,re.S);assert match
 html=html[:match.start()]+'const MODEL_ATELIER_CANONICAL_PROJECT='+enc+';\n'+html[match.end():]
 html=once(html,'function atelierReferenceGeometry(part){',(r/'runtime/model_atelier_refinement_v11_14.js').read_text()+'\nfunction atelierReferenceGeometry(part){\n  if(part.kind===\'loft\'&&part.surfaceStyle===\'silken-lock\')return atelierSilkenLock(part);\n  if(part.kind===\'loft\'&&part.surfaceStyle===\'tailored-panel\')return atelierTailoredPanel(part);')
 html=once(html,"const palette=part.group==='Azure frost'?", "const palette=part.paperVariation===true?(part.group==='Azure frost'?['#35c7d8','#4fd4de','#26b7cf','#65dce0','#32c1d8']:['#f66b61','#ff9171','#ec5a5c','#ffac79','#f87c66']):part.group==='Azure frost'?")
 # Deterministic variation retains stable geometry across save/load and exports.
 html=once(html,'const t=(i+.35)/rings,a=(j+(i%2)*.5)*Math.PI*2/facets;', 'const variation=part.paperVariation===true;\n    const t=(i+.35+(variation?.14*Math.sin(i*5.13+j*2.7):0))/rings,a=(j+(i%2)*.5+(variation?.12*Math.sin(i*1.7+j*4.3):0))*Math.PI*2/facets;')
 html=once(html,'width=r*.76,span=.20+.09*Math.sin(t*Math.PI)', 'width=r*.76*(variation?1+.20*Math.sin(i*2.17+j*4.3):1),span=(.20+.09*Math.sin(t*Math.PI))*(variation?1+.22*Math.cos(i*3.1+j*1.7):1)')
 html=once(html,'v11.13 · reference sculpt & living piñatas','v11.14 · sculpted hair & silhouette refinement')
 html=html.replace('Maker v11.13','Maker v11.14').replace('MAKER v11.13','MAKER v11.14').replace("version:'v11.13'","version:'v11.14'").replace('version:11.13','version:11.14')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_13_REFERENCE_ASSEMBLIES','SWYRL_ENGINE_DEPLOY_MARKER: V11_14_REFERENCE_REFINEMENT')
 return html
