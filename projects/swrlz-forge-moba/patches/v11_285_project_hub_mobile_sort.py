"""§E v11.285 — repair starter categories and compact overlay on small screens.
The previous sorter attempted to call a private function from a global scope,
which could abort the main script. Fix in the assembled source, preserving history.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def once(html,old,new,label):
    n=html.count(old)
    if n!=1: raise AssertionError(('v11.285',label,n,old[:120]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/starter_hub_mobile_v11_285.js').read_text('utf8')
    css=(ROOT/'runtime/starter_hub_mobile_v11_285.css').read_text('utf8')
    broken="""const se284PriorGroups=se236InstallStarterGroups;
se236InstallStarterGroups=function(){
 const result=se284PriorGroups.apply(this,arguments);
 se284SortStarterCards();
 return result;
};
"""
    html=once(html,broken,js+'\n','remove cross-scope se236 reference')
    html=once(html,'</head>','<style id="se285CompactProjectHub">\n'+css+'\n</style>\n</head>','compact modal CSS')
    before=" source.engine='§wyrl§ Engine · Maker v11.284';source.version=11.284;"
    n=html.count(before)
    if n!=3:raise AssertionError(('v11.285 provenance count',n))
    html=html.replace(before," source.engine='§wyrl§ Engine · Maker v11.285';source.version=11.285;")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_284_PLAIN_HAND_MODEL_CATEGORIES',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_285_PROJECT_HUB_MOBILE_SORT'),
      ('ENGINE · MAKER v11.284','ENGINE · MAKER v11.285'),
      ('v11.284 · plain anatomy hand and corrected starter models tabs',
       'v11.285 · compact project picker and reliable model tab sorting'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.284'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.285'"),
      ('<title>§wyrl§ Engine · Maker v11.284</title>',
       '<title>§wyrl§ Engine · Maker v11.285</title>')
    ]:html=once(html,old,new,'release metadata')
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Compact project picker, proper Starter Models and foreground Details stacking',
      date='2026-11-05',changes=[
      'Repair Starter Games / Starter Models sorting: the prior model sorter referenced a private Chat-host function from the global engine script, aborting before it could complete.',
      'Wait until native project group DOM exists, then reparent the actual starter cards and their default checkboxes to the correct tab without cloning.',
      'Keep playable game starters in Starter Games; put Plain Hand, Rocky Anime Hand, Arcane Gloves, sheep buildings and other model-only starters in Starter Models.',
      'Make project modal a compact centered scrolling sheet on phone and coarse-pointer desktop-site mode; the header and project categories remain accessible.',
      'Promote the active Projects dialog above right Details/left Outliner drawers, the Chat side panel and game overlays; restoring the editor when closed.',
      'Preserve model loaders, rigging, saved projects, account permissions, default choices, VR controls and gameplay. Owner phone/Quest visual acceptance pending.'])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
