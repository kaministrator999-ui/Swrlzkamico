"""§E v11.485: replace the assembled Sorting Hat with one sculpted UV-painted cloth mesh."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_485_ONE_CLOTH_SORTING_HAT"

def once(html,old,new,label):
    amount=html.count(old)
    assert amount==1,("v11.485",label,amount,old[:120])
    return html.replace(old,new,1)

def apply(html):
    assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_484_RING_DETAIL_AND_TRANSFORMS" in html
    # This updates only the Sorting Hat starter validation; all 483 model
    # loading, native project routing, save/clone, and other starters persist.
    html=once(html,
        "parts.length<12||parts.length>400||!Array.isArray(scene?.scene?.actors)",
        "parts.length!==1||!Array.isArray(scene?.scene?.actors)",
        "single cloth mesh validation")

    html=once(html,
        "Expressive wrinkled crown, crooked fabric face, folded speaking mouth,"
        " floppy asymmetric brim, cloth band, rear patches and stitched seams."
        " Fully editable native mesh project.",
        "One continuous UV-painted cloth sculpture. The brows protrude from the crown,"
        " eyes and mouth are carved as shallow cloth dents, and fabric shadows,"
        " wrinkles, patches and stitches are painted in the same UV texture."
        " One editable model part; no floating face objects or holes.",
        "single mesh starter description")

    for old,new,label in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_484_RING_DETAIL_AND_TRANSFORMS",MARKER,"marker"),
      ("ENGINE · MAKER v11.484","ENGINE · MAKER v11.485","visible title"),
      ("v11.484 · ring detail and group transforms",
       "v11.485 · unified sculpted Sorting Hat","headline"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.484'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.485'","build label"),
      ("<title>§wyrl§ Engine · Maker v11.484</title>",
       "<title>§wyrl§ Engine · Maker v11.485</title>","browser title"),
    ):html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.484';source.version=11.484;"
    assert html.count(old)==5,("provenance",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.485';source.version=11.485;")

    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes["history"]=[entry for entry in notes.get("history",[]) if entry.get("version")!="v11.484"]
    notes["history"].insert(0,{"version":"v11.484","changes":notes.get("changes",[])})
    notes.update(version="v11.485",date="2026-11-17",
      title="Sorting Hat rebuilt as one sculpted, UV-painted fabric mesh",
      changes=[
       "Replaced the 49-object Sorting Hat assembly with one connected, editable topology mesh containing the entire cap, folded tip, wavy brim, brim underside, and interior cloth.",
       "Eyebrows are raised folds of the crown vertices. Eyes are inward cloth indentations; neither eye is a hole, separately inserted black shape or mesh.",
       "The nose rises organically and the mouth is one recessed fabric crease with sculpted upper and lower lips rather than a black rectangular insert.",
       "All aged material coloring, deep soft crease shadows, weave, wear and rear patch details are in a native UV-painted PNG with readable full-surface UVs, compatible with UV Editor.",
       "One selectable model object makes proportional sculpting, topology changes, ring editing, save, cloning, VR and mobile controls simpler. The previous v11.483 assembly is backed up as a separate unshipped scene.",
       "Source topology, project routing and texture limits are verified automatically. Physical Moto and Quest visual acceptance remains owner testing."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace("</",r"<\/")+html[at+width:]
