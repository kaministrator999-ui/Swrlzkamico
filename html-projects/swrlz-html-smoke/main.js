(() => {
  'use strict';
  const button=document.getElementById('increment');
  const counter=document.getElementById('counter');
  const message=document.getElementById('message');
  let clicks=0;
  button.addEventListener('click',()=>{
    clicks+=1;
    counter.textContent=String(clicks);
    message.textContent='Interaction passed · '+clicks+' click'+(clicks===1?'':'s')+' recorded in this page.';
  });
})();
