"""§E v11.223 — stronger glove clench and an alternating wrist-driven wave.

Append-only source patch. Saved user poses and keyframes, the old thumb helix,
all model topology, Sheep Tag and Quest inputs remain untouched.
"""
from pathlib import Path
import json


def once(html, old, new):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.223 hand motion anchor', old[:135], count))
    return html.replace(old,new,1)


def apply(html):
    root=Path(__file__).resolve().parents[1]
    helper=(root/'runtime/model_atelier_hand_motion_v11_223.js').read_text('utf8')
    html=once(html,"const se212Id='floating-hand-glove';",
              helper+"\nconst se212Id='floating-hand-glove';")

    # Stronger digit flexion at all three joints, with differentiated curl
    # and an opposable, flexed thumb tucked against the closed fingers.
    old="""  case 'fist':
   curl(['index','middle','ring','pinky'],.88,1.10,.63);
   // Cross the thumb IN FRONT of the folded fingers, rather than
   // pivoting every thumb phalanx around a single sideways axis.
   thumb([.29,1.02,-.37],[.17,.12,.05],[.14,.01,.10]);break;"""
    new="""  case 'fist':
   // Strong clench: MCP closes the finger, PIP folds middle phalanx,
   // DIP brings the fingertip toward the palm. Slight stagger is natural.
   digit('index',1.06,1.42,.87,.020);
   digit('middle',1.09,1.47,.91,.005);
   digit('ring',1.12,1.47,.92,-.010);
   digit('pinky',1.14,1.49,.92,-.025);
   // Oppose and flex all three thumb pivots to secure the fist.
   thumb([.37,1.18,-.48],[.34,.19,.20],[.25,.03,.28]);break;"""
    html=once(html,old,new)

    # The static preview also shows actual wrist roll+twist instead of
    # spreading the fingers while keeping the arm rigid.
    old="""  case 'wave':
   digit('index',.08,.10,.04,.16);
   digit('middle',.05,.08,.04,.055);
   digit('ring',.06,.10,.04,-.045);
   digit('pinky',.06,.10,.04,-.16);
   pose.wrist=[0,0,.13];
   thumb([.07,.14,-.34],[.03,0,-.02],[.02,0,0]);break;"""
    new="""  case 'wave':
   digit('index',.08,.10,.04,.16);
   digit('middle',.05,.08,.04,.055);
   digit('ring',.06,.10,.04,-.045);
   digit('pinky',.06,.10,.04,-.16);
   pose.wrist=[-.025,.18,.25];pose.palm=[0,.06,.05];
   thumb([.07,.14,-.34],[.03,0,-.02],[.02,0,0]);break;"""
    html=once(html,old,new)

    # Wave-specific eight-key clip alternates left/right with wrist yaw and
    # roll, rather than repeating a single static wrist pose.
    html=once(html,
      """  rig.duration=1.5;
  rig.timeline=[
   {time:0,pose:open},
   {time:.75,pose:structuredClone(gesture)},
   {time:1.5,pose:structuredClone(open)}
  ];""",
      """  rig.duration=kind==='wave'?2.20:1.5;
  rig.timeline=kind==='wave'?se223WaveTimeline(rig):[
   {time:0,pose:open},
   {time:.75,pose:structuredClone(gesture)},
   {time:1.5,pose:structuredClone(open)}
  ];""")
    html=once(html,
      "se220Time=0;se220R('Time').max='1.5';se220R('Time').value='0';",
      "se220Time=0;se220R('Time').max=String(rig.duration);se220R('Time').value='0';")
    html=once(html,
      "se220R('Length').value='1.5';",
      "se220R('Length').value=String(rig.duration);")
    html=once(html,
      "se220RigTouched('Playing open → '+(se221Gestures.find(([k])=>k===kind)?.[1]||'custom')+' → open. Edit or save these three keys.');",
      "se220RigTouched(kind==='wave'?'Playing a wrist-twist and side-to-side wave with finger flutter · 8 editable keys.':"+
      "'Playing open → '+(se221Gestures.find(([k])=>k===kind)?.[1]||'custom')+' → open. Edit or save these three keys.');")

    html=once(html,
      " source.engine='§wyrl§ Engine · Maker v11.222';source.version=11.222;",
      " source.engine='§wyrl§ Engine · Maker v11.223';source.version=11.223;")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_222_CLOVER_MOTIONS_BUILD_SPARKS',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_223_FIST_CLENCH_WRIST_WAVE'),
      ('ENGINE · MAKER v11.222','ENGINE · MAKER v11.223'),
      ('v11.222 · Clover motions and Sheep Tag building sparkles',
       'v11.223 · Stronger hand clench and wrist-driven wave'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.222'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.223'"),
      ('<title>§wyrl§ Engine · Maker v11.222</title>',
       '<title>§wyrl§ Engine · Maker v11.223</title>')
    ]:
        html=once(html,old,new)

    tag='const SE_RELEASE_NOTES='
    pos=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Arcane Glove: stronger fist clench and wrist-driven wave',
      date='2026-11-02',changes=[
       'Recalibrated each finger’s MCP/PIP/DIP flexions for a tighter, visibly closed fist, with the thumb CMC opposing across the fingers and MCP/IP joints tucking under instead of sticking out.',
       'Wave now has an open-palm pose with real wrist twist (yaw), wrist roll, a slight palm follow-through and gentle finger flutter.',
       'Animate Selected Gesture with Wave builds eight native skeletal keys across 2.2 seconds, swinging left-right repeatedly before returning to neutral. Other gestures retain their three-key 1.5-second previews.',
       'Timeline keys remain editable and saved/exported in the existing rigging JSON. All previous saved user clips remain intact; no edits to models, 3D mesh topology, Quest inputs, Sheep Tag, or §C.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
