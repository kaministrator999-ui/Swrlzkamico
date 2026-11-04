// §E v11.265 — runtime-house batching and toggleable Sheep Tag nerd statistics.
// Source of truth: native gameplay buildings. No changes to authored/editor meshes,
// sheep AI, colliders, fog masks, camera pose, XR render loop or network authority.
const se265Perf={
  housesOptimized:0,sourceMeshes:0,packedMeshes:0,drawablesSaved:0,
  skipped:0,failures:0,lastFailure:'',flatFrames:[],flatLast:0,
  metricPage:0,hud:null,hudOpen:false,lastHudPaint:0
};
function se265BatchBuilding(building){
  if(!building||building.authored||!building.mesh?.children)return false;
  const root=building.mesh;
  // Preserve all pivoted pieces, instanced decoration, and custom children.
  // The common static house surfaces are direct children of the root.
  const old=root.children.filter(o=>o.isMesh&&!o.isInstancedMesh&&
    o.geometry?.getAttribute('position')&&o.material&&!Array.isArray(o.material));
  if(old.length<6){se265Perf.skipped++;return false;}
  const byMaterial=new Map();
  for(const mesh of old){
    if(!byMaterial.has(mesh.material))byMaterial.set(mesh.material,[]);
    byMaterial.get(mesh.material).push(mesh);
  }
  const staged=[],temporary=[];
  try{
    for(const [material,meshes] of byMaterial){
      const chunks=[];let count=0;
      for(const mesh of meshes){
        mesh.updateMatrix();
        let geo=mesh.geometry.clone();
        if(geo.index){const flat=geo.toNonIndexed();geo.dispose();geo=flat;}
        geo.applyMatrix4(mesh.matrix);
        const position=geo.getAttribute('position'),normal=geo.getAttribute('normal');
        if(!position||!normal||position.itemSize!==3||normal.itemSize!==3)
          throw Error('Unsupported static house vertex format');
        chunks.push(geo);temporary.push(geo);count+=position.count;
      }
      const positions=new Float32Array(count*3),normals=new Float32Array(count*3),
        uvs=new Float32Array(count*2);
      let offset=0;
      for(const geo of chunks){
        const pos=geo.getAttribute('position'),norm=geo.getAttribute('normal'),
          uv=geo.getAttribute('uv');
        for(let i=0;i<pos.count;i++){
          const dst=offset+i;
          positions[dst*3]=pos.getX(i);positions[dst*3+1]=pos.getY(i);
          positions[dst*3+2]=pos.getZ(i);
          normals[dst*3]=norm.getX(i);normals[dst*3+1]=norm.getY(i);
          normals[dst*3+2]=norm.getZ(i);
          if(uv){uvs[dst*2]=uv.getX(i);uvs[dst*2+1]=uv.getY(i);}
        }
        offset+=pos.count;
      }
      const merged=new THREE.BufferGeometry();
      merged.setAttribute('position',new THREE.BufferAttribute(positions,3));
      merged.setAttribute('normal',new THREE.BufferAttribute(normals,3));
      merged.setAttribute('uv',new THREE.BufferAttribute(uvs,2));
      merged.computeBoundingSphere();
      const mesh=new THREE.Mesh(merged,material);
      mesh.castShadow=true;mesh.receiveShadow=true;
      mesh.name='Sheep Tag runtime house · batched '+staged.length;
      staged.push(mesh);
    }
    if(staged.length>=old.length){
      staged.forEach(mesh=>mesh.geometry.dispose());se265Perf.skipped++;return false;
    }
    // Atomic swap: all geometry is built before touching the live house.
    const oldGeometries=new Set();
    old.forEach(mesh=>{oldGeometries.add(mesh.geometry);root.remove(mesh);});
    staged.forEach(mesh=>root.add(mesh));
    oldGeometries.forEach(geo=>geo.dispose());
    const colors=new Set();
    root.traverse(node=>{
      const mats=Array.isArray(node.material)?node.material:[node.material];
      for(const mat of mats)if(mat?.color)colors.add(mat);
    });
    building.colors=[...colors].map(material=>({material,color:material.color.clone()}));
    root.userData.se265Batch={source:old.length,packed:staged.length,
      retained:root.children.length-staged.length};
    se265Perf.housesOptimized++;
    se265Perf.sourceMeshes+=old.length;
    se265Perf.packedMeshes+=staged.length;
    se265Perf.drawablesSaved+=old.length-staged.length;
    return true;
  }catch(error){
    staged.forEach(mesh=>mesh.geometry.dispose());
    se265Perf.failures++;se265Perf.lastFailure=String(error?.message||error);
    return false;
  }finally{
    temporary.forEach(geo=>geo.dispose());
  }
}
const se265OriginalNewBuilding=stNewBuilding;
stNewBuilding=function(...args){
  const building=se265OriginalNewBuilding(...args);
  if(building&&!building.authored)se265BatchBuilding(building);
  return building;
};
function se265Snapshot(){
  const session=typeof stSession!=='undefined'?stSession:null;
  const buildings=session?.buildings?.filter(b=>b.hp>0)||[];
  const live=buildings.filter(b=>!b.authored);
  let source=0,packed=0,retained=0,optimized=0;
  for(const b of live){
    const batch=b.mesh?.userData?.se265Batch;
    if(batch){source+=batch.source;packed+=batch.packed;retained+=batch.retained;optimized++;}
  }
  const xr=!!renderer?.xr?.isPresenting;
  const p=window.SWYRL_ENGINE_QUEST_PERFORMANCE_210?.diagnose?.()||{};
  const gaps=window.SWYRL_ENGINE_QUEST_HEADTURN_239?.diagnose?.()||{};
  const info=renderer?.info||{};
  const flat=se265Perf.flatFrames;
  const averageFlat=flat.length?flat.reduce((a,b)=>a+b,0)/flat.length:0;
  return {
    active:!!session&&!session.simulate,
    mode:xr?'WebXR':'browser',
    callbackFps:xr?(p.fps||0):(averageFlat?Math.round(1000/averageFlat):0),
    callbackMs:xr?(p.avgFrameMs||0):Number(averageFlat.toFixed(2)),
    // Callback cadence is not a GPU timer; the compositor can reproject frames.
    timingBasis:'main-thread callback cadence; not measured GPU time',
    drawCalls:info.render?.calls??0,triangles:info.render?.triangles??0,
    textures:info.memory?.textures??0,geometries:info.memory?.geometries??0,
    houses:buildings.length,runtimeHouses:live.length,optimizedHouses:optimized,
    housePartsBefore:source,housePartsAfter:packed+retained,
    partsSaved:Math.max(0,source-packed),
    liveSheep:session?.units?.filter(u=>u.kind==='sheep'&&!u.captured).length||0,
    liveWolves:session?.units?.filter(u=>u.kind==='wolf'&&!u.captured).length||0,
    callbackGapMs:gaps.recentMeanCallbackGapMs||0,
    worstCallbackGapMs:gaps.worstCallbackGapMs||0,
    gapsOver20:gaps.gapOver20ms||0,gapsOver35:gaps.gapOver35ms||0,
    gapsOver70:gaps.gapOver70ms||0,
    menuGapCount:gaps.largeGapsWhileMenuOpen||0,
    otherGapCount:gaps.largeGapsWithoutMenu||0,
    fogCpuMs:p.fogUpdateCpuMs||0,fogCalls:p.fogSampleCalls||0,
    fogUploads:p.fogTextureUploads||0,
    batchFailures:se265Perf.failures,batchLastError:se265Perf.lastFailure
  };
}
function se265Lines(s,page){
  const top='PAGE '+(page+1)+'/3  ·  CENTER: NEXT PAGE';
  if(page===0)return [
    'CADENCE '+s.callbackFps+' FPS · '+s.callbackMs+'ms avg',
    'DRAWS '+s.drawCalls+' · TRIANGLES '+s.triangles,
    'GPU MEM OBJECTS: TEX '+s.textures+' / GEO '+s.geometries,
    'HOUSES '+s.houses+' · RUNTIME '+s.runtimeHouses,
    'SHEEP '+s.liveSheep+' · WOLVES '+s.liveWolves,
    top
  ];
  if(page===1)return [
    'BATCHED HOUSES '+s.optimizedHouses+' / '+s.runtimeHouses,
    'HOUSE PARTS BEFORE '+s.housePartsBefore,
    'HOUSE PARTS AFTER '+s.housePartsAfter,
    'SAVED HOUSE DRAWS (EST) '+s.partsSaved,
    'BATCH ERRORS '+s.batchFailures,
    top
  ];
  return [
    'XR GAP AVG '+s.callbackGapMs+'ms · WORST '+s.worstCallbackGapMs+'ms',
    'LATE 20/35/70ms '+s.gapsOver20+'/'+s.gapsOver35+'/'+s.gapsOver70,
    'LATE MENU '+s.menuGapCount+' · OTHER '+s.otherGapCount,
    'FOG CPU TOTAL '+s.fogCpuMs+'ms / '+s.fogCalls+' calls',
    'FOG UPLOADS '+s.fogUploads+' · no GPU timer',
    top
  ];
}
// Reuse the existing world-space, grabbable VR metrics panel: NO new render
// surface or head-tracking loop. Updates already run at a bounded 1Hz.
const se265OldPanelLines=se210PanelLines;
se210PanelLines=function(panel){
  if(panel.kind==='metrics')return se265Lines(se265Snapshot(),se265Perf.metricPage);
  return se265OldPanelLines(panel);
};
const se265OldPanelPress=se210PanelPress;
se210PanelPress=function(hit){
  const uv=hit?.uv;
  if(hit?.panel?.kind==='metrics'&&uv&&uv.y>=.17&&uv.y<=.79){
    se265Perf.metricPage=(se265Perf.metricPage+1)%3;
    hit.panel.lastKey='';se210CanvasRender(hit.panel);return true;
  }
  return se265OldPanelPress(hit);
};
// Expose the stats button directly from the SESSION wheel, with the same
// existing workspaceMetrics action path. It remains movable/pinnable.
const se265OldOptions=se195Options;
se195Options=function(mode=se195.mode,page=se195.page){
  const options=se265OldOptions(mode,page);
  if(mode==='game'&&page==='more'&&!options.some(v=>v[0]==='workspaceMetrics'))
    return [...options.filter(v=>v[0]!=='back'),['workspaceMetrics','NERD STATS'],...options.filter(v=>v[0]==='back')];
  if(mode==='game'&&page==='workspace')
    return options.map(v=>v[0]==='workspaceMetrics'?['workspaceMetrics','NERD STATS']:v);
  return options;
};
function se265EnsureHud(){
  if(se265Perf.hud||!document.body)return;
  const button=document.createElement('button'),panel=document.createElement('div');
  button.id='se265NerdStatsToggle';button.type='button';button.textContent='📊 NERD STATS';
  button.style.cssText='position:fixed;right:12px;bottom:82px;z-index:10060;background:#113845;color:#c9fff1;border:1px solid #55d8d2;border-radius:9px;padding:9px 13px;font:bold 13px sans-serif;cursor:pointer;box-shadow:0 3px 13px #0008;';
  panel.id='se265NerdStatsPanel';
  panel.style.cssText='position:fixed;right:12px;top:12%;width:min(360px,85vw);max-height:75vh;overflow:auto;z-index:10060;background:#061722ee;color:#d9fff3;border:1px solid #5acdc8;border-radius:12px;padding:12px;font:12px/1.55 monospace;white-space:pre-wrap;box-shadow:0 5px 22px #0009;';
  panel.hidden=true;
  const heading=document.createElement('div');
  heading.textContent='§E / SHEEP TAG / NERD STATS';
  heading.style.cssText='font-weight:bold;color:#7af5df;margin-bottom:8px';
  const content=document.createElement('div');panel.append(heading,content);
  button.addEventListener('click',()=>{
    se265Perf.hudOpen=!se265Perf.hudOpen;
    panel.hidden=!se265Perf.hudOpen;
    if(se265Perf.hudOpen)se265PaintHud();
  });
  document.body.append(button,panel);se265Perf.hud={button,panel,content};
}
function se265PaintHud(){
  const hud=se265Perf.hud;
  if(!hud||!se265Perf.hudOpen)return;
  const s=se265Snapshot();
  hud.content.textContent=se265Lines(s,0).slice(0,5).join('\n')+
    '\n\n'+se265Lines(s,1).slice(0,5).join('\n')+
    '\n\n'+se265Lines(s,2).slice(0,5).join('\n')+
    '\n\nFrame cadence ≠ measured GPU render time.';
}
function se265UpdateHud(now){
  if(!se265Perf.hud)se265EnsureHud();
  const hud=se265Perf.hud;if(!hud)return;
  const eligible=!!stSession&&!stSession.simulate&&
    currentProject?.kind==='sheep-tag'&&!renderer.xr?.isPresenting;
  hud.button.hidden=!eligible;
  hud.panel.hidden=!eligible||!se265Perf.hudOpen;
  if(eligible&&se265Perf.hudOpen&&now-se265Perf.lastHudPaint>920){
    se265Perf.lastHudPaint=now;se265PaintHud();
  }
}
const se265OldUpdate=stUpdate;
stUpdate=function(dt,t){
  const r=se265OldUpdate(dt,t);
  const now=performance.now();
  if(stSession&&!renderer.xr?.isPresenting){
    const diff=se265Perf.flatLast?now-se265Perf.flatLast:0;
    if(diff>0&&diff<150){
      se265Perf.flatFrames.push(diff);
      if(se265Perf.flatFrames.length>90)se265Perf.flatFrames.shift();
    }
    se265Perf.flatLast=now;
  }else se265Perf.flatLast=0;
  if(!se265Perf.hud||now-se265Perf.lastHudPaint>700)se265UpdateHud(now);
  return r;
};
const se265OldStop=stStop;
stStop=function(...args){
  const result=se265OldStop(...args);
  se265Perf.flatFrames.length=0;se265Perf.flatLast=0;
  if(se265Perf.hud){se265Perf.hud.button.hidden=true;se265Perf.hud.panel.hidden=true;}
  return result;
};
window.SWYRL_ENGINE_SHEEP_NERD_STATS_265=Object.freeze({
  diagnose:se265Snapshot,
  openVR:()=>se210PanelCreate('metrics'),
  openBrowser:()=>{se265EnsureHud();se265Perf.hudOpen=true;se265UpdateHud(performance.now());se265PaintHud();},
  batchStatus:()=>({housesOptimized:se265Perf.housesOptimized,
    meshesBefore:se265Perf.sourceMeshes,meshesAfter:se265Perf.packedMeshes,
    estimatedSavedDrawables:se265Perf.drawablesSaved,
    skipped:se265Perf.skipped,failures:se265Perf.failures,lastFailure:se265Perf.lastFailure})
});
