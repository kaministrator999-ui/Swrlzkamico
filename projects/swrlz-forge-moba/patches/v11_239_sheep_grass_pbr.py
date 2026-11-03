"""§E v11.239 — candidate Sheep Tag meadow color/normal/roughness material.
Append-only runtime injection; preserve previous saved scenes and native simulation.
"""
from pathlib import Path
import json

def once(html, old, new, label):
    n=html.count(old)
    if n!=1:
        raise AssertionError(('v11.239 grass material anchor',label,n,old[:90]))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    grass=(root/'runtime/sheep_grass_pbr_v11_239.js').read_text(encoding='utf-8')
    for key in ('function stMakeVisual(type)', 'MoonbellWildwoodGround', 'stMeadowGround',
                'window.SWRLZ_FORGE_BUILD=', 'SWYRL_ENGINE_DEPLOY_MARKER: V11_238_QUEST_RADIAL_AND_WORKSPACE'):
        assert key in html, ('v11.239 grass prerequisite missing',key)
    html=once(html,'window.SWRLZ_FORGE_BUILD=',grass+'\nwindow.SWRLZ_FORGE_BUILD=','inject runtime')
    before=" source.engine='§wyrl§ Engine · Maker v11.238';source.version=11.238;"
    after=" source.engine='§wyrl§ Engine · Maker v11.239';source.version=11.239;"
    if html.count(before)!=2:raise AssertionError(('grass provenance',html.count(before)))
    html=html.replace(before,after)
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_238_QUEST_RADIAL_AND_WORKSPACE',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_239_SHEEP_GRASS_PBR'),
      ('ENGINE · MAKER v11.238','ENGINE · MAKER v11.239'),
      ('v11.238 · Quest radial menu frame recovery and studio layout',
       'v11.239 · Sheep Tag full grass material'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.238'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.239'"),
      ('<title>§wyrl§ Engine · Maker v11.238</title>',
       '<title>§wyrl§ Engine · Maker v11.239</title>')
    ):html=once(html,old,new,'release identity')
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(
      title='Sheep Tag grass material with matching base color, normal and matte roughness',
      date='2026-11-03',
      changes=[
        'Use the owner-created grassy color-map artwork, packaged as a small Quest-friendly WebP tile, as material detail over existing green meadow and Wildwood surfaces.',
        'Preserve authored Wildwood paths, meadow routes and sanctuary map painting by retaining the non-green source colors when composing the new base-color map.',
        'Generate matching tangent-space normal and matte roughness maps from the same color source at load time, with subtle normal strength, 16 world repeats and mipmapped textures.',
        'Prepare each ground once only, with no extra geometry or new render loop. Preserve the existing fog, navigation collision, buildings, sheep/wolf behavior, gameplay and VR input.',
        'Desktop and Quest 2 material/lighting acceptance is owner-tested; texture source is an artistic generated reference and roughness/normal are computed estimates.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
