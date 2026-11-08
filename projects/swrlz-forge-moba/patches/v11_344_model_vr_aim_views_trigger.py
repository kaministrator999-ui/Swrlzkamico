"""§E v11.344 · precise controller aim calibration, VR view presets, responsive clicks."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def one(src,old,new):
    count=src.count(old)
    assert count==1,('v11.344 source anchor',old[:110],count)
    return src.replace(old,new,1)
def apply(html):
    # Keep native history and original model geometry authoritative.
    for old,new in [
        ('runtime/model_vr_bridge_v11_340.js','runtime/model_vr_bridge_v11_344.js'),
        ('runtime/model_studio_vr_ui_v11_342.js','runtime/model_studio_vr_ui_v11_344.js'),
    ]:html=one(html,(ROOT/old).read_text('utf8'),(ROOT/new).read_text('utf8'))
    html=one(html,'function se340Cast(record){',
       (ROOT/'runtime/model_vr_aim_views_v11_344.js').read_text('utf8')+'\nfunction se340Cast(record){')
    html=one(html,"helpVisible:false,gesture:null,fit:1,zoom:1,yaw:0,pan:new THREE.Vector2(),",
       "helpVisible:false,gesture:null,page:'tools',viewMode:'orbit',aimHand:'right',aim:null,fit:1,zoom:1,yaw:0,pan:new THREE.Vector2(),")
    html=one(html,
       "['inspect','move','rotate','scale','undo','redo','focus','recenter','help','precision','snap','exit']",
       "['inspect','move','rotate','scale','undo','redo','focus','recenter','help','precision','snap','exit','views','tools','aim','view-front','view-back','view-left','view-right','view-top','view-bottom','view-iso','aim-hand','aim-yaw-minus','aim-yaw-plus','aim-pitch-minus','aim-pitch-plus','aim-reset','aim-reset-all']")
    html=one(html,
       "const direction=new THREE.Vector3(0,0,-1).transformDirection(record.target.matrixWorld).normalize();",
       """const correction=se344AimQuat(record);
 record.ray.quaternion.copy(correction);
 const direction=new THREE.Vector3(0,0,-1).applyQuaternion(correction)
  .transformDirection(record.target.matrixWorld).normalize();""")
    # One inexpensive connected surface hit replaces every-trigger native
    # SkinnedMesh.raycast (which CPU skins and intersects thousands of faces).
    html=one(html,'const hit=se340Hit(record);if(!hit?.id||hit.ui)return false;',
       'const hit=se340Hit(record,false);if(!hit?.id||hit.ui)return false;')
    html=one(html,
       'const hit=se340Hit(record);record.hit=hit;',
       'const triggerStarted=performance.now();const hit=se340Hit(record,false);record.hit=hit;')
    html=one(html,
       """if(hit?.id&&!se340XR.gesture){se340Bridge().select(hit.id);se340XR.frameEntries=null;se340XR.cachedEntries=null;se340XR.projectionRevision=-1;se343DropHoverSurfaces();se340XR.boxCache=new WeakMap();se340XR.lastAction='Selected '+hit.name;
  se340Notice(se340XR.lastAction);se340Pulse(record,.3,25);se340Publish();}""",
       """if(hit?.id&&!se340XR.gesture){
   const bridge=se340Bridge(),native=bridge.inspect(),different=native.selectedId!==hit.id;
   if(different){
    const result=bridge.select(hit.id);
    if(result?.ok===false){se340Notice(result.error||'Selection unavailable',true);return;}
    // Native selected parts can replace derived geometry; next frame validates.
    se340XR.frameEntries=null;se340XR.cachedEntries=null;se340XR.projectionRevision=-1;
    se343DropHoverSurfaces();se340XR.boxCache=new WeakMap();
   }
   se340XR.lastAction=(different?'Selected ':'Already selected ')+hit.name;
   se340Notice(se340XR.lastAction);se340Pulse(record,.3,25);se340Publish();
  }
  const duration=performance.now()-triggerStarted,stats=se340XR.pickStats;
  stats.lastTriggerMs=+duration.toFixed(2);
  stats.maxTriggerMs=Math.max(stats.maxTriggerMs||0,stats.lastTriggerMs);""")
    # Repeated grip on the same part now also bypasses bridge's native select
    # path; bridge_v11_344 contains the invariant-safe no-op.
    html=one(html,
       "s.yaw=Math.atan2(-forward.x,-forward.z);s.pitch=0;",
       "s.yaw=Math.atan2(-forward.x,-forward.z);s.pitch=0;s.viewMode='orbit';")
    html=one(html,
       "// Camera-relative left pan and right orbit; right click+vertical preserves conventional zoom.\n    se340XR.yaw+=",
       "// Camera-relative left pan and right orbit; right click+vertical preserves conventional zoom.\n    if(dx||dy&&!se340Pressed(record,3))se340XR.viewMode='orbit';\n    se340XR.yaw+=")
    html=one(html,
       "precision:s.precision,snap:s.snap,helpVisible:s.helpVisible,",
       """precision:s.precision,snap:s.snap,helpVisible:s.helpVisible,
   page:s.page,viewMode:s.viewMode,aimHand:s.aimHand,
   aimYaw:s.aim?.[s.aimHand]?.yaw||0,aimPitch:s.aim?.[s.aimHand]?.pitch||0,""")
    html=one(html,
       "if(action==='exit'){void se340ModelXRExit();return true;}",
       """if(action==='exit'){void se340ModelXRExit();return true;}
 if(action==='tools'||action==='views'||action==='aim'){
  s.page=action;s.helpVisible=false;
  se340Notice(action==='aim'?'Aim alignment · select hand and nudge yaw/pitch to match Meta pointer.':
   action==='views'?'Model perspectives · choose front, back, side, top, bottom or isometric.':'Model tools.');
  se340SyncUI();se340Publish();return true;
 }
 if(action.startsWith('view-')){
  if(!se344SetView(action.slice(5)))return false;
  se340SyncUI();se340Publish();return true;
 }
 if(action.startsWith('aim-')){
  if(!se344AimAction(action))return false;
  se340SyncUI();se340Publish();return true;
 }""")
    html=one(html,
       "s.session=requested;s.mode='inspect';s.precision=false;s.snap=false;s.paletteVisible=true;s.helpVisible=false;",
       """s.session=requested;s.mode='inspect';s.precision=false;s.snap=false;s.paletteVisible=true;s.helpVisible=false;
   s.page='tools';s.viewMode='orbit';s.aimHand='right';s.aim=se344ReadAim();""")
    html=one(html,
       "lastAction:se340XR.lastAction,error:se340XR.error,picking:{...se340XR.pickStats,hoverFaceRaycasts:0}",
       """lastAction:se340XR.lastAction,error:se340XR.error,
   viewMode:se340XR.viewMode,page:se340XR.page,
   aimCalibration:se340XR.aim?{left:{...se340XR.aim.left},right:{...se340XR.aim.right}}:null,
   picking:{...se340XR.pickStats,hoverFaceRaycasts:0}""")
    # Clear an action from the UI without losing ray calibration.
    html=one(html,
       "if(action==='palette'){s.paletteVisible=!s.paletteVisible;s.helpVisible=false;",
       "if(action==='palette'){s.paletteVisible=!s.paletteVisible;s.helpVisible=false;")
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_343_MODEL_VR_SURFACE_CAMERA','SWYRL_ENGINE_DEPLOY_MARKER: V11_344_MODEL_VR_AIM_VIEWS_TRIGGER'),
        ('ENGINE · MAKER v11.343','ENGINE · MAKER v11.344'),
        ('v11.343 · glove surface reticle and corrected camera orbit','v11.344 · calibrated controller rays, perspective views, responsive clicks'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.343'","window.SWRLZ_FORGE_BUILD={version:'v11.344'"),
        ('<title>§wyrl§ Engine · Maker v11.343</title>','<title>§wyrl§ Engine · Maker v11.344</title>'),
    ]:html=one(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.343';source.version=11.343;"
    assert html.count(old)==3
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.344';source.version=11.344;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.343' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.343','changes':notes.get('changes',[])})
    notes.update(version='v11.344',title='Controller alignment, model perspectives, faster VR trigger',date='2026-11-08',changes=[
        'Independent Quest controller yaw/pitch calibration, retained in the local browser, aligns both visible rays and their collision directions; the default uses WebXR targetRaySpace.',
        'Compact Model VR palette adds Front, Back, Left, Right, Top, Bottom and Isometric model views and a dedicated Aim menu without adding UI clutter or changing the headset stereo perspective.',
        'Trigger and Grip now use cached surface picking instead of full-resolution skinned raycasting, and repeated selection of the same native part skips costly rebuilds. Source/undo remains intact and trigger-time metrics are available.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
