"""§wyrl§ Engine v5.3: object grouping + improved immersive Dragon's Den."""
from __future__ import annotations

def _once(s: str, old: str, new: str) -> str:
    if old not in s:
        raise RuntimeError("v5.3 patch token missing: " + old[:180])
    return s.replace(old, new, 1)

def _before(s: str, marker: str, block: str) -> str:
    i=s.find(marker)
    if i<0: raise RuntimeError("v5.3 insert marker missing: "+marker[:180])
    return s[:i]+block+s[i:]

def _replace_block(s: str, start: str, end: str, block: str) -> str:
    a=s.find(start)
    if a<0: raise RuntimeError("v5.3 block start missing: "+start[:180])
    b=s.find(end,a)
    if b<0: raise RuntimeError("v5.3 block end missing: "+end[:180])
    return s[:a]+block+s[b:]

def apply(html: str) -> str:
    s=html

    repl={
      "<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_2_FIRST_PERSON_TWIN_STICK -->":
        "<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_3_GROUPS_IMMERSIVE_DEN -->",
      "<title>§wyrl§ Engine · Maker v5.2</title>":
        "<title>§wyrl§ Engine · Maker v5.3</title>",
      '<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.2</div>':
        '<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.3</div>',
      '<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.2 · FIRST PERSON</div>':
        '<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.3 · GROUPS + DEN</div>',
      "window.SWRLZ_FORGE_BUILD={version:'v5.2',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;":
        "window.SWRLZ_FORGE_BUILD={version:'v5.3',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick',grouping:'hierarchical'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;",
      "version:'swyrl-engine-agent-v3.2',":"version:'swyrl-engine-agent-v3.3',",
      "editorLog('§wyrl§ Engine v5.2 initialized · first-person PIE · twin-stick mobile controls','ok')":
        "editorLog('§wyrl§ Engine v5.3 initialized · hierarchical groups · immersive Den pass','ok')",
      "engine:'§wyrl§ Engine · Maker v5.1',":"engine:'§wyrl§ Engine · Maker v5.3',",
      "version:5.1,":"version:5.3,",
    }
    for a,b in repl.items(): s=_once(s,a,b)

    # Grouping controls are first-class editor operations.
    s=_once(
      s,
      '    <button id="scaleBtn">Scale</button>\n    <button id="spaceBtn">World</button>',
      '    <button id="scaleBtn">Scale</button>\n    <button id="spaceBtn">World</button>\n    <button id="multiSelectBtn" title="Toggle multi-select">Multi</button>\n    <button id="groupBtn" title="Group selected objects (Ctrl+G)">Group</button>\n    <button id="ungroupBtn" title="Ungroup selected group (Ctrl+Shift+G)">Ungroup</button>'
    )
    s=_once(
      s,
      '<div class="outliner-tools"><input id="outlinerSearch" placeholder="Search actors…"></div>',
      '<div class="outliner-tools"><input id="outlinerSearch" placeholder="Search actors…"><button id="outlinerMultiBtn" title="Multi-select">＋</button></div>'
    )
    s=_once(
      s,
      '<div class="inspector-actions"><button id="focusBtn">Focus</button><button id="snapGroundBtn">Snap Ground</button><button id="duplicateBtn">Duplicate Ghost</button><button id="deleteBtn" class="danger">Delete</button><button id="playFromHereBtn">Play From Here</button></div>',
      '<div class="inspector-actions"><button id="focusBtn">Focus</button><button id="snapGroundBtn">Snap Ground</button><button id="groupInspectorBtn">Group Selection</button><button id="ungroupInspectorBtn">Ungroup</button><button id="duplicateBtn">Duplicate Ghost</button><button id="deleteBtn" class="danger">Delete</button><button id="playFromHereBtn">Play From Here</button></div>'
    )

    css=r"""
.tree-item.multi-selected{background:#55478866;outline:1px solid #9a8cff55}.tree-item.group-root .tree-name{font-weight:800}.tree-item.group-root:after{content:attr(data-parts);margin-left:auto;font-size:10px;color:#b9a8ff}
#multiSelectBtn.active,#outlinerMultiBtn.active{border-color:#a884ff;background:#352b59;color:#e8ddff}
.outliner-tools{display:flex;gap:6px}.outliner-tools input{min-width:0;flex:1}.outliner-tools button{padding:6px 9px}
.group-help{color:#9aacc2;font-size:10px;margin:6px 0 0}
"""
    s=_once(s,"</style>",css+"\n</style>")

    # Selection state.
    s=_once(
      s,
      "let selected = null;\nlet playing = false;",
      "let selected = null;\nlet multiSelected=[];let multiSelectMode=false;\nlet playing = false;"
    )

    # Generic group type.
    s=_once(
      s,
      "if(type==='ground') return 'Environment/Terrain';\n  return 'World';",
      "if(type==='ground') return 'Environment/Terrain';\n  if(type==='group') return 'World/Groups';\n  return 'World';"
    )
    s=_once(
      s,
      "if(type==='hero') c.push('CharacterMovement');\n  return c;",
      "if(type==='hero') c.push('CharacterMovement');\n  if(type==='group') c.push('Group');\n  return c;"
    )
    s=_once(
      s,
      "return {ground:'▱', tower:'🏰', base:'💎', spawner:'⚔', camp:'👹', bush:'🌿', wall:'🧱', rock:'🪨', hero:'🦸', tree:'🌲', dragon:'🐉', crystal:'🔮', portal:'🌀', throne:'♛', pedestal:'◉', denStructure:'▰'}[type] || '◆';",
      "return {ground:'▱', tower:'🏰', base:'💎', spawner:'⚔', camp:'👹', bush:'🌿', wall:'🧱', rock:'🪨', hero:'🦸', tree:'🌲', dragon:'🐉', crystal:'🔮', portal:'🌀', throne:'♛', pedestal:'◉', denStructure:'▰', group:'▣'}[type] || '◆';"
    )
    s=_once(
      s,
      "runtimeVelocity:[0,0,0], runtimeBaseY:null, role:opts.role||'', tags:[...(opts.tags||[])], visualColor:opts.visualColor||''",
      "runtimeVelocity:[0,0,0], runtimeBaseY:null, role:opts.role||'', tags:[...(opts.tags||[])], visualColor:opts.visualColor||'', groupParentId:opts.groupParentId||null, groupChildIds:[...(opts.groupChildIds||[])]"
    )

    grouping=r"""
function rootGroupFor(a){
  if(!a)return null;
  let cur=a,guard=0;
  while(cur?.userData?.groupParentId&&guard++<24){
    const p=actors.find(x=>x.userData.id===cur.userData.groupParentId);
    if(!p)break;cur=p;
  }
  return cur;
}
function groupChildren(g){return actors.filter(a=>a.userData.groupParentId===g?.userData?.id);}
function groupDescendants(g){
  const out=[];const visit=x=>{for(const c of groupChildren(x)){out.push(c);if(c.userData.actorType==='group')visit(c);}};visit(g);return out;
}
function makeGroupActor(name='Group',baked=true){
  const g=new THREE.Group();
  return markActor(g,'group',{name,baked,colliderRadius:0,folder:'World/Groups',components:['Transform','Scene','Group'],tags:['editor-group']});
}
function groupActors(members,name='Group',options={}){
  const record=options.record!==false,select=options.select!==false;
  const roots=[...new Set((members||[]).map(rootGroupFor).filter(Boolean))].filter(a=>a.userData.actorType!=='ground');
  if(roots.length<2){if(record)toast('Select at least two objects to group');return null;}
  if(record)beginTransaction('Group '+roots.length+' objects');
  const center=new THREE.Vector3();
  for(const a of roots){const p=new THREE.Vector3();a.getWorldPosition(p);center.add(p);}
  center.multiplyScalar(1/roots.length);
  const g=makeGroupActor(name,roots.every(a=>a.userData.baked));
  g.position.copy(center);g.userData.folder=options.folder||'World/Groups';g.userData.role=options.role||'';g.userData.tags=[...(g.userData.tags||[]),...(options.tags||[])];
  for(const a of roots){g.attach(a);a.userData.groupParentId=g.userData.id;}
  g.userData.groupChildIds=roots.map(a=>a.userData.id);
  if(select){multiSelected=[g];selectActor(g);}
  if(record){commitTransaction('Grouped '+roots.length+' objects');toast(roots.length+' objects grouped');}
  else rebuildHierarchy();
  return g;
}
function ungroupActor(g,options={}){
  g=rootGroupFor(g);if(!g||g.userData.actorType!=='group'){if(options.record!==false)toast('Select a group to ungroup');return [];}
  const record=options.record!==false;if(record)beginTransaction('Ungroup '+g.name);
  const children=groupChildren(g);
  for(const c of children){scene.attach(c);c.userData.groupParentId=null;}
  g.parent?.remove(g);const i=actors.indexOf(g);if(i>=0)actors.splice(i,1);
  multiSelected=[...children];selected=children[0]||null;
  if(record){commitTransaction('Ungrouped '+g.name);toast('Ungrouped '+g.name);}
  selectActor(selected,{preserveMulti:true});rebuildHierarchy();return children;
}
function restoreActorGroups(){
  const byId=new Map(actors.map(a=>[a.userData.id,a]));
  for(const g of actors.filter(a=>a.userData.actorType==='group')){
    for(const id of g.userData.groupChildIds||[]){
      const child=byId.get(id);if(!child||child===g)continue;
      g.add(child);child.userData.groupParentId=g.userData.id;
    }
  }
}
function removeActorRecursive(a){
  if(!a)return;
  if(a.userData.actorType==='group')for(const c of [...groupChildren(a)])removeActorRecursive(c);
  a.parent?.remove(a);const i=actors.indexOf(a);if(i>=0)actors.splice(i,1);
}
function groupSelection(){
  const list=multiSelected.length>1?multiSelected:(selected?[selected]:[]);
  return groupActors(list,'Group '+Math.max(1,actors.filter(a=>a.userData.actorType==='group').length+1));
}
function setMultiSelectMode(on){
  multiSelectMode=on===undefined?!multiSelectMode:!!on;
  $('multiSelectBtn')?.classList.toggle('active',multiSelectMode);$('outlinerMultiBtn')?.classList.toggle('active',multiSelectMode);
  toast('Multi-select '+(multiSelectMode?'ON':'OFF'));
}
function worldPos(a,target=new THREE.Vector3()){return a.getWorldPosition(target);}
function worldColliderRadius(a){
  const ws=new THREE.Vector3();a.getWorldScale(ws);return (a.userData.colliderRadius||0.8)*Math.max(Math.abs(ws.x),Math.abs(ws.z));
}
function setRuntimeShellVisibility(runtime){
  for(const a of actors.filter(x=>(x.userData.tags||[]).includes('runtime-shell')))a.visible=!!runtime;
}
"""
    s=_before(s,"function makeTree(pos",grouping)

    # Cavern terrain should read as rock, not grass/river.
    terrain_old="""function terrainHeight(x,z){
  let y = 0.18*Math.sin(x*0.18) + 0.14*Math.cos(z*0.16);
  const ridgeA = Math.max(0, 1 - Math.hypot(x+8,z+8)/12) * 0.9;
  const ridgeB = Math.max(0, 1 - Math.hypot(x-8,z-8)/12) * 0.9;
  y += ridgeA + ridgeB;
  const riverBand = Math.max(0, 1 - riverDistance(x,z)/2.6);
  y -= riverBand * 0.95;
  return y;
}"""
    terrain_new="""function terrainHeight(x,z){
  if(currentProject?.environment==='dragon-den'){
    const bowl=Math.max(0,1-Math.hypot(x,z)/23);
    return -0.08 + 0.09*Math.sin(x*.18)*Math.cos(z*.15) - bowl*.10;
  }
  let y = 0.18*Math.sin(x*0.18) + 0.14*Math.cos(z*0.16);
  const ridgeA = Math.max(0, 1 - Math.hypot(x+8,z+8)/12) * 0.9;
  const ridgeB = Math.max(0, 1 - Math.hypot(x-8,z-8)/12) * 0.9;
  y += ridgeA + ridgeB;
  const riverBand = Math.max(0, 1 - riverDistance(x,z)/2.6);
  y -= riverBand * 0.95;
  return y;
}"""
    s=_once(s,terrain_old,terrain_new)

    terrain_color_old="""    const riverBand = Math.max(0, 1 - riverDistance(x,z)/3.0);
    const grass = new THREE.Color(COLORS.grass);
    const dirt = new THREE.Color(COLORS.dirt);
    const river = new THREE.Color(COLORS.river);
    let c = grass.clone().lerp(dirt, 0.25 + Math.max(0, y)*0.15);
    c = c.lerp(river, riverBand*0.7);
    colors.push(c.r, c.g, c.b);"""
    terrain_color_new="""    let c;
    if(currentProject?.environment==='dragon-den'){
      const caveA=new THREE.Color('#292631'),caveB=new THREE.Color('#3c3444'),rune=new THREE.Color('#4b3d61');
      const radial=Math.max(0,1-Math.hypot(x,z)/24);
      c=caveA.clone().lerp(caveB,.28+.18*Math.sin((x+z)*.16)).lerp(rune,radial*.10);
    }else{
      const riverBand = Math.max(0, 1 - riverDistance(x,z)/3.0);
      const grass = new THREE.Color(COLORS.grass);
      const dirt = new THREE.Color(COLORS.dirt);
      const river = new THREE.Color(COLORS.river);
      c = grass.clone().lerp(dirt, 0.25 + Math.max(0, y)*0.15);
      c = c.lerp(river, riverBand*0.7);
    }
    colors.push(c.r, c.g, c.b);"""
    s=_once(s,terrain_color_old,terrain_color_new)

    # Extend Den structural primitives with reusable slabs, pillars, and floor plates.
    s=_once(
      s,
      "  }else if(kind==='walkway'){\n    box(7.5,.25,2.5,concrete,0,.12,0);const stripe=box(6.8,.035,.16,arcane,0,.27,0);",
      "  }else if(kind==='slab'){\n    box(1,1,1,stone,0,.5,0);\n  }else if(kind==='floorPlate'){\n    box(1,.18,1,stone,0,.09,0);const inset=box(.86,.025,.86,arcane,0,.195,0);\n  }else if(kind==='pillar'){\n    const p=new THREE.Mesh(new THREE.CylinderGeometry(.62,.82,1,8),stone);p.position.y=.5;p.castShadow=p.receiveShadow=true;g.add(p);\n  }else if(kind==='walkway'){\n    box(7.5,.25,2.5,concrete,0,.12,0);const stripe=box(6.8,.035,.16,arcane,0,.27,0);"
    )

    # Outliner: grouped children collapse into one root object; multi-select is visible.
    outliner=r"""function rebuildHierarchy(){
  const h=$('hierarchy');h.innerHTML='';const q=($('outlinerSearch')?.value||'').trim().toLowerCase();
  const roots=actors.filter(a=>!a.userData.groupParentId),folders=new Map();
  const matches=(a)=>{
    const self=(a.name+' '+a.userData.actorType+' '+(a.userData.folder||'')).toLowerCase();
    if(!q||self.includes(q))return true;
    return a.userData.actorType==='group'&&groupDescendants(a).some(c=>(c.name+' '+c.userData.actorType+' '+(c.userData.folder||'')).toLowerCase().includes(q));
  };
  for(const a of roots){if(!matches(a))continue;const folder=a.userData.folder||'World';if(!folders.has(folder))folders.set(folder,[]);folders.get(folder).push(a);}
  for(const folder of [...folders.keys()].sort()){
    const list=folders.get(folder);const head=document.createElement('div');head.className='folder-row';head.innerHTML='<span>▾</span><span></span><span class="count"></span>';head.children[1].textContent=folder;head.querySelector('.count').textContent=list.length;h.appendChild(head);
    for(const a of list){
      const isMulti=multiSelected.includes(a),parts=a.userData.actorType==='group'?groupDescendants(a).length:0;
      const row=document.createElement('div');row.className='tree-item'+(a===selected?' selected':'')+(isMulti?' multi-selected':'')+(!a.userData.baked?' ghost':'')+(a.userData.actorType==='group'?' group-root':'');if(parts)row.dataset.parts=parts+' parts';
      row.innerHTML='<button class="eye-btn" title="Toggle visibility">'+(a.visible===false?'○':'◉')+'</button><span class="tree-icon">'+actorIcon(a.userData.actorType)+'</span><span class="tree-name"></span>';row.querySelector('.tree-name').textContent=a.name;
      row.querySelector('.eye-btn').onclick=(e)=>{e.stopPropagation();a.visible=a.visible===false?true:false;commitTransaction('Toggle visibility '+a.name);rebuildHierarchy();};
      row.onclick=(e)=>selectActor(a,{additive:multiSelectMode||e.shiftKey||e.ctrlKey||e.metaKey});h.appendChild(row);
    }
  }
  const rootsCount=roots.length;$('actorCount').textContent=rootsCount+' objects · '+actors.length+' parts';$('ghostCount').textContent=roots.filter(a=>!a.userData.baked).length+' ghosts';
}
"""
    s=_replace_block(s,"function rebuildHierarchy(){","function selectActor(o){",outliner)

    selection=r"""function selectActor(o,options={}){
  o=rootGroupFor(o);const additive=!!options.additive;
  if(options.preserveMulti){selected=o||null;}
  else if(additive&&o){
    if(multiSelected.includes(o)){multiSelected=multiSelected.filter(x=>x!==o);if(selected===o)selected=multiSelected.at(-1)||null;}
    else{multiSelected=[...multiSelected,o];selected=o;}
  }else{selected=o||null;multiSelected=selected?[selected]:[];}
  transform.detach();
  if(selectionBox){scene.remove(selectionBox);selectionBox.geometry?.dispose?.();selectionBox.material?.dispose?.();selectionBox=null;}
  if(selected&&!playing){transform.attach(selected);if(selected.userData.actorType!=='ground'){selectionBox=new THREE.BoxHelper(selected,0x9a8cff);selectionBox.userData.editorOnly=true;scene.add(selectionBox);}}
  rebuildHierarchy();
  if(!selected){$('inspector').classList.add('hidden');$('inspectorEmpty').classList.remove('hidden');$('selectionStatus').textContent='Nothing selected';if(window.innerWidth<=620&&$('mobileDrawer').dataset.mode==='inspector')fillMobileInspector();return;}
  $('inspector').classList.remove('hidden');$('inspectorEmpty').classList.add('hidden');$('selectionStatus').textContent=multiSelected.length>1?multiSelected.length+' objects selected':'Selected: '+selected.name;syncInspector();if(window.innerWidth<=620&&$('mobileDrawer').dataset.mode==='inspector')fillMobileInspector();
}
"""
    s=_replace_block(s,"function selectActor(o){","function renderComponents(){",selection)

    # Group / Ungroup buttons.
    controls=r"""
$('multiSelectBtn').onclick=()=>setMultiSelectMode();
$('outlinerMultiBtn').onclick=()=>setMultiSelectMode();
$('groupBtn').onclick=groupSelection;
$('groupInspectorBtn').onclick=groupSelection;
$('ungroupBtn').onclick=()=>ungroupActor(selected);
$('ungroupInspectorBtn').onclick=()=>ungroupActor(selected);
"""
    s=_before(s,"$('moveBtn').onclick",controls)

    # Delete groups recursively or multiple selected roots.
    delete_block=r"""function deleteSelected(){
  const roots=[...new Set((multiSelected.length?multiSelected:(selected?[selected]:[])).map(rootGroupFor).filter(Boolean))];
  if(!roots.length)return;beginTransaction('Delete '+roots.length+' object(s)');
  for(const a of roots)removeActorRecursive(a);
  selected=null;multiSelected=[];rebuildHierarchy();selectActor(null);refreshDebug();commitTransaction('Delete '+roots.length+' object(s)');
}
"""
    s=_replace_block(s,"function deleteSelected(){","$('deleteBtn').onclick",delete_block)

    # Duplicate grouped trees as grouped trees.
    dup_old="""$('duplicateBtn').onclick = ()=>{
  if(!selected) return;
  const d = actorData(selected);
  d.baked = false;
  d.position = [selected.position.x+1, selected.position.y, selected.position.z+1];
  d.name = selected.name + ' Copy';
  const o = fromData(d);
  if(o){ selectActor(o); rebuildHierarchy(); commitTransaction('Duplicate '+selected.name); toast('Duplicate created as ghost'); }
};"""
    dup_new="""$('duplicateBtn').onclick=()=>{
  if(!selected)return;beginTransaction('Duplicate '+selected.name);
  if(selected.userData.actorType==='group'){
    const tree=[selected,...groupDescendants(selected)],idMap=new Map(tree.map(a=>[a.userData.id,uid()])),datas=tree.map(actorData);
    for(const d of datas){d.id=idMap.get(d.id);if(d.groupParentId)d.groupParentId=idMap.get(d.groupParentId)||null;d.groupChildIds=(d.groupChildIds||[]).map(id=>idMap.get(id)||id);d.baked=false;if(d.type==='group'&&!d.groupParentId){d.position=[d.position[0]+1,d.position[1],d.position[2]+1];d.name+=' Copy';}}
    const created=datas.map(fromData).filter(Boolean);restoreActorGroups();const root=created.find(a=>a.userData.actorType==='group'&&!a.userData.groupParentId);if(root){selectActor(root);commitTransaction('Duplicate '+selected.name);toast('Grouped copy created as ghost');}
  }else{
    const d=actorData(selected);d.id=uid();d.groupParentId=null;d.baked=false;d.position=[selected.position.x+1,selected.position.y,selected.position.z+1];d.name=selected.name+' Copy';const o=fromData(d);if(o){selectActor(o);commitTransaction('Duplicate '+selected.name);toast('Duplicate created as ghost');}
  }
};"""
    s=_once(s,dup_old,dup_new)

    # Persist hierarchy IDs.
    s=_once(
      s,
      "name:a.name, type:a.userData.actorType, team:a.userData.team, baked:a.userData.baked, role:a.userData.role||'', tags:[...(a.userData.tags||[])], visualColor:a.userData.visualColor||'',",
      "id:a.userData.id, name:a.name, type:a.userData.actorType, team:a.userData.team, baked:a.userData.baked, role:a.userData.role||'', tags:[...(a.userData.tags||[])], visualColor:a.userData.visualColor||'', groupParentId:a.userData.groupParentId||null, groupChildIds:[...(a.userData.groupChildIds||[])],"
    )
    s=_once(
      s,
      "colliderRadius:a.userData.colliderRadius, mass:a.userData.mass, restitution:a.userData.restitution, componentSpeed:a.userData.componentSpeed, bobAmplitude:a.userData.bobAmplitude, launchStrength:a.userData.launchStrength, visible:a.visible!==false",
      "colliderRadius:a.userData.colliderRadius, mass:a.userData.mass, restitution:a.userData.restitution, componentSpeed:a.userData.componentSpeed, bobAmplitude:a.userData.bobAmplitude, launchStrength:a.userData.launchStrength, visible:(a.userData.tags||[]).includes('runtime-shell')?true:a.visible!==false"
    )
    s=_once(
      s,
      "  if(d.type==='denStructure') o = makeDenStructure((d.blueprintClass||'DEN_walkway').replace(/^DEN_/,''),[d.position[0],0,d.position[2]],d.baked!==false,d.name,d.visualColor||'#6f5b82');\n  if(!o) return null;",
      "  if(d.type==='denStructure') o = makeDenStructure((d.blueprintClass||'DEN_walkway').replace(/^DEN_/,''),[d.position[0],0,d.position[2]],d.baked!==false,d.name,d.visualColor||'#6f5b82');\n  if(d.type==='group') o=makeGroupActor(d.name||'Group',d.baked!==false);\n  if(!o) return null;"
    )
    s=_once(
      s,
      "  o.userData.maxHp = d.maxHp ?? o.userData.maxHp;",
      "  if(d.id)o.userData.id=d.id;o.userData.groupParentId=d.groupParentId||null;o.userData.groupChildIds=[...(d.groupChildIds||[])];\n  o.userData.maxHp = d.maxHp ?? o.userData.maxHp;"
    )
    s=_once(
      s,
      "  for(const d of p.scene.actors) fromData(d);\n  rebuildHierarchy();refreshDebug();selectActor(",
      "  for(const d of p.scene.actors) fromData(d);\n  restoreActorGroups();setRuntimeShellVisibility(playing);\n  rebuildHierarchy();refreshDebug();selectActor("
    )

    # Group-aware collision uses world transforms.
    collision_old="""function resolveCircleCollision(pos,radius,ignore=null){
  for(const b of blockerActors()){if(b===ignore)continue;const dx=pos.x-b.position.x,dz=pos.z-b.position.z,dist=Math.hypot(dx,dz),min=radius+(b.userData.colliderRadius||0.8);if(dist<min&&dist>0.0001){const push=min-dist;pos.x+=dx/dist*push;pos.z+=dz/dist*push;}}
}"""
    collision_new="""function resolveCircleCollision(pos,radius,ignore=null){
  const wp=new THREE.Vector3();
  for(const b of blockerActors()){if(b===ignore)continue;worldPos(b,wp);const dx=pos.x-wp.x,dz=pos.z-wp.z,dist=Math.hypot(dx,dz),min=radius+worldColliderRadius(b);if(dist<min&&dist>0.0001){const push=min-dist;pos.x+=dx/dist*push;pos.z+=dz/dist*push;}}
}"""
    s=_once(s,collision_old,collision_new)

    # Clicking a part selects its root group; Ctrl/Shift or Multi mode builds a selection basket.
    pointer_old="""    let o = hits[0].object;
    while(o.parent && !actors.includes(o)) o = o.parent;
    if(actors.includes(o)) selectActor(o);"""
    pointer_new="""    let o=hits[0].object;
    while(o.parent&&!actors.includes(o))o=o.parent;
    if(actors.includes(o))selectActor(rootGroupFor(o),{additive:multiSelectMode||e.shiftKey||e.ctrlKey||e.metaKey});"""
    s=_once(s,pointer_old,pointer_new)

    # Keyboard group shortcuts.
    s=_once(
      s,
      "if((e.ctrlKey||e.metaKey)&&(e.key.toLowerCase()==='y'||(e.shiftKey&&e.key.toLowerCase()==='z'))){e.preventDefault();restoreHistory(historyIndex+1);return;}\n  if(!playing){",
      "if((e.ctrlKey||e.metaKey)&&(e.key.toLowerCase()==='y'||(e.shiftKey&&e.key.toLowerCase()==='z'))){e.preventDefault();restoreHistory(historyIndex+1);return;}\n  if(!playing&&(e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='g'){e.preventDefault();if(e.shiftKey)ungroupActor(selected);else groupSelection();return;}\n  if(!playing){"
    )

    # Mobile tools expose grouping and multi-select.
    s=_once(
      s,
      '<button data-click="scaleBtn">Scale</button><button data-click="spaceBtn">World/Local</button><button data-click="terrainSnapBtn">Terrain Snap</button>',
      '<button data-click="scaleBtn">Scale</button><button data-click="spaceBtn">World/Local</button><button data-click="multiSelectBtn">Multi Select</button><button data-click="groupBtn">Group</button><button data-click="ungroupBtn">Ungroup</button><button data-click="terrainSnapBtn">Terrain Snap</button>'
    )
    s=_once(
      s,
      r'''d.innerHTML = '<div class="section-body"><h3 style="color:#94a5bb">Mobile Inspector</h3><div><b>'+selected.name+'</b></div><div class="hint">'+selected.userData.actorType+' · '+(selected.userData.baked?'Baked':'Ghost')+' · '+selected.userData.team+'</div><div class="hint" style="margin-top:10px">Move, rotate, or scale with the viewport gizmo. Use desktop/tablet width for the full numeric inspector.</div></div>';''',
      r'''d.innerHTML='<div class="section-body"><h3 style="color:#94a5bb">Mobile Inspector</h3><div><b>'+selected.name+'</b></div><div class="hint">'+selected.userData.actorType+' · '+(selected.userData.baked?'Baked':'Ghost')+' · '+selected.userData.team+'</div><div class="row" style="margin-top:10px"><button id="miMulti">Multi</button><button id="miGroup">Group</button><button id="miUngroup">Ungroup</button></div><div class="hint" style="margin-top:10px">Multi lets you tap several objects, then Group turns them into one transformable object.</div></div>';d.querySelector('#miMulti').onclick=()=>setMultiSelectMode();d.querySelector('#miGroup').onclick=groupSelection;d.querySelector('#miUngroup').onclick=()=>ungroupActor(selected);'''
    )

    # Better Den architecture: stone floor, grouped cavern shell, grouped vaulted roof, uncluttered editor.
    den_block=r"""function buildDragonsDenProject(){
  clearAll();applyProjectMeta({name:"Dragon's Den — Seed Chamber",template:'dragons-den',kind:'dragons-den',environment:'dragon-den'});setProjectBackground('#030208');scene.fog.near=16;scene.fog.far=62;renderer.toneMappingExposure=1.08;rebuildTerrain();makeGroundActor();clearGroup(waterGroup);

  const floorParts=[];
  for(const cfg of [
    [0,0.03,1.0,16,1,12,0,'Council Floor'],
    [0,0.02,11.3,9,1,7,0,'Wake Floor'],
    [-11.2,0.05,5.5,8,1,8,-.12,'Creator Floor'],
    [10.4,0.08,-6.5,9,1,8,.10,'Throne Floor'],
    [11.4,0.12,3.8,7,1,6,-.18,'Perch Floor'],
    [-9.8,0.04,-8.4,7,1,6,.15,'Portal Floor'],
    [0,0.04,-10.2,7,1,5,0,'Memory Floor']
  ]){
    const p=makeDenStructure('floorPlate',[cfg[0],0,cfg[2]],true,cfg[7],'#5e477d');p.position.y=cfg[1];p.scale.set(cfg[3],.7,cfg[5]);p.rotation.y=cfg[6];p.userData.colliderRadius=0;floorParts.push(p);
  }
  const floorGroup=groupActors(floorParts,'Seed Chamber Stone Floor',{record:false,select:false,folder:'Dragon Den/Main Chamber',role:'den-floor',tags:['dragon-den','architecture']});

  const shellParts=[];
  const wallPoints=[
    [-20,-14],[-15.5,-16],[-10.5,-16.5],[-5,-16.4],[5,-16.4],[10.5,-16.5],[15.5,-16],[20,-14],
    [21,-9],[21,-4],[21,2],[21,8],[19,13],[15,16],[10,17],[5,17],[-5,17],[-10,17],[-15,16],[-19,13],
    [-21,8],[-21,2],[-21,-4],[-21,-9]
  ];
  wallPoints.forEach((p,i)=>{const rock=makeRock([p[0],0,p[1]],[2.8+(i%3)*.32,5.8+(i%4)*.65,2.6+(i%2)*.38],true,'Cavern Wall '+String(i+1));rock.userData.folder='Dragon Den/Cavern Shell';rock.userData.tags=['dragon-den','cavern-shell'];shellParts.push(rock);});
  const shell=groupActors(shellParts,'Cavern Shell',{record:false,select:false,folder:'Dragon Den/Cavern Shell',role:'cavern-shell',tags:['dragon-den','cavern-shell']});

  // Roof is built from many editable pieces, then grouped into one selectable object.
  const roofParts=[];
  for(const side of [-1,1])for(const z of [-10,-3,4,11]){
    const slab=makeDenStructure('slab',[side*10.5,0,z],true,'Vault Slab','#34303c');
    slab.position.y=11.8;slab.scale.set(11.5,.55,4.1);slab.rotation.z=side*-.36;slab.userData.colliderRadius=0;roofParts.push(slab);
  }
  for(const z of [-12,-5,2,9]){
    const rib=makeDenStructure('slab',[0,0,z],true,'Vault Rib','#514b59');rib.position.y=12.7;rib.scale.set(1.0,.7,5.1);rib.rotation.y=Math.PI/2;rib.userData.colliderRadius=0;roofParts.push(rib);
  }
  const roof=groupActors(roofParts,'Vaulted Cavern Roof',{record:false,select:false,folder:'Dragon Den/Cavern Shell',role:'den-roof',tags:['dragon-den','runtime-shell']});roof.visible=false;

  // Structural pillars imply a huge chamber without filling the room with blockers.
  const pillarParts=[];
  for(const p of [[-15,-9],[15,-9],[-16,8],[16,8]]){const q=makeDenStructure('pillar',[p[0],0,p[1]],true,'Cavern Pillar','#403948');q.scale.set(2.1,8.5,2.1);q.userData.colliderRadius=1.2;pillarParts.push(q);}
  groupActors(pillarParts,'Cavern Pillars',{record:false,select:false,folder:'Dragon Den/Cavern Shell',role:'den-pillars',tags:['dragon-den','architecture']});

  const wake=makeDenStructure('wakeNook',[0,0,13.0],true,'Wake Nook','#ff9d66');wake.userData.role='wake-nook';
  const visitor=makeHero('blue',[0,0,9.1],true,'Visitor / Creator');visitor.userData.folder='Dragon Den/Visitors';visitor.userData.role='human-presence';visitor.rotation.y=Math.PI;

  const dais=makePedestal([0,0,.6],'#9d72ff',true,'Council Rune Dais',5.3);dais.userData.role='council-center';dais.userData.folder='Dragon Den/Main Chamber';
  const memory=makeCrystal([0,0,.6],'#d49bff',true,'Memory Crystal',1.75);memory.userData.role='memory-anchor';memory.userData.tags.push('memory-hook','council-center');

  const creator=makeDenStructure('creatorAlcove',[-11.0,0,5.8],true,'Creator Alcove','#61cfff');creator.rotation.y=.12;creator.userData.role='creator-workspace';
  const forgeCore=makeCrystal([-11.0,0,2.8],'#56d7ff',true,'Forge Workspace Core',.95);forgeCore.userData.role='world-builder-interface';

  const terrace=makeDenStructure('throneTerrace',[9.5,0,-7.0],true,'Throne Terrace','#d49bff');terrace.rotation.y=-.14;terrace.userData.role='throne-side';
  const throne=makeThrone([9.5,0,-7.8],'#d49bff',true,'Kamilion Throne');throne.position.y+=1.75;throne.rotation.y=Math.PI;throne.userData.role='human-author-seat';throne.userData.folder='Dragon Den/Throne Side';

  const perch=makeDenStructure('perch',[11.2,0,3.5],true,'Primary Dragon Perch','#9e70ff');perch.rotation.y=-.35;perch.userData.role='dragon-perch';
  const sw=makeDragon([11.0,0,3.1],'#9e70ff',true,'§wyrl§ Dragon',2.15);sw.position.y+=2.25;sw.rotation.y=-1.58;sw.userData.role='primary-lalm-avatar';
  const forge=makeDragon([-14.0,0,-3.0],'#56d7ff',true,'Forge Dragon',1.45);forge.position.y+=1.0;forge.rotation.y=1.25;forge.userData.role='world-builder-agent';
  const coder=makeDragon([-10.9,0,6.0],'#ff8b55',true,'Coder Dragon',1.15);coder.position.y+=.55;coder.rotation.y=.42;coder.userData.role='coding-reasoner-agent';

  const portalHall=makeDenStructure('arch',[-10.6,0,-10.0],true,'Portal Hall Exit','#a86cff');portalHall.rotation.y=.35;portalHall.userData.role='portal-hall-exit';portalHall.userData.tags.push('dormant-exit');
  const memoryExit=makeDenStructure('arch',[0,0,-13.1],true,'Memory Vault Exit','#6fb7ff');memoryExit.userData.role='memory-vault-exit';memoryExit.userData.tags.push('dormant-exit');
  const inferenceExit=makeDenStructure('arch',[14.0,0,9.1],true,'Inference Core Exit','#59f0c0');inferenceExit.rotation.y=-.72;inferenceExit.userData.role='inference-core-exit';inferenceExit.userData.tags.push('dormant-exit');

  const voice=makeCrystal([-5.0,0,-5.3],'#ff75cf',true,'Spatial Voice Anchor',.75);voice.userData.role='spatial-voice-hook';
  const inference=makeCrystal([7.2,0,7.0],'#65f6c1',true,'Inference Core',.95);inference.userData.role='lalm-inference-hook';

  const lamps=[];
  for(const p of [[-5,9],[5,9],[-6,3],[6,3],[-8,-6],[5,-7],[-14,1],[14,1]]){const l=makeDenStructure('lantern',[p[0],0,p[1]],true,'Den Lantern','#ffb45f');l.userData.folder='Dragon Den/Lighting';lamps.push(l);}
  groupActors(lamps,'Den Lanterns',{record:false,select:false,folder:'Dragon Den/Lighting',role:'den-lighting',tags:['dragon-den','lighting']});

  const crystals=[];
  for(const cfg of [[-16,5,'#5ccfff'],[16,4,'#b36cff'],[-14,-9,'#ff5fc9'],[14,-10,'#62ffc6'],[-4,-12,'#6fb7ff'],[5,13,'#d49bff']]){const c=makeCrystal([cfg[0],0,cfg[1]],cfg[2],true,'Cavern Crystal',.72);c.userData.folder='Dragon Den/Crystals';crystals.push(c);}
  groupActors(crystals,'Cavern Rune Crystals',{record:false,select:false,folder:'Dragon Den/Crystals',role:'den-runes',tags:['dragon-den','crystals']});

  finishTemplate('hero');setRuntimeShellVisibility(false);
  orbit.target.set(0,2,1);perspectiveCamera.position.set(20,13,26);orbit.update();
  toast("Dragon's Den v5.3 · grouped architecture + immersive cavern");
}
"""
    s=_replace_block(s,"function buildDragonsDenProject(){","function inferProjectMeta(p){",den_block)

    # Runtime shell is visible only when inhabiting the Den.
    s=_once(
      s,
      "  const h=heroActor();",
      "  setRuntimeShellVisibility(true);\n  const h=heroActor();"
    )
    s=_once(
      s,
      "  const h=heroActor();setHeroBodyVisible(h,true);resetStick($('moveStick'),fpMove);",
      "  const h=heroActor();setHeroBodyVisible(h,true);setRuntimeShellVisibility(false);resetStick($('moveStick'),fpMove);"
    )

    # Keep debug collider rendering correct for grouped children.
    s=_once(
      s,
      "c.position.set(a.position.x, terrainHeight(a.position.x,a.position.z)+0.1, a.position.z);",
      "const wp=worldPos(a,new THREE.Vector3());c.position.set(wp.x,terrainHeight(wp.x,wp.z)+0.1,wp.z);c.scale.setScalar(worldColliderRadius(a)/(a.userData.colliderRadius||1));"
    )

    # Agent surface gets grouping operations.
    s=_once(
      s,
      "  openProjects:()=>{showProjectHub();return true;}\n};",
      "  openProjects:()=>{showProjectHub();return true;},\n  groupActors:(ids,name='Agent Group')=>{const list=ids.map(id=>actors.find(a=>a.userData.id===id)).filter(Boolean);const g=groupActors(list,name);return g?.userData.id||null;},\n  ungroup:(id)=>{const g=actors.find(a=>a.userData.id===id);return !!ungroupActor(g).length;}\n};"
    )

    return s
