/* SE476_ACCOUNT_BRIDGE_START */
// Expose only native, credential-free orchestration to the first-paint gate.
// Existing Chat origin owns Google tokens and validates project downloads.
window.SWYRL_ENGINE_STARTUP_ACCOUNT_476=Object.freeze({
 ready:()=>ready===true,
 connected:()=>se176AccountConnected===true,
 signIn:()=>signIn(),
 retry(){
  if(!frame)return false;
  // Reload only the existing authenticated Chat iframe. Never touch local data.
  const base=CHAT_ORIGIN+'/?forgeEmbed=1';
  frame.src=base+'&reconnect='+Date.now();
  return true;
 },
 async list(){
  await se176RefreshProjects();
  return {
   authenticated:se176AccountConnected===true,
   local:(se176LocalRows||[]).slice(0,1000).map(r=>({
    id:String(r.id),name:summaryName(r.name),updatedAt:String(r.updatedAt||'')
   })),
   cloud:se176AccountConnected===true?(se176CloudRows||[]).slice(0,1000).map(r=>({
    id:String(r.id),name:summaryName(r.name),revision:r.revision
   })):[]
  };
 },
 async loadLocal(id){
  if(typeof id!=='string'||id.length>160||!se175LocalList)return false;
  await se175RefreshLocal();
  se175LocalList.value=id;if(se175LocalList.value!==id)return false;
  const loaded=await se175LoadLocal();
  return loaded===true&&window.SWYRL_ENGINE_STARTUP_476?.readLast?.()?.id===id&&
    window.SWYRL_ENGINE_STARTUP_476.readLast().source==='local';
 },
 async loadCloud(id){
  if(!se176AccountConnected||!ready||typeof id!=='string'||id.length>160)return false;
  return (await loadCloud(id))===true;
 }
});
/* SE476_ACCOUNT_BRIDGE_END */