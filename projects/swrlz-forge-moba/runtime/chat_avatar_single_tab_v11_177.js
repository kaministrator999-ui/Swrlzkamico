// §E v11.177: Google avatar is display-only; pairing code stays in Chat iframe.
let se177Prepared=null;
function se177SafePicture(raw){
 try{
  const url=new URL(String(raw||''));
  if(url.protocol!=='https:'||url.username||url.password||url.port||url.href.length>1024)return '';
  if(url.hostname!=='googleusercontent.com'&&!url.hostname.endsWith('.googleusercontent.com'))return '';
  return url.href;
 }catch{return '';}
}
function se177ShowPicture(mark,raw){
 mark.replaceChildren();
 const picture=se177SafePicture(raw);
 if(!picture){mark.textContent='G';return;}
 const image=document.createElement('img');
 image.alt='';image.setAttribute('aria-hidden','true');
 image.referrerPolicy='no-referrer';
 image.style.cssText='display:block;width:100%;height:100%;object-fit:cover;border-radius:50%;';
 image.src=picture;
 image.onerror=()=>{if(mark.contains(image)){mark.replaceChildren();mark.textContent='G';}};
 mark.append(image);
}
function se177ResetPrepared(){
 se177Prepared=null;popupPair=null;
 const button=document.getElementById('seChatSignIn');
 if(button)button.textContent='Sign in with Google';
}
async function signIn(){
 if(!ready){setStatus('Chat is still connecting. Try sign-in when it is ready.',true);return;}
 const button=document.getElementById('seChatSignIn');
 if(se177Prepared&&Date.now()<se177Prepared.until){
  // A separate user gesture avoids popup blocking, and allows copying first.
  // Never put the recovery proof in the URL or the §E host.
  popup=window.open(se177Prepared.url,'seChatAccountConnect','popup,width=520,height=700');
  if(!popup){setStatus('The browser blocked Google sign-in. Permit popups or open §E directly in Chrome.',true);return;}
  setStatus('Complete Google sign-in. If the opener cannot reconnect, enter the code copied from § Chat.');
  return;
 }
 se177ResetPrepared();
 if(button)button.disabled=true;
 try{
  // The Chat-origin iframe displays an independent short-lived proof BEFORE
  // we open the popup or navigate; it never exposes that proof to this host.
  const result=await rpc('account.signIn');
  const url=new URL(result.loginUrl,CHAT_ORIGIN);
  if(url.origin!==CHAT_ORIGIN||url.pathname!=='/forge/login'||!bounded(result.pairId,128)||url.searchParams.get('pairId')!==result.pairId)throw Error('INVALID_LOGIN_URL');
  popupPair=result.pairId;
  se177Prepared={pairId:result.pairId,url:url.href,until:Date.now()+270000};
  if(button)button.textContent='Continue to Google';
  setStatus('First copy the one-time code shown at the TOP of embedded Chat. Then tap Continue to Google. In a single-tab browser, the code will already be on your clipboard.');
 }catch(error){se177ResetPrepared();setStatus('Could not prepare Google connection: '+summaryName(error.message),true);}
 finally{if(button)button.disabled=false;}
}