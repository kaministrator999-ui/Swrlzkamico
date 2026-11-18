"""§E v11.511: repair native Model mini-studio rail and inspector layout."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA='70adeebcac766b4b3c7c090f18860f159b399f552e2a100b46904747422e4c67'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_511_MODEL_DOCK_VISIBILITY'
def once(s,a,b):
 assert s.count(a)==1,(a[:90],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 assert hashlib.sha256(html.encode('utf8')).hexdigest()==PARENT_SHA
 css=(ROOT/'runtime/model_dock_visibility_v11_511.css').read_text('utf8')
 assert 'SE511_MODEL_DOCK_VISIBILITY_END' in css
 html=html.replace('</head>','<style id="se511ModelDockVisibility">\n'+css+'\n</style>\n</head>',1)
 for a,b in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_510_CONE_AWARE_UV',MARKER),
  ('ENGINE · MAKER v11.510','ENGINE · MAKER v11.511'),
  ('v11.510 · measured curvature-aware UV islands','v11.511 · restore Modeling rail and inspector layout'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.510'","window.SWRLZ_FORGE_BUILD={version:'v11.511'"),
  ('<title>§wyrl§ Engine · Maker v11.510</title>','<title>§wyrl§ Engine · Maker v11.511</title>')
 ):html=once(html,a,b)
 old=" source.engine='§wyrl§ Engine · Maker v11.510';source.version=11.510;"
 assert html.count(old)==5,html.count(old)
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.511';source.version=11.511;")
 key='const SE_RELEASE_NOTES='
 pos=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[pos:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.510']
 notes['history'].insert(0,{'version':'v11.510','changes':notes.get('changes',[])})
 notes.update(version='v11.511',date='2026-11-18',title='Restore Modeling dock visibility',changes=[
  'Restore the existing Modeling category rail grid track and native fold control.',
  'Restore the real inspector panel when its Show/Hide control reports an expanded state.',
  'Respect Rigging and Animation isolation and preserve model, project and tool state.'
 ])
 return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\\/')+html[pos+width:]
