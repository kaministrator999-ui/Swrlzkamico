"""§E v11.434 — crowded Sheep Tag VR stability and faithful editor rendering."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_434_SHEEP_CROWDED_VR'
def one(src,old,new):
 assert src.count(old)==1,('v11.434 source anchor',old[:110],src.count(old))
 return src.replace(old,new,1)
def apply(html):
 old='const occluded=st132GroundUnderDeck(unit,s)||st132CameraBlocked(unit,s);'
 html=one(html,old,'const occluded=se434XrayEligible(unit,s)&&(st132GroundUnderDeck(unit,s)||st132CameraBlocked(unit,s));')
 old="const cam=typeof perspectiveCamera!=='undefined'?perspectiveCamera:camera;\n cam.getWorldPosition(st132Eye);"
 html=one(html,old,"const cam=renderer.xr?.isPresenting?renderer.xr.getCamera(camera):(typeof perspectiveCamera!=='undefined'?perspectiveCamera:camera);\n cam.getWorldPosition(st132Eye);")
 code='\n'.join((ROOT/'runtime'/name).read_text('utf8') for name in ['sheep_visual_batch_v11_434.js','sheep_visible_frame_recovery_v11_434.js','sheep_xray_policy_v11_434.js','engine_editor_shadow_cache_v11_434.js'])
 html=one(html,'installPerformanceSettings();se189InstallPerfUI();',code+'\ninstallPerformanceSettings();se189InstallPerfUI();')
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_433_CAMERA_PREFERENCES_TOUCH_GIZMOS',MARKER),
  ('ENGINE · MAKER v11.433','ENGINE · MAKER v11.434'),
  ('v11.433 · adjustable touch camera and easier gizmo grab','v11.434 · crowded Sheep Tag VR and faithful rendering'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.433'","window.SWRLZ_FORGE_BUILD={version:'v11.434'"),
  ('<title>§wyrl§ Engine · Maker v11.433</title>','<title>§wyrl§ Engine · Maker v11.434</title>')]:html=one(html,before,after)
 old=" source.engine='§wyrl§ Engine · Maker v11.433';source.version=11.433;";assert html.count(old)==5
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.434';source.version=11.434;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,length=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.433']
 notes['history'].insert(0,{'version':'v11.433','changes':notes.get('changes',[])})
 notes.update(version='v11.434',date='2026-11-13',title='Crowded Sheep Tag VR with faithful graphics',changes=[
  'Crowded visible Sheep Tag frames no longer repeatedly masquerade as Meta-menu focus loss. Explicit WebXR visibility, browser hiding, input-release gates and genuine long-suspension recovery remain authoritative.',
  'Occluded-sheep feedback uses the cached native XR camera in VR. Busy Auto/Low/Medium scenes prioritize the controlled and selected sheep overlays; High retains the full teammate overlay set. The sheep models, normal visibility, minimap and gameplay rules remain native.',
  'Static scenery and authored editor buildings reuse compatible opaque native materials in fewer draw meshes, preserving triangles, normals, UVs, shadows and named animation pivots. Existing runtime-house batching remains the authority for match buildings.',
  'The shared scene editor reuses unchanged light-space shadow maps during camera movement. Actor, light, geometry, material, visibility and instance changes invalidate them; Play/Simulate and unsupported shadow materials stay on the native path.',
  'Preserves the latest saved touch-orbit preference and larger mobile gizmo targets. Physical Quest frame pacing, compositor behavior and thermal performance still require owner acceptance.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+length:]
