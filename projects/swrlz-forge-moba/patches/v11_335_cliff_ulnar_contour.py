"""§E v11.335 — pinky-side palm less bulbous, with no unrelated edits."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_335_CLIFF_ULNAR_CONTOUR'

def once(html,old,new,label):
    occurrences=html.count(old)
    if occurrences!=1:
        raise AssertionError(('v11.335',label,occurrences,old[:130]))
    return html.replace(old,new,1)

def apply(html):
    src=(ROOT/'runtime/cliff_ulnar_contour_v11_335.js').read_text('utf8')
    assert 'function se335NarrowUlnarField(math){' in src
    for prerequisite in (
      ' const hand=se334ReferenceHandField(math);',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_334_PHOTO_DORSAL_CRYSTALS',
      "window.SWRLZ_FORGE_BUILD={version:'v11.334'",
      'window.SWYRL_ENGINE_CLIFF_HAND_334='):
        if prerequisite not in html:
            raise AssertionError(('v11.335','missing source',prerequisite))
    # Preserve entire original photo-guided field and substitute only the Cliff
    # Hand caller; no global se217 anatomy changes and no new mesh objects.
    html=once(html,'window.SWRLZ_FORGE_BUILD=',src+'\nwindow.SWRLZ_FORGE_BUILD=',
         'install localized positive-X ulnar silhouette helper')
    html=once(html,
      ' const hand=se334ReferenceHandField(math);',
      ' const hand=se335NarrowUlnarField(math);',
      'connect inward SDF sampling to Cliff Hand starter only')
    old=" source.engine='§wyrl§ Engine · Maker v11.334';source.version=11.334;"
    if html.count(old)!=3:
        raise AssertionError(('v11.335','scene provenance',html.count(old)))
    html=html.replace(old,
      " source.engine='§wyrl§ Engine · Maker v11.335';source.version=11.335;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_334_PHOTO_DORSAL_CRYSTALS',MARKER),
      ('ENGINE · MAKER v11.334','ENGINE · MAKER v11.335'),
      ('v11.334 · photo-refined hand and dorsal crystal knuckles',
       'v11.335 · refined pinky-side palm contour'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.334'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.335'"),
      ('<title>§wyrl§ Engine · Maker v11.334</title>',
       '<title>§wyrl§ Engine · Maker v11.335</title>')
    ):
       html=once(html,old,new,'release identity')
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    if not any(v.get('version')=='v11.334' for v in notes.get('history',[])):
       notes.setdefault('history',[]).insert(0,{
         'version':'v11.334','changes':notes.get('changes',[])})
    notes.update(
      version='v11.335',date='2026-11-07',
      title='Smooth Cliff Hand: straighten the outer palm directly below the pinky',
      changes=[
         'Owner real-hand and latest phone screenshots show excessive outward hypothenar/pinky-side bow compared with the nearly straight human palm edge.',
         'Adjust only the Smooth Cliff Hand starter by remapping positive-X SDF sample positions inward up to 0.105 world units between y 1.24 and 2.19, fading into the existing wrist and pinky finger root. No planar clip, hard contour, or extra geometry.',
         'Retain prior photo-guided finger length, thumb/thenar shape and overall palm anatomy. Preserve original one connected editable gauntlet surface and 17 bone rig.',
         'Do not change dorsal teal crystal texture, palmar stone, moss, crack atlas, PBR, animation or other starter models.',
         'Verify actual ulnar mesh bounds and browser viewport rendering; physical phone/Quest owner visual acceptance remains pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
