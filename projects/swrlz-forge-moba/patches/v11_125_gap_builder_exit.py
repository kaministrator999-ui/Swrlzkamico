"""§E v11.125: truthful local gaps and validated nearest-side builder exit."""
from pathlib import Path
import hashlib,json

def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:180],n)
 return s.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parent.parent
 js=(root/'runtime/sheep_gap_builder_exit_v11_125.js').read_text(encoding='utf8')
 # The original native self-occupancy check ran before the later vetted
 # nearest-side exit path, making that path unreachable. Exempt only the
 # living builder, not other units; all obstacle/house placement guards stay.
 html=once(html,
  'for(const unit of s.units)if(!unit.captured&&Math.abs(snappedX-unit.pos.x)',
  'for(const unit of s.units)if(unit!==owner&&!unit.captured&&Math.abs(snappedX-unit.pos.x)')
 # v11.90 intentionally disabled native relocation; new owner direction
 # supersedes that single line. The existing stLanesEjection routine
 # searches closest collision-free side and refuses unsafe outcomes.
 html=once(html,'stLanesEjection=()=>null;',
  '/* §E v11.125: allow existing validated closest-side stLanesEjection. */')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'Red: blocked. Physical diameters: sheep',
  'Red: blocked. Cyan/Gold: locally swept clear (not a full-route guarantee). Physical diameters: sheep')
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_124_FLUSH_OR_PASSABLE_SHEEP_BUILD_PLACEMENT',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_125_CLEAR_GAPS_AND_SAFE_BUILDER_EXIT')
 for a,b in [
  ('ENGINE · MAKER v11.124','ENGINE · MAKER v11.125'),
  ('v11.124 · honest sheep house placement','v11.125 · clear gaps and safe build exit'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.124'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.125'"),
  ('<title>§wyrl§ Engine · Maker v11.124</title>',
   '<title>§wyrl§ Engine · Maker v11.125</title>')
 ]:
  html=once(html,a,b)
 tag='const SE_RELEASE_NOTES='
 index=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[index:])
 notes.update(
  title='Locally truthful Sheep Tag gaps and nearest-safe builder relocation',
  date='2026-10-26',
  changes=[
   'At least 1.20m house gaps with a verified local swept sheep lane are labeled SHEEP CLEAR or BOTH CLEAR instead of incorrectly showing BLOCKED because an unrelated house lies beyond the measured gap.',
   'The colored clearance overlay explicitly reports local swept clearance; it does not claim an entire connected route is navigable.',
   'Building where the sheep stands is allowed only when the already-native nearest-outside-side search finds a collision-free destination clear of terrain, other structures, and other units.',
   'If no safe side exists the placement is rejected before spending gold or creating a building.',
   'Collision footprints, house snapping, joystick steering, other-unit protection, HUD layout, previous patches and native scene assets are preserved.'
  ])
 html=html[:index]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[index+n:]
 raw=html.encode('utf8')
 print('SWRLZ_V11125_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
