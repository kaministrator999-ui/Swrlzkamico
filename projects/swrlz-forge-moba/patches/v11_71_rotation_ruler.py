"""§E v11.71: native 3-axis curved rotation ruler and draggable angle beads."""
import json
from pathlib import Path

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_70_PRECISION_GIZMO_TOOLBAR'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_71_ARC_ROTATION_RULER'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='
def once(html,old,new):
    n=html.count(old)
    assert n==1,(old[:130],n)
    return html.replace(old,new,1)
def scene(html):
    assert html.count(CANONICAL)==1
    data=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(data)
    return data[:end]
def apply(html):
    original=scene(html)
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/model_atelier_rotation_arc_v11_71.js').read_text(encoding='utf-8')
    css=(root/'runtime/model_atelier_rotation_arc_v11_71.css').read_text(encoding='utf-8')
    html=once(html,'function atelierMeshGizmoBuild(){',js+'\nfunction atelierMeshGizmoBuild(){')
    html=once(html,
      " for(const [axis,color] of [['x',0xff666b],['y',0x6cf2a8],['z',0x6baaff]]){\n  const direction=",
      " for(const [axis,color] of [['x',0xff666b],['y',0x6cf2a8],['z',0x6baaff]]){\n  if(atelierMeshMode==='rotate')continue;\n  const direction=")
    html=once(html,' atelierMeshGizmo=root;\n',' atelierMeshGizmo=root;\n atelierArcBuild(root);\n')
    html=once(html,'function atelierMeshGizmoClear(){','function atelierMeshGizmoClear(){\n atelierArcReset();')
    html=once(html,
      'function atelierMeshGizmoDown(e){','function atelierMeshGizmoDown(e){\n if(atelierArcDown(e))return true;')
    html=once(html,
      'function atelierMeshGizmoMove(e){','function atelierMeshGizmoMove(e){\n if(atelierArcMove(e))return true;')
    html=once(html,
      'function atelierMeshGizmoUp(e){','function atelierMeshGizmoUp(e){\n if(atelierArcUp(e))return true;')
    html=once(html,
      ' atelierMeshPrecisionInstall(strip);\n atelierViewportTopArrange(panel);',
      ' atelierMeshPrecisionInstall(strip);\n atelierArcInstall(strip);\n atelierViewportTopArrange(panel);')
    html=once(html,
      "  if(btn.dataset.mode){atelierMeshMode=btn.dataset.mode;atelierMeshAxis='x';atelierMeshPrecisionRefresh();}",
      "  if(btn.dataset.mode){atelierMeshMode=btn.dataset.mode;atelierMeshAxis='x';atelierMeshPrecisionRefresh();atelierArcReadout();}")
    html=once(html,
      "  else if(btn.dataset.axis){atelierMeshAxis=btn.dataset.axis;}",
      "  else if(btn.dataset.axis){atelierMeshAxis=btn.dataset.axis;atelierArcReadout();}")
    # Existing v11.69 per-pointer painting is reused unchanged for rotation.
    assert '</head>' in html
    html=html.replace('</head>','<style id="atelierArcV1171">'+css+'</style>\n</head>',1)
    for old,new in (
        (OLD,NEW),
        ('ENGINE · MAKER v11.70','ENGINE · MAKER v11.71'),
        ('v11.70 · precision mesh controls','v11.71 · arc rotation ruler'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.70'","window.SWRLZ_FORGE_BUILD={version:'v11.71'"),
        ('<title>§wyrl§ Engine · Maker v11.70</title>','<title>§wyrl§ Engine · Maker v11.71</title>')
    ):html=once(html,old,new)
    assert scene(html)==original,'Original model changed'
    assert html.count(NEW)==1
    assert html.count('function atelierArcBuild(root)')==1
    assert html.count('function atelierArcMove(e)')==1
    return html
