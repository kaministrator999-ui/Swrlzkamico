"""§E v11.424: correct Sheep Tag radial bridge lexical owner and recover app boot.

The v11.420 wrapper was injected at the global build marker even though
se416Show is owned by the nested Chat/Sheep setup closure. That synchronous
ReferenceError aborted the rest of the main editor initialization, leaving
project tabs, level data, and viewport empty. Relocate the exact original
runtime (do not remove Sheep Tag functionality), with no new state/store.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_424_SHEEP_MENU_SCOPE_STARTUP'

def one(html,old,new):
 count=html.count(old)
 assert count==1,('v11.424 anchor',old[:105],count)
 return html.replace(old,new,1)

def apply(html):
 js=(ROOT/'runtime/sheep_setup_menu_controls_v11_420.js').read_text('utf8')
 assert js.startswith('// §E v11.420')
 assert 'const se420PreviousShow=se416Show;' in js
 assert 'se195HandleAction=function(action,record)' in js
 assert 'SE423_LEVEL_SELECTOR_RECOVERY_START' in html
 assert html.index(js)<html.index('function se416Show(){')
 html=one(html,js,'/* SE424_SHEEP_BRIDGE_MOVED_FROM_GLOBAL_BUILD_MARKER */')
 # v11.418 placed the Sheep AI setup helpers in the native Chat-host lexical
 # closure just before this one-shot host mount. This is the *same* lexical
 # scope as se416Show, se416Count, se416Max, and se416SetCount.
 anchor='if(ALLOWED_PARENTS.has(location.origin))queueMicrotask('
 html=one(html,anchor,
  '/* SE424_SHEEP_MENU_SCOPE_START */\n'+js+'\n/* SE424_SHEEP_MENU_SCOPE_END */\n'+anchor)
 assert html.index('function se416Show(){')<html.index('/* SE424_SHEEP_MENU_SCOPE_START */')
 assert html.count('const se420PreviousShow=se416Show;')==1
 for old,new in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_423_PROJECT_LEVEL_MENU_RECOVERY',MARKER),
  ('ENGINE · MAKER v11.423','ENGINE · MAKER v11.424'),
  ('v11.423 · restore Projects tabs, touch scroll and editor levels',
   'v11.424 · fix startup scope for Projects, levels and default scene'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.423'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.424'"),
  ('<title>§wyrl§ Engine · Maker v11.423</title>',
   '<title>§wyrl§ Engine · Maker v11.424</title>')]:
  html=one(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.423';source.version=11.423;"
 assert html.count(old)==5
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.424';source.version=11.424;")
 at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.setdefault('history',[]).insert(0,{'version':'v11.423','changes':notes.get('changes',[])})
 notes.update(version='v11.424',date='2026-11-11',
 title='Restore full editor initialization: Projects, levels, and scene',
 changes=[
  'Fix a real Chromium-reproduced startup ReferenceError: se416Show was read in the v11.420 Sheep Tag VR menu wrapper outside the lexical scope that defines it.',
  'Relocate the existing v11.420 native radial bridge inside its proper Sheep Tag setup closure, retaining all AI sheep count controls and stable hover/trigger targets.',
  'Allow the normal startup sequence to initialize the native Starter/My Projects/Tutorials tabs, editor level bar, and default scene without resetting user projects.',
  'Verify in an actual browser with a mobile viewport, not only simulated DOM or JavaScript syntax checks.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
