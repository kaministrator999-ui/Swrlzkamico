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
  host.goto(f"http://127.0.0.1:{server.server_port}/",wait_until="domcontentloaded")
  host.wait_for_function("() => !!window.SWYRL_ENGINE_SHEEP_TAG && !!window.SWYRL_ENGINE_LEVELS",timeout=45000)
  host.evaluate("() => window.SWYRL_ENGINE_SHEEP_TAG.load()")
  host.evaluate("() => {const d=document.querySelector('#seReleaseNotesDialog');if(d?.open)d.close();}")
  host.wait_for_timeout(400)
  host.wait_for_function("() => !!document.querySelector('#st141MenuPreview')",timeout=20000)
  assert host.locator("#se149PreviewLan").count()==1
  assert host.locator("#se149PreviewLan").is_disabled()
  print("SE149_BEFORE_PLAY",host.evaluate("() => window.SWYRL_ENGINE_LEVELS.status()"),flush=True)
  host.locator("#playBtn").click(force=True)
  host.wait_for_function("() => window.SWYRL_ENGINE_LEVELS.status().menuPlaying",timeout=20000)
  host.locator("#se146LanOpen").click()
  host.wait_for_function("() => !!document.querySelector('#se149OfferIn')",timeout=7000)
  # Local HTTP launch normally uses the Python bridge; force the new native
  # browser-only direct-peer path without pretending that this is public HTTPS.
  host.evaluate("() => window.SWYRL_ENGINE_LAN.hostPeer()")
  host.wait_for_function("() => !!document.querySelector('#se148WaitingRoom') && !document.querySelector('#se148WaitingRoom').hidden")
  assert host.locator("#se148Slots .se148-slot").count()==8
  host.locator("#se149CreateInvite").click()
  host.wait_for_function("() => !!document.querySelector('#se149OfferOut').value",timeout=20000)
  invite=host.locator("#se149OfferOut").input_value()
  guest.goto("about:blank")
  reply=guest.evaluate("""async (invite) => {
    const offer=JSON.parse(atob(invite));
    const pc=new RTCPeerConnection({iceServers:[]});window.guestPC=pc;
    pc.ondatachannel=event=>{
      const channel=event.channel;window.guestChannel=channel;
      channel.onopen=()=>channel.send(JSON.stringify({kind:'hello',name:'Clover'}));
      channel.onmessage=event=>{
        try{if(JSON.parse(event.data).kind==='roster')window.guestRoster=JSON.parse(event.data).game;}catch{}
      };
    };
    await pc.setRemoteDescription({type:'offer',sdp:offer.sdp});
    await pc.setLocalDescription(await pc.createAnswer());
    if(pc.iceGatheringState!=='complete'){
      await new Promise(resolve=>{
       const on=()=>{if(pc.iceGatheringState==='complete'){pc.removeEventListener('icegatheringstatechange',on);resolve();}};
       pc.addEventListener('icegatheringstatechange',on);
       setTimeout(resolve,8500);
      });
    }
    return btoa(JSON.stringify({protocol:'se149-peer-lan-v1',kind:'answer',
      roomId:offer.roomId,sdp:pc.localDescription.sdp}));
  }""",invite)
  host.locator("#se149ReplyIn").fill(reply)
  host.locator("#se149AcceptReply").click()
  host.wait_for_function("() => document.querySelector('#se148RoomCount')?.textContent.includes('2 / 8')",timeout=25000)
  assert "Clover" in host.locator("#se148Slots").inner_text()
  guest.wait_for_function("() => window.guestRoster?.players===2",timeout=25000)
  assert host.locator("#se148Start").is_disabled()
  guest.evaluate("() => window.guestPC.close()")
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
