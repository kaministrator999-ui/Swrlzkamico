/* SWRLZ Ice Dragon Theme controller v3.0.0 — state only */
(function(global){
  'use strict';
  const STORAGE_KEY='swrlz.chat.theme';
  const THEME='ice-dragon';
  const DEFAULT='default';
  const SELECT_ID='swrlzThemeSelect';

  function current(){return document.body?.dataset.swrlzTheme===THEME?THEME:DEFAULT;}
  function syncControl(theme){const select=document.getElementById(SELECT_ID);if(select&&select.value!==theme)select.value=theme;}
  function emit(theme){global.dispatchEvent(new CustomEvent('swrlz-theme-change',{detail:{theme}}));}
  function set(theme,persist=true){
    const body=document.body;if(!body)return;
    const next=theme===THEME?THEME:DEFAULT;
    if(next===THEME)body.dataset.swrlzTheme=THEME;else delete body.dataset.swrlzTheme;
    if(persist){try{localStorage.setItem(STORAGE_KEY,next)}catch(_){}}
    syncControl(next);emit(next);
  }
  function enable(){set(THEME,true)}
  function disable(){set(DEFAULT,true)}
  function toggle(){set(current()===THEME?DEFAULT:THEME,true)}
  function mountControl(){
    if(document.getElementById(SELECT_ID))return;
    const host=document.querySelector('.topbar-right');if(!host)return;
    const select=document.createElement('select');select.id=SELECT_ID;select.className='swrlz-theme-select';select.setAttribute('aria-label','Chat theme');select.title='Chat theme';
    const def=document.createElement('option');def.value=DEFAULT;def.textContent='Default';
    const ice=document.createElement('option');ice.value=THEME;ice.textContent='❄ Ice Dragon';
    select.append(def,ice);select.value=current();select.addEventListener('change',()=>set(select.value,true));host.insertBefore(select,host.firstChild);
  }
  function init(){
    let saved=DEFAULT;try{saved=localStorage.getItem(STORAGE_KEY)||DEFAULT}catch(_){}
    set(saved,false);mountControl();
  }
  global.IceDragonTheme={enable,disable,toggle,set,current,init,name:THEME};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})(window);
