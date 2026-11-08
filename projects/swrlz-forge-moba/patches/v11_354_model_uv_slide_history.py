"""§E v11.354: texture UV slide on the model, viewport Undo and Redo."""
import json
ROOT_MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_354_MODEL_UV_SLIDE_HISTORY'
def once(html,old,new):
    if html.count(old)!=1:
        raise AssertionError(('v11.354 anchor',old[:110],html.count(old)))
    return html.replace(old,new,1)
def apply(html):
    # Runtime is provided by the already lineage-pinned native Model Studio
    # modules. Never change raw mesh UV vertices or silently bake image pixels.
    for needle in [
        'function se336SlideSet(offset)', 'function se336InstallSlideEvents()',
        'window.SWYRLZ_E_MODEL_UV_SLIDE=Object.freeze',
        'part.uvPaintOffset=next;', 'texture.offset.set(slide[0],slide[1]);',
        'data-se320-history="undo"', 'data-se320-history="redo"',
        'data-se320-uv="toggle"', 'swrlz:uv-slide-change'
    ]:
        if needle not in html:
            raise AssertionError(('v11.354 missing native integration',needle))
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_353_MODEL_VIEWPORT_TRANSFORM',ROOT_MARKER),
        ('ENGINE · MAKER v11.353','ENGINE · MAKER v11.354'),
        ('v11.353 · selected model transforms in viewport','v11.354 · on-model UV texture slide and viewport history'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.353'","window.SWRLZ_FORGE_BUILD={version:'v11.354'"),
        ('<title>§wyrl§ Engine · Maker v11.353</title>','<title>§wyrl§ Engine · Maker v11.354</title>')
    ]:
        html=once(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.353';source.version=11.353;"
    assert html.count(old)==3
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.354';source.version=11.354;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.353' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.353','changes':notes.get('changes',[])})
    notes.update(version='v11.354',date='2026-11-08',
        title='On-model UV slide with viewport Undo and Redo',
        changes=[
            'A selected, textured mesh now exposes UV Slide next to Move, Rotate and Scale in the viewport top toolbar.',
            'Drag on the actual selected mesh to offset the imported texture without moving the geometry or rewriting native UV vertex coordinates.',
            'Fine U/V nudges and Reset UV update a persistent per-part UV texture offset in model project saves and JSON exports.',
            'Every completed UV drag uses one native Undo checkpoint. Viewport Undo/Redo forwards to original 50-step model history; selection remains active when still present.',
            'The compact toolbar scrolls horizontally on phones; hidden native controls retain their handlers. No duplicate inspector transform bar.',
            'Existing textures without UV offsets render at original alignment; only explicitly adjusted painted meshes change their texture mapping.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
