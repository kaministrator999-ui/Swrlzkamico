"""§E v11.293: general native character geometry and painted Chat receipts.

Append-only successor of the sealed v11.292 artifact. Existing code is patched
at exact governed anchors; historical patch/runtime inputs remain unchanged.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def once(text,old,new):
    count=text.count(old)
    if count!=1:raise AssertionError(('v11.293 anchor',old[:150],count))
    return text.replace(old,new,1)

def section(source,name):
    return source.split(f'/* SE293_{name}_START */',1)[1].split(f'/* SE293_{name}_END */',1)[0]

def apply(html):
    source=(ROOT/'runtime/chat_character_tools_v11_293.js').read_text('utf8')
    shared=section(source,'SHARED')
    html=once(html,'function seChatAtelierApply(op){',
        shared+section(source,'ATELIER')+'\nfunction seChatAtelierApply(op){')
    old="const p={id:'atelier-chat-'+crypto.randomUUID(),name:op.name||'New mesh',kind:op.kind,position:op.position||[0,2.6,.7],rotation:op.rotation||[0,0,0],scale:op.scale||[.3,.3,.3],color:op.color||'#88daff',material:op.material||'gloss',group:'Custom'};"
    html=once(html,old,'const p=se293ChatNativePart(op);')
    html=once(html,"if(op.op.startsWith('rig.'))return seChatRigApply(op);\n  const describe=",
        "if(op.op.startsWith('rig.'))return seChatRigApply(op);\n  if(op.op==='editor.frame'){const view=op.view||'three';if(!['front','back','left','right','three','hero','top','bottom'].includes(view)||!atelierCourierCamera(view))throw Error('MODEL_FRAME_UNAVAILABLE');return {framed:true,view};}\n  const describe=")
    # Validate the full candidate before changing a native part or recording
    # history. Existing import/sculpt/topology validators remain authoritative.
    html=once(html,"if(changed){checkpoint();for(const k of keys)p[k]=Array.isArray(op[k])?[...op[k]]:op[k];selection=p.id;signalEdited();}",
        "if(changed){const candidate={...p,...Object.fromEntries(keys.map(k=>[k,Array.isArray(op[k])?[...op[k]]:op[k]]))};if(!checkPart(candidate))throw Error('INVALID_NATIVE_PART');checkpoint();for(const k of keys)p[k]=candidate[k];selection=p.id;signalEdited();}")
    # Scratch history must restore the same draft model, never overwrite the
    # unrelated scene project's modelAtelier field.
    html=once(html,'dst.push(modelSnapshot());currentProject.modelAtelier=JSON.parse(src.pop());selection=null;',
        "dst.push(modelSnapshot());const restored=JSON.parse(src.pop());if(window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()){const draft=model();for(const key of Object.keys(draft))delete draft[key];Object.assign(draft,restored);}else currentProject.modelAtelier=restored;selection=null;")
    html=once(html,'const MAX_RAW=96*1024*1024,MAX_META=48,MAX_BATCH=16;',
        'const MAX_RAW=96*1024*1024,MAX_META=48,MAX_BATCH=64;')
    html=once(html,"KINDS=new Set(['sphere','box','cone','cylinder'])", "KINDS=new Set(['sphere','box','cone','cylinder','loft','lathe'])")
    # Preserve the existing 48-row metadata contract for older Chat backends;
    # the negotiated 64-operation plan limit is an independent capability.
    html=once(html,"function getProjectId(){if(!currentProject||typeof currentProject!=='object')throw Error('PROJECT_NOT_READY');if(!projectIds.has(currentProject))projectIds.set(currentProject,bounded(currentProject.instanceId,160)?currentProject.instanceId:id());return projectIds.get(currentProject);}",
        "function getProjectId(){const scratch=atelierOpen()&&window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.(),owner=scratch?window.SWYRL_ENGINE_WORKSPACES.scratchModel():currentProject;if(!owner||typeof owner!=='object')throw Error('PROJECT_NOT_READY');if(!projectIds.has(owner))projectIds.set(owner,!scratch&&bounded(owner.instanceId,160)?owner.instanceId:id());return projectIds.get(owner);}")
    html=once(html,"const workspace=atelierOpen()?'model-atelier':'scene',ms=ModelAtelier.status(),parts=currentProject?.modelAtelier?.parts||[];",
        "const workspace=atelierOpen()?'model-atelier':'scene',ms=ModelAtelier.status(),scratch=workspace==='model-atelier'&&window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.(),activeModel=scratch?window.SWYRL_ENGINE_WORKSPACES.scratchModel():currentProject?.modelAtelier,parts=activeModel?.parts||[];")
    html=once(html,"const value={...studioData,projectId:getProjectId(),project:{name:summaryName(currentProject.projectName||currentProject.name),kind:summaryName(currentProject.kind),template:summaryName(currentProject.template),sourceStarterId:summaryName(currentProject.sourceStarterId||'')},",
        "const value={...studioData,meshTools:se293MeshTools,projectId:getProjectId(),project:{name:scratch?'Untitled model':summaryName(currentProject.projectName||currentProject.name),kind:scratch?'model-atelier':summaryName(currentProject.kind),template:scratch?'blank-model':summaryName(currentProject.template),sourceStarterId:scratch?'':summaryName(currentProject.sourceStarterId||'')},")
    html=once(html,'const rigData=currentProject?.modelAtelier,hand=',
        "const rigData=workspace==='model-atelier'&&window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()?window.SWYRL_ENGINE_WORKSPACES.scratchModel():currentProject?.modelAtelier,hand=")
    html=once(html,'se178EnrichContext(value);se175UpdateLabel();if(new TextEncoder().encode(JSON.stringify(value)).length>32768)',
        "const sampledRows=workspace==='model-atelier'?value.meshes:value.actors;while(new TextEncoder().encode(JSON.stringify(value)).length>24000&&sampledRows.length>1)sampledRows.pop();se178EnrichContext(value);se175UpdateLabel();if(new TextEncoder().encode(JSON.stringify(value)).length>32768)")
    html=once(html,'function validateOperation(op,ctx){',shared+'\nfunction validateOperation(op,ctx){')
    html=once(html,"'mesh.add':[['op','kind'],['name','position','rotation','scale','color','material']],",
        "'mesh.add':[['op','kind'],['name','position','rotation','scale','color','material','path','radii','profile','arcStart','arcLength','segments']],")
    html=once(html,"'editor.undo':[['op'],[]],'editor.redo':[['op'],[]]", "'editor.undo':[['op'],[]],'editor.redo':[['op'],[]],'editor.frame':[['op'],['view']]")
    html=once(html,"if(ctx.mode!=='edit')throw Error('STOP_PLAY_BEFORE_EDITING');",
        "if(ctx.mode!=='edit')throw Error('STOP_PLAY_BEFORE_EDITING');if(op.op==='editor.frame'&&(ctx.workspace!=='model-atelier'||Object.hasOwn(op,'view')&&!['front','back','left','right','three','hero','top','bottom'].includes(op.view)))throw Error('INVALID_FRAME_VIEW');")
    html=once(html,"if(op.op==='mesh.add'&&!KINDS.has(op.kind)||op.op==='sceneactor.add'&&!PREFABS.has(op.prefab))throw Error('INVALID_PRIMITIVE');",
        "if(op.op==='mesh.add'&&!KINDS.has(op.kind)||op.op==='sceneactor.add'&&!PREFABS.has(op.prefab))throw Error('INVALID_PRIMITIVE');if(op.op==='mesh.add')se293ShapeData(op);")
    start=html.index('async function applyBatch(payload){')
    end=html.index('async function receive(message){',start)
    html=html[:start]+section(source,'HOST')+'\n'+html[end:]
    prev=" source.engine='§wyrl§ Engine · Maker v11.292';source.version=11.292;"
    assert html.count(prev)==3,('v11.293 provenance',html.count(prev))
    html=html.replace(prev," source.engine='§wyrl§ Engine · Maker v11.293';source.version=11.293;")
    for old,new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_292_CLIFF_WRIST_MOSS_KNUCKLES','SWYRL_ENGINE_DEPLOY_MARKER: V11_293_CHAT_CHARACTER_TOOLS'),
        ('ENGINE · MAKER v11.292','ENGINE · MAKER v11.293'),
        ('v11.292 · wrist-only moss and texture-mapped rock knuckles','v11.293 · Chat native character tools and visible progress'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.292'","window.SWRLZ_FORGE_BUILD={version:'v11.293'"),
        ('<title>§wyrl§ Engine · Maker v11.292</title>','<title>§wyrl§ Engine · Maker v11.293</title>'),
    ):html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Chat builds editable native character surfaces with visible progress',date='2026-11-06',changes=[
        'Chat mesh tools v2 advertise bounded tapered lofts and partial lathe surfaces alongside the original four primitives; lathe results are normal saved editable topology meshes.',
        'Human-reviewed plans apply up to 64 typed operations with a visible paint between native edits and named progress backed by actual operation receipts.',
        'Closing Chat, changing project/workspace or editing during a batch stops subsequent operations; successful partial edits remain truthfully reported and undoable.',
        'Lease renewal continues during longer batches. Scratch models report their actual draft mesh context and restore their own Undo history.',
        'Existing Chat approval, host-only credentials, native persistence, materials, particles, games and single renderer remain in place. No model-generated scripts execute.',
        'Separate paired Chat deployment and owner device visual acceptance are required; generic geometry tools do not establish reference likeness or model-weight training.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
