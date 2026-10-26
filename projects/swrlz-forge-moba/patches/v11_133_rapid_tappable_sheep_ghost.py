"""§E v11.133: real Android skill tap/click lifecycle and rapid UI fix."""
from pathlib import Path
import json,hashlib

def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:170],n)
 return s.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/sheep_build_skill_click_rapid_ui_v11_133.css').read_text(encoding='utf8')
 js=(root/'runtime/sheep_build_skill_click_rapid_ui_v11_133.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se133-rapid-and-skill-click">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 # v11.130 fixed the initial seed, but omitted the synthetic click following
 # pointerup. That click invoked the native skill onclick a second time and
 # toggled its mode OFF; the ghost vanished. Intercept only that duplicate.
 html=once(html,
  'if(world)stBuildInputAim(event);else st126SeedAtSheep();',
  'if(world)stBuildInputAim(event);else st133SeedWhileSkillHeld();')
 # Keep ghost at sheep until dragged into open meadow. Pointer capture keeps
 # target on the button even when finger is out in the 3D world, so test the
 # actual on-screen element under the finger rather than event.target.
 html=once(html,
  "if(stBuildInput.source==='skill')return; // do not aim at the skill icon or finger during selection",
  "if(stBuildInput.source==='skill'&&!st133CanAimSkillAt(event.clientX,event.clientY))return; // preview stays at sheep until finger enters open meadow")
 html=once(html,
  "const source=stBuildInput.source;\n if(source==='skill'){\n  stBuildInputFinish('Tool selected',true);\n  st126SeedAtSheep();\n  stUiFeedback('Preview begins at your sheep. Touch the meadow to aim, then release to build.');return;\n }\n stBuildInputAim(event);",
  "const source=stBuildInput.source;\n if(source==='skill')st133RememberBuildTouch(event,stBuildInput.kind);\n if(source==='skill'&&!stBuildInput.moved){\n  stBuildInputFinish('Tool selected',true);\n  st126SeedAtSheep();\n  stUiFeedback('House ghost ready at your sheep. Drag onto meadow or touch meadow to place.');return;\n }\n stBuildInputAim(event);")
 # If the skill dragged off button but released above another UI control or
 # blocked ground, keep the selected ghost rather than cancelling the tool.
 html=once(html,
  "if(!stTouchPlacement.valid){stBuildInputReject('Drop on clear meadow ground, away from controls.');return;}",
  "if(!stTouchPlacement.valid){if(source==='skill'){stBuildInputFinish('Tool selected',true);st126SeedAtSheep();return;}stBuildInputReject('Drop on clear meadow ground, away from controls.');return;}")
 html=once(html,
  "if(!fit?.ok){stBuildInputReject(fit?.reason||'That site is blocked. Drag a building icon to try another spot.');return;}",
  "if(!fit?.ok){if(source==='skill'){stBuildInputFinish('Tool selected',true);st126SeedAtSheep();stUiFeedback(fit?.reason||'Choose a clear spot.',true);return;}stBuildInputReject(fit?.reason||'That site is blocked. Drag a building icon to try another spot.');return;}")
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_132_RAPID_BUILD_UNDERPASS_AND_SHEEP_WIREFRAME',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_133_TOUCHABLE_RAPID_AND_PERSISTENT_SHEEP_GHOST')
 for old,new in [
  ('ENGINE · MAKER v11.132','ENGINE · MAKER v11.133'),
  ('v11.132 · rapid building and raised crossings','v11.133 · tappable rapid and sheep house preview'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.132'","window.SWRLZ_FORGE_BUILD={version:'v11.133'"),
  ('<title>§wyrl§ Engine · Maker v11.132</title>','<title>§wyrl§ Engine · Maker v11.133</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Rapid Build beside Income, real touch toggle and persistent sheep-origin building ghost',
  date='2026-10-26',changes=[
   'Owner screenshot confirmed v11.132 Rapid button mid-map, not next to Income in lower-right; it appeared square and could not be toggled. Move Rapid and Rotate controls into native Sheep Tag build-skill cluster, position circular Rapid immediately LEFT of Income, and explicitly set pointer-events:auto despite HUD inherited pointer-events:none. Keep it touch-friendly, accessible and showing ON/OFF state.',
   'Fix native Android pointerup followed by synthesized click: after touch selected the house tool and seeded the hologram at the sheep, a second native onclick toggled off the same tool and removed the ghost. Ignore only that one handled touch-generated skill click. Keyboard, mouse and future intentional taps remain unchanged.',
   'The building hologram appears at the sheep while the build skill is held. Dragging the SAME finger from the skill icon out onto clear meadow starts moving the ghost only after leaving the icon, and releasing on valid ground can order a build. Alternatively tap the skill then drag across the meadow to position it. UI/blocked releases keep the selected tool active at sheep instead of silently cancelling it.',
   'Viewport child layers now count as valid visible meadow for hit testing. Original grid, collision, resources, landscape and successful Rapid Build repeat mode remain active.',
   'Rotated permanent crossings, under-deck ground traversal, sheep x-ray wireframe, Mirror decoy, all 164 earlier patches and 68 native assets remain unchanged.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11133_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
