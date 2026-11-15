"""§E v11.464 — five scoped viewport/inspector polish repairs."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_464_MODEL_VISUAL_INSPECTOR'
def one(html,old,new):
 count=html.count(old)
 if count!=1:raise AssertionError(('v11.464 source anchor drift',old[:140],count))
 return html.replace(old,new,1)
def apply(html):
 js=(ROOT/'runtime/model_visual_polish_v11_464.js').read_text('utf8')
 css=(ROOT/'runtime/model_visual_polish_v11_464.css').read_text('utf8')
 assert js.startswith('/* SE464_MODEL_VISUAL_POLISH_START */')
 assert js.strip().endswith('/* SE464_MODEL_VISUAL_POLISH_END */')
 assert css.startswith('/* SE464_INSPECTOR_VISUAL_POLISH_START */')
 # Extend the single original ModelAtelier closure: no second renderer/model.
 html=one(html,'/* SE462_MODEL_WIRE_CLARITY_END */',
  '/* SE462_MODEL_WIRE_CLARITY_END */\n'+js)
 html=html.replace('</head>',
  '<style id="se464ModelVisualPolishStyles">\n'+css+'\n</style>\n</head>',1)
 # In Solid/Flat/Clay, reduce self-illumination that masks cavity shading.
 html=one(html,
  '  emissive:color.clone().multiplyScalar(.09),\n  emissiveIntensity:.2',
  '  emissive:color.clone().multiplyScalar(.05),\n  emissiveIntensity:.1')
 # Native component overlay remains the selector/face-owner; we only improve
 # the on-screen color palette (including visible selected vertex/edge/face).
 html=one(html,
  'const colors={vertex:0x56e9e7,edge:0x69bbff,face:0xe3b6ff};',
  'const colors={vertex:0x74ffdb,edge:0x86d7ff,face:0xffd17e};')
 html=one(html,
  'const outline=new THREE.BoxHelper(mesh,0xf3cf86);',
  'const outline=new THREE.BoxHelper(mesh,0x8fffe3);')
 # Historical labels are preserved and the source schema remains unchanged.
 html=one(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_463_TRANSFORM_BAR_HISTORY',MARKER)
 html=one(html,'/* SE464_MODEL_VISUAL_POLISH_END */',
  '/* SE464_MODEL_VISUAL_POLISH_END */\n'
  '/* Historical v11.463 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_463_TRANSFORM_BAR_HISTORY */')
 for old,new in [
  ('ENGINE · MAKER v11.463','ENGINE · MAKER v11.464'),
  ('v11.463 · persistent transform history bar','v11.464 · modeling depth and inspector focus'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.463'","window.SWRLZ_FORGE_BUILD={version:'v11.464'"),
  ('<title>§wyrl§ Engine · Maker v11.463</title>','<title>§wyrl§ Engine · Maker v11.464</title>')
 ]:html=one(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.463';source.version=11.463;"
 assert html.count(old)==5,('v11.464 provenance count',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.464';source.version=11.464;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.463']
 notes['history'].insert(0,{'version':'v11.463','changes':notes.get('changes',[])})
 notes.update(version='v11.464',date='2026-11-15',
  title='Model Studio depth, X-Ray and mobile inspector polish',
  changes=[
   'Native Solid/Flat/Clay get reduced display-only emissive wash and two soft directional studio fill lights for visible inset walls and corners. Fill is disabled when the VR model bridge borrows the view.',
   'Material mode retains authored textures/PBR properties, with improved studio illumination and existing bounded planar hard-surface shading.',
   'X-Ray uses a lightweight neutral translucent front surface, a depth-only occlusion helper, dim behind-surface topology and strong depth-tested front edges. All view-only helpers and cloned materials are disposable and do not affect real topology or UVs.',
   'Mobile inspector has a reversible Expand/Dock focus state with readable full-width controls; expanding temporarily frees the dock track without altering stored splitter widths or native drag handlers.',
   'Selected native object and component geometry uses distinctive high-contrast box, vertex, edge and face colors with refreshed selection states. Undo/Redo toolbar, orbit camera, existing inset workflow and VR tools are preserved.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
