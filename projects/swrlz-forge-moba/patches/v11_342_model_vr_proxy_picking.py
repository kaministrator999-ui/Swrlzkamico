"""§E v11.342 · lightweight dual-controller model hover, exact action picking."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def one(s,a,b):
 assert s.count(a)==1,('v11.342 anchor',a[:70],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 for a,b in [('runtime/model_vr_workspace_v11_341.js','runtime/model_vr_workspace_v11_342.js'),('runtime/model_studio_vr_ui_v11_341.js','runtime/model_studio_vr_ui_v11_342.js')]:
  html=one(html,(ROOT/a).read_text('utf8'),(ROOT/b).read_text('utf8'))
 for a,b in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_341_MODEL_VR_HOVER_ORBIT','SWYRL_ENGINE_DEPLOY_MARKER: V11_342_MODEL_VR_PROXY_PICKING'),('ENGINE · MAKER v11.341','ENGINE · MAKER v11.342'),('v11.341 · faster XR picking and smooth model orbit','v11.342 · coarse hover proxies and exact action picking'),("window.SWRLZ_FORGE_BUILD={version:'v11.341'","window.SWRLZ_FORGE_BUILD={version:'v11.342'"),('<title>§wyrl§ Engine · Maker v11.341</title>','<title>§wyrl§ Engine · Maker v11.342</title>')]:
  html=one(html,a,b)
 a=" source.engine='§wyrl§ Engine · Maker v11.341';source.version=11.341;"
 assert html.count(a)==3
 html=html.replace(a," source.engine='§wyrl§ Engine · Maker v11.342';source.version=11.342;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 if not any(h.get('version')=='v11.341' for h in notes.get('history',[])):
  notes.setdefault('history',[]).insert(0,{'version':'v11.341','changes':notes.get('changes',[])})
 notes.update(version='v11.342',title='Lightweight dual-controller model hover',date='2026-11-08',changes=[
  'Idle rays use world-space part proxies instead of CPU skinned triangles; Trigger and Grip preserve precise original mesh picking.',
  'Native model projections and bounds are cached; unnecessary world-traversal overhead is removed when pointing at the hand.',
  'Read-only XR picking diagnostics report proxy/precise sample counts and hover times; smooth modeling joystick controls remain intact.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
