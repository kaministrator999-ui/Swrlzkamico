"""Keep editor layers, authored visibility and runtime shells independent."""


def _once(source, before, after):
    if before not in source:
        raise RuntimeError("v8.0 layer integrity token missing: " + before[:180])
    return source.replace(before, after, 1)


def apply(html):
    s = html
    s = _once(
        s,
        "editorLayerIds:[...(opts.editorLayerIds||[])]",
        "editorLayerIds:[...(opts.editorLayerIds||[])], manualVisible:opts.manualVisible!==false",
    )
    s = _once(
        s,
        "function setRuntimeShellVisibility(runtime){\n  for(const a of actors.filter(x=>(x.userData.tags||[]).includes('runtime-shell')))a.visible=!!runtime;\n}",
        """function syncActorVisibility(a){
  const hidden=(a.userData.editorLayerIds||[]).some(id=>layerById(id)?.visible===false);
  const runtimeShell=(a.userData.tags||[]).includes('runtime-shell');
  a.userData.layerHidden=hidden;
  a.visible=a.userData.manualVisible!==false && !hidden && (!runtimeShell || playing || simulating);
}
function setRuntimeShellVisibility(runtime){
  for(const a of actors.filter(x=>(x.userData.tags||[]).includes('runtime-shell')))syncActorVisibility(a);
}""",
    )
    s = _once(
        s,
        "visible:(a.userData.tags||[]).includes('runtime-shell')?true:a.visible!==false",
        "manualVisible:a.userData.manualVisible!==false, visible:a.userData.manualVisible!==false",
    )
    s = _once(
        s,
        "o.userData.visualColor=d.visualColor||o.userData.visualColor||''; o.visible=d.visible!==false;",
        """o.userData.visualColor=d.visualColor||o.userData.visualColor||'';
  // Older saves conflated layer/runtime hiding with an actor's authored visibility.
  const legacyDerivedHide=(d.tags||[]).includes('runtime-shell') || (d.editorLayerIds||[]).some(id=>layerById(id)?.visible===false);
  o.userData.manualVisible=d.manualVisible===undefined?(legacyDerivedHide || d.visible!==false):d.manualVisible!==false;
  syncActorVisibility(o);""",
    )
    s = _once(
        s,
        "row.classList.toggle('layer-hidden',!!a.userData.layerHidden);row.querySelector('.eye-btn').onclick=(e)=>{e.stopPropagation();a.userData.manualVisible=a.userData.manualVisible===false?true:false;a.visible=a.userData.manualVisible!==false&&!a.userData.layerHidden;commitTransaction('Toggle visibility '+a.name);rebuildHierarchy();};",
        "row.classList.toggle('layer-hidden',!!a.userData.layerHidden);row.querySelector('.eye-btn').onclick=(e)=>{e.stopPropagation();beginTransaction('Toggle visibility '+a.name);a.userData.manualVisible=a.userData.manualVisible===false?true:false;applyLayerVisibility();commitTransaction('Toggle visibility '+a.name);};",
    )

    start = s.index("function selectedRoots(){")
    end = s.index("function installLayerPanel(){", start)
    s = s[:start] + r"""function selectedRoots(){return [...new Set((multiSelected.length?multiSelected:(selected?[selected]:[])).map(rootGroupFor).filter(Boolean))]}
function layerById(id){return editorLayers.find(x=>x.id===id)||null}
function actorInLayer(a,id){return !!a&&(a.userData.editorLayerIds||[]).includes(id)}
function applyLayerVisibility(){
  for(const a of actors)syncActorVisibility(a);
  rebuildHierarchy();
}
function finishLayerTransaction(label){
  applyLayerVisibility();renderLayerPanel();commitTransaction(label);
}
function createEditorLayer(name){
  const value=name==null?prompt('Layer name','Layer '+(editorLayers.length+1)):String(name);
  const n=(value||'').trim();if(!n)return null;
  beginTransaction('Create layer '+n);
  const l={id:'layer-'+uid(),name:n,visible:true};editorLayers.push(l);activeEditorLayerId=l.id;
  finishLayerTransaction('Create layer '+n);return {...l};
}
function assignActorsToEditorLayer(ids,id,options={}){
  const l=layerById(id);if(!l)return 0;
  const requested=[...new Set((ids||[]).map(actorId=>actors.find(a=>a.userData.id===actorId)).filter(Boolean))];
  const tree=[...new Set(requested.flatMap(a=>a.userData.actorType==='group' && options.includeDescendants!==false?[a,...groupDescendants(a)]:[a]))];
  if(!tree.length)return 0;
  const action=options.remove?'Remove from':'Assign to';beginTransaction(action+' layer '+l.name);
  let changed=0;
  for(const a of tree){
    const before=a.userData.editorLayerIds||[];
    const after=options.remove?before.filter(layerId=>layerId!==id):options.replace?[id]:[...new Set([...before,id])];
    if(JSON.stringify(before)!==JSON.stringify(after)){a.userData.editorLayerIds=after;changed++;}
  }
  finishLayerTransaction(action+' layer '+l.name);return changed;
}
function addSelectionToLayer(id=activeEditorLayerId){
  const l=layerById(id);const roots=selectedRoots();if(!l||!roots.length){toast('Select objects and a layer first');return}
  assignActorsToEditorLayer(roots.map(a=>a.userData.id),id);
  toast(roots.length+' object(s) → '+l.name);
}
function removeSelectionFromLayer(id=activeEditorLayerId){
  return assignActorsToEditorLayer(selectedRoots().map(a=>a.userData.id),id,{remove:true});
}
function setEditorLayerVisibility(id,visible){
  const l=layerById(id);if(!l)return false;
  const value=visible!==false;if(l.visible===value)return true;
  beginTransaction((value?'Show':'Hide')+' layer '+l.name);l.visible=value;
  finishLayerTransaction((value?'Show':'Hide')+' layer '+l.name);return true;
}
function toggleEditorLayer(id){const l=layerById(id);return l?setEditorLayerVisibility(id,l.visible===false):false}
function renameEditorLayer(id,name){
  const l=layerById(id);const n=String(name||'').trim();if(!l||!n)return false;if(l.name===n)return true;
  beginTransaction('Rename layer '+l.name);l.name=n;finishLayerTransaction('Rename layer '+n);return true;
}
function deleteEditorLayer(id){
  const l=layerById(id);if(!l)return false;if(!confirm('Delete layer "'+l.name+'"? Objects will remain in the scene.'))return false;
  beginTransaction('Delete layer '+l.name);
  editorLayers=editorLayers.filter(x=>x.id!==id);for(const a of actors)a.userData.editorLayerIds=(a.userData.editorLayerIds||[]).filter(x=>x!==id);
  if(activeEditorLayerId===id)activeEditorLayerId=editorLayers[0]?.id||null;
  finishLayerTransaction('Delete layer '+l.name);return true;
}
function renderLayerPanel(){
  const list=$('editorLayerList');if(!list)return;list.innerHTML='';
  for(const l of editorLayers){const row=document.createElement('div');row.className='layer-row'+(l.id===activeEditorLayerId?' active':'');const count=actors.filter(a=>actorInLayer(a,l.id)).length;
    row.innerHTML='<button class="layer-eye">'+(l.visible===false?'○':'◉')+'</button><span class="layer-name"></span><span class="layer-count">'+count+'</span>';
    row.querySelector('.layer-name').textContent=l.name;row.querySelector('.layer-name').onclick=()=>{activeEditorLayerId=l.id;renderLayerPanel()};
    row.querySelector('.layer-eye').onclick=()=>toggleEditorLayer(l.id);row.ondblclick=()=>{const n=prompt('Rename layer',l.name);if(n?.trim())renameEditorLayer(l.id,n)};
    list.appendChild(row);
  }
}
""" + s[end:]

    s = _once(
        s,
        "function beginRuntimeComponents(){\n  for(const a of actors){a.userData.runtimeBaseY=a.position.y;a.userData.runtimeVelocity=[0,0,0];a.userData._launchCooldown=0;}\n}",
        "function beginRuntimeComponents(){\n  for(const a of actors){a.userData.runtimeBaseY=a.position.y;a.userData.runtimeVelocity=[0,0,0];a.userData._launchCooldown=0;}\n  applyLayerVisibility();\n}",
    )
    s = _once(
        s,
        "playing=false;simulating=false;paused=false;restorePlaySnapshot();",
        "playing=false;simulating=false;paused=false;restorePlaySnapshot();applyLayerVisibility();",
    )
    s = _once(
        s,
        "const h=heroActor();setHeroBodyVisible(h,true);setRuntimeShellVisibility(false);",
        "for(const h of actors.filter(a=>a.userData.actorType==='hero'))setHeroBodyVisible(h,true);setRuntimeShellVisibility(false);",
    )
    s = _once(
        s,
        "  inspectScene:()=>projectData(),",
        """  inspectScene:()=>projectData(),
  createLayer:(name)=>createEditorLayer(name),
  listLayers:()=>editorLayers.map(l=>({...l,actorCount:actors.filter(a=>actorInLayer(a,l.id)).length})),
  setLayerVisibility:(id,visible)=>setEditorLayerVisibility(id,visible),
  assignActorsToLayer:(ids,id,options={})=>assignActorsToEditorLayer(ids,id,options),""",
    )
    return s
