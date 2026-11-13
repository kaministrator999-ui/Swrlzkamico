"""§E v11.439 — live wolf pursuit contact, bounded approach and capture tracing."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_439_SHEEP_CAPTURE_PURSUIT'

def one(s,old,new,label):
 n=s.count(old)
 assert n==1,('v11.439',label,n,old[:125])
 return s.replace(old,new,1)

def apply(html):
 runtime=(ROOT/'runtime/sheep_capture_pursuit_v11_439.js').read_text('utf-8')
 assert 'SE439_SHEEP_CAPTURE_PURSUIT_START' in runtime
 assert 'requestAnimationFrame(' not in runtime and 'setAnimationLoop(' not in runtime
 # Redirect ONLY the native active lane-movement's normal path selection;
 # collision sweeps, unsupported map routes and prior XR worker are retained.
 html=one(html,
   "unit.path=(traffic.mode==='alternate lane'?stLanesDynamicPath(unit,aim):se438Route(unit,unit.pos,aim,radius))||[];",
   "unit.path=(se439DirectChase(unit,aim,context)?[aim.clone()]:(traffic.mode==='alternate lane'?stLanesDynamicPath(unit,aim):se438Route(unit,unit.pos,aim,radius)))||[];",
   'unobstructed solo XR wolf chase')
 # The wolf's native per-frame capture scan remains one-shot. Replace only
 # the scan to count eligibility and preserve its original contact radius.
 html=one(html,
   "for(const sheep of s.units)if(sheep.kind==='sheep'&&!sheep.captured&&s.elapsed>=sheep.invulnerableUntil&&Math.hypot(unit.pos.x-sheep.pos.x,unit.pos.z-sheep.pos.z)<1.05)stCapture(sheep,unit);",
   "se439CaptureProbe(unit,s);",
   'capture eligibility tracing')
 html=one(html,'installPerformanceSettings();se189InstallPerfUI();',
   runtime+'\ninstallPerformanceSettings();se189InstallPerfUI();',
   'append wolf pursuit runtime')
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_438_RENDER_SIMULATION_BRIDGE',MARKER),
  ('ENGINE · MAKER v11.438','ENGINE · MAKER v11.439'),
  ('v11.438 · nonblocking AI paths and frame diagnostics',
   'v11.439 · smooth wolf pursuit and capture diagnosis'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.438'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.439'"),
  ('<title>§wyrl§ Engine · Maker v11.438</title>',
   '<title>§wyrl§ Engine · Maker v11.439</title>')
 ]:html=one(html,before,after,'release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.438';source.version=11.438;"
 assert html.count(old)==5,('v11.439 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.439';source.version=11.439;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.setdefault('history',[]).insert(0,{'version':'v11.438','changes':notes.get('changes',[])})
 notes.update(version='v11.439',date='2026-11-13',
   title='Sheep Tag wolf pursuit and capture proximity stability',changes=[
     'When pursuing a moving sheep in SOLO Quest VR, wolves first check an unobstructed direct approach rather than repeatedly performing up to nine synchronous A* approach searches. Close, unobstructed chases can follow the current position directly while keeping native collision and player movement.',
     'Wolf bot planning is paced at one full decision per solo XR simulation tick, while normal wolf movement and capture eligibility run every frame. Blocked maps keep the original building/alternate lane planning path.',
     'Swept movement into a sheep collider can now register the original 1.05-unit capture contact instead of missing a narrow capture zone on a blocked 0.09-unit movement step; captured flags, invulnerability, team rules and LAN behavior remain authoritative.',
     'Capture diagnostics separately count approach checks/CPU time, decision deferrals, contact sweeps, capture calls/CPU duration, immediate frame duration and following frames so headset testing can isolate the remaining hitch.',
     'The v11.438 worker, v11.434 graphics batching, v11.437 base/spirits, Model Studio and authored project data remain intact; GPU and Quest compositor times still require physical observation.'
   ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
