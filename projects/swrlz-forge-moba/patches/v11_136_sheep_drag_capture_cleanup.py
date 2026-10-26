"""§E v11.136: same-camera sheep-origin drag and batched/deferred capture cleanup."""
from pathlib import Path
import json,hashlib

def once(html,old,new):
 n=html.count(old)
 assert n==1,(old[:150],n)
 return html.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_capture_drag_performance_v11_136.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 # Recompute both drag rays against the *current* camera. Storing the ray
 # from initial selection causes drift as camera follows a moving sheep.
 html=once(html,
  """ const here=stTouchPlacementOriginalGround(x,y);
 if(!here||!anchor.ground){
  stTouchPlacement.valid=false;
  stTouchPlacement.reason='Drag onto clear meadow ground.';
  return;
 }
 const target=new THREE.Vector3(
  anchor.origin.x+here.x-anchor.ground.x,0,
  anchor.origin.z+here.z-anchor.ground.z
 );
 target.y=terrainHeight(target.x,target.z);
 st135SetAimWorld(event,target);""",
  """ const target=st136StableAimTarget(anchor,x,y);
 if(!target){
  stTouchPlacement.valid=false;
  stTouchPlacement.reason='Drag onto clear meadow ground.';
  return;
 }
 st135SetAimWorld(event,target);""")
 # A sheep capture may destroy 28 houses in one tick. Keep every immediate
 # HP/collision/visual change, but invalidate navigation once per wave.
 html=once(html,
  "for(const b of s.buildings)if(b.owner===unit.id&&b.hp>0)stRemoveBuilding(b);",
  "st136RemoveCapturedBuildings(s,unit.id);")
 # GPU resource release is expensive on Android; detach each destroyed mesh
 # synchronously, then dispose at most two visuals per subsequent game tick.
 html=once(html,
  "else stDisposeVisual(building.mesh);stInvalidateNavigation();}",
  "else st136RetireBuildingVisual(building.mesh);stInvalidateNavigation();}")
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_135_SHEEP_ORIGIN_RELATIVE_DRAG_FREE_FORT_MIRROR',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_136_SHEEP_DRAG_CAMERA_CAPTURE_CLEANUP')
 for old,new in [
  ('ENGINE · MAKER v11.135','ENGINE · MAKER v11.136'),
  ('v11.135 · sheep-origin drag and sheep ability HUD','v11.136 · camera-stable sheep drag and capture cleanup'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.135'","window.SWRLZ_FORGE_BUILD={version:'v11.136'"),
  ('<title>§wyrl§ Engine · Maker v11.135</title>','<title>§wyrl§ Engine · Maker v11.136</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Camera-stable sheep building drag and smoother capture cleanup',
  date='2026-10-26',changes=[
  'Sheep building preview now computes both origin and finger ground rays from the same current follow camera, preserving the sheep-relative movement and avoiding drift when the camera follows the sheep during a drag. The native validator and commit remain authoritative.',
  'When one sheep is tagged, all their buildings still disappear from sight and collisions immediately. Repeated navigation invalidations are coalesced into one per capture group; heavy GPU geometry/material disposals are spread over frames and always flushed when exiting a match.',
  'Repeated pointer events on exactly the same validated snapped footprint now reuse the existing placement guide instead of reconstructing WebGL geometry, while changed snapped sites, blocked results or nav updates trigger redraw.',
  'Original sheep/Wolf balance, 7-minute round, capture/wisp rescue, Rapid, Free/Fort positions, Mirror/Totem, raised walkways, and all 68 assets remain untouched.',
  'The release is sealed by exact SHA and targeted tests. Source-level performance improvements still require owner Android frame-time/playfeel acceptance.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11136_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
