"""§E v11.297: reference-guided UV surface artwork + refined knight forms."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.297',label,n,old[:110]))
    return s.replace(old,new,1)

def apply(html):
    for t in (
      'function se296HeroScene(){',
      'se291HeroScene=se296HeroScene;',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_296_VANGUARD_REBUILT',
      "window.SWRLZ_FORGE_BUILD={version:'v11.296'",
      '<strong>Hooded Vanguard · Rebuilt Character</strong>'
    ):
        if t not in html:raise AssertionError(('v11.297 source missing',t))
    js=(ROOT/'runtime/hooded_vanguard_painted_v11_297.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
      'insert material painting and fitted character override')
    html=once(html,'<strong>Hooded Vanguard · Rebuilt Character</strong>',
      '<strong>Hooded Vanguard · Painted Remaster</strong>',
      'update model starter card title')
    html=once(html,
      'Rebuilt hooded knight: smooth fitted face, dark layered hair, curved cloth hood, sculpted scarf and armor, five-finger gloves, teal coat, UV-mapped fabric, metal, leather and skin. Static model; no bird or weapon.',
      'Painted-UV hooded knight: rounded fitted face, hair and full hood, draped scarf, metal armor and five-finger gloves; Warcraft-style drawn cloth embroidery, armor edges, skin and leather across mapped color/normal/roughness textures. Static, no bird or weapon.',
      'update starter model details')
    old=" source.engine='§wyrl§ Engine · Maker v11.296';source.version=11.296;"
    assert html.count(old)==3,('v11.297 project versions',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.297';source.version=11.297;")
    for a,b in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_296_VANGUARD_REBUILT',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_297_PAINTED_UV_VANGUARD'),
      ('ENGINE · MAKER v11.296','ENGINE · MAKER v11.297'),
      ('v11.296 · rebuilt hooded knight anatomy and materials',
       'v11.297 · character-art UV remaster'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.296'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.297'"),
      ('<title>§wyrl§ Engine · Maker v11.296</title>',
       '<title>§wyrl§ Engine · Maker v11.297</title>')
    ):html=once(html,a,b,'build identity')
    anchor='const SE_RELEASE_NOTES='
    at=html.index(anchor)+len(anchor)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Hooded Vanguard UV-painted clothing and improved head/hood',
      date='2026-11-06',changes=[
      'Remaster the freshly opened Hooded Vanguard Starter Model with a rounded, better-fitted head, fabric hood crown and side drape, reduced flat scarf bib, softer tapering hair, and flowing coat panels. Preserve existing 17-editable-part structure and five-finger hands.',
      'Replace basic noise/stripes with purpose-painted, UV-aligned character texture artwork for face, hair, gold-trimmed pale hood, layered embroidered scarf, engraved dark armor, shoulder plates, dark suit, teal coat, leather, boots and gloves.',
      'Generate corresponding conservative normal and roughness maps from each painted tile; no separate geometry for details such as metallic edging, fabric folds, gold embroidery or glove seams.',
      'The supplied concept atlas is a design reference rather than a matching UV bake. Surface art is mapped to the real native UV coordinates, not pasted as a mismatched concept sheet.',
      'Keep v11.296 original generator in patch history, previous saved scenes, §C, Sheep Tag, VR and other model starters intact. Static with no bird/weapon/full-body rig; owner phone/Quest appearance inspection remains the visual gate.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
