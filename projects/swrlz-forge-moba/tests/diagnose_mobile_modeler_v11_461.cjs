'use strict';
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path');
const root='/tmp/se461-diagnostic',host='https://kamiloki-swrlz-forge-moba.hf.space';
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader','--disable-web-security']});
 const page=await browser.newPage({viewport:{width:412,height:915},isMobile:true,hasTouch:true,deviceScaleFactor:2});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.route(host+'/**',route=>{
  const u=new URL(route.request().url()),name=decodeURIComponent(u.pathname).replace(/^\/+/,'')||'index.html';
  const file=path.resolve(root,name);
  if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile())return route.fulfill({status:404,body:'not found'});
  const b=fs.readFileSync(file),ext=path.extname(file).toLowerCase();
  return route.fulfill({status:200,body:b,contentType:{'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.jpg':'image/jpeg'}[ext]||'application/octet-stream'});
 });
 await page.goto(host+'/modeler.html',{waitUntil:'domcontentloaded',timeout:35000});
 await page.waitForTimeout(6200);
 await page.evaluate(()=>document.querySelector('#seReleaseNotesDialog[open]')?.close?.());
 const get=()=>page.evaluate(()=>{
  const r=selector=>{const e=document.querySelector(selector);if(!e)return null;const rect=e.getBoundingClientRect(),st=getComputedStyle(e);return {rect:{x:rect.x,y:rect.y,w:rect.width,h:rect.height},
   display:st.display,visibility:st.visibility,z:st.zIndex,pointerEvents:st.pointerEvents,touchAction:st.touchAction,
   hit:document.elementFromPoint(rect.x+rect.width/2,rect.y+rect.height/2)?.outerHTML?.slice(0,170)}};
  const root=document.querySelector('#modelAtelierPanel'),body=root?.querySelector('.atelier-body');
  return {innerWidth,innerHeight,layout:root?.dataset.se251Layout,collapsed:root?.dataset.se251Collapsed,rightCollapsed:root?.dataset.se251RightCollapsed,
    vars:{left:root?.style.getPropertyValue('--se251-left'),right:root?.style.getPropertyValue('--se251-right'),se320left:getComputedStyle(body).getPropertyValue('--se320-left'),se320right:getComputedStyle(body).getPropertyValue('--se320-right')},
    left:r('#se251-split-model-left'),right:r('#se251-split-model-right'),
    hierarchy:r('#modelAtelierHierarchy'),canvas:r('#modelAtelierViewport canvas'),stage:r('.atelier-scene'),
    inspector:r('#modelAtelierInspector'),body:r('#modelAtelierPanel .atelier-body'),
    camera:window.SWYRL_ENGINE_MODEL_CAMERA?.inspect?.()||null,
    mode:window.SWYRL_ENGINE_MODEL_VIEW?.inspect?.()||null};
 });
 const first=await get();console.log('SE461_MOBILE_INITIAL '+JSON.stringify(first));
 await page.setViewportSize({width:980,height:915});
 await page.waitForTimeout(400);
 console.log('SE461_DESKTOP_TOUCH_LAYOUT '+JSON.stringify(await get()));
 const wide=await get();

 for(const side of ['left','right']){
  const gr=wide[side];if(!gr?.rect?.w||!gr?.rect?.h)continue;
  const px=gr.rect.x+gr.rect.w/2,py=gr.rect.y+gr.rect.h/2;
  await page.mouse.move(px,py);await page.mouse.down();
  await page.mouse.move(px+(side==='left'?46:-46),py,{steps:7});await page.mouse.up();
  console.log('SE461_MOBILE_MOUSE_SPLITTER '+side+' '+JSON.stringify(await get()));
  const now=(await get())[side];if(!now?.rect?.w||!now?.rect?.h)continue;
  const tx=now.rect.x+now.rect.w/2,ty=now.rect.y+now.rect.h/2;
  const cdp=await page.context().newCDPSession(page);
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:tx,y:ty}]});
  for(let i=1;i<=6;i++)await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:tx+(side==='left'?6:-6)*i,y:ty}]});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  console.log('SE461_MOBILE_TOUCH_SPLITTER '+side+' '+JSON.stringify(await get()));
  await cdp.detach();
 }
 const camera=await page.evaluate(()=>{
  const api=window.SWYRL_ENGINE_MODEL_CAMERA;
  const before=api?.inspect?.();
  const framed=api?.frame?.('all',true);
  const after=api?.inspect?.();
  return {framed,before,after};
 });console.log('SE461_MOBILE_CAMERA_FRAME '+JSON.stringify(camera));
 console.log('SE461_UI_ADD_CHOICES '+JSON.stringify(await page.locator('button').evaluateAll(bs=>bs.filter(b=>/add cube|create geometry|mesh/i.test(b.textContent||'')).slice(0,18).map(b=>({text:b.textContent.trim().slice(0,100),id:b.id,visible:b.getBoundingClientRect().height>0})))));
 const cube=page.getByRole('button',{name:/Run.*Add cube/i}).first();
 if(await cube.count()&&await cube.isVisible()){
  await cube.click({timeout:5000});
  await page.waitForTimeout(200);
  const a=await page.evaluate(()=>({before:window.SWYRL_ENGINE_MODEL_CAMERA?.inspect?.(),
    framed:window.SWYRL_ENGINE_MODEL_CAMERA?.frame?.('all',true),
    after:window.SWYRL_ENGINE_MODEL_CAMERA?.inspect?.()}));
  console.log('SE461_MOBILE_CAMERA_ADD_CUBE '+JSON.stringify(a));
 }
 console.log('SE461_MOBILE_ERRORS '+JSON.stringify(errors.slice(0,12)));
 await browser.close();
})().catch(e=>{console.error('SE461_MOBILE_DIAG_ERROR',e.stack||e);process.exit(1)});
