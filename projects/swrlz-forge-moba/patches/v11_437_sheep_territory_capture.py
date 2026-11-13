"""§E v11.437 — independent SOLO sheep AI territories and prepared capture wisps."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_436_SHEEP_TERRITORY_CAPTURE'
def one(source,old,new,label):
 n=source.count(old)
 assert n==1,('v11.437',label,n,old[:125])
 return source.replace(old,new,1)
def scoped(source,start,end,old,new,label):
 a=source.index(start);b=source.index(end,a)
 section=source[a:b]
 assert section.count(old)==1,('v11.437',label,section.count(old),old[:110])
 return source[:a]+section.replace(old,new,1)+source[b:]
def apply(html):
 js=(ROOT/'runtime/sheep_territory_capture_v11_436.js').read_text('utf8')
 assert 'SE437_SHEEP_TERRITORY_CAPTURE_START' in js
 # Both the desktop/native sheep base chooser and Quest's time-sliced chooser
 # stop importing every sheep-owned house into their candidate territories.
 html=scoped(html,'function stChooseBase(unit){','function stBotSheep(unit){',
  "candidates=[unit.home.clone(),...s.buildings.filter(b=>b.hp>0&&s.units.some(u=>u.id===b.owner&&u.kind==='sheep')).slice(0,12).map(b=>b.pos.clone().add(new THREE.Vector3(4.5,0,4.5)))]",
  'candidates=se437BaseCandidates(unit)','desktop base candidates')
 html=scoped(html,'function stChooseBase(unit){','function stBotSheep(unit){',
  '||stBlocked(p.x,p.z,stUnitRadius(unit)))continue;',
  '||!se437BaseAllowed(unit,p)||stBlocked(p.x,p.z,stUnitRadius(unit)))continue;',
  'desktop base separation')
 html=scoped(html,'function se411ChooseSheepBase(unit){','function se411PlanSheepBuild(unit){',
  """const candidates=[unit.home.clone(),
      ...s.buildings.filter(b=>b.hp>0&&s.units.some(u=>
        u.id===b.owner&&u.kind==='sheep')).slice(0,12)
        .map(b=>b.pos.clone().add(new THREE.Vector3(4.5,0,4.5)))];""",
  'const candidates=se437BaseCandidates(unit);','Quest base candidates')
 html=scoped(html,'function se411ChooseSheepBase(unit){','function se411PlanSheepBuild(unit){',
  'if(permitted&&!stBlocked(p.x,p.z,r)){',
  'if(permitted&&se437BaseAllowed(unit,p)&&!stBlocked(p.x,p.z,r)){',
  'Quest base separation')
 html=scoped(html,'function se411PlanSheepBuild(unit){','const se411PriorSeenByRole=stSeenByRole;',
  'if(result.ok){','if(result.ok&&se437BuildAllowed(unit,x,z)){',
  'Quest AI construction separation')
 html=scoped(html,'function stBotSheep(unit){','function stBotWolf(unit){',
  'if(!result.ok)continue;','if(!result.ok||!se437BuildAllowed(unit,x,z))continue;',
  'desktop AI construction separation')
 html=one(html,'installPerformanceSettings();se189InstallPerfUI();',
   js+'\ninstallPerformanceSettings();se189InstallPerfUI();','append scoped runtime')
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_436_CUBE_EXTRUDE_SATCHEL_CAVITY',MARKER),
  ('ENGINE · MAKER v11.436','ENGINE · MAKER v11.437'),
  ('v11.436 · working cube extrusion and connected satchel tutorial',
   'v11.437 · independent sheep territories and smoother capture'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.436'","window.SWRLZ_FORGE_BUILD={version:'v11.437'"),
  ('<title>§wyrl§ Engine · Maker v11.436</title>',
   '<title>§wyrl§ Engine · Maker v11.437</title>')
 ]:html=one(html,before,after,'release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.436';source.version=11.436;"
 assert html.count(old)==5,('v11.437 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.437';source.version=11.437;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.setdefault('history',[]).insert(0,{'version':'v11.436','changes':notes.get('changes',[])})
 notes.update(version='v11.437',date='2026-11-12',
  title='Sheep Tag independent AI building territory and capture visual pooling',
  changes=[
   'Solo sheep bots now choose home-centred, staggered territory candidates rather than converging around other sheep-owned houses; their construction respects player houses and other assigned bases.',
   'Quest AI retains v11.411 candidate time-slicing and v11.419 congestion path budget, with no new per-frame path searches.',
   'Solo Quest games prepare at most four unattached captured-sheep spirit visuals gradually, so wolf captures usually reuse one instead of building the entire wisp synchronously.',
   'The existing v11.136 capture building-removal nav batching and deferred GPU disposal remain authoritative; new capture CPU metrics distinguish remaining work from render stalls.',
   'Player building freedom, headstart, spirit rescue, wolf AI, LAN authority, authored map data, VR camera and model gizmos remain unchanged.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
