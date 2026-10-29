#!/usr/bin/env python3
"""Real 412×915 touch Chromium against actual local bridge: host -> seats -> guest -> close."""
import json,sys,threading,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"scripts"))
from lan_bridge import LANState,make_handler
out=root.parent.parent/"dist/swrlz-forge-moba"
assert (out/"index.html").is_file(),out
state=LANState(ip="127.0.0.1")
server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(state,out))
state.port=server.server_address[1]
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{state.port}"
def send(path,body):
 req=urllib.request.Request(url+path,json.dumps(body).encode("utf-8"),
  {"Content-Type":"application/json"},method="POST")
 with urllib.request.urlopen(req,timeout=3) as response:return json.load(response)
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(channel="chrome",headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--enable-webgl","--enable-unsafe-swiftshader"])
  context=browser.new_context(viewport={"width":412,"height":915},
                              device_scale_factor=2.5,is_mobile=True,has_touch=True)
  page=context.new_page()
  page.goto(url+"/",wait_until="domcontentloaded",timeout=60000)
  page.wait_for_function("() => !!window.SWYRL_ENGINE_LEVELS && !!window.SWYRL_ENGINE_SHEEP_TAG",timeout=45000)
  page.evaluate("() => window.SWYRL_ENGINE_SHEEP_TAG.load()")
  page.evaluate("() => {const d=document.querySelector('#seReleaseNotesDialog');if(d?.open)d.close();}")
  page.locator("#playBtn").click(force=True)
  page.wait_for_function("() => window.SWYRL_ENGINE_LEVELS.status().menuPlaying===true",timeout=15000)
  page.locator("#se146LanOpen").click()
  assert page.locator("#se146LanScreen").is_visible()
  page.wait_for_function("() => !document.querySelector('#se146LanHost').disabled",timeout=12000)
  page.locator("#se146LanHost").click()
  page.wait_for_function("() => document.querySelector('#se148WaitingRoom') && !document.querySelector('#se148WaitingRoom').hidden",timeout=12000)
  assert page.locator("#se148WaitingRoom").is_visible()
  assert page.locator("#se148Slots .se148-slot").count()==8
  assert page.locator("#se148Slots .se148-host").count()==1
  assert page.locator("#se148Start").is_disabled(), "don't fake a networked match"
  assert "host" in page.locator("#se148Authority").inner_text().lower()
  game=state.snapshot()
  assert game and game["players"]==1
  guest=send("/api/lan/join",{"host":"127.0.0.1","port":state.port,
                              "gameId":game["id"],"name":"Clover"})
  assert guest["joined"]
  page.wait_for_function("() => document.querySelector('#se148RoomCount')?.textContent.includes('2 / 8')",timeout=14000)
  assert "Clover" in page.locator("#se148Slots").inner_text()
  assert page.locator("#se148Slots").bounding_box()["height"]>200
  send("/api/lan/leave",{"gameId":game["id"],"playerId":guest["playerId"]})
  page.wait_for_function("() => document.querySelector('#se148RoomCount')?.textContent.includes('1 / 8')",timeout=14000)
  page.locator("#se148Leave").click()
  page.wait_for_function("() => document.querySelector('#se148WaitingRoom').hidden",timeout=10000)
  assert state.snapshot() is None, "host closing must stop the live lobby"
  page.locator("#se146LanBack").click()
  page.locator("#se145ExitEditor").click()
  page.wait_for_function("() => !document.body.classList.contains('se145-runtime')",timeout=9000)
  assert page.locator("#st141LevelBar").is_visible()
  print("SE148_REAL_ANDROID_SIZE_CHROME_HOST_EIGHT_SEATS_GUEST_JOIN_LEAVE_STOP_RESTORE_PASS",flush=True)
  browser.close()
finally:
 server.shutdown();server.server_close()
