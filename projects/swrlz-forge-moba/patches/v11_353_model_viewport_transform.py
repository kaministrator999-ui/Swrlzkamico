"""§E v11.353: native transform controls in the selected mesh viewport toolbar."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_353_MODEL_VIEWPORT_TRANSFORM'

def once(source,old,new):
    count=source.count(old)
    if count!=1:
        raise AssertionError(('v11.353 source anchor',old[:100],count))
    return source.replace(old,new,1)

def apply(html):
    # This is still the same native transform editor, only a viewport access
    # point; no alternate gizmo implementation or change to the UV source.
    for needle in [
      "function se320ModelTransformAccess(panel,scene)",
      "se320ModelTransformAccess(panel,q('.atelier-scene',panel));",
      "source.closest('.amq-line')?.classList.add('se320-native-transform-proxy');",
      "source?.click();",
      "const active=!!state?.open&&!!state?.selected&&!panel.hidden;"
    ]:
        if needle not in html:
            raise AssertionError(('v11.353 viewport controls',needle))
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_352_MODEL_TRANSFORM_ACCESS',MARKER),
      ('ENGINE · MAKER v11.352','ENGINE · MAKER v11.353'),
      ('v11.352 · Model Studio transform access restored',
       'v11.353 · selected model transforms in viewport'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.352'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.353'"),
      ('<title>§wyrl§ Engine · Maker v11.352</title>',
       '<title>§wyrl§ Engine · Maker v11.353</title>')
    ]:
        html=once(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.352';source.version=11.352;"
    assert html.count(old)==3
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.353';source.version=11.353;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,size=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.352' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{
            'version':'v11.352','changes':notes.get('changes',[])
        })
    notes.update(
      version='v11.353',date='2026-11-08',
      title='Selection-only viewport transform toolbar',
      changes=[
       'Show native Move, Rotate, Scale and X/Y/Z nudge controls in a compact bar near the top of the 3D Model Studio viewport only while a model mesh is selected.',
       'The viewport controls remain available with the sidebar inspector collapsed, preserving the model canvas and the existing camera controls.',
       'Reuse original mesh transform actions, gizmos, grouped selection, validated native mutations and Undo. Remove duplicate transform rows from the sidebar without deleting their backing handlers.',
       'Leave existing UV layouts, face and eye geometry, VR editor and Game Engine controls unchanged. Physical phone and Quest acceptance remains owner testing.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+size:]
