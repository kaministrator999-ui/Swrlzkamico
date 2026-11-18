"""§E v11.512 proposal: native Trigger gizmo capture and headset-facing menu.
Not active until appended to source-manifest and resealed from a real build.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_512_TRIGGER_GIZMOS_MENU_FACING"

def once(html,old,new):
    n=html.count(old)
    if n!=1: raise AssertionError(("v11.512 anchor",old[:100],n))
    return html.replace(old,new,1)

def apply(html):
    assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_511_MODEL_DOCK_VISIBILITY" in html
    src=(ROOT/"runtime/model_vr_trigger_gizmo_v11_512.js").read_text("utf8")
    assert "SE512_MODEL_VR_TRIGGER_GIZMO_END" in src
    html=once(html,"installPerformanceSettings();se189InstallPerfUI();",
              src+"\ninstallPerformanceSettings();se189InstallPerfUI();")
    for a,b in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_511_MODEL_DOCK_VISIBILITY",MARKER),
      ("ENGINE · MAKER v11.511","ENGINE · MAKER v11.512"),
      ("v11.511 · restore Modeling rail and inspector layout",
       "v11.512 · trigger capture for VR gizmos and user-facing world menus"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.511'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.512'"),
      ("<title>§wyrl§ Engine · Maker v11.511</title>",
       "<title>§wyrl§ Engine · Maker v11.512</title>")
    ):html=once(html,a,b)
    old=" source.engine='§wyrl§ Engine · Maker v11.511';source.version=11.511;"
    assert html.count(old)==5,("model provenance",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.512';source.version=11.512;")
    tag="const SE_RELEASE_NOTES="
    at=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes["history"]=[x for x in notes.get("history",[]) if x.get("version")!="v11.511"]
    notes["history"].insert(0,{"version":"v11.511","changes":notes.get("changes",[])})
    notes.update(version="v11.512",date="2026-11-18",
      title="Native WebXR Trigger gizmo capture and world menu facing",
      changes=[
       "Controller Trigger directly captures an aim-hovered visible transform gizmo; native Move, Rotate, Scale and Grab-axis previews use existing skin-safe model transactions and one-step Undo.",
       "Trigger release completes one native edit and suppresses the otherwise generated selection click. Cancel, tracking loss and XR cleanup discard pending previews.",
       "Movable immersive VR console maintains its placed world position while continuously facing the headset for readable front-side controls.",
       "Existing Grip/free grab, account project data, UV texture, and browser 2D editing behavior are untouched."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[at+n:]
