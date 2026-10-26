"""§E v11.123: intentional sheep-safe house placement, native main toolbar workflow, inset HUD."""
from pathlib import Path
import hashlib,json
def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:140],n)
 return s.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parent.parent
 safe=(root/'runtime/sheep_safe_snap_v11_123.js').read_text(encoding='utf8')
 bar=(root/'runtime/engine_main_toolbar_v11_123.js').read_text(encoding='utf8')
 css=(root/'runtime/engine_main_toolbar_sheep_hud_v11_123.css').read_text(encoding='utf8')
 # Base building collision: flush, *non-overlapping* edges are valid.
 # Earlier +.02 margin incorrectly rejected house-to-house contact, producing
 # the visually misleading tiny-gap layouts that the user reported.
 html=once(html,
 "Math.abs(snappedX-building.pos.x)<1.2+building.halfX+.02&&Math.abs(snappedZ-building.pos.z)<1.2+building.halfZ+.02",
 "Math.abs(snappedX-building.pos.x)<1.2+building.halfX-0.00001&&Math.abs(snappedZ-building.pos.z)<1.2+building.halfZ-0.00001")
 # Late installation, after Sheep Tag's historical lane/collision improvements.
 # Every placement preview, command, and final revalidation uses the same
 # stCanBuild wrapper and stLanesSnapHouse, with no second game state.
 html=once(html,"window.SWRLZ_FORGE_BUILD=",safe+'\n'+bar+"\nwindow.SWRLZ_FORGE_BUILD=")
 html=html.replace('</head>','<style id="se-v11123-workflow-safe-lanes">'+css+'</style>\n</head>',1)
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_122_SITEWIDE_EDITOR_TOUCH_BOUNDARIES',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_123_SHEEP_LANE_GRID_AND_WORKFLOW_TOOLBAR')
 for a,b in [
 ('ENGINE · MAKER v11.122','ENGINE · MAKER v11.123'),
 ('v11.122 · full-engine touch guard','v11.123 · sheep lanes and organized editor toolbar'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.122'","window.SWRLZ_FORGE_BUILD={version:'v11.123'"),
 ('<title>§wyrl§ Engine · Maker v11.122</title>','<title>§wyrl§ Engine · Maker v11.123</title>')
 ]:html=once(html,a,b)
 tag='const SE_RELEASE_NOTES=';index=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[index:])
 notes.update(title='Sheep-safe snap placements, Projects-first main toolbar, inset HUD controls',
 date='2026-10-25',changes=[
 'Sheep Tag house placement uses a consistent 0.3 m grid and magnetizes near house faces into either true flush contact or at least a 0.9 m sheep-passable lane (expanded for user-defined sheep radius).',
 'Validation rejects narrow misleading gaps in the exact same native preview/build pipeline; keeps authored houses unchanged, collision checks, builder escape and original navigation.',
 'Main §E header orders Projects first then Play, Pause, Simulate and Stop while preserving native button nodes/actions; mobile targets are slightly larger.',
 'Joystick and right-side Sheep Tag building/ability rings sit a little farther inward from the phone edges without changing their sizes or drag behavior.',
 'Preserves Model Atelier tools, whole-editor double-tap/hold guards and bundled native game assets.'
 ])
 html=html[:index]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[index+n:]
 raw=html.encode('utf8')
 print('SWRLZ_V11123_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
