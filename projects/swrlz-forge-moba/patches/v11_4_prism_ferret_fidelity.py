"""§E v11.4 append-only geometry and canonical-model refinement.

Preserve original v11.3 runtime and reference scene unchanged. Upgrade only the
generated editor with curved tapered geometry and route Projects to a distinct
v11.4 original authored variant; historical v11.3 native assets remain.
"""
import json
import re
from pathlib import Path


def once(s, old, replacement):
    n=s.count(old)
    if n != 1:
        raise AssertionError(f'§E v11.4 integration expected one {old[:65]!r}, found {n}')
    return s.replace(old,replacement,1)


def apply(html):
    root=Path(__file__).resolve().parent.parent
    path=root/'scenes/model-atelier-prism-jester-ferret-v11-4.swyrl.json'
    scene=json.loads(path.read_text(encoding='utf-8'))
    parts=scene['project']['modelAtelier']['parts']
    assert scene['project']['canonicalId']=='model-atelier-prism-jester'
    assert scene['project']['modelAtelier']['schema']=='swyrl-model-atelier-v1'
    assert len(parts)==303 and sum(p['kind']=='loft' for p in parts)==2
    assert {'Azure frost','Coral flare','Character'} <= {p['group'] for p in parts}
    match=r'const MODEL_ATELIER_CANONICAL_PROJECT=.*?;\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    replacement='const MODEL_ATELIER_CANONICAL_PROJECT='+json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'
    html,n=re.subn(match,lambda _:replacement,html,count=1,flags=re.DOTALL)
    assert n==1,'Unable to upgrade v11.3 canonical starter with separate v11.4 project'
    html=once(html,
      "const MODEL_ATELIER_KINDS=['sphere','box','cone','cylinder'];",
      "const MODEL_ATELIER_KINDS=['sphere','box','cone','cylinder','loft'];")
    check="    return ['position','rotation','scale'].every(key=>"
    guard="""    if(p.kind==='loft'&&(!Array.isArray(p.path)||p.path.length<2||p.path.length>40
      ||!Array.isArray(p.radii)||p.radii.length!==p.path.length
      ||p.path.some(v=>!Array.isArray(v)||v.length!==3||v.some(n=>!Number.isFinite(n)||Math.abs(n)>100))
      ||p.radii.some(n=>!Number.isFinite(n)||n<.025||n>5)))return false;
"""
    html=once(html,check,guard+check)
    script=(root/'runtime/model_atelier_organic_v11_4.js').read_text(encoding='utf-8')
    html=once(html,"  function geometry(part){\n    switch(part.kind){",
         script+"\n  function geometry(part){\n    if(part.kind==='loft')return atelierOrganicLoft(part);\n    switch(part.kind){")
    html=once(html,"case 'cone':return new THREE.ConeGeometry(1,1,9,1);","case 'cone':return new THREE.ConeGeometry(1,1,14,1);")
    html=once(html,"case 'cylinder':return new THREE.CylinderGeometry(1,1,1,10,1);","case 'cylinder':return new THREE.CylinderGeometry(1,1,1,16,1);")
    html=once(html,"default:return new THREE.SphereGeometry(1,16,12);","default:return new THREE.SphereGeometry(1,30,22);")
    # Loft vertices already carry sRGB-correct THREE.Color values; white base
    # avoids multiplying cyan/coral twice and darkening the actual piñata bodies.
    html=once(html,"new THREE.MeshStandardMaterial({color:col,roughness:",
        "new THREE.MeshStandardMaterial({color:part.kind==='loft'?new THREE.Color('#ffffff'):col,roughness:")
    html=once(html,"metalness:part.material==='metal'?.68:.05,side:THREE.DoubleSide",
        "metalness:part.material==='metal'?.68:.05,vertexColors:part.kind==='loft',side:THREE.DoubleSide")
    html=once(html,"<option>cylinder</option></select>","<option>cylinder</option><option>loft</option></select>")
    html=once(html,"    if(index!==null)p[key][index]=next;else p[key]=next;",
        "    if(key==='kind'&&next==='loft'&&(!Array.isArray(p.path)||p.path.length<2)){p.path=[[0,-.3,0],[0,.3,0]];p.radii=[.16,.12];}\n    if(index!==null)p[key][index]=next;else p[key]=next;")
    html=once(html,"V11_3_MODEL_ATELIER_PRISM_JESTER","V11_4_PRISM_FERRET_FIDELITY")
    html=html.replace("Maker v11.3","Maker v11.4").replace("MAKER v11.3","MAKER v11.4")
    html=html.replace("version:'v11.3'","version:'v11.4'").replace("version:11.3","version:11.4")
    html=once(html,"// MODEL_ATELIER_V11_3_BEGIN","// MODEL_ATELIER_V11_4_FERRET_FIDELITY\n// MODEL_ATELIER_V11_3_BEGIN")
    return html
