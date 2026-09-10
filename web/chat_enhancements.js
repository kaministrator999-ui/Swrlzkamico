(()=>{"use strict";
const UI_VERSION='1.4.2';
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