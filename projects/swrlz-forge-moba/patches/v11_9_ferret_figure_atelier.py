"""§E v11.9 original model refinement: append-only native scene and editable panel geometry."""
import json
import re
from pathlib import Path

def once(text, old, new):
    n=text.count(old)
    if n!=1:
        raise AssertionError(f"v11.9 integration anchor count={n}: {old[:90]!r}")
    return text.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    scene=json.loads((root/'scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json').read_text('utf-8'))
    parts=scene['project']['modelAtelier']['parts']
    assert scene['version']==11.9 and len(parts)==811
    assert len({p['id'] for p in parts})==811
    assert sum(p.get('surfaceStyle')=='pinata-twisted' for p in parts)==2
    assert sum(p.get('surfaceStyle')=='anatomy-smooth' for p in parts)==6
    assert sum(p.get('surfaceStyle')=='fabric-panel' for p in parts)==8
    for ferret in (p for p in parts if p.get('surfaceStyle')=='pinata-twisted'):
        assert ferret['layers']==36 and ferret['facets']==8
        radii=ferret['radii']
        assert radii[0]<.15 and max(radii)>.70 and radii[-1]<.25
    match=r'const MODEL_ATELIER_CANONICAL_PROJECT=.*?;\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    data='const MODEL_ATELIER_CANONICAL_PROJECT='+json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'
    html,n=re.subn(match,lambda _:data,html,count=1,flags=re.DOTALL)
    assert n==1,'v11.9 scene insertion anchor missing'
    code=(root/'runtime/model_atelier_drape_v11_9.js').read_text('utf-8')
    anchor="    if(part.kind==='loft'&&part.surfaceStyle==='pinata-twisted')return atelierPinataTwist(part);"
    html=once(html,anchor,code+"\n    if(part.kind==='loft'&&part.surfaceStyle==='fabric-panel')return atelierFabricPanel(part);\n"+anchor)
    html=once(html,'V11_8_TWISTED_SCULPT_STUDIO','V11_9_FERRET_FIGURE_ATELIER')
    html=html.replace('Maker v11.8','Maker v11.9').replace('MAKER v11.8','MAKER v11.9')
    html=html.replace("version:'v11.8'","version:'v11.9'").replace('version:11.8','version:11.9')
    html=once(html,'v11.8 · twisted sculpt studio','v11.9 · figure and piñata creature atelier')
    # Taller practical mobile viewport; local inspector retains full scroll and tap targets.
    style="""\n/* §E v11.9: model-first mobile canvas; controls scroll independently. */
@media (max-width:900px),(pointer:coarse){
 .atelier-scene{flex:1 1 auto;min-height:64dvh;max-height:none}
 .atelier-inspector{flex:0 0 auto;height:19dvh;min-height:112px;max-height:23dvh;overflow-y:auto}
 .model-atelier-body{min-height:0;overflow:hidden}
 #modelAtelierParts{min-height:58px;max-height:74px}
}
"""
    html=once(html,'/* v11.8 procedural sculpt tools:',style+'/* v11.8 procedural sculpt tools:')
    return html
