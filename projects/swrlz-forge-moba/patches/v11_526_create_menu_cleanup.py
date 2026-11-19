"""§E v11.526 — focused immersive Create UI, existing shape/action engines only.
Four native primitives, then a visible physical divider and Hip Pouch; contextual
accessory settings, but no duplicated primitives or Create navigation controls.
"""
import json
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_526_CREATE_MENU_CLEANUP'
def one(s,old,new,reason):
 count=s.count(old)
 if count!=1:raise AssertionError(('v11.526',reason,count,old[:130]))
 return s.replace(old,new,1)
def section(s,start,end,transform):
 a=s.index(start);b=s.index(end,a+len(start))
 return s[:a]+transform(s[a:b])+s[b:]
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_525_DISPLAY_MENU_GROUPS' in html
 def stage(s):
  s=one(s,
   "'create-menu':[['create-box','Cube'],['create-sphere','Sphere'],['create-cylinder','Cylinder'],['create-cone','Cone'],['create-pouch','Hip pouch'],['draw','Draw outline'],['duplicate','Duplicate']],",
   "'create-menu':[['create-box','Cube'],['create-sphere','Sphere'],['create-cylinder','Cylinder'],['create-cone','Cone'],['create-pouch','Hip Pouch']],",
   'five distinct Create actions, no Draw or Duplicate')
  s=one(s,
   "  const closeDetail=paintMesh(details,'Close modifier settings',",
   """  // SE526_CREATE_DIVIDER: real, non-interactive spatial separator between
  // four primitive choices and the independent pouch creation workflow.
  const createDivider=paintMesh(submenu,'Create · primitives / accessories separator',
   .200,.006,0,.095,(c,w,h)=>{
    c.fillStyle='#6d909d';c.fillRect(0,0,w,h);
    c.fillStyle='#b2ebe0';c.fillRect(0,0,w,Math.max(1,h*.28));
   },.052);
  createDivider.mesh.userData.se340Block=true;
  createDivider.mesh.visible=false;createDivider.paint();
  const closeDetail=paintMesh(details,'Close modifier settings',""",
   'visible separator in existing 3D middle panel')
  s=one(s,
   "item.mesh.position.y=category==='views'&&i===1?.212:.280-i*.049;",
   "item.mesh.position.y=category==='views'&&i===1?.212:category==='create-menu'&&i>=4?.280-i*.049-.027:.280-i*.049;",
   'space pouch below the physical divider, preserve all other row positions')
  s=one(s,
   "displayDivider.mesh.visible=category==='views'&&submenuOpen;",
   "displayDivider.mesh.visible=category==='views'&&submenuOpen;\n   createDivider.mesh.visible=category==='create-menu'&&submenuOpen;",
   'show Create divider only on Create page')
  s=one(s,
   "   if(action.startsWith('create-')||action==='duplicate')return 'create';",
   "   if(action==='create-pouch')return 'accessory';\n   if(action.startsWith('create-')||action==='duplicate')return 'create';",
   'pouch opens its real accessory editing panel')
  s=one(s,
   "detailPage=choosePage(item.action);detailsOpen=category==='inspect'?item.action==='selector-lasso':true;",
   "detailPage=choosePage(item.action);detailsOpen=category==='inspect'?item.action==='selector-lasso':category==='create-menu'?item.action==='create-pouch':true;",
   'primitive selection keeps panel closed; hip pouch opens contextual controls')
  return s
 html=section(html,'/* SE445_VR_PROGRESSIVE_TOOLS_START',
              '/* SE445_VR_PROGRESSIVE_TOOLS_END',stage)
 def native(s):
  i=s.index('  create:[\n');j=s.index('\n  \'accessory-body\':',i)
  s=s[:i]+"""  // SE526_CREATE_CONTEXT: primitives use their actual tracked ghost/trigger
  // controls. Pouch customization is the only Create settings page.
  create:[],
  accessory:[
   ['accessory-body','Body Shape'],['accessory-details','Flap & Details'],
   ['accessory-fit','Fit & Attach'],['accessory-material','Leather'],
   ['accessory-stitches','Stitching'],['accessory-emblem','Emblem'],
   ['accessory-reset','Reset Shape']
  ],"""+s[j:]
  s=one(s,
   "create:['Create a model','CHOOSE · PREVIEW · PLACE']",
   "create:['Create a model','CONTROLLER PREVIEW · TRIGGER TO PLACE · B TO CANCEL']",
   'primitive contextual status and unchanged placement')
  return s
 html=section(html,'/* SE360_MODEL_VR_UI_START',
              '/* SE360_MODEL_VR_UI_END',native)
 for a,z in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_525_DISPLAY_MENU_GROUPS',MARKER),
  ('ENGINE · MAKER v11.525','ENGINE · MAKER v11.526'),
  ('v11.525 · Display groups with visible angle/render divider',
   'v11.526 · five Create choices with primitive/accessory separator'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.525'","window.SWRLZ_FORGE_BUILD={version:'v11.526'"),
  ('<title>§wyrl§ Engine · Maker v11.525</title>',
   '<title>§wyrl§ Engine · Maker v11.526</title>')
 ):
  html=one(html,a,z,'release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.525';source.version=11.525;"
 if html.count(old)!=5:raise AssertionError(('source provenance',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.526';source.version=11.526;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.525']
 notes['history'].insert(0,{'version':'v11.525','changes':notes.get('changes',[])})
 notes.update(version='v11.526',date='2026-11-19',
  title='Immersive Create primitives, accessories and visible separator',
  changes=[
   'Modeling Lab → Create contains exactly Cube, Sphere, Cylinder, Cone and Hip Pouch. Draw Outline remains in Draw and Duplicate remains in Objects.',
   'A visible, non-interactive 3D separator and extra gap divide the four primitive shapes from Hip Pouch, without introducing new menu groups or replacing the native three-stage menu.',
   'Primitive choices use the existing ghost-preview, size control, Trigger confirm and B cancel; no duplicated primitive buttons or unnecessary third-stage Create controls appear.',
   'Hip Pouch opens the existing accessory customization panel for Body Shape, Flap & Details, Fit & Attach, Leather, Stitching, Emblem and Reset Shape; accessory subpanels remain functional.',
   'Creation is committed only on confirmation, preserving native edit journal/Undo, project history, native VR controllers, Select, Sculpt, Display and Face Tools. Quest acceptance pending.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
