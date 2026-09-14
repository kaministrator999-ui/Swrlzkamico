(()=>{"use strict";
if(window.__swrlzRuntimeLoaderV2)return;
const REV='53';
const ROOT='/live/assets/';
const diagnostics={contractId:'swrlz_chat_phased_boot_v2',revision:REV,startedAt:performance.now(),critical:[],background:[],styleErrors:[],scriptErrors:[],mainReady:false,backgroundReady:false};
window.__swrlzRuntimeLoaderV2=diagnostics;

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
const critical=[
  'chat_frontend_boot.js',
  'chat_boot_guard.js',
  'chat_admin_session.js',
  'chat_enhancements.js',
  'chat_google_server_config.js',
  'chat_version.js',
  'themes/ice-dragon/ice-dragon-theme-v3.2.js',
  'chat_account_identity_v1.js',
  'chat_user_settings_v2.js',
  'chat_boot_ready.js'
];
const background=[
  'themes/ice-dragon/ice-dragon-art-loader-v17.js',
  'themes/ice-dragon/ice-dragon-wallpaper-v21.js',
  'chat_stream_focus.js',
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
  'chat_response_layout_v1.js',
  'chat_theme_settings_v1.js',
  'chat_scroll_gesture_v1.js'
];
const src=path=>`${ROOT}${path}?v=${REV}`;

function startStyles(){
  for(const path of styles){
    if(document.querySelector(`link[data-swrlz-runtime-style="${CSS.escape(path)}"]`))continue;
    const link=document.createElement('link');
    link.rel='stylesheet';link.href=src(path);link.dataset.swrlzRuntimeStyle=path;
    link.addEventListener('error',()=>diagnostics.styleErrors.push(path),{once:true});
    document.head.appendChild(link);
  }
}
function loadOrdered(paths,bucket){
  return new Promise(resolve=>{
    if(!paths.length)return resolve();
    let settled=0;
    const done=()=>{settled++;if(settled===paths.length)resolve()};
    for(const path of paths){
      const script=document.createElement('script');
      script.src=src(path);script.async=false;script.dataset.swrlzRuntimeScript=path;
      script.addEventListener('load',()=>{bucket.push(path);done()},{once:true});
      script.addEventListener('error',()=>{diagnostics.scriptErrors.push(path);done()},{once:true});
      document.body.appendChild(script);
    }
  });
}
function loadOne(path){
  return new Promise(resolve=>{
    const script=document.createElement('script');script.src=src(path);script.async=false;script.dataset.swrlzRuntimeScript=path;
    script.addEventListener('load',resolve,{once:true});
    script.addEventListener('error',()=>{diagnostics.scriptErrors.push(path);resolve()},{once:true});
    document.body.appendChild(script);
  });
}
async function boot(){
  startStyles();
  await loadOne('chat_legacy_state_retirement.js');
  if(window.__swrlzLegacyChatState?.reloadRequired)return;
  await loadOrdered(critical,diagnostics.critical);
  diagnostics.mainReady=true;diagnostics.mainReadyAt=performance.now();
  document.documentElement.classList.add('swrlz-main-chat-ready');
  window.dispatchEvent(new CustomEvent('swrlz:main-chat-ready',{detail:{revision:REV,at:diagnostics.mainReadyAt}}));
  const run=async()=>{
    await loadOrdered(background,diagnostics.background);
    diagnostics.backgroundReady=true;diagnostics.backgroundReadyAt=performance.now();
    window.dispatchEvent(new CustomEvent('swrlz:chat-background-ready',{detail:{revision:REV,errors:[...diagnostics.scriptErrors],at:diagnostics.backgroundReadyAt}}));
  };
  if('requestIdleCallback'in window)requestIdleCallback(()=>run(),{timeout:900});else setTimeout(run,0);
}
boot().catch(error=>{diagnostics.fatal=String(error?.message||error);console.error('[§wyrlz chat boot]',error)});
})();
