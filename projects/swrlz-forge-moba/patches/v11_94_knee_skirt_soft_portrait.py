"""Arrange existing armor as a covered knee-length skirt; soften the portrait."""
from pathlib import Path
import json


def once(html, old, new):
    assert html.count(old) == 1, (old[:90], html.count(old))
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parents[1]
    html = once(html, 'function atelierAnimeGirlProject(original=MODEL_ATELIER_CANONICAL_PROJECT){',
                'function atelierAnimeGirlProjectV1193(original=MODEL_ATELIER_CANONICAL_PROJECT){')
    modules = ['model_atelier_portrait_v11_94.js', 'model_atelier_skirt_v11_94.js']
    js = '\n'.join((root / 'runtime' / name).read_text() for name in modules)
    wrapper = '''
function atelierAnimeGirlProject(original=MODEL_ATELIER_CANONICAL_PROJECT){
 const scene=atelierAnimeGirlProjectV1193(original);atelierPortraitV1194(scene);atelierKneeSkirtV1194(scene);
 const model=scene.project.modelAtelier;model.appearanceRevision='v11.94';if(model.referenceProfile)model.referenceProfile.version='v11.94';
 model.name='Prism · Knee-Length Festival Armor';scene.project.name=model.name;scene.engine='§wyrl§ Engine · Maker v11.94';
 model.artDirection='Soft smooth nose, subtly narrower head, rising amber eyes, visible attached cyan/coral hair piñatas, smooth anatomy and overlapping festival armor panels forming a full skirt above the kneecaps.';return scene;
}
'''
    html = once(html, '  function refreshList(){', js + wrapper + '\n  function refreshList(){')
    html = once(html, "'scenes/model-atelier-smooth-girl-v11-93.swyrl.json'",
                "'scenes/model-atelier-knee-armor-v11-94.swyrl.json'")
    for old, new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_93_SMOOTH_ANATOMY_PINATAS', 'SWYRL_ENGINE_DEPLOY_MARKER: V11_94_KNEE_SKIRT_SOFT_PORTRAIT'),
        ('ENGINE · MAKER v11.93', 'ENGINE · MAKER v11.94'),
        ('v11.93 · smooth anatomy and restored hair piñatas', 'v11.94 · full knee-length armor skirt and soft portrait'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.93'", "window.SWRLZ_FORGE_BUILD={version:'v11.94'"),
        ('<title>§wyrl§ Engine · Maker v11.93</title>', '<title>§wyrl§ Engine · Maker v11.94</title>'),
        ('<strong>Prism · Festival Girl and Hair Piñatas</strong>', '<strong>Prism · Knee-Length Festival Armor</strong>'),
        ('Attached hair piñatas, smooth face and exposed muscle contours, upward-sloping almond eyes, compact swept hair and layered festival tailoring. Native editing and export retained.',
         'Overlapping festival armor forms a full skirt above the kneecaps. Softer nose, subtly narrower face, smooth anatomy and original hair piñatas. Native editing and export retained.'),
    ]:
        html = once(html, old, new)
    prefix = 'const SE_RELEASE_NOTES='
    start = html.index(prefix) + len(prefix)
    notes, size = json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Full festival armor skirt · softer portrait', date='2026-10-24', changes=[
        'The existing lower armor panels overlap around the entire waist to form a covered festival skirt.',
        'Armor hems and attached trim end at or above the kneecaps; the fitted opaque underlayer retains crotch coverage.',
        'The nose has a softer bridge and rounded transition, and the head is slightly narrower to follow the references.',
        'Hair piñatas, rising eye corners, smooth skin contours, native materials, editing, save/import and textured export remain available.',
    ])
    html = html[:start] + json.dumps(notes, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[start + size:]
    return html
