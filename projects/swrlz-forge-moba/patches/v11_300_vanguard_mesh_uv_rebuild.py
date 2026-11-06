"""§E v11.300: reconstruct actual knight geometry and artwork UVs together.

Preserve every original patch (including v11.299) and saved user projects.
Only new Starter Models Hooded Vanguard construction is superseded.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_300_VANGUARD_MESH_UV_COUPLED'

def once(html,old,new,label):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.300',label,n,old[:110]))
    return html.replace(old,new,1)

def apply(html):
    for token in (
      'function se299ExtractImage(image,family){',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_299_REAL_IMAGE_UV_ALIGNMENT',
      "window.SWRLZ_FORGE_BUILD={version:'v11.299'",
      '<strong>Hooded Vanguard · Corrected Artwork UV</strong>'
    ):
        if token not in html:raise AssertionError(('v11.300 missing prerequisite',token))
    js=(ROOT/'runtime/hooded_vanguard_mesh_uv_v11_300.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
      'insert coupled mesh+UV character factory')
    html=once(html,
      '<strong>Hooded Vanguard · Corrected Artwork UV</strong>',
      '<strong>Hooded Vanguard · Geometry + UV Rebuild</strong>',
      'starter card label')
    html=once(html,
      'Corrected image-backed Hooded Vanguard: original concept-art pixels separated into actual painted surfaces, aligned to each native mesh local UV instead of stretching entire illustrated cutouts. Front-only facial painting, no paper backgrounds. Static; no bird or weapon.',
      'New shape-matched Hooded Vanguard: rebuilt sculpted hood, layered hair, continuous face, actual draped scarf, tapered armor, curved pauldrons and two-sided flowing teal coats. Every surface has matched native UVs plus actual generated artwork details. 17 editable parts; static; no bird or weapon.',
      'starter card description')
    old=" source.engine='§wyrl§ Engine · Maker v11.299';source.version=11.299;"
    if html.count(old)!=3:raise AssertionError(('v11.300 source native versions',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.300';source.version=11.300;")
    for a,b in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_299_REAL_IMAGE_UV_ALIGNMENT',MARKER),
      ('ENGINE · MAKER v11.299','ENGINE · MAKER v11.300'),
      ('v11.299 · source-image material UV alignment','v11.300 · coupled model geometry and painted UV rebuild'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.299'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.300'"),
      ('<title>§wyrl§ Engine · Maker v11.299</title>',
       '<title>§wyrl§ Engine · Maker v11.300</title>')
    ):html=once(html,a,b,'release build identity')
    anchor='const SE_RELEASE_NOTES='
    at=html.index(anchor)+len(anchor)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(
      title='Hooded Vanguard: rebuilt mesh contours and UV art together',
      date='2026-11-06',
      changes=[
       'Rebuild actual character geometry and its UV coordinates as a single change, after owner Android screenshots showed a Boba Fett-like oversized hood, slab armor, spear-shaped coattails, flat scarf, mismatched UVs and artificial photographic details.',
       'Keep continuous round anatomically scaled face without separate chin objects, a fitted layered hair crown, sculpted locks and fringe. Shape a true arched hood opening, separate canopy and mantle, and fitted gold-border geometry instead of a helmet slab.',
       'Refit the neck cowl and draped V-shaped chest scarf, a tapered curved breastplate, smaller formed shoulder pauldrons and two actual two-sided cloth panels extending from waist to ankle. Preserve 17 independently editable native parts and prior articulated fingers.',
       'Author new explicit local UVs on every rebuilt surface and rebuild the material textures to use only carefully sampled regions of the previously verified original character-art image, rather than sticking entire illustrated objects onto anatomy.',
       'Restrict face art to front longitude, body back to dark uniform, coat to teal sample and hood to ivory textile with its trim. Reuse 11 coherent paint-and-UV material families and source-image SHA with conservative PBR response.',
       'Preserve all saved scenes, other model starters, §C editor, VR, Sheep Tag and historical patches. Still a static model without bird, weapon or full skeletal rig. Owner visual comparison and device quality acceptance remain pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
