"""§E v11.70: per-mode precision slider and reorganized mobile viewport tools.

The camera toolbar remains accessible while its advanced options are collapsed.
"""
import json
from pathlib import Path

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_69_DRAG_PREVIEW_RENDER'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_70_PRECISION_GIZMO_TOOLBAR'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='

def once(html,old,new):
    count=html.count(old)
    assert count==1,(old[:125],count)
    return html.replace(old,new,1)

def scene(html):
    assert html.count(CANONICAL)==1
    txt=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(txt)
    return txt[:end]

def apply(html):
    before=scene(html)
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/model_atelier_precision_v11_70.js').read_text(encoding='utf-8')
    css=(root/'runtime/model_atelier_precision_v11_70.css').read_text(encoding='utf-8')
    html=once(html,'function atelierMeshNudge(direction){',js+'\nfunction atelierMeshNudge(direction){')
    # Each mode controls movement for touch dragging AND ± nudge steps.
    html=once(html,
      "const amount=atelierMeshMode==='move'?direction*.1:\n  atelierMeshMode==='rotate'?direction*Math.PI/36:Math.pow(1.1,direction);",
      "const speed=atelierMeshSensitivity();\n const amount=atelierMeshMode==='move'?direction*.1*speed:\n  atelierMeshMode==='rotate'?direction*Math.PI/36*speed:Math.pow(1.1,direction*speed);")
    html=once(html,
      'atelierMeshClamp(pixels*.0009*Math.min(orbit.distance,8),-.45,.45)',
      'atelierMeshClamp(pixels*.0009*Math.min(orbit.distance,8)*atelierMeshSensitivity(d.mode),-.45*atelierMeshSensitivity(d.mode),.45*atelierMeshSensitivity(d.mode))')
    html=once(html,
      'atelierMeshClamp(pixels*.009,-Math.PI,Math.PI)',
      'atelierMeshClamp(pixels*.009*atelierMeshSensitivity(d.mode),-Math.PI,Math.PI)')
    html=once(html,
      'Math.exp(pixels*.009)',
      'Math.exp(pixels*.009*atelierMeshSensitivity(d.mode))')
    html=once(html,
      " viewport.append(strip);atelierMeshStrip=strip;atelierMeshDialogInstall();",
      " viewport.append(strip);atelierMeshStrip=strip;atelierMeshDialogInstall();\n atelierMeshPrecisionInstall(strip);\n atelierViewportTopArrange(panel);")
    html=once(html,
      "  if(btn.dataset.mode){atelierMeshMode=btn.dataset.mode;atelierMeshAxis='x';}",
      "  if(btn.dataset.mode){atelierMeshMode=btn.dataset.mode;atelierMeshAxis='x';atelierMeshPrecisionRefresh();}")
    # Keep the viewport controls' actual nodes and event handlers. The new
    # arrangement uses flex groups and an accessible details disclosure.
    html=once(html,
      " bar.dataset.arranged='1';",
      " bar.dataset.arranged='1';bar.classList.add('atelier-top-organized');")
    assert '</head>' in html
    html=html.replace('</head>','<style id="atelierPrecisionV1170">'+css+'</style>\n</head>',1)
    for old,new in (
        (OLD,NEW),
        ('ENGINE · MAKER v11.69','ENGINE · MAKER v11.70'),
        ('v11.69 · direct live drag rendering','v11.70 · precision mesh controls'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.69'","window.SWRLZ_FORGE_BUILD={version:'v11.70'"),
        ('<title>§wyrl§ Engine · Maker v11.69</title>','<title>§wyrl§ Engine · Maker v11.70</title>')
    ):html=once(html,old,new)
    assert scene(html)==before
    assert html.count(NEW)==1
    assert html.count('function atelierMeshPrecisionInstall(strip)')==1
    assert html.count('function atelierViewportTopArrange(panel)')==1
    return html
