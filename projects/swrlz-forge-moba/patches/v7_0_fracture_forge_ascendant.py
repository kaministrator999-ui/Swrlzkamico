"""§wyrl§ Engine v7.0: Forge Command Deck + Fracture Forge landmark production pass."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v7.0 token missing: "+old[:200])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V6_8_DEN2_GROUND_SNAP":"V7_0_FRACTURE_FORGE_ASCENDANT",
      "Maker v6.8":"Maker v7.0","MAKER v6.8":"MAKER v7.0",
      "v6.8 · DEN 2 GROUND SNAP":"v7.0 · FRACTURE FORGE ASCENDANT",
      "version:'v6.8'":"version:'v7.0'",
      "version:'swyrl-engine-agent-v4.8'":"version:'swyrl-engine-agent-v5.0'",
      "engine:'§wyrl§ Engine · Maker v6.8'":"engine:'§wyrl§ Engine · Maker v7.0'",
      "version:6.8":"version:7.0",
      "editorLog('§wyrl§ Engine v6.8 initialized · Fracture Forge dragons hard-snapped to support','ok')":"editorLog('§wyrl§ Engine v7.0 initialized · Command Deck · Fracture Forge Ascendant','ok')"
    }.items(): s=_once(s,a,b)

    # Engine production layer: compact command deck, searchable tools, quick focus/frame,
    # scene statistics and one-tap runtime/editor switching without disturbing existing handlers.
    css=r"""
.engine-command-deck{position:absolute;left:50%;top:74px;transform:translateX(-50%);z-index:24;display:flex;gap:6px;padding:6px;border:1px solid #304862;border-radius:15px;background:#07111ddd;backdrop-filter:blur(12px);box-shadow:0 10px 32px #0008;max-width:calc(100vw - 26px);overflow:auto}
.engine-command-deck button{border:1px solid #38536f;background:#132337;color:#dff7ff;border-radius:10px;padding:8px 11px;font:750 12px system-ui;white-space:nowrap}
.engine-command-deck button:active{transform:translateY(1px)}
.engine-command-deck .accent{border-color:#8c69ff;background:#291d53;color:#f2eaff}
.engine-stats-pill{position:absolute;right:14px;top:128px;z-index:22;padding:7px 10px;border:1px solid #29475c;border-radius:999px;background:#07111dcc;color:#8edfff;font:700 11px system-ui;pointer-events:none}
.tool-search{width:100%;box-sizing:border-box;border:1px solid #34506b;border-radius:12px;background:#07111d;color:#e9f7ff;padding:11px 12px;margin:0 0 10px;font:600 14px system-ui}
.tool-section[hidden]{display:none!important}
@media(max-width:720px){.engine-command-deck{top:70px;left:12px;right:12px;transform:none}.engine-stats-pill{top:126px;right:12px}.engine-command-deck button{padding:8px 10px}}
"""
    s=_once(s,"</style>",css+"\n</style>")
    marker="bindVirtualStick('moveStick',fpMove);bindVirtualStick('lookStick',fpLook);"
    engine=r"""
function installEngineCommandDeck(){
  if(document.querySelector('.engine-command-deck'))return;
  const app=document.querySelector('.app')||document.body,deck=document.createElement('div');deck.className='engine-command-deck';
  const actions=[
    ['Projects',()=>showProjectHub?.()],['Focus',()=>{if(selected){const p=new THREE.Vector3();selected.getWorldPosition(p);orbit.target.copy(p);orbit.update();}}],
    ['Frame',()=>{if(selected){const box=new THREE.Box3().setFromObject(selected),sp=new THREE.Sphere();box.getBoundingSphere(sp);orbit.target.copy(sp.center);perspectiveCamera.position.copy(sp.center).add(new THREE.Vector3(sp.radius*1.8,sp.radius*1.15,sp.radius*1.8));orbit.update();}}],
    ['Top',()=>{perspectiveCamera.position.set(0,55,.01);orbit.target.set(0,0,0);orbit.update();}],
    ['Play',()=>$('playBtn')?.click(),true],['Tools',()=>$('mobileToolsBtn')?.click()]
  ];
  for(const [label,fn,accent] of actions){const b=document.createElement('button');b.textContent=label;if(accent)b.className='accent';b.onclick=fn;deck.appendChild(b);}
  app.appendChild(deck);const stats=document.createElement('div');stats.className='engine-stats-pill';stats.id='engineStatsPill';app.appendChild(stats);
  setInterval(()=>{const n=actors?.length||0,sel=selected?.name||'None';stats.textContent=n+' actors · '+sel;},700);
  const panel=$('mobileToolsPanel');if(panel){const host=panel.querySelector('.sheet-body,.panel-body,.tools-body')||panel;if(!host.querySelector('.tool-search')){const q=document.createElement('input');q.className='tool-search';q.placeholder='Search tools…';q.oninput=()=>{const term=q.value.trim().toLowerCase();host.querySelectorAll('.tool-section').forEach(sec=>sec.hidden=!!term&&!sec.textContent.toLowerCase().includes(term));};host.prepend(q);}}
}
installEngineCommandDeck();
"""
    s=_once(s,marker,marker+"\n"+engine)

    # Fracture Forge Ascendant: add authored landmarks and layered readable routes.
    # These use established engine primitives, remain editable actors, and don't duplicate the project.
    denMarker="  const sw=makeGlitchDragonV3([17,0,8],'#7c55ff',true,'§wyrl§ Glitch Dragon',2.8,'#5cecff');"
    den=r"""
  // Ascendant landmark pass: distinct silhouettes make the megacavern navigable at a glance.
  const asc=[];
  const gateL=makeDenStructure('pillar',[-7,0,18],true,'Ascendant Gate Left','#35214f');gateL.scale.set(1.5,8,1.5);asc.push(gateL);
  const gateR=makeDenStructure('pillar',[7,0,18],true,'Ascendant Gate Right','#35214f');gateR.scale.set(1.5,8,1.5);asc.push(gateR);
  const gateC=makeDenStructure('arch',[0,0,18],true,'Ascendant Crown Gate','#8259c9');gateC.scale.set(1.8,2.1,1.5);asc.push(gateC);
  const overlook=makeDenStructure('floorPlate',[0,0,11],true,'Creator Overlook','#263a58');overlook.position.y=.55;overlook.scale.set(7,.55,3.4);asc.push(overlook);
  const bridge=makeDenStructure('floorPlate',[0,0,-9],true,'Fracture Spine Bridge','#2b2447');bridge.position.y=.72;bridge.scale.set(3.2,.38,9);asc.push(bridge);
  const vaultL=makeDenStructure('arch',[-18,0,-5],true,'Frost Dragon Vault','#3d8aa6');vaultL.scale.set(1.45,1.8,1.35);asc.push(vaultL);
  const vaultR=makeDenStructure('arch',[14,0,-15],true,'Ember Dragon Vault','#9d3e65');vaultR.scale.set(1.45,1.8,1.35);asc.push(vaultR);
  groupActors(asc,'Ascendant Landmarks',{record:false,select:false,folder:'Glitch Den/Landmarks',role:'navigation-landmarks',tags:['glitch-den','landmark','ascendant']});
  const beacons=[];
  [[0,1,18,'#a26cff'],[0,1,-18,'#ff6dba'],[-18,1,-5,'#65eaff'],[14,1,-15,'#ff8b62'],[-12,1,11,'#77a8ff'],[12,1,11,'#ae75ff']].forEach((q,i)=>{const c=makeCrystal([q[0],q[1],q[2]],q[3],true,'Wayfinder Crystal '+(i+1),1.25);c.userData.folder='Glitch Den/Wayfinding';beacons.push(c);});
  groupActors(beacons,'Fracture Wayfinders',{record:false,select:false,folder:'Glitch Den/Wayfinding',role:'wayfinding',tags:['glitch-den','wayfinder']});
  addPath('Creator Overlook Route',[[0,18],[0,12],[-7,7],[0,2],[7,7],[0,12]]);
  addPath('Guardian Vault Route',[[-18,-5],[-10,-7],[0,-9],[8,-12],[14,-15]]);
"""
    s=_once(s,denMarker,den+"\n"+denMarker)

    # Lighting composition: authored pools rather than blanket brightness.
    lightMarker="  for(const q of [[0,7,0,'#7d5cff',3.2,26],[-18,6,-5,'#55ddff',2.4,20],[14,6,-15,'#ff5d8d',2.2,19],[0,9,-18,'#ff9b55',1.6,17]])"
    newLight="  for(const q of [[0,8,0,'#8c64ff',4.2,30],[0,5,17,'#9a72ff',2.2,20],[-18,7,-5,'#55ddff',3.0,23],[14,7,-15,'#ff5d8d',2.8,22],[0,10,-18,'#ff9b55',2.1,20],[-11,4,10,'#557dff',1.5,15],[11,4,10,'#bb65ff',1.5,15]])"
    s=_once(s,lightMarker,newLight)
    return s
