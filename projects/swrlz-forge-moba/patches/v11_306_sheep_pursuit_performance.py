"""§E v11.306 — bound the effective Sheep Tag wolf-pursuit A* work.
Preserve v11.256 sheep AI budget, existing capture, collision and XR authority.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_306_SHEEP_PURSUIT_PERFORMANCE'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.306',label,count,old[:120]))
    return html.replace(old,new,1)

def apply(html):
    for symbol in ('function stLanesSheepApproach(wolf,sheep) {',
                   'const stLanesOrderTargetBase = stOrderTarget;',
                   'const stLanesBotWolfBase = stBotWolf;',
                   'const se256AIBudget',
                   'function se286Lines(page){',
                   'SWYRL_ENGINE_DEPLOY_MARKER: V11_305_VANGUARD_COMPLETE_MESH_UV'):
        if symbol not in html:raise AssertionError(('v11.306 prerequisite',symbol))
    helper="""// SE306_SHARED_APPROACH_CACHE — one bounded A* approach for both callers.
function se306CachedApproach(wolf,sheep){
  const s=stSession,prior=wolf.sheepApproach;
  if(prior&&prior.id===sheep.id&&prior.version===s.navVersion&&
      prior.at>s.elapsed&&prior.target.distanceToSquared(sheep.pos)<=4){
    se306Perf.reuses++;
    return prior.point?prior.point.clone():null;
  }
  const point=stLanesSheepApproach(wolf,sheep);
  // Negative cache prevents repeated nine-candidate A* scans while blocked.
  // Recheck after movement, changed buildings, or a brief per-wolf timeout.
  wolf.sheepApproach={id:sheep.id,version:s.navVersion,
    at:s.elapsed+.4+((wolf.botIndex||0)%3)*.08,
    target:sheep.pos.clone(),point:point?point.clone():null};
  se306Perf.adoptions++;
  return point;
}
"""
    html=once(html,'const stLanesOrderTargetBase = stOrderTarget;',
              helper+'const stLanesOrderTargetBase = stOrderTarget;',
              'share cached approach between wolf target update and AI decisions')
    old_target="""      const cache=unit.sheepApproach;
      if(cache&&cache.id===sheep.id&&cache.version===stSession.navVersion&&cache.at>stSession.elapsed&&cache.target.distanceToSquared(sheep.pos)<.04)return cache.point.clone();
      const point=stLanesSheepApproach(unit,sheep);
      if(point){unit.sheepApproach={id:sheep.id,version:stSession.navVersion,at:stSession.elapsed+.3,target:sheep.pos.clone(),point:point.clone()};return point;}
"""
    new_target="""      // SE306_CACHE_BOTH_CALLERS: do not redo nine A* candidates every frame.
      const point=se306CachedApproach(unit,sheep);
      if(point)return point;
"""
    html=once(html,old_target,new_target,'replace overly strict moving-target cache')
    html=once(html,
              '    const approach=stLanesSheepApproach(unit,sheep);',
              '    const approach=se306CachedApproach(unit,sheep);',
              'reuse the same cache from the wolf AI decision')
    html=once(html,'se265Perf.metricPage=(se265Perf.metricPage+1)%6;',
              'se265Perf.metricPage=(se265Perf.metricPage+1)%8;',
              'two additional Nerd Stats pages')
    script=(ROOT/'runtime/sheep_pursuit_performance_v11_306.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',script+'\nwindow.SWRLZ_FORGE_BUILD=',
              'add observational A* and simulation-cadence metrics')
    old_version=" source.engine='§wyrl§ Engine · Maker v11.305';source.version=11.305;"
    if html.count(old_version)!=3:
        raise AssertionError(('v11.306 source metadata count',html.count(old_version)))
    html=html.replace(old_version,
      " source.engine='§wyrl§ Engine · Maker v11.306';source.version=11.306;")
    for before,after in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_305_VANGUARD_COMPLETE_MESH_UV',MARKER),
      ('ENGINE · MAKER v11.305','ENGINE · MAKER v11.306'),
      ('v11.305 · simultaneous full character mesh and UV sculpt',
       'v11.306 · Sheep Tag pursuit routing and frame diagnostics'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.305'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.306'"),
      ('<title>§wyrl§ Engine · Maker v11.305</title>',
       '<title>§wyrl§ Engine · Maker v11.306</title>')
    ):html=once(html,before,after,'runtime identity')
    marker='const SE_RELEASE_NOTES='
    at=html.index(marker)+len(marker)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Sheep Tag wolf pursuit cache and simulation performance diagnostics',
      date='2026-11-06',changes=[
        'Owner Quest report: all sheep and wolves in motion sometimes stutter; three wolves attacking maximum houses remain smooth until the last sheep leaves shelter, then movement globally slows.',
        'Reuse the same short-lived wolf approach cache for both the live attack target and bot decision; the old 0.2-unit movement threshold caused near-per-frame A* searches when chasing a moving sheep.',
        'Cache a reachable approach or an unreachable result briefly, invalidate on building navigation changes and significant sheep movement; stagger expiration by wolf index.',
        'Preserve v11.256 global frame-budgeted sheep escape AI, wolf visibility and tactics, building attacks, captures, collision, movement and multiplayer authority.',
        'Add Nerd Stats pages 7/8 and 8/8: A* CPU by path radius, cached approach hits and refreshes, and wall-clock versus simulation-clock progression. CPU timers are not GPU timers.',
        'Keep existing 50ms simulation step cap unchanged until real Quest diagnosis shows whether timing correction is needed.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
