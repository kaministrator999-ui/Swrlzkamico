"""§E v11.7 governed layered-piñata model sculpt, preserving native histories."""
import json
import re
from pathlib import Path

def replace_once(text, old, new):
    n=text.count(old)
    if n!=1:
        raise AssertionError(f'v11.7 integration expected once: {old[:60]!r}; got {n}')
    return text.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    scene=json.loads((root/'scenes/model-atelier-prism-jester-festival-v11-7.swyrl.json').read_text(encoding='utf-8'))
    parts=scene['project']['modelAtelier']['parts']
    assert scene['project']['canonicalId']=='model-atelier-prism-jester'
    assert scene['version']==11.7 and len(parts)==733
    assert len({p['id'] for p in parts})==len(parts)
    lofts=[p for p in parts if p['kind']=='loft']
    assert len(lofts)==2 and all(p.get('surfaceStyle')=='pinata-stacked' and p['layers']==36 for p in lofts)
    assert all(x['group'] in ('Azure frost','Coral flare') for x in lofts)
    pattern=r'const MODEL_ATELIER_CANONICAL_PROJECT=.*?;\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    encoded='const MODEL_ATELIER_CANONICAL_PROJECT='+json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'
    html,n=re.subn(pattern,lambda _:encoded,html,count=1,flags=re.DOTALL)
    assert n==1,'Unable to install v11.7 canonical layered piñata model'
    script=(root/'runtime/model_atelier_pinata_v11_7.js').read_text(encoding='utf-8')
    anchor="  function geometry(part){\n    if(part.kind==='loft')return atelierOrganicLoft(part);"
    html=replace_once(html,anchor,script+"\n  function geometry(part){\n    if(part.kind==='loft'&&part.surfaceStyle==='pinata-stacked')return atelierPinataStack(part);\n    if(part.kind==='loft')return atelierOrganicLoft(part);")
    html=replace_once(html,'V11_6_MULTIVIEW_FESTIVAL_ATELIER','V11_7_STACKED_PINATA_SCULPT')
    html=replace_once(html,'v11.6 · multi-view festival studio','v11.7 · layered piñata sculpture')
    html=html.replace('Maker v11.6','Maker v11.7').replace('MAKER v11.6','MAKER v11.7')
    html=html.replace("version:'v11.6'","version:'v11.7'").replace('version:11.6','version:11.7')
    # Front-on and less overhead. Zoom is set based on screen aspect only on initial open,
    # retaining user orbit/zoom interaction instead of aggressively re-framing each edit.
    assert html.count('orbit={yaw:.3,pitch:.19,distance:9}')==2,'Expected initial orbit and reset-view orbit defaults'
    html=html.replace('orbit={yaw:.3,pitch:.19,distance:9}', 'orbit={yaw:0,pitch:.08,distance:8.2}')
    html=replace_once(html,"camera=new THREE.PerspectiveCamera(44,1,.1,100);cameraUpdate();",
        "camera=new THREE.PerspectiveCamera(44,1,.1,100);orbit.distance=window.innerWidth<=700?10.2:8.2;cameraUpdate();")
    return html
