"""§E v11.345: model-display VR modes and native multi-part UV atlas export/import."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def one(source,old,new,label=''):
 count=source.count(old)
 assert count==1,('v11.345 source mismatch',label,old[:110],count)
 return source.replace(old,new,1)
def apply(html):
 # Reuse the original model inspector UV tool and native geometry/UV data.
 old=(ROOT/'runtime/model_atelier_uv_layout_v11_336.js').read_text('utf8')
 additional=(ROOT/'runtime/model_atelier_multi_uv_atlas_v11_345.js').read_text('utf8')
 html=one(html,old,old+'\n'+additional,'existing UV inspector source')
 # The v11.336 single-mesh UI disabled every button within the whole section.
 # Scope its disable behavior to its own three buttons, not the atlas controls.
 html=one(html,
  "for (const button of root.querySelectorAll('button'))",
  "for (const button of root.querySelectorAll('.se336-uv-actions button'))",
  'original UV button ownership')
 ui_old=(ROOT/'runtime/model_studio_vr_ui_v11_344.js').read_text('utf8')
 ui_new=(ROOT/'runtime/model_studio_vr_ui_v11_345.js').read_text('utf8')
 html=one(html,ui_old,ui_new,'VR native palette')
 display=(ROOT/'runtime/model_vr_display_modes_v11_345.js').read_text('utf8')
 html=one(html,'function se344ReadAim(){',display+'\nfunction se344ReadAim(){','VR helper')
 html=one(html,
  "helpVisible:false,gesture:null,page:'tools',viewMode:'orbit',aimHand:'right',aim:null,",
  "helpVisible:false,gesture:null,page:'tools',viewMode:'orbit',aimHand:'right',aim:null,displayMode:'textured',displayOriginals:new Map(),displayMaterials:new Map(),",
  'VR state')
 html=one(html,'viewMode:se340XR.viewMode,page:se340XR.page,',
  'viewMode:se340XR.viewMode,page:se340XR.page,displayMode:se340XR.displayMode,',
  'VR inspector display state')
 html=one(html,'page:s.page,viewMode:s.viewMode,aimHand:s.aimHand,',
  'page:s.page,viewMode:s.viewMode,displayMode:s.displayMode,aimHand:s.aimHand,',
  'VR panel state')
 html=one(html,"if(action==='tools'||action==='views'||action==='aim'){",
  "if(action==='tools'||action==='views'||action==='aim'||action==='cameras'){",
  'VR view navigation')
 html=one(html,
  "if(action==='exit'){void se340ModelXRExit();return true;}",
  """if(action==='exit'){void se340ModelXRExit();return true;}
 if(action.startsWith('display-')){
  if(!se345SetDisplay(action.slice(8)))return false;
  se340SyncUI();se340Publish();return true;
 }""",'VR surface modes')
 html=one(html,
  "s.cachedEntries=bridge.projection().meshes;s.projectionRevision=native.revision;\n   se343DropHoverSurfaces();s.boxCache=new WeakMap();",
  "s.cachedEntries=bridge.projection().meshes;s.projectionRevision=native.revision;\n   se343DropHoverSurfaces();s.boxCache=new WeakMap();se345SyncDisplay();",
  'model-revision display sync')
 html=one(html,
  "try{se340Bridge()?.releaseRoot?.();}catch(error)",
  "se345RestoreDisplay();\n try{se340Bridge()?.releaseRoot?.();}catch(error)",
  'restore model materials before releasing borrowed root')
 html=one(html,
  "s.page='tools';s.viewMode='orbit';s.aimHand='right';s.aim=se344ReadAim();",
  "s.page='tools';s.viewMode='orbit';s.aimHand='right';s.aim=se344ReadAim();s.displayMode='textured';s.displayOriginals=new Map();s.displayMaterials=new Map();",
  'entry display default')
 css=(ROOT/'runtime/model_atelier_multi_uv_atlas_v11_345.css').read_text('utf8')
 assert html.index('</head>')<html.index('<body')
 html=html.replace('</head>','<style id="se345MultiUVAtlasStyle">\n'+css+'\n</style>\n</head>',1)
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_344_MODEL_VR_AIM_VIEWS_TRIGGER','SWYRL_ENGINE_DEPLOY_MARKER: V11_345_MODEL_MULTI_UV_VR_DISPLAY'),
  ('ENGINE · MAKER v11.344','ENGINE · MAKER v11.345'),
  ('v11.344 · calibrated controller rays, perspective views, responsive clicks',
   'v11.345 · VR wireframe modes and linked multi-object UV atlas'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.344'","window.SWRLZ_FORGE_BUILD={version:'v11.345'"),
  ('<title>§wyrl§ Engine · Maker v11.344</title>','<title>§wyrl§ Engine · Maker v11.345</title>'),
 ]:html=one(html,before,after,'release version')
 old=" source.engine='§wyrl§ Engine · Maker v11.344';source.version=11.344;"
 assert html.count(old)==3
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.345';source.version=11.345;")
 key='const SE_RELEASE_NOTES=';i=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[i:])
 if not any(x.get('version')=='v11.344' for x in notes.get('history',[])):
  notes.setdefault('history',[]).insert(0,{'version':'v11.344','changes':notes.get('changes',[])})
 notes.update(version='v11.345',date='2026-11-08',
  title='Model VR display modes and character-scale linked UV atlas',
  changes=[
   'Model Studio VR Views now changes the actual model render: Textured, Solid, Wireframe, X-ray and Normals; model angle presets remain in a separate Angles page. Native materials are restored when VR ends.',
   'The existing UV Layout inspector gains Select All, per-group and multi-object selection. A 2048/4096 transparent atlas guide exports real mesh UV wireframes with numbered part labels and a companion precise JSON mapping.',
   'The linked atlas preview selects exact corresponding native 3D parts by tile; users can load the mapping JSON and import a painted atlas back into the original UVs in one validated Undo transaction.',
   'UVs, topology and normal materials remain unchanged. Existing overlaps within a part are reported as source-authored rather than silently projected or claimed automatically unwrapped.'
  ])
 return html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[i+n:]
