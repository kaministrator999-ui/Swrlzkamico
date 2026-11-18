/* SE506_UV_BUTTON_OWNERSHIP_START
   The original UV toolbar refresh must not own nested UV preview/atlas buttons.
   Preserve independent tool state even when base UV selection is unavailable. */
const se506Prior336UpdateUI=se336UpdateUI;
se336UpdateUI=function(...args){
 const root=document.getElementById('modelAtelierUVLayout');
 if(!root)return se506Prior336UpdateUI.apply(this,args);
 const owned=new Set(root.querySelectorAll('.se336-uv-actions > button'));
 const independent=Array.from(root.querySelectorAll('button'))
  .filter(button=>!owned.has(button))
  .map(button=>({button,disabled:button.disabled}));
 const result=se506Prior336UpdateUI.apply(this,args);
 for(const {button,disabled} of independent){
  if(button.isConnected!==false)button.disabled=disabled;
 }
 // Recompute after restoring nested state, so newly selected saved topology
 // can enable the primary UV atlas action. Apply/export still require preview.
 if(root.querySelector('#se503AtlasTool'))se503Refresh();
 return result;
};
/* SE506_UV_BUTTON_OWNERSHIP_END */