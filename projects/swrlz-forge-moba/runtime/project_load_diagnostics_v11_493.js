/* §E v11.493 — ZIP signature fallback and truthful account-project open errors.
 * All downloads are read-only; no new save or destructive retry behavior. */
const se493ProjectLoad=(()=>{
 'use strict';
 let lastError='';
 const bounded=e=>String(e?.message||e||'Unknown account error').slice(0,210);
 const transient=e=>/Failed to fetch|fetch failed|networkerror|network request failed|connection timed out|Chat connection timed out|HTTP 50[234]/i.test(bounded(e));
 function reset(){lastError=''}
 function failure(e){lastError=bounded(e);return lastError}
 async function fetchProject(projectId,onProgress=()=>{}){
  for(let attempt=1;attempt<=3;attempt++){
   try{
    const response=await rpc('cloud.load',{projectId});
    if(response?.project?.id!==projectId)throw Error('Account returned a different project ID. Nothing was opened.');
    return response;
   }catch(e){
    if(!transient(e)||attempt===3||!ready||!se176AccountConnected){
     throw Error(transient(e)?'§C account download unavailable after '+attempt+
      ' attempt(s): '+bounded(e):bounded(e));
    }
    onProgress('§C account download interrupted; retry '+(attempt+1)+'/3');
    await new Promise(resolve=>setTimeout(resolve,700*attempt));
   }
  }
  throw Error('Account read unavailable');
 }
 async function parseModel(file,onProgress=()=>{}){
  if(!file)throw Error('No model file selected');
  // Android pickers sometimes present ZIP bytes with a generic .json name.
  // Read the header instead of assuming a filename determines the format.
  const header=new Uint8Array(await file.slice(0,4).arrayBuffer());
  const zip=header.length>=4&&header[0]===0x50&&header[1]===0x4b&&(
    header[2]===3&&header[3]===4||
    header[2]===5&&header[3]===6||
    header[2]===7&&header[3]===8);
  const namedZip=/\.zip$/i.test(String(file.name||''));
  if(!zip&&namedZip)throw Error('Selected .zip does not contain a valid ZIP header');
  if(!zip)return se492ModelUpload.parse(file,onProgress);
  onProgress('ZIP detected; checking archive member…');
  const wrapper={
    name:String(file.name||'model')+'.zip',
    size:file.size,
    arrayBuffer:()=>file.arrayBuffer()
  };
  return se492ModelUpload.parse(wrapper,onProgress);
 }
 return Object.freeze({fetchProject,parseModel,reset,failure,getError:()=>lastError,transient});
})();
window.SWYRL_ENGINE_PROJECT_LOAD_493=se493ProjectLoad;
