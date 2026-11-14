"""§E v11.442: regular-browser satchel with one native floating tutor."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_442_SATCHEL_MOBILE_DIALOG'
def one(s,old,new):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.442 anchor',old[:120],n))
 return s.replace(old,new,1)
def tutorial(s):
 start=s.index("   $('#se412Fold',panel).addEventListener('click'")
 end=s.index("   $('#se412Drag',panel).addEventListener('pointercancel',finish);",start)+len("   $('#se412Drag',panel).addEventListener('pointercancel',finish);")
 s=s[:start]+'   // SE442_NATIVE_DIALOG_INPUT: the independent dialog owns its header only.\n'+s[end:]
 s=one(s,'  if(panel.parentElement!==scene)scene.append(panel);\n  panel.hidden=false;display();',
  '  panel.hidden=false;display();\n  window.SWYRL_E_SATCHEL_DIALOG_442.mount(panel);')
 a=s.index("   const toolLink=button('Open relevant native tools',()=>{")
 b=s.index("   bar.after(toolLink);",a)
 s=s[:a]+"""   const toolLink=button('Open relevant native tools',()=>{
    const result=window.SWYRL_E_SATCHEL_FLAT_LESSON_442.openTools(current,{transform:current===0||current>=2&&current<=4});
    lessonNotice(result.message);
   },'se413-tool-link');
   toolLink.id='se442FlatTools';
"""+s[b:]
 s=one(s,"  $('#se412Tool',panel).textContent=step.tool;", "  $('#se412Tool',panel).textContent=step.tool;\n  const tools=panel.querySelector('#se442FlatTools');if(tools)tools.textContent=current===0||current>=2&&current<=4?'Size & position':'Open relevant native tools';")
 return s

def apply(html):
 assert 'SE441_QUEST_SIDE_PLACEMENT' in html and 'SE441_NATIVE_GHOST_ROOT' in html
 dialog=(ROOT/'runtime/model_satchel_dialog_v11_442.js').read_text()
 css=(ROOT/'runtime/model_satchel_dialog_v11_442.css').read_text()
 flat=(ROOT/'runtime/model_satchel_flat_lesson_v11_442.js').read_text()
 html=one(html,'/* SE441_SATCHEL_LESSON_END */','/* SE441_SATCHEL_LESSON_END */\n'+flat+'\n'+dialog)
 a=html.index('(function se412SatchelTutorial(){');b=html.index('/* SE413_SATCHEL_VR_QUEST_START',a)
 html=html[:a]+tutorial(html[a:b])+html[b:]
 # Keep the native Transform group after Assemblies insertion; identity gets
 # its own named group. Avoid array-position assumptions in curated tools.
 html=one(html," GROUPS.Meshes[2]=['Mesh identity',['Name','Kind']];", " if(!GROUPS.Meshes.some(row=>row[0]==='Mesh identity'))GROUPS.Meshes.splice(GROUPS.Meshes.findIndex(row=>row[0]==='Material & shape'),0,['Mesh identity',['Name','Kind']]); // SE442_TRANSFORM_DISCOVERY")
 # Three-decimal precision matches the native inspector's displayed values.
 # Retain native min/max, applyField validation, checkpoints and mesh guards.
 for kind in ['position','rotation','scale']:
  for axis in range(3):
   tail=(' min=".006"' if kind=='scale' else '')+' id="modelAtelier'+kind+str(axis)+'"'
   html=one(html,'step=".05"'+tail+'>','step=".001"'+tail+' aria-label="'+kind.title()+' '+['X','Y','Z'][axis]+(' (radians)' if kind=='rotation' else '')+'">')
 old="return {inset:{min:.03,max:.8,step:.05,value:.2,label:'Inset fraction · 0.2 = 20%'},extrude:{min:-4,max:4,step:.05,value:.15,label:'Depth · negative goes inward'},solidify:{min:.005,max:4,step:.025,value:.1,label:'Thickness · local units'},subdivide:{min:.025,max:4,step:.05,value:.25,label:'Target edge length · local units'}}[operation]||null;"
 html=one(html,old,old.replace('step:.05','step:.001').replace('step:.025','step:.001')+' // SE442_VALID_NUMERIC_PRECISION')
 html=one(html,'id="modelAtelierWorkshopAmount" type="number" min=".03" max=".8" step=".05"','id="modelAtelierWorkshopAmount" type="number" min=".03" max=".8" step=".001"')
 head=html.index('</head>');assert head<html.index('<body')
 html=html[:head]+'<style id="se442SatchelDialogStyles">\n'+css+'\n</style>\n'+html[head:]
 return identity(html)

def identity(html):
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_441_SATCHEL_VR_WORKFLOW',MARKER),
  ('ENGINE · MAKER v11.441','ENGINE · MAKER v11.442'),
  ('v11.441 · one connected satchel from real VR tools','v11.442 · a movable satchel tutor for mobile browsers'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.441'","window.SWRLZ_FORGE_BUILD={version:'v11.442'"),
  ('<title>§wyrl§ Engine · Maker v11.441</title>','<title>§wyrl§ Engine · Maker v11.442</title>')]:html=one(html,before,after)
 old=" source.engine='§wyrl§ Engine · Maker v11.441';source.version=11.441;";assert html.count(old)==5
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.442';source.version=11.442;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.441'];notes['history'].insert(0,{'version':'v11.441','changes':notes.get('changes',[])})
 notes.update(version='v11.442',date='2026-11-14',title='A movable satchel tutor for regular mobile browsers',changes=[
  'The existing Apprentice Satchel panel becomes its own non-modal dialog with touch/mouse dragging, collapse, minimize/reopen and position reset. Its local layout stays separate from model data.',
  'Mobile instructions teach the connected cube body, a thin flap, three manually placed strap sections and a small sphere clasp using actual native tools, numeric fields and materials.',
  'Transform has a named place in Meshes. Three-decimal numeric precision accepts the demonstrated dimensions and valid manual-tool defaults while retaining native bounds, previews and Undo.',
  'Show Me finds the actual current selection/view/operation/Apply controls. Construction objectives offer Size & position; final saving highlights the visible Model Studio Save button.',
  'The window remains reachable after orientation or viewport changes and clears the DOM during immersive VR. Existing world-space Quest windows, projects, seven objective IDs, checkpoints and source geometry authorities stay native.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
