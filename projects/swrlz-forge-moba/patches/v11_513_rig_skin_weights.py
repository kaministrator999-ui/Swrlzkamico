"""§E v11.513 — generic cloth skin independence and precise vertex weights.
Build only from the sealed v11.512 chain, preserving project and UV lineage.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_513_RIG_SKIN_WEIGHT_STUDIO'
def once(text,old,new):
 n=text.count(old)
 if n!=1:raise AssertionError(('v11.513 anchor',old[:125],n))
 return text.replace(old,new,1)
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_512_TRIGGER_GIZMOS_MENU_FACING' in html
 math=(ROOT/'runtime/model_rig_skin_math_v11_513.js').read_text('utf8')
 editor=(ROOT/'runtime/model_rig_weight_studio_v11_513.js').read_text('utf8')
 assert 'SE513_RIG_SKIN_MATH_END' in math
 assert 'SE513_RIG_WEIGHT_STUDIO_END' in editor
 # Both scripts run inside the existing ModelAtelier lexical closure. They
 # reuse native scene, per-part undo, model save, GPU skeleton and mesh data.
 html=once(html,'window.SWYRL_ENGINE_RIG_CONNECTED_EDIT_500=se500RigEdit;',
     'window.SWYRL_ENGINE_RIG_CONNECTED_EDIT_500=se500RigEdit;\n'+math+'\n'+editor)
 # Only the authored cloth target is skinned; unrelated model objects must not
 # inherit an arbitrary character's bind skeleton and accidentally deform.
 html=once(html,'if(!pos)return new THREE.Mesh(g,mat);',
     "if(!pos||rig.schema==='swyrl-cloth-skin-v1'&&part.id!==rig.targetPartId)return new THREE.Mesh(g,mat);")
 css="""
#se513WeightStudio{display:grid;gap:8px;margin:8px 0;padding:10px;
 border:1px solid #627894;border-radius:9px;background:#182438;color:#e5efff}
#se513WeightStudio[hidden]{display:none}
#se513WeightStudio label{display:grid;gap:4px}
#se513WeightStudio input[type=range]{width:100%;min-height:27px}
#se513WeightStudio output{font-variant-numeric:tabular-nums;color:#b6ffe8}
#se513WeightStudio small{line-height:1.4;color:#b7cbe1}
#se513WeightStudio .se513WeightActions{display:flex;flex-wrap:wrap;gap:7px}
#se513WeightStudio button{min-height:39px;flex:1;border:1px solid #7494b9;
 border-radius:8px;color:#f1f7ff;background:#253952;padding:7px 9px}
#se513WeightStudio button[aria-pressed=true]{border-color:#9ef3d0;background:#225c56}
"""
 if '</head>' not in html:raise AssertionError('v11.513 document head missing')
 html=html.replace('</head>','<style id="se513WeightStudio">'+css+'</style>\n</head>',1)
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_512_TRIGGER_GIZMOS_MENU_FACING',MARKER),
  ('ENGINE · MAKER v11.512','ENGINE · MAKER v11.513'),
  ('v11.512 · trigger capture for VR gizmos and user-facing world menus',
   'v11.513 · precise skin weights and independent rig mesh bindings'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.512'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.513'"),
  ('<title>§wyrl§ Engine · Maker v11.512</title>',
   '<title>§wyrl§ Engine · Maker v11.513</title>')
 ):html=once(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.512';source.version=11.512;"
 assert html.count(old)==5,('v11.513 model provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.513';source.version=11.513;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.512']
 notes['history'].insert(0,{'version':'v11.512','changes':notes.get('changes',[])})
 notes.update(version='v11.513',date='2026-11-18',
  title='Editable weighted skin and isolated bind targets',changes=[
   'Rigging Studio now has a deliberate Paint selected bone weights mode with Add/Erase, brush radius and influence step, for generic editable rigged meshes using the existing native GPU skinning and project history.',
   'Each painted stroke updates actual four-influence skinIndex/skinWeight GPU attributes and saves validated, normalized per-vertex weights in the current project, in one native Undo step. Mirrored UV seam vertices receive matching paint.',
   'Paint mode is separate from ordinary bone selection and rest-joint drag, and canceling does not persist preview changes; current camera/orbit behavior remains untouched when the brush is not armed.',
   'Cloth skeletons are only bound to their declared targetPartId; unrelated scene meshes remain ordinary independent objects, avoiding unintended cross-object skin transforms.',
   'The v11.512 Quest Browser selection, immersive Trigger gizmos, menu-facing behavior, platform display toggle, Indent brush, UV editor, starters, cloud revision history and authored assets are preserved.',
   'This is progress on rigging QA #11/#12, not a claim of headset-verified parity or a complete remedy for the Sorting Hat-specific abnormal deformation. Immersive weight painting and full bone control remain open.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
