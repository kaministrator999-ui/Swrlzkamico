"""§E v11.545 — anatomy-aware display of real humanoid UV chart regions.
Read-only: no UV, texture, geometry, rig, or project state mutation.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_544_HUMANOID_SURFACE_PAINT'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_545_HUMANOID_UV_ANATOMY_VIEW'
def once(html,before,after,label):
    count=html.count(before)
    if count!=1:raise AssertionError(('se545',label,count,before[:130]))
    return html.replace(before,after,1)
def apply(html):
    runtime=(ROOT/'runtime/humanoid_uv_anatomy_view_v11_545.js').read_text('utf8')
    for token in ('SE545_UV_ANATOMY_VIEW_END','se545Faces','se545Export','SWYRL_E_UV_ANATOMY_545'):
        assert token in runtime,token
    html=once(html,'  function ensurePanel(){',runtime+'\n  function ensurePanel(){','native UV anatomy view')
    for old,new in (
       (OLD,MARKER),
       ('ENGINE · MAKER v11.544','ENGINE · MAKER v11.545'),
       ('v11.544 · anatomically mapped robot material and safe paint recovery',
        'v11.545 · inspect real UV anatomy without disturbing the texture'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.544'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.545'"),
       ('<title>§wyrl§ Engine · Maker v11.544</title>',
        '<title>§wyrl§ Engine · Maker v11.545</title>')
    ):
        html=once(html,old,new,'version identity')
    old=" source.engine='§wyrl§ Engine · Maker v11.544';source.version=11.544;"
    assert html.count(old)==5,('source provenance',html.count(old))
    html=html.replace(old,
       " source.engine='§wyrl§ Engine · Maker v11.545';source.version=11.545;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,chars=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes['history'] if x.get('version')!='v11.544']
    notes['history'].insert(0,{'version':'v11.544','changes':notes['changes']})
    notes.update(
      version='v11.545',date='2026-11-22',
      title='Humanoid UV anatomy — read-only chart identification',
      changes=[
       'Added an opt-in Humanoid UV anatomy view to the existing UV Editor. Highlights actual mapped head, torso front/back/sides, individual arms and legs, not a guessed six-panel UV diagram.',
       'Body regions are classified from selected native triangle positions/direction in their real correct UV coordinates.',
       'Export a 2048px color-coded anatomy reference for painting, explicitly not a texture to import.',
       'Preserved existing 84-chart xatlas packing, painted PNG, geometry, Undo/history and account saves; no risky UV repack or repaint.',
       'Maintained current geometry-anchored material repair, UV guide, distortion heatmap and VR Model Studio.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+chars:]
