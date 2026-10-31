// §E v11.180: a click/tap outside the Chat panel slides it away.
// The iframe is never unmounted and no pointer event is canceled or replayed.
let se180CloseTimer=null,se180OpenFrame=null;
function se180Duration(){
 return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches?0:210;
}
function se180CancelAnimation(){
 if(se180CloseTimer!==null){clearTimeout(se180CloseTimer);se180CloseTimer=null;}
 if(se180OpenFrame!==null){cancelAnimationFrame(se180OpenFrame);se180OpenFrame=null;}
}
function openPanel(){
 se180CancelAnimation();
 open=true;panel.hidden=false;panel.inert=false;panel.removeAttribute('aria-hidden');
 document.getElementById('seChatToggle').setAttribute('aria-expanded','true');
 // One frame ensures the previously hidden panel can animate from offscreen.
 se180OpenFrame=requestAnimationFrame(()=>{
  se180OpenFrame=null;
  if(open&&!panel.hidden)panel.classList.add('se180-chat-visible');
 });
 document.getElementById('seChatClose').focus();
 if(!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';
 if(port)send('host.visibility',{visible:true});
}
function closePanel(restoreFocus=true){
 if(!open)return;
 se180CancelAnimation();
 revoke('Chat panel closed.');
 open=false;panel.inert=true;panel.setAttribute('aria-hidden','true');
 panel.classList.remove('se180-chat-visible');
 const toggle=document.getElementById('seChatToggle');
 toggle.setAttribute('aria-expanded','false');
 // Outside selection must keep focus on the editor control that was tapped.
 if(restoreFocus!==false)toggle.focus();
 se180CloseTimer=setTimeout(()=>{
  se180CloseTimer=null;
  if(!open)panel.hidden=true;
 },se180Duration());
}
function se180Outside(event){
 if(!open||!panel||panel.hidden)return;
 if(event.isPrimary===false)return;
 if(event.type==='pointerdown'&&event.pointerType==='mouse'&&event.button!==0)return;
 const toggle=document.getElementById('seChatToggle');
 const path=typeof event.composedPath==='function'?event.composedPath():[];
 if(path.includes(panel)||path.includes(toggle)||panel.contains(event.target)||toggle?.contains(event.target))return;
 // Keep the original pointer event untouched: editors still receive the tap.
 closePanel(false);
}
function se180InstallDismiss(){
 document.addEventListener('pointerdown',se180Outside,true);
 // Keyboard-activated controls outside the panel can also dismiss it.
 document.addEventListener('click',se180Outside,true);
}