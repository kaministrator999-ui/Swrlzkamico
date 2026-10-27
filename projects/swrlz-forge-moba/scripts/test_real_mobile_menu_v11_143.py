#!/usr/bin/env python3
"""End-to-end Android-size TOUCH test using actual assembled §e HTML/DOM."""
from playwright.sync_api import sync_playwright
import sys,json
URL=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8765/'
with sync_playwright() as p:
 browser=p.chromium.launch(channel='chrome',headless=True,
  args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader'])
 ctx=browser.new_context(viewport={'width':412,'height':915},device_scale_factor=2.5,is_mobile=True,has_touch=True)
 page=ctx.new_page()
 errors=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.goto(URL,wait_until='domcontentloaded',timeout=60000)
 page.wait_for_function("() => !!window.SWYRL_ENGINE_SHEEP_TAG && !!window.SWYRL_ENGINE_LEVELS",timeout=35000)
 page.wait_for_timeout(600)
 page.evaluate("() => window.SWYRL_ENGINE_SHEEP_TAG.load()")
 # Release notes are an explicit modal until the user presses Continue.
 page.evaluate("() => {const d=document.querySelector('#seReleaseNotesDialog');if(d?.open)d.close();}")
 page.wait_for_timeout(350)
 def inspect(label):
  s=page.evaluate("""() => {
   const l=window.SWYRL_ENGINE_LEVELS.status();
   const canvas=document.querySelector('#viewport'),host=canvas?.parentElement,
    bar=document.querySelector('#st141LevelBar'),preview=document.querySelector('#st141MenuPreview'),
    overlay=document.querySelector('#st141RuntimeMenu'),start=document.querySelector('#st141StartGame');
   const rect=el=>{if(!el)return null;const r=el.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
   const mr=rect(start);const hit=mr?document.elementFromPoint(mr.x+mr.width/2,mr.y+mr.height/2):null;
   return {version:document.title,state:l,canvas:canvas?.tagName,host:host?.tagName,
    canvasRect:rect(canvas),hostRect:rect(host),
    barHost:bar?.parentElement?.tagName,bar:rect(bar),preview:rect(preview),
    overlayHost:overlay?.parentElement?.tagName,overlay:rect(overlay),
    start:rect(start),startHit:hit?.id||hit?.tagName,modalOpen:!!document.querySelector('#seReleaseNotesDialog')?.open};
  }""")
  print('REAL_MOBILE_'+label,json.dumps(s,ensure_ascii=False),flush=True)
  return s
 editor=inspect('EDITOR')
 assert editor['state']['active']=='menu',editor
 assert editor['canvas']=='CANVAS' and editor['host']=='MAIN',editor
 assert editor['barHost']=='MAIN' and editor['bar']['width']>90, 'level browser must NOT live in canvas'
 assert editor['preview']['width']>90 and editor['preview']['height']>90,'author-editable menu preview invisible'
 assert not editor['state']['menuPlaying'] and not editor['modalOpen']
 rect=page.locator('#playBtn').bounding_box()
 assert rect and rect['width']>15,rect
 page.touchscreen.tap(rect['x']+rect['width']/2,rect['y']+rect['height']/2)
 page.wait_for_function("() => window.SWYRL_ENGINE_LEVELS?.status().menuPlaying===true",timeout=10000)
 page.wait_for_timeout(350)
 menu=inspect('PLAY')
 try:page.screenshot(path='/tmp/se143-mobile-PLAY.png',full_page=True)
 except Exception:pass
 assert menu['state']['runtimeGuiMounted'] and menu['state']['runtimeGuiVisible'],menu
 assert menu['overlayHost']=='MAIN' and menu['overlay']['width']>100 and menu['overlay']['height']>100,menu
 assert menu['overlay']['height']>=menu['canvasRect']['height']-6,'Runtime UI must cover real canvas height, not short wrapper'
 assert menu['start']['width']>75 and menu['start']['height']>20,'Start Game must be visible and touch-sized'
 assert menu['startHit']=='st141StartGame','touch center must hit Start Game, not hidden canvas or tool'
 b=menu['start']
 page.touchscreen.tap(b['x']+b['width']/2,b['y']+b['height']/2)
 page.wait_for_function("() => window.SWYRL_ENGINE_LEVELS?.status().active==='game'",timeout=12000)
 page.wait_for_timeout(500)
 game=inspect('START_GAME')
 assert game['state']['active']=='game' and not game['state']['menuPlaying']
 assert game['start'] is None and game['overlay'] is None,'menu actors/UI must not leak to gameplay'
 # Built-in gameplay preflight can enforce maps/rules: report actual session.
 status=page.evaluate("() => window.SWYRL_ENGINE_SHEEP_TAG.status()")
 print('REAL_MOBILE_GAME_STATUS',json.dumps(status,ensure_ascii=False)[:1300],flush=True)
 assert status.get('active') is True,'Start Game must launch a real Sheep Tag session'
 assert not errors,errors[-6:]
 print('SE143_REAL_ANDROID_SIZE_TOUCH_MENU_VISIBLE_LEVEL_BAR_EDIT_PREVIEW_AND_GAMEPLAY_PASS',flush=True)
 browser.close()
