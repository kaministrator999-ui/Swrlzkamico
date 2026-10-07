"""§wyrl§ Engine v7.8: retractable desktop docks + multi-object layer manager."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v7.8 token missing: "+old[:180])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V7_7_CANONICAL_GLITCH_DEN_PROJECT":"V7_8_RETRACTABLE_LAYERS",
      "Maker v7.7":"Maker v7.8","MAKER v7.7":"MAKER v7.8",
      "version:'v7.7'":"version:'v7.8'",
      "version:'swyrl-engine-agent-v5.7'":"version:'swyrl-engine-agent-v5.8'",
      "engine:'§wyrl§ Engine · Maker v7.7'":"engine:'§wyrl§ Engine · Maker v7.8'",
      "version:7.7":"version:7.8"
    }.items(): s=_once(s,a,b)

    css=r"""
/* v7.8 retractable authoring docks + layers */
.editor-dock-toggle{position:absolute;z-index:66;top:46px;width:28px;height:44px;border:1px solid #34506b;background:#0b1928;color:#bdeaff;border-radius:8px;font:800 16px system-ui;box-shadow:0 6px 18px #0008}
#outlinerDockToggle{left:4px}#detailsDockToggle{right:4px}
.app.outliner-collapsed #hierarchy{display:none!important}.app.details-collapsed #inspector{display:none!important}
.app.outliner-collapsed #outlinerDockToggle{left:4px}.app.details-collapsed #detailsDockToggle{right:4px}
.layer-manager{position:absolute;z-index:67;top:44px;left:50%;transform:translateX(-50%);width:min(520px,92vw);max-height:72vh;overflow:auto;display:none;border:1px solid #34506b;border-radius:12px;background:#081421f7;box-shadow:0 18px 50px #000c;padding:10px;color:#d9edfa;font:12px system-ui}.layer-manager.open{display:block}
.layer-head,.layer-row{display:flex;align-items:center;gap:7px}.layer-head{justify-content:space-between;margin-bottom:8px;font-weight:800}.layer-actions{display:flex;gap:5px;flex-wrap:wrap}.layer-manager button{border:1px solid #36516a;border-radius:7px;background:#102338;color:#d9edfa;padding:6px 8px;font:700 11px system-ui}.layer-list{display:grid;gap:5px}.layer-row{padding:6px;border:1px solid #23394c;border-radius:8px;background:#0d1d2d}.layer-row .layer-name{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.layer-row.mixed{border-color:#7558ad}.layer-row.hidden-layer{opacity:.58}
.multi-object-selected{outline:1px solid #8d65ff!important;background:#261c42!important}
@media(min-width:721px) and (max-width:1100px){
 #hierarchy{max-width:190px!important}
 #inspector{max-width:245px!important}
}
"""
    s=_once(s,"</style>",css+"\n</style>")

    marker="polishDesktopEditorChrome();"
    js=r"""
const multiObjectSelection=new Set();
function actorLabel(a){return a?.userData?.name||a?.name||'Actor'}
function actorFolder(a){return a?.userData?.folder||'Unlayered'}
function setActorFolder(a,v){a.userData=a.userData||{};a.userData.folder=v}
function installRetractableDocks(){
  const app=document.querySelector('.app'),h=$('hierarchy'),d=$('inspector');if(!app||!h||!d)return;
  if(!$('outlinerDockToggle')){const b=document.createElement('button');b.id='outlinerDockToggle';b.className='editor-dock-toggle';b.title='Retract / restore World Outliner';b.onclick=()=>{app.classList.toggle('outliner-collapsed');b.textContent=app.classList.contains('outliner-collapsed')?'›':'‹'};b.textContent='‹';app.appendChild(b)}
  if(!$('detailsDockToggle')){const b=document.createElement('button');b.id='detailsDockToggle';b.className='editor-dock-toggle';b.title='Retract / restore Details';b.onclick=()=>{app.classList.toggle('details-collapsed');b.textContent=app.classList.contains('details-collapsed')?'‹':'›'};b.textContent='›';app.appendChild(b)}
}
function layerActors(){return (typeof actors!=='undefined'?actors:[]).filter(a=>a&&a.userData)}
function refreshLayerManager(){
  const p=$('layerManager');if(!p)return;const list=p.querySelector('.layer-list');list.innerHTML='';
  const map=new Map();for(const a of layerActors()){const f=actorFolder(a);if(!map.has(f))map.set(f,[]);map.get(f).push(a)}
  for(const [name,items] of [...map].sort((a,b)=>a[0].localeCompare(b[0]))){
    const row=document.createElement('div');row.className='layer-row';const visible=items.filter(a=>a.visible!==false).length;if(!visible)row.classList.add('hidden-layer');if(visible&&visible<items.length)row.classList.add('mixed');
    const check=document.createElement('input');check.type='checkbox';check.checked=items.every(a=>multiObjectSelection.has(a));check.indeterminate=items.some(a=>multiObjectSelection.has(a))&&!check.checked;check.title='Select all objects in this layer';check.onchange=()=>{items.forEach(a=>check.checked?multiObjectSelection.add(a):multiObjectSelection.delete(a));refreshLayerManager()};
    const label=document.createElement('span');label.className='layer-name';label.textContent=name+' · '+items.length;
    const eye=document.createElement('button');eye.textContent=visible?'👁':'◌';eye.title='Hide / show layer';eye.onclick=()=>{const show=!visible;items.forEach(a=>a.visible=show);markDirty?.();refreshLayerManager()};
    row.append(check,label,eye);list.appendChild(row)
  }
  p.querySelector('.selection-count').textContent=multiObjectSelection.size+' selected';
}
function installLayerManager(){
  const app=document.querySelector('.app');if(!app||$('layerManager'))return;
  const p=document.createElement('section');p.id='layerManager';p.className='layer-manager';p.innerHTML='<div class="layer-head"><span>Layers & Multi-Object</span><button data-close>×</button></div><div class="layer-actions"><button data-all>Select All</button><button data-clear>Clear</button><button data-hide>Hide Selected</button><button data-show>Show All</button><button data-group>Group / Layer Selected</button><span class="selection-count">0 selected</span></div><div class="layer-list"></div>';app.appendChild(p);
  p.querySelector('[data-close]').onclick=()=>p.classList.remove('open');
  p.querySelector('[data-all]').onclick=()=>{layerActors().forEach(a=>multiObjectSelection.add(a));refreshLayerManager()};
  p.querySelector('[data-clear]').onclick=()=>{multiObjectSelection.clear();refreshLayerManager()};
  p.querySelector('[data-hide]').onclick=()=>{multiObjectSelection.forEach(a=>a.visible=false);markDirty?.();refreshLayerManager()};
  p.querySelector('[data-show]').onclick=()=>{layerActors().forEach(a=>a.visible=true);markDirty?.();refreshLayerManager()};
  p.querySelector('[data-group]').onclick=()=>{if(multiObjectSelection.size<2){toast('Select 2+ objects first');return}const name=prompt('Group / layer name','Group '+Date.now().toString().slice(-4));if(!name)return;multiObjectSelection.forEach(a=>setActorFolder(a,name));markDirty?.();if(typeof rebuildHierarchy==='function')rebuildHierarchy();refreshLayerManager();toast(multiObjectSelection.size+' objects grouped into '+name)};
  refreshLayerManager();
}
function toggleLayerManager(){installLayerManager();refreshLayerManager();$('layerManager').classList.toggle('open')}
installRetractableDocks();installLayerManager();
"""
    s=_once(s,marker,marker+"\n"+js)

    # Add Layers to the authoritative desktop Window menu and make Reset Workspace restore docks.
    s=_once(s,"['Outliner','outliner'],['Inspector / Details','inspector'],['Content Browser','content']","['Outliner','outliner'],['Inspector / Details','inspector'],['Layers & Multi-Object','layers'],['Content Browser','content']")
    s=_once(s,"inspector:()=>engineClick('inspectorBtn'),outliner:()=>enginePanel('hierarchy')","inspector:()=>engineClick('inspectorBtn'),outliner:()=>enginePanel('hierarchy'),layers:()=>toggleLayerManager()")
    s=s.replace("document.querySelectorAll('.hidden').forEach(e=>{if(['hierarchy','inspector','console'].includes(e.id))e.classList.remove('hidden')});toast('Workspace reset')","document.querySelectorAll('.hidden').forEach(e=>{if(['hierarchy','inspector','console'].includes(e.id))e.classList.remove('hidden')});document.querySelector('.app')?.classList.remove('outliner-collapsed','details-collapsed');toast('Workspace reset')")
    return s
