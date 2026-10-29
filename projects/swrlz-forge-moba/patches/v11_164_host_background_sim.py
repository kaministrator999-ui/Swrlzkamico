"""§E v11.164: host-simulation catch-up during background browser operation."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_host_background_sim_v11_164.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_163_GUEST_BUILDING_GROWTH',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_164_HOST_BACKGROUND_SIM')
 for a,b in [
  ('ENGINE · MAKER v11.163','ENGINE · MAKER v11.164'),
  ('v11.163 · host-synchronized growing guest houses',
   'v11.164 · background-safe host game simulation'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.163'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.164'"),
  ('<title>§wyrl§ Engine · Maker v11.163</title>',
   '<title>§wyrl§ Engine · Maker v11.164</title>')
 ]:html=once(html,a,b)
 tag='const SE_RELEASE_NOTES='
 pos=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[pos:])
 notes.update(title='Keep the host game advancing while its browser is backgrounded',
 date='2026-10-28',changes=[
  'Real Android guest screenshot shows 12/12 house replicas synchronized, but 9% construction progress from both host and guest with progress stalled.',
  'The browser host gameplay advances via requestAnimationFrame while LAN snapshots run on a separate interval; switching to the guest browser can stop the host render loop but continue stale world packets.',
  'On each existing host-world snapshot timer, compare real wall-clock passage with native simulated time; advance ONLY the missing host gameplay using bounded native stUpdate physics substeps before broadcasting world state.',
  'Host catch-up advances actual sheep build approaches, authoritative structure progress, native AI and game rules, not merely a guest-side fake house-growth animation.',
  'Never double-step a normally rendering host. Pause, game end and world resets do not accumulate simulation debt. Limit catch-up to three seconds and sixty substeps per timer callback.',
  'Attach lightweight host simulation mode and catch-up telemetry to the existing world packet; show host catch-up status on guests and SWYRL_ENGINE_LAN.hostSimulationClock().',
  'If the phone fully suspends a host page and all its JavaScript timers, no browser-only code can guarantee uninterrupted background multiplayer; a standalone hosted game authority is a future upgrade.',
  'Focused deterministic JS test: stalled 9% house reached full progress in host timer fallback, updates contained 100%, foreground had no double-tick, paused time produced no catch-up debt.',
  'Preserve v11.161 continuous sheep movement, live lobby search, guest house sync, fog and wolf timing. No additional GitHub CI steps; HF release remains package+upload.'
 ])
 html=html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
 return html
