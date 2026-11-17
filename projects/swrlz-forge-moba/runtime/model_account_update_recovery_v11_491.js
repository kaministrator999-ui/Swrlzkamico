/* §E v11.491 — cloud read retry; no write retries or identity bypasses.
   Inserted inside se489MyProjectUpdate so NAME is the existing trusted
   selected-card reader and only cloud.load is retried. */
const se491TransientRead = error =>
 /failed to fetch|fetch failed|networkerror|network error|network request failed|connection timed out|load failed|http 50[234]/i
 .test(String(error?.message||error));
async function se491SelectedDocument(record,source,onProgress=()=>{}){
 const tries=source==='cloud'?3:1;
 for(let i=1;i<=tries;i++){
  try{
   return await NAME.selectedDocument(record,source);
  }catch(error){
   if(i===tries||!se491TransientRead(error)||source!=='cloud'){
    if(source==='cloud'&&se491TransientRead(error)){
     const out=Error('Could not reach §C account storage after '+i+
      ' attempts. No model changes were sent. Reopen § Chat / Sign in, then use Retry Update.');
     out.se491Recoverable=true;throw out;
    }
    throw error;
   }
   if(!ready||!se176AccountConnected){
    const out=Error('§C account disconnected. Sign in again; your selected model file is retained for Retry Update.');
    out.se491Recoverable=true;throw out;
   }
   onProgress('§C account read interrupted · retry '+(i+1)+'/'+tries+'…');
   await new Promise(resolve=>setTimeout(resolve,700*i));
  }
 }
 throw Error('Account read unavailable');
}
window.SWYRL_ENGINE_UPDATE_READ_491=Object.freeze({read:se491SelectedDocument,isTransient:se491TransientRead});
