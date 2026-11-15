"""§E v11.463 — retain the native viewport toolbar after Undo clears mesh selection.

The existing v11.320 transform proxy is the only toolbar. Do not create
another one or change model history, saved topology, UVs, or camera/docks.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_463_TRANSFORM_BAR_HISTORY'
def one(text,old,new):
 count=text.count(old)
 if count!=1:raise AssertionError(('v11.463 anchor drift',old[:160],count))
 return text.replace(old,new,1)
def apply(html):
 # Native source still decides selection and history availability. Undo is
 # allowed to clear selection; that must DISABLE transforms, not hide Redo.
 html=one(html,
  '  const active=!!state?.open&&!!state?.selected&&!panel.hidden;\n'
  '  if(bar.hidden===active)bar.hidden=!active;',
  '  const active=!!state?.open&&!panel.hidden;\n'
  '  const hasSelection=!!state?.selected;\n'
  "  const caption=bar.querySelector('.se320-transform-label');\n"
  "  if(caption)caption.textContent=hasSelection?'Transform':'Select mesh · Undo / Redo';\n"
  '  if(bar.hidden===active)bar.hidden=!active;')
 html=one(html,
  "   button.disabled=!active||!uv?.available;",
  "   button.disabled=!hasSelection||!uv?.available;")
 html=one(html,
  "   button.disabled=!active||!original||original.disabled;",
  "   button.disabled=!hasSelection||!original||original.disabled;")
 # The toolbar's original history handlers do NOT depend on a selected part.
 # The native backing strip may be temporarily replaced while restoring Undo.
 html=one(html,
  "  if(!native||!scene)return; // Native selection/gizmo may mount later.",
  "  if(!scene)return; // Keep Undo/Redo reachable while native strip remounts.")
 html=one(html,
  "   new MutationObserver(()=>se320RefreshTransformAccess(panel)).observe(native,{\n"
  "    subtree:true,attributes:true,attributeFilter:['aria-pressed','disabled','hidden']\n"
  "   });",
  "   // Native strip observers bind below and are rebound if Undo replaces it.")
 html=one(html,
  "  if(bar.parentElement!==scene)scene.append(bar);\n"
  "  // Remove duplicate buttons from the sidebar, but keep their original DOM",
  "  if(bar.parentElement!==scene)scene.append(bar);\n"
  "  if(native&&bar._se463ObservedNative!==native){\n"
  "   new MutationObserver(()=>se320RefreshTransformAccess(panel)).observe(native,{\n"
  "    subtree:true,attributes:true,attributeFilter:['aria-pressed','disabled','hidden']\n"
  "   });\n"
  "   bar._se463ObservedNative=native;\n"
  "  }\n"
  "  // Remove duplicate buttons from the sidebar, but keep their original DOM")
 html=one(html,
  "  for(const source of native.querySelectorAll('[data-mode],[data-axis]'))",
  "  for(const source of native?.querySelectorAll('[data-mode],[data-axis]')||[])")
 # The original immediate click refresh precedes some asynchronous undo
 # state changes. The next animation frame re-reads native state safely.
 html=one(html,
  "    se320RefreshTransformAccess(panel);\n"
  "   });\n"
  "   // Native strip observers bind below and are rebound if Undo replaces it.",
  "    se320RefreshTransformAccess(panel);\n"
  "    if(button.dataset.se320History)requestAnimationFrame(()=>se320RefreshTransformAccess(panel));\n"
  "   });\n"
  "   // Native strip observers bind below and are rebound if Undo replaces it.")
 # Keep native history buttons in the inspector only when the toolbar cannot
 # be displayed (closed modeler); no user action loses the only Undo access.
 html=one(html,
  "SWYRL_ENGINE_DEPLOY_MARKER: V11_462_WIRE_CLARITY_MOBILE",MARKER)
 html=one(html,
  "/* SE462_MODEL_WIRE_CLARITY_END */",
  "/* SE462_MODEL_WIRE_CLARITY_END */\n"
  "/* Historical v11.462 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_462_WIRE_CLARITY_MOBILE */")
 for a,b in [
  ('ENGINE · MAKER v11.462','ENGINE · MAKER v11.463'),
  ('v11.462 · clean wire edges and mobile viewport','v11.463 · persistent transform history bar'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.462'","window.SWRLZ_FORGE_BUILD={version:'v11.463'"),
  ('<title>§wyrl§ Engine · Maker v11.462</title>','<title>§wyrl§ Engine · Maker v11.463</title>')
 ]:html=one(html,a,b)
 old=" source.engine='§wyrl§ Engine · Maker v11.462';source.version=11.462;"
 assert html.count(old)==5,('v11.463 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.463';source.version=11.463;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,size=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[r for r in notes.get('history',[]) if r.get('version')!='v11.462']
 notes['history'].insert(0,{'version':'v11.462','changes':notes.get('changes',[])})
 notes.update(version='v11.463',date='2026-11-15',
  title='Transform bar stays accessible after Undo and selection changes',
  changes=[
   'Undo/Redo remain in the original top Model Studio transform toolbar even when Undo clears object selection. Move/Rotate/Scale and axis nudges safely disable until a mesh is selected again.',
   'The toolbar states Select mesh instead of silently disappearing; reselecting a mesh automatically restores its enabled native transform actions.',
   'Native mesh selection/history controls are still the source of truth. The existing transform proxy rebinds after native strips remount and rereads state after Undo/Redo without touching the mesh or saved project.',
   'Previously validated camera orbit, draggable model docks, v11.462 clean wire modes, Inset/Extrude, VR and project/account saves remain unchanged.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+size:]
