"""§E v11.418 — append solo Sheep Tag flock choice after the v11.417 VR Object Index."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_418_SHEEP_FLOCK_SETUP'

def one(s,old,new):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.418 anchor',old[:100],n))
    return s.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/sheep_team_setup_v11_416.js').read_text('utf8')
    css=(ROOT/'runtime/sheep_team_setup_v11_416.css').read_text('utf8')
    assert 'SWYRL_ENGINE_SHEEP_TEAM_SETUP_416' in js
    assert 'SWYRL_ENGINE_SHEEP_AI_FRAME_BUDGET_411' in html
    assert 'SWYRL_E_SATCHEL_ACADEMY_416' in html
    html=one(html,'if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(',
      js+'\nif(ALLOWED_PARENTS.has(location.origin))queueMicrotask(')
    assert '</head>' in html and html.index('</head>')<html.index('<body'), 'head insertion missing'
    html=html.replace('</head>','<style id="se416FlockSetupStyles">\n'+css+'\n</style>\n</head>',1)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_417_MODEL_VR_OBJECT_INDEX',MARKER),
      ('ENGINE · MAKER v11.417','ENGINE · MAKER v11.418'),
      ('v11.417 · VR Object Index & mesh highlights','v11.418 · Sheep Tag AI flock setup'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.417'","window.SWRLZ_FORGE_BUILD={version:'v11.418'"),
      ('<title>§wyrl§ Engine · Maker v11.417</title>','<title>§wyrl§ Engine · Maker v11.418</title>')
    ]:html=one(html,old,new)
    # Carry all five v11.417 source provenance labels forward intact.
    old=" source.engine='§wyrl§ Engine · Maker v11.417';source.version=11.417;"
    assert html.count(old)==5,('v11.418 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.418';source.version=11.418;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,{'version':'v11.417','changes':notes.get('changes',[])})
    notes.update(version='v11.418',date='2026-11-11',
      title='Sheep Tag: choose AI sheep teammates before playing',
      changes=[
       'Main Menu Start Game opens a keyboard/touch-friendly dialog to choose 0–5 authored sheep AI teammates in the starter map; edited maps expose available spawns up to 8.',
       'Quest VR Start opens the same choice through the existing controller radial menu, with plus/minus, count, confirm and cancel.',
       'The selected roster only affects the active solo match, never saved actors, wolf counts, LAN seats, or project exports; native Stop restores all authored spawns.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
