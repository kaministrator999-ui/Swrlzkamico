// §E v11.251: native validated controls for nebula width and star distribution.
(function(){
'use strict';
const previousDefault=se223Default,previousValidate=se223ValidateEmitter;
const specs=[['nebulaSpread','Smoke arm spread',.25,2.5,.05,1],
 ['starDensity','Starfield density',0,1,.05,.75]];
se223Default=function(...args){
 const value=previousDefault(...args);
 for(const item of specs)value[item[0]]=item[5];
 return value;
};
se223ValidateEmitter=function(input){
 const value=previousValidate(input);
 for(const [key,,min,max,,fallback]of specs){
  const n=input?.[key]??fallback;
  if(typeof n!=='number'||!Number.isFinite(n)||n<min||n>max)
   throw Error(key+' must be between '+min+' and '+max);
  value[key]=Math.round(n*1000)/1000;
 }
 return value;
};
const q=s=>document.querySelector(s);
function selected(){return se223Get(se223State.selected)||null}
function sync(){
 const root=q('#se251NebulaControls');if(!root)return;
 const c=selected(),isArm=c&&(c.preset==='vortex'||c.preset==='vortexCyan');
 root.hidden=!isArm;
 if(!isArm)return;
 for(const item of specs){
  const key=item[0],fallback=item[5];
  for(const input of root.querySelectorAll('[data-se251-param="'+key+'"]')){
   if(document.activeElement!==input)input.value=c[key]??fallback;
  }
 }
}
function install(){
 const box=q('#se249VortexSettings');if(!box)return false;
 if(q('#se251NebulaControls'))return true;
 const group=document.createElement('div');group.id='se251NebulaControls';
 group.className='se251-nebula-controls';
 const title=document.createElement('strong');title.textContent='Nebula & starfield';group.append(title);
 for(const [key,label,min,max,step,defaultValue]of specs){
  const row=document.createElement('label');row.className='se251-nebula-row';
  const heading=document.createElement('span');heading.textContent=label;
  const input=document.createElement('input');input.type='number';
  input.min=String(min);input.max=String(max);input.step=String(step);
  input.value=String(defaultValue);input.dataset.se251Param=key;
  const range=document.createElement('input');range.type='range';
  range.min=input.min;range.max=input.max;range.step=input.step;
  range.dataset.se251Param=key;range.value=String(defaultValue);
  const save=value=>{
   const c=selected(),v=Number(value);
   if(!c||!Number.isFinite(v)||v<min||v>max){sync();return}
   se223Update(c.id,{[key]:v});sync();
  };
  input.addEventListener('change',()=>save(input.value));
  range.addEventListener('change',()=>save(range.value));
  range.addEventListener('input',()=>{input.value=range.value});
  row.append(heading,input,range);group.append(row);
 }
 box.append(group);
 const old=se223UIRefresh;
 se223UIRefresh=function(...args){const result=old(...args);sync();return result;};
 sync();return true;
}
function boot(){
 if(install())return;
 const mo=new MutationObserver(()=>{if(install())mo.disconnect()});
 mo.observe(document.body,{subtree:true,childList:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
window.SWYRL_ENGINE_NEBULA_SETTINGS_251=Object.freeze({
 inspect:()=>({keys:specs.map(x=>x[0]),selected:!!selected()})
});
})();