"""§wyrl§ Engine v7.8: desktop docks + independent editor layers."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v7.8 token missing: "+old[:220])
    return s.replace(old,new,1)

def apply(html):
    s=html
    for a,b in {
      "V7_7_CANONICAL_GLITCH_DEN_PROJECT":"V7_8_LAYERS_DESKTOP_DOCKS",
      "Maker v7.7":"Maker v7.8","MAKER v7.7":"MAKER v7.8",
      "v7.7 · CANONICAL GLITCH DEN":"v7.8 · LAYERS + DESKTOP DOCKS",
      "version:'v7.7'":"version:'v7.8'",
      "version:'swyrl-engine-agent-v5.7'":"version:'swyrl-engine-agent-v5.8'",
      "engine:'§wyrl§ Engine · Maker v7.7'":"engine:'§wyrl§ Engine · Maker v7.8'",
      "version:7.7":"version:7.8",
    }.items(): s=_once(s,a,b)

    css=r"""
/* v7.8: usable desktop docks + independent object layers */
@media(min-width:721px){
  #hierarchy,#inspector{transition:width .16s ease,min-width .16s ease,opacity .12s ease}
  #hierarchy.desktop-collapsed,#inspector.desktop-collapsed{width:34px!important;min-width:34px!important;overflow:hidden!important}
  #hierarchy.desktop-collapsed>*:not(.desktop-dock-tab),#inspector.desktop-collapsed>*:not(.desktop-dock-tab){display:none!important}
  .desktop-dock-tab{position:sticky;top:0;z-index:12;width:100%;min-height:34px;border:0;border-bottom:1px solid #26394d;background:#0d1825;color:#a9c3da;font:800 11px system-ui;cursor:pointer}
  #hierarchy:not(.desktop-collapsed) .desktop-dock-tab:before{content:'◀  '}
  #inspector:not(.desktop-collapsed) .desktop-dock-tab:before{content:'▶  '}
  .desktop-collapsed .desktop-dock-tab{writing-mode:vertical-rl;min-height:150px;padding:10px 7px}
  .desktop-collapsed .desktop-dock-tab:before{content:'◆  '}
}
.layer-panel{border-bottom:1px solid #25384a;background:#0a1420}
.layer-head{display:flex;align-items:center;gap:6px;padding:7px 8px}.layer-head b{font-size:10px;letter-spacing:.08em;color:#829bb2;margin-right:auto}.layer-head button{padding:4px 7px;font-size:10px}
.layer-list{max-height:150px;overflow:auto;padding:0 6px 6px}
.layer-row{display:grid;grid-template-columns:26px minmax(0,1fr) auto;gap:5px;align-items:center;padding:4px;border-radius:6px;font-size:10px;color:#b8c9d8}
.layer-row.active{background:#20344a}.layer-row button{padding:3px 5px;min-width:0}.layer-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;cursor:pointer}.layer-count{color:#70879d}
.tree-item.layer-hidden{opacity:.46}.tree-item.multi-selected{box-shadow:inset 3px 0 #a884ff}
"""
    s=_once(s,"</style>",css+"\n</style>")

    # Persist layer membership on each actor and project-level layer definitions.
    s=_once(s,
      "runtimeVelocity:[0,0,0], runtimeBaseY:null, role:opts.role||'', tags:[...(opts.tags||[])], visualColor:opts.visualColor||'', groupParentId:opts.groupParentId||null, groupChildIds:[...(opts.groupChildIds||[])]",
      "runtimeVelocity:[0,0,0], runtimeBaseY:null, role:opts.role||'', tags:[...(opts.tags||[])], visualColor:opts.visualColor||'', groupParentId:opts.groupParentId||null, groupChildIds:[...(opts.groupChildIds||[])], editorLayerIds:[...(opts.editorLayerIds||[])]"
    )
    s=_once(s,
      "id:a.userData.id, name:a.name, type:a.userData.actorType, team:a.userData.team, baked:a.userData.baked, role:a.userData.role||'', tags:[...(a.userData.tags||[])], visualColor:a.userData.visualColor||'', groupParentId:a.userData.groupParentId||null, groupChildIds:[...(a.userData.groupChildIds||[])],",
      "id:a.userData.id, name:a.name, type:a.userData.actorType, team:a.userData.team, baked:a.userData.baked, role:a.userData.role||'', tags:[...(a.userData.tags||[])], visualColor:a.userData.visualColor||'', groupParentId:a.userData.groupParentId||null, groupChildIds:[...(a.userData.groupChildIds||[])], editorLayerIds:[...(a.userData.editorLayerIds||[])],"
    )
    s=_once(s,
      "if(d.id)o.userData.id=d.id;o.userData.groupParentId=d.groupParentId||null;o.userData.groupChildIds=[...(d.groupChildIds||[])];",
      "if(d.id)o.userData.id=d.id;o.userData.groupParentId=d.groupParentId||null;o.userData.groupChildIds=[...(d.groupChildIds||[])];o.userData.editorLayerIds=[...(d.editorLayerIds||[])];"
    )
    s=_once(s,
      "let selected = null;\nlet multiSelected=[];let multiSelectMode=false;",
      "let selected = null;\nlet multiSelected=[];let multiSelectMode=false;\nlet editorLayers=[];let activeEditorLayerId=null;"
    )
    s=_once(s,
      "project:{...currentProject},\n    editor:{transformSpace,snapEnabled,terrainSnapEnabled,viewMode,cameraView:editorCameraView,revision},",
      "project:{...currentProject},\n    editor:{transformSpace,snapEnabled,terrainSnapEnabled,viewMode,cameraView:editorCameraView,revision,layers:editorLayers.map(x=>({...x})),activeLayerId:activeEditorLayerId},"
    )
    s=_once(s,
      "clearAll();applyProjectMeta(p.project||inferProjectMeta(p));",
      "clearAll();applyProjectMeta(p.project||inferProjectMeta(p));editorLayers=(p.editor?.layers||[]).map(x=>({...x}));activeEditorLayerId=p.editor?.activeLayerId||editorLayers[0]?.id||null;"
    )

    js=r"""
function selectedRoots(){return [...new Set((multiSelected.length?multiSelected:(selected?[selected]:[])).map(rootGroupFor).filter(Boolean))]}
function layerById(id){return editorLayers.find(x=>x.id===id)||null}
function actorInLayer(a,id){return !!a&&(a.userData.editorLayerIds||[]).includes(id)}
function applyLayerVisibility(){
  for(const a of actors){
    const hidden=(a.userData.editorLayerIds||[]).some(id=>layerById(id)?.visible===false);
    a.userData.layerHidden=hidden;
    a.visible=!hidden && a.userData.manualVisible!==false;
  }
  rebuildHierarchy();
}
function createEditorLayer(name){
  const n=(name||prompt('Layer name','Layer '+(editorLayers.length+1))||'').trim();if(!n)return null;
  const l={id:'layer-'+uid(),name:n,visible:true};editorLayers.push(l);activeEditorLayerId=l.id;renderLayerPanel();markDirty?.();return l;
}
function addSelectionToLayer(id=activeEditorLayerId){
  const l=layerById(id);const roots=selectedRoots();if(!l||!roots.length){toast('Select objects and a layer first');return}
  beginTransaction('Add '+roots.length+' object(s) to '+l.name);
  for(const a of roots){const tree=a.userData.actorType==='group'?[a,...groupDescendants(a)]:[a];for(const x of tree)x.userData.editorLayerIds=[...new Set([...(x.userData.editorLayerIds||[]),id])]}
  commitTransaction('Layer '+l.name);renderLayerPanel();rebuildHierarchy();toast(roots.length+' object(s) → '+l.name);
}
function removeSelectionFromLayer(id=activeEditorLayerId){
  const l=layerById(id);if(!l)return;beginTransaction('Remove from '+l.name);
  for(const a of selectedRoots()){const tree=a.userData.actorType==='group'?[a,...groupDescendants(a)]:[a];for(const x of tree)x.userData.editorLayerIds=(x.userData.editorLayerIds||[]).filter(v=>v!==id)}
  commitTransaction('Remove from '+l.name);renderLayerPanel();rebuildHierarchy();
}
function toggleEditorLayer(id){
  const l=layerById(id);if(!l)return;l.visible=l.visible===false?true:false;applyLayerVisibility();renderLayerPanel();markDirty?.();
}
function deleteEditorLayer(id){
  const l=layerById(id);if(!l)return;if(!confirm('Delete layer "'+l.name+'"? Objects will remain in the scene.'))return;
  editorLayers=editorLayers.filter(x=>x.id!==id);for(const a of actors)a.userData.editorLayerIds=(a.userData.editorLayerIds||[]).filter(x=>x!==id);
  if(activeEditorLayerId===id)activeEditorLayerId=editorLayers[0]?.id||null;applyLayerVisibility();renderLayerPanel();markDirty?.();
}
function renderLayerPanel(){
  const list=$('editorLayerList');if(!list)return;list.innerHTML='';
  for(const l of editorLayers){const row=document.createElement('div');row.className='layer-row'+(l.id===activeEditorLayerId?' active':'');const count=actors.filter(a=>actorInLayer(a,l.id)).length;
    row.innerHTML='<button class="layer-eye">'+(l.visible===false?'○':'◉')+'</button><span class="layer-name"></span><span class="layer-count">'+count+'</span>';
    row.querySelector('.layer-name').textContent=l.name;row.querySelector('.layer-name').onclick=()=>{activeEditorLayerId=l.id;renderLayerPanel()};
    row.querySelector('.layer-eye').onclick=()=>toggleEditorLayer(l.id);row.ondblclick=()=>{const n=prompt('Rename layer',l.name);if(n?.trim()){l.name=n.trim();renderLayerPanel();markDirty?.()}};
    list.appendChild(row);
  }
}
function installLayerPanel(){
  if($('editorLayerPanel'))return;const h=$('hierarchy');if(!h)return;
  const p=document.createElement('section');p.id='editorLayerPanel';p.className='layer-panel';p.innerHTML='<div class="layer-head"><b>LAYERS</b><button id="layerNew">+ Layer</button><button id="layerAdd">+ Selected</button><button id="layerRemove">− Selected</button><button id="layerDelete">Delete</button></div><div id="editorLayerList" class="layer-list"></div>';
  h.insertBefore(p,h.firstChild);$('layerNew').onclick=()=>createEditorLayer();$('layerAdd').onclick=()=>addSelectionToLayer();$('layerRemove').onclick=()=>removeSelectionFromLayer();$('layerDelete').onclick=()=>deleteEditorLayer(activeEditorLayerId);renderLayerPanel();
}
function installDesktopDockTabs(){
  for(const [id,label] of [['hierarchy','Outliner'],['inspector','Details']]){const p=$(id);if(!p||p.querySelector('.desktop-dock-tab'))continue;const b=document.createElement('button');b.className='desktop-dock-tab';b.textContent=label;b.title='Collapse / expand '+label;b.onclick=()=>p.classList.toggle('desktop-collapsed');p.insertBefore(b,p.firstChild)}
}
installLayerPanel();installDesktopDockTabs();
"""
    s=_once(s,"polishDesktopEditorChrome();","polishDesktopEditorChrome();\n"+js)

    # Individual visibility must coexist with layer visibility.
    s=_once(s,
      "row.querySelector('.eye-btn').onclick=(e)=>{e.stopPropagation();a.visible=a.visible===false?true:false;commitTransaction('Toggle visibility '+a.name);rebuildHierarchy();};",
      "row.classList.toggle('layer-hidden',!!a.userData.layerHidden);row.querySelector('.eye-btn').onclick=(e)=>{e.stopPropagation();a.userData.manualVisible=a.userData.manualVisible===false?true:false;a.visible=a.userData.manualVisible!==false&&!a.userData.layerHidden;commitTransaction('Toggle visibility '+a.name);rebuildHierarchy();};"
    )

    # Keep the layer panel fresh after project loads and canonical boot.
    s=_once(s,
      "restoreActorGroups();setRuntimeShellVisibility(playing);\n  rebuildHierarchy();",
      "restoreActorGroups();setRuntimeShellVisibility(playing);applyLayerVisibility();renderLayerPanel();\n  rebuildHierarchy();"
    )
    s=s.replace("editorLog('§wyrl§ Engine v7.7 initialized · canonical Moonfire Sanctum starter','ok')","editorLog('§wyrl§ Engine v7.8 initialized · multi-object layers · collapsible desktop docks','ok')",1)
    return s
