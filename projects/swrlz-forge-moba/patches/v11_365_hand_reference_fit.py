"""§E v11.365 · anatomical WebXR hand reference calibration for both stone starters."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_365_HAND_REFERENCE_FIT'

def once(src,old,new,label):
    n=src.count(old)
    if n!=1:raise AssertionError(('v11.365',label,n,old[:120]))
    return src.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/hand_reference_fit_v11_365.js').read_text('utf8')
    for needle in ['function se365RefinedRockScene(){','se365WebXRAnatomy',
                   'se365OriginalStoneScene=se281RockScene','rockFingerRise',
                   'SWYRL_ENGINE_HAND_REFERENCE_FIT_365']:
        if needle not in js:raise AssertionError(('v11.365 runtime helper missing',needle))
    for prerequisite in [
      "SWYRL_ENGINE_DEPLOY_MARKER: V11_364_UV_ALIGNMENT_EXPORT",
      "const length={index:.026,middle:.037,ring:.020,pinky:.023};",
      "const shapedX=x*(1-.035*palmBand);",
      "const forearm=cap(p,[.004,.20,-.004],[.004,1.29,-.009],.322,.232);",
      "function se337OrganicFingerSkin(digits,{ell,cap,blend}){",
      "const se365OriginalStoneScene=se281RockScene;" if False else "function se282FullRockScene(){"
    ]:
        if prerequisite not in html:raise AssertionError(('v11.365 missing prerequisite',prerequisite))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
              'register rock scene refinements after existing weathered rock builder')
    # Cliff hand remains one SDF mesh, still UV mapped/skin weighted. These
    # adjustments are measured half-steps toward the WebXR joint ratios,
    # rather than an unsafe replacement with an unrigged 25-joint reference.
    html=once(html,
      "const length={index:.026,middle:.037,ring:.020,pinky:.023};",
      "const length={index:.074,middle:.037,ring:.020,pinky:.065};",
      'finger length corrections preserving middle/ring')
    html=once(html,
      "const shapedX=x*(1-.035*palmBand);",
      "const shapedX=x*(1+.018*palmBand);",
      'reduce inflated cliff palm breadth while preserving old thumb/ulnar shaping')
    html=once(html,
      "const forearm=cap(p,[.004,.20,-.004],[.004,1.29,-.009],.322,.232);",
      "const forearm=cap(p,[.004,.20,-.004],[.004,1.29,-.009],.298,.232);",
      'taper excessive outer wrist')
    start=html.index('function se337OrganicFingerSkin(digits,{ell,cap,blend}){')
    end=html.index('function se337HandField(math){',start)
    skin=html[start:end]
    for old,new,label in [
      ('f.r*1.20,f.r*.92','f.r*1.17,f.r*.90','finger proximal'),
      ('f.r*.91,f.r*.77','f.r*.89,f.r*.74','finger middle'),
      ('f.r*.76,f.r*.62','f.r*.74,f.r*.59','finger distal'),
      ('f.r*.67,.099,f.r*.67','f.r*.65,.097,f.r*.65','fingertip pad')
    ]:skin=once(skin,old,new,label)
    html=html[:start]+skin+html[end:]
    for old,new,label in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_364_UV_ALIGNMENT_EXPORT',MARKER,'marker'),
      ('ENGINE · MAKER v11.364','ENGINE · MAKER v11.365','visible version'),
      ('v11.364 · export corrected UV placement',
       'v11.365 · WebXR anatomy fit for stone hand starters','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.364'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.365'",'build'),
      ('<title>§wyrl§ Engine · Maker v11.364</title>',
       '<title>§wyrl§ Engine · Maker v11.365</title>','browser title')
    ]:html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.364';source.version=11.364;"
    if html.count(old)!=5:raise AssertionError(('v11.365 source model version',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.365';source.version=11.365;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.364' for x in notes.get('history',[])):
      notes.setdefault('history',[]).insert(0,{'version':'v11.364','changes':notes.get('changes',[])})
    notes.update(version='v11.365',date='2026-11-08',
      title='WebXR hand anatomy compared and fitted to both stone hand starters',
      changes=[
       'Smooth Cliff Hand: reference-measured index and pinky phalange length correction, slimmer finger taper, more believable metacarpal palm breadth and wrist transition. Keep native one-mesh stone texture, PBR geodes and 17-bone rig.',
       'Rocky Anime Hand / multi-rock: preserve stone finger/knuckle/solid thumb construction but reduce 28 redundant palm, side, finger and wrist outcroppings, taper boulder-like finger shafts and flatten excessive palm/stone thickness.',
       'Use the actual bundled WebXR 25-joint right-hand reference to calibrate digit ratios, not the unrelated controller meshes. No user-edited/saved project is overwritten; only new starter instances are refined.',
       'Preserve the UV source/artwork, native selection, project save/export, all controller/VR controls, and every unrelated model. Physical mobile/Quest review remains owner acceptance.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
