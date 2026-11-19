/* SE518_REVISION_CACHE_START
  Account-side project cache: reuse existing on-device IndexedDB snapshots
  only after current authenticated cloud.list confirms the SAME revision.
  No OAuth tokens or document contents cross from the §Chat closure. */
const se518CloudCache=(()=>{
 'use strict';
 let last={status:'idle',id:null,revision:null,localId:null,reason:null};
 const valid=id=>typeof id==='string'&&id.length>0&&id.length<=160;
 const okRow=row=>row?.data?.project&&Array.isArray(row.data.scene?.actors);
 async function load(id){
  if(!valid(id)||!ready||!se176AccountConnected)return false;
  if(cloudBusy||se175Transition||se175LocalLoading)return false;
  // A metadata-only remote lookup verifies ownership, freshness and changes.
  // If the lookup is unavailable, do NOT trust an old account cache.
  await se176RefreshProjects();
  const remote=(se176CloudRows||[]).find(x=>x.id===id);
  const rev=remote?.revision;
  const verified=Number.isInteger(rev)&&rev>=1;
  if(verified){
   try{
    const metas=await se175Read();
    const match=(Array.isArray(metas)?metas:[]).find(r=>
     valid(r?.id)&&r.cloudRef?.id===id&&r.cloudRef?.revision===rev);
    if(match){
     const row=await se175Read(match.id);
     if(okRow(row)&&row.cloudRef?.id===id&&row.cloudRef.revision===rev){
      if(getProjectId()!==row.id){
       // The existing local loader saves a recovery snapshot, checks guards,
       // and rebuilds Model Atelier. Never bypass it with raw deserialization.
       if(!se175LocalList)throw Error('Local project picker is not mounted');
       await se175RefreshLocal();
       se175LocalList.value=row.id;
       if(se175LocalList.value!==row.id)throw Error('Cached project not in local picker');
       const before=getProjectId();
       await se175LoadLocal();
       if(getProjectId()!==row.id)throw Error('Local project loader did not confirm the cache');
      }
      // Preserve the user's account identity for startup resume, not local ID.
      window.SWYRL_ENGINE_STARTUP_476?.markLoaded?.('cloud',id);
      last={status:'cache-hit',id,revision:rev,localId:row.id,reason:null};
      return true;
     }
    }
   }catch(error){
    last={status:'cache-fallback',id,revision:rev,localId:null,
     reason:String(error?.message||error).slice(0,120)};
   }
  }
  // Missing/mismatched revision always invokes the original authenticated
  // downloader. Its validated successful load already writes a local mirror
  // and remembers the cloudRef through se371RememberLink.
  const loaded=await loadCloud(id);
  if(loaded!==true){last={status:'network-failed',id,revision:rev??null,localId:null,reason:'Native cloud load unconfirmed'};return false;}
  last={status:'network-loaded',id,revision:rev??null,localId:getProjectId(),reason:null};
  window.SWYRL_ENGINE_STARTUP_476?.markLoaded?.('cloud',id);
  return true;
 }
 return Object.freeze({load,inspect:()=>({...last})});
})();
window.SWYRL_ENGINE_CLOUD_CACHE_518=se518CloudCache;
/* SE518_REVISION_CACHE_END */
