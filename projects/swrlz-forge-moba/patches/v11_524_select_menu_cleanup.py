"""§E v11.524 — one Select menu, one Lasso tool with Depth modifier.

Keep the real native 3-stage WebXR UI, reversible sweep, selection lasso,
project journal and controller gestures. No new selection implementation.
"""
import json

MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_524_SELECT_MENU_CLEANUP'

def one(s,old,new,description):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.524',description,n,old[:145]))
 return s.replace(old,new,1)

def section(s,begin,end,transform):
 a=s.index(begin);b=s.index(end,a+len(begin))
 return s[:a]+transform(s[a:b])+s[b:]

def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_523_SCULPT_DIRECTION_CLEANUP' in html

 def stage(block):
  block=one(block,
   "inspect:[['inspect','Select'],['selector-sweep','Sweep select'],['selector-lasso-front','Front lasso'],['selector-lasso-through','Through lasso'],['selection-clear','Clear selection'],['focus','Focus selection']],",
   "inspect:[['selector-sweep','Sweep'],['selector-lasso','Lasso'],['selection-clear','Clear Selection']],",
   'Select has exactly Sweep, Lasso, Clear')
  block=one(block,
   "objects:[['objects','Object index'],['index-add','Multi select'],['selection-clear','Clear selection'],['focus','Focus selection'],['duplicate','Duplicate']],",
   "objects:[['objects','Object index'],['index-add','Multi select'],['focus','Focus selection'],['duplicate','Duplicate']],",
   'clear selection lives under Select, Focus belongs to Objects')
  block=one(block,
   "   detailPage=choosePage(item.action);detailsOpen=true;",
   "   detailPage=choosePage(item.action);detailsOpen=category==='inspect'?item.action==='selector-lasso':true;",
   'only Lasso opens third-stage settings when Select category is active')
  return block
 html=section(html,'/* SE445_VR_PROGRESSIVE_TOOLS_START',
              '/* SE445_VR_PROGRESSIVE_TOOLS_END',stage)

 def panel(block):
  a=block.index('  selector:[')
  b=block.index('\n  projects:[',a)
  block=block[:a]+"""  // SE524_SELECT_LASSO_SETTINGS: operation choices live in native middle rail.
  selector:[
   ['selector-depth','Depth: Front']
  ],"""+block[b:]
  block=one(block,"function enabled(id){",
    "function enabled(id){\n  if(id==='selector-depth')return ['lasso-front','lasso-through'].includes(state.selectionMode);",
    'depth settings available only for Lasso')
  block=one(block,"function active(item){const id=item.id;",
    "function active(item){const id=item.id;\n  if(id==='selector-depth')return state.selectionMode==='lasso-through';",
    'depth state reflects through selection')
  block=one(block,"function label(item){",
    "function label(item){\n  if(item.id==='selector-depth')return state.selectionMode==='lasso-through'?'Depth: Through':'Depth: Front';",
    'native depth label follows current mode')
  block=one(block,"function description(item){",
    "function description(item){\n  if(item.id==='selector-depth')return state.selectionMode==='lasso-through'?'Select meshes at all depths inside the outline':'Select meshes in the nearest depth band';",
    'native depth description')
  block=one(block,"selector:['Selector','SWEEP · FRONT LASSO · THROUGH LASSO']",
    "selector:['Lasso settings','DEPTH · FRONT / THROUGH']",
    'third-stage modifier header, not duplicated brush options')
  return block
 html=section(html,'/* SE360_MODEL_VR_UI_START',
              '/* SE360_MODEL_VR_UI_END',panel)

 def interaction(block):
  block=one(block,
   """  if(action==='selector'){s.page='selector';s.se376SelectionMode||='sweep';}
  else if(['selector-sweep','selector-lasso-front','selector-lasso-through'].includes(action)){
   s.page='selector';s.se376SelectionMode=action.slice('selector-'.length);
  }else return false;
  if(s.gesture)se340CancelGesture('Selection mode changed · unfinished gesture canceled.');""",
   """  if(!['selector','selector-sweep','selector-lasso','selector-depth',
       'selector-lasso-front','selector-lasso-through'].includes(action))return false;
  if(s.gesture)se340CancelGesture('Selection mode changed · unfinished gesture canceled.');
  // A selection tool must never leave the previous Sculpt/Draw mode active.
  s.mode='inspect';s.page='selector';
  if(action==='selector'||action==='selector-sweep')s.se376SelectionMode='sweep';
  else if(action==='selector-lasso')s.se376SelectionMode=
   s.se376SelectionMode==='lasso-through'?'lasso-through':'lasso-front';
  else if(action==='selector-depth')s.se376SelectionMode=
   s.se376SelectionMode==='lasso-through'?'lasso-front':'lasso-through';
  else s.se376SelectionMode=action.slice('selector-'.length);""",
   'single Lasso action and preserved front/through implementation')
  return block
 html=section(html,'/* SE376_VR_SELECTOR_LASSO_START',
              '/* SE376_VR_SELECTOR_LASSO_END',interaction)

 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_523_SCULPT_DIRECTION_CLEANUP',MARKER),
  ('ENGINE · MAKER v11.523','ENGINE · MAKER v11.524'),
  ('v11.523 · unified Push/Pull and no redundant Exit VR',
   'v11.524 · concise Select menu with contextual Lasso depth'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.523'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.524'"),
  ('<title>§wyrl§ Engine · Maker v11.523</title>',
   '<title>§wyrl§ Engine · Maker v11.524</title>'),
 ):
  html=one(html,old,new,'release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.523';source.version=11.523;"
 if html.count(old)!=5:raise AssertionError(('source provenance',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.524';source.version=11.524;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.523']
 notes['history'].insert(0,{'version':'v11.523','changes':notes.get('changes',[])})
 notes.update(version='v11.524',date='2026-11-19',
  title='Immersive Select submenu and contextual Lasso depth',changes=[
   'Modeling Lab → Select now has Sweep, Lasso and Clear Selection, without a redundant Select action or duplicate Focus.',
   'Lasso uses one native operation with its Front/Through depth setting in the existing third-stage VR panel. Sweep and Clear do not open settings.',
   'Selecting Sweep or Lasso explicitly returns to Inspect/selection mode so earlier Sculpt and Draw gestures cannot remain armed.',
   'Sweep retains its reversible Left Trigger tracking; Lasso retains Left Grip drawing, front-depth filtering, through-depth capture, B cancellation and 32-mesh selection limit.',
   'Clear Selection has one logical home under Select, while Focus remains under Objects. Native scene, project journal, labs and VR menu architecture are untouched.',
   'Compiled source tests run automatically; hardware Quest acceptance remains pending.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
