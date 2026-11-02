"""§E v11.215: sculpt the user's Floating Hand into a volumetric anatomical glove.

Append-only. Only the Floating Hand template construction code is changed.
All existing starter/Quest/Sheep Game Engine state, native validation, saved
custom projects, browser rendering and original reference/release lineage remain.
"""
from pathlib import Path
import json

def once(html,old,new):
    n=html.count(old)
    assert n==1,("v11.215 anatomy source anchor",old[:150],n)
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    addon=(root/"runtime/model_atelier_hand_anatomy_v11_215.js").read_text(encoding="utf8")
    html=once(html,"const se212Id='floating-hand-glove';",
              addon+"\nconst se212Id='floating-hand-glove';")
    # Replace only the hand's original SDF: old 2D-like palm, straight four
    # extruded fingers and shallow, tube-like thumb. Use pure 3D anatomy.
    old_begin=" const digit=[\n  {x:-.43,from:2.23,to:3.07,r:.112},"
    old_end=" // The native marching-tetrahedra helper provides indexed mesh geometry and UVs."
    assert html.count(old_begin)==1 and html.count(old_end)==1
    start=html.index(old_begin);end=html.index(old_end,start)
    html=html[:start]+(
      " const digit=se215FingerSpec;\n"
      " const skin=se215OrganicHandSkin(digit,{ell,cap,blend});\n"
      +html[end:])
    html=once(html,
      "ops.surface(skin,[[-1.52,.53,-.40],[.83,3.49,.42]],.049)",
      "ops.surface(skin,[[-1.58,.53,-.56],[.88,3.51,.55]],.047)")
    # Reposition original authored plates/crests so the enlarged palm does
    # not occlude them. Keep all identities/mesh IDs and all authored groups.
    subs=[
      ("const y=f.to-.13,x=f.x+f.x*.09;","const y=f.to-.14,x=f.x+f.splay;"),
      ("f.x+f.x*.045","f.x+f.splay*.52"),
      ("[0,1.70,.226]","[0,1.70,.342]"),
      ("loop([0,1.70,.290]","loop([0,1.70,.405]"),
      ("loop([0,1.70,.298]","loop([0,1.70,.413]"),
      ("[[-.15,1.59,.310],[-.19,1.73,.312],[-.095,1.845,.312],[.065,1.858,.312],",
       "[[-.15,1.59,.424],[-.19,1.73,.426],[-.095,1.845,.426],[.065,1.858,.426],"),
      ("[.170,1.75,.312],[.13,1.625,.312],[.025,1.605,.314],[-.026,1.685,.317],",
       "[.170,1.75,.426],[.13,1.625,.426],[.025,1.605,.428],[-.026,1.685,.431],"),
      ("[.038,1.728,.319],[.095,1.690,.319]]",
       "[.038,1.728,.433],[.095,1.690,.433]]"),
      ("[-.77,1.71,-.123]","[-.77,1.71,-.236]"),
      ("[[-.72,1.64,-.154],[-.96,1.91,-.084],[-1.19,2.13,-.048]]",
       "[[-.72,1.64,-.235],[-.96,1.91,-.086],[-1.19,2.13,-.021]]"),
      ("[0,1.71,-.205]","[0,1.71,-.306]"),
      ("[[0,2.14,-.301],[-.19,1.95,-.308],[-.065,1.78,-.307],[0,1.59,-.307],",
       "[[0,2.14,-.399],[-.19,1.95,-.404],[-.065,1.78,-.402],[0,1.59,-.402],"),
      ("[.065,1.78,-.307],[.19,1.95,-.308],[0,2.14,-.301]]",
       "[.065,1.78,-.402],[.19,1.95,-.404],[0,2.14,-.399]]"),
      ("[[0,1.63,-.305],[0,1.23,-.245]]",
       "[[0,1.63,-.400],[0,1.23,-.284]]"),
      ("[[s*.14,1.60,-.300],[s*.34,1.91,-.285],[s*.46,2.18,-.211]]",
       "[[s*.14,1.60,-.401],[s*.34,1.91,-.368],[s*.46,2.18,-.245]]"),
    ]
    for old,new in subs:
        n=html.count(old)
        assert n in (1,2),("v11.215 ornament",old,n)
        html=html.replace(old,new)
    html=once(html,
      " m.name='Floating Hand · Arcane Glove';m.parts=parts;",
      " se215HandAnatomicalTrim({digits:digit,wire,sphere,color});\n"
      " m.name='Floating Hand · Arcane Glove';m.parts=parts;")
    # Never mutate the canonical model envelope or previously saved projects.
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_214_SHEEP_QUEST_UPRIGHT_WHEEL_SINGLE_RAY',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_215_FLOATING_HAND_SCULPT_ANATOMY'),
      ('ENGINE · MAKER v11.214','ENGINE · MAKER v11.215'),
      ('v11.214 · Sheep Tag Quest modal build wheel camera and ray ownership fix',
       'v11.215 · floating glove anatomical sculpt and materials'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.214'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.215'"),
      ('<title>§wyrl§ Engine · Maker v11.214</title>',
       '<title>§wyrl§ Engine · Maker v11.215</title>')
    ]: html=once(html,old,new)
    tag='const SE_RELEASE_NOTES='
    start=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Floating Hand: rounded ulnar side, thumb saddle and articulated fingers',
      date='2026-11-02',changes=[
        'Owner four-angle phone screenshots exposed a planar palm, straight little-finger-side silhouette and an unconvincing attached thumb. Replaced only the hand starter signed-distance field with fuller carpal, cupped palm, separate thenar and hypothenar pads, convex dorsal arch, curved ulnar edge and strongly connected forward-angled two-segment thumb.',
        'Each of four fingers has graduated length, asymmetrical splay, taper and a smooth intermediate knuckle. The palm and thumb have greater X/Y/Z volume at a slightly finer sampling step, without a runtime frame loop or fetched texture.',
        'Lifted front medallion and backhand crest above their thicker palm surface. Added ulnar rim seams, palmar thenar/hypothenar seams, knuckle flexion curves and thumb-saddle armor details as independently editable native mesh groups.',
        'All updates affect new Floating Hand starter opens only. Preserve original source lineage, v11.214 Quest wheel and camera fixes, Sheep Tag, Game Editor, existing saved models, and native validator. No claims of skeletal rigging, real texture maps or animation.',
        'Focused anatomy geometry assertions, direct-link browser initialization and mobile performance inspection precede deployment. Owner physical Quest 2 and phone aesthetics remain acceptance stages.'
      ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+n:]
