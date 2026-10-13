// Read-only spectator review. This viewer also ships inside the standalone
// HTML export; it has no engine, network, or live-match dependencies.
function stRunViewerMount(host,run) {
  const doc=host.ownerDocument;
  host.innerHTML=`<div class="srv-controls"><button id="stRunViewPlay" type="button">▶ Play recording</button><button id="stRunViewReset" type="button">Reset view</button><select id="stRunViewMode" aria-label="Spectator view"><option value="orbit">Orbit overview</option><option value="camera">Recorded player camera</option></select><select id="stRunObserver" aria-label="Follow recorded object"><option value="">Whole map</option></select><span id="stRunViewTime"></span></div><input id="stRunTimeline" aria-label="Recording time" type="range" min="0" step="0.01"><canvas id="stRunReviewCanvas" aria-label="Recorded 3D scene; drag to orbit and scroll to zoom"></canvas><p>Recorded positions, bounds and poses. Drag to orbit; scroll to zoom. Player-camera mode uses the captured lens and orientation.</p><label>Word-described 3D observation<textarea id="stRunNarrative" readonly rows="12"></textarea></label><label>Events at this time<pre id="stRunEvents"></pre></label>`;
  const get=id=>host.querySelector('#'+id),canvas=get('stRunReviewCanvas'),ctx=canvas.getContext('2d');
  const clone=o=>JSON.parse(JSON.stringify(o)),frames=run.frames||[],initial=run.initial||{entities:{},camera:{},game:{}};
  const duration=Math.max(0,Number(run.duration)||Number(frames.at(-1)?.t)||0);
  let t=0,state=null,playing=false,raf=0,last=0,yaw=-.65,pitch=.67,zoom=1,drag=null,disposed=false;
  const pos=e=>Array.isArray(e?.position)?e.position:Array.isArray(e?.pos)?e.pos:[0,0,0];
  const kind=e=>String(e?.actorType||e?.type||e?.kind||'object');
  function frame(at) {
    let source=initial,start=0;
    for(const checkpoint of run.checkpoints||[])if(checkpoint.t<=at&&checkpoint.t>=(source.t||0)){source=checkpoint;start=checkpoint.index+1;}
    const result=clone({entities:source.entities||{},camera:source.camera||{},game:source.game||{}});
    for(let i=start;i<frames.length;i++) {
      const f=frames[i];if(f.t>at+1e-8)break;
      for(const [id,patch]of Object.entries(f.patch||{})){if(patch===null)delete result.entities[id];else result.entities[id]={...(result.entities[id]||{}),...clone(patch)};}
      if(f.camera)result.camera=clone(f.camera);if(f.game)Object.assign(result.game,clone(f.game));
    }
    result.t=at;return result;
  }
  function words() {
    const lines=[`EDITOR SPECTATOR · ${t.toFixed(2)} seconds · X east, Y up, −Z north`,
      'This is the recorded world state. Player visibility and camera framing are separate from the spectator’s knowledge.'];
    if(state.camera.position)lines.push('Player camera at ['+state.camera.position.map(n=>Number(n).toFixed(2)).join(', ')+']; lens '+(state.camera.fov||'?')+'°; aspect '+(state.camera.aspect||'?')+'.');
    const entities=Object.values(state.entities),follow=get('stRunObserver').value;
    for(const e of entities) {
      const p=pos(e),label=e.name||e.id||kind(e),r=e.rotation||[];
      const hidden=e.playerVisible===false||e.visibleToPlayer===false;
      let line=label+' ('+kind(e)+') at ['+p.map(n=>Number(n).toFixed(2)).join(', ')+']';
      if(e.destroyed)line+='; destroyed, no standing structure remains';
      if(e.parts?.length)line+='; '+e.parts.length+' articulated nodes; local pose changes '+JSON.stringify(e.partTransforms||{});
      if(e.captured||kind(e)==='wisp')line+='; captured wisp';
      if(e.onUpper||e.archiveOnUpper)line+='; on a raised route';
      if(hidden)line+='; hidden from the player';
      if(e.inFrustum===false||e.inCamera===false)line+='; outside the recorded camera frustum';
      if(e.baked===false)line+='; unbaked editor object';
      if(Number.isFinite(e.hp))line+='; health '+e.hp+(e.maxHp!==undefined?'/'+e.maxHp:'');
      if(e.progress!==undefined)line+='; construction '+Math.round(e.progress*100)+'%';
      if(e.order)line+='; order '+JSON.stringify(e.order);
      if(e.traffic?.mode)line+='; traffic '+e.traffic.mode+(e.traffic.blockedBy?' blocked by '+e.traffic.blockedBy:'');
      if(e.limbAngles)line+='; joint pose ['+e.limbAngles.map(n=>Number(n).toFixed(3)).join(', ')+']';
      if(follow&&e.id===follow)line='FOLLOWING · '+line;
      if(/sheep|wolf|wisp/.test(kind(e))) {
        const near=entities.filter(other=>other.id!==e.id&&Math.hypot(pos(other)[0]-p[0],pos(other)[2]-p[2])<5).sort((a,b)=>Math.hypot(pos(a)[0]-p[0],pos(a)[2]-p[2])-Math.hypot(pos(b)[0]-p[0],pos(b)[2]-p[2])).slice(0,4);
        if(near.length)line+='; nearby '+near.map(other=>{const q=pos(other),dx=q[0]-p[0],dz=q[2]-p[2];return (other.name||other.id)+' '+Math.hypot(dx,dz).toFixed(2)+' units '+(Math.abs(dx)<.1?'':dx>0?'east':'west')+(Math.abs(dz)<.1?'':dz>0?' south':' north')+(Math.abs(q[1]-p[1])>.5?' at a different height':'');}).join(', ');
      }
      lines.push(line+'.');
    }
    lines.push('Recorded game state: '+JSON.stringify(state.game));return lines.join('\n');
  }
  function project(point,width,height,centre) {
    if(get('stRunViewMode').value==='camera') {
      const c=state.camera,p=c.position||[0,20,30],q=c.quaternion||[0,0,0,1],v=point.map((n,i)=>n-p[i]),[x,y,z,w]=[-q[0],-q[1],-q[2],q[3]];
      const tx=2*(y*v[2]-z*v[1]),ty=2*(z*v[0]-x*v[2]),tz=2*(x*v[1]-y*v[0]);
      const r=[v[0]+w*tx+y*tz-z*ty,v[1]+w*ty+z*tx-x*tz,v[2]+w*tz+x*ty-y*tx],depth=-r[2];
      if(depth<=.05)return null;
      const aspect=Number(c.aspect)||width/height,viewHeight=Math.min(height,width/aspect),viewWidth=viewHeight*aspect,focal=viewHeight/(2*Math.tan((Number(c.fov)||55)*Math.PI/360));
      return {x:width/2+r[0]/depth*focal,y:height/2-r[1]/depth*focal,d:depth,scale:focal/depth};
    }
    const [x,y,z]=point.map((n,i)=>n-centre[i]),horizontal=x*Math.cos(yaw)-z*Math.sin(yaw),depth=z*Math.cos(yaw)+x*Math.sin(yaw);
    const extent=Number(run.rules?.bounds||run.map?.project?.sheepTag?.bounds||run.project?.sheepTag?.bounds||40);
    const scale=Math.min(width/(extent*2.5),height/(extent*1.7))*zoom;
    return {x:width/2+horizontal*scale,y:height*.53+(depth*Math.sin(pitch)-y*Math.cos(pitch))*scale,d:depth*Math.cos(pitch)+y*Math.sin(pitch),scale};
  }
  function draw() {
    if(disposed||!state)return;const rect=canvas.getBoundingClientRect(),width=Math.max(260,rect.width),height=Math.max(240,rect.height),dpr=Math.min(2,doc.defaultView.devicePixelRatio||1);
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#101e1b';ctx.fillRect(0,0,width,height);
    const entities=Object.values(state.entities),follow=state.entities[get('stRunObserver').value],centre=follow?pos(follow):[0,0,0];
    const line=(a,b,color)=>{const p=project(a,width,height,centre),q=project(b,width,height,centre);if(!p||!q)return;ctx.strokeStyle=color;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();};
    for(let n=-40;n<=40;n+=5){line([n,0,-40],[n,0,40],'#23423b');line([-40,0,n],[40,0,n],'#23423b');}
    line([0,0,0],[8,0,0],'#eead83');line([0,0,0],[0,0,-8],'#96c7ff');line([0,0,0],[0,8,0],'#c8e99d');
    const ordered=entities.filter(e=>e.active!==false&&!e.removed&&!e.destroyed).map(e=>({e,p:project(pos(e),width,height,centre)})).filter(x=>x.p).sort((a,b)=>b.p.d-a.p.d);
    ctx.font='11px system-ui';
    for(const {e,p}of ordered) {
      const k=kind(e),at=pos(e);if(/meadow|grass|earth|road|zone/.test(k))continue;
      const unit=/sheep|wolf|wisp/.test(k),color=/wolf/.test(k)?'#ed9e8e':/wisp/.test(k)?'#7fe5ef':unit?'#fff0cb':/pond/.test(k)?'#51aeba':/tree|thorn/.test(k)?'#5eaa70':/income/.test(k)?'#e4c87f':'#c5b18b';
      const half=Number(e.halfX||e.radius||(/tree/.test(k)?1.4:unit ? .35:1.2)),h=unit?1:/wall/.test(k)?3.3:/tree/.test(k)?5:2;
      const top=project([at[0],at[1]+h,at[2]],width,height,centre);if(!top)continue;
      ctx.fillStyle=color;ctx.globalAlpha=(e.playerVisible===false||e.visibleToPlayer===false) ? .55:1;
      if(unit){ctx.beginPath();ctx.ellipse(top.x,top.y,Math.max(3,half*p.scale),Math.max(3,half*p.scale*.65),0,0,Math.PI*2);ctx.fill();line(at,[at[0],at[1]+h,at[2]],color);}
      else {
        const hz=Number(e.halfZ||half),bounds=e.worldBounds;
        const lo=bounds?.min||[at[0]-half,at[1],at[2]-hz],hi=bounds?.max||[at[0]+half,at[1]+h,at[2]+hz];
        const corners=[[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],lo[1],hi[2]],[lo[0],lo[1],hi[2]]],tops=corners.map(c=>[c[0],hi[1],c[2]]);
        const projected=tops.map(c=>project(c,width,height,centre));if(projected.every(Boolean)){ctx.beginPath();projected.forEach((q,i)=>i?ctx.lineTo(q.x,q.y):ctx.moveTo(q.x,q.y));ctx.closePath();ctx.fill();}
        for(let i=0;i<4;i++){line(corners[i],tops[i],color);line(tops[i],tops[(i+1)%4],'#f6e5c2');}
      }
      ctx.globalAlpha=1;if(unit||e.id===get('stRunObserver').value){ctx.fillStyle='#eef7e7';ctx.fillText(e.name||e.id||k,top.x+5,top.y-7);}
    }
    ctx.fillStyle='#cce5da';ctx.fillText('NORTH = −Z  ·  EAST = +X  ·  HEIGHT = Y',12,height-12);
  }
  function seek(value) {
    t=Math.max(0,Math.min(duration,Number(value)||0));state=frame(t);get('stRunTimeline').value=t;
    get('stRunViewTime').textContent=t.toFixed(2)+' / '+duration.toFixed(2)+' s';get('stRunNarrative').value=words();
    get('stRunEvents').textContent=(run.events||[]).filter(e=>e.t<=t&&e.t>=Math.max(0,t-3)).map(e=>'['+e.t.toFixed(2)+'s] '+e.type+' '+(e.actorId||'')+' '+JSON.stringify(e.details||{})).join('\n')||'No event in the preceding three seconds.';
    draw();return clone(state);
  }
  function pause(){playing=false;if(raf)doc.defaultView.cancelAnimationFrame(raf);raf=0;get('stRunViewPlay').textContent='▶ Play recording';}
  function advance(now){if(!playing||disposed)return;if(last)seek(t+(now-last)/1000);last=now;if(t>=duration){pause();return;}raf=doc.defaultView.requestAnimationFrame(advance);}
  function play(){if(t>=duration)seek(0);playing=true;last=0;get('stRunViewPlay').textContent='Ⅱ Pause recording';raf=doc.defaultView.requestAnimationFrame(advance);}
  get('stRunTimeline').max=duration;get('stRunTimeline').oninput=e=>{pause();seek(e.target.value);};get('stRunViewPlay').onclick=()=>playing?pause():play();
  get('stRunViewReset').onclick=()=>{yaw=-.65;pitch=.67;zoom=1;draw();};get('stRunViewMode').onchange=draw;
  const catalog={...(initial.entities||{})};for(const f of frames)for(const [id,patch]of Object.entries(f.patch||{}))if(patch&&!catalog[id])catalog[id]={id,...patch};
  for(const e of Object.values(catalog)){const option=doc.createElement('option');option.value=e.id;option.textContent=e.name||e.id;get('stRunObserver').append(option);}
  get('stRunObserver').onchange=()=>seek(t);
  canvas.onpointerdown=e=>{drag={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture?.(e.pointerId);};
  canvas.onpointermove=e=>{if(!drag||drag.id!==e.pointerId)return;yaw+=(e.clientX-drag.x)*.01;pitch=Math.max(.15,Math.min(1.4,pitch+(e.clientY-drag.y)*.006));drag.x=e.clientX;drag.y=e.clientY;draw();};
  canvas.onpointerup=canvas.onpointercancel=()=>{drag=null;};canvas.onwheel=e=>{e.preventDefault();zoom=Math.max(.25,Math.min(8,zoom*Math.exp(-e.deltaY*.001)));draw();};
  const resize=()=>draw();doc.defaultView.addEventListener('resize',resize);seek(0);
  return {seek,state:()=>clone(state),time:()=>t,pause,play,destroy:()=>{pause();disposed=true;doc.defaultView.removeEventListener('resize',resize);host.replaceChildren();}};
}

const ST_RUN_VIEW_STYLES=`.srv-controls{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.srv-controls>*{min-height:44px}#stRunTimeline{width:100%;min-height:44px}#stRunReviewCanvas{display:block;width:100%;height:330px;background:#101e1b;border:1px solid #526f5b;border-radius:8px;touch-action:none}#stRunNarrative{box-sizing:border-box;width:100%;background:#101e1b;color:#e8f1df;border:1px solid #526f5b;border-radius:7px;font:12px/1.55 ui-monospace,monospace;padding:10px}#stRunEvents{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.5 ui-monospace,monospace;max-height:220px;overflow:auto;background:#15271f;padding:9px}#stRunViewerContainer label{display:block;margin-top:12px}#stRunViewerContainer p{font-size:12px;color:#b9ccbc}`;
const stRunReviewState={open:false,record:null,viewer:null,installed:false};
function stRunDownloadBlob(blob,name) {const link=document.createElement('a'),url=URL.createObjectURL(blob);link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);}
function stRunExport(format='json',id=null) {
  if(playing||simulating)return {ok:false,reason:'Stop Play before exporting the spectator record.'};
  const run=id?stRunData(id):(stRunReviewState.record||stRunData());if(!run)return {ok:false,reason:'Record a Play run or open a saved recording first.'};
  const name='play-run-'+String(run.id||run.startedAt||'run').replace(/[^a-z0-9_-]/gi,'-').slice(0,80)+'.swyrl-run.';
  if(format==='text'){stRunDownloadBlob(new Blob([stRunTranscript(run)],{type:'text/plain;charset=utf-8'}),name+'txt');}
  else if(format==='html') {
    const payload=JSON.stringify(run).replace(/</g,'\\u003c').replace(/>/g,'\\u003e').replace(/&/g,'\\u0026');
    const html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Editor · Recorded spectator</title><style>body{margin:0;padding:18px;background:#172b22;color:#edf2df;font:14px/1.5 system-ui}main{max-width:1100px;margin:auto}button,select{font:inherit;background:#294331;color:#edf2df;border:1px solid #8ba376;border-radius:7px;padding:8px}'+ST_RUN_VIEW_STYLES+'</style><main><h1>Editor · Recorded spectator</h1><p>Read-only recorded world. Scrub time, orbit the scene, follow objects, and read the written observations.</p><div id="stRunViewerContainer"></div></main><script id="stRunPayload" type="application/json">'+payload+'<\/script><script>window.SWYRL_RUN_VIEWER=('+stRunViewerMount.toString()+')(document.getElementById("stRunViewerContainer"),JSON.parse(document.getElementById("stRunPayload").textContent));<\/script></html>';
    stRunDownloadBlob(new Blob([html],{type:'text/html;charset=utf-8'}),name+'html');
  }else if(format==='json')stRunDownloadBlob(new Blob([JSON.stringify(run)],{type:'application/json'}),name+'json');
  else return {ok:false,reason:'Choose JSON, text or spectator HTML.'};
  return {ok:true,format,id:run.id};
}
function stRunOpenRecord(run) {
  if(playing||simulating)return {ok:false,reason:'Stop Play before opening the omniscient spectator view.'};
  const valid=stRunValidate(run);if(!valid.ok)return {ok:false,reason:valid.reason};
  const mount=document.createElement('div');let viewer;try{viewer=stRunViewerMount(mount,run);}catch(error){return {ok:false,reason:'Cannot review this recording: '+error.message};}
  stRunReviewState.viewer?.destroy();stRunReviewState.record=run;
  $('stRunViewerContainer').hidden=false;$('stRunViewerContainer').replaceChildren(mount);stRunReviewState.viewer=viewer;viewer.seek(0);$('stRunRecordDetails').textContent=(run.complete?'Complete':'Incomplete')+' run · '+(run.project?.project?.name||'Editor project')+' · '+(run.endReason||'captured states')+' · '+(run.duration??run.frames.at(-1)?.t??0).toFixed(2)+' s · '+run.frames.length+' frames · '+run.events.length+' events';
  for(const id of ['stRunExportJson','stRunExportText','stRunExportHtml'])$(id).disabled=false;
  return {ok:true,id:run.id};
}
function stRunRefreshUI() {
  if(!stRunReviewState.installed)return;
  const available=!!currentProject,status=stRunStatus();$('stRunLauncher').style.bottom=currentProject?.canonicalId==='ghosts-different-forms-ep01'?'114px':'12px';$('stRunLauncher').classList.toggle('hidden',!available||!!(playing||simulating));
  $('stRunBadge').hidden=(!status.active&&!status.error)||!(playing||simulating);
  if(status.active)$('stRunBadge').textContent='● Recording · '+status.active.frameCount+' frames · '+status.active.duration.toFixed(1)+' s';
  if(status.error)$('stRunBadge').textContent='Recording incomplete: '+status.error;
  const restart=$('stRestart');if(restart&&!restart.dataset.runRecorder){const native=restart.onclick;restart.dataset.runRecorder='1';restart.onclick=function(...args){if(stRunState.active)stRunState.active._requestedEndReason='restart';return native?.apply(this,args);};}
  if((playing||simulating)&&stRunReviewState.open)stRunCloseUI();
}
function stRunCloseUI() {stRunReviewState.viewer?.pause();$('stRunPanel').hidden=true;stRunReviewState.open=false;$('stRunLauncher')?.focus();}
function stRunOpenUI() {
  if(playing||simulating){toast('Stop Play before reviewing its spectator recording.');return false;}
  const status=stRunStatus();stRunReviewState.open=true;$('stRunPanel').hidden=false;$('stRunEnabled').checked=status.settings.enabled;$('stRunCadence').value=String(status.settings.cadence);
  const select=$('stRunRun');select.replaceChildren();for(const r of status.runs||[]){const option=document.createElement('option');option.value=r.id;option.textContent=(r.startedAt||r.id)+' · '+Number(r.duration).toFixed(1)+' s · '+r.endReason;select.append(option);}
  const run=stRunData();if(run)stRunOpenRecord(run);else{$('stRunRecordDetails').textContent='Enable recording, close this panel, then use Play. Stop preserves the full run for review and export.';$('stRunViewerContainer').hidden=true;for(const id of ['stRunExportJson','stRunExportText','stRunExportHtml'])$(id).disabled=true;}
  $('stRunClose').focus();return true;
}
function stRunInstallUI() {
  if(stRunReviewState.installed)return;
  const style=document.createElement('style');style.id='sheepRunStyles';style.textContent=ST_RUN_VIEW_STYLES+`#stRunPanel{position:fixed;z-index:130;inset:30px max(14px,calc((100vw - 1120px)/2));overflow:auto;padding:18px;background:#172b22f7;color:#edf2df;border:1px solid #8a9c70;border-radius:12px;font:13px/1.5 system-ui;box-sizing:border-box}#stRunPanel[hidden]{display:none!important}#stRunPanel header{display:flex;align-items:center;gap:8px}#stRunPanel h2{flex:1;font:700 22px Georgia;margin:0}#stRunPanel button,#stRunPanel select,#stRunPanel input{min-height:44px;font:inherit;touch-action:manipulation}#stRunPanel button,#stRunPanel select{padding:8px;color:#eef4da;border:1px solid #728362;border-radius:7px;background:#294331}#stRunPanel .str-options,#stRunPanel .str-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:12px 0}#stRunPanel .str-options label{display:flex;align-items:center;gap:7px}#stRunPanel input[type=checkbox]{width:24px;accent-color:#cbd3a5}#stRunPanel input[type=file]{max-width:100%}#stRunBadge{position:fixed;right:12px;top:150px;z-index:40;padding:5px 9px;background:#173328dc;color:#d3ecbe;border:1px solid #6c9275;border-radius:7px;font:11px system-ui;pointer-events:none}#stRunBadge[hidden]{display:none!important}body:has(#stCreatorPanel:not([hidden])) #stRunLauncher{display:none!important}@media(max-width:860px){#stRunLauncher{display:block!important;position:fixed;right:12px;bottom:12px;z-index:85;min-height:44px;background:#294331;color:#edf2df;border:1px solid #8a9c70;border-radius:7px;padding:9px}#stRunLauncher.hidden{display:none!important}}@media(max-width:620px){#stRunPanel{inset:6px;padding:12px}#stRunReviewCanvas{height:270px}#stRunLauncher{min-height:44px}.str-actions>*{flex:1}}`;
  document.head.append(style);
  const button=document.createElement('button');button.id='stRunLauncher';button.type='button';button.textContent='◉ Run recorder';button.className='top-button';button.title='Record and review editor Play runs';button.style.touchAction='manipulation';if(matchMedia('(max-width:860px)').matches)document.body.append(button);else $('sheepTagRulesBtn').after(button);
  const panel=document.createElement('section');panel.id='stRunPanel';panel.hidden=true;panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-label','Editor run recorder');panel.innerHTML=`<header><h2>Play-run recorder</h2><button id="stRunClose" type="button">Close</button></header><p>Keep the whole Play run for analysis. After Stop, see the recorded world from a spectator’s perspective, including objects hidden from the player.</p><div class="str-options"><label><input id="stRunEnabled" type="checkbox">Record Play run</label><label>Snapshots<select id="stRunCadence"><option value="full">Full · every simulation update</option><option value="0.1">10 snapshots / second</option><option value="0.5">2 snapshots / second</option></select></label></div><p>The enable/disable setting applies to all projects and starters on this device. All commands and game events are recorded at their observed times. The latest three finished runs remain available in this tab; export them to keep them after closing it.</p><div class="str-options"><label>Finished runs<select id="stRunRun" aria-label="Finished recorded run"></select></label><label>Open saved JSON<input id="stRunFile" type="file" accept=".json,application/json"></label></div><p id="stRunRecordDetails"></p><div class="str-actions"><button id="stRunExportJson" type="button" disabled>Export JSON</button><button id="stRunExportText" type="button" disabled>Export text</button><button id="stRunExportHtml" type="button" disabled>Export spectator HTML</button></div><p id="stRunImportFeedback" role="status"></p><div id="stRunViewerContainer" hidden></div>`;
  document.body.append(panel);const badge=document.createElement('div');badge.id='stRunBadge';badge.hidden=true;document.body.append(badge);stRunReviewState.installed=true;
  button.onclick=stRunOpenUI;$('stRunClose').onclick=stRunCloseUI;
  const configure=()=>{const result=stRunConfigure({enabled:$('stRunEnabled').checked,cadence:$('stRunCadence').value});if(!result?.ok)$('stRunImportFeedback').textContent=result?.reason||'Could not change recording settings.';};
  $('stRunEnabled').onchange=$('stRunCadence').onchange=configure;
  $('stRunRun').onchange=e=>stRunOpenRecord(stRunData(e.target.value));
  for(const [id,format]of [['stRunExportJson','json'],['stRunExportText','text'],['stRunExportHtml','html']])$(id).onclick=()=>{const result=stRunExport(format);$('stRunImportFeedback').textContent=result.ok?'Recording downloaded.':result.reason;};
  $('stRunFile').onchange=async e=>{try{const file=e.target.files?.[0];if(!file)return;if(file.size>200*1024*1024)throw Error('This recording is larger than the 200 MB viewer import limit. Keep the original file for analysis.');const run=JSON.parse(await file.text());const valid=typeof stRunValidate==='function'?stRunValidate(run):{ok:true};if(!valid.ok)throw Error(valid.reason);const result=stRunOpenRecord(run);if(!result.ok)throw Error(result.reason);$('stRunImportFeedback').textContent='Saved recording opened. The editor map is unchanged.';}catch(error){$('stRunImportFeedback').textContent='Could not open recording: '+error.message;}finally{e.target.value='';}};
  document.addEventListener('keydown',e=>{if(stRunReviewState.open&&e.key==='Escape'){e.preventDefault();e.stopPropagation();stRunCloseUI();}},true);
  const refresh=stRefreshHUD;stRefreshHUD=function(...args){const result=refresh(...args);stRunRefreshUI();return result;};
  const stopped=stopSession;stopSession=function(...args){const result=stopped(...args);stRunRefreshUI();return result;};$('stopBtn').onclick=()=>stopSession();
  const sessionButtons=setSessionButtons;setSessionButtons=function(...args){const result=sessionButtons(...args);stRunGuard(stRunPause);stRunRefreshUI();return result;};
  for(const type of ['keydown','keyup','pointerdown','pointerup'])document.addEventListener(type,e=>{if(!stRunState.active||stRunState.active.mode==='sheep-tag')return;const run=stRunState.active;queueMicrotask(()=>{if(stRunState.active!==run)return;stRunGuard(()=>stRunNote('input',null,{type,key:e.key||null,pointerType:e.pointerType||null,target:e.target?.id||null,screen:Number.isFinite(e.clientX)?[e.clientX,e.clientY]:null,wallTime:new Date().toISOString()}));});});
  window.SWYRL_ENGINE_RUNS=window.SWYRL_ENGINE_SHEEP_TAG_RUNS={...window.SWYRL_ENGINE_SHEEP_TAG_RUNS,export:stRunExport,review:stRunOpenRecord,open:stRunOpenUI,close:stRunCloseUI};stRunRefreshUI();
}
