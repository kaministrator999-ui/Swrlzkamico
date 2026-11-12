"""§E v11.420 — stable Sheep Tag VR teammate-count menu controls.

Keep the same Quest native controller-ray/trigger radial used on the main menu.
The old setup page destroyed and recreated all clickable meshes on every +/-
press, and offered a non-actionable count wedge. Keep targets stable and render
the chosen count in the heading, with only genuine actions as buttons.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_420_SHEEP_SETUP_MENU_CONTROLS'
def one(src,old,new):
    count=src.count(old)
    if count!=1:raise AssertionError(('v11.420',old[:130],count))
    return src.replace(old,new,1)
def apply(html):
    js=(ROOT/'runtime/sheep_setup_menu_controls_v11_420.js').read_text('utf8')
    for required in ('function se420SyncFlockMenu(){',
                     'window.SWYRL_ENGINE_SHEEP_SETUP_MENU_420',
                     'se420PreviousAction=se195HandleAction'):
        assert required in js,required
    for required in ('SWYRL_ENGINE_SHEEP_TEAM_SETUP_416',
                     'SE419_SHEEP_CONGESTION_BUDGET_START',
                     'function se195MakeRadial(reposition=true){'):
        assert required in html,required
    html=one(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_419_SHEEP_CONGESTION_BUDGET',MARKER),
      ('ENGINE · MAKER v11.419','ENGINE · MAKER v11.420'),
      ('v11.419 · bounded Sheep Tag congestion','v11.420 · consistent Sheep Tag VR setup controls'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.419'","window.SWRLZ_FORGE_BUILD={version:'v11.420'"),
      ('<title>§wyrl§ Engine · Maker v11.419</title>','<title>§wyrl§ Engine · Maker v11.420</title>')
    ]:html=one(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.419';source.version=11.419;"
    assert html.count(old)==5,('v11.420 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.420';source.version=11.420;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,{'version':'v11.419','changes':notes.get('changes',[])})
    notes.update(version='v11.420',date='2026-11-11',
      title='Sheep Tag VR AI-count setup uses original Quest radial controls',
      changes=[
       'The AI teammate-count page now uses the exact same existing Quest controller-ray and trigger selection pathway as the Sheep Tag main menu.',
       'Plus/minus changes update small button and count-heading textures in place without moving or reconstructing the hit meshes while the ray is hovering.',
       'Replace the nonfunctional fake count button with a real No AI Sheep choice; distinguish minimum and maximum choices and keep Start Match/Cancel actionable.',
       'Preserve desktop and touch match dialog, the v11.419 congestion budget, selected solo roster, LAN authority and other VR tools.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
