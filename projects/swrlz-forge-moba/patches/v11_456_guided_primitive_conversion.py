"""§E v11.456: safe primitive conversion before face selection in guided Inset.

Keeps native se430 geometry ownership, existing source guards, Undo and two
preview/apply checkpoints. The module only adds one contextual editor button.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_456_GUIDED_PRIMITIVE_CONVERSION"

def once(source,old,new):
 count=source.count(old)
 if count!=1:raise AssertionError(("v11.456 anchor",old[:170],count))
 return source.replace(old,new,1)

def apply(html):
 js=(ROOT/"runtime/model_guided_primitive_conversion_v11_456.js").read_text("utf8")
 css=(ROOT/"runtime/model_guided_primitive_conversion_v11_456.css").read_text("utf8")
 assert js.startswith("/* SE456_GUIDED_PRIMITIVE_CONVERSION_START */")
 assert js.rstrip().endswith("/* SE456_GUIDED_PRIMITIVE_CONVERSION_END */")
 assert css.startswith("/* SE456_GUIDED_PRIMITIVE_CONVERSION_STYLES_START */")
 html=once(html,"SWYRL_ENGINE_DEPLOY_MARKER: V11_455_VIEW_READABILITY",MARKER)
 html=once(html,"/* SE455_TRANSIENT_FACE_HIGHLIGHT_END */",
  "/* SE455_TRANSIENT_FACE_HIGHLIGHT_END */\n"+
  "/* Historical v11.455 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_455_VIEW_READABILITY */\n"+js)
 html=once(html,"</head>","<style id=\"se456GuidedPrimitiveConversionStyles\">\n"+css+"\n</style>\n</head>")
 # Correct the old guidance, which told the user to tap a face that the
 # unconverted primitive selector explicitly refuses to choose.
 html=once(html,
  "message('Select the cube, then tap the face you want to inset.');draw();return false;",
  "message('Make the selected primitive editable, then tap its square face to start Inset.');draw();return false;")
 for old,new in [
  ("ENGINE · MAKER v11.455","ENGINE · MAKER v11.456"),
  ("v11.455 · readable solid modeling and viewport modes",
   "v11.456 · guided cube conversion before Inset"),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.455'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.456'"),
  ("<title>§wyrl§ Engine · Maker v11.455</title>",
   "<title>§wyrl§ Engine · Maker v11.456</title>")
 ]:
  html=once(html,old,new)
 prior=" source.engine='§wyrl§ Engine · Maker v11.455';source.version=11.455;"
 assert html.count(prior)==5,("v11.456 provenance",html.count(prior))
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.456';source.version=11.456;")
 key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes["history"]=[item for item in notes.get("history",[]) if item.get("version")!="v11.455"]
 notes["history"].insert(0,{"version":"v11.455","changes":notes.get("changes",[])})
 notes.update(version="v11.456",date="2026-11-14",
  title="Make cube editable before selecting a face for Inset",
  changes=[
   "Choosing Inset on one plain selected primitive now presents a prominent Make Editable & Continue action inside the existing top-of-viewport Inset guide, without requiring a face to be selected first.",
   "That action calls the existing validated native convert operation, keeps the original cube recoverable through Undo, and returns to Face selection for a full-square tap and the established rim/depth previews.",
   "Saved primitive vertex edits still require explicit bake confirmation; rigged, painted, textured, authored or otherwise blocked meshes remain protected and are never silently converted.",
   "No new geometry pipeline or parallel edit state is introduced. The original v11.454 rim/depth Set buttons, v11.452 tool flyouts, native preview/Apply/Cancel/Undo, camera, save/load, desktop, mobile, and VR functionality remain in place.",
   "The conversion control is displayed only for a single convertible source during the rim stage and cannot commit any Inset or Extrude on its own."
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace("</",r"<\/")+html[at+width:]
