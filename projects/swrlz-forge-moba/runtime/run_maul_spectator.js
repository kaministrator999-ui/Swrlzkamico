// Maul-specific, read-only spectator presentation of recorded entity state.
// The original Sheep Tag spectator remains unchanged for non-Maul recordings.
function stRunDrawMaul(ctx, entities, project, width, height, selectedId, game) {
  const active=entities.filter(e=>e&&e.active!==false&&!e.removed&&!e.destroyed&&e.visible!==false);
  const kind=e=>String(e.type||e.kind||'').toLowerCase();
  const position=e=>Array.isArray(e.position)?e.position:[0,0,0];
  const point=(x,y,z)=>project([x,y,z]);
  function polygon(points,fill,stroke='#385363',lineWidth=.65) {
    const ps=points.map(p=>project(p));if(ps.some(p=>!p))return;
    ctx.beginPath();ps.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));
    ctx.closePath();ctx.fillStyle=fill;ctx.fill();
    if(stroke){ctx.lineWidth=lineWidth;ctx.strokeStyle=stroke;ctx.stroke();}
  }
  function bounds(e) {
    if(e.worldBounds?.min&&e.worldBounds?.max)return e.worldBounds;
    const at=position(e),halfX=Math.max(.5,Number(e.size?.[0]||2)/2);
    const halfZ=Math.max(.5,Number(e.size?.[2]||2)/2);
    return {min:[at[0]-halfX,at[1],at[2]-halfZ],max:[at[0]+halfX,at[1]+1,at[2]+halfZ]};
  }
  function surface(e,fill,stroke) {
    const b=bounds(e),lo=b.min,hi=b.max,y=hi[1];
    polygon([[lo[0],y,lo[2]],[hi[0],y,lo[2]],[hi[0],y,hi[2]],[lo[0],y,hi[2]]],fill,stroke);
  }
  function box(e,topFill,sideFill,stroke) {
    const b=bounds(e),a=b.min,z=b.max;
    polygon([[a[0],a[1],z[2]],[z[0],a[1],z[2]],[z[0],z[1],z[2]],[a[0],z[1],z[2]]],sideFill,'');
    polygon([[z[0],a[1],a[2]],[z[0],a[1],z[2]],[z[0],z[1],z[2]],[z[0],z[1],a[2]]],sideFill,'');
    surface(e,topFill,stroke);
  }
  // Paint the enormous sea first rather than interpreting its bounds as a giant opaque cube.
  for(const e of active.filter(e=>kind(e)==='maul-water'))surface(e,'#24495c','#417489');
  for(const e of active.filter(e=>kind(e)==='maul-snowfield'))surface(e,'#d9eaf0','#9bbdc9');
  for(const e of active.filter(e=>kind(e)==='maul-cliff'))box(e,'#b9d1da','#263e4f','#72919e');
  const decorations=active.filter(e=>/maul-pine|maul-route-turn|maul-banner|maul-spawn|maul-gate|maul-exit/.test(kind(e)));
  for(const e of decorations){
    const k=kind(e),p=point(...position(e));if(!p)continue;
    if(k==='maul-pine'){
      ctx.fillStyle='#3b786e';ctx.beginPath();ctx.moveTo(p.x,p.y-8);ctx.lineTo(p.x-5,p.y+3);ctx.lineTo(p.x+5,p.y+3);ctx.closePath();ctx.fill();
    }else if(k==='maul-route-turn'){
      ctx.strokeStyle='#ddbe6c';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(p.x,p.y,4,0,Math.PI*2);ctx.stroke();
    }else if(k==='maul-banner'){
      ctx.fillStyle='#edbb6e';ctx.fillRect(p.x-1,p.y-8,1,11);ctx.fillStyle='#e58c69';
      ctx.beginPath();ctx.moveTo(p.x,p.y-8);ctx.lineTo(p.x+8,p.y-5);ctx.lineTo(p.x,p.y-2);ctx.fill();
    }else if(k==='maul-spawn'||k==='maul-gate'){
      ctx.strokeStyle=k==='maul-spawn'?'#bc83e9':'#e7bc64';ctx.lineWidth=2;
      ctx.beginPath();ctx.arc(p.x,p.y,5,0,Math.PI*2);ctx.stroke();
    }else if(k==='maul-exit'){
      ctx.fillStyle='#ffda8b';ctx.beginPath();ctx.moveTo(p.x,p.y-7);ctx.lineTo(p.x+7,p.y);ctx.lineTo(p.x,p.y+7);ctx.lineTo(p.x-7,p.y);ctx.closePath();ctx.fill();
      ctx.fillStyle='#172d3b';ctx.font='bold 10px system-ui';ctx.fillText('EXIT',p.x+9,p.y);
    }
  }
  // Shared ground footprint is visible; combat pieces stay individually distinguishable.
  const props=active.filter(e=>/maul-maze-wall|maul-arrow|maul-cannon|maul-frost|maul-storm/.test(kind(e)));
  props.sort((a,b)=>(position(a)[2]-position(b)[2]));
  const colors={'maul-arrow':'#f1d179','maul-cannon':'#f18d6e','maul-frost':'#75cce9','maul-storm':'#c99bf8'};
  for(const e of props){
    const k=kind(e);
    if(k==='maul-maze-wall'){box(e,'#7e99a4','#3e5561','#b4ced6');continue;}
    const p=point(...position(e));if(!p)continue;
    ctx.fillStyle='#263f50';ctx.strokeStyle=colors[k];ctx.lineWidth=1.5;ctx.beginPath();
    ctx.rect(p.x-4,p.y-5,8,9);ctx.fill();ctx.stroke();
    ctx.fillStyle=colors[k];ctx.beginPath();ctx.arc(p.x,p.y-1,2.4,0,Math.PI*2);ctx.fill();
  }
  for(const e of active.filter(e=>kind(e)==='maul-builder')){
    const p=point(...position(e));if(!p)continue;ctx.fillStyle='#e5cf83';
    ctx.beginPath();ctx.arc(p.x,p.y-3,3.2,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle='#334f5f';ctx.stroke();
  }
  for(const e of active.filter(e=>kind(e)==='maul-shot')){
    const p=point(...position(e));if(!p)continue;ctx.fillStyle='#ffe1a2';
    ctx.beginPath();ctx.arc(p.x,p.y,2.5,0,Math.PI*2);ctx.fill();
  }
  for(const e of active.filter(e=>kind(e)==='maul-creep')){
    const p=point(...position(e));if(!p)continue;const hp=Number(e.hp),maxHp=Number(e.maxHp);
    ctx.fillStyle='#d75f60';ctx.strokeStyle='#672e3a';ctx.lineWidth=1;ctx.beginPath();ctx.arc(p.x,p.y,3.8,0,Math.PI*2);ctx.fill();ctx.stroke();
    if(maxHp>0&&Number.isFinite(hp)){ctx.fillStyle='#152d39';ctx.fillRect(p.x-6,p.y-8,12,2.5);ctx.fillStyle='#84e4a0';ctx.fillRect(p.x-6,p.y-8,12*Math.max(0,Math.min(1,hp/maxHp)),2.5);}
  }
  const chosen=active.find(e=>e.id===selectedId);if(chosen){
    const p=point(...position(chosen));if(p){ctx.strokeStyle='#ffffff';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x,p.y,9,0,Math.PI*2);ctx.stroke();
      ctx.font='bold 11px system-ui';ctx.fillStyle='#f4f8fb';ctx.fillText(String(chosen.name||chosen.type||'Selected'),Math.min(width-160,p.x+10),Math.max(24,p.y-10));}
  }
  // Recorder replay HUD uses captured game data rather than calculating simulated outcomes.
  const wave=Number(game?.wave||0),lives=Number(game?.lives??0),gold=Number(game?.gold??0);
  ctx.fillStyle='#102633dd';ctx.fillRect(6,6,Math.min(width-12,280),28);
  ctx.font='bold 11px system-ui';ctx.fillStyle='#eff8fc';
  ctx.fillText('FROSTVEIL  ·  Wave '+wave+'/30   ♥ '+lives+'   Gold '+Math.floor(gold),12,24);
  ctx.font='10px system-ui';ctx.fillStyle='#bad3df';
  ctx.fillText('NORTH −Z  •  EAST +X  •  drag to orbit, scroll to zoom',10,height-11);
}
