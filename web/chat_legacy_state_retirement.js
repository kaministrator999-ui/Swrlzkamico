(()=>{"use strict";
const EXACT_KEYS=new Set([
  'swrlz.vercel.chat.v1',
  'swrlz.vercel.chat.v2.migrated'
]);
const PREFIXES=[
  'swrlz.vercel.chat.v2.account.'
];
const RETIRED_MARK='swrlz.chat.legacy-state-retired.v2';
let removed=[];
let shouldReload=false;
try{
  const alreadyRetired=localStorage.getItem(RETIRED_MARK)==='1';
  if(!alreadyRetired){
    const keys=[];
    for(let i=0;i<localStorage.length;i++){
      const key=localStorage.key(i);
      if(key)keys.push(key);
    }
    for(const key of keys){
      if(EXACT_KEYS.has(key)||PREFIXES.some(prefix=>key.startsWith(prefix))){
        localStorage.removeItem(key);
        removed.push(key);
      }
    }
    localStorage.setItem(RETIRED_MARK,'1');
    shouldReload=removed.length>0;
  }
}catch(_){}
window.__swrlzLegacyChatState=Object.freeze({
  version:2,
  retired:true,
  removedCount:removed.length,
  reloadRequired:shouldReload
});
if(shouldReload){
  location.reload();
  return;
}
})();
