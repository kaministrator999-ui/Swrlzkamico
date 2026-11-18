"""§E v11.512 proposal: Trigger gizmos, menu facing and native indent sculpting.
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
    # §E VR sculpting: positive normal displacement stays outward Pull;
    # negative normal displacement is inward Indent using the same native
    # geometry preview, sparse vertex edits, save and Undo pipeline.
    html=once(html,
      "const SE350_BRUSHES=['push','smooth','flatten','inflate','pinch','translate'];",
      "const SE350_BRUSHES=['push','smooth','flatten','inflate','pinch','translate','indent'];")
    html=once(html,
      "Object.assign(se340XR,{sculptTool:'push',brushRadius:.12,brushStrength:.3,",
      "Object.assign(se340XR,{sculptTool:'push',brushRadius:.12,brushStrength:.3,brushFalloff:'smooth',")
    html=once(html,
      "const result=se350Surface().sculptBegin(hit.id,{operation:s.sculptTool,radius:s.brushRadius,strength:s.brushStrength});",
      "const result=se350Surface().sculptBegin(hit.id,{operation:s.sculptTool==='indent'?'push':s.sculptTool,radius:s.brushRadius,strength:s.sculptTool==='indent'?-Math.abs(s.brushStrength):s.brushStrength});")
    html=once(html,
      "strength:se340XR.brushStrength,smooth:!!se340XR.inputSample?.held['temporary-smooth']",
      "strength:se340XR.sculptTool==='indent'?-Math.abs(se340XR.brushStrength):se340XR.brushStrength,falloff:se340XR.brushFalloff,smooth:!!se340XR.inputSample?.held['temporary-smooth']")
    html=once(html,
      "operation, falloff: 'smooth', plateau: 0, taper: .5, half: false, level: false,",
      "operation, falloff: ['smooth','soft','sharp','flat'].includes(sample.falloff)?sample.falloff:'smooth', plateau: 0, taper: .5, half: false, level: false,")
    html=once(html,
      "['sculpt-push','Push'],['sculpt-smooth','Smooth'],['sculpt-flatten','Flatten'],\n   ['sculpt-inflate','Inflate'],['sculpt-pinch','Pinch'],['sculpt-translate','Translate'],\n   ['brush-radius-minus','Radius −']",
      "['sculpt-push','Pull'],['sculpt-indent','Indent'],['sculpt-smooth','Smooth'],\n   ['sculpt-flatten','Flatten'],['sculpt-inflate','Inflate'],['sculpt-pinch','Pinch'],\n   ['brush-radius-minus','Radius −']")
    html=once(html,
      "['brush-strength-plus','Strength +'],['studio','Studio'],['exit','Exit VR']",
      "['brush-strength-plus','Strength +'],['sculpt-falloff','Falloff'],['exit','Exit VR']")
    html=once(html,
      "function label(item){\n  if(item.id==='index-add')",
      "function label(item){\n  if(item.id==='sculpt-falloff')return 'Falloff: '+(state.brushFalloff||'smooth');\n  if(item.id==='index-add')")
    html=once(html,
      "selectedCount:selectedIds.size,sculptTool:s.sculptTool,brushRadius:s.brushRadius",
      "selectedCount:selectedIds.size,sculptTool:s.sculptTool,brushFalloff:s.brushFalloff,brushRadius:s.brushRadius")
    html=once(html,
      "if(action.startsWith('sculpt-')){const tool=action.slice(7);",
      "if(action==='sculpt-falloff'){const choices=['smooth','soft','sharp','flat'];s.brushFalloff=choices[(choices.indexOf(s.brushFalloff)+1)%choices.length];se340Notice('Sculpt falloff: '+s.brushFalloff);se340SyncUI();return true;}\n if(action.startsWith('sculpt-')){const tool=action.slice(7);")
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
      title="Native Trigger gizmos, world-space menu facing and signed indent sculpting",
      changes=[
       "Controller Trigger directly captures an aim-hovered visible transform gizmo; native Move, Rotate, Scale and Grab-axis previews use existing skin-safe model transactions and one-step Undo.",
       "Trigger release completes one native edit and suppresses the otherwise generated selection click. Cancel, tracking loss and XR cleanup discard pending previews.",
       "Movable immersive VR console maintains its placed world position while continuously facing the headset for readable front-side controls.",
       "Immersive sculpting now offers positive outward Pull and inward Indent with radius, strength and smooth/soft/sharp/flat falloff using the existing native signed displacement operator.",
       "Existing Grip/free grab, account project data, UV texture, and browser 2D editing behavior are untouched."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[at+n:]
