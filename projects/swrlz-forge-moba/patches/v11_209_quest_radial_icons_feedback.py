"""§E v11.209: polished Sheep Tag Play quick-wheels without changing inputs.
Append-only; original hold/tap gameplay and authority remain source-of-truth.
"""
from pathlib import Path
import json
def once(s,old,new):
    count=s.count(old)
    assert count==1,('v11.209 expected inherited source',old[:140],count)
    return s.replace(old,new,1)
def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_sheep_radial_icons_feedback_v11_209.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_208_QUEST_BIOMES_FOG_DEPTH',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_209_SHEEP_RADIAL_ICONS_FEEDBACK'),
      ('ENGINE · MAKER v11.208','ENGINE · MAKER v11.209'),
      ('v11.208 · Sheep Tag Quest four-biome world and fog-layer stability',
       'v11.209 · Sheep Tag Quest graphical house and ability selectors'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.208'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.209'"),
      ('<title>§wyrl§ Engine · Maker v11.208</title>',
       '<title>§wyrl§ Engine · Maker v11.209</title>'),
    ]:html=once(html,old,new)
    tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Sheep Tag Quest Play: illustrated rapid-build houses and skill radial with readable status',
      date='2026-11-01',changes=[
       'In the existing A-hold house radial and X-hold ability radial, each option now receives a stylized original pictogram: Farm cottage, Income Farm with gold emblem, fortified farm, Mirror split, Totem crystal or Cancel/None. Illustrations are created as 128px shared CanvasTextures only once per XR session.',
       'The original compact radial uses bright selectable wedge sectors, larger active icons, an active center-image readout, clear separate option text and a small cached info caption. Gold costs come from the authoritative stBuildingConfig and current sheep resources; unaffordable houses are dimmed. Ability rule-lock states and Totem house selection are surfaced without bypassing native cooldown/cast validation.',
       'Subtle animation uses only a ring of eight preallocated glints and simple rotation/material transitions during the existing controller-hold frames. No per-frame canvas/text uploads, additional renderer, new physics objects or input-loop overhead.',
       'The existing hold A/select/release and tap A/repeat build, hold X/select/release and tap X/activate, 3.6m grid, direct Quest movement, menu hit priority, all authorizations and gameplay camera remain identical. Graphic resources are disposed at XR cleanup; shared native se195Text textures remain owned by the prior menu cache.',
       'Full camera/inspector floating panel manager, actual Quest performance capture and deeper map-geometry remodel remain separate tracked tasks.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
