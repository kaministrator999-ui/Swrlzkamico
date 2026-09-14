(()=>{"use strict";
const LEGACY_KEY='swrlz.vercel.chat.v1';
const RETIRED_MARK='swrlz.chat.legacy-state-retired.v1';
let shouldReload=false;
try{
  const alreadyRetired=localStorage.getItem(RETIRED_MARK)==='1';
  if(!alreadyRetired){
    if(localStorage.getItem(LEGACY_KEY)!==null){
      localStorage.removeItem(LEGACY_KEY);
      shouldReload=true;
    }
    localStorage.setItem(RETIRED_MARK,'1');
  }
}catch(_){}
window.__swrlzLegacyChatState=Object.freeze({version:1,legacyKey:LEGACY_KEY,retired:true,reloadRequired:shouldReload});
if(shouldReload){
  location.reload();
  return;
}
})();
