"""§wyrl§ Engine v7.4: professional editor menu + workspace shell."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v7.4 token missing: "+old[:220])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V7_3_ENGINE_HEALTH":"V7_4_EDITOR_WORKSPACES",
      "Maker v7.3":"Maker v7.4","MAKER v7.3":"MAKER v7.4",
      "v7.3 · ENGINE HEALTH":"v7.4 · EDITOR WORKSPACES",
      "version:'v7.3'":"version:'v7.4'",
      "version:'swyrl-engine-agent-v5.3'":"version:'swyrl-engine-agent-v5.4'",
      "engine:'§wyrl§ Engine · Maker v7.3'":"engine:'§wyrl§ Engine · Maker v7.4'",
      "version:7.3":"version:7.4",
      "editorLog('§wyrl§ Engine v7.3 initialized · unified Wisp flight · runtime diagnostics','ok')":"editorLog('§wyrl§ Engine v7.4 initialized · editor menus · workspace launcher','ok')"
    }.items(): s=_once(s,a,b)

    css=r"""
.engine-menubar{position:absolute;left:8px;right:8px;top:8px;z-index:70;display:flex;align-items:center;gap:2px;padding:4px;border:1px solid #273e55;border-radius:11px;background:#07111df2;box-shadow:0 7px 24px #0008;overflow-x:auto;scrollbar-width:none}
.engine-menubar::-webkit-scrollbar{display:none}.engine-menu{position:relative;flex:0 0 auto}.engine-menu>button{border:0;background:transparent;color:#cfe3f4;padding:7px 9px;border-radius:7px;font:700 12px system-ui}.engine-menu>button:hover,.engine-menu.open>button{background:#18304a;color:white}
.engine-menu-pop{position:fixed;z-index:90;display:none;min-width:220px;max-width:min(310px,92vw);padding:6px;border:1px solid #34506b;border-radius:11px;background:#0a1523f8;box-shadow:0 16px 40px #000b}.engine-menu.open .engine-menu-pop{display:block}
.engine-menu-pop button{display:flex;width:100%;align-items:center;justify-content:space-between;gap:14px;border:0;background:transparent;color:#dcebf7;text-align:left;padding:9px 10px;border-radius:7px;font:600 12px system-ui}.engine-menu-pop button:hover{background:#19304a}.engine-menu-pop button[disabled]{opacity:.42}.engine-menu-pop .sep{height:1px;background:#263c50;margin:5px}.engine-menu-pop small{color:#7f9ab2;font-weight:500}
.workspace-launcher{position:absolute;inset:48px 10px auto 10px;z-index:68;display:none;padding:12px;border:1px solid #34506b;border-radius:14px;background:#07111df5;box-shadow:0 18px 50px #000c}.workspace-launcher.open{display:block}.workspace-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;color:#e7f6ff;font:800 15px system-ui}.workspace-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.workspace-grid button{min-height:62px;border:1px solid #304d67;border-radius:11px;background:#102136;color:#dcefff;padding:8px;font:700 12px system-ui}.workspace-grid button span{display:block;margin-top:4px;color:#7f9cb5;font:500 10px system-ui}
.app.runtime-play .engine-menubar,.app.runtime-play .workspace-launcher{display:none!important}
@media(max-width:720px){.engine-menubar{top:6px}.workspace-launcher{top:46px}.workspace-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.engine-menu>button{padding:7px 8px}.engine-command-deck{top:48px!important}}
"""
    s=_once(s,"</style>",css+"\n</style>")

    marker="installRuntimeDiagnostics();"
    js=r"""
function engineClick(id){const e=$(id);if(e){e.click();return true}toast('Tool not available in this build');return false}
function enginePanel(id){const e=$(id);if(!e){toast('Panel not available in this build');return false}e.classList.toggle('hidden');return true}
function engineUnavailable(name){toast(name+' · planned workspace — not implemented yet')}
function installEngineMenus(){
  if($('engineMenubar'))return;
  const host=document.querySelector('.app')||document.body,bar=document.createElement('nav');bar.id='engineMenubar';bar.className='engine-menubar';bar.setAttribute('aria-label','§wyrl§ Engine menu');
  const menus={
    File:[['Projects','projects'],['Save Project','save'],['Load Project','load'],['Export Standalone','export'],['sep'],['Project Settings','project-settings']],
    Edit:[['Undo','undo'],['Redo','redo'],['sep'],['Duplicate','duplicate'],['Delete','delete'],['Group Selection','group'],['Ungroup','ungroup']],
    Create:[['Build / Place Actor','build'],['Content Browser','content'],['sep'],['Blueprint / Logic','blueprint'],['Material','material'],['Animation','animation'],['Audio','audio'],['UI / HUD','ui']],
    View:[['Focus Selection','focus'],['Frame Selection','frame'],['Top View','top'],['World / Local','space'],['Terrain Snap','terrain'],['sep'],['Outliner','outliner'],['Inspector / Details','inspector']],
    Play:[['Play In Editor','play'],['Simulate','simulate'],['Play From Here','play-here'],['sep'],['Runtime Diagnostics','diagnostics']],
    Tools:[['Workspace Launcher','workspaces'],['Components','components'],['World Tools','world'],['Bake Ghosts','bake'],['sep'],['Input Mapping','input'],['Physics','physics'],['Lighting','lighting'],['Profiler','profiler']],
    Window:[['Outliner','outliner'],['Inspector / Details','inspector'],['Content Browser','content'],['Components','components'],['Console / Output Log','console'],['World','world'],['sep'],['Reset Workspace','reset-layout']],
    Help:[['Keyboard / Controls','controls'],['Engine Build Info','build-info'],['About §wyrl§ Engine','about']]
  };
  const action=(key)=>{
    const map={projects:()=>showProjectHub?.(),save:()=>engineClick('saveBtn'),load:()=>engineClick('loadBtn'),export:()=>engineClick('exportBtn'),undo:()=>engineClick('undoBtn'),redo:()=>engineClick('redoBtn'),duplicate:()=>engineClick('duplicateBtn'),delete:()=>engineClick('deleteBtn'),group:()=>engineClick('groupBtn'),ungroup:()=>engineClick('ungroupBtn'),build:()=>engineClick('buildBtn'),content:()=>engineClick('contentBtn'),focus:()=>engineClick('focusBtn'),frame:()=>{if(selected){const b=new THREE.Box3().setFromObject(selected),sp=new THREE.Sphere();b.getBoundingSphere(sp);orbit.target.copy(sp.center);perspectiveCamera.position.copy(sp.center).add(new THREE.Vector3(sp.radius*1.8,sp.radius*1.15,sp.radius*1.8));orbit.update()}},top:()=>{perspectiveCamera.position.set(0,55,.01);orbit.target.set(0,0,0);orbit.update()},space:()=>engineClick('spaceBtn'),terrain:()=>engineClick('terrainSnapBtn'),play:()=>engineClick('playBtn'),simulate:()=>engineClick('simulateBtn'),['play-here']:()=>engineClick('playFromHereBtn'),bake:()=>engineClick('bakeBtn'),world:()=>engineClick('worldBtn'),components:()=>engineClick('componentsBtn'),inspector:()=>engineClick('inspectorBtn'),outliner:()=>enginePanel('hierarchy'),console:()=>enginePanel('console'),workspaces:()=>$('engineWorkspaces')?.classList.toggle('open'),diagnostics:()=>$('runtimeDiag')?.classList.toggle('force-show'),['reset-layout']:()=>{document.querySelectorAll('.hidden').forEach(e=>{if(['hierarchy','inspector','console'].includes(e.id))e.classList.remove('hidden')});toast('Workspace reset')},controls:()=>toast('Editor: W move · E rotate · R scale · Delete · Ctrl/Cmd+G group · Play uses twin-stick/WASD'),['build-info']:()=>toast('§wyrl§ Engine '+(window.SWYRL_ENGINE_BUILD?.version||'v7.4')),about:()=>toast('§wyrl§ Engine · browser-native world/game editor')};
    if(map[key])return map[key]();engineUnavailable(key.replaceAll('-',' '));
  };
  for(const [name,items] of Object.entries(menus)){const m=document.createElement('div');m.className='engine-menu';const b=document.createElement('button');b.textContent=name;const pop=document.createElement('div');pop.className='engine-menu-pop';for(const item of items){if(item[0]==='sep'){const d=document.createElement('div');d.className='sep';pop.appendChild(d);continue}const x=document.createElement('button');x.innerHTML='<span>'+item[0]+'</span>';x.onclick=()=>{action(item[1]);m.classList.remove('open')};pop.appendChild(x)}b.onclick=e=>{e.stopPropagation();document.querySelectorAll('.engine-menu.open').forEach(x=>x!==m&&x.classList.remove('open'));m.classList.toggle('open');const r=b.getBoundingClientRect();pop.style.left=Math.min(r.left,innerWidth-230)+'px';pop.style.top=(r.bottom+3)+'px'};m.append(b,pop);bar.appendChild(m)}
  host.appendChild(bar);document.addEventListener('pointerdown',e=>{if(!e.target.closest('.engine-menu'))document.querySelectorAll('.engine-menu.open').forEach(x=>x.classList.remove('open'))});
  const w=document.createElement('section');w.id='engineWorkspaces';w.className='workspace-launcher';w.innerHTML='<div class="workspace-head"><span>§E Workspaces</span><button id="workspaceClose">×</button></div><div class="workspace-grid"></div>';host.appendChild(w);$('workspaceClose').onclick=()=>w.classList.remove('open');
  const cards=[['Level Design','Outliner · Details · transforms','outliner'],['Content','Assets · import · organize','content'],['Gameplay','Components · logic · input','components'],['World','Environment · terrain · lighting','world'],['Play & Debug','PIE · simulation · diagnostics','play'],['Console','Logs · commands · errors','console'],['Project','Save · load · export · settings','projects'],['Build','Ghosts · bake · packaging','bake']];
  for(const [a,b,k] of cards){const x=document.createElement('button');x.innerHTML=a+'<span>'+b+'</span>';x.onclick=()=>{action(k);w.classList.remove('open')};w.querySelector('.workspace-grid').appendChild(x)}
}
installEngineMenus();
"""
    s=_once(s,marker,marker+"\n"+js)
    return s
