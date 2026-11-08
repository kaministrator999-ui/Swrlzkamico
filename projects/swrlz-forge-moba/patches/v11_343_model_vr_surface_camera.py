"""§E v11.343 — smooth surface reticles and camera-relative thumbsticks."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def one(src,old,new):
 assert src.count(old)==1,('v11.343 anchor mismatch',old[:90],src.count(old))
 return src.replace(old,new,1)
def apply(html):
 # Hover surface helper remains isolated from native model and undo history.
 html=one(html,'function se340PartEntries(){',
  (ROOT/'runtime/model_vr_surface_pick_v11_343.js').read_text('utf8')+'\nfunction se340PartEntries(){')
 html=one(html,'boxCache:new WeakMap(),pickStats:',
  'boxCache:new WeakMap(),hoverSurfaceCache:new WeakMap(),hoverGeometries:new Set(),hoverSurfaceMaterial:null,pickStats:')
 hover_before=""" if(!precise){
  // Both controller rays only touch cheap world-space boxes while hovering.
  let candidate=null,nearest=cast.far;
  for(const entry of entries){
   const point=cast.ray.intersectBox(se340PartBox(entry.mesh),new THREE.Vector3());
   if(!point)continue;
   const distance=cast.ray.origin.distanceTo(point);
   if(distance>=cast.near&&distance<nearest){
    nearest=distance;candidate={id:entry.id,name:entry.name,mesh:entry.mesh,distance,point,proxy:true};
   }
  }
  return finish(candidate||{distance:1.2,point:cast.ray.at(1.2,new THREE.Vector3())});
 }"""
 hover_after=""" if(!precise){
  // Bounding boxes are broadphase only. The reticle hits a connected,
  // lightweight model surface (including current skin pose), not the box.
  let nearest=null;
  for(const entry of entries){
   if(!cast.ray.intersectsBox(se340PartBox(entry.mesh)))continue;
   const hit=se343HoverContact(entry,cast);
   if(hit&&(!nearest||hit.distance<nearest.distance))nearest=hit;
  }
  return finish(nearest||{distance:1.2,point:cast.ray.at(1.2,new THREE.Vector3())});
 }"""
 html=one(html,hover_before,hover_after)
 for old,new in [
  ('se340XR.frameEntries=null;if(result?.changed){se340XR.boxCache=new WeakMap();',
   'se340XR.frameEntries=null;if(result?.changed){se343DropHoverSurfaces();se340XR.boxCache=new WeakMap();'),
  ('se340XR.frameEntries=null;se340XR.cachedEntries=null;se340XR.projectionRevision=-1;se340XR.boxCache=new WeakMap();se340XR.lastAction',
   'se340XR.frameEntries=null;se340XR.cachedEntries=null;se340XR.projectionRevision=-1;se343DropHoverSurfaces();se340XR.boxCache=new WeakMap();se340XR.lastAction'),
  ('const result=se340Bridge()[action]();s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.boxCache=new WeakMap();',
   'const result=se340Bridge()[action]();s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;se343DropHoverSurfaces();s.boxCache=new WeakMap();'),
  ('s.cachedEntries=bridge.projection().meshes;s.projectionRevision=native.revision;\n   s.boxCache=new WeakMap();',
   's.cachedEntries=bridge.projection().meshes;s.projectionRevision=native.revision;\n   se343DropHoverSurfaces();s.boxCache=new WeakMap();'),
  ('s.documentToken=null;s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.pickMatrixFrame=-1;s.boxCache=new WeakMap();',
   's.documentToken=null;s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.pickMatrixFrame=-1;se343DropHoverSurfaces();s.hoverSurfaceMaterial=null;s.boxCache=new WeakMap();'),
  ('s.hoverId=null;s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.pickMatrixFrame=-1;s.boxCache=new WeakMap();s.pickStats=',
   's.hoverId=null;s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.pickMatrixFrame=-1;se343DropHoverSurfaces();s.boxCache=new WeakMap();s.pickStats='),
  ('se340XR.pan.x+dx*dt*.42*gain','se340XR.pan.x-dx*dt*.42*gain'),
  ('se340XR.pan.y-dy*dt*.42*gain','se340XR.pan.y+dy*dt*.42*gain'),
  ('se340XR.yaw-=dx*dt*1.35*gain','se340XR.yaw+=dx*dt*1.35*gain'),
  ('se340XR.pitch+dy*dt*1.05*gain','se340XR.pitch-dy*dt*1.05*gain'),
  ('// Smooth model-centred orbit; right stick pressed + vertical = optical zoom.',
   '// Camera-relative left pan and right orbit; right click+vertical preserves conventional zoom.'),
 ]:html=one(html,old,new)
 # Bake the first few surface proxies when VR opens, not on first pointer hit.
 html=one(html,'s.documentToken=se340Bridge().inspect().documentToken;',
 """s.documentToken=se340Bridge().inspect().documentToken;
 const initial=se340Bridge().projection();
 s.cachedEntries=initial.meshes;s.projectionRevision=initial.revision;
 for(const entry of initial.meshes.slice(0,4))
  if(entry.mesh?.visible!==false)se343SurfaceMesh(entry.mesh);""")
 for old,new in [
 ('SWYRL_ENGINE_DEPLOY_MARKER: V11_342_MODEL_VR_PROXY_PICKING','SWYRL_ENGINE_DEPLOY_MARKER: V11_343_MODEL_VR_SURFACE_CAMERA'),
 ('ENGINE · MAKER v11.342','ENGINE · MAKER v11.343'),
 ('v11.342 · coarse hover proxies and exact action picking','v11.343 · glove surface reticle and corrected camera orbit'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.342'","window.SWRLZ_FORGE_BUILD={version:'v11.343'"),
 ('<title>§wyrl§ Engine · Maker v11.342</title>','<title>§wyrl§ Engine · Maker v11.343</title>'),
 ]:html=one(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.342';source.version=11.342;"
 assert html.count(old)==3,('v11.343 runtime owner count',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.343';source.version=11.343;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,size=json.JSONDecoder().raw_decode(html[at:])
 if not any(x.get('version')=='v11.342' for x in notes.get('history',[])):
  notes.setdefault('history',[]).insert(0,{'version':'v11.342','changes':notes.get('changes',[])})
 notes.update(version='v11.343',title='Glove-surface targeting and camera-like stick controls',date='2026-11-08',changes=[
 'Idle pointer rays target a cached simplified continuous model surface instead of the rectangular broadphase bounds. The skinned glove proxy shares its live skeleton; exact trigger/grip selection still uses original geometry.',
 'Both joystick view axes reverse to camera-relative pan/orbit. Right thumbstick click plus vertical movement retains the same in/out zoom.',
 'Low-poly picking geometry is constructed on initial VR setup and invalidated on native model revision, selection and edit/undo; the editor saves no proxy geometry.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+size:]
