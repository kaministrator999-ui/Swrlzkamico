"""§E v11.130: second-touchstart browser page-zoom defense and
true sheep-centered skill selection instead of finger-origin build placement."""
from pathlib import Path
import json,hashlib

def once(source,old,new):
 n=source.count(old)
 assert n==1,(old[:170],n)
 return source.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 touch=(root/'runtime/engine_second_touchstart_zoom_guard_v11_130.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',touch+'\nwindow.SWRLZ_FORGE_BUILD=')
 # Previous v11.126 seeded the preview at the sheep, but the older v11.84
 # pointer lifecycle immediately rewrote it with screen raycasts from the
 # building-button finger, including pointerup even for a simple skill tap.
 # Keep the button as a tool *selector*, not a placement world coordinate.
 html=once(html,
   "if(event.pointerId!==stBuildInput.pointer)return;\n event.preventDefault();event.stopImmediatePropagation();\n if(stBuildInput.session!==stSession||!stTouchPlacementEnabled()||event.pointerType==='mouse'",
   "if(event.pointerId!==stBuildInput.pointer)return;\n event.preventDefault();event.stopImmediatePropagation();\n if(stBuildInput.source==='skill')return; // do not aim at the skill icon or finger during selection\n if(stBuildInput.session!==stSession||!stTouchPlacementEnabled()||event.pointerType==='mouse'")
 html=once(html,
   "const source=stBuildInput.source;stBuildInputAim(event);\n if(!stBuildInput.moved&&source==='skill'){stBuildInputFinish('Tool selected',true);st126SeedAtSheep();stUiFeedback('Preview starts at your sheep. Drag on the meadow, release to build.');return;}",
   "const source=stBuildInput.source;\n if(source==='skill'){\n  stBuildInputFinish('Tool selected',true);\n  st126SeedAtSheep();\n  stUiFeedback('Preview begins at your sheep. Touch the meadow to aim, then release to build.');return;\n }\n stBuildInputAim(event);")
 # Pin preview to sheep through the whole skill-to-ground handoff.
 # Existing native meadow pointerdown, drag, site collision and build commit
 # are still responsible for actual placement and remain unchanged.
 html=once(html,
   'SWYRL_ENGINE_DEPLOY_MARKER: V11_129_PROJECT_HANDOFF_PAGE_ZOOM_GUARD',
   'SWYRL_ENGINE_DEPLOY_MARKER: V11_130_SECOND_TOUCH_BROWSER_ZOOM_AND_SHEEP_BUILD_SEED')
 for before,after in [
  ('ENGINE · MAKER v11.129','ENGINE · MAKER v11.130'),
  ('v11.129 · project transition touch protection','v11.130 · mobile page zoom and sheep placement'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.129'","window.SWRLZ_FORGE_BUILD={version:'v11.130'"),
  ('<title>§wyrl§ Engine · Maker v11.129</title>','<title>§wyrl§ Engine · Maker v11.130</title>')
 ]:html=once(html,before,after)
 key='const SE_RELEASE_NOTES='
 start=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[start:])
 notes.update(title='Cancel second browser double-tap early and seed building preview at the sheep',
 date='2026-10-26',changes=[
  'Real Android testing reproduced smaller remaining browser page zoom on rapid taps while selecting starter projects despite v11.129. New passive:false capture listener cancels the second single-finger touchstart within 670ms after a real stationary starter-card touch, before Chrome can begin smart magnification.',
  'The second-touchstart guard explicitly excludes multi-touch pinch, editable inputs, long holds, scrolling and keyboard/mouse and retains earlier 420ms transition shield and site touch-action protections. No browser viewport maximum-scale or global user-scalable restriction.',
  'Fix actual Sheep Tag skill-button placement bug: previous v11.126 sheep-centered preview was overwritten by v11.84 pointermove/pointerup rays originating at the skill icon. Skill-button finger now only selects the tool and re-seeds the existing live preview at the controlled sheep; aiming starts only from a new meadow pointer interaction.',
  'Placing a house still needs an explicit meadow pointer release, native collision checks and available resources; the joystick, other units, safe relocation, non-destructible world ramps and earlier editor project picker remain unchanged.',
  'All 68 bundled assets, 161 earlier source patches, Model Atelier Clover sheep mesh and cosmetic pounce-swurv are preserved.'
 ])
 html=html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[start+n:]
 raw=html.encode('utf8')
 print('SE_V11130_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
