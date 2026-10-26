"""§E v11.126: start house ghosts at the sheep, add permanent raised crossings,
and let sheep use Mirror/Totem sooner without changing combat/collision systems."""
from pathlib import Path
import hashlib,json

def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:180],n)
 return s.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parent.parent
 js=(root/'runtime/sheep_centered_placement_world_routes_magic_v11_126.js').read_text(encoding='utf8')
 # The existing §E v11.84 pointer owner remains sole input owner. Its
 # skill tap now leaves a preview at the sheep; no skill-button drag required.
 html=once(html,
  'if(world)stBuildInputAim(event);else stTouchPlacementHide(null);',
  'if(world)stBuildInputAim(event);else st126SeedAtSheep();')
 html=once(html,
  "if(!stBuildInput.moved&&source==='skill'){stBuildInputFinish('Tool selected',true);stUiFeedback('Drag on the meadow and release to place.');return;}",
  "if(!stBuildInput.moved&&source==='skill'){stBuildInputFinish('Tool selected',true);st126SeedAtSheep();stUiFeedback('Preview starts at your sheep. Drag on the meadow, release to build.');return;}")
 html=once(html,
  "b.title=f.ok?'Drag to place · release to build':stBuildInputFundsMessage(kind);",
  "b.title=f.ok?'Tap: preview at sheep · drag on meadow to build':stBuildInputFundsMessage(kind);")
 html=once(html,
  "Drag a house above your finger; release on green ground to build.",
  "Preview starts at your sheep. Drag on the meadow; release on green to build.")
 # Native totem conversion only needs one completed owned house (not 9).
 # The status HUD must report the same threshold; no false density values.
 html=once(html,"if(count<=8)return stResult(false,'This settlement needs nine allied houses inside the density radius.',{density:count,required:9});",
                 "if(count<1)return stResult(false,'Complete a house before converting it into a totem.',{density:count,required:1});")
 html=once(html,"densityRequired:9,upper:","densityRequired:1,upper:")
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_125_CLEAR_GAPS_AND_SAFE_BUILDER_EXIT',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_126_SHEEP_CENTERED_BUILD_PERMANENT_ROUTES_READY_SKILLS')
 for a,b in [
  ('ENGINE · MAKER v11.125','ENGINE · MAKER v11.126'),
  ('v11.125 · clear gaps and safe build exit','v11.126 · sheep-centered build and permanent routes'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.125'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.126'"),
  ('<title>§wyrl§ Engine · Maker v11.125</title>',
   '<title>§wyrl§ Engine · Maker v11.126</title>')
 ]:html=once(html,a,b)
 tag='const SE_RELEASE_NOTES='
 index=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[index:])
 notes.update(title='Sheep-centered construction, three permanent raised crossings, ready-at-start magic',
  date='2026-10-26',changes=[
   'Tap a house skill once to show its true live building preview at the controlled sheep. Drag directly on the meadow to move the preview and release to place; skill-to-meadow dragging is optional.',
   'The canonical Moonbell Sheep Tag starter includes three prebuilt crossing groups, each with two functioning ramps and a completed connecting deck; routes are scenery and cannot be damaged, sold, or removed during play.',
   'Player-built walls, ramps and houses retain their normal collision, health, costs, destruction and owner rules.',
   'Sheep Mirror (Illusive Split) is unlocked at level one, is ready immediately, and recharges in 12 seconds. Repeatable Totem recharges in 25 seconds and needs only one completed owned house to convert.',
   'Earlier Sheep Tag v11.125 passage and builder relocation behavior, joystick movement, authoring, editor history, 68 bundled assets and previous patches remain intact.'
  ])
 html=html[:index]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[index+n:]
 raw=html.encode('utf8')
 print('SWRLZ_V11126_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
