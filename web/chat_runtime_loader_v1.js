(()=>{"use strict";
if(window.__swrlzRuntimeLoaderInstalled)return;
window.__swrlzRuntimeLoaderInstalled=true;

const current=document.currentScript;
const currentUrl=current?.src?new URL(current.src,location.href):null;
const revision=currentUrl?.searchParams.get('v')||'runtime';
const RAW_BASE='https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/runtime/web/';
const styles=[
  'chat_boot_guard.css',
  'chat_enhancements.css',
  'chat_user_settings_v2.css',
  'themes/ice-dragon/ice-dragon-theme.css',
  'themes/ice-dragon/ice-dragon-art-v2.css',
  'themes/ice-dragon/ice-dragon-shell-v1.css',
  'themes/ice-dragon/ice-dragon-brand-v1.css',
  'themes/ice-dragon/ice-dragon-polish-v2.css',
  'themes/ice-dragon/ice-dragon-response-layout-v1.css',
  'chat_mobile_viewport_fix.css',
  'chat_code_artifacts.css'
];
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

function rawUrl(path){return `${RAW_BASE}${path}?swrlz_runtime=${encodeURIComponent(revision)}`}
function markIceDragonEarly(){
  let theme='ice-dragon';
  try{theme=localStorage.getItem('swrlz.chat.theme')||'ice-dragon'}catch(_){}
  if(theme==='ice-dragon')document.body?.setAttribute('data-swrlz-theme','ice-dragon');
}
function loadStyle(path){return new Promise((resolve,reject)=>{
  const node=document.createElement('link');
  node.rel='stylesheet';
  node.href=rawUrl(path);
  node.dataset.swrlzRuntimeStyle=path;
  node.onload=()=>resolve(path);
  node.onerror=()=>reject(new Error(`Runtime style failed: ${path}`));
  document.head.appendChild(node);
})}
function loadScript(path){return new Promise((resolve,reject)=>{
  const node=document.createElement('script');
  node.src=rawUrl(path);
  node.async=false;
  node.dataset.swrlzRuntimeScript=path;
  node.onload=()=>resolve(path);
  node.onerror=()=>reject(new Error(`Runtime script failed: ${path}`));
  document.body.appendChild(node);
})}

markIceDragonEarly();
const startedAt=performance.now();
const styleJobs=styles.map(loadStyle);
const scriptJobs=scripts.map(loadScript);

Promise.all([...styleJobs,...scriptJobs]).then(()=>{
  document.documentElement.dataset.swrlzRuntimeHydration='ready';
  const detail={contract:'direct-runtime-source-parallel-v2',revision,styleCount:styles.length,scriptCount:scripts.length,durationMs:Math.round(performance.now()-startedAt)};
  window.dispatchEvent(new CustomEvent('swrlz:runtime-hydrated',{detail}));
}).catch(error=>{
  document.documentElement.dataset.swrlzRuntimeHydration='failed';
  const detail={contract:'direct-runtime-source-parallel-v2',revision,error:String(error?.message||error)};
  console.error('[§wyrlz runtime hydration]',error);
  window.dispatchEvent(new CustomEvent('swrlz:runtime-hydration-failed',{detail}));
  try{typeof toast==='function'&&toast('Chat enhancements could not finish loading. Refresh to retry.')}catch(_){}
});

window.__swrlzRuntimeLoader=Object.freeze({
  version:2,
  contract:'direct-runtime-source-parallel-v2',
  revision,
  source:'github-runtime-raw-direct',
  styleCount:styles.length,
  scriptCount:scripts.length,
  policy:'one-vercel-loader-direct-runtime-assets-parallel-download-ordered-script-execution'
});
})();
