"""§E v11.337: smooth organic fingertips, heel-of-palm wrist curve and geode knuckles."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_337_CLIFF_ORGANIC_GEODES'
def once(html,old,new,label):
    n=html.count(old)
    if n!=1:
        raise AssertionError(('v11.337',label,n,old[:130]))
    return html.replace(old,new,1)
def apply(html):
    js=(ROOT/'runtime/cliff_hand_refinement_v11_337.js').read_text('utf8')
    for token in ('function se337OrganicFingerSkin(digits,{ell,cap,blend}){',
                  'function se337HandField(math){',
                  'function se337PaintGeode(ctx,k,i){',
                  'function se337DorsalGeodeMaterial(mat){'):
        assert token in js,token
    for token in ('SWYRL_ENGINE_DEPLOY_MARKER: V11_336_MESH_UV_GUIDE',
                  'function se336UVLayout(mesh, canvas)',
                  'function se335NarrowUlnarField(math){',
                  'function se334ReferenceHandField(math){'):
        assert token in html,token
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
          'register isolated anatomy and PBR geode code')
    # Optional skin dependency affects only the Cliff hand field; other
    # starters keep the native se217OrganicHandSkin unmodified.
    html=once(html,'function se334ReferenceHandField(math){',
          'function se334ReferenceHandField(math,skinFactory=se217OrganicHandSkin){',
          'accept optional organic finger field for Cliff only')
    html=once(html,' const skin=se217OrganicHandSkin(photoDigits,math);',
          ' const skin=skinFactory(photoDigits,math);',
          'inject smoother finger SDF')
    html=once(html,'function se335NarrowUlnarField(math){',
          'function se335NarrowUlnarField(math,skinFactory=se217OrganicHandSkin){',
          'preserve previous ulnar remapping')
    html=once(html,' const original=se334ReferenceHandField(math);',
          ' const original=se334ReferenceHandField(math,skinFactory);',
          'forward optional smooth finger field')
    html=once(html,' const hand=se335NarrowUlnarField(math);',
          ' const hand=se337HandField(math);',
          'refine palm-heel curve and finger joint shell only')
    html=once(html,' return se334DorsalOnlyCrystalMaterial(mat);',
          ' return se337DorsalGeodeMaterial(mat);',
          'replace overly repeated spike stencil with inset PBR geodes')
    html=once(html,'const mesh=ops.weld(ops.surface(field,bounds,.047));',
          'const mesh=ops.weld(ops.surface(field,bounds,.044));',
          'slightly finer single connected shell for rounded fingertip contour')
    old=" source.engine='§wyrl§ Engine · Maker v11.336';source.version=11.336;"
    if html.count(old)!=3:raise AssertionError(('v11.337','scene provenance',html.count(old)))
    html=html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.337';source.version=11.337;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_336_MESH_UV_GUIDE',MARKER),
      ('ENGINE · MAKER v11.336','ENGINE · MAKER v11.337'),
      ('v11.336 · selected mesh UV image guides and painted texture import',
       'v11.337 · natural palm wrist taper, smooth fingertips and inset crystal geodes'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.336'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.337'"),
      ('<title>§wyrl§ Engine · Maker v11.336</title>',
       '<title>§wyrl§ Engine · Maker v11.337</title>'),
    ):
      html=once(html,old,new,'release identity')
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,used=json.JSONDecoder().raw_decode(html[at:])
    if not any(item.get('version')=='v11.336' for item in notes.get('history',[])):
      notes.setdefault('history',[]).insert(0,{
        'version':'v11.336','changes':notes.get('changes',[])})
    notes.update(version='v11.337',date='2026-11-07',
      title='Smooth Cliff Hand: curved palm-to-wrist edge, rounder fingers and inlaid crystal geodes',
      changes=[
        'Owner real-hand closeups and actual mobile model screenshots reveal a bulging lower pinky-side palm-to-wrist step and blocky middle/tip finger sections; previous straight-edge pass was incomplete.',
        'Only the Cliff Hand starter receives a second positive-X, smooth SDF remap that rolls the hypothenar heel inward as it joins the narrower wrist. No flat side clip or additional hand geometry.',
        'Swap only this starter’s four finger segment field for overlapping smooth fingertip, PIP and DIP blends, preserving the original digit lengths, metacarpal roots, thumb/thenar and all native 17 bones.',
        'Improve native gauntlet tessellation pitch slightly from .047 to .044 for rounder tip outlines while staying one connected editable topology mesh.',
        'Replace four repeated fluorescent spikes with four differently-shaped recessed aquamarine geodes, distinct polygonal cut facets, dark stone sockets, glass-like roughness and restrained luminous flecks. Crystals remain dorsal-only and are never projected onto the palm.',
        'Preserve original rock/crack/moss PBR, no separate rock objects, material UV guide v11.336, other studios/projects and underlying skeletal animation.',
        'Check strict source seal plus focused field geometry and GPU compilation. Final real Moto/Quest visual acceptance stays with owner.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+used:]
