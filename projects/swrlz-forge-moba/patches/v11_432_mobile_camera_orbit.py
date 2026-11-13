"""§E v11.432 — non-destructive mobile Model Studio orbit direction correction."""
import json

MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_432_MOBILE_CAMERA_ORBIT'

def one(html, before, after):
    matches = html.count(before)
    assert matches == 1, ('v11.432 expected one anchor', before[:130], matches)
    return html.replace(before, after, 1)

def apply(html):
    # Fix the final assembled editor. Historical patches depend on the
    # original native source, and a pre-assembly mutation breaks their anchors.
    # Operate on the assembled editor: the base runtime file by itself is NOT the
    # published artifact. Keep the latest v11.430 camera pitch bounds.
    old = 'orbit.yaw=pressed.yaw-dx*.008;orbit.pitch=THREE.MathUtils.clamp(pressed.pitch+dy*.006,-Math.PI/2+.001,Math.PI/2-.001);'
    new = "const touch=e.pointerType==='touch';orbit.yaw=pressed.yaw+(touch?dx:-dx)*.008;orbit.pitch=THREE.MathUtils.clamp(pressed.pitch+(touch?-dy:dy)*.006,-Math.PI/2+.001,Math.PI/2-.001);"
    html = one(html, old, new)
    for before, after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_431_MODEL_GIZMO_ACCESS', MARKER),
        ('ENGINE · MAKER v11.431', 'ENGINE · MAKER v11.432'),
        ('v11.431 · comfortable touch and VR transform handles', 'v11.432 · mobile camera orbit direction corrected'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.431'", "window.SWRLZ_FORGE_BUILD={version:'v11.432'"),
        ('<title>§wyrl§ Engine · Maker v11.431</title>', '<title>§wyrl§ Engine · Maker v11.432</title>'),
    ]:
        html = one(html, before, after)
    before = " source.engine='§wyrl§ Engine · Maker v11.431';source.version=11.431;"
    assert html.count(before) == 5, ('v11.432 provenance', html.count(before))
    html = html.replace(before, " source.engine='§wyrl§ Engine · Maker v11.432';source.version=11.432;")
    key = 'const SE_RELEASE_NOTES='
    at = html.index(key) + len(key)
    notes, count = json.JSONDecoder().raw_decode(html[at:])
    if not any(item.get('version') == 'v11.431' for item in notes.get('history', [])):
        notes.setdefault('history', []).insert(0, {'version':'v11.431','changes':notes.get('changes', [])})
    notes.update(
        version='v11.432', date='2026-11-12',
        title='Correct mobile Model Studio orbit direction',
        changes=[
            'One-finger touchscreen drags now orbit the Model Studio camera in the finger direction horizontally and vertically.',
            'Desktop mouse orbit keeps its previous behavior. Two-finger pinch/pan, tap selection, transform handles, project history and Quest VR input are unchanged.',
            'Camera orbit remains nondestructive and retains the existing near-pole pitch clamps.'
        ]
    )
    return html[:at] + json.dumps(notes, ensure_ascii=False, separators=(',', ':')).replace('</', r'<\/') + html[at+count:]
