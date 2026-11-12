"""§E v11.425: eliminate a real-device-blocking level-toolbar feedback loop.

The v11.423 observer reacted to toolbar reorders (rather than actual removal)
and queued se423RepairLevels(), which in turn moved existing controls and
refreshed select option nodes. That created hundreds of self-sustaining
MutationObserver/microtask cycles after the first authored scene load.

Preserve native level/project data and browser/VR tools. Only restore controls
that have become truly detached from the document; never contest valid layout
changes made by the editor.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_425_LEVEL_OBSERVER_FEEDBACK_GUARD'

def once(src,old,new):
 n=src.count(old)
 assert n==1,('v11.425 exact anchor',old[:115],n)
 return src.replace(old,new,1)

def apply(html):
 old=(ROOT/'runtime/level_selector_recovery_v11_423.js').read_text('utf8')
 assert old in html and html.count(old)==1
 js=old
 begin=js.index('seLevelsEnsureUI=function se423EnsureLevels(...args){')
 end=js.index('const se423PriorLevelsHydrate=',begin)
 safe="""/* SE425_LEVEL_UI_OBSERVER_GUARD
 * Run the native installer first. Reparent only nodes disconnected by a
 * real toolbar rebuild; never reshuffle existing attached controls.
 */
seLevelsEnsureUI=function se425EnsureLevels(...args){
 const result=se423PriorLevelsEnsure(...args);
 const play=$('playBtn'),stop=$('stopBtn'),viewport=$('viewport');
 if(play&&seLevels.bar&&!seLevels.bar.isConnected)play.before(seLevels.bar);
 if(stop&&seLevels.nextButton&&!seLevels.nextButton.isConnected)
  stop.after(seLevels.nextButton);
 if(viewport&&seLevels.preview&&!seLevels.preview.isConnected)
  viewport.appendChild(seLevels.preview);
 if(viewport?.parentElement&&seLevels.inspector&&!seLevels.inspector.isConnected)
  viewport.parentElement.appendChild(seLevels.inspector);
 return result;
};
"""
 js=js[:begin]+safe+js[end:]
 before="""function se423RepairLevels(){
 se423LevelRepairPending=false;
 if(!seLevels.records.size)return;
 seLevelsEnsureUI();
 se423PriorLevelsRefresh();
}"""
 after="""function se423RepairLevels(){
 se423LevelRepairPending=false;
 if(!seLevels.records.size)return;
 // If all native level controls are connected, editing/layout is already
 // authoritative. Never refresh dropdowns in response to harmless reorders.
 const detached=!seLevels.bar?.isConnected||!seLevels.nextButton?.isConnected||
   !seLevels.preview?.isConnected||!seLevels.inspector?.isConnected;
 if(!detached)return;
 seLevelsEnsureUI();
 se423PriorLevelsRefresh();
}"""
 js=once(js,before,after)
 before="""  if(seLevels.records.size&&currentPlay&&
    (!bar||bar.parentElement!==currentPlay.parentElement||bar.nextSibling!==currentPlay))
   se423ScheduleLevels();"""
 after="""  if(seLevels.records.size&&currentPlay&&(!bar||!bar.isConnected))
   se423ScheduleLevels();"""
 js=once(js,before,after)
 assert "bar.nextSibling!==play" not in js
 assert "bar.nextSibling!==currentPlay" not in js
 assert 'SE425_LEVEL_UI_OBSERVER_GUARD' in js
 html=once(html,old,js)
 for a,b in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_424_SHEEP_MENU_SCOPE_STARTUP',MARKER),
  ('ENGINE · MAKER v11.424','ENGINE · MAKER v11.425'),
  ('v11.424 · fix startup scope for Projects, levels and default scene',
   'v11.425 · stop level toolbar observer startup feedback'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.424'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.425'"),
  ('<title>§wyrl§ Engine · Maker v11.424</title>',
   '<title>§wyrl§ Engine · Maker v11.425</title>')]:
  html=once(html,a,b)
 provenance=" source.engine='§wyrl§ Engine · Maker v11.424';source.version=11.424;"
 assert html.count(provenance)==5
 html=html.replace(provenance," source.engine='§wyrl§ Engine · Maker v11.425';source.version=11.425;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.setdefault('history',[]).insert(0,{'version':'v11.424','changes':notes.get('changes',[])})
 notes.update(version='v11.425',date='2026-11-12',
  title='Restore responsive startup after level toolbar observer feedback',
  changes=[
   'Correct a real Chromium-reproduced event-loop stall: v11.423 level toolbar recovery contested legitimate UI positions and rebuilt controls on every observed mutation.',
   'Use the original native level installer first, restore level UI only after actual disconnection, and never force existing attached controls into a different order.',
   'Stop observer-triggered dropdown rebuilding for harmless toolbar changes while preserving saved level packs, names, Next Level links, and native editor placement.',
   'Preserve v11.424 Sheep Tag scope correction and the native Starter Projects / My Projects / Tutorials controls.',
   'Require real-browser startup acceptance with the 170-part Dragon Den, populated level selector and three Project tabs before publishing.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]

# Source-chain test entry: the 406-patch candidate requires live Chromium acceptance.
