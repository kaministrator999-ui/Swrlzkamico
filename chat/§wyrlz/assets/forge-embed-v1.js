/* Canonical Chat-origin broker. Account credentials never cross the frame boundary. */
(() => {
  "use strict";
  const PROTOCOL = "swrlz-forge-chat-v1";
  const PARENTS = new Set([
    "https://kamiloki-swrlz-forge-moba.static.hf.space",
    "https://kamiloki-swrlz-forge-moba.hf.space"
  ]);
  const embedded = window.parent !== window && new URLSearchParams(location.search).get("forgeEmbed") === "1";
  const nativeFetch = window.fetch.bind(window);
  let binding = null, port = null, token = "", expiresAt = 0, accountEpoch = 0;
  let thread = "", lease = "", hostVisible = false, pairing = null, cloudBusy = false;
  const pending = new Map(), seenBatches = new Set(), cloudCatalog = new Map();
  const id = () => crypto.randomUUID().replaceAll("-", "");
  const validBinding = value => typeof value === "string" && /^[A-Za-z0-9_-]{16,128}$/.test(value);
  const envelope = (type, payload, requestId = id()) => ({protocol:PROTOCOL,...binding,type,requestId,payload});
  const sameBinding = value => value && value.protocol === PROTOCOL && binding && value.hostId === binding.hostId && value.channelId === binding.channelId;
  const isAuthenticated = () => !!token && Date.now() < expiresAt;
  const emit = (name, detail) => window.dispatchEvent(new CustomEvent(name,{detail}));
  const error = message => new Error(message);
  const send = (type, payload, requestId, transfer = []) => {
    if(!port) throw error("The §e connection is unavailable.");
    port.postMessage(envelope(type,payload,requestId),transfer);
  };
  const rpc = (type, payload, timeout = 20000) => new Promise((resolve,reject) => {
    if(!port){reject(error("Open Chat from the §e panel to connect."));return;}
    const requestId = id();
    const timer = setTimeout(() => {pending.delete(requestId);reject(error("The §e connection timed out."));},timeout);
    pending.set(requestId,{resolve,reject,timer});
    try{send(type,payload,requestId);}catch(reason){clearTimeout(timer);pending.delete(requestId);reject(reason);}
  });
  const publicAccount = user => ({authenticated:!!user,user:user?{name:String(user.displayName || "Google Account").slice(0,120)}:null});
  const revoke = reason => {
    lease="";seenBatches.clear();
    if(port)send("host.revoke",{reason:String(reason||"connection-changed").slice(0,80)});
  };
  const clearAccount = () => {
    token="";expiresAt=0;accountEpoch++;pairing=null;cloudCatalog.clear();revoke("account-changed");
    if(port)send("account.status",publicAccount(null));
    emit("swrlz-forge-account-changed",{signedIn:false});
  };
  // A 401 from an unrelated protected feature (such as GitHub OAuth) is NOT
  // evidence that the verified Google/Chat embed session has been revoked.
  const sessionRejected = async (response,path) => {
    if(response.status !== 401)return false;
    const value = await response.clone().json().catch(()=>({}));
    const code = String(value?.detail || value?.code || "");
    return ["FORGE_EMBED_SESSION_INVALID","FORGE_PARENT_LOGIN_REVOKED",
      "FORGE_EMBED_CREDENTIAL_REQUIRED","FORGE_EMBED_CREDENTIAL_INVALID"].includes(code)
      || (path === "/api/account/me" && code === "ACCOUNT_SESSION_INVALID");
  };
  const protectedPath = path => /^\/api\/(?:lalm_station(?:\/|$)|chat_state(?:\/|$)|chatgpt_archive(?:\/|$)|chat(?:\/|$)|account(?:\/|$)|github(?:\/|$)|forge\/projects(?:\/|$)|forge\/embed\/(?:presence|logout)(?:\/|$))/.test(path)
    && path !== "/api/account/status";
  if(embedded){
    document.documentElement.classList.add("forge-embedded");
    window.fetch = async (input, init = {}) => {
      const url = new URL(typeof input === "string" || input instanceof URL ? input : input.url,location.href);
      if(url.origin !== location.origin || !protectedPath(url.pathname))return nativeFetch(input,init);
      if(!isAuthenticated()){
        if(token)clearAccount();
        return new Response(JSON.stringify({detail:"FORGE_GOOGLE_CONNECTION_REQUIRED"}),{status:401,headers:{"Content-Type":"application/json"}});
      }
      const requestToken=token,requestEpoch=accountEpoch;
      const headers = new Headers(init.headers || (input instanceof Request ? input.headers : undefined));
      headers.set("Authorization","Bearer "+requestToken);
      const requestInput = url.pathname === "/api/account/logout" ? "/api/forge/embed/logout" : input;
      const response = await nativeFetch(requestInput,{...init,headers,credentials:"omit",cache:"no-store"});
      if(url.pathname === "/api/account/logout" && response.ok && requestToken===token && requestEpoch===accountEpoch)clearAccount();
      else if(response.status === 401 && requestToken===token && requestEpoch===accountEpoch && await sessionRejected(response,url.pathname) && requestToken===token && requestEpoch===accountEpoch)clearAccount();
      return response;
    };
  }
  const json = async (path, body, method = "POST") => {
    const response = await window.fetch(path,{method,headers:{"Content-Type":"application/json"},...(body === undefined?{}:{body:JSON.stringify(body)})});
    const value = await response.json().catch(()=>({}));
    if(!response.ok)throw error(typeof value.detail === "string" ? value.detail.slice(0,240) : "Account operation failed ("+response.status+").");
    return value;
  };
  const base64url = bytes => btoa(String.fromCharCode(...new Uint8Array(bytes))).replaceAll("+","-").replaceAll("/","_").replace(/=+$/g,"");
  const sha = async bytes => [...new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))].map(v=>v.toString(16).padStart(2,"0")).join("");
  const startPair = async () => {
    if(!binding || !port)throw error("Connect from the §e panel first.");
    const verifier = base64url(crypto.getRandomValues(new Uint8Array(48)));
    const challenge = base64url(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(verifier)));
    const value = await json("/api/forge/embed/pair",{parentOrigin:binding.parentOrigin,hostId:binding.hostId,channelId:binding.channelId,challenge});
    const url = new URL(value.loginUrl,location.origin);
    if(url.origin !== location.origin || url.pathname !== "/forge/login" || !/^[a-f0-9]{32}$/.test(value.pairId))throw error("Invalid account connection response.");
    pairing={pairId:value.pairId,verifier,until:Number(value.expiresAt)*1000};
    void pollPair(pairing);
    return {loginUrl:url.href,pairId:value.pairId};
  };
  const pollPair = async attempt => {
    while(pairing === attempt && Date.now() < attempt.until){
      await new Promise(resolve=>setTimeout(resolve,1200));
      if(pairing !== attempt)return;
      try{
        const state = await json("/api/forge/embed/pair/"+attempt.pairId,undefined,"GET");
        if(!state.approved)continue;
        const result = await json("/api/forge/embed/pair/exchange",{pairId:attempt.pairId,verifier:attempt.verifier,hostId:binding.hostId,channelId:binding.channelId});
        if(pairing !== attempt)return;
        if(!/^sfe1_[A-Za-z0-9_-]+$/.test(result.token) || result.parentOrigin !== binding.parentOrigin || result.hostId !== binding.hostId || result.channelId !== binding.channelId)throw error("Account connection did not match this panel.");
        revoke("account-changed");cloudCatalog.clear();token=result.token;expiresAt=Number(result.expiresAt)*1000;accountEpoch++;attempt.provisional=result.token;
        // Verify the SAME account through the actual Chat session resolver
        // before telling the editor that embedded Chat has signed in.
        const checked=await window.fetch("/api/account/me",{cache:"no-store",credentials:"omit"});
        const verified=checked.ok?await checked.json().catch(()=>({})):null;
        if(pairing!==attempt)return;
        if(!verified?.user?.id || verified.user.id!==result.user?.id){
          clearAccount();send("account.error",{message:"Chat could not verify the Google connection. Sign in again."});return;
        }
        pairing=null;
        send("account.status",publicAccount(verified.user));
        emit("swrlz-forge-account-changed",{signedIn:true});
        return;
      }catch(reason){
        if(pairing===attempt && attempt.provisional && token===attempt.provisional){
          clearAccount();send("account.error",{message:"Chat account verification failed. Sign in again."});return;
        }
        if(pairing === attempt && Date.now() >= attempt.until){pairing=null;send("account.error",{message:"Google connection expired. Sign in again."});}
      }
    }
  };
  const withCloud = async action => {
    if(!isAuthenticated())throw error("Sign in to §e with Google before using account projects.");
    if(cloudBusy)throw error("A cloud project operation is already running.");
    const epoch=accountEpoch;cloudBusy=true;
    try{return await action(()=>{if(epoch !== accountEpoch || !isAuthenticated())throw error("Account changed. Local work was preserved.");});}
    finally{cloudBusy=false;}
  };
  const cloudSave = payload => withCloud(async check => {
    const raw=payload?.bytes;
    if(!(raw instanceof ArrayBuffer) || raw.byteLength === 0 || raw.byteLength > 96*1024*1024)throw error("Project must be between 1 byte and 96 MiB. Local work was preserved.");
    if(typeof payload.name !== "string" || !payload.name.trim() || payload.name.length > 160 || !Number.isSafeInteger(payload.expectedRevision) || payload.expectedRevision < 0)throw error("A project name and current cloud revision are required.");
    if(payload.projectId && !/^[a-f0-9]{32}$/.test(payload.projectId))throw error("Invalid cloud project identifier.");
    let encoded=raw,codec="identity";
    if(typeof CompressionStream === "function"){
      try{
        const compressed=await new Response(new Blob([raw]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer();
        if(compressed.byteLength < raw.byteLength && compressed.byteLength <= 64*1024*1024){encoded=compressed;codec="gzip";}
      }catch(_){encoded=raw;codec="identity";}
    }
    const rawSha256=await sha(raw),encodedSha256=encoded===raw?rawSha256:await sha(encoded);check();
    const upload=await json("/api/forge/projects/uploads",{name:payload.name.trim(),...(payload.projectId?{projectId:payload.projectId}:{}),expectedRevision:payload.expectedRevision,codec,rawBytes:raw.byteLength,rawSha256,encodedBytes:encoded.byteLength,encodedSha256});
    if(!/^[a-f0-9]{32}$/.test(upload.uploadId) || upload.partBytes !== 524288 || upload.parts !== Math.ceil(encoded.byteLength/upload.partBytes))throw error("Invalid cloud upload plan.");
    try{
      for(let index=0;index<upload.parts;index++){
        check();
        const response=await window.fetch("/api/forge/projects/uploads/"+upload.uploadId+"/parts/"+index,{method:"PUT",headers:{"Content-Type":"application/octet-stream"},body:encoded.slice(index*upload.partBytes,(index+1)*upload.partBytes)});
        if(!response.ok)throw error("Cloud upload interrupted. Previous cloud revision and local work were preserved.");
        const receipt=await response.json();
        if(receipt.confirmed !== true || receipt.index !== index)throw error("Cloud upload was not confirmed.");
      }
      check();
      const result=await json("/api/forge/projects/uploads/"+upload.uploadId+"/commit",{});
      check();
      if(result.durable !== true || result.project?.rawSha256 !== rawSha256)throw error("Cloud save was not confirmed.");
      cloudCatalog.set(result.project.id,result.project);return result;
    }catch(reason){
      if(epochStillValid())await window.fetch("/api/forge/projects/uploads/"+upload.uploadId,{method:"DELETE"}).catch(()=>{});
      throw reason;
    }
    function epochStillValid(){try{check();return true;}catch(_){return false;}}
  });
  const cloudLoad = payload => withCloud(async check => {
    if(!/^[a-f0-9]{32}$/.test(payload?.projectId))throw error("Choose a cloud project to load.");
    const response=await window.fetch("/api/forge/projects/"+payload.projectId,{cache:"no-store"});
    if(!response.ok)throw error("Cloud project could not be loaded. Local work was preserved.");
    const bytes=await response.arrayBuffer();check();
    if(bytes.byteLength > 96*1024*1024)throw error("Cloud project exceeds the supported size.");
    const rawSha256=await sha(bytes);check();
    if(response.headers.get("X-SWRLZ-Project-SHA256") !== rawSha256)throw error("Cloud project integrity check failed. Local work was preserved.");
    const revision=Number(response.headers.get("X-SWRLZ-Project-Revision")),known=cloudCatalog.get(payload.projectId);
    return {bytes,project:{...(known?.revision===revision&&known.rawSha256===rawSha256?known:{name:"§E project"}),id:payload.projectId,revision,rawSha256,rawBytes:bytes.byteLength}};
  });
  const incoming = async event => {
    const message=event.data;
    if(!sameBinding(message) || typeof message.type !== "string" || typeof message.requestId !== "string" || message.requestId.length > 128)return;
    if(message.type === "rpc.result"){
      const task=pending.get(message.requestId);if(!task)return;
      pending.delete(message.requestId);clearTimeout(task.timer);
      if(message.error || message.payload?.ok === false)task.reject(error(String(message.error?.message || message.error || message.payload?.error || message.payload?.message || "§e operation failed.").slice(0,240)));
      else task.resolve(message.payload?.result ?? message.payload);
      return;
    }
    if(message.type === "host.visibility"){
      hostVisible=message.payload?.visible === true;
      if(!hostVisible){lease="";seenBatches.clear();}
      return;
    }
    if(message.type === "host.closed" || message.type === "host.projectChanged" || message.type === "host.inactive"){
      lease="";seenBatches.clear();return;
    }
    let result;
    try{
      if(message.type === "account.signIn")result=await startPair();
      else if(message.type === "cloud.list")result=await withCloud(async check=>{const value=await json("/api/forge/projects",undefined,"GET");check();for(const project of value.projects||[])cloudCatalog.set(project.id,project);return value;});
      else if(message.type === "cloud.save")result=await cloudSave(message.payload);
      else if(message.type === "cloud.load")result=await cloudLoad(message.payload);
      else return;
      send("rpc.result",{ok:true,result},message.requestId,result?.bytes instanceof ArrayBuffer?[result.bytes]:[]);
    }catch(reason){send("rpc.result",{ok:false,error:String(reason.message || "Account operation failed.").slice(0,240)},message.requestId);}
  };
  if(embedded)window.addEventListener("message",event => {
    const message=event.data;
    if(event.source !== window.parent || !PARENTS.has(event.origin) || !message || message.protocol !== PROTOCOL || !validBinding(message.hostId) || !validBinding(message.channelId))return;
    if(message.type === "host.hello" && !port){
      if(binding && (binding.parentOrigin !== event.origin || binding.hostId !== message.hostId || binding.channelId !== message.channelId))return;
      binding={parentOrigin:event.origin,hostId:message.hostId,channelId:message.channelId};
      window.parent.postMessage(envelope("iframe.ready",{}),event.origin);
    }else if(message.type === "host.connect" && sameBinding(message) && event.ports?.length === 1 && !port){
      port=event.ports[0];port.onmessage=incoming;port.start();hostVisible=true;
      send("iframe.connected",{});send("account.status",publicAccount(null));
      emit("swrlz-forge-connected",{});
    }
  });
  const api = {
    embedded,
    setThread(threadId){const next=String(threadId||"");if(next !== thread){thread=next;revoke("thread-changed");}},
    async beforeSend(threadId){
      if(!embedded || !binding || !port || !isAuthenticated())return {};
      api.setThread(threadId);
      if(!hostVisible || document.visibilityState !== "visible")return {};
      const epoch=accountEpoch,expectedThread=thread;
      const check=()=>{if(epoch!==accountEpoch || expectedThread!==thread || !isAuthenticated() || !hostVisible || document.visibilityState!=="visible")throw error("The editor connection changed. Your message was not sent.");};
      // Native project opening can finish queued view updates between context
      // and activation. Retry only that explicit stale-snapshot rejection with
      // entirely fresh context/ticket; never reuse or weaken its preconditions.
      for(let attempt=0;attempt<3;attempt++){
        check();
        const snapshot=await rpc("host.context",{threadId:thread});check();
        if(!snapshot || typeof snapshot.projectId !== "string" || !snapshot.context || typeof snapshot.context !== "object")throw error("The editor context is unavailable. Your message was not sent.");
        const presence=await json("/api/forge/embed/presence",{threadId:thread,projectId:snapshot.projectId,context:snapshot.context});check();
        try{
          const active=await rpc("host.presence",{...presence,context:snapshot.context});check();
          if(typeof active?.leaseId !== "string" || !/^[a-f0-9]{32}$/.test(active.leaseId))throw error("The editor connection could not be confirmed.");
          lease=active.leaseId;seenBatches.clear();return {forgeLeaseId:lease};
        }catch(reason){
          check();if(reason.message!=="EDITOR_CONTEXT_CHANGED" || attempt===2)throw reason;
        }
      }
    },
    forwardBatch(event){
      const value=event?.payload && !event.batchId?event.payload:event;
      if(!embedded || !port || !lease || !hostVisible || !isAuthenticated() || value?.leaseId !== lease || value?.threadId !== thread || !/^[a-f0-9]{32}$/.test(value?.batchId) || seenBatches.has(value.batchId))return;
      seenBatches.add(value.batchId);
      send("host.batch",{batchId:value.batchId,leaseId:lease,threadId:thread,generationId:String(value.generationId||""),projectId:String(value.projectId||"")});
    },
    notifyAccount(user){if(embedded && port)send("account.status",publicAccount(user));},
    requestSignIn(){if(port)send("account.signInRequested",{});},
    revoke,
  };
  Object.defineProperty(window,"SwrlzForgeEmbedV1",{value:Object.freeze(api),writable:false,configurable:false});
  if(embedded){
    document.addEventListener("visibilitychange",()=>{if(document.visibilityState !== "visible")revoke("document-hidden");});
    window.addEventListener("pagehide",()=>revoke("page-hidden"));
    document.addEventListener("click",async event=>{
      const anchor=event.target.closest?.("a[download]");
      if(!anchor || !protectedPath(new URL(anchor.href,location.href).pathname) || new URL(anchor.href,location.href).origin !== location.origin)return;
      event.preventDefault();
      try{
        const response=await window.fetch(anchor.href);if(!response.ok)throw error("Download could not be authenticated.");
        const blob=await response.blob(),url=URL.createObjectURL(blob),link=document.createElement("a");
        link.href=url;link.download=anchor.download||"download";document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
      }catch(reason){emit("swrlz-forge-download-error",{message:String(reason.message||"Download failed.")});}
    },true);
  }
})();
