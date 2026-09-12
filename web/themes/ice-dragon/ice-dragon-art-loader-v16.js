/* SWRLZ Ice Dragon compatibility bridge v16 -> v17 */
(()=>{'use strict';
if(window.__swrlzIceDragonV17Bridge)return;
window.__swrlzIceDragonV17Bridge=true;
const s=document.createElement('script');
s.src='/live/assets/themes/ice-dragon/ice-dragon-art-loader-v17.js?v=17';
s.async=false;
s.dataset.swrlzIceDragonBridge='v17';
(document.head||document.documentElement).appendChild(s);
})();
