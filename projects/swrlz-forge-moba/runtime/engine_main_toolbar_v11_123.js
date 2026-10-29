// §E v11.123: reorder native editor buttons, preserving every DOM node/listener.
// A small priority run at the left makes projects and playback discoverable.
function seMainToolbarOrganize(){
 const root=document.querySelector('.topbar');
 if(!root)return false;
 const buttons=[...root.querySelectorAll('button')];
 const label=b=>(b.innerText||b.textContent||'').replace(/\s+/g,' ').trim().toLowerCase();
 const find=(id,test)=>buttons.find(b=>b.id===id)||buttons.find(b=>test(label(b)));
 const projects=buttons.find(b=>/\bprojects\b/i.test(label(b)));
 if(!projects)return false;
 const play=find('playBtn',s=>/\bplay\b/.test(s)&&!/\breplay\b/.test(s));
 const pause=find('pauseBtn',s=>/\bpause\b/.test(s));
 const simulate=find('simulateBtn',s=>/\bsimulate\b/.test(s));
 const stop=find('stopBtn',s=>/\bstop\b/.test(s));
 const native=[projects,play,pause,simulate,stop].filter(Boolean);
 const parent=projects.parentElement;
 if(!parent||!native.every(b=>b.parentElement===parent))return false;
 if(parent.dataset.se123Organized==='1')return true;
 // reverse prepend keeps Projects at the far left, followed by playback.
 for(const b of [...native].reverse())parent.prepend(b);
 parent.dataset.se123Organized='1';
 for(const b of native)b.classList.add('se-main-workflow-button');
 projects.classList.add('se-main-project-button');
 native.at(-1)?.classList.add('se-main-workflow-end');
 parent.scrollLeft=0;
 return true;
}
function seMainToolbarBoot(){
 if(seMainToolbarOrganize())return;
 // A few deferred frames accommodate initial editor setup without timers.
 let tries=0;
 const retry=()=>{if(seMainToolbarOrganize()||++tries>50)return;
  requestAnimationFrame(retry);};
 requestAnimationFrame(retry);
}
if(document.readyState==='loading')
 document.addEventListener('DOMContentLoaded',seMainToolbarBoot,{once:true});
else seMainToolbarBoot();
