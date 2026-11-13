"""§E v11.433 — saved mobile orbit inversion and accessible native touch gizmos."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_433_CAMERA_PREFERENCES_TOUCH_GIZMOS'
def one(src,old,new):
    assert src.count(old)==1,('v11.433 source anchor',old[:140],src.count(old))
    return src.replace(old,new,1)

def apply(html):
    # Apply after v11.432 to preserve all historical patch anchors/lineage.
    native=(ROOT/'runtime/model_camera_preferences_v11_433.js').read_text('utf8')
    html=one(html,'/* ATELIER_BRIDGE_END */',native+'\n/* ATELIER_BRIDGE_END */')
    old="const touch=e.pointerType==='touch';orbit.yaw=pressed.yaw+(touch?dx:-dx)*.008;orbit.pitch=THREE.MathUtils.clamp(pressed.pitch+(touch?-dy:dy)*.006,-Math.PI/2+.001,Math.PI/2-.001);"
    new="const touch=e.pointerType==='touch',invertTouch=touch&&se433CameraPrefs.inverted;orbit.yaw=pressed.yaw+(touch&&!invertTouch?dx:-dx)*.008;orbit.pitch=THREE.MathUtils.clamp(pressed.pitch+(touch&&!invertTouch?-dy:dy)*.006,-Math.PI/2+.001,Math.PI/2-.001);"
    html=one(html,old,new)
    html=one(html,'se430ModelCamera.install();loop();','se430ModelCamera.install();se433CameraPrefs.install(panel);loop();')
    # Existing v11.431 native pick path remains authoritative; slightly larger
    # 56px touch targets and 28px shaft corridor improve grip without a new
    # mesh/gizmo, a bigger floating toolbar, or expanded desktop/XR picking.
    for before,after in [
        ("const targetRadius=type=>type==='touch'?22:type==='pen'?18:12;","const targetRadius=type=>type==='touch'?28:type==='pen'?18:12;"),
        ("o.scale.setScalar(unit*(touch?10:8)/Math.max(radius,.00001));","o.scale.setScalar(unit*(touch?12:8)/Math.max(radius,.00001));"),
        ("o.scale.setScalar(unit*(touch?11:9)/(radius*item.ring.scale.x));","o.scale.setScalar(unit*(touch?13:9)/(radius*item.ring.scale.x));"),
        ("if(along<=Math.min(radius,coarse()?11:6))distance=along+radius*.4;","if(along<=Math.min(radius,coarse()?14:6))distance=along+radius*.4;"),
        ("touchRadius:22,mouseRadius:12","touchRadius:28,mouseRadius:12"),
    ]:html=one(html,before,after)
    css="""<style id="se433CameraSettingsStyle">
.model-atelier .atelier-viewbar #se433CameraSettings,.model-atelier .atelier-viewbar #se433CameraSettings summary{pointer-events:auto}
.model-atelier #se433CameraSettings{position:relative;flex:0 0 auto;align-self:center;z-index:190;color:#e9f3ff;font-size:12px}
.model-atelier #se433CameraSettings>summary{list-style:none;cursor:pointer;display:flex;align-items:center;padding:9px 12px;min-height:44px;border:1px solid #5b7494;border-radius:8px;background:#293b56;font-size:12px;font-weight:600;white-space:nowrap;user-select:none}
.model-atelier #se433CameraSettings>summary::-webkit-details-marker{display:none}
.model-atelier #se433CameraSettings[open]>summary{border-color:#84d7e5}
.model-atelier #se433CameraSettings .se433-camera-settings-body{position:absolute;z-index:220;top:calc(100% + 5px);left:0;width:min(265px,calc(100vw - 35px));box-sizing:border-box;padding:12px;border:1px solid #657c9b;border-radius:9px;background:#15243a;box-shadow:0 12px 25px #0009}
.model-atelier #se433CameraSettings .se433-camera-invert{display:flex;flex-direction:row;align-items:center;gap:9px;min-height:44px;font-size:13px;color:#f3f8ff;cursor:pointer}
.model-atelier #se433CameraSettings input[type=checkbox]{width:21px;height:21px;flex:0 0 auto;accent-color:#65d7eb}
.model-atelier #se433CameraSettings small{display:block;margin-top:6px;font-size:11px;line-height:1.5;color:#c2d3e9}
.model-atelier #se433CameraSettings :focus-visible{outline:2px solid #73e2ee;outline-offset:2px}
@media(max-width:600px){.model-atelier #se433CameraSettings .se433-camera-settings-body{left:auto;right:0}}
</style>"""
    html=one(html,'</head>',css+'\n</head>')
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_432_MOBILE_CAMERA_ORBIT',MARKER),
        ('ENGINE · MAKER v11.432','ENGINE · MAKER v11.433'),
        ('v11.432 · mobile camera orbit direction corrected','v11.433 · adjustable touch camera and easier gizmo grab'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.432'","window.SWRLZ_FORGE_BUILD={version:'v11.433'"),
        ('<title>§wyrl§ Engine · Maker v11.432</title>','<title>§wyrl§ Engine · Maker v11.433</title>'),
    ]:html=one(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.432';source.version=11.432;"
    assert html.count(old)==5,('v11.433 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.433';source.version=11.433;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.432' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.432','changes':notes.get('changes',[])})
    notes.update(version='v11.433',date='2026-11-12',title='Custom touch orbit and easier gizmo selection',changes=[
        'Model Studio Camera settings now includes Invert touch orbit. Switching applies immediately and is remembered on the device; default remains the current follow-finger direction.',
        'Move/Rotate/Scale gizmos have 56px mobile touch pick targets and easier near-axis grabbing, with only subtly larger visual grips and unchanged mouse and VR picking.',
        'Native selection priorities, pinch and pan, camera clipping, orthographic projection, project geometry, save schema and Undo remain unchanged.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+length:]
