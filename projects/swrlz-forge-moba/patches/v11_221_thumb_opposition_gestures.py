"""§E v11.221 — append-only Arcane Glove thumb opposition and gesture library.

Only the already-rigged native Model Atelier hand and its rigging controls change.
No scene migration, geometry replacement, Quest input or unrelated game change.
"""
from pathlib import Path
import json


def once(html, old, new):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.221 scoped hand gesture anchor', old[:155], count))
    return html.replace(old,new,1)


def apply(html):
    root=Path(__file__).resolve().parents[1]
    gesture=(root/'runtime/model_atelier_hand_gestures_v11_221.js').read_text('utf8')
    studio=(root/'runtime/model_atelier_gesture_studio_v11_221.js').read_text('utf8')
    html=once(html,"const se212Id='floating-hand-glove';",
              gesture+"\nconst se212Id='floating-hand-glove';")

    # Keep the same native rig pose API, with corrected anatomically distinct
    # CMC/MCP/IP orientations rather than uniformly curling all thumb joints.
    a='function se220RigPreset(rig,kind){'
    b='function se220CreateHandRig(digits){'
    assert html.count(a)==1 and html.count(b)==1
    start=html.index(a)
    end=html.index(b,start)
    assert 'const curled=kind===' in html[start:end], 'unexpected prior preset shape'
    html=html[:start]+"function se220RigPreset(rig,kind){return se221GesturePose(rig,kind);}\n"+html[end:]

    # The dorsal + palmar thumb skin, band/helix, and distal tip use a joint
    # projection with broader but localized capsule falloff. Palm web remains
    # anchored; finger weights and the underlying organic topology are intact.
    a=' // Thumb roots follow an angled two-section skeleton, unlike upright fingers.'
    b=' const entries=[...result].filter('
    assert html.count(a)==1 and html.count(b)==1
    start=html.index(a);end=html.index(b,start)
    html=html[:start]+""" // Thumb CMC/MCP/IP capsule ownership and its physical spiral follow each other.
 const thumb=se221ThumbInfluences(pt,rig);
 if(thumb.mix>0){
  for(const [id,w] of [...result])result.set(id,w*(1-thumb.mix));
  for(const [id,w] of thumb.links)add(id,w);
 }
"""+html[end:]

    # Progress between poses is eased on every bone channel (no overshoot);
    # timeline storage and hand-authored custom keys remain unchanged.
    html=once(html,
       'const left=keys[hi-1],right=keys[hi],s=(t-left.time)/(right.time-left.time);',
       'const left=keys[hi-1],right=keys[hi],s=se220Smooth((t-left.time)/(right.time-left.time));')

    html=once(html,'  function refreshList(){',
              studio+'\n  function refreshList(){')
    html=once(html,'    se220RigControlsInstall();',
              '    se220RigControlsInstall();se221StudioInstall();')
    css="""
/* §E v11.221 · compact extra gesture authoring inside v11.220 rig studio. */
.atelier-gesture-library{display:grid;grid-template-columns:minmax(0,1fr);gap:6px;
 padding:7px 0 8px;border-bottom:1px solid #405879}
.atelier-gesture-library label{font-size:11px;font-weight:700;color:#c5d8ee}
.atelier-gesture-library select,.atelier-gesture-library button{
 min-width:0;width:100%;min-height:35px;font-size:11px}
.atelier-thumb-kinematics{display:grid;gap:7px;
 padding:8px 0;border-top:1px solid #405879}
.atelier-thumb-kinematics>strong{font-size:11px;color:#e6b9ff}
.atelier-thumb-kinematics label{display:grid;grid-template-columns:1fr auto;
 gap:4px;font-size:11px;align-items:center}
.atelier-thumb-kinematics label output{text-align:right;color:#e6affd;
 font-variant-numeric:tabular-nums}
.atelier-thumb-kinematics input[type=range]{grid-column:1/-1;width:100%;
 min-height:26px;accent-color:#c65af1;touch-action:pan-y}
.atelier-thumb-kinematics small{font-size:10px;line-height:1.45;color:#b8cfea}
"""
    assert '</head>' in html
    html=html.replace('</head>','<style id="atelierGestureV11221">'+css+'</style>\n</head>',1)
    html=once(html,
        " source.engine='§wyrl§ Engine · Maker v11.220';source.version=11.220;",
        " source.engine='§wyrl§ Engine · Maker v11.221';source.version=11.221;")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_220_NATIVE_HAND_SKELETAL_STUDIO',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_221_THUMB_OPPOSITION_GESTURES'),
      ('ENGINE · MAKER v11.220','ENGINE · MAKER v11.221'),
      ('v11.220 · Native hand rig, posing and keyframe studio',
       'v11.221 · Opposable thumb and gesture animation library'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.220'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.221'"),
      ('<title>§wyrl§ Engine · Maker v11.220</title>',
       '<title>§wyrl§ Engine · Maker v11.221</title>')
    ]:
        html=once(html,old,new)
    tag='const SE_RELEASE_NOTES='
    pos=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Arcane Glove: opposable thumb and 14 animated hand gestures',
      date='2026-11-02',changes=[
        'Corrected the existing 17-bone glove rig so the angled thumb CMC rotates into actual opposition across the palm; MCP and IP flex separately. The open hand geometry and existing named joints are retained.',
        'Rebalanced thumb capsule skin weights around the curved thumb, retaining band, and glowing double helix so distal parts follow the skeleton while the saddle remains joined to the palm.',
        'Added distinct Open, Relaxed, Fist, Point, Precision Pinch, OK, Thumbs Up, Peace, Rock Horns, I Love You, Shaka, Wave, Grasp and Finger Gun gesture presets to the native rig studio. The index-thumb pinch is fingertip-aligned rather than generic finger curl.',
        'Added a gesture selector, one-tap 3-key open-to-gesture-to-open animated preview, and dedicated thumb opposition and thumb flex sliders for touch devices. Existing custom joint sliders, keyed timeline, saves, import and export remain intact.',
        'Smoothed per-bone frame interpolation. No migration of saved projects, no change to §C, Sheep Tag, Quest controllers or other model starters. Real-device acceptance remains with the owner.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
