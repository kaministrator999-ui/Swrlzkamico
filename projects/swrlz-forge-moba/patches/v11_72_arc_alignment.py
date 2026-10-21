"""§E v11.72: mesh-sized axis arcs and calibrated rotation touch geometry."""
import json
from pathlib import Path

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_71_ARC_ROTATION_RULER'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_72_ROTATION_ARC_ALIGNMENT'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='

def once(html,old,new):
    count=html.count(old)
    assert count==1,(old[:130],count)
    return html.replace(old,new,1)

def scene(html):
    assert html.count(CANONICAL)==1
    source=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(source)
    return source[:end]

def apply(html):
    initial=scene(html)
    js=(Path(__file__).resolve().parents[1]/'runtime/model_atelier_arc_alignment_v11_72.js').read_text(encoding='utf-8')
    html=once(html,'function atelierMeshGizmoBuild(){',
        js+'\nfunction atelierMeshGizmoBuild(){')
    # Replace only runtime dispatch: old v11.71 functions remain in lineage
    # but all active paths use calibrated object-relative behavior.
    html=once(html,' atelierArcBuild(root);',' atelierArcCalibratedBuild(root);')
    html=once(html,' if(atelierArcDown(e))return true;',' if(atelierArcCalibratedDown(e))return true;')
    html=once(html,' const current=atelierArcPointerAngle(d,e);',
        ' const current=atelierArcCalibratedPointerAngle(d,e);')
    # The readout in v11.71 called a last *gesture delta* an absolute angle,
    # despite the arc bead resetting to zero for the next gesture.
    html=once(html,
      " if(output)output.textContent=(amount>=0?'+':'')+(amount*180/Math.PI).toFixed(1)+'°';",
      " if(output){const recent=(atelierMeshDrag?.arc||atelierArcLastAxis===atelierMeshAxis)?amount:0;\n"
      "  output.textContent=(atelierMeshDrag?.arc?'Δ ':'Last Δ ')+(recent>=0?'+':'')+(recent*180/Math.PI).toFixed(1)+'°';}")
    html=once(html,
      ' atelierArcLast=d.amount;\n if(Math.abs(d.amount)<1e-6){',
      ' atelierArcLast=d.amount;atelierArcLastAxis=d.axis;\n if(Math.abs(d.amount)<1e-6){')
    html=once(html,
      "'<span>⤾ Rotation arc <b data-arc-axis>X</b></span>'+",
      "'<span>⤾ Rotation Δ <b data-arc-axis>X</b></span>'+")
    for before,after in (
       (OLD,NEW),
       ('ENGINE · MAKER v11.71','ENGINE · MAKER v11.72'),
       ('v11.71 · arc rotation ruler','v11.72 · aligned rotation ruler'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.71'","window.SWRLZ_FORGE_BUILD={version:'v11.72'"),
       ('<title>§wyrl§ Engine · Maker v11.71</title>','<title>§wyrl§ Engine · Maker v11.72</title>')
    ):
       html=once(html,before,after)
    assert scene(html)==initial
    assert html.count(NEW)==1
    assert html.count('function atelierArcCalibratedBuild(root)')==1
    assert html.count('function atelierArcCalibratedDown(e)')==1
    return html
