"""§E v11.542 — genuine anatomical humanoid UV atlas and safe UV workflow.

The previous 4-panel front/back/brim projector is an experimental tool for
cone-like models, not a general humanoid unwrap. Its guide can create tall,
degenerate arms/legs. Replace starter UV data with offline xatlas-authored
charts and stop this misleading candidate on this specific body.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_541_HUMANOID_STARTER_CATEGORY'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_542_HUMANOID_RELAXED_UV_ATLAS'

def once(html,before,after,label):
    count=html.count(before)
    if count!=1:
        raise AssertionError(('se542',label,count,before[:130]))
    return html.replace(before,after,1)

def apply(html):
    loader=(ROOT/'runtime/humanoid_uv_starter_v11_542.js').read_text('utf8')
    guard=(ROOT/'runtime/humanoid_uv_guard_v11_542.js').read_text('utf8')
    for token in ('se542OpenHumanoid','se537OpenMannequin=se542OpenHumanoid','SE542_HUMANOID_UV_STARTER_END'):
        assert token in loader,token
    for token in ('se542IsHumanoidUV','SE542_HUMANOID_UV_GUARD_END','se503Candidate=function()'):
        assert token in guard,token
    # Place the v11.503 guard inside the existing native Model Atelier
    # lexical scope, not the global/external UI script.
    html=once(html,'  function ensurePanel(){',guard+'\n  function ensurePanel(){','native UV guard')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',loader+'\nwindow.SWRLZ_FORGE_BUILD=','new starter route')
    html=once(html,
       '<strong>Futuristic Humanoid · Detailed Hands</strong>',
       '<strong>Futuristic Humanoid · UV-Ready Hands</strong>',
       'starter name')
    html=once(html,
       '<span class="template-tag">STARTER MODEL · ONE UV BODY · FIVE FINGERS PER HAND</span>',
       '<span class="template-tag">STARTER MODEL · ONE BODY · RELAXED PAINT-READY UVS</span>',
       'model classification')
    html=once(html,
       "'robotic-humanoid-mannequin':['Futuristic Humanoid · Detailed Hands','model-atelier','model-atelier']",
       "'robotic-humanoid-mannequin':['Futuristic Humanoid · UV-Ready Hands','model-atelier','model-atelier']",
       'VR starter index')
    for before,after in (
       (OLD,MARKER),
       ('ENGINE · MAKER v11.541','ENGINE · MAKER v11.542'),
       ('v11.541 · restored mannequin Starter Models category',
        'v11.542 · relaxed humanoid UV atlas and safe editor projection'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.541'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.542'"),
       ('<title>§wyrl§ Engine · Maker v11.541</title>',
        '<title>§wyrl§ Engine · Maker v11.542</title>')
    ):
        html=once(html,before,after,'version')
    old=" source.engine='§wyrl§ Engine · Maker v11.541';source.version=11.541;"
    assert html.count(old)==5,('source provenance',html.count(old))
    html=html.replace(old,
       " source.engine='§wyrl§ Engine · Maker v11.542';source.version=11.542;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,chars=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes['history'] if x.get('version')!='v11.541']
    notes['history'].insert(0,{'version':'v11.541','changes':notes['changes']})
    notes.update(
      version='v11.542',date='2026-11-22',
      title='Futuristic Humanoid — relaxed non-overlapping UV charts',
      changes=[
       'Replaced the original distorted/pinched 6-sector cylindrical UV projection with geometry-aware xatlas chart parameterization and packing, retaining one watertight mesh and independent UV seam vertices.',
       'Reprojected the preexisting 1024px satin/graphite/teal PNG onto the new UV charts rather than destroying its painted material association.',
       'Published a 2048px diagnostic UV layout from the same exact new UV coordinates used by the shipped native mannequin scene.',
       'Prevented the generic experimental front/back/brim projection from generating unsafe replacement UV candidates for the humanoid; current UV guide, paint preview and heatmap remain available.',
       'Kept the stable Starter Models ID, both articulated hands, source geometry, account projects, VR tools and old user saves unchanged.',
       'Verified UV triangle area, atlas occupancy, seam validity, material PNG registration and current live model loader. Manual Moto/Quest inspection remains owner acceptance.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+chars:]
