#!/usr/bin/env python3
"""§E v11.147 Android-size Chromium UI geometry smoke.

Checks the real compiled editor, not a simulated DOM or stylesheet alone.
"""
import http.server,json,threading,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root.parent.parent/"dist/swrlz-forge-moba"
assert (out/"index.html").is_file(),out
class Serve(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(out),**kw)
 def log_message(self,*args):pass
http=http.server.ThreadingHTTPServer(("127.0.0.1",0),Serve)
threading.Thread(target=http.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(channel="chrome",headless=True,
   args=["--no-sandbox","--disable-dev-shm-usage","--enable-webgl","--enable-unsafe-swiftshader"])
  context=browser.new_context(viewport={"width":412,"height":915},
   device_scale_factor=2.5,is_mobile=True,has_touch=True)
  page=context.new_page()
  page.goto(f"http://127.0.0.1:{http.server_port}/",wait_until="domcontentloaded",timeout=60000)
  page.wait_for_function("() => !!window.SWYRL_ENGINE_LEVELS && !!window.SWYRL_ENGINE_SHEEP_TAG",timeout=45000)
  page.evaluate("() => window.SWYRL_ENGINE_SHEEP_TAG.load()")
  page.evaluate("() => {const d=document.querySelector('#seReleaseNotesDialog');if(d?.open)d.close();}")
  page.wait_for_timeout(400)
  def metrics():
   return page.evaluate("""() => {
    const r=id=>{const e=document.querySelector(id);if(!e)return null;
     const b=e.getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height,visible:getComputedStyle(e).display!=='none'}};
    return {vh:innerHeight,vw:innerWidth,
     full:document.body.classList.contains('se145-runtime'),
     canvas:r('#viewport'),host:r('.viewport-wrap'),
     menu:r('#st141RuntimeMenu'),panel:r('#st141RuntimeMenu .st141-menu-panel'),
     start:r('#st141StartGame'),lan:r('#se146LanOpen'),
     exit:r('#se145ExitEditor'),level:r('#st141LevelBar'),
     state:window.SWYRL_ENGINE_LEVELS.status()};
   }""")
  initial=metrics();assert initial["state"]["active"]=="menu",initial
  page.locator("#playBtn").click(force=True)
  page.wait_for_function("() => window.SWYRL_ENGINE_LEVELS.status().menuPlaying===true",timeout=15000)
  page.wait_for_timeout(550)
  playing=metrics()
  print("SE147_ANDROID_MENU_METRICS",json.dumps(playing,ensure_ascii=False)[:2600],flush=True)
  assert playing["full"],playing
  assert playing["host"] and playing["host"]["h"]>=playing["vh"]*.88,playing
  assert playing["canvas"] and playing["canvas"]["h"]>=playing["vh"]*.85,playing
  assert playing["menu"] and playing["menu"]["h"]>=playing["vh"]*.8,playing
  assert playing["start"] and playing["start"]["h"]>=36,playing
  assert playing["lan"] and playing["lan"]["h"]>=28,playing
  assert playing["panel"] and playing["panel"]["y"]>playing["vh"]*.12,playing
  assert playing["exit"] and playing["exit"]["y"]>playing["vh"]*.78,playing
  page.locator("#se146LanOpen").click()
  page.wait_for_function("() => window.SWYRL_ENGINE_LAN.status().screen",timeout=7000)
  assert page.locator("#se146LanScreen").is_visible()
  page.locator("#se146LanBack").click()
  assert not page.locator("#se146LanScreen").is_visible()
  page.locator("#se145ExitEditor").click()
  page.wait_for_function("() => !document.body.classList.contains('se145-runtime')",timeout=9000)
  restored=metrics()
  print("SE147_ANDROID_EDITOR_RESTORED",json.dumps(restored,ensure_ascii=False)[:1600],flush=True)
  assert restored["level"] and restored["level"]["visible"],restored
  assert not restored["full"],restored
  print("SE147_REAL_CHROMIUM_ANDROID_FULLSCREEN_MENU_LAN_EXIT_EDITOR_PASS",flush=True)
  browser.close()
finally:
 http.shutdown()
 http.server_close()
