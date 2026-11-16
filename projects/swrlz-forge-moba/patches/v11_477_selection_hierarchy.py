"""§E v11.477: operation -> component type -> selection shape, with native vertex points."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_477_VERTEX_SELECTION_HIERARCHY'
def once(src,old,new):
 n=src.count(old)
 assert n==1,('se477 anchor',old[:125],n)
 return src.replace(old,new,1)
def segment(content,label):
 start=f'/* SE477_{label}_START */'
 end=f'/* SE477_{label}_END */'
 assert content.count(start)==content.count(end)==1
 return content.split(start,1)[1].split(end,1)[0].strip()+'\n'
def between(html,start,end,content):
 assert html.count(start)==1 and html.count(end)==1,(start,end,html.count(start),html.count(end))
 a=html.index(start);b=html.index(end,a+len(start))
 assert b>a
 return html[:a]+content+html[b:]
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_476_ACCOUNT_FIRST_WORKSPACE' in html
 native=(ROOT/'runtime/model_vertex_entry_v11_477.js').read_text('utf8')
 script=(ROOT/'runtime/model_progressive_hierarchy_v11_477.js').read_text('utf8')
 css=(ROOT/'runtime/model_progressive_hierarchy_v11_477.css').read_text('utf8')
 assert '/* SE477_VERTEX_ENTRY_END */' in native
 assert '/* SE477_SELECTION_HIERARCHY_STYLES_END */' in css
 # The ModelAtelier closure owns the THREE scene, topology and component
 # pointer callbacks. Inserting here preserves its original edit history.
 html=once(html,'/* SE430_MODEL_WORKSHOP_BRIDGE_END */',
           '/* SE430_MODEL_WORKSHOP_BRIDGE_END */\n'+native)
 # Replace only the v11.474 presentation controller's scoped functions.
 # Preserve the original family rail, click capture, settings and UI ownership.
 html=between(html,' function toolList(family){',' function renderFlyout(){',
              segment(script,'TOOL_LIST'))
 html=between(html,' function specificModes(){',' function selectFamily(family){',
              segment(script,'TOP_BARS'))
 html=between(html,' function chooseTool(name,kind){',' function nativeOperation(op){',
              segment(script,'CHOOSE_TOOL'))
 html=between(html,' function selectSpecific(mode){',' function mount(){',
              segment(script,'SPECIFIC_SELECTION'))
 html=once(html,
  "   state.family=family;state.tool='';state.toolType='';state.mode='';",
  "   state.family=family;state.tool='';state.toolType='';state.mode='';\n"+
  "   state.operation=false;state.selectionType='';state.shape='';\n"+
  "   state.panel.dataset.se477SelectionType='none';\n"+
  "   state.panel.dataset.se477SelectionShape='none';\n"+
  "   state.panel.dataset.se477Operation='false';")
 html=once(html,
  "  top.hidden=true;body.append(top);",
  "  top.hidden=true;body.append(top);\n"+
  "  const shapes=document.createElement('nav');shapes.id='se477SelectionShapes';\n"+
  "  shapes.className='se477-selection-shapes';\n"+
  "  shapes.setAttribute('aria-label','Selection shape for current operation');\n"+
  "  shapes.hidden=true;body.append(shapes);")
 html=once(html,
  "state={panel:p,rail,flyout,top,feedback:line,family:'',tool:'',toolType:'',mode:'',flyoutOpen:false,settings:false};",
  "state={panel:p,rail,flyout,top,shapeBar:shapes,feedback:line,"+
  "family:'',tool:'',toolType:'',mode:'',operation:false,selectionType:'',shape:'',flyoutOpen:false,settings:false};")
 html=once(html,
  "  p.dataset.se474Progressive='true';p.dataset.se474SettingsOpen='false';p.dataset.se474SpecificType='none';",
  "  p.dataset.se474Progressive='true';p.dataset.se474SettingsOpen='false';p.dataset.se474SpecificType='none';\n"+
  "  p.dataset.se477SelectionType='none';p.dataset.se477SelectionShape='none';p.dataset.se477Operation='false';")
 html=once(html,
  "  p.addEventListener('keydown',event=>{",
  "  shapes.addEventListener('pointerdown',event=>event.stopPropagation());\n"+
  "  shapes.addEventListener('click',event=>{\n"+
  "   const b=event.target.closest('button[data-se474-kind=\"shape\"]');\n"+
  "   if(b)selectShape(b.dataset.se474Value);\n"+
  "   event.stopPropagation();\n"+
  "  });\n"+
  "  p.addEventListener('keydown',event=>{")
 html=once(html,
  "   flyout:state.flyoutOpen,settings:state.settings},",
  "   flyout:state.flyoutOpen,settings:state.settings,\n"+
  "   selectionType:state.selectionType,shape:state.shape,operation:state.operation},")
 html=once(html,
  "  chooseMode:mode=>{if(state)selectSpecific(mode);}",
  "  chooseMode:mode=>{if(state)selectSpecific(mode);},\n"+
  "  chooseShape:shape=>{if(state)selectShape(shape);}")
 # Existing v11.475 mobile placement already follows the native transform bar.
 # Its second row now sits immediately BELOW the first, in the same viewport.
 html=once(html,
  "   top.style.setProperty('--se475-modes-width',number(width));",
  "   top.style.setProperty('--se475-modes-width',number(width));\n"+
  "   const shapeBar=panel.querySelector('#se477SelectionShapes');\n"+
  "   if(shapeBar){\n"+
  "    shapeBar.style.setProperty('--se477-shapes-x',number(x));\n"+
  "    shapeBar.style.setProperty('--se477-shapes-y',number(Math.min(y+55,Math.max(55,area.height-50))));\n"+
  "    shapeBar.style.setProperty('--se477-shapes-width',number(width));\n"+
  "   }")
 # Native selection cap + original persistent geometry are not changed.
 # Larger on-screen vertices improve touch recognition on Android.
 html=once(html,"    colors.vertex,5);",
  "    colors.vertex,typeof matchMedia==='function'&&matchMedia('(pointer:coarse)').matches?8:5);")
 assert '</head>' in html
 html=html.replace('</head>','<style id="se477SelectionHierarchyStyles">\n'+css+'\n</style>\n</head>',1)
 for old,new in [
   ('SWYRL_ENGINE_DEPLOY_MARKER: V11_476_ACCOUNT_FIRST_WORKSPACE',MARKER),
   ('ENGINE · MAKER v11.476','ENGINE · MAKER v11.477'),
   ('v11.476 · Google-first project restoration','v11.477 · selectable vertices and contextual modeling modes'),
   ("window.SWRLZ_FORGE_BUILD={version:'v11.476'","window.SWRLZ_FORGE_BUILD={version:'v11.477'"),
   ('<title>§wyrl§ Engine · Maker v11.476</title>','<title>§wyrl§ Engine · Maker v11.477</title>')
 ]:html=once(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.476';source.version=11.476;"
 assert html.count(old)==5,('se477 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.477';source.version=11.477;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[entry for entry in notes.get('history',[]) if entry.get('version')!='v11.476']
 notes['history'].insert(0,{'version':'v11.476','changes':notes.get('changes',[])})
 notes.update(version='v11.477',date='2026-11-16',
   title='Contextual modeling selection and visible native vertices',
   changes=[
    'Sculpt and Topology flyouts show operations such as Extrude and Inset rather than treating Vertex as a modeling operation.',
    'Selecting an operation defaults to Vertex and Single selection, revealing native model vertices; one active mesh is selected automatically, while multiple meshes can be selected by tapping their surface.',
    'Top selection bar chooses Vertex, Edge or Face; second horizontal bar provides Single Vertex, Vertex Ring or Filled Vertex Ring in vertex mode, Face/Region in face mode and native box/lasso in edge mode.',
    'Two independent horizontally scrollable mode bars appear beneath the existing transform toolbar without changing the inspector ownership.',
    'A valid topology center and connected ring are required for vertex Ring/Fill; topology-only boundary extrusion and native Face Inset/Extrude remain the actual geometry owners.',
    'No mesh duplication, UV changes or destructive topology conversion; Undo, VR controllers and local account/project login are preserved.',
    'Physical Moto touch and Quest acceptance still require user confirmation after automated browser checks.'
   ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
