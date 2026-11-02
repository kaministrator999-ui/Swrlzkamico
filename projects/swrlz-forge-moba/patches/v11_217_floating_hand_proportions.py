"""§E v11.217 · second owner screenshot pass: fingers and opposite-thumb palm.

Append-only hand-starter-only source patch. Preserve v11.215 source, existing
saved hand projects, §E engine, VR controllers, Sheep Tag and user workspaces.
"""
from pathlib import Path
import json

def once(html, old, new):
    count=html.count(old)
    if count!=1:
        raise AssertionError(("v11.217 hand anchor",old[:170],count))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    code=(root/"runtime/model_atelier_hand_proportions_v11_216.js").read_text(encoding="utf8")
    html=once(html,"const se212Id='floating-hand-glove';",
        code+"\nconst se212Id='floating-hand-glove';")
    # Replace only starter construction's local function bindings, not old
    # helpers or previously saved source lineages.
    edits=[
      (" const digit=se215FingerSpec;"," const digit=se217FingerSpec;"),
      (" const skin=se215OrganicHandSkin(digit,{ell,cap,blend});",
       " const skin=se217OrganicHandSkin(digit,{ell,cap,blend});"),
      (" se215HandAnatomicalTrim({digits:digit,wire,sphere,color});",
       " se217HandAnatomicalTrim({digits:digit,wire,sphere,color});"),
      # Remove the round shield/disk impression: expose actual tapered palm.
      ("[0,1.70,.342],[.345,.345,.055]","[0,1.70,.325],[.284,.295,.046]"),
      ("loop([0,1.70,.405],.326,.326)","loop([0,1.70,.386],.281,.290)"),
      ("loop([0,1.70,.413],.267,.267)","loop([0,1.70,.394],.230,.236)"),
      ("[0,1.71,-.306],[.54,.53,.083]","[0,1.71,-.298],[.451,.428,.072]"),
      # Anatomy-aware knuckle placement. Previous constant y=2.31 and
      # identical spheres made the pinky appear as tall/thick as its siblings.
      ("[f.x,2.31,-.183],[f.r*1.19,.17,.055]",
       "[f.x,f.from+.052,-.166],[f.r*1.12,.122,.044]"),
      ("[f.r*.89,(f.to-f.from)*.29,.042]",
       "[f.r*.75,(f.to-f.from)*.29,.035]"),
      ("[f.x,2.325,-.242],[.060,.080,.036]",
       "[f.x,f.from+.065,-.224],[f.r*.48,f.r*.57,.030]"),
      ("[[f.x,2.41,-.205],[f.x+f.splay*.52,(f.from+f.to)*.53,-.181],",
       "[[f.x,f.from+.12,-.187],[f.x+f.splay*.52,(f.from+f.to)*.53,-.160],"),
      ("[x,f.to-.09,-.084],[.038,.053,.027]",
       "[x,f.to-.085,-.079],[f.r*.29,f.r*.40,.022]"),
      # Original thumb armor was bigger than small physical MCP joint.
      ("[-.77,1.71,-.236],[.19,.15,.051]",
       "[-.730,1.704,-.215],[.152,.125,.042]")
    ]
    for before,after in edits:
        html=once(html,before,after)
    # Existing medallion crest stays a compact original motif. Do not
    # delete the editable plate or change UV material selection.
    for old,new in [
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_216_SHEEP_LIVE_MOVE_WHILE_SELECTING",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_217_HAND_FINGER_PALM_PROPORTIONS"),
      ("ENGINE · MAKER v11.216","ENGINE · MAKER v11.217"),
      ("v11.216 · Sheep Tag Quest keep moving while selecting A/X wheel",
       "v11.217 · Floating Hand finger and outer-palm proportions"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.216'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.217'"),
      ("<title>§wyrl§ Engine · Maker v11.216</title>",
       "<title>§wyrl§ Engine · Maker v11.217</title>")
    ]:
        html=once(html,old,new)
    key="const SE_RELEASE_NOTES="
    start=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title="Floating Hand: proportional fingers and refined outer palm",
      date="2026-11-02",changes=[
        "Owner's second phone screenshots showed four rigid/overlarge cylinders and a ballooned side of the palm opposite the thumb. Rebuilt only the new Floating Hand starter's organic hand surface with narrower tapered phalanges, different joint positions, shorter pinky, naturally varied index/ring/middle heights, and more credible thumb webbing.",
        "Pulled the hypothenar/ulnar palm into a slimmer tapered curve anchored to wrist and little-finger metacarpal rather than a bulbous disk; maintained a curved deep palm, thumb pad and the 3D dorsal arch.",
        "Scaled and lowered individual knuckle armor/studs with per-digit root positions; tightened the oversized backhand/palmar medallions so the actual hand silhouette remains legible. Refit thumb saddle and outer-palm piping.",
        "Retained Model Atelier's native topology/UV, editable mesh groups and glowing wrist effects. No changes to other projects, saved hand variants, Quest gameplay/VR input or rigging/animation.",
        "Targeted browser model-load, anatomical proportions and source-integrity checks precede manual owner phone and Quest visual inspection."
      ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[start+n:]
