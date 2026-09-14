(()=>{"use strict";
if(window.__swrlzRuntimeLoaderInstalled)return;
window.__swrlzRuntimeLoaderInstalled=true;

const nativeFetch=window.fetch.bind(window);
const current=document.currentScript;
const currentUrl=current?.src?new URL(current.src,location.href):null;
const revision=currentUrl?.searchParams.get('v')||'runtime';
const scripts=[
  'chat_frontend_boot.js',
  'chat_boot_guard.js',
  'chat_admin_session.js',
  'chat_enhancements.js',
  'chat_google_server_config.js',
  'chat_stream_focus.js',
  'chat_version.js',
  'themes/ice-dragon/ice-dragon-theme-v3.2.js',
  'themes/ice-dragon/ice-dragon-art-loader-v17.js',
  'themes/ice-dragon/ice-dragon-wallpaper-v21.js',
  'chat_code_artifacts.js',
  'chat_stream_incremental.js',
  'chat_committed_contract_bridge.js',
  'chat_committed_output_v3.js',
  'chat_activity_immediate.js',
  'chat_user_time_context.js',
  'chat_context_canonical.js',
  'chat_background_resume_v2.js',
  'chat_response_presence.js',
  'chat_transcript_sync.js',
  'chat_terminal_integrity.js',
  'chat_context_capacity.js',
  'chat_context_camera.js',
  'chat_response_polish.js',
  'chat_turn_integrity_v1.js',
  'chat_account_identity_v1.js',
  'chat_response_layout_v1.js',
  'chat_theme_settings_v1.js',
  'chat_user_settings_v2.js',
  'chat_scroll_gesture_v1.js',
  'chat_boot_ready.js'
];

function urlFor(path){return `/live/assets/${path}?v=${encodeURIComponent(revision)}`}
async function fetchSource(path){
  const response=await nativeFetch(urlFor(path),{cache:'force-cache'});
  if(!response.ok)throw new Error(`Runtime asset ${path} returned HTTP ${response.status}`);
  return response.text();
}
function executeSource(path,source){
  const node=document.createElement('script');
  node.dataset.swrlzHydratedAsset=path;
  node.textContent=`${source}\n//# sourceURL=${location.origin}${urlFor(path)}`;
  document.body.appendChild(node);
  node.remove();
}

const jobs=scripts.map(path=>fetchSource(path).then(source=>({path,source})));
const startedAt=performance.now();

aSyncHydrate();
async function aSyncHydrate(){
  try{
    for(const job of jobs){
      const {path,source}=await job;
      executeSource(path,source);
    }
    document.documentElement.dataset.swrlzRuntimeHydration='ready';
    const detail={contract:'parallel-fetch-ordered-exec-v1',revision,assetCount:scripts.length,durationMs:Math.round(performance.now()-startedAt)};
    window.dispatchEvent(new CustomEvent('swrlz:runtime-hydrated',{detail}));
  }catch(error){
    document.documentElement.dataset.swrlzRuntimeHydration='failed';
    const detail={contract:'parallel-fetch-ordered-exec-v1',revision,error:String(error?.message||error)};
    console.error('[§wyrlz runtime hydration]',error);
    window.dispatchEvent(new CustomEvent('swrlz:runtime-hydration-failed',{detail}));
    try{typeof toast==='function'&&toast('Chat enhancements could not finish loading. Refresh to retry.')}catch(_){}
  }
}

window.__swrlzRuntimeLoader=Object.freeze({
  version:1,
  contract:'parallel-fetch-ordered-exec-v1',
  revision,
  assetCount:scripts.length,
  policy:'fetch-runtime-enhancements-concurrently-execute-in-dependency-order'
});
})();
