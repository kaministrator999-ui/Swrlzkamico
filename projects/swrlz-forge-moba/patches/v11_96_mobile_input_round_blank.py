"""Fix mobile editor focus zoom and make blank-model starter spherical."""
import hashlib
import json

def once(s, a, b):
    count = s.count(a)
    assert count == 1, (a[:90], count)
    return s.replace(a, b, 1)

def apply(html):
    # The independent blank-model starter originally used deliberately uneven
    # dimensions. Edit ONLY that template; preserve all saved character models.
    html = once(html,
        "id:'model-seed',name:'Model blockout',kind:'sphere',position:[0,1.5,0],rotation:[0,0,0],scale:[.5,.6,.8]",
        "id:'model-seed',name:'Model blockout',kind:'sphere',position:[0,1.5,0],rotation:[0,0,0],scale:[.6,.6,.6]")
    # Keep browser pinch/zoom accessibility. Prevent common focus-triggered page
    # magnification by making every mobile editable text/numeric field >=16px.
    # Important beats earlier 12px tool-dock and transform-field rules.
    css = """<style id="se-v1196-mobile-input-size">
@media (max-width: 900px), (pointer: coarse) {
  .model-atelier input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="color"]):not([type="file"]),
  .model-atelier select, .model-atelier textarea {
    font-size: 16px !important;
  }
}
</style>"""
    html = once(html, '</head>', css + '</head>')
    replacements = [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_95_FITTED_SKIRT_WAIST',
         'SWYRL_ENGINE_DEPLOY_MARKER: V11_96_MOBILE_INPUT_ROUND_BLANK'),
        ('ENGINE · MAKER v11.95', 'ENGINE · MAKER v11.96'),
        ('v11.95 · fitted waist and covered festival skirt',
         'v11.96 · mobile inputs and round blank model'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.95'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.96'"),
        ('<title>§wyrl§ Engine · Maker v11.95</title>',
         '<title>§wyrl§ Engine · Maker v11.96</title>'),
    ]
    for old, new in replacements:
        html = once(html, old, new)
    prefix = 'const SE_RELEASE_NOTES='
    start = html.index(prefix) + len(prefix)
    notes, size = json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Mobile model input focus and spherical blank starter',
                 date='2026-10-23', changes=[
        'New Model Project starts with a uniform 0.6 x 0.6 x 0.6 sphere, not a stretched egg.',
        'On phone-sized or coarse-pointer screens Model Atelier editable inputs use 16px text, reducing browser focus zoom while preserving user pinch-to-zoom.',
        'No changes to historical model scenes, hero anatomy, materials, exports or saved character geometry.'
    ])
    html = html[:start] + json.dumps(notes, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[start + size:]
    raw = html.encode('utf-8')
    print('SWRLZ_V1196_BUILD_MEASURE', len(raw), hashlib.sha256(raw).hexdigest(), flush=True)
    return html
