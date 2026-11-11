"""§E v11.393 — bounded Quest sheep NPC planning, same-tick sight reuse.

The owner's Quest 3S has severe gameplay-only callback stalls correlated with
multiple living AI sheep. Keep every gameplay/physics tick intact; distribute
the original base/build candidate searches over successive SOLO XR frames.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_393_SHEEP_QUEST_AI_FRAME_BUDGET'
def one(s,old,new,tag):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.393',tag,n,old[:120]))
    return s.replace(old,new,1)
def apply(html):
    runtime=(ROOT/'runtime/sheep_quest_bot_frame_budget_v11_393.js').read_text('utf8')
    for required in ('function se393ChooseSheepBase(unit){',
                     'function se393PlanSheepBuild(unit){',
                     'SWYRL_ENGINE_SHEEP_AI_FRAME_BUDGET_393'):
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
    next_block="""if(unit.order){if(se393Active())se393CancelSheepPlan(unit);return;}
  if(se393Active()){
    if(unit.base&&Math.hypot(unit.base.x-s.pen.x,unit.base.z-s.pen.z)<
       stSanctuaryRadius()+4.5){
      unit.base=null;unit.se393Base=null;unit.se393Build=null;
    }
    if(!unit.base&&!se393ChooseSheepBase(unit))return;
    if(!unit.base){unit.aiIntent='seek clear building ground outside the sanctuary';return;}
    if(se393PlanSheepBuild(unit))return;
  }else{
    """+fallback+"\n  }\n  "
    html=one(html,original,next_block,'effective NPC base/build with sanctuary')
    prior_guard=('if(unit.captured||unit.isIllusion||unit.archiveRoute||'
      '(!unit.se256Escape&&s.elapsed<unit.botAt))return;'
      'if(!unit.se256Escape)unit.botAt=s.elapsed+1.1;')
    next_guard="""if(unit.captured||unit.isIllusion||unit.archiveRoute){
    if(se393Active())se393CancelSheepPlan(unit);
    return;
  }
  const se393Pending=se393Active()&&(!!unit.se393Base||!!unit.se393Build);
  if(!unit.se256Escape&&!se393Pending&&s.elapsed<unit.botAt)return;
  if(!unit.se256Escape&&!se393Pending)unit.botAt=s.elapsed+1.1;"""
    html=one(html,prior_guard,next_guard,'continue pending base/build decisions')
    html=one(html,'window.SWRLZ_FORGE_BUILD=',runtime+'\nwindow.SWRLZ_FORGE_BUILD=',
      'late standalone runtime helpers and diagnostics')
    for a,b in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_391_SHEEP_QUEST_Y_TOOLS_RADIAL',MARKER),
      ('ENGINE · MAKER v11.391','ENGINE · MAKER v11.393'),
      ('v11.391 · Quest Sheep Tag Y quick tools radial',
       'v11.393 · smooth Quest sheep NPC planning'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.391'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.393'"),
      ('<title>§wyrl§ Engine · Maker v11.391</title>',
       '<title>§wyrl§ Engine · Maker v11.393</title>')
    ]:html=one(html,a,b,'release identity')
    provenance=" source.engine='§wyrl§ Engine · Maker v11.391';source.version=11.391;"
    assert html.count(provenance)==5,('v11.393 provenance',html.count(provenance))
    html=html.replace(provenance,
       " source.engine='§wyrl§ Engine · Maker v11.393';source.version=11.393;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.391' for x in notes.get('history',[])):
      notes.setdefault('history',[]).insert(0,
        {'version':'v11.391','changes':notes.get('changes',[])})
    notes.update(version='v11.393',date='2026-11-10',
      title='Quest Sheep Tag: bound NPC base/build planning without slowing movement',
      changes=[
        'Quest owner reports match-only 3s running/1s freeze pattern with many living sheep; menu smooth, fewer sheep markedly smoother. Restore the unchanged v11.391 camera and target game CPU work.',
        'Solo Quest XR sheep bots spread base-site path selection and 12-site building exit validation across headset game frames, at most one navigation candidate per frame across all sheep. Native collision, continuous unit movement, AI escape logic and building validation are retained.',
        'Avoid duplicate per-entity team-visibility computations within the same simulation tick when entity positions, team, capture state and navigation have not changed.',
        'Non-VR/desktop/phone planners and LAN match authority remain unchanged. Include truthful planning counters; Quest physical verification is pending and no zero-freeze guarantee is claimed.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
