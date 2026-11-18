"""§E v11.509: keep the existing fold button accessible after collapsing."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_509_RAIL_REEXPAND'
def once(src,old,new,label):
 n=src.count(old)
 if n!=1:raise AssertionError(('v11.509',label,n))
 return src.replace(old,new,1)
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_508_UV_DEGENERATE_PREVIEW' in html
 css=(ROOT/'runtime/model_rail_reexpand_v11_509.css').read_text('utf8')
 assert 'SE509_RAIL_REEXPAND_END' in css
 html=html.replace('</head>','<style id="se509RailReexpand">\n'+css+'\n</style>\n</head>',1)
 for a,b in (
 ('SWYRL_ENGINE_DEPLOY_MARKER: V11_508_UV_DEGENERATE_PREVIEW',MARKER),
 ('ENGINE · MAKER v11.508','ENGINE · MAKER v11.509'),
 ('v11.508 · UV preview tolerates degenerate source triangles','v11.509 · restore collapsed tool rail expand control'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.508'","window.SWRLZ_FORGE_BUILD={version:'v11.509'"),
 ('<title>§wyrl§ Engine · Maker v11.508</title>','<title>§wyrl§ Engine · Maker v11.509</title>'),
 ):html=once(html,a,b,'identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.508';source.version=11.508;"
 assert html.count(old)==5
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.509';source.version=11.509;")
 key='const SE_RELEASE_NOTES='
 pos=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[pos:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.508']
 notes['history'].insert(0,{'version':'v11.508','changes':notes.get('changes',[])})
 notes.update(version='v11.509',date='2026-11-18',title='Restore collapsed Modeling rail expansion',changes=[
 'Keep the existing collapse/expand control visible and touch-accessible when the Modeling tool rail is folded on compact mobile screens.',
 'Preserve the original click handler, fold preference, tool selections and model state without adding a second button.',
 'Do not expose Modeling controls in Rigging or Animation.'
 ])
 return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[pos+width:]
