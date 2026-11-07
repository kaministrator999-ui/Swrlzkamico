"""§E v11.320: navigable studio chrome and completed-load workspace routing."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_320_STUDIO_NAVIGATION_LAYOUT'
def once(s,old,new):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.320 anchor',old[:110],n))
 return s.replace(old,new,1)
def apply(html):
 css=(ROOT/'runtime/studio_editor_layout_v11_320.css').read_text('utf8')
 js='\n'.join((ROOT/'runtime'/name).read_text('utf8') for name in ['studio_project_routing_v11_320.js','studio_editor_layout_v11_320.js'])
 assert html.index('</head>')<html.index('<body')
 html=html.replace('</head>','<style id="se320StudioNavigation">\n'+css+'\n</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,"document.querySelector('.app>.topbar>.se187-game-tabs');", "document.querySelector('.app .se187-game-tabs');")
 html=once(html,"document.querySelector('.app>.topbar>.se187-game-tabs .segui-mini');", "document.querySelector('.app .se187-game-tabs .segui-mini');")
 html=once(html,"if(topbar&&!topbar.querySelector('.se187-workspace-tabs'))", "if(topbar&&!document.querySelector('.app .se187-game-tabs'))")
 html=once(html,"function onNativeLoad(data){\n  if(data?.project?.kind==='model-atelier')preferScratch=false;", "function onNativeLoad(data){\n  if(Array.isArray(data?.scene?.actors))initializedGame=true;\n  if(data?.project?.kind==='model-atelier')preferScratch=false;")
 html=once(html,"     try{loadCanonicalGlitchDen();}catch(error){", "     try{if(!dirty&&currentProject?.kind!=='model-atelier'&&!currentProject?.particleStudio?.emitters?.length)loadCanonicalGlitchDen();}catch(error){")
 old=" source.engine='§wyrl§ Engine · Maker v11.309';source.version=11.309;"
 assert html.count(old)==3
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.320';source.version=11.320;")
 for old,new in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_309_ARCANE_NATIVE_RAY_AIM',MARKER),
  ('ENGINE · MAKER v11.309','ENGINE · MAKER v11.320'),
  ('v11.309 · native Arcane aim and complete VR ray hiding','v11.320 · organized studios and project-aware navigation'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.309'","window.SWRLZ_FORGE_BUILD={version:'v11.320'"),
  ('<title>§wyrl§ Engine · Maker v11.309</title>','<title>§wyrl§ Engine · Maker v11.320</title>')]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,width=json.JSONDecoder().raw_decode(html[at:])
 if not any(n.get('version')=='v11.309' for n in notes.get('history',[])):
  notes.setdefault('history',[]).insert(0,{'version':'v11.309','changes':notes.get('changes',[])})
 notes.update(version='v11.320',title='Clearer studios, tool docks and project navigation',date='2026-11-07',changes=[
  'Modeling tools now sit in their own rail to the left of the inspector. Collapsing the inspector gives that space back to the viewport; tool categories stay visible and reopen the inspector when chosen.',
  'Keep tool mode buttons inside the inspector, with readable category buttons and a dedicated Projects action. Compact layouts use a separate horizontally scrollable tool row above the inspector.',
  'Project Library keeps its header and Starter Projects / My Projects tabs separate from scrolling content. Starter Games, Models and Particles stay in their own content row without covering the saved-project tabs.',
  'Game Engine has separate studio, menu and quick-action rows, with advanced scene/build/VR controls grouped under More tools. Particle Studio has a dedicated studio-tab row, readable menus and separately scrolling actions.',
  'Completed native project loads switch to Modeling, Game Engine or the saved Particle workspace. Remember the chosen studio in new project exports; importing an emitter library opens Particle Studio. Switching after an explicit load preserves that loaded document instead of initializing a default game over it.',
  'Preserve existing native controls, shortcut handlers, authoring history, model and emitter data, Chat account storage, and the v11.309 Vanguard geometry/UV rebuild. Desktop and compact browser checks are separate from owner device acceptance.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
