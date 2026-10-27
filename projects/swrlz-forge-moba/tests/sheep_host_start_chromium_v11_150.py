#!/usr/bin/env python3
"""Actual 412x915 Chrome §E host starts native Gameplay; real RTC guest receives start."""
import http.server,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root.parent.parent/"dist/swrlz-forge-moba"
assert (out/"index.html").is_file()
class Serve(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(out),**kw)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Serve)
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(channel="chrome",headless=True,args=[
   "--no-sandbox","--disable-dev-shm-usage","--enable-webgl","--enable-unsafe-swiftshader"])
  ctx=browser.new_context(viewport={"width":412,"height":915},device_scale_factor=2.5,
                          is_mobile=True,has_touch=True)
  host=ctx.new_page();guest=ctx.new_page()
  host.goto(f"http://127.0.0.1:{server.server_port}/",wait_until="domcontentloaded",timeout=60000)
  host.wait_for_function("() => !!window.SWYRL_ENGINE_LEVELS && !!window.SWYRL_ENGINE_SHEEP_TAG",timeout=45000)
  host.evaluate("() => window.SWYRL_ENGINE_SHEEP_TAG.load()")
  host.evaluate("() => {const d=document.querySelector('#seReleaseNotesDialog');if(d?.open)d.close();}")
  host.wait_for_timeout(300)
  host.locator("#playBtn").click(force=True)
  host.wait_for_function("() => window.SWYRL_ENGINE_LEVELS.status().menuPlaying",timeout=16000)
  host.locator("#se146LanOpen").click()
  host.evaluate("() => window.SWYRL_ENGINE_LAN.hostPeer()")
  host.wait_for_function("() => !document.querySelector('#se148WaitingRoom').hidden",timeout=10000)
  assert host.locator("#se148Start").is_disabled()
  host.locator("#se149CreateInvite").click()
  host.wait_for_function("() => !!document.querySelector('#se149OfferOut').value",timeout=22000)
  offer=host.locator("#se149OfferOut").input_value()
  guest.goto("about:blank")
  response=guest.evaluate("""async invite => {
   const offer=JSON.parse(atob(invite));const pc=new RTCPeerConnection({iceServers:[]});
   window.guestPC=pc;
   pc.ondatachannel=e=>{
     const ch=e.channel;window.guestChannel=ch;
     ch.onopen=()=>ch.send(JSON.stringify({kind:'hello',name:'Shelter Laptop'}));
     ch.onmessage=ev=>{
       try{const msg=JSON.parse(ev.data);
       if(msg.kind==='roster')window.guestRoster=msg.game;
       if(msg.kind==='match-start')window.guestStart=msg;}catch{}
     };
   };
   await pc.setRemoteDescription({type:'offer',sdp:offer.sdp});
   await pc.setLocalDescription(await pc.createAnswer());
   if(pc.iceGatheringState!=='complete')await new Promise(resolve=>{
     const done=()=>{if(pc.iceGatheringState==='complete'){pc.removeEventListener('icegatheringstatechange',done);resolve();}};
     pc.addEventListener('icegatheringstatechange',done);setTimeout(resolve,8500);
   });
   return btoa(JSON.stringify({protocol:'se149-peer-lan-v1',kind:'answer',
      roomId:offer.roomId,sdp:pc.localDescription.sdp}));
  }""",offer)
  host.locator("#se149ReplyIn").fill(response)
  host.locator("#se149AcceptReply").click()
  host.wait_for_function("() => document.querySelector('#se148RoomCount')?.textContent==='2 / 8 players'",timeout=20000)
  assert host.locator("#se148Start").is_enabled()
  host.locator("#se148Start").click()
  host.wait_for_function("() => window.SWYRL_ENGINE_LEVELS.status().active==='game' && window.SWYRL_ENGINE_LAN.matchStatus().nativeGameplayActive",timeout=20000)
  guest.wait_for_function("() => window.guestStart?.kind==='match-start'",timeout=16000)
  assert guest.evaluate("() => window.guestStart.level")=="game"
  assert host.locator("#se150MatchStatus").is_visible()
  host.locator("#se145ExitEditor").click()
  host.wait_for_function("() => !window.SWYRL_ENGINE_LAN.matchStatus().active",timeout=16000)
  print("SE150_REAL_CHROME_MOBILE_HOST_STARTS_NATIVE_SHEEP_TAG_GUEST_RECEIVES_MATCH_START_STOP_PASS",flush=True)
  browser.close()
finally:
 server.shutdown();server.server_close()
