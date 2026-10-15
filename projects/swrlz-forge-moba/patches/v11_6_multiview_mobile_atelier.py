"""§E v11.6 additive improvement to native multi-view character and mobile editor surface."""
import json,re
from pathlib import Path

def apply(html):
    root=Path(__file__).resolve().parent.parent
    scene=json.loads((root/'scenes/model-atelier-prism-jester-festival-v11-6.swyrl.json').read_text(encoding='utf-8'))
    parts=scene['project']['modelAtelier']['parts']
    assert len(parts)==653 and len({x['id'] for x in parts})==653
    assert sum(x['kind']=='loft' for x in parts)==2
    pat=r'const MODEL_ATELIER_CANONICAL_PROJECT=.*?;\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    repl='const MODEL_ATELIER_CANONICAL_PROJECT='+json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'
    html,count=re.subn(pat,lambda _:repl,html,count=1,flags=re.DOTALL)
    assert count==1,'v11.6 canonical model anchor missing'
    assert html.count('V11_5_FESTIVAL_LOFT_ATELIER')==1
    html=html.replace('V11_5_FESTIVAL_LOFT_ATELIER','V11_6_MULTIVIEW_FESTIVAL_ATELIER',1)
    html=html.replace('v11.5 · festival loft atelier','v11.6 · multi-view festival studio',1)
    html=html.replace('Maker v11.5','Maker v11.6').replace('MAKER v11.5','MAKER v11.6')
    html=html.replace("version:'v11.5'","version:'v11.6'").replace('version:11.5','version:11.6')
    return html
