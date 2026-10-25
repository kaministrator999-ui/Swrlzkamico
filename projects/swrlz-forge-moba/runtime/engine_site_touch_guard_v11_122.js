// §E v11.122: protect both the full maker and Model Atelier surfaces.
// Never call preventDefault on pointer/touch gestures or change zoom scale.
(function(){
 if(window.__SE_MAIN_TOUCH_GUARD_INSTALLED)return;
 window.__SE_MAIN_TOUCH_GUARD_INSTALLED=true;
 const editSelector='input,textarea,[contenteditable]:not([contenteditable="false"]),[role="textbox"]';
 function isEditable(node){
  if(node?.nodeType===3)node=node.parentElement;
  return Boolean(node?.closest?.(editSelector));
 }
 window.seEngineIsEditable=isEditable;
 const editableEvent=e=>isEditable(e.target)||
  Boolean(e.composedPath?.().some(isEditable));
 document.addEventListener('contextmenu',e=>{
  if(!editableEvent(e))e.preventDefault();
 },true);
 document.addEventListener('selectstart',e=>{
  if(!editableEvent(e))e.preventDefault();
 },true);
})();
