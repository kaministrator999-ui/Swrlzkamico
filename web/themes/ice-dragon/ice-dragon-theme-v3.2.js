/* SWRLZ Ice Dragon Theme controller v3.2.0 — state + persistent diagnostics UI */
(function(global){
  'use strict';
  const STORAGE_KEY='swrlz.chat.theme';
  const DEBUG_KEY='swrlz.theme.debug.log.v1';
  const THEME='ice-dragon';
  const DEFAULT='default';
  const SELECT_ID='swrlzThemeSelect';
  const VIEW_BUTTON_ID='swrlzThemeLogsButton';
  const VIEWER_ID='swrlzThemeLogsViewer';

  function ensureDebug(){
    if(global.SWRLZThemeDebug)return global.SWRLZThemeDebug;
    let entries=[];
    try{entries=JSON.parse(localStorage.getItem(DEBUG_KEY)||'[]');if(!Array.isArray(entries))entries=[]}catch(_){entries=[]}

    const persist=()=>{try{localStorage.setItem(DEBUG_KEY,JSON.stringify(entries))}catch(_){ }};
    const formatText=()=>entries.map(e=>`${new Date(e.at).toISOString()} ${e.event}${e.detail?' '+e.detail:''}`).join('\n');
    const renderViewer=()=>{
      const viewer=document.getElementById(VIEWER_ID);if(!viewer)return;
      const output=viewer.querySelector('[data-theme-log-output]');
      const count=viewer.querySelector('[data-theme-log-count]');
      if(count)count.textContent=`${entries.length} events`;
      if(output){output.textContent=formatText()||'No theme diagnostic events recorded yet.';output.scrollTop=output.scrollHeight;}
    };
    const log=(event,detail='')=>{
      const item={at:Date.now(),t:new Date().toISOString().slice(11,23),event:String(event),detail:typeof detail==='string'?detail:JSON.stringify(detail)};
      entries.push(item);if(entries.length>120)entries=entries.slice(-120);persist();
      console.debug('[SWRLZ theme]',item.event,item.detail);renderViewer();return item;
    };
    const clear=()=>{entries=[];try{localStorage.removeItem(DEBUG_KEY)}catch(_){ }renderViewer();};
    const dump=()=>entries.slice();
    global.SWRLZThemeDebug={log,clear,dump,formatText,renderViewer};
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

  function button(label){
    const el=document.createElement('button');el.type='button';el.textContent=label;
    Object.assign(el.style,{minHeight:'40px',padding:'0 13px',border:'1px solid rgba(145,235,255,.24)',borderRadius:'11px',cursor:'pointer',color:'#dff8ff',background:'rgba(7,27,46,.92)',fontSize:'12px',fontWeight:'750'});
    return el;
  }

  function closeViewer(){document.getElementById(VIEWER_ID)?.remove();}
  function openViewer(){
    closeViewer();
    const viewer=document.createElement('section');viewer.id=VIEWER_ID;viewer.setAttribute('role','dialog');viewer.setAttribute('aria-modal','true');viewer.setAttribute('aria-label','Theme diagnostic logs');
    Object.assign(viewer.style,{position:'fixed',inset:'0',zIndex:'10050',display:'grid',gridTemplateRows:'auto minmax(0,1fr) auto',background:'rgba(0,5,12,.985)',color:'#e8fbff',padding:'max(14px,env(safe-area-inset-top)) 12px max(14px,env(safe-area-inset-bottom))',fontFamily:'Inter,ui-sans-serif,system-ui,sans-serif'});

    const head=document.createElement('div');Object.assign(head.style,{display:'flex',alignItems:'center',justifyContent:'space-between',gap:'12px',padding:'4px 2px 12px'});
    const titleWrap=document.createElement('div');
    const title=document.createElement('strong');title.textContent='Theme diagnostic logs';Object.assign(title.style,{display:'block',fontSize:'16px'});
    const count=document.createElement('span');count.dataset.themeLogCount='1';Object.assign(count.style,{display:'block',marginTop:'3px',color:'#8fb8c9',fontSize:'11px'});
    titleWrap.append(title,count);
    const close=button('Close');close.addEventListener('click',closeViewer);head.append(titleWrap,close);

    const output=document.createElement('pre');output.dataset.themeLogOutput='1';
    Object.assign(output.style,{minHeight:'0',overflow:'auto',margin:'0',padding:'12px',border:'1px solid rgba(145,235,255,.18)',borderRadius:'14px',background:'#020a12',color:'#dffbff',font:'11px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace',whiteSpace:'pre-wrap',overflowWrap:'anywhere',userSelect:'text'});

    const actions=document.createElement('div');Object.assign(actions.style,{display:'grid',gridTemplateColumns:'repeat(3,minmax(0,1fr))',gap:'8px',paddingTop:'12px'});
    const copy=button('Copy Logs');const exportBtn=button('Export Logs');const clear=button('Clear Logs');actions.append(copy,exportBtn,clear);
    copy.addEventListener('click',async()=>{
      const text=debug.formatText();
      try{await navigator.clipboard.writeText(text);debug.log('logs-copied',`events=${debug.dump().length}`);copy.textContent='Copied ✓';setTimeout(()=>copy.textContent='Copy Logs',1300)}
      catch(error){debug.log('logs-copy-failed',String(error));copy.textContent='Copy failed';setTimeout(()=>copy.textContent='Copy Logs',1600)}
    });
    exportBtn.addEventListener('click',()=>{
      const payload={contractId:'swrlz_theme_diagnostics_v1',exportedAt:new Date().toISOString(),theme:current(),location:location.pathname,events:debug.dump()};
      const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const link=document.createElement('a');
      link.href=url;link.download=`swrlz-theme-logs-${new Date().toISOString().replace(/[:.]/g,'-')}.json`;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);debug.log('logs-exported',`events=${payload.events.length}`);
    });
    clear.addEventListener('click',()=>{debug.clear();debug.log('logs-cleared-by-user');});

    viewer.append(head,output,actions);document.body.appendChild(viewer);debug.log('logs-viewer-opened');debug.renderViewer();
  }

  function mountLogsButton(){
    if(document.getElementById(VIEW_BUTTON_ID))return;
    const dialog=document.getElementById('settingsDialog');if(!dialog){debug.log('logs-button-mount-missed','settingsDialog missing');return;}
    const host=dialog.querySelector('.dialog-actions')||dialog.querySelector('.dialog-body');if(!host){debug.log('logs-button-mount-missed','settings actions missing');return;}
    const view=button('View Theme Logs');view.id=VIEW_BUTTON_ID;view.addEventListener('click',openViewer);host.prepend(view);debug.log('logs-button-mounted');
  }

  function mountControl(){
    if(document.getElementById(SELECT_ID)){debug.log('selector-existing');mountLogsButton();return;}
    const host=document.querySelector('.topbar-right');if(!host){debug.log('selector-mount-missed','.topbar-right missing');return;}
    const select=document.createElement('select');select.id=SELECT_ID;select.className='swrlz-theme-select';select.setAttribute('aria-label','Chat theme');select.title='Chat theme';
    const def=document.createElement('option');def.value=DEFAULT;def.textContent='Default';
    const ice=document.createElement('option');ice.value=THEME;ice.textContent='❄ Ice Dragon';
    select.append(def,ice);select.value=current();select.addEventListener('change',()=>{debug.log('selector-change',select.value);set(select.value,true)});host.insertBefore(select,host.firstChild);
    debug.log('selector-mounted',select.value);mountLogsButton();
  }
  function init(){
    let saved=DEFAULT;try{saved=localStorage.getItem(STORAGE_KEY)||DEFAULT}catch(error){debug.log('theme-storage-read-error',String(error))}
    debug.log('theme-init',`saved=${saved} readyState=${document.readyState}`);
    set(saved,false);mountControl();mountLogsButton();
  }
  global.IceDragonTheme={enable,disable,toggle,set,current,init,openLogs:openViewer,name:THEME};
  if(document.readyState==='loading'){debug.log('theme-init-wait','DOMContentLoaded');document.addEventListener('DOMContentLoaded',init,{once:true})}else init();
})(window);
