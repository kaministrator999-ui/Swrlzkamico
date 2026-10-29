"""Reusable vault architecture and dependable desktop editor framing."""

def once(s, old, new):
    if old not in s:
        raise RuntimeError("v8.0 sanctuary primitive anchor missing: " + old[:100])
    return s.replace(old, new, 1)

def apply(html):
    s = html
    css = r"""
/* Desktop docks size the grid tracks, rather than only their inner content. */
.app{width:100%;min-width:0;grid-template-columns:minmax(0,1fr)}
@media(min-width:721px){
 .workspace{grid-template-columns:235px minmax(0,1fr) 300px;min-width:0}
 .workspace.left-collapsed{grid-template-columns:34px minmax(0,1fr) 300px}
 .workspace.right-collapsed{grid-template-columns:235px minmax(0,1fr) 34px}
 .workspace.left-collapsed.right-collapsed{grid-template-columns:34px minmax(0,1fr) 34px}
 .panel.left,.panel.right{min-width:0;position:relative}
 .workspace.left-collapsed .panel.left>*:not(.dock-rail),.workspace.right-collapsed .panel.right>*:not(.dock-rail){display:none!important}
 .dock-rail{position:sticky;top:0;z-index:20;width:100%;border-radius:0;border-width:0 0 1px;min-height:30px;font-size:10px;letter-spacing:.06em}
 .workspace.left-collapsed .panel.left .dock-rail,.workspace.right-collapsed .panel.right .dock-rail{writing-mode:vertical-rl;min-height:160px;padding:10px 6px}
 .viewport-toolbar{max-width:calc(100% - 20px);overflow-x:auto;flex-wrap:nowrap}
 .layer-head{flex-wrap:wrap}.layer-head b{flex:1 0 100%}.layer-head button{font-size:9px;padding:3px 5px}
 .help{font-size:10px}.help span:last-child{max-width:40%}
 .app.runtime-play .workspace{grid-template-columns:0 minmax(0,1fr) 0!important}
 .app.runtime-play .workspace>.viewport-wrap{grid-column:2;grid-row:1}
 .app.runtime-play .panel.left,.app.runtime-play .panel.right{display:none!important}
 .app.runtime-play .help,.app.runtime-play .badgeBox,.app.runtime-play .viewport-toolbar,.app.runtime-play .build-stamp,.app.runtime-play .engine-stats-pill{display:none!important}
}
"""
    s = once(s, "</style>", css + "\n</style>")
    # Old hint detection matched ancestor text and shrank the entire app to 46%.
    s = once(s, "document.querySelectorAll('div').forEach(e=>{", "document.querySelectorAll('.help span').forEach(e=>{")
    s = once(s, "const nodes=ids.map(id=>$(id)).filter(Boolean);if(!nodes.length)continue;", "const nodes=ids.map(id=>$(id)).filter(n=>n&&panel.contains(n));if(!nodes.length)continue;")
    geometry = r"""
  const vaultPoints=[[-20,4.4],[-17,6.8],[-13,8.6],[-7,10],[0,10.7],[7,10],[13,8.6],[17,6.8],[20,4.4]];
  const beam=(a,b,r,m)=>{const av=new THREE.Vector3(...a),bv=new THREE.Vector3(...b),d=bv.clone().sub(av);const q=new THREE.Mesh(new THREE.CylinderGeometry(r,r,d.length(),8),m);q.position.copy(av.add(bv).multiplyScalar(.5));q.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),d.normalize());g.add(q);return q;};
  if(kind==='vaultCanopy'){
    const canopy=new THREE.MeshStandardMaterial({color:'#242b38',emissive:'#20384d',emissiveIntensity:.25,roughness:.92,metalness:.08,side:THREE.DoubleSide});
    for(let i=0;i<vaultPoints.length-1;i++){
      const [x1,y1]=vaultPoints[i],[x2,y2]=vaultPoints[i+1];
      for(const [z1,z2] of [[-16,-3],[-3,3],[3,16]]){
        if(z1===-3&&Math.abs(x1)<=7&&Math.abs(x2)<=7)continue;
        const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute([x1,y1,z1,x2,y2,z1,x2,y2,z2,x1,y1,z1,x2,y2,z2,x1,y1,z2],3));geo.computeVertexNormals();
        const q=new THREE.Mesh(geo,canopy);q.receiveShadow=false;g.add(q);
      }
    }
  }else if(kind==='chamberWall'){
    const wallMat=new THREE.MeshStandardMaterial({color:'#2c3342',emissive:'#182837',emissiveIntensity:.15,roughness:1,side:THREE.DoubleSide});
    for(let i=0;i<vaultPoints.length-1;i++){const [x1,y1]=vaultPoints[i],[x2,y2]=vaultPoints[i+1];const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute([x1,0,0,x2,0,0,x2,y2,0,x1,0,0,x2,y2,0,x1,y1,0],3));geo.computeVertexNormals();g.add(new THREE.Mesh(geo,wallMat));}
  }else if(kind==='vaultRib'){
    const brass=new THREE.MeshStandardMaterial({color:'#947355',roughness:.52,metalness:.48});
    const trim=glowMat(color,.4);
    for(let i=0;i<vaultPoints.length-1;i++){
      const a=vaultPoints[i],b=vaultPoints[i+1];beam([a[0],a[1]-.25,0],[b[0],b[1]-.25,0],.25,brass);
      beam([a[0],a[1]-.48,-.18],[b[0],b[1]-.48,-.18],.035,trim);
    }
    for(const x of [-17,17]){box(1.0,6.0,1.0,stone,x,3,0);box(1.7,.3,1.7,concrete,x,.15,0);}
  }else if(kind==='oculus'){
    const ring=new THREE.Mesh(new THREE.TorusGeometry(3.15,.15,8,64),mat('#947355'));ring.rotation.x=Math.PI/2;ring.scale.y=.76;g.add(ring);
    const glass=new THREE.Mesh(new THREE.CircleGeometry(3.0,64),new THREE.MeshBasicMaterial({color:'#213f55',side:THREE.DoubleSide}));glass.rotation.x=Math.PI/2;glass.scale.y=.76;glass.position.y=.04;g.add(glass);
    const inner=new THREE.Mesh(new THREE.TorusGeometry(2.65,.028,6,64),glowMat(color,.65));inner.rotation.x=Math.PI/2;inner.scale.y=.76;inner.position.y=-.05;g.add(inner);
    for(let i=0;i<18;i++){const t=i*2.399963,r=.35+2.15*Math.sqrt((i+1)/18);const star=new THREE.Mesh(new THREE.SphereGeometry(i%4===0?.06:.025,6,4),glowMat('#e6d5a9',.5));star.position.set(Math.cos(t)*r,-.09,Math.sin(t)*r*.76);g.add(star);}
  }else if(kind==='workFloor'){
    box(1,.18,1,stone,0,.09,0);box(.94,.018,.94,mat('#272d39'),0,.19,0);
    for(const x of [-.47,.47])box(.012,.015,.94,arcane,x,.205,0);
    for(const z of [-.47,.47])box(.94,.015,.012,arcane,0,.205,z);
  }else
"""
    s = once(s, "  if(kind==='ceiling'){", geometry + "  if(kind==='ceiling'){")
    s = once(s, "  if(type==='denWorkbench')", "  if(type==='denVault') o=makeDenStructure('vaultCanopy',[0,0,0],false,'Vault Canopy','#85cfe0');\n  if(type==='denVaultRib') o=makeDenStructure('vaultRib',[0,0,0],false,'Vault Rib','#e0bb7a');\n  if(type==='denOculus') o=makeDenStructure('oculus',[0,0,0],false,'Star Oculus','#80c8da');\n  if(type==='denSupportColumn'){o=makeDenStructure('pillar',[0,0,0],false,'Gallery Support','#85cfe0');o.userData.colliderRadius=.8;addComponent(o,'Collider');}\n  if(type==='denWorkbench')")
    s = once(s, "  if(type==='denVault')", "  if(type==='denChamberWall')o=makeDenStructure('chamberWall',[0,0,0],false,'Chamber End Wall','#85cfe0');\n  if(type==='denVault')")
    s = once(s, "const ASSET_LIBRARY=[", "const ASSET_LIBRARY=[\n {id:'denVault',name:'Vault Canopy',path:'/Engine/Architecture',desc:'Enclosed stone vault with central skylight'},\n {id:'denVaultRib',name:'Vault Rib',path:'/Engine/Architecture',desc:'Stone and brass vaulted arch'},\n {id:'denOculus',name:'Star Oculus',path:'/Engine/Architecture',desc:'Quiet constellation ceiling light'},\n {id:'denSupportColumn',name:'Gallery Support',path:'/Engine/Architecture',desc:'Stone structural support with collision'},")
    s = once(s, "const ASSET_LIBRARY=[", "const ASSET_LIBRARY=[\n {id:'denChamberWall',name:'Chamber End Wall',path:'/Engine/Architecture',desc:'Vault-profile stone wall'},")
    # Preserve namespaces owned by imported projects, including scripts and station data.
    s = once(s, "  currentProject={\n    name:meta.name", "  currentProject={\n    ...structuredClone(meta),\n    name:meta.name")
    s = once(s, "sun.shadow.mapSize.set(2048,2048);", "sun.shadow.mapSize.set(2048,2048);sun.shadow.normalBias=.08;sun.shadow.bias=-.0005;")
    s = once(s, "      c.material = c.material.clone();\n      c.material.transparent = ghost;\n      c.material.opacity = ghost ? 0.42 : 1;\n      c.material.depthWrite = !ghost;", """      const authored=c.material.userData.authoredVisual||{transparent:c.material.transparent,opacity:c.material.opacity,depthWrite:c.material.depthWrite};
      c.material = c.material.clone();c.material.userData.authoredVisual=authored;
      c.material.transparent = ghost || authored.transparent;
      c.material.opacity = ghost ? Math.min(.42,authored.opacity) : authored.opacity;
      c.material.depthWrite = ghost ? false : authored.depthWrite;""")
    # Replace obsolete dock tabs with rails attached to the actual grid columns.
    start=s.index("function installDesktopDockTabs(){")
    end=s.index("\ninstallLayerPanel();installDesktopDockTabs();",start)
    s=s[:start]+r"""function installDesktopDockTabs(){
  const w=document.querySelector('.workspace');if(!w)return;
  for(const [side,label] of [['left','Outliner'],['right','Details']]){
    const panel=w.querySelector('.panel.'+side);if(!panel||panel.querySelector('.dock-rail'))continue;
    const b=document.createElement('button');b.className='dock-rail';b.textContent=(side==='left'?'◀ ':'▶ ')+label;b.setAttribute('aria-label','Collapse or expand '+label);
    b.onclick=()=>{w.classList.toggle(side+'-collapsed');b.setAttribute('aria-expanded',String(!w.classList.contains(side+'-collapsed')))};
    b.setAttribute('aria-expanded','true');panel.insertBefore(b,panel.firstChild);
  }
}"""+s[end:]
    # Rebuilding the inner hierarchy no longer destroys the layer panel.
    s = once(s, "h.insertBefore(p,h.firstChild);$('layerNew')", "h.parentElement.insertBefore(p,h);$('layerNew')")
    s = once(s, "  if(dirty&&!force&&!confirm('Open the canonical Glitch Dragon Den and discard unsaved scene changes?'))return;\n  loadCanonicalGlitchDen();\n  $('projectHub').classList.remove('show');", "  if(dirty&&!force&&!confirm('Create a new project and discard unsaved scene changes?'))return;\n  if(template==='moba')buildMobaProject();else if(template==='default')buildDefaultProject();else loadCanonicalGlitchDen();\n  initializeHistory('Opened '+currentProject.name);markSaved();$('projectHub').classList.remove('show');")
    return s
