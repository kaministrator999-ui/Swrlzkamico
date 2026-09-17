(()=>{"use strict";
if(window.__swrlzSidebarCommandV1)return;window.__swrlzSidebarCommandV1=true;
const $=(s,r=document)=>r.querySelector(s),all=(s,r=document)=>[...r.querySelectorAll(s)];
const closeDrawer=()=>document.body.classList.remove('sidebar-open');
const modal=(title,body)=>{const host=document.createElement('div');host.className='swrlz-modal';host.innerHTML=`<section class="swrlz-panel swrlz-sidebar-panel"><header class="swrlz-panel-head"><div><h2>${title}</h2><p class="swrlz-account-sub">§wyrlz Chat control surface</p></div><button type="button" data-close>Close</button></header><div class="swrlz-sidebar-panel-body">${body}</div></section>`;host.addEventListener('click',e=>{if(e.target===host||e.target.closest('[data-close]'))host.remove()});document.body.appendChild(host);closeDrawer();return host};
const nav=[
 ['chats','▣','Chats','Conversation threads'],['bookmarks','☆','Bookmarks','Saved response positions'],['pinned','◇','Pinned','Priority conversations'],['settings','⚙','Settings','Account and Chat preferences'],['knowledge','▤','Knowledge','Knowledge workspace'],['tools','⌁','Tools','Available action surfaces'],['activity','⌁','Activity Log','Runtime and response traces'],['help','?','Help','Chat controls and diagnostics']
];
function install(){const side=$('.sidebar');if(!side||$('#swrlzSidebarCommand'))return;const newChat=$('.new-chat');const label=$('.sidebar-label');const threads=$('.thread-list');if(!newChat||!label||!threads)return;
 const command=document.createElement('nav');command.id='swrlzSidebarCommand';command.className='swrlz-sidebar-command';command.setAttribute('aria-label','Chat navigation');command.innerHTML=nav.map(([id,icon,name,desc])=>`<button type="button" data-swrlz-nav="${id}" title="${desc}"><span class="swrlz-nav-icon">${icon}</span><span>${name}</span></button>`).join('');newChat.after(command);
 label.classList.add('swrlz-thread-label');
 command.addEventListener('click',e=>{const b=e.target.closest('[data-swrlz-nav]');if(!b)return;const id=b.dataset.swrlzNav;
  if(id==='chats'){threads.scrollTo?.({top:0,behavior:'smooth'});return}
  if(id==='settings'){const gear=$('#swrlzAccountSettings');if(gear){gear.click();closeDrawer();return}}
  if(id==='activity'){const traces=all('.trace,.activity-log');const expanded=traces.filter(x=>x.open||x.offsetParent!==null).length;modal('Activity Log',`<div class="swrlz-setting-row"><strong>Response activity</strong><span>${traces.length?`${traces.length} trace surface${traces.length===1?'':'s'} available in the loaded conversation. Expand Activity log on a response for its exact runtime trace.`:'No response activity traces are loaded in this conversation yet.'}</span></div>`);return}
  if(id==='bookmarks'||id==='pinned'){modal(id==='bookmarks'?'Bookmarks':'Pinned',`<div class="swrlz-setting-row"><strong>${id==='bookmarks'?'Response bookmarks':'Pinned conversations'}</strong><span>The navigation surface is installed. Durable ${id} state is not enabled yet, so this panel will not pretend items exist.</span></div>`);return}
  if(id==='knowledge'||id==='tools'){modal(id==='knowledge'?'Knowledge':'Tools',`<div class="swrlz-setting-row"><strong>${id==='knowledge'?'Knowledge workspace':'Action tools'}</strong><span>This destination is reserved in the Chat control surface. Its backing capability is not enabled in this runtime yet.</span></div>`);return}
  modal('Help','<div class="swrlz-setting-row"><strong>Chat navigation</strong><span>Use Chats for threads, Settings for account and Chat preferences, and Activity Log for runtime trace access. Disabled backing capabilities are explicitly identified rather than simulated.</span></div>');
 });
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
})();
