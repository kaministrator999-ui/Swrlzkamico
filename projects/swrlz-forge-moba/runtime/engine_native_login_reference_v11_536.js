/* SE536_HOST_START */
let se536Pair=null,se536Bound=false;
function se536Status(message,problem=false){
 const node=document.getElementById('se476StartupStatus');
 if(node){node.textContent=message;node.dataset.error=String(!!problem);}
}
function se536Clear(){
 se536Pair=null;popupPair=null;
 const box=document.getElementById('se536LoginProof');
 if(box)box.hidden=true;
 const input=document.getElementById('se536RecoveryCode');
 if(input)input.value='';
 const button=document.getElementById('se476SignIn');
 if(button)button.textContent='Sign in with Google';
}
function se536Attach(){
 if(se536Bound)return;
 const copy=document.getElementById('se536CopyCode');
 const continueButton=document.getElementById('se536ContinueGoogle');
 if(!copy||!continueButton)return;
 se536Bound=true;
 window.addEventListener('swrlz:account-assets',event=>{if(event.detail?.authenticated===true)se536Clear();});
 copy.addEventListener('click',async()=>{
   if(!se536Pair||Date.now()>=se536Pair.until){se536Clear();se536Status('Code expired. Generate another code.',true);return;}
   const input=document.getElementById('se536RecoveryCode');
   try{
     if(!navigator.clipboard?.writeText)throw Error('CLIPBOARD_UNAVAILABLE');
     await navigator.clipboard.writeText(se536Pair.code);
     se536Status('Code copied. Continue to Google to finish connecting §E and §C.');
   }catch{
     input?.focus();input?.select();
     se536Status('Code selected. Copy it manually before continuing.');
   }
 });
 continueButton.addEventListener('click',()=>{
   if(!se536Pair||Date.now()>=se536Pair.until){se536Clear();se536Status('Code expired. Generate another code.',true);return;}
   // Direct second click preserves the popup user gesture on mobile/Quest.
   popupPair=se536Pair.pairId;
   popup=window.open(se536Pair.url,'seChatAccountConnect','popup,width=520,height=700');
   if(!popup){se536Status('Browser blocked the sign-in tab. Allow popups or open §E in Chrome.',true);return;}
   se536Status('Finish Google sign-in, then Connect. If prompted, paste the copied code.');
 });
}
async function se536PrepareLogin(){
 const gate=document.getElementById('se476StartupGate');
 if(!gate||gate.hidden)return signIn();
 se536Attach();
 if(!ready){se536Status('Connecting to §C account service. Retry when connected.',true);return;}
 if(se536Pair&&Date.now()<se536Pair.until){
   document.getElementById('se536LoginProof').hidden=false;
   se536Status('Your existing code is still valid. Copy it, then Continue to Google.');
   return;
 }
 se536Clear();
 const button=document.getElementById('se476SignIn');
 if(button)button.disabled=true;
 se536Status('Preparing secure Google connection code…');
 try{
   const result=await rpc('account.signIn',{surface:'engine-startup'});
   const url=new URL(result?.loginUrl,CHAT_ORIGIN);
   const until=Number(result?.expiresAt);
   if(url.origin!==CHAT_ORIGIN||url.pathname!=='/forge/login'||
      !/^[a-f0-9]{32}$/.test(result?.pairId||'')||
      !/^[a-f0-9]{12}$/.test(result?.recoveryCode||'')||
      url.searchParams.get('pairId')!==result.pairId||
      !Number.isFinite(until)||until<=Date.now()+5000||until>Date.now()+360000)
      throw Error('Chat returned an invalid Google pairing code.');
   se536Pair={pairId:result.pairId,code:result.recoveryCode,until,url:url.href};
   popupPair=result.pairId;
   document.getElementById('se536RecoveryCode').value=result.recoveryCode;
   document.getElementById('se536LoginProof').hidden=false;
   if(button)button.textContent='Get a new code';
   se536Status('Code ready. Copy it here on §E, then Continue to Google. One account connects both §E and §C.');
 }catch(reason){se536Clear();se536Status('Could not prepare sign-in: '+String(reason?.message||reason).slice(0,160),true);}
 finally{if(button)button.disabled=false;}
}
/* SE536_HOST_END */

/* SE536_IMPORT_START */
importFromChat:async offer=>{
 const {name,type,bytes}=offer||{};
 if(!panel||panel.hidden||!model())throw Error('Open §E Model Studio before importing an image reference.');
 if(typeof name!=='string'||!name||name.length>100||/[\x00-\x1f]/.test(name)||
    !['image/png','image/jpeg','image/webp'].includes(type)||
    !(bytes instanceof Uint8Array)||bytes.byteLength<12||bytes.byteLength>8*1024*1024)
   throw Error('Invalid Chat image reference. Select JPEG, PNG or WebP under 8 MB.');
 const png=bytes.length>=8&&[137,80,78,71,13,10,26,10].every((v,i)=>bytes[i]===v);
 const jpeg=bytes.length>=3&&bytes[0]===255&&bytes[1]===216&&bytes[2]===255;
 const webp=bytes.length>=12&&String.fromCharCode(...bytes.subarray(0,4))==='RIFF'&&String.fromCharCode(...bytes.subarray(8,12))==='WEBP';
 if(!((type==='image/png'&&png)||(type==='image/jpeg'&&jpeg)||(type==='image/webp'&&webp)))
   throw Error('Reference contents do not match the selected image type.');
 const before=model().references?.length||0;
 await atelierRefUpload([new File([bytes],name,{type})]);
 const after=model().references?.length||0;
 if(after!==before+1)throw Error('Native reference library did not confirm the import.');
 return {added:true,count:after,name};
},
/* SE536_IMPORT_END */
