"""§E v11.121: unbury native mesh component toolbar below top controls."""
from pathlib import Path
import hashlib,json
def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:125],n)
 return s.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parent.parent
 css=(root/'runtime/model_atelier_uncovered_components_v11_121.css').read_text(encoding='utf8')
 html=once(html,
  " parent.append(row);\n row.addEventListener('pointerdown',e=>e.stopPropagation());",
  """ const seComponentToolbarAnchor=panel.querySelector('#modelAtelierViewportModes');
 if(seComponentToolbarAnchor?.parentElement){
  seComponentToolbarAnchor.after(row);
  row.classList.add('se-component-inline');
 }else parent.append(row);
 row.addEventListener('pointerdown',e=>e.stopPropagation());""")
 html=html.replace('</head>','<style id="se-v11121-component-row">'+css+'</style>\n</head>',1)
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_120_CENTERED_TOOLBAR_LAYER_AND_TOUCH_ZOOM',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_121_UNCOVERED_MESH_COMPONENT_TOOLBAR')
 for a,b in [
 ('ENGINE · MAKER v11.120','ENGINE · MAKER v11.121'),
 ('v11.120 · top menus and centered tools','v11.121 · uncovered mesh component tools'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.120'","window.SWRLZ_FORGE_BUILD={version:'v11.121'"),
 ('<title>§wyrl§ Engine · Maker v11.120</title>','<title>§wyrl§ Engine · Maker v11.121</title>'),
 ]:html=once(html,a,b)
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Mesh component toolbar visibly below top render/view/reference controls',
 date='2026-10-25',changes=[
  'Move Mesh/Vertex/Edge/Face with Multi/Tap/Box/Lasso/Clear/axis nudges into an independently visible row directly beneath References, rather than leaving it under the render toolbar.',
  'Reuse the original component control node and click/pointer handlers, keeping object and topology selection, vertex/edge/face modes, camera orbit and undo unchanged.',
  'Provide touch-friendly full-width row on mobile with local scrolling on short screens; keep top Export/Views menus and centered bottom tool categories.',
  'Avoid stacking hacks or disabling component controls to mask the overlap.'
 ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SWRLZ_V11121_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
