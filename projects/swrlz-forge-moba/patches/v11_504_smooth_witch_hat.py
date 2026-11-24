"""§E v11.504: independent Smooth Witch Hat starter, texture-first comparison.
Only appends a new starter/loader; both original hats remain unchanged.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_504_SMOOTH_WITCH_HAT'
PREVIOUS_SHA256 = 'db31f6261c8afc118506e72dd44e3f697dc89aebea9ffddc1740042c1dda6824'

def once(source, old, new, label):
    count = source.count(old)
    if count != 1:
        raise AssertionError(('se504', label, count, old[:100]))
    return source.replace(old, new, 1)

def apply(html):
    # Validate the entire previous §E build, not just the immediately prior marker.
    prior = hashlib.sha256(html.encode('utf-8')).hexdigest()
    assert prior == PREVIOUS_SHA256, ('se504 source chain', prior)
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_503_UV_ISLAND_ATLAS' in html
    script = (ROOT / 'runtime/smooth_witch_hat_v11_504.js').read_text('utf-8')
    assert 'SE504_SMOOTH_WITCH_HAT_END' in script
    html = once(html, 'window.SWRLZ_FORGE_BUILD=',
                script + '\nwindow.SWRLZ_FORGE_BUILD=', 'native starter loader')
    card = (
        '<button class="project-card den" data-project-template="smooth-witch-hat">'
        '<span class="project-icon">🎩</span>'
        '<strong>Smooth Witch Hat</strong>'
        '<span class="template-tag">STARTER MODEL · SINGLE MESH · TEXTURE FIRST</span>'
        '<p>A separate, smooth witch cone and continuous brim with the Sorting Hat '
        'UV artwork preserved. No sculpted face; ideal for comparing texture-driven '
        'appearance before adding facial cavities or rigging.</p>'
        '<span class="hint den-glow">Open in Model Studio</span>'
        '</button>'
    )
    html = once(html,
                '<button class="project-card den" data-project-template="sorting-hat-sculpted">',
                card + '<button class="project-card den" data-project-template="sorting-hat-sculpted">',
                'third independent starter card')
    html = once(html, 'function se128LaunchStartupProject(){',
                """function se128LaunchStartupProject(){
 if(new URLSearchParams(location.search).get('project')==='smooth-witch-hat'){
  window.se128StartupPending=true;
  queueMicrotask(()=>Promise.resolve(se504OpenSmoothWitchHat(true))
   .catch(error=>console.error('Smooth Witch Hat startup',error))
   .finally(()=>{window.se128StartupPending=false;}));
  return;
 }
""", 'deep link')
    for old, new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_503_UV_ISLAND_ATLAS', MARKER),
        ('ENGINE · MAKER v11.503', 'ENGINE · MAKER v11.504'),
        ('v11.503 · native UV seam and front/back island atlas',
         'v11.504 · independent smooth textured witch hat starter'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.503'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.504'"),
        ('<title>§wyrl§ Engine · Maker v11.503</title>',
         '<title>§wyrl§ Engine · Maker v11.504</title>')
    ):
        html = once(html, old, new, 'release metadata')
    old = " source.engine='§wyrl§ Engine · Maker v11.503';source.version=11.503;"
    assert html.count(old) == 5, ('se504 project provenance', html.count(old))
    html = html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.504';source.version=11.504;")
    key = 'const SE_RELEASE_NOTES='
    start = html.index(key) + len(key)
    notes, width = json.JSONDecoder().raw_decode(html[start:])
    notes['history'] = [x for x in notes.get('history', [])
                        if x.get('version') != 'v11.503']
    notes['history'].insert(0, {'version': 'v11.503',
                                 'changes': notes.get('changes', [])})
    notes.update(version='v11.504', date='2026-11-17',
                 title='Third Sorting Hat experiment — smooth texture-first witch hat',
                 changes=[
                     'Added Smooth Witch Hat as a third independent Model Studio starter card with its own canonical project ID and deep link.',
                     'Keeps the original watertight 7,859-vertex single-mesh topology, UV coordinates and painted Sorting Hat texture, but replaces sculpted facial relief and folds with a smooth cone, brim and inner liner.',
                     'Original Sorting Hat and Sculpted Sorting Hat starters are unchanged; this is a separate comparison project rather than an update or overwrite.',
                     'Loads through the existing Model Studio; visual verification on phone and Quest remains pending user acceptance.'
                 ])
    return html[:start] + json.dumps(notes, ensure_ascii=False,
                separators=(',', ':')).replace('</', r'<\/') + html[start+width:]
