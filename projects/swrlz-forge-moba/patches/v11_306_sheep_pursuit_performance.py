"""§E v11.306 — reuse wolf pursuit routes and rank sheep escape candidates.
Do not change capture, collision, player input or multiplayer authority.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_306_SHEEP_PURSUIT_PERFORMANCE'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.306',label,count,old[:110]))
    return html.replace(old,new,1)

def apply(html):
    for symbol in ('function stBotWolf(unit){','function stBotSheep(unit){',
                   'function stPath(start,target,radius){',
                   'SWYRL_ENGINE_DEPLOY_MARKER: V11_305_VANGUARD_COMPLETE_MESH_UV',
                   'function se286Lines(page){','function se265Lines(s,page){'):
        if symbol not in html:raise AssertionError(('v11.306 prerequisite',symbol))
    helper="""// SE306_PLANNED_ROUTE_REUSE
function stAdoptPlannedPath(unit,route,target,repathDelay=.8){
  unit.path=route;unit.pathVersion=stSession.navVersion;
  unit.pathTarget=target.clone();unit.repathAt=stSession.elapsed+repathDelay;
  se306Perf.adoptions++;
}
"""
    html=once(html,'function stBotSheep(unit){',helper+'function stBotSheep(unit){',
              'add route adoption helper')
    old_flee="""  if(danger){
    let best=null,score=-Infinity;
    for(let i=0;i<12;i++){
      const angle=i*Math.PI/6,x=unit.pos.x+Math.cos(angle)*7.5,z=unit.pos.z+Math.sin(angle)*7.5;
      if(stBlocked(x,z,ST_SHEEP_RADIUS))continue;
      const safety=Math.min(...wolves.map(w=>(x-w.pos.x)**2+(z-w.pos.z)**2));
      if(safety>score&&stPath(unit.pos,new THREE.Vector3(x,0,z),ST_SHEEP_RADIUS)){score=safety;best={x,z};}
    }
    if(best)stSetOrder(unit,{action:'move',...best});return;
  }
"""
    new_flee="""  if(danger){
    // SE306_SHEEP_SORTED_FLEE: score 12 options cheaply, pathfind best first.
    const choices=[];
    for(let i=0;i<12;i++){
      const angle=i*Math.PI/6,x=unit.pos.x+Math.cos(angle)*7.5,z=unit.pos.z+Math.sin(angle)*7.5;
      if(stBlocked(x,z,ST_SHEEP_RADIUS))continue;
      const safety=Math.min(...wolves.map(w=>(x-w.pos.x)**2+(z-w.pos.z)**2));
      choices.push({x,z,safety});
    }
    choices.sort((a,b)=>b.safety-a.safety);
    for(const choice of choices){
      const point=new THREE.Vector3(choice.x,0,choice.z);
      const route=stPath(unit.pos,point,ST_SHEEP_RADIUS);
      if(!route)continue;
      stSetOrder(unit,{action:'move',x:choice.x,z:choice.z});
      stAdoptPlannedPath(unit,route,point);
      break;
    }
    return;
  }
"""
    html=once(html,old_flee,new_flee,'reuse the highest-safe reachable sheep escape path')
    old_wolf="""  if(stPath(unit.pos,target.pos,ST_WOLF_RADIUS)){stSetOrder(unit,{action:'attack',id:target.id});return;}
"""
    new_wolf="""  // SE306_WOLF_ROUTE_REUSE: do not discard a valid chase route each AI decision.
  const sameChase=unit.order?.action==='attack'&&unit.order.id===target.id;
  if(sameChase&&unit.path?.length&&unit.pathVersion===s.navVersion&&
      unit.pathTarget?.distanceToSquared(target.pos)<=1){
    se306Perf.reuses++;
    return;
  }
  const chaseRoute=stPath(unit.pos,target.pos,ST_WOLF_RADIUS);
  if(chaseRoute){
    if(!sameChase)stSetOrder(unit,{action:'attack',id:target.id});
    stAdoptPlannedPath(unit,chaseRoute,target.pos,.8+(unit.botIndex%3)*.07);
    return;
  }
"""
    html=once(html,old_wolf,new_wolf,'preserve and stagger wolf chase route')
    old_blocker="""    if(cell>=0&&stPath(unit.pos,stCellPoint(nav,cell),ST_WOLF_RADIUS)){stSetOrder(unit,{action:'attack',id:building.id});return;}
"""
    new_blocker="""    if(cell<0)continue;
    const route=stPath(unit.pos,stCellPoint(nav,cell),ST_WOLF_RADIUS);
    if(!route)continue;
    if(unit.order?.action!=='attack'||unit.order.id!==building.id)
      stSetOrder(unit,{action:'attack',id:building.id});
    stAdoptPlannedPath(unit,route,building.pos,.8+(unit.botIndex%3)*.07);
    return;
"""
    html=once(html,old_blocker,new_blocker,'avoid double A* on wolf building route')
    html=once(html,'se265Perf.metricPage=(se265Perf.metricPage+1)%6;',
              'se265Perf.metricPage=(se265Perf.metricPage+1)%8;',
              'two additional Nerd Stats pages')
    script=(ROOT/'runtime/sheep_pursuit_performance_v11_306.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',script+'\nwindow.SWRLZ_FORGE_BUILD=',
              'append observational CPU and simulation diagnostics')
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
    notes.update(title='Sheep Tag pursuit pathfinding reuse and performance diagnostics',
      date='2026-11-06',changes=[
        'Owner Quest report: all sheep and all wolves moving sometimes stutter; three wolves attacking maximum houses remain smooth until the last sheep leaves shelter, when the whole simulation gradually slows.',
        'Rank all twelve bot sheep escape directions cheaply, then A* the safest reachable route rather than performing repeated incremental-best route searches; reuse the actual calculated route.',
        'Prevent wolf chase target refresh from discarding an already valid route; reuse reachability routes for sheep and house targets with small per-wolf stagger.',
        'Add 7/8 and 8/8 Nerd Stats pages measuring actual wolf/sheep A* CPU costs, reuse counts, simulation/wall-clock ratio and update time; no claimed GPU timing.',
        'Leave control, building health, collisions, WebXR input, game rules, multiplayer authority and the existing 50ms timestep cap untouched; the owner tests before any timing overhaul.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
