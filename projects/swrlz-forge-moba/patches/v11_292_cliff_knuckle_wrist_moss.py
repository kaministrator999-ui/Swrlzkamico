"""§E v11.292: owner correction — mineral knuckles are PBR, moss on wrist only."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def once(html,old,new,label):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.292',label,n,old[:150]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/cliff_knuckle_wrist_moss_v11_292.js').read_text('utf8')
    assert 'function se292WristMossKnuckleMaterial(part){' in js
    for key in (
       'function se290CliffMaterial(part){',
       "part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se290CliffMaterial(part):",
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_291_HOODED_VANGUARD_MATERIALS',
       'window.SWRLZ_FORGE_BUILD=',
       'Connected smooth Cliff Hand and short stone gauntlet forearm'):
        if key not in html:raise AssertionError(('missing v11.292 prerequisite',key))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
       'register locally authored knuckle PBR and wrist-only moss mask')
    html=once(html,
       "part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se290CliffMaterial(part):",
       "part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se292WristMossKnuckleMaterial(part):",
       'connect new knuckle material to existing rigged hand')
    html=once(html,
       '<p>Connected smooth Cliff Hand and short stone gauntlet forearm with enhanced sandstone normal depth, dark texture-mapped cracks, selective moss and the native 17-bone rig.</p>',
       '<p>Smooth single-mesh sandstone hand with modeled-looking stone knuckles drawn in PBR maps and moss restricted to the bottom gauntlet wrist. Native 17-bone rig.</p>',
       'describe new material preview card')
    html=once(html,
       'Smooth Cliff Hand · seamless gauntlet and enhanced rock PBR ready',
       'Smooth Cliff Hand · wrist moss and mapped stone knuckles ready',
       'owner startup confirmation')
    html=once(html,
       "model.reference+=' Short tapered stone gauntlet forearm sculpted into the same connected mesh; no separate rock, cuff or crack pieces.';",
       "model.reference+=' Short tapered stone gauntlet forearm sculpted into the same connected mesh; no separate rock, cuff or crack pieces. Material update: sandstone throughout palm/fingers, moss confined to lower wrist, four knuckle stone ridges painted in aligned color/normal/AO UV maps.';",
       'native model project texture provenance')
    old=" source.engine='§wyrl§ Engine · Maker v11.291';source.version=11.291;"
    if html.count(old)!=3:raise AssertionError(('provenance occurrence',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.292';source.version=11.292;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_291_HOODED_VANGUARD_MATERIALS',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_292_CLIFF_WRIST_MOSS_KNUCKLES'),
      ('ENGINE · MAKER v11.291','ENGINE · MAKER v11.292'),
      ('v11.291 · Hooded Vanguard native sculpt and mapped material study',
       'v11.292 · wrist-only moss and texture-mapped rock knuckles'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.291'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.292'"),
      ('<title>§wyrl§ Engine · Maker v11.291</title>',
       '<title>§wyrl§ Engine · Maker v11.292</title>')):
        html=once(html,old,new,'version and release provenance')
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Cliff Hand: rock knuckle material and wrist-only moss',
      date='2026-11-06',changes=[
      'Use clean sandstone albedo for the whole connected hand and four fingers instead of repeating the mossy composite across every surface.',
      'Composite the original owner moss texture through a soft alpha mask restricted to the lowest 23 percent of gauntlet wrist UV space. Remove broad green material from thumb, palm and knuckles.',
      'Author four anatomically placed knuckle rock ridges solely in albedo, tangent-space normal and AO/crevice maps; no new geometric rocks, fingertip attachments or 3D crack tubes.',
      'Retain the owner-provided 384px per tile original atlas as packaged input and compose localized PBR maps one time on canvas, with GPU updates after asset load.',
      'Keep the single native connected gauntlet surface, fixed v11.290 loader, original 17-bone rig, UV mapping, timeline, independent models, Sheep Tag and saved projects unchanged.',
      'Verify assembled inline JavaScript and focused material layout regression. Final quality and posing require owner phone/Quest checks.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
