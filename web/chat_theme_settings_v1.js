(()=>{'use strict';if(window.__swrlzThemeSettingsV1Installed)return;window.__swrlzThemeSettingsV1Installed=true;
/* Theme selection is owned by Appearance in chat_user_settings_v2.js.
   This compatibility helper only removes legacy theme controls that older
   settings layers may have left behind; it must not inject another selector. */
function removeLegacyThemeControls(){
 document.querySelector('#swrlzThemeSelect')?.remove();
 document.querySelectorAll('[data-swrlz-theme-setting]').forEach(node=>node.remove());
 document.querySelectorAll('.swrlz-settings-theme-select').forEach(select=>{
  const legacy=select.closest('[data-swrlz-theme-setting]');
  if(legacy)legacy.remove();else select.remove();
 });
}
function patch(){removeLegacyThemeControls()}
const obs=new MutationObserver(()=>patch());
function boot(){patch();obs.observe(document.documentElement,{childList:true,subtree:true});window.addEventListener('swrlz-theme-change',patch)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();})();
