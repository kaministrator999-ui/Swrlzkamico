"""Fit the festival skirt waist to the existing bodice and preserve coverage."""
from pathlib import Path
import json


def once(html, old, new):
    assert html.count(old) == 1, (old[:90], html.count(old))
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parents[1]
    html = once(html, 'function atelierAnimeGirlProject(original=MODEL_ATELIER_CANONICAL_PROJECT){',
                'function atelierAnimeGirlProjectV1194(original=MODEL_ATELIER_CANONICAL_PROJECT){')
    js = (root / 'runtime/model_atelier_skirt_fit_v11_95.js').read_text()
    wrapper = '''
function atelierAnimeGirlProject(original=MODEL_ATELIER_CANONICAL_PROJECT){
 const scene=atelierAnimeGirlProjectV1194(original);atelierFittedSkirtV1195(scene);
 const model=scene.project.modelAtelier;model.appearanceRevision='v11.95';if(model.referenceProfile)model.referenceProfile.version='v11.95';
 model.name='Prism · Fitted Festival Armor';scene.project.name=model.name;scene.engine='§wyrl§ Engine · Maker v11.95';
 model.artDirection='Fitted skirt waist following the bodice, smoothly flared overlapping festival armor above the kneecaps, opaque coverage, soft portrait, smooth anatomy and original attached hair piñatas.';return scene;
}
'''
    html = once(html, '  function refreshList(){', js + wrapper + '\n  function refreshList(){')
    replacements = [
        ("'scenes/model-atelier-knee-armor-v11-94.swyrl.json'", "'scenes/model-atelier-fitted-waist-v11-95.swyrl.json'"),
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_94_KNEE_SKIRT_SOFT_PORTRAIT', 'SWYRL_ENGINE_DEPLOY_MARKER: V11_95_FITTED_SKIRT_WAIST'),
        ('ENGINE · MAKER v11.94', 'ENGINE · MAKER v11.95'),
        ('v11.94 · full knee-length armor skirt and soft portrait', 'v11.95 · fitted waist and covered festival skirt'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.94'", "window.SWRLZ_FORGE_BUILD={version:'v11.95'"),
        ('<title>§wyrl§ Engine · Maker v11.94</title>', '<title>§wyrl§ Engine · Maker v11.95</title>'),
        ('<strong>Prism · Knee-Length Festival Armor</strong>', '<strong>Prism · Fitted Festival Armor</strong>'),
        ('Overlapping festival armor forms a full skirt above the kneecaps. Softer nose, subtly narrower face, smooth anatomy and original hair piñatas. Native editing and export retained.',
         'A fitted waist blends into the covered festival skirt above the knees. Soft portrait, smooth anatomy and original hair piñatas. Native editing and export retained.'),
    ]
    for old, new in replacements:
        html = once(html, old, new)
    prefix = 'const SE_RELEASE_NOTES='
    start = html.index(prefix) + len(prefix)
    notes, size = json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Fitted festival skirt waist', date='2026-10-24', changes=[
        'The upper skirt follows the waist and bodice more closely, with a smooth transition into the lower flare.',
        'Matching trim and the waistband follow the fitted silhouette; full skirt coverage and the knee-length limit remain.',
        'The soft portrait, smooth anatomy, attached hair piñatas, native editing, save/import and textured export are preserved.',
    ])
    html = html[:start] + json.dumps(notes, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[start + size:]
    return html
