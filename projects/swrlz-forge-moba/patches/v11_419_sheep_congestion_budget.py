"""§E v11.419 — bound SOLO Quest AI collision recovery and avoid blocked path churn.
Preserve v11.418 team choice, Model VR index, satchel and LAN/controlled movement.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_419_SHEEP_CONGESTION_BUDGET'

def one(src,old,new,tag):
    n=src.count(old)
    if n!=1:raise AssertionError(('v11.419',tag,n,old[:120]))
    return src.replace(old,new,1)

def apply(html):
    helper=(ROOT/'runtime/sheep_congestion_budget_v11_419.js').read_text('utf8')
    assert helper.count('SE419_SHEEP_CONGESTION_BUDGET_START')==1
    begin=html.index('function stLanesYield(unit,blocker,target) {')
    end=html.index('// Raised routes use the same swept-body test',begin)
    block=html[begin:end]
    block=one(block,'function stLanesYield(unit,blocker,target) {',
      helper+'\nfunction stLanesYield(unit,blocker,target) {','install shared VR AI route budget')
    block=one(block,
'''  for (const candidate of candidates) {
    const route=stLanesDynamicPath(unit,candidate.p);''',
'''  // The old 100-point trail could produce dozens of synchronous A* searches.
  // Rotate one candidate per recovery tick for SOLO Quest AI only.
  const budgeted=se419TrafficActive(unit);
  const attempts=budgeted?Math.min(1,candidates.length):candidates.length;
  const offset=budgeted?(t.se419YieldIndex||0)%Math.max(1,candidates.length):0;
  for(let i=0;i<attempts;i++) {
    const candidate=candidates[(offset+i)%candidates.length];
    if(!se419TrafficPermit(unit))break;
    if(budgeted){t.se419YieldIndex=(offset+i+1)%candidates.length;se419Traffic.yieldProbes++;}
    const route=stLanesDynamicPath(unit,candidate.p);''','cap yield path searches')
    block=one(block,
'''  if(unit.pathVersion!==s.navVersion||movedTarget||s.elapsed>=unit.repathAt) {
    unit.path=(traffic.mode==='alternate lane'?stLanesDynamicPath(unit,aim):stPath(unit.pos,aim,radius))||[];''',
'''  if(unit.pathVersion!==s.navVersion||movedTarget||s.elapsed>=unit.repathAt) {
    // Building nav invalidation can repath every teammate in the SAME XR frame.
    // Defer only AI planning; never defer existing movement on a usable path.
    if(se419TrafficActive(unit)&&!se419TrafficPermit(unit)){
      traffic.retryAt=s.elapsed+se419TrafficPause(unit,.085);
      return false;
    }
    unit.path=(traffic.mode==='alternate lane'?stLanesDynamicPath(unit,aim):stPath(unit.pos,aim,radius))||[];''','budget newly invalidated movement paths')
    block=one(block,
'''    if(!stSegmentClear(context,unit.pos,candidate,radius)){unit.path=[];unit.repathAt=0;break;}''',
'''    if(!stSegmentClear(context,unit.pos,candidate,radius)){
      unit.path=[];
      if(se419TrafficActive(unit)){
        // Do not rerun costly A* every tick into a house that still occupies the lane.
        unit.repathAt=s.elapsed+se419TrafficPause(unit,.72);
        traffic.retryAt=unit.repathAt;traffic.mode='waiting for lane';
        se419Traffic.blockedStatic++;
      }else unit.repathAt=0;
      break;
    }''','back off blocked house lane')
    block=one(block,
'''      if(s.elapsed>=traffic.retryAt) {
        const route=stLanesDynamicPath(unit,aim);
        if(route?.length){unit.path=route;traffic.mode='alternate lane';unit.repathAt=s.elapsed+1.2;}
        else if(blocker.kind===unit.kind)stLanesYield(unit,blocker,target);
        traffic.retryAt=s.elapsed+.3;
      }''',
'''      if(s.elapsed>=traffic.retryAt) {
        const budgeted=se419TrafficActive(unit);
        if(budgeted)se419Traffic.blockedUnits++;
        if(budgeted&&traffic.se419TryYield&&blocker.kind===unit.kind){
          // The previous failed alternate route schedules ONE trail probe next time.
          stLanesYield(unit,blocker,target);
          traffic.se419TryYield=false;
          traffic.retryAt=s.elapsed+se419TrafficPause(unit,.80);
        }else if(se419TrafficPermit(unit)){
          const route=stLanesDynamicPath(unit,aim);
          if(route?.length){unit.path=route;traffic.mode='alternate lane';unit.repathAt=s.elapsed+1.2;traffic.se419TryYield=false;}
          else if(blocker.kind===unit.kind){
            if(budgeted)traffic.se419TryYield=true;
            else stLanesYield(unit,blocker,target);
          }
          traffic.retryAt=s.elapsed+(budgeted?se419TrafficPause(unit,.80):.3);
        }else traffic.retryAt=s.elapsed+se419TrafficPause(unit,.10);
      }''','avoid traffic retry storms')
    html=html[:begin]+block+html[end:]
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_418_SHEEP_FLOCK_SETUP',MARKER),
      ('ENGINE · MAKER v11.418','ENGINE · MAKER v11.419'),
      ('v11.418 · Sheep Tag AI flock setup','v11.419 · bounded Sheep Tag congestion'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.418'","window.SWRLZ_FORGE_BUILD={version:'v11.419'"),
      ('<title>§wyrl§ Engine · Maker v11.418</title>','<title>§wyrl§ Engine · Maker v11.419</title>')
    ]:html=one(html,old,new,'release identity')
    old=" source.engine='§wyrl§ Engine · Maker v11.418';source.version=11.418;"
    assert html.count(old)==5,('v11.419 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.419';source.version=11.419;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,{'version':'v11.418','changes':notes.get('changes',[])})
    notes.update(version='v11.419',date='2026-11-11',
      title='Sheep Tag: prevent AI congestion from triggering repeated route bursts',
      changes=[
       'When AI sheep converge between tight house lanes, cap their combined SOLO Quest path recalculations to one expensive route search per match update.',
       'A blocked sheep evaluates at most one rotating back-out candidate rather than dozens of trail routes in one frame, and retries failed lanes on staggered cooldowns.',
       'Human player movement, ordinary unobstructed AI movement, non-VR, multiplayer, wolf capture/AI and authorized building placement remain unchanged.',
       'Expose actual route-budget and congestion counters; physical Quest lag acceptance is still pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
