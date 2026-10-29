"""§E v11.73: immediate gizmo switching and visible/tappable rotation rulers.

Overlapping axes honor the deliberately selected axis before nearest-ring ties.
"""
from pathlib import Path
import json

OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_72_ROTATION_ARC_ALIGNMENT'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_73_INSTANT_GIZMO_ROTATION_TOUCH'
CANONICAL='const MODEL_ATELIER_CANONICAL_PROJECT='
def once(html, old, new):
    assert html.count(old)==1,(old[:145],html.count(old))
    return html.replace(old,new,1)
def canonical(html):
    assert html.count(CANONICAL)==1
    raw=html.split(CANONICAL,1)[1]
    _,end=json.JSONDecoder().raw_decode(raw)
    return raw[:end]
def apply(html):
    baseline=canonical(html)
    js=(Path(__file__).resolve().parents[1]/'runtime/model_atelier_gizmo_touch_v11_73.js').read_text(encoding='utf-8')
    html=once(html,'function atelierMeshGizmoBuild(){',js+'\nfunction atelierMeshGizmoBuild(){')
    # The tool click built a new gizmo but awaited an unrelated camera event
    # to paint it; a synchronous WebGL render makes every switch immediate.
    html=once(html,
      "  else if(btn.hasAttribute('data-mesh-hide'))atelierMeshHidden=true;\n  atelierMeshToolbarRefresh();",
      "  else if(btn.hasAttribute('data-mesh-hide'))atelierMeshHidden=true;\n  atelierMeshToolbarRefresh();\n  if(btn.dataset.mode||btn.dataset.axis)atelierMeshPaintModeImmediately();")
    # Draw a thick native 3D tube along the calibrated radius; no extra
    # project geometry, and no 3D raycaster bead-only restriction.
    html=once(html,
      " atelierArcVisualFocus(atelierMeshAxis);\n atelierArcReadout();\n}",
      " atelierArcVisualFocus(atelierMeshAxis);\n atelierArcThickenRulers();\n atelierArcReadout();\n}")
    html=once(html,
      '  item.hit.visible=true;',
      '  item.hit.visible=true;\n  if(item.wideTrack)item.wideTrack.material.opacity=active?.96:.22;')
    html=once(html,
      ' if(atelierArcCalibratedDown(e))return true;',
      ' if(atelierArcEasyDown(e))return true;')
    html=once(html,
      ' atelierArcPosition(d.axis,amount);',
      ' atelierArcPosition(d.axis,(d.arcStartOffset||0)+amount);')
    for old,new in (
      (OLD,NEW),
      ('ENGINE · MAKER v11.72','ENGINE · MAKER v11.73'),
      ('v11.72 · aligned rotation ruler','v11.73 · responsive gizmo touch'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.72'","window.SWRLZ_FORGE_BUILD={version:'v11.73'"),
      ('<title>§wyrl§ Engine · Maker v11.72</title>','<title>§wyrl§ Engine · Maker v11.73</title>')
    ):
       html=once(html,old,new)
    assert canonical(html)==baseline
    assert html.count(NEW)==1
    assert html.count('function atelierMeshPaintModeImmediately()')==1
    assert html.count('function atelierArcPickOnScreen(e)')==1
    return html
