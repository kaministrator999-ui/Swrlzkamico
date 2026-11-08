"""§E v11.352: restore native Model Studio transform quick access."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_352_MODEL_TRANSFORM_ACCESS'

def once(source,old,new):
    count=source.count(old)
    if count!=1:
        raise AssertionError(('v11.352 source anchor',old[:100],count))
    return source.replace(old,new,1)

def apply(html):
    # The v11.320 layout patch already sources current JS and CSS directly.
    # Do not add another transform system, toolbar injector, or cloned gizmo.
    assert 'function se320ModelTransformAccess(panel,inspector)' in html
    assert 'id="se320ModelTransform"' not in html or 'se320ModelTransform' in html
    assert 'source?.click();' in html
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_351_GAME_QUICK_ACTIONS',MARKER),
      ('ENGINE · MAKER v11.351','ENGINE · MAKER v11.352'),
      ('v11.351 · restored Game Engine quick actions',
       'v11.352 · Model Studio transform access restored'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.351'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.352'"),
      ('<title>§wyrl§ Engine · Maker v11.351</title>',
       '<title>§wyrl§ Engine · Maker v11.352</title>')
    ]:
        html=once(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.351';source.version=11.351;"
    assert html.count(old)==3
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.352';source.version=11.352;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,size=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.351' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{
            'version':'v11.351','changes':notes.get('changes',[])
        })
    notes.update(
      version='v11.352',date='2026-11-08',
      title='Model Studio: restore direct transform controls',
      changes=[
       'Move, Rotate and Scale are again directly available in the native Tool settings inspector when a model mesh is selected, including category mode on phone, desktop and Quest Browser.',
       'Expose X, Y and Z axis selection with positive/negative nudges. All buttons delegate to the original mesh transform handlers, selection gizmos, native validation and Undo history.',
       'Keep selection, components and grouping in their existing disclosure section. No new viewport overlay, extra transform math, shader change, 3D facial asset change or UV rewrites.',
       'Preserve Game Engine navigation improvements from v11.351 and all v11.350 immersive modeler controls. Owner device acceptance remains pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+size:]
