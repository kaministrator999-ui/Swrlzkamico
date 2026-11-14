"""§E v11.444: reachable native Delete Selected on phone, desktop and VR."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_444_DELETE_SELECTED'

def once(html,old,new):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.444 anchor',old[:130],count))
    return html.replace(old,new,1)

def apply(html):
    native="""  // Delete whole objects, not selected vertices/faces. The canonical
  // checkpoint includes the full model envelope (assemblies and meshGroups).
  function deleteSelectedObjects(){
    const data=model();
    if(!data)return {ok:false,reason:'Open a Model Studio project first.'};
    if(atelierComponentMode!=='mesh'){
      status('Switch to Object mode to delete complete meshes.',true);
      return {ok:false,reason:'Switch to Object mode first.'};
    }
    if(se340ModelBridge.inspect().gesture||se350ModelTools.inspect().gesture||
       se430ModelWorkshop.inspect().preview.active){
      status('Finish or cancel the current mesh edit before deleting.',true);
      return {ok:false,reason:'An edit is in progress.'};
    }
    const ids=[...new Set((atelierMeshIds||[]).filter(id=>!!partById(id)))];
    if(!ids.length&&partById(selection))ids.push(selection);
    if(!ids.length){
      status('Select at least one mesh to delete.',true);
      return {ok:false,reason:'No meshes selected.'};
    }
    if(ids.length>=data.parts.length){
      status('Keep at least one mesh in the model.',true);
      return {ok:false,reason:'Cannot delete every mesh.'};
    }
    // Exactly one Undo checkpoint for the entire selected set.
    checkpoint();
    const removing=new Set(ids);
    data.parts=data.parts.filter(part=>!removing.has(part.id));
    selection=null;atelierMeshIds=[];atelierMeshAdding=false;atelierGroupCurrent=null;
    atelierComponentIds=[];atelierComponentPartId=null;
    signalEdited(); // owns mesh-group pruning, render, inspector and dirty state.
    status('Deleted '+ids.length+' selected mesh'+(ids.length===1?'':'es')+'. Use Undo to restore.');
    return {ok:true,changed:true,deletedCount:ids.length};
  }
"""
    at=html.index('  function removePart(){')
    at=html.index('  function cameraUpdate(){',at)
    html=html[:at]+native+html[at:]
    html=once(html,'vrAccessory:se410ModelAccessory,workshop:se430ModelWorkshop,',
             'vrAccessory:se410ModelAccessory,deleteSelected:deleteSelectedObjects,workshop:se430ModelWorkshop,')
    # A persistent, full-sized touch target next to selection summary / tools.
    html=once(html,
        " strip.querySelector('#se430ContextTools').addEventListener('click',()=>{",
        """ const deleteSelected=document.createElement('button');
 deleteSelected.type='button';deleteSelected.id='se444DeleteSelected';
 deleteSelected.textContent='Delete selected';deleteSelected.disabled=true;
 deleteSelected.setAttribute('aria-label','Delete selected whole mesh objects');
 deleteSelected.addEventListener('click',()=>{
  ModelAtelier.deleteSelected();se430BeginnerQueue();
 });
 strip.querySelector('#se430ContextTools').after(deleteSelected);
 strip.querySelector('#se430ContextTools').addEventListener('click',()=>{""")
    html=once(html,
        " const modes=p.querySelector('#seAtelierModes');if(modes)modes.setAttribute('aria-label',",
        """ const deleteButton=p.querySelector('#se444DeleteSelected');
 if(deleteButton){
  const canDelete=selection.mode==='mesh'&&!preview.active&&objectCount>0&&
   objectCount<(ModelAtelier.status()?.count||0);
  deleteButton.disabled=!canDelete;
  deleteButton.title=canDelete?'Delete '+objectCount+' selected object(s) · Undo restores':
   selection.mode!=='mesh'?'Switch to Object mode to delete whole meshes.':
   preview.active?'Apply or cancel your preview first.':'Select meshes, leaving at least one in the model.';
 }
 const modes=p.querySelector('#seAtelierModes');if(modes)modes.setAttribute('aria-label',""")
    # One permanent VR rail button, no additional floating dialog or tool panel.
    html=once(html,
        "['manual-mesh','Mesh edit','manual-mesh'],['objects','Objects','objects'],['views','Display','views'],['projects','Projects','projects']",
        "['manual-mesh','Mesh edit','manual-mesh'],['objects','Objects','objects'],['views','Display','views'],['projects','Projects','projects'],['delete-selected','Delete',null]")
    html=once(html,
        "const [action,label,page]=entries[i],y=.305-i*.054;",
        "const [action,label,page]=entries[i],y=.305-i*.050;")
    # Give the small VR row a recognisable destructive icon.
    html=once(html,
        "if(id==='draw-clear'||id==='selection-clear')return 'clear';",
        "if(id==='draw-clear'||id==='selection-clear'||id==='delete-selected')return 'clear';")
    html=once(html,'installPerformanceSettings();se189InstallPerfUI();',
        (ROOT/'runtime/model_delete_selected_v11_444.js').read_text(encoding='utf-8')+
        '\ninstallPerformanceSettings();se189InstallPerfUI();')
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_443_VR_VERTICAL_TOOL_DOCK',MARKER),
      ('ENGINE · MAKER v11.443','ENGINE · MAKER v11.444'),
      ('v11.443 · VR vertical tool dock and slide-out settings','v11.444 · delete selected meshes everywhere'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.443'","window.SWRLZ_FORGE_BUILD={version:'v11.444'"),
      ('<title>§wyrl§ Engine · Maker v11.443</title>','<title>§wyrl§ Engine · Maker v11.444</title>')
    ]:html=once(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.443';source.version=11.443;"
    assert html.count(old)==5,('v11.444 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.444';source.version=11.444;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.443']
    notes['history'].insert(0,{'version':'v11.443','changes':notes.get('changes',[])})
    notes.update(version='v11.444',date='2026-11-14',
        title='Delete Selected from any Model Studio workspace',
        changes=[
        'A persistent Delete selected button sits beside the object selection context on phone and desktop, while the VR vertical tool dock always shows Delete without opening a second panel.',
        'Delete Selected removes one or many selected native meshes as one undoable edit, preserving unselected meshes, project data, and supported mesh group membership.',
        'VR uses a second Trigger on the same Delete control to confirm the unchanged selection; active transforms/previews and removing every mesh are blocked.',
        'Selection, controller action routing, Save, Undo/Redo and existing Model Studio menus retain their original ownership and behavior.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
