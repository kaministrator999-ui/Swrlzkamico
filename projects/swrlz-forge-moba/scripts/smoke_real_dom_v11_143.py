#!/usr/bin/env python3
"""Real Chromium smoke against the ACTUAL assembled §wyrl§ Engine, not VM stubs."""
from playwright.sync_api import sync_playwright
import json,time,sys
URL=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8765/"
with sync_playwright() as p:
 browser=p.chromium.launch(channel="chrome",headless=True,args=[
  "--no-sandbox","--enable-webgl","--enable-unsafe-swiftshader",
  "--use-gl=angle","--disable-dev-shm-usage"
 ])
 page=browser.new_page(viewport={"width":440,"height":900},device_scale_factor=1)
 errors=[]
 page.on("pageerror",lambda err: errors.append(str(err)))
 page.on("console",lambda msg: errors.append("console: "+msg.text[:300]) if msg.type=="error" else None)
 print("SMOKE_OPEN",URL,flush=True)
 page.goto(URL,wait_until="domcontentloaded",timeout=60000)
 page.wait_for_timeout(4500)
 snap_js="""() => ({
  ready:document.readyState,
  version:document.querySelector('title')?.textContent,
  controls:[...document.querySelectorAll('button')].filter(b=>/play|stop|projects/i.test(b.textContent||'')).slice(0,14).map(b=>({id:b.id,label:b.textContent.trim().slice(0,30),hidden:b.hidden,cls:b.className})),
  api:typeof window.SWYRL_ENGINE_LEVELS,
  sheeptag:typeof window.SWYRL_ENGINE_SHEEP_TAG,
  project:typeof currentProject==='undefined'?null:{name:currentProject?.name,kind:currentProject?.kind,root:currentProject?.levelProjectRoot,level:currentProject?.sheepTagLevel,canonicalId:currentProject?.canonicalId},
  levels:typeof window.SWYRL_ENGINE_LEVELS==='undefined'?null:window.SWYRL_ENGINE_LEVELS.status(),
  menu:document.querySelector('#st141RuntimeMenu')?.outerHTML?.slice(0,800)||null,
  bar:document.querySelector('#st141LevelBar')?.outerHTML?.slice(0,500)||null,
  actors:typeof actors==='undefined'?'no variable':actors.length,
  play:document.querySelector('#playBtn')?.outerHTML?.slice(0,250)
 })"""
 def state(stage):
  try: print("SMOKE_STATE_"+stage,json.dumps(page.evaluate(snap_js),ensure_ascii=False),flush=True)
  except Exception as e:print("SMOKE_STATE_FAIL_"+stage,str(e),flush=True)
 state("BOOT")
 try:
  call=page.evaluate("""() => window.SWYRL_ENGINE_SHEEP_TAG?.load?.() ?? 'no sheep API'""")
  print("SMOKE_LOAD",repr(call)[:600],flush=True)
 except Exception as e:print("SMOKE_LOAD_ERROR",str(e),flush=True)
 page.wait_for_timeout(1100)
 state("STARTER")
 try:
  res=page.evaluate("""() => {const p=document.getElementById('playBtn');if(!p)return 'no playBtn';p.click();return 'clicked native button'}""")
  print("SMOKE_PLAY",res,flush=True)
 except Exception as e:print("SMOKE_PLAY_ERROR",str(e),flush=True)
 page.wait_for_timeout(900)
 state("AFTER_PLAY")
 try:page.screenshot(path="/tmp/se143-after-play.png",full_page=True)
 except Exception as e:print("SCREEN_ERROR",str(e),flush=True)
 print("SMOKE_ERRORS",json.dumps(errors[-22:],ensure_ascii=False),flush=True)
 # Real Android-like touch viewport: compare actual page.tap and menu hit area.
 mobile=browser.new_context(viewport={"width":412,"height":915},device_scale_factor=2.5,
  is_mobile=True,has_touch=True)
 m=mobile.new_page()
 mob_errors=[]
 m.on("pageerror",lambda err: mob_errors.append(str(err)))
 m.goto(URL,wait_until="domcontentloaded",timeout=60000)
 m.wait_for_timeout(3200)
 m.evaluate("() => window.SWYRL_ENGINE_SHEEP_TAG?.load?.()")
 m.wait_for_timeout(900)
 def mobile_state(stage):
  d=m.evaluate("""() => {
   const play=document.querySelector('#playBtn');
   const rect=play?.getBoundingClientRect();
   const menu=document.querySelector('#st141RuntimeMenu');
   const bar=document.querySelector('#st141LevelBar');
   const style=menu?getComputedStyle(menu):null;
   const mb=menu?.getBoundingClientRect();
   const hit=rect&&document.elementFromPoint(rect.left+rect.width/2,rect.top+rect.height/2);
   return {
    viewport:[innerWidth,innerHeight,visualViewport?.width,visualViewport?.height],
    playRect:rect?{x:rect.x,y:rect.y,width:rect.width,height:rect.height}:null,
    playHit:hit?{id:hit.id,tag:hit.tagName,text:hit.textContent?.trim().slice(0,65),html:hit.outerHTML?.slice(0,900),rect:hit.getBoundingClientRect().toJSON(),pointer:getComputedStyle(hit).pointerEvents}:null,
    playStack:rect?[...document.elementsFromPoint(rect.left+rect.width/2,rect.top+rect.height/2)].slice(0,8).map(e=>({tag:e.tagName,id:e.id,cls:e.className?.toString().slice(0,100),text:e.textContent?.trim().slice(0,60),pointer:getComputedStyle(e).pointerEvents})):[],
    menuExists:!!menu,menuCSS:style?{display:style.display,visibility:style.visibility,opacity:style.opacity,z:style.zIndex,pointer:style.pointerEvents}:null,
    menuRect:mb?{x:mb.x,y:mb.y,width:mb.width,height:mb.height}:null,
    menuVisible:!!menu&&style.display!=='none'&&style.visibility!=='hidden'&&mb.width>5,
    barHidden:bar?.hidden,barRect:bar?.getBoundingClientRect().toJSON()||null,
    state:window.SWYRL_ENGINE_LEVELS?.status(),selected:document.querySelector('#statusBar')?.textContent?.slice(0,220)
   };
  }""")
  print("MOBILE_"+stage,json.dumps(d,ensure_ascii=False),flush=True)
 mobile_state("STARTER")
 try:
  m.locator("#playBtn").tap(timeout=5000)
  print("MOBILE_TAP_PLAY_DONE",flush=True)
 except Exception as e:
  print("MOBILE_TAP_ERROR",str(e)[:1000],flush=True)
 m.wait_for_timeout(1400)
 mobile_state("AFTER_TAP")
 try:m.screenshot(path="/tmp/se143-mobile-after-play.png",full_page=True)
 except Exception as e:print("MOBILE_SCREEN_ERROR",str(e),flush=True)
 print("MOBILE_ERRORS",json.dumps(mob_errors[-15:]),flush=True)
 mobile.close()
 browser.close()
