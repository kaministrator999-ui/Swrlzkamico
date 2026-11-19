"""§E v11.525 — tidy the existing immersive Display menu.
Two spatial operation groups with a real visible divider; retained 3-stage XR
menu, preview-only materials, preset camera poses and project lineage.
"""
import json
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_525_DISPLAY_MENU_GROUPS'
def one(s,old,new,why):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.525',why,n,old[:125]))
 return s.replace(old,new,1)
def section(s,start,end,fn):
 a=s.index(start);z=s.index(end,a+len(start))
 return s[:a]+fn(s[a:z])+s[z:]
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_524_SELECT_MENU_CLEANUP' in html

 def stage(s):
  s=one(s,
   "views:[['view-front','Front'],['view-back','Back'],['view-left','Left'],['view-right','Right'],['view-top','Top'],['view-bottom','Bottom'],['view-iso','Isometric'],['display-textured','Textured'],['display-wireframe','Wireframe'],['display-xray','X-ray'],['display-normals','Normals']],",
   "views:[['views-angles','View Angles'],['views-render','Render Modes']],",
   'replace mixed Display operations with two logical groups')
  s=one(s,
   "  const closeDetail=paintMesh(details,'Close modifier settings',",
   """  // SE525_DISPLAY_DIVIDER: actual world-space visual rule between
  // View Angles and Render Modes, not an interactive or duplicate option.
  const displayDivider=paintMesh(submenu,'Display · angles / render separator',
   .200,.006,0,.246,(c,w,h)=>{
    c.fillStyle='#6d909d';c.fillRect(0,0,w,h);
    c.fillStyle='#b2ebe0';c.fillRect(0,0,w,Math.max(1,h*.28));
   },.052);
  displayDivider.mesh.userData.se340Block=true;
  displayDivider.mesh.visible=false;displayDivider.paint();
  const closeDetail=paintMesh(details,'Close modifier settings',""",
   'add real visible separator to spatial submenu')
  s=one(s,
   "    item.mesh.userData.se340Action=item.action||null;item.mesh.visible=!!item.action;item.paint();",
   """    item.mesh.userData.se340Action=item.action||null;item.mesh.visible=!!item.action;
    // Allow a readable gap for the physical divider in Display only.
    item.mesh.position.y=category==='views'&&i===1?.212:.280-i*.049;
    item.paint();""",
   'space the grouped Display rows without moving other tools')
  s=one(s,
   "   subHead.paint();",
   "   displayDivider.mesh.visible=category==='views'&&submenuOpen;\n   subHead.paint();",
   'show separator only for Display')
  s=one(s,
   "   if(action.startsWith('view-')||action.startsWith('display-'))return 'views';",
   """   if(action==='views-angles')return 'cameras';
   if(action==='views-render')return 'views';
   if(action.startsWith('view-')||action.startsWith('display-'))return 'views';""",
   'route group selection to existing native angle / rendering pages')
  return s
 html=section(html,'/* SE445_VR_PROGRESSIVE_TOOLS_START',
              '/* SE445_VR_PROGRESSIVE_TOOLS_END',stage)

 def ui(s):
  a=s.index('  views:[\n');z=s.index('\n  aim:[',a)
  block="""  // SE525_DISPLAY_NATIVE_PANELS: only relevant settings; operation groups
  // themselves are in the middle spatial rail, not duplicated here.
  views:[
   ['display-textured','Textured'],['display-solid','Solid'],
   ['display-wireframe','Wireframe'],['display-xray','X-Ray'],
   ['display-normals','Normals']
  ],
  cameras:[
   ['view-front','Front'],['view-back','Back'],['view-left','Left'],
   ['view-right','Right'],['view-top','Top'],['view-bottom','Bottom'],
   ['view-iso','Isometric']
  ],"""
  s=s[:a]+block+s[z:]
  s=one(s,
    "views:['Model display','PREVIEW MATERIAL & STRUCTURE'],cameras:['Model angles','LOOK FROM EVERY SIDE']",
    "views:['Render modes','PREVIEW ONLY · ORIGINAL MATERIALS RETAINED'],cameras:['View angles','MODEL ORIENTATION · RIGHT STICK TO ORBIT']",
    'accurate native panel headings')
  return s
 html=section(html,'/* SE360_MODEL_VR_UI_START',
              '/* SE360_MODEL_VR_UI_END',ui)

 html=one(html,
  " if(action==='tools'||action==='views'||action==='aim'||action==='cameras'){",
  """ if(action==='views-angles'||action==='views-render'){
  s.page=action==='views-angles'?'cameras':'views';s.helpVisible=false;
  se340Notice(action==='views-angles'?'View Angles · choose a preset; right stick resumes orbit.':
   'Render Modes · preview geometry without changing saved model materials.');
  se340SyncUI();se340Publish();return true;
 }
 if(action==='tools'||action==='views'||action==='aim'||action==='cameras'){""",
  'group action dispatch selects existing XR settings pages')

 for a,z in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_524_SELECT_MENU_CLEANUP',MARKER),
  ('ENGINE · MAKER v11.524','ENGINE · MAKER v11.525'),
  ('v11.524 · concise Select menu with contextual Lasso depth',
   'v11.525 · Display groups with visible angle/render divider'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.524'","window.SWRLZ_FORGE_BUILD={version:'v11.525'"),
  ('<title>§wyrl§ Engine · Maker v11.524</title>',
   '<title>§wyrl§ Engine · Maker v11.525</title>'),
 ):
  html=one(html,a,z,'release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.524';source.version=11.524;"
 if html.count(old)!=5:raise AssertionError(('source provenance',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.525';source.version=11.525;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.524']
 notes['history'].insert(0,{'version':'v11.524','changes':notes.get('changes',[])})
 notes.update(version='v11.525',date='2026-11-19',
  title='Immersive Display grouped views, render modes and visible separator',
  changes=[
   'Permanent Display in the native far-right menu opens two middle-rail categories: View Angles and Render Modes, separated by a visible world-space divider and spacing.',
   'View Angles reuses the seven functional native front/back/left/right/top/bottom/isometric camera presets; Render Modes reuses textured, solid, wireframe, x-ray and normal preview materials.',
   'The third-stage settings shows only the selected group, eliminating Focus, Aim, Studio, Guide, Exit VR and repeated navigation from Display.',
   'Original model materials are retained and restored; display previews change runtime materials only, not saved project mesh or project edit journal.',
   'Original three-stage VR menu, controller ray hit testing, native camera orbit and sculpt/select labs preserved. Hardware Quest acceptance pending.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
