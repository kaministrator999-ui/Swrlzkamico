"""§E v11.411 — bounded Quest sheep NPC planning, same-tick sight reuse.

The owner's Quest 3S has severe gameplay-only callback stalls correlated with
multiple living AI sheep. Keep every gameplay/physics tick intact; distribute
the original base/build candidate searches over successive SOLO XR frames.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_411_SHEEP_QUEST_AI_FRAME_BUDGET'
def one(s,old,new,tag):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.411',tag,n,old[:120]))
    return s.replace(old,new,1)
def apply(html):
    runtime=(ROOT/'runtime/sheep_quest_bot_frame_budget_v11_411.js').read_text('utf8')
    for required in ('function se411ChooseSheepBase(unit){',
                     'function se411PlanSheepBuild(unit){',
                     'SWYRL_ENGINE_SHEEP_AI_FRAME_BUDGET_411'):
        assert required in runtime,required
    assert 'SWYRL_ENGINE_SHEEP_VR_Y_MENU_391' in html
    assert 'SWYRL_ENGINE_SHEEP_PURSUIT_306' in html
    # Prior patches also protect the wide-map sanctuary and avoid huge
    # navigation arrays for 256m maps. Snapshot their effective source and
    # preserve it VERBATIM in the desktop / LAN fallback branch.
    prefix=('if(unit.order)return;if(unit.base&&Math.hypot('
      'unit.base.x-s.pen.x,unit.base.z-s.pen.z)<stSanctuaryRadius()+4.5)')
    assert html.count(prefix)==1,('effective Quest sheep planner',html.count(prefix))
    start=html.index(prefix)
    end=html.index('if(s.elapsed>=unit.nextWanderAt)',start)
    original=html[start:end]
    fallback=original[len('if(unit.order)return;'):]
    next_block="""if(unit.order){if(se411Active())se411CancelSheepPlan(unit);return;}
  if(se411Active()){
    if(unit.base&&Math.hypot(unit.base.x-s.pen.x,unit.base.z-s.pen.z)<
       stSanctuaryRadius()+4.5){
      unit.base=null;unit.se411Base=null;unit.se411Build=null;
    }
    if(!unit.base&&!se411ChooseSheepBase(unit))return;
    if(!unit.base){unit.aiIntent='seek clear building ground outside the sanctuary';return;}
    if(se411PlanSheepBuild(unit))return;
  }else{
    """+fallback+"\n  }\n  "
    html=one(html,original,next_block,'effective NPC base/build with sanctuary')
    prior_guard=('if(unit.captured||unit.isIllusion||unit.archiveRoute||'
      '(!unit.se256Escape&&s.elapsed<unit.botAt))return;'
      'if(!unit.se256Escape)unit.botAt=s.elapsed+1.1;')
    next_guard="""if(unit.captured||unit.isIllusion||unit.archiveRoute){
    if(se411Active())se411CancelSheepPlan(unit);
    return;
  }
  const se411Pending=se411Active()&&(!!unit.se411Base||!!unit.se411Build);
  if(!unit.se256Escape&&!se411Pending&&s.elapsed<unit.botAt)return;
  if(!unit.se256Escape&&!se411Pending)unit.botAt=s.elapsed+1.1;"""
    html=one(html,prior_guard,next_guard,'continue pending base/build decisions')
    html=one(html,'window.SWRLZ_FORGE_BUILD=',runtime+'\nwindow.SWRLZ_FORGE_BUILD=',
      'late standalone runtime helpers and diagnostics')
    for a,b in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_410_MODEL_VR_ACCESSORY_WORKSHOP',MARKER),
      ('ENGINE · MAKER v11.410','ENGINE · MAKER v11.411'),
      ('v11.410 · shape and fit editable hip pouches in VR',
       'v11.411 · smooth Quest sheep NPC planning'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.410'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.411'"),
      ('<title>§wyrl§ Engine · Maker v11.410</title>',
       '<title>§wyrl§ Engine · Maker v11.411</title>')
    ]:html=one(html,a,b,'release identity')
    provenance=" source.engine='§wyrl§ Engine · Maker v11.410';source.version=11.410;"
    assert html.count(provenance)==5,('v11.411 provenance',html.count(provenance))
    html=html.replace(provenance,
       " source.engine='§wyrl§ Engine · Maker v11.411';source.version=11.393;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.410' for x in notes.get('history',[])):
      notes.setdefault('history',[]).insert(0,
        {'version':'v11.410','changes':notes.get('changes',[])})
    notes.update(version='v11.411',date='2026-11-11',
      title='Quest Sheep Tag: bound NPC base/build planning without slowing movement',
      changes=[
        'Quest owner reports match-only 3s running/1s freeze pattern with many living sheep; menu smooth, fewer sheep markedly smoother. Retain the restored v11.391 camera and the v11.410 VR accessory workshop while targeting game CPU work.',
        'Solo Quest XR sheep bots spread base-site path selection and 12-site building exit validation across headset game frames, at most one navigation candidate per frame across all sheep. Native collision, continuous unit movement, AI escape logic and building validation are retained.',
        'Avoid duplicate per-entity team-visibility computations within the same simulation tick when entity positions, team, capture state and navigation have not changed.',
        'Non-VR/desktop/phone planners and LAN match authority remain unchanged. Include truthful planning counters; Quest physical verification is pending and no zero-freeze guarantee is claimed.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
