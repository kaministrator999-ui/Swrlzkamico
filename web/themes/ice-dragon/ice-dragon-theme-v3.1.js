/* SWRLZ Ice Dragon Theme controller v3.1.0 — state + diagnostics */
(function(global){
  'use strict';
  const STORAGE_KEY='swrlz.chat.theme';
  const DEBUG_KEY='swrlz.theme.debug.log.v1';
  const THEME='ice-dragon';
  const DEFAULT='default';
  const SELECT_ID='swrlzThemeSelect';
  const debugEnabled=()=>new URLSearchParams(location.search).get('themeDebug')==='1';

  function ensureDebug(){
    if(global.SWRLZThemeDebug)return global.SWRLZThemeDebug;
    let entries=[];
    try{entries=JSON.parse(localStorage.getItem(DEBUG_KEY)||'[]');if(!Array.isArray(entries))entries=[]}catch(_){entries=[]}
    const panel=()=>{
      if(!debugEnabled())return null;
      let el=document.getElementById('swrlzThemeDebugPanel');
      if(el)return el;
      el=document.createElement('pre');el.id='swrlzThemeDebugPanel';
      Object.assign(el.style,{position:'fixed',left:'8px',right:'8px',bottom:'8px',zIndex:'9999',maxHeight:'34vh',overflow:'auto',margin:'0',padding:'9px',border:'1px solid rgba(120,240,255,.35)',borderRadius:'10px',background:'rgba(0,7,14,.94)',color:'#dffbff',font:'10px/1.35 ui-monospace,monospace',whiteSpace:'pre-wrap',pointerEvents:'none'});
      document.body?.appendChild(el);return el;
    };
    const render=()=>{const el=panel();if(el)el.textContent=entries.slice(-28).map(e=>`${e.t} ${e.event}${e.detail?' '+e.detail:''}`).join('\n')};
    const log=(event,detail='')=>{
      const item={at:Date.now(),t:new Date().toISOString().slice(11,23),event:String(event),detail:typeof detail==='string'?detail:JSON.stringify(detail)};
      entries.push(item);if(entries.length>120)entries=entries.slice(-120);
      try{localStorage.setItem(DEBUG_KEY,JSON.stringify(entries))}catch(_){ }
      console.debug('[SWRLZ theme]',item.event,item.detail);render();return item;
    };
    const clear=()=>{entries=[];try{localStorage.removeItem(DEBUG_KEY)}catch(_){ }render()};
    const dump=()=>entries.slice();
    global.SWRLZThemeDebug={log,clear,dump,get enabled(){return debugEnabled()}};
    log('debug-ready',`readyState=${document.readyState}`);
    return global.SWRLZThemeDebug;
  }
  const debug=ensureDebug();

  function current(){return document.body?.dataset.swrlzTheme===THEME?THEME:DEFAULT;}
  function syncControl(theme){const select=document.getElementById(SELECT_ID);if(select&&select.value!==theme){select.value=theme;debug.log('selector-sync',theme)}}
  function emit(theme){debug.log('theme-event-dispatch',theme);global.dispatchEvent(new CustomEvent('swrlz-theme-change',{detail:{theme}}));}
  function set(theme,persist=true){
    const body=document.body;if(!body){debug.log('theme-set-deferred','body-missing');return;}
    const next=theme===THEME?THEME:DEFAULT;
    debug.log('theme-set-start',`requested=${theme} next=${next} persist=${persist}`);
    if(next===THEME)body.dataset.swrlzTheme=THEME;else delete body.dataset.swrlzTheme;
    if(persist){try{localStorage.setItem(STORAGE_KEY,next);debug.log('theme-storage-write',next)}catch(error){debug.log('theme-storage-error',String(error))}}
    syncControl(next);emit(next);
    debug.log('theme-set-complete',`body=${body.dataset.swrlzTheme||DEFAULT}`);
  }
  function enable(){set(THEME,true)}
  function disable(){set(DEFAULT,true)}
  function toggle(){set(current()===THEME?DEFAULT:THEME,true)}
  function mountControl(){
    if(document.getElementById(SELECT_ID)){debug.log('selector-existing');return;}
    const host=document.querySelector('.topbar-right');if(!host){debug.log('selector-mount-missed','.topbar-right missing');return;}
    const select=document.createElement('select');select.id=SELECT_ID;select.className='swrlz-theme-select';select.setAttribute('aria-label','Chat theme');select.title='Chat theme';
    const def=document.createElement('option');def.value=DEFAULT;def.textContent='Default';
    const ice=document.createElement('option');ice.value=THEME;ice.textContent='❄ Ice Dragon';
    select.append(def,ice);select.value=current();select.addEventListener('change',()=>{debug.log('selector-change',select.value);set(select.value,true)});host.insertBefore(select,host.firstChild);
    debug.log('selector-mounted',select.value);
  }
  function init(){
    let saved=DEFAULT;try{saved=localStorage.getItem(STORAGE_KEY)||DEFAULT}catch(error){debug.log('theme-storage-read-error',String(error))}
    debug.log('theme-init',`saved=${saved} readyState=${document.readyState}`);
    set(saved,false);mountControl();
  }
  global.IceDragonTheme={enable,disable,toggle,set,current,init,name:THEME};
  if(document.readyState==='loading'){debug.log('theme-init-wait','DOMContentLoaded');document.addEventListener('DOMContentLoaded',init,{once:true})}else init();
})(window);
