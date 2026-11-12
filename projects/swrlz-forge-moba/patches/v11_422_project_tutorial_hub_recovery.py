"""§E v11.422: restore and retain the native Projects → Tutorials tab.

The old one-shot tutorial installer silently returned if the se170 account
project tabs were not mounted. Keep a single Projects dialog and restore all
three tabs when the dialog is constructed or reopened. Preserve starter
cards, account project references, tutorial model data and native saves.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_422_PROJECT_TUTORIAL_HUB_RECOVERY'

def one(s,old,new):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.422 anchor',old[:120],count))
    return s.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/project_tutorial_hub_recovery_v11_422.js').read_text('utf8')
    css=(ROOT/'runtime/project_tutorial_hub_recovery_v11_422.css').read_text('utf8')
    assert 'function se170Install(){' in html
    assert '/* §E v11.412: apprentice satchel' in html
    assert 'SE421_MODEL_VR_MENU_STABILITY_START' in html
    a=html.index(' function installLibrary(){',html.index('/* §E v11.412: apprentice satchel'))
    b=html.index(' window.SWYRL_ENGINE_TUTORIAL_412=Object.freeze(',a)
    old=html[a:b]
    for required in ['const tab=button(', 'function schedule(){installLibrary()', 'document.addEventListener(']:
        assert required in old,('v11.422 original tutorial hub missing',required)
    assert 'SE422_PROJECT_TUTORIAL_HUB_RECOVERY_START' not in html
    html=html[:a]+js+'\n'+html[b:]
    assert js.count('function installLibrary(){')==1
    assert html[a:a+len(js)+1].count('function installLibrary(){')==1
    assert 'SWYRL_ENGINE_PROJECT_TUTORIAL_HUB_422' in html[a:a+len(js)+1]
    assert html.index('</head>')<html.index('<body')
    html=html.replace('</head>','<style id="se422ProjectTutorialTabs">'+css+'</style>\n</head>',1)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_421_VR_TUTORIAL_MENU_INTERACTION',MARKER),
      ('ENGINE · MAKER v11.421','ENGINE · MAKER v11.422'),
      ('v11.421 · reliable and readable Model VR tutorial menus','v11.422 · restore the Projects tutorial tab'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.421'","window.SWRLZ_FORGE_BUILD={version:'v11.422'"),
      ('<title>§wyrl§ Engine · Maker v11.421</title>','<title>§wyrl§ Engine · Maker v11.422</title>')
    ]:html=one(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.421';source.version=11.421;"
    assert html.count(old)==5,('v11.422 source provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.422';source.version=11.422;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,{'version':'v11.421','changes':notes.get('changes',[])})
    notes.update(version='v11.422',date='2026-11-11',title='Projects: preserve Starter / My Projects / Tutorials',
      changes=[
       'Restore the Projects → Tutorials tab when the native Starter Projects/My Projects hub initializes late or its DOM is reconstructed; never require the user to reset model projects.',
       'Integrate Tutorials into the native se170 Projects tab selector: selecting Starter or My Projects hides the tutorial pane, and selecting Tutorials hides the other panes.',
       'Observe only the existing project hub for a missing tab/pane and perform an idempotent recovery, without replacing the starter cards or cloud project list.',
       'Keep all three native tabs visible in one compact, responsive tab row on Moto/Quest screens, with keyboard roles and accessible selected state.',
       'Expose read-only tutorial hub diagnostics and a manual repair action. Preserve the Apprentice Satchel quest, all saves, native VR tool menu and Sheep Tag.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
