"""§E v11.367 — undo the false rock deletion and visibly reshape both original stone starters."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_367_PROPER_STONE_HAND_ANATOMY'
def once(src,old,new,label):
    n=src.count(old)
    if n!=1:raise AssertionError(('v11.367',label,n,old[:140]))
    return src.replace(old,new,1)
def apply(html):
    js=(ROOT/'runtime/stone_hand_anatomy_v11_367.js').read_text('utf8')
    for token in [
      'function se367CliffField(math){',
      'function se367AnatomicalRockScene(){',
      'se365OriginalStoneScene()',
      'se281RockScene=se367AnatomicalRockScene;',
      'se288SmoothCliffHandScene=function(){',
      'SWYRL_ENGINE_STONE_HAND_ANATOMY_367'
    ]:assert token in js,token
    for term in [
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_366_UV_AUTHORING_MARKER',
      'function se290GauntletField(){',
      ' const hand=se337HandField(math);',
      'const se365OriginalStoneScene=se281RockScene;',
      "const forearm=cap(p,[.004,.20,-.004],[.004,1.29,-.009],.298,.232);"
    ]:assert term in html,term
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
      'install stone anatomy refinements after existing runtime')
    html=once(html,
      ' const hand=se337HandField(math);',
      ' const hand=se367CliffField(math);',
      'native connected Cliff hand generator must call physically different anatomy')
    html=once(html,
      "const forearm=cap(p,[.004,.20,-.004],[.004,1.29,-.009],.298,.232);",
      "const forearm=cap(p,[.004,.20,-.004],[.004,1.29,-.009],.270,.215);",
      'visible tapered wrist profile')
    # One *smooth* connected SDF finger barrel per digit. The v11.365 radii
    # remain too broad. Taper the actual native anatomy before remeshing, not
    # through a discontinuous nearest-bone coordinate transform.
    start=html.index('function se337OrganicFingerSkin(digits,{ell,cap,blend}){')
    end=html.index('function se337HandField(math){',start)
    skin=html[start:end]
    for before,after,label in [
      ('f.r*1.17,f.r*.90','f.r*1.06,f.r*.84','proximal barrel'),
      ('f.r*.94,.080,f.r*.94','f.r*.89,.078,f.r*.89','PIP joint volume'),
      ('f.r*.89,f.r*.74','f.r*.82,f.r*.68','middle barrel'),
      ('f.r*.79,.068,f.r*.79','f.r*.73,.066,f.r*.73','DIP volume'),
      ('f.r*.74,f.r*.59','f.r*.67,f.r*.51','distal taper'),
      ('f.r*.65,.097,f.r*.65','f.r*.57,.093,f.r*.57','rounded fingertip')
    ]:skin=once(skin,before,after,label)
    html=html[:start]+skin+html[end:]
    for old,new,label in [
       ('SWYRL_ENGINE_DEPLOY_MARKER: V11_366_UV_AUTHORING_MARKER',MARKER,'marker'),
       ('ENGINE · MAKER v11.366','ENGINE · MAKER v11.367','header'),
       ('v11.366 · UV authoring alignment marker',
        'v11.367 · distinct anatomical Cliff and full-rock hands','release headline'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.366'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.367'",'build'),
       ('<title>§wyrl§ Engine · Maker v11.366</title>',
        '<title>§wyrl§ Engine · Maker v11.367</title>','title')
    ]:html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.366';source.version=11.366;"
    if html.count(old)!=5:raise AssertionError(('v11.367 scene provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.367';source.version=11.367;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.366' for x in notes.get('history',[])):
      notes.setdefault('history',[]).insert(0,{'version':'v11.366','changes':notes.get('changes',[])})
    notes.update(version='v11.367',date='2026-11-08',
      title='Stone hand anatomy correction: unmistakable Cliff silhouette, keep every Rock Hand stone',
      changes=[
        'Smooth Cliff Hand now uses the revised connected SDF directly, rather than only a minor proportion nudge: visibly narrower palm and heel, stronger wrist taper, straighter pinky-side edge, realistic separate finger barrel shapes and natural thenar/thumb connection.',
        'Multi-rock Rocky Anime Hand starts from the complete original 89-part geometry, restoring the 28 decorative stones mistakenly deleted in v11.365. All stone sections remain, but every palm, wrist, side, digit and thumb rock is recentered/reshaped around the correct anatomical outline.',
        'Retain individual editable stones with full angular/faceted detail, 12 closed finger shafts, all separate knuckle chips, 3 closed thumb segments and native 17-bone rig. No smooth glove replacement or new material presets.',
        'Both starter projects have updated names that make the new load path visible. Saved user models, original WebXR hand references, Quest 2 controller meshes, original UV image data and VR tool bindings remain untouched.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
