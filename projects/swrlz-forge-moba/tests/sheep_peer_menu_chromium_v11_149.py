#!/usr/bin/env python3
"""Real 412x915 Chrome editor preview + hosted-style peer invite and guest session."""
import http.server,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root.parent.parent/"dist/swrlz-forge-moba"
assert (out/"index.html").is_file(),out
class Serve(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(out),**kw)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Serve)
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(channel="chrome",headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--enable-webgl","--enable-unsafe-swiftshader"])
  context=browser.new_context(viewport={"width":412,"height":915},has_touch=True,is_mobile=True,device_scale_factor=2.5)
  host=context.new_page()
  guest=context.new_page()
  for page in (host,guest):
   page.goto(f"http://127.0.0.1:{server.server_port}/",wait_until="domcontentloaded")
   page.wait_for_function("() => !!window.SWYRL_ENGINE_SHEEP_TAG && !!window.SWYRL_ENGINE_LEVELS",timeout=45000)
   page.evaluate("() => window.SWYRL_ENGINE_SHEEP_TAG.load()")
   page.evaluate("() => {const d=document.querySelector('#seReleaseNotesDialog');if(d?.open)d.close();}")
   page.wait_for_function("() => !!document.querySelector('#st141MenuPreview')",timeout=20000)
   assert page.locator("#se149PreviewLan").count()==1
   assert page.locator("#se149PreviewLan").is_disabled()
   page.locator("#playBtn").click(force=True)
   page.wait_for_function("() => window.SWYRL_ENGINE_LEVELS.status().menuPlaying",timeout=20000)
   page.locator("#se146LanOpen").click()
   page.wait_for_function("() => !!document.querySelector('#se149OfferIn')",timeout=7000)
  # Local HTTP launch normally uses the Python bridge; force the new native
  # browser-only direct-peer path without pretending that this is public HTTPS.
  host.evaluate("() => se149Host()")
  host.wait_for_function("() => !!document.querySelector('#se148WaitingRoom') && !document.querySelector('#se148WaitingRoom').hidden")
  assert host.locator("#se148Slots .se148-slot").count()==8
  host.locator("#se149CreateInvite").click()
  host.wait_for_function("() => !!document.querySelector('#se149OfferOut').value",timeout=20000)
  invite=host.locator("#se149OfferOut").input_value()
  guest.locator("#se148PlayerName").fill("Clover")
  guest.locator("#se149OfferIn").fill(invite)
  guest.locator("#se149JoinInvite").click()
  guest.wait_for_function("() => !!document.querySelector('#se149AnswerOut')?.value",timeout=20000)
  reply=guest.locator("#se149AnswerOut").input_value()
  host.locator("#se149ReplyIn").fill(reply)
  host.locator("#se149AcceptReply").click()
  host.wait_for_function("() => document.querySelector('#se148RoomCount')?.textContent.includes('2 / 8')",timeout=25000)
  assert "Clover" in host.locator("#se148Slots").inner_text()
  guest.wait_for_function("() => document.querySelector('#se148RoomCount')?.textContent.includes('2 / 8')",timeout=25000)
  assert guest.locator("#se148Start").is_hidden()
  assert host.locator("#se148Start").is_disabled()
  guest.locator("#se148Leave").click()
  host.wait_for_function("() => document.querySelector('#se148RoomCount')?.textContent.includes('1 / 8')",timeout=12000)
  host.locator("#se148Leave").click()
  host.locator("#se146LanBack").click()
  host.locator("#se145ExitEditor").click()
  host.wait_for_function("() => !document.body.classList.contains('se145-runtime')",timeout=12000)
  assert host.locator("#se149PreviewLan").count()==1
  print("SE149_ANDROID_CHROME_MENU_PARITY_BROWSER_P2P_HOST_GUEST_ROSTER_STOP_PASS",flush=True)
  browser.close()
finally:
 server.shutdown();server.server_close()
