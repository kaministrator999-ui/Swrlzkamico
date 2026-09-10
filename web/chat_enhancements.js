(()=>{"use strict";
const UI_VERSION='1.4.1';
const $=s=>document.querySelector(s);
const safe=v=>v??'—';
let camera=[];
let ops=null;
let verifiedHot=null;

function toast(message){
  const el=$('#toast');
  if(!el)return;
  el.textContent=message;
  el.classList.add('show');
  clearTimeout(el.__swrlzTimer);
  el.__swrlzTimer=setTimeout(()=>el.classList.remove('show'),2600);
}

function safeFilePart(value){
  return String(value||'chat').replace(/[^a-z0-9._-]+/gi,'-').replace(/^-|-$/g,'').slice(0,80)||'chat';
}

function effectiveServerReceipt(){
  const server=ops?.operations?.server||{};
  return {base:server.version||'—',loaded:!!verifiedHot,effective:verifiedHot?.version||'',hot:verifiedHot?.revision||'',requestId:verifiedHot?.requestId||''};
}

function cameraText(includeMeta=false){
  return camera.length
    ? camera.slice(-160).map(x=>`${x.at} #${x.seq??'—'} ${x.type||'EVENT'} ${x.phase||''} ${x.text||''}`.trim()).join('\n')
    : 'No stream events captured yet.';
}

function paintMode(){
  const mode=ops?.mode||'UNKNOWN';
  const server=ops?.operations?.server||{};
  const local=ops?.localR39||{};
  const ready=mode==='UPSTREAM_SERVER'
    ? !!ops?.upstream?.configurationReady
    : !!(local.oneTokenReady||local.interactiveReady);
  const pill=$('#statusPill'),light=$('#nodeLight'),title=$('#nodeTitle'),detail=$('#nodeDetail'),line=$('#swrlzHotVersionLine');
  pill?.classList.toggle('ready',ready);
  pill?.classList.toggle('error',mode==='UNKNOWN');
  light?.classList.toggle('ready',ready);
  light?.classList.toggle('error',mode==='UNKNOWN');
  if(title)title.textContent=mode==='LOCAL_R39'?(ready?'Local R39 ready':'Server R39 warming'):mode==='UPSTREAM_SERVER'?(ready?'Upstream bridge ready':'Upstream setup needed'):'Runtime status unavailable';
  if(detail)detail.textContent=`Chat v${UI_VERSION} · ${verifiedHot?.version?`HOT SERVER v${verifiedHot.version}`:'HOT RUNTIME'} · Base v${server.version||'—'}`;
  if(line)line.textContent=`CHAT v${UI_VERSION} · ${verifiedHot?.version?`HOT SERVER v${verifiedHot.version}`:'HOT RUNTIME'} · BASE v${server.version||'—'}`;
}

async function loadOps(){
  try{
    const r=await fetch('/api/chat/ops',{cache:'no-store'});
    if(!r.ok)throw Error(`HTTP ${r.status}`);
    ops=await r.json();
    paintMode();
  }catch(_){
    if(!ops)paintMode();
  }
}

function capture(event,context){
  if(event?.phase==='HOT_ENGINE_ENTERED'){
    const reason=String(event.reason||'');
    const match=reason.match(/server\s+(\d+\.\d+\.\d+)/i);
    const revision=reason.match(/revision\s+([^·]+)/i);
    if(match)verifiedHot={version:match[1],revision:(revision?.[1]||'').trim(),requestId:context?.requestId||event?.identity?.requestId||''};
  }
  camera.push({at:new Date().toISOString().slice(11,23),seq:event?.seq,type:event?.type,phase:event?.phase,text:event?.type==='DELTA'?String(event.text||'').slice(0,140):event?.reason||''});
  if(camera.length>500)camera=camera.slice(-500);
  paintMode();
}

function exportCameraLog(){
  const thread=typeof currentThread==='function'?currentThread():null;
  const receipt=effectiveServerReceipt();
  const header=[
    '§wyrlz Stream Camera Export',
    `exported=${new Date().toISOString()}`,
    `chatVersion=${UI_VERSION}`,
    `threadId=${thread?.id||'—'}`,
    `threadTitle=${thread?.title||'—'}`,
    `baseVersion=${receipt.base}`,
    `hotServerVersion=${receipt.effective||'—'}`,
    `hotRevision=${receipt.hot||'—'}`,
    `eventCount=${camera.length}`,'',''
  ].join('\n');
  const blob=new Blob([header+cameraText(true)+'\n'],{type:'text/plain;charset=utf-8'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download=`swrlz-camera-${safeFilePart(thread?.id)}-${Date.now()}.log.txt`;
  document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
  toast(`Exported ${camera.length} camera event${camera.length===1?'':'s'}`);
}

const baseConsume=typeof consumeEvent==='function'?consumeEvent:null;
if(baseConsume){
  consumeEvent=function(event,context){
    capture(event,context);
    return baseConsume(event,context);
  };
}

function addVersionReceipt(){
  const foot=$('.sidebar-foot');
  if(!foot)return;
  let line=$('#swrlzHotVersionLine');
  if(!line){
    line=document.createElement('div');
    line.id='swrlzHotVersionLine';
    line.className='swrlz-version-line';
    line.dataset.source='runtime';
    foot.append(line);
  }
  paintMode();
}

function addTools(){
  const top=$('.topbar');
  if(!top||$('#swrlzRuntimeTools'))return;
  const bar=document.createElement('div');
  bar.id='swrlzRuntimeTools';
  bar.className='swrlz-enhance-bar';
  bar.innerHTML='<span id="swrlzMode" class="swrlz-mode">RUNTIME</span><button type="button" data-refresh>REFRESH STATE</button><button type="button" data-camera>STREAM CAMERA</button>';
  top.insertAdjacentElement('afterend',bar);
  bar.querySelector('[data-refresh]').onclick=loadOps;
  bar.querySelector('[data-camera]').onclick=()=>{
    const pre=document.createElement('pre');
    pre.className='swrlz-camera';
    pre.textContent=cameraText(true);
    const modal=document.createElement('div');
    modal.className='swrlz-modal';
    modal.innerHTML='<div class="swrlz-panel"><div class="swrlz-panel-head"><h3>Stream camera</h3><div data-actions></div></div><div data-body></div></div>';
    modal.querySelector('[data-body]').append(pre);
    const actions=modal.querySelector('[data-actions]');
    const copy=document.createElement('button');copy.textContent='COPY';copy.onclick=()=>navigator.clipboard?.writeText(cameraText(true));actions.append(copy);
    const exp=document.createElement('button');exp.textContent='EXPORT';exp.onclick=exportCameraLog;actions.append(exp);
    const close=document.createElement('button');close.textContent='CLOSE';close.onclick=()=>modal.remove();actions.append(close);
    document.body.append(modal);
  };
}

addVersionReceipt();
addTools();
loadOps();
setInterval(loadOps,15000);
window.addEventListener('pageshow',loadOps);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)loadOps()});
window.__SWRLZ_RUNTIME_HOT_TEST='runtime-only-2026-09-10T17:24Z';
})();
