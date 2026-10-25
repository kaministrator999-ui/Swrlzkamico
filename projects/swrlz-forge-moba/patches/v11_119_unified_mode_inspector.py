"""§E v11.119 — single movable mode-specific inspector and compact top bars."""
from pathlib import Path
import hashlib,json

def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:110],n)
 return s.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parent.parent
 js=(root/'runtime/model_atelier_unified_modes_v11_119.js').read_text(encoding='utf8')
 css=(root/'runtime/model_atelier_unified_modes_v11_119.css').read_text(encoding='utf8')
 html=once(html,'function atelierAdaptiveInstall(panel){',
                js+'\nfunction atelierAdaptiveInstall(panel){')
 # Do not create the second fixed-context sheet. Reuse its field proxies inside
 # the actual draggable inspector, retaining original source controls.
 html=once(html,' panel.append(ui);\n window.__SWRLZ_CONTEXT_BOOT.attached=true;',
                ' inspector.append(ui);\n window.__SWRLZ_CONTEXT_BOOT.attached=true;')
 # The v11.62 mobile context takeover formerly hid the actual inspector.
 html=once(html,"  panel.classList.toggle('atelier-mobile-context-mode',open);",
  """  panel.classList.toggle('atelier-mobile-context-mode',false);
  panel.classList.toggle('se-inspector-mode-view',open);
  if(open){
   panel.classList.remove('atelier-tools-closed');
   inspector.setAttribute('aria-hidden','false');
  }""")
 # Programmatically select an operation from the new horizontal mode bar
 # using the existing v11.61 registry, source fields and renderFields path.
 old="window.SWYRL_E_CONTEXT=Object.freeze({groups:()=>Object.fromEntries(allGroupNames.map(k=>[k,(catalog[k]||[]).map(v=>v.name)])),open:()=>open,current:()=>({group,operation:selectedName})});"
 new="""window.SWYRL_E_CONTEXT=Object.freeze({
  groups:()=>{buildCatalog();return Object.fromEntries(allGroupNames.map(k=>[k,(catalog[k]||[]).map(v=>v.name)]));},
  open:()=>open,current:()=>({group,operation:selectedName}),
  activate:(category,mode)=>{
   if(!allGroupNames.includes(category))return false;
   if(!open)setOpen(true);
   if(group!==category)pickGroup(category);
   const available=operations();
   if(mode&&available.some(o=>o.name===mode)){
    selectedName=mode;viewMode='all';showOps();
   }
   return true;
  }
 });"""
 html=once(html,old,new)
 # Re-selecting a category should not cause the native inspector to disappear.
 html=once(html,"if(open&&lastChoice===label){setOpen(false);return;}",
                "if(open&&lastChoice===label){setOpen(true);return;}")
 html=once(html,
 " buildCatalog();\n}\n// Native Model Atelier may be installed after initial module evaluation;",
 """ buildCatalog();
 seAtelierModeToolbarInstall(panel);
 seAtelierTopBarArrange(panel);
}
// Native Model Atelier may be installed after initial module evaluation;""")
 html=html.replace('</head>','<style id="se-v11119-unified-mode-layout">'+css+'</style>\n</head>',1)
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_118_SEMANTIC_TOOL_ORGANIZATION',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_119_UNIFIED_DRAGGABLE_MODE_INSPECTOR')
 for a,b in [
 ('ENGINE · MAKER v11.118','ENGINE · MAKER v11.119'),
 ('v11.118 · organized modeling tools','v11.119 · unified mode inspector'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.118'","window.SWRLZ_FORGE_BUILD={version:'v11.119'"),
 ('<title>§wyrl§ Engine · Maker v11.118</title>',
  '<title>§wyrl§ Engine · Maker v11.119</title>'),
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='One movable inspector, contextual tool modes and compact top controls',
 date='2026-10-25',changes=[
  'Retire the redundant bottom contextual sheet: its settings now live inside the existing movable mesh inspector.',
  'Show the selected tool category modes in a scrollable secondary bar directly above the original bottom category rail.',
  'Select a mode to show its actual associated tool settings and actions in the draggable inspector, without cloning any modeling implementations.',
  'Keep Meshes, Sculpt, Lasso, Topology, Face, Appearance, Motion and References mode-specific, with More opening the original full inspector.',
  'Compact top controls by grouping GLB/OBJ/PNG actions under Export and camera presets under Views while preserving their original buttons.',
  'Preserve saved models, undo, native tool bindings, 68 bundled assets, viewport pinch/orbit, and long-press menu suppression.'
 ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SWRLZ_V11119_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
