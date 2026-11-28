
/* SE558: center the square atlas without clipping zoomed islands. */
const se558LayoutOpen=se552Open;
se552Open=function(){
 se558LayoutOpen();
 const host=se552Portal?.host,cv=host?.querySelector('#se356UVCanvas');
 const bar=host?.querySelector('[data-se551="fit"]')?.parentElement;
 if(!host||!cv||!bar)return;
 if(!document.getElementById('se558ExpandedCSS')){
  const style=document.createElement('style');style.id='se558ExpandedCSS';
  style.textContent='#se552UVHost #se356UVCanvas{display:block!important;margin-inline:auto!important;flex:none!important} #se552UVHost>div:nth-child(2)>label{flex:0 0 auto!important;max-width:100%;white-space:nowrap!important;overflow-wrap:normal!important} #se552UVHost>div:nth-child(2)>button{flex:0 0 auto;white-space:nowrap!important}';
  document.head.append(style);
 }
 const viewport=cv.parentElement;
 function setZoom(z){
  se551Zoom=Math.min(6,Math.max(.25,z));cv.style.width=cv.style.height=(512*se551Zoom)+'px';
  cv.style.maxWidth='none';bar.querySelector('[data-se551-zoom]').textContent=Math.round(se551Zoom*100)+'%';
 }
 function fit(){
  if(!se552Portal||se552Portal.host!==host)return;
  const h=Math.max(128,host.getBoundingClientRect().bottom-viewport.getBoundingClientRect().top-12);
  viewport.style.maxHeight=h+'px';
  const size=Math.max(128,Math.min(viewport.clientWidth-4,h-4,2048));
  setZoom(size/512);viewport.scrollTop=viewport.scrollLeft=0;
 }
 bar.__se558Fit=fit;bar.__se558SetZoom=setZoom;
 if(!bar.dataset.se558Fit){bar.dataset.se558Fit='1';bar.addEventListener('click',e=>{
  const op=e.target.closest('[data-se551]')?.dataset.se551;
  if(!se552Portal||!['fit','plus','minus'].includes(op))return;
  e.preventDefault();e.stopImmediatePropagation();
  if(op==='fit')bar.__se558Fit();else bar.__se558SetZoom(se551Zoom*(op==='plus'?1.4:1/1.4));
 },true);}
 fit();requestAnimationFrame(fit);
};
/* SE558_LAYOUT_END */
