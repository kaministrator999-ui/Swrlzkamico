"""§E v11.5 additive native starter detail and bounded loft profile authoring.

The original v11.3 and v11.4 scenes and their patches remain immutable.
"""
import json
import re
from pathlib import Path

def once(source, old, new):
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"v11.5 expected one anchor, found {count}: {old[:90]!r}")
    return source.replace(old, new, 1)

def apply(html):
    root = Path(__file__).resolve().parent.parent
    scene = json.loads((root / 'scenes/model-atelier-prism-jester-festival-v11-5.swyrl.json').read_text(encoding='utf-8'))
    parts = scene['project']['modelAtelier']['parts']
    assert scene['project']['canonicalId'] == 'model-atelier-prism-jester'
    assert len(parts) == 539 and sum(p['kind'] == 'loft' for p in parts) == 2
    assert len({p['id'] for p in parts}) == len(parts)
    pat = r'const MODEL_ATELIER_CANONICAL_PROJECT=.*?;\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    replacement = 'const MODEL_ATELIER_CANONICAL_PROJECT=' + json.dumps(scene, ensure_ascii=False, separators=(',', ':')).replace('</','<\\/') + ';\n'
    html, count = re.subn(pat, lambda _: replacement, html, count=1, flags=re.DOTALL)
    assert count == 1
    html = once(html, 'const MODEL_ATELIER_LIMIT=400;', 'const MODEL_ATELIER_LIMIT=1200;')
    html = once(html, 'file.size>2_000_000', 'file.size>8_000_000')
    html = once(html, 'JSON below 2 MB.', 'JSON below 8 MB.')
    # Loft control fields are part of the actual native edit inspector, not a separate mock view.
    html = once(html, '<label class="atelier-import">', '''<section id="modelAtelierLoftEditor" hidden aria-label="Organic loft profile editor"><h3>Organic spline profile</h3><p>Edit control points as [x,y,z] rows and matching radii. Maximum 40 knots.</p><label>Curve points (JSON)<textarea id="modelAtelierLoftPath" rows="6" spellcheck="false"></textarea></label><label>Cross-section radii (JSON)<textarea id="modelAtelierLoftRadii" rows="3" spellcheck="false"></textarea></label><button id="modelAtelierApplyLoft" type="button">Apply spline geometry</button></section><label class="atelier-import">''')
    html = once(html, '    updating=false;\n  }\n  function select(id)', '''    const loft=$m('LoftEditor');
    if(loft){loft.hidden=!p||p.kind!=='loft';if(p&&p.kind==='loft'){
      $m('LoftPath').value=JSON.stringify(p.path,null,2);
      $m('LoftRadii').value=JSON.stringify(p.radii);
    }}
    updating=false;
  }
  function select(id)''')
    html = once(html, "    $m('ImportFile').addEventListener('change',e=>importJSON(e.target.files?.[0]));", """    action('ApplyLoft',()=>{
      const p=partById(selection);if(!p||p.kind!=='loft')return;
      try{
        const path=JSON.parse($m('LoftPath').value),radii=JSON.parse($m('LoftRadii').value);
        const candidate={...p,path,radii};
        if(!checkPart(candidate))throw Error('Invalid knots: use 2–40 finite XYZ points within ±100 and equal-length radii from 0.025 to 5.');
        checkpoint();p.path=path;p.radii=radii;signalEdited();select(p.id);
      }catch(error){status('Loft rejected: '+error.message,true);}
    });
    $m('ImportFile').addEventListener('change',e=>importJSON(e.target.files?.[0]));""")
    html = once(html, 'v11.3 · original reference study', 'v11.5 · festival loft atelier')
    html = once(html, 'V11_4_PRISM_FERRET_FIDELITY', 'V11_5_FESTIVAL_LOFT_ATELIER')
    html = html.replace('Maker v11.4','Maker v11.5').replace('MAKER v11.4','MAKER v11.5')
    html = html.replace("version:'v11.4'","version:'v11.5'").replace('version:11.4','version:11.5')
    return html
