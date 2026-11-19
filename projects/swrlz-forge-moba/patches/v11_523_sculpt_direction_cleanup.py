"""§E v11.523 — one signed Push/Pull brush, no duplicate native Exit VR."""
import json
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_523_SCULPT_DIRECTION_CLEANUP'
def one(s,a,b,why):
 n=s.count(a)
 if n!=1:raise AssertionError(('v11.523',why,n,a[:100]))
 return s.replace(a,b,1)
def section(s,a,b,fn):
 i=s.index(a);j=s.index(b,i+len(a))
 return s[:i]+fn(s[i:j])+s[j:]
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_522_SCULPT_BRUSH_MENU' in html
 def operations(s):
  s=one(s,"['sculpt-push','Push']","['sculpt-push','Push / Pull']",'axial brush label')
  return one(s,"   sculpt:[[","   // SE523_SCULPT_DIRECTION: six unique brushes.\n   sculpt:[[",'direction marker')
 html=section(html,'/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END',operations)
 def native(s):
  s=one(s,"['sculpt-indent','Indent']","['sculpt-direction','Pull Out']",'replace Indent button')
  n=s.count("['exit','Exit VR']")
  if n<2:raise AssertionError(('native Exit duplication',n))
  s=s.replace(",['exit','Exit VR']",'').replace("['exit','Exit VR'],",'').replace("['exit','Exit VR']",'')
  assert "['exit','Exit VR']" not in s
  s=one(s,"function label(item){\n  if(item.id==='sculpt-falloff')",
   "function label(item){\n  if(item.id==='sculpt-direction')return state.sculptDirection==='in'?'Push In':'Pull Out';\n  if(item.id==='sculpt-falloff')",'direction label')
  s=one(s,"function active(item){const id=item.id;\n  if(id==='index-add')",
   "function active(item){const id=item.id;\n  if(id==='sculpt-direction')return state.sculptDirection==='in';\n  if(id==='index-add')",'direction active')
  s=one(s,"function description(item){\n  if(item.id.startsWith('index-part-'))",
   "function description(item){\n  if(item.id==='sculpt-direction')return 'Push inward / pull outward along brush axis';\n  if(item.id.startsWith('index-part-'))",'direction hint')
  return s
 html=section(html,'/* SE360_MODEL_VR_UI_START','/* SE360_MODEL_VR_UI_END',native)
 for a,b,why in (
  ("const SE350_BRUSHES=['push','smooth','flatten','inflate','pinch','translate','indent'];",
   "const SE350_BRUSHES=['push','smooth','flatten','inflate','pinch','translate'];",'brush cycle'),
  ("Object.assign(se340XR,{sculptTool:'push',brushRadius:.12,brushStrength:.3,brushFalloff:'smooth',",
   "Object.assign(se340XR,{sculptTool:'push',brushRadius:.12,brushStrength:.3,brushFalloff:'smooth',sculptDirection:'out',",'direction init'),
  ("operation:s.sculptTool==='indent'?'push':s.sculptTool,radius:s.brushRadius,strength:s.sculptTool==='indent'?-Math.abs(s.brushStrength):s.brushStrength",
   "operation:s.sculptTool,radius:s.brushRadius,strength:s.sculptTool==='push'&&s.sculptDirection==='in'?-Math.abs(s.brushStrength):s.brushStrength",'stroke begin'),
  ("strength:se340XR.sculptTool==='indent'?-Math.abs(se340XR.brushStrength):se340XR.brushStrength,falloff:se340XR.brushFalloff",
   "strength:se340XR.sculptTool==='push'&&se340XR.sculptDirection==='in'?-Math.abs(se340XR.brushStrength):se340XR.brushStrength,falloff:se340XR.brushFalloff",'stroke update'),
  ("if(action==='sculpt-falloff'){",
   "if(action==='sculpt-direction'){se340CancelGesture();s.sculptDirection=s.sculptDirection==='in'?'out':'in';se340Notice('Push / Pull: '+(s.sculptDirection==='in'?'Push In':'Pull Out'));se340SyncUI();se340Publish();return true;}\n if(action==='sculpt-falloff'){",'direction action'),
  ("selectedCount:selectedIds.size,sculptTool:s.sculptTool,brushFalloff:s.brushFalloff,brushRadius:s.brushRadius",
   "selectedCount:selectedIds.size,sculptTool:s.sculptTool,sculptDirection:s.sculptDirection,brushFalloff:s.brushFalloff,brushRadius:s.brushRadius",'UI sync'),
  ("se340Notice('Sculpt '+s.sculptTool+' · release trigger to apply; left trigger smooths; B cancels.');",
   "se340Notice('Sculpt '+(s.sculptTool==='push'?(s.sculptDirection==='in'?'Push In':'Pull Out'):s.sculptTool)+' · release trigger to apply; left trigger smooths; B cancels.');",'stroke notice'),
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_522_SCULPT_BRUSH_MENU',MARKER,'marker'),
  ('ENGINE · MAKER v11.522','ENGINE · MAKER v11.523','header'),
  ('v11.522 · focused immersive Sculpt brushes and dedicated brush settings',
   'v11.523 · unified Push/Pull and no redundant Exit VR','subtitle'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.522'","window.SWRLZ_FORGE_BUILD={version:'v11.523'",'runtime'),
  ('<title>§wyrl§ Engine · Maker v11.522</title>','<title>§wyrl§ Engine · Maker v11.523</title>','title')
 ):
  html=one(html,a,b,why)
 old=" source.engine='§wyrl§ Engine · Maker v11.522';source.version=11.522;"
 if html.count(old)!=5:raise AssertionError(('provenance',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.523';source.version=11.523;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.522']
 notes['history'].insert(0,{'version':'v11.522','changes':notes.get('changes',[])})
 notes.update(version='v11.523',date='2026-11-19',title='Sculpt direction and menu redundancy cleanup',changes=[
  'Push/Pull shares one signed axial brush, with Push In or Pull Out selected in native Sculpt modifiers.',
  'Inflate stays distinct because vertex normals differ across curved geometry.',
  'Remove duplicate Indent including brush cycle; retain Radius, Strength and Falloff.',
  'Remove redundant Exit VR controls from all native settings; keep headset exit and engine cleanup.',
  'Native spatial menus, Face Tools, Labs, controller rays and model history retained. Quest acceptance pending.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
