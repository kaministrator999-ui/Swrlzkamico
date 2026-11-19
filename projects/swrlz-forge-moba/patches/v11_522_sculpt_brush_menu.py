"""§E v11.522 — immersive Sculpt is six surface brushes only.
Retain native Sculpt radius/strength controls in the third-stage inspector;
topology operations remain in the existing Face Tools category.
Append-only patch; no duplicate XR menu, tool dispatcher or model authority.
"""
import json

MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_522_SCULPT_BRUSH_MENU'

def one(source,old,new,description):
 count=source.count(old)
 if count!=1:
  raise AssertionError(('v11.522',description,count,old[:100]))
 return source.replace(old,new,1)

def section(source,begin,end,transform):
 a=source.index(begin)
 b=source.index(end,a+len(begin))
 return source[:a]+transform(source[a:b])+source[b:]

def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_521_LABS_PROJECT_JOURNAL' in html

 def sculpt_operations(block):
  start=block.index('   sculpt:[')
  end=block.index("\n   'manual-mesh':",start)
  assert block.count('   sculpt:[')==1
  # Preserve all other categories; only substitute Sculpt's operation entries.
  replacement=(
   "   // SE522_SCULPT_BRUSH_MENU: primary shaping -> detail refinement;\n"
   "   // topology remains exclusively in Face Tools.\n"
   "   sculpt:[['sculpt-push','Push'],['sculpt-translate','Translate'],"
   "['sculpt-inflate','Inflate'],['sculpt-pinch','Pinch'],"
   "['sculpt-flatten','Flatten'],['sculpt-smooth','Smooth']],")
  block=block[:start]+replacement+block[end:]
  assert "   'manual-mesh':[['manual-convert','Make editable']" in block
  assert "['manual-inset','Inset']" in block and "['manual-extrude','Extrude']" in block
  return block
 html=section(html,'/* SE445_VR_PROGRESSIVE_TOOLS_START',
              '/* SE445_VR_PROGRESSIVE_TOOLS_END',sculpt_operations)

 def sculpt_settings(block):
  start=block.index('  sculpt:[')
  end=block.index("\n  create:[",start)
  assert block.count('  sculpt:[')==1
  replacement=(
   "  // SE522_SCULPT_SETTINGS: the operation rail owns the six brush choices.\n"
   "  sculpt:[\n"
   "    ['brush-radius-minus','Radius −'],['brush-radius-plus','Radius +'],\n"
   "    ['brush-strength-minus','Strength −'],['brush-strength-plus','Strength +'],\n"
   "    ['studio','Studio'],['exit','Exit VR']\n"
   "   ],")
  return block[:start]+replacement+block[end:]
 html=section(html,'/* SE360_MODEL_VR_UI_START',
              '/* SE360_MODEL_VR_UI_END',sculpt_settings)

 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_521_LABS_PROJECT_JOURNAL',MARKER),
  ('ENGINE · MAKER v11.521','ENGINE · MAKER v11.522'),
  ('v11.521 · native labs, clean VR tool rail and persistent project edit journal',
   'v11.522 · focused immersive Sculpt brushes and dedicated brush settings'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.521'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.522'"),
  ('<title>§wyrl§ Engine · Maker v11.521</title>',
   '<title>§wyrl§ Engine · Maker v11.522</title>'),
 ):
  html=one(html,old,new,'release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.521';source.version=11.521;"
 count=html.count(old)
 if count!=5:raise AssertionError(('v11.522 source provenance',count))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.522';source.version=11.522;")
 tag='const SE_RELEASE_NOTES='
 at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.521']
 notes['history'].insert(0,{'version':'v11.521','changes':notes.get('changes',[])})
 notes.update(version='v11.522',date='2026-11-19',
  title='Immersive Sculpt brush organization',
  changes=[
   'Immersive Modeling Lab Sculpt operation menu has six surface tools in modeling order: Push, Translate, Inflate, Pinch, Flatten, Smooth.',
   'Sculpt settings use the existing native modifier panel for brush Radius −/+, Strength −/+; brush choices are not duplicated in the modifier panel.',
   'Inset, Extrude, Solidify, Subdivide and other mesh topology tools remain available through Face Tools instead of being repeated under Sculpt.',
   'Existing three-stage world-space menu, lab switching, project-scoped edit history, controller input, modeling tools and saved projects remain unchanged.',
   'Source and menu checks are automated; hands-on Quest acceptance remains pending.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
