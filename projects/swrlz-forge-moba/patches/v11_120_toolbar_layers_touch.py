"""§E v11.120: mobile top menus, bottom category centering and scoped zoom."""
from pathlib import Path
import hashlib,json
def once(src,old,new):
 assert src.count(old)==1,(old[:125],src.count(old))
 return src.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parent.parent
 js=(root/'runtime/model_atelier_chrome_layer_v11_120.js').read_text(encoding='utf8')
 css=(root/'runtime/model_atelier_chrome_layer_v11_120.css').read_text(encoding='utf8')
 html=once(html,'function seAtelierModeNames(api,category){',
           js+'\nfunction seAtelierModeNames(api,category){')
 html=once(html,'function atelierMeshToolbarRefresh(){',
  """// Respect the final existing placement algorithm and only lift the strip
// when it would otherwise be hidden behind the top toolbar.
const seAtelierPriorMeshToolbarPosition=atelierMeshToolbarPosition;
atelierMeshToolbarPosition=function(...args){
 seAtelierPriorMeshToolbarPosition(...args);
 if(!atelierMeshStrip||atelierMeshStrip.hidden||!stage)return;
 const safeTop=seAtelierQuickstripSafeTop(stage);
 const currentTop=parseFloat(atelierMeshStrip.style.top);
 if(Number.isFinite(currentTop)&&currentTop<safeTop)
  atelierMeshStrip.style.top=Math.round(safeTop)+'px';
};
function atelierMeshToolbarRefresh(){""")
 html=once(html,' seAtelierModeToolbarInstall(panel);\n seAtelierTopBarArrange(panel);',
 """ seAtelierModeToolbarInstall(panel);
 seAtelierTopBarArrange(panel);
 seAtelierBottomRailCenter(panel);
 seAtelierTopMenuExclusivity(panel);""")
 html=html.replace('</head>','<style id="se-v11120-toolbar-layer">'+css+'</style>\n</head>',1)
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_119_UNIFIED_DRAGGABLE_MODE_INSPECTOR',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_120_CENTERED_TOOLBAR_LAYER_AND_TOUCH_ZOOM')
 for a,b in [
 ('ENGINE · MAKER v11.119','ENGINE · MAKER v11.120'),
 ('v11.119 · unified mode inspector','v11.120 · top menus and centered tools'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.119'","window.SWRLZ_FORGE_BUILD={version:'v11.120'"),
 ('<title>§wyrl§ Engine · Maker v11.119</title>','<title>§wyrl§ Engine · Maker v11.120</title>'),
 ]:html=once(html,a,b)
 tag='const SE_RELEASE_NOTES=';i=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[i:])
 notes.update(title='Unobscured top menus, centered tool rail, editor-only double-tap fix',
 date='2026-10-25',changes=[
  'Layer Views and Export above adjacent top controls with original buttons intact.',
  'Position floating mesh quickstrip below measured top toolbar, avoiding covered controls.',
  'Center the selected bottom tool category by scrolling the original RTL-aware rail.',
  'Prevent double-tap browser zoom only within the editor; preserve pinch zoom and text size accessibility elsewhere.',
  'Preserve all native modeling, scene data, undo, touch gestures and all 68 bundled assets.'])
 html=html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[i+n:]
 raw=html.encode('utf8')
 print('SWRLZ_V11120_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
