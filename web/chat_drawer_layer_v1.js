(()=>{"use strict";
if(window.__swrlzChatDrawerLayerV1)return;
const state={version:1,normalized:false,moved:false,reason:""};window.__swrlzChatDrawerLayerV1=state;
function normalize(){
  const app=document.querySelector('.app');
  const sidebar=document.querySelector('.sidebar');
  const scrim=document.getElementById('sidebarScrim')||document.querySelector('.sidebar-scrim');
  if(!app||!sidebar||!scrim){state.reason='missing-shell-node';return false;}
  if(!app.contains(sidebar)){state.reason='sidebar-outside-app';return false;}
  if(scrim.parentElement!==app){app.insertBefore(scrim,sidebar.nextSibling);state.moved=true;}
  scrim.dataset.swrlzLayerOwner='app';
  sidebar.dataset.swrlzLayerOwner='app';
  state.normalized=true;state.reason='drawer-and-scrim-share-app-layer';
  try{window.__swrlzDebug?.log('layout','drawer-layer-normalized',{moved:state.moved,parent:scrim.parentElement?.className||scrim.parentElement?.tagName||''});}catch(_){ }
  return true;
}
if(!normalize())document.addEventListener('DOMContentLoaded',normalize,{once:true});
})();
