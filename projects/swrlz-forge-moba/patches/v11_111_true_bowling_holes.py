"""Simple native indexed bowling ball bore maker: true walls and rounded bottoms."""
import hashlib,json
from pathlib import Path

def once(s,a,b):
    n=s.count(a)
    assert n==1,(a[:130],n)
    return s.replace(a,b,1)

def apply(html):
    root=Path(__file__).resolve().parent.parent
    js=(root/"runtime/model_atelier_bowling_holes_v11_111.js").read_text(encoding="utf8")
    html=once(html,"function atelierSculptGhostInstall(){",js+"\nfunction atelierSculptGhostInstall(){")
    html=once(html," atelierSculptGhostInstall();\n",
              " atelierSculptGhostInstall();\n atelierBowlingInstall();\n")
    html=once(html,"SWYRL_ENGINE_DEPLOY_MARKER: V11_110_TRUE_DISPLACEMENT_PREVIEW",
      "SWYRL_ENGINE_DEPLOY_MARKER: V11_111_ROUND_BOWLING_HOLE_KIT")
    for old,new in [
      ("ENGINE · MAKER v11.110","ENGINE · MAKER v11.111"),
      ("v11.110 · displacement-accurate ghost","v11.111 · actual round bowling holes"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.110'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.111'"),
      ("<title>§wyrl§ Engine · Maker v11.110</title>",
       "<title>§wyrl§ Engine · Maker v11.111</title>")
    ]:html=once(html,old,new)
    key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="True round bowling-ball holes with indexed tube walls and rounded bottoms",
       date="2026-10-24",changes=[
        "Add a simple one-/three-hole bowling ball builder for selected spherical primitives, instead of repurposing an organic sculpt dent.",
        "Build real circular apertures, stitched cylindrical internal walls and hemispherical ends as an editable indexed topology mesh.",
        "Preview the replacement geometry independently; Apply is explicit and Undo restores the original procedural sphere.",
        "Reuse existing 9k-vertex/16k-triangle validation, topology audit, local transform, native JSON/OBJ/GLB export and mesh inspector."
       ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+n:]
    raw=html.encode("utf8")
    print("SWRLZ_V11111_BUILD_MEASURE",len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
