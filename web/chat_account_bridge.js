(()=>{"use strict";
const STORAGE_KEY="swrlz.vercel.chat.v1";
const base=window.fetch.bind(window);
window.fetch=function(input,init={}){
  try{
    const url=new URL(typeof input==="string"?input:input.url,location.href);
    const method=String(init.method||"GET").toUpperCase();
    if(url.origin===location.origin&&url.pathname==="/api/account/generate"&&method==="POST"){
      const body=JSON.parse(init.body||"{}");
      if(!body.threadId){
        const state=JSON.parse(localStorage.getItem(STORAGE_KEY)||"null");
        if(state?.currentId)body.threadId=String(state.currentId);
      }
      init={...init,body:JSON.stringify(body)};
    }
  }catch(_){}
  return base(input,init);
};
})();
