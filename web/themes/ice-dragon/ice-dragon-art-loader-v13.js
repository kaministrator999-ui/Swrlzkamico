/* SWRLZ Ice Dragon v13 compatibility bridge — stale manifest fallback to v14 */
(()=>{'use strict';
  const debug=window.SWRLZThemeDebug||{log:(event,detail='')=>console.debug('[SWRLZ theme]',event,detail)};
  if(window.__swrlzIceDragonV14BridgeStarted){debug.log('v13-bridge-skip','already-started');return;}
  window.__swrlzIceDragonV14BridgeStarted=true;
  debug.log('v13-bridge-start','loading v14 full-resolution hydrator');
  const script=document.createElement('script');
  script.src='/live/assets/themes/ice-dragon/ice-dragon-art-loader-v14.js?v=14-fullres';
  script.async=false;
  script.onload=()=>debug.log('v13-bridge-loaded','v14');
  script.onerror=()=>debug.log('v13-bridge-failed','v14 script load error');
  (document.head||document.documentElement).appendChild(script);
})();
