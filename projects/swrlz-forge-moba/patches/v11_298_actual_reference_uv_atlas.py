"""§E v11.298 actual illustration pixels on the Hooded Vanguard native UV islands.

Unlike v11.297's hand-drawn imitation, this patch loads the true generated
texture-sheet sample, verifies it byte-for-byte and embeds it into the hosted
static bundle. Only a new Hooded Vanguard starter is remapped.
"""
from pathlib import Path
import json,hashlib,base64

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_298_ACTUAL_IMAGE_UV_ATLAS'
ATLAS_DIR=ROOT/'payload/vanguard-real-art-v11-298'
EXPECTED='d34f6afc422cbfafe54dfbbd420752b12d37967654ea5c1443c031f3b6720b27'

def once(s,old,new,label):
    n=s.count(old)
    if n!=1: raise AssertionError(('v11.298',label,n,old[:110]))
    return s.replace(old,new,1)

def load_real_art():
    paths=[ATLAS_DIR/('part-%d.b64'%i) for i in range(4)]
    if not all(p.is_file() for p in paths):
        raise AssertionError('Actual generated atlas chunks are missing')
    source=''.join(p.read_text('ascii').strip() for p in paths)
    img=base64.b64decode(source,validate=True)
    if len(img)!=11291 or hashlib.sha256(img).hexdigest()!=EXPECTED:
        raise AssertionError('Imported REAL artwork image checksum does not match')
    if img[:3]!=b'\xff\xd8\xff' or img[-2:]!=b'\xff\xd9':
        raise AssertionError('Imported painting JPEG data truncated')
    return source

def apply(html):
    for required in (
        'function se297MakePBR(tile){',
        'se291HeroScene=function(){return se297Redesign(se297PreviousScene());};',
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_297_PAINTED_UV_VANGUARD',
        "window.SWRLZ_FORGE_BUILD={version:'v11.297'",
        '<strong>Hooded Vanguard · Painted Remaster</strong>'
    ):
        if required not in html:raise AssertionError(('v11.298 prerequisite',required))
    js=(ROOT/'runtime/hooded_vanguard_real_uv_v11_298.js').read_text('utf8')
    if js.count('__SE298_ATLAS_DATA_URL__')!=1:raise AssertionError('Missing image injection marker')
    js=js.replace('__SE298_ATLAS_DATA_URL__',json.dumps('data:image/jpeg;base64,'+load_real_art()))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
        'import actual painted pixels directly into the live renderer')
    html=once(html,
        '<strong>Hooded Vanguard · Painted Remaster</strong>',
        '<strong>Hooded Vanguard · Real Artwork UV</strong>',
        'starter model title')
    html=once(html,
        'Painted-UV hooded knight: rounded fitted face, hair and full hood, draped scarf, metal armor and five-finger gloves; Warcraft-style drawn cloth embroidery, armor edges, skin and leather across mapped color/normal/roughness textures. Static, no bird or weapon.',
        'Image-backed Hooded Vanguard: real pixels cropped from the generated concept-art texture sheet and UV-tiled across 17 editable native meshes (face, hair, hood, scarf, plate armor, cloth, coat, gloves and boots). Not procedural imitation. Static; no bird or weapon.',
        'starter project description')
    old=" source.engine='§wyrl§ Engine · Maker v11.297';source.version=11.297;"
    if html.count(old)!=3:raise AssertionError(('v11.298 native version count',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.298';source.version=11.298;")
    for a,b in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_297_PAINTED_UV_VANGUARD',MARKER),
        ('ENGINE · MAKER v11.297','ENGINE · MAKER v11.298'),
        ('v11.297 · character-art UV remaster','v11.298 · actual generated artwork UV mapping'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.297'",
          "window.SWRLZ_FORGE_BUILD={version:'v11.298'"),
        ('<title>§wyrl§ Engine · Maker v11.297</title>',
          '<title>§wyrl§ Engine · Maker v11.298</title>')
    ):html=once(html,a,b,'release identity')
    anchor='const SE_RELEASE_NOTES='
    at=html.index(anchor)+len(anchor)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Hooded Vanguard: actual generated texture image mapped to native UVs',
        date='2026-11-06',changes=[
          'Directly embed exact JPEG bytes sampled from the previously generated Hooded Vanguard UV artwork, with build-time SHA-256 validation. No procedural imitation artwork.',
          'UV-assign eleven regions of one shared 4x3 generated-image atlas to all seventeen editable native meshes. The image tiles correspond to face, hair, hood, scarf, uniform, breastplate, pauldrons, teal cloth, leather, gloves and boots.',
          'Keep the existing topology and actual editable material geometry; only freshly created Hooded Vanguard starter models receive remapped UV coordinates. Previously saved models and all other starters remain unchanged.',
          'Favor source-painted lighting/color with conservative physical roughness and metalness. Disable mipmapping across the packed tile boundaries to avoid color bleeding.',
          'Image was UV-resampled to fit a mobile-friendly 512x384 RGB atlas from the original illustration. The illustration is not a magically exact original topology UV bake; practical visual review and higher-resolution refinement remain owner-dependent.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
