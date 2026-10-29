// §E v11.117 — suppress browser-native long-hold popups in Model Atelier.
// No touch/pointer default is cancelled here: orbit, pinch, drag, scrolling
// and the in-editor numeric keyboard remain owned by their native handlers.
function seAtelierCalloutInstall(){
 if(seAtelierCalloutInstall.installed)return;
 seAtelierCalloutInstall.installed=true;
 const activeScope=target=>{
  const panel=document.getElementById('modelAtelierPanel');
  if(!panel||panel.hidden||!target)return false;
  if(panel.contains(target))return true;
  const numpad=document.getElementById('seMobileNumberPad');
  return !!(numpad&&!numpad.hidden&&numpad.contains(target));
 };
 document.addEventListener('contextmenu',event=>{
  if(activeScope(event.target))event.preventDefault();
 },true);
 document.addEventListener('selectstart',event=>{
  if(!activeScope(event.target))return;
  // Editable fields retain native caret, text selection and paste support.
  // This cancels text-selection callouts on labels, buttons and viewport chrome.
  if(event.target?.closest?.('input,textarea,select,[contenteditable],[role="textbox"]'))return;
  event.preventDefault();
 },true);
}
