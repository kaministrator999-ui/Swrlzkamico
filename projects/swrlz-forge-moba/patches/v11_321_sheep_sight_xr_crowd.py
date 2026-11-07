"""§E v11.321: sight-blocking houses, crowded-Quest AI budget and head-turn diagnosis."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_321_SHEEP_SIGHT_XR_CROWD'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.321',label,count,old[:115]))
    return html.replace(old,new,1)

def apply(html):
    for token in ('function stPerceivesDirect(observer,target){',
                  'function se306CachedApproach(wolf,sheep){',
                  'const se256AIBudget={frame:-1,used:0,perFrame:2',
                  'function se286Sample(start,at,version,prior){',
                  'SWYRL_ENGINE_DEPLOY_MARKER: V11_320_STUDIO_NAVIGATION_LAYOUT'):
        if token not in html:raise AssertionError(('v11.321 prerequisite',token))
    script=(ROOT/'runtime/sheep_sight_xr_crowd_v11_321.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',script+'\nwindow.SWRLZ_FORGE_BUILD=',
              'append low-overhead sight and busy XR diagnostic overlay')
    # v11.306 changed the Wolf's physical collision radius to 0.78 via
    # v10.4 Sheep Lanes; its A* diagnostic still classified only 0.68.
    html=once(html,
      "const kind=Math.abs(args[2]-ST_WOLF_RADIUS)<.001?'wolf':'sheep';",
      "const kind=Math.abs(args[2]-stUnitRadius('wolf'))<.001?'wolf':'sheep';",
      'correct path radius telemetry without rewriting historic patches')
    html=once(html,'se265Perf.metricPage=(se265Perf.metricPage+1)%8;',
              'se265Perf.metricPage=(se265Perf.metricPage+1)%10;',
              'surface two additional Nerd Stats pages')
    old=" source.engine='§wyrl§ Engine · Maker v11.320';source.version=11.320;"
    if html.count(old)!=3:raise AssertionError(('v11.321 provenance count',html.count(old)))
    html=html.replace(old,
      " source.engine='§wyrl§ Engine · Maker v11.321';source.version=11.321;")
    for before,after in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_320_STUDIO_NAVIGATION_LAYOUT',MARKER),
      ('ENGINE · MAKER v11.320','ENGINE · MAKER v11.321'),
      ('v11.320 · organized studios and project-aware navigation',
       'v11.321 · Sheep Tag sightlines and busy Quest metrics'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.320'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.321'"),
      ('<title>§wyrl§ Engine · Maker v11.320</title>',
       '<title>§wyrl§ Engine · Maker v11.321</title>')
    ):html=once(html,before,after,'release identity')
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(n.get('version')=='v11.320' for n in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.320','changes':notes.get('changes',[])})
    notes.update(version='v11.321',title='Sheep Tag house visibility and busy Quest diagnostics',
      date='2026-11-07',changes=[
        'Owner Quest acceptance: the earlier last-sheep wolf pursuit slowdown largely improved; head turning in dense matches with living teammates and active house construction remains severe.',
        'Within fog-enabled games, an actual built-house footprint can occlude enemy sheep/wolf visibility, so visible detection no longer penetrates house walls. Enemy memories and approximate scent clues remain authentic last-known behavior, not live target coordinates.',
        'Enemy sight calculations cache each observer-target result within a simulation tick; do not add pathfinding or extra render or tracking loops.',
        'For crowded immersive games with more than one living sheep and eight or more houses, distribute v11.256 sheep evasion planning at one candidate per simulation update rather than two; retain all candidate choices and scores.',
        'Extend Nerd Stats to pages 9/10 and 10/10 for house-heavy head-turn versus still callback gaps, per-frame draw calls, occluded sight checks, and adaptive AI budget.',
        'Correct v11.306 wolf-radius A* metrics to use actual configured wolf radius (0.78) rather than obsolete 0.68; leave movement timestep, gameplay capture and save data unchanged.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
