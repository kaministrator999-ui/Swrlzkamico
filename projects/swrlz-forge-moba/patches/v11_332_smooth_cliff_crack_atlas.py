"""§E v11.332 — actually map owner-authored fracture outlines into Cliff Hand albedo."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_332_CLIFF_CRACK_ATLAS'

def once(html,old,new,label):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.332',label,n,old[:130]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/cliff_fracture_overlay_v11_332.js').read_text('utf8')
    assert 'function se332OverlayRockFractures(img,albedoCtx){' in js
    for token in (
        'function se292PaintAtlas(img){',
        'se292DrawKnuckleColor(albedo);',
        "m.drawImage(img,1152,384,size,size,0,0,size,size);",
        'window.SWRLZ_FORGE_BUILD=',
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_331_SMOOTH_CLIFF_MATERIAL_UV',
    ):
        # The fracture mask draw operation resides in the separately authored JS.
        if 'm.drawImage' not in token and token not in html:
            raise AssertionError(('v11.332', 'missing prerequisite', token))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',
              js+'\nwindow.SWRLZ_FORGE_BUILD=','inject owner fracture map processor')
    # Overlay the high-contrast authored fault mask after clean sandstone
    # and wrist-only moss, BEFORE the four decorative knuckle paint marks.
    html=once(html,' se292DrawKnuckleColor(albedo);',
              ' se332OverlayRockFractures(img,albedo);\n se292DrawKnuckleColor(albedo);',
              'reveal image-backed stone crack lines, not 3D geometry')
    previous=" source.engine='§wyrl§ Engine · Maker v11.331';source.version=11.331;"
    if html.count(previous)!=3:
        raise AssertionError(('v11.332','model provenance',html.count(previous)))
    html=html.replace(previous,
        " source.engine='§wyrl§ Engine · Maker v11.332';source.version=11.332;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_331_SMOOTH_CLIFF_MATERIAL_UV',MARKER),
      ('ENGINE · MAKER v11.331','ENGINE · MAKER v11.332'),
      ('v11.331 · Smooth Cliff Hand mapped PBR and AO UV repair',
       'v11.332 · authored rock fracture mask on Smooth Cliff Hand'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.331'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.332'"),
      ('<title>§wyrl§ Engine · Maker v11.331</title>',
       '<title>§wyrl§ Engine · Maker v11.332</title>'),
    ):
        html=once(html,old,new,'release identity')
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,used=json.JSONDecoder().raw_decode(html[at:])
    if not any(i.get('version')=='v11.331' for i in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{
          'version':'v11.331','changes':notes.get('changes',[])})
    notes.update(
      version='v11.332',title='Smooth Cliff Hand: original fracture mask now paints visible mineral seams',
      date='2026-11-07',changes=[
        'Inspect the actual owner-provided 1536×768 rock atlas: its clean sandstone color tile does not provide the strong fissures that exist in the separate bottom-right fracture mask.',
        'Compose that existing aligned fracture mask into clean sandstone after the wrist-moss blend and before the four native painted knuckles, creating dark natural mineral fault lines visible at mobile texture resolution.',
        'Use a one-pixel shoulder to retain crack contrast at typical 3D viewport minification, with zero extra geometry, floating rocks, emissive lines or additional texture fetches.',
        'Keep the original normal map, AO/secondary UV, roughness, moss restricted to the wrist, anatomical topology, rig/animation, other starter models and projects intact.',
        'Expose fracture-mask composition counts to diagnostics and validate the real pixels and exact source package. Final phone/Quest visual acceptance remains owner-controlled.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+used:]
