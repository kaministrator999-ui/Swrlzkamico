(()=>{"use strict";
const body=document.body;
const messages=document.querySelector('.messages');
const stack=document.querySelector('.message-stack');
let img,shade;
function ensure(){
 if(!messages)return;
 if(!img){
  img=document.createElement('img');img.className='ice-dragon-adult-image';img.alt='';img.setAttribute('aria-hidden','true');
  Object.assign(img.style,{position:'absolute',inset:'0',width:'100%',height:'100%',objectFit:'cover',objectPosition:'50% 42%',pointerEvents:'none',zIndex:'0',display:'block',opacity:'0'});
  shade=document.createElement('div');Object.assign(shade.style,{position:'absolute',inset:'0',pointerEvents:'none',zIndex:'1',background:'linear-gradient(180deg,rgba(1,7,16,.10),rgba(1,8,18,.18) 52%,rgba(1,6,14,.30)),linear-gradient(90deg,rgba(1,8,18,.16),transparent 62%)',opacity:'0'});
  messages.prepend(shade);messages.prepend(img);messages.style.setProperty('position','relative','important');messages.style.setProperty('isolation','isolate','important');
  if(stack){stack.style.setProperty('position','relative','important');stack.style.setProperty('z-index','2','important');}
  img.addEventListener('load',()=>{if(body?.dataset.swrlzTheme==='ice-dragon'){img.style.opacity='1';shade.style.opacity='1';}});
  img.addEventListener('error',()=>{console.warn('Ice Dragon adult JPEG failed to load');});
 }
}
function paint(){ensure();if(!img)return;const active=body?.dataset.swrlzTheme==='ice-dragon';if(active){messages.style.setProperty('background','transparent','important');if(!img.src)img.src='/live/assets/themes/ice-dragon/assets/adult-background.jpg?v=1';if(img.complete&&img.naturalWidth>0){img.style.opacity='1';shade.style.opacity='1';}}else{messages.style.removeProperty('background');img.style.opacity='0';shade.style.opacity='0';}}
paint();new MutationObserver(paint).observe(body,{attributes:true,attributeFilter:['data-swrlz-theme']});
})();
