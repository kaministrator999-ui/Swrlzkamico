"""§E v11.423: restore native project tabs, touch scrolling and level chrome."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_423_PROJECT_LEVEL_MENU_RECOVERY'

def one(s,old,new):
 n=s.count(old)
 assert n==1,('v11.423 missing or duplicate anchor',old[:110],n)
 return s.replace(old,new,1)

def apply(html):
 projects=(ROOT/'runtime/project_menu_recovery_v11_423.js').read_text('utf8')
 levels=(ROOT/'runtime/level_selector_recovery_v11_423.js').read_text('utf8')
 css=(ROOT/'runtime/project_menu_scroll_v11_423.css').read_text('utf8')
 assert 'SE422_PROJECT_TUTORIAL_HUB_RECOVERY_START' in html
 assert 'function seLevelsEnsureUI(){' in html
 assert 'function se170Install(){' in html
 assert 'SE423_PROJECT_MENU_RECOVERY_START' not in html
 html=one(html,' window.SWYRL_ENGINE_TUTORIAL_412=Object.freeze(',
          projects+'\n window.SWYRL_ENGINE_TUTORIAL_412=Object.freeze(')
 html=one(html,"window.SWRLZ_FORGE_BUILD={version:'v11.422'",
          levels+"\nwindow.SWRLZ_FORGE_BUILD={version:'v11.422'")
 html=one(html,'</head>',
          '<style id="se423ProjectMenuScroll">'+css+'</style>\n</head>')
 for old,new in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_422_PROJECT_TUTORIAL_HUB_RECOVERY',MARKER),
  ('ENGINE · MAKER v11.422','ENGINE · MAKER v11.423'),
  ('v11.422 · restore the Projects tutorial tab','v11.423 · restore Projects tabs, touch scroll and editor levels'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.422'","window.SWRLZ_FORGE_BUILD={version:'v11.423'"),
  ('<title>§wyrl§ Engine · Maker v11.422</title>',
   '<title>§wyrl§ Engine · Maker v11.423</title>'),
 ]:html=one(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.422';source.version=11.422;"
 assert html.count(old)==5,('v11.423 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.423';source.version=11.423;")
 at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.setdefault('history',[]).insert(0,{'version':'v11.422','changes':notes.get('changes',[])})
 notes.update(version='v11.423',date='2026-11-11',
  title='Projects and game level controls recovered',
  changes=[
   'Recover missing native Starter Projects, My Projects and Tutorials tabs after partial dialog reconstruction; preserve account references and starter nodes.',
   'Restore finger scrolling of the existing Projects dialog on mobile and Quest; keep tab buttons in a single accessible three-column row.',
   'Reattach the original game-editor level selector and next-level control when editor chrome is rebuilt; preserve level maps and unsaved snapshots.',
   'Recover a saved level-pack root when an older level snapshot lacks its project-root marker; never replace or reset the saved level collection.',
   'Provide focused runtime diagnostics for Project hub and level controls, without adding a frame loop or changing Sheep Tag gameplay.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]

# Seal trigger: the native starter and level recovery are integrated after v11.422.
