"""§E v11.124: enforce honest flush-or-passable sheep building placement."""
from pathlib import Path
import hashlib,json
def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:140],n)
 return s.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parent.parent
 js=(root/'runtime/sheep_build_passable_grid_v11_124.js').read_text(encoding='utf8')
 # Late wrapper of the native snap, placement validator and clearance overlay.
 # Does not alter any sheep movement or player analog input functions.
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,
  "Sheep need '+(stUnitRadius('sheep')*2).toFixed(2)+' m; wolves '",
  "Physical diameters: sheep '+(stUnitRadius('sheep')*2).toFixed(2)+' m; wolves '")
 html=once(html,
  "Gold circle: no building.';legend.style.top",
  "Safe snapped sheep lanes '+stSafeLaneWidth().toFixed(2)+' m minimum. Gold circle: no building.';legend.style.top")
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_123_SHEEP_LANE_GRID_AND_WORKFLOW_TOOLBAR',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_124_FLUSH_OR_PASSABLE_SHEEP_BUILD_PLACEMENT')
 for a,b in [
 ('ENGINE · MAKER v11.123','ENGINE · MAKER v11.124'),
 ('v11.123 · sheep lanes and organized editor toolbar',
  'v11.124 · honest sheep house placement'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.123'",
  "window.SWRLZ_FORGE_BUILD={version:'v11.124'"),
 ('<title>§wyrl§ Engine · Maker v11.123</title>',
  '<title>§wyrl§ Engine · Maker v11.124</title>')
 ]:html=once(html,a,b)
 tag='const SE_RELEASE_NOTES=';index=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[index:])
 notes.update(title='Sheep Tag housing grids snap flush or leave a genuinely navigable passage',
 date='2026-10-25',changes=[
 'Sheep Tag no longer accepts construction gaps that look sheep-passable but strand a sheep.',
 'Near another house, building placement snaps to visually flush contact or an actual safe lane (1.20m at default sheep radius, enlarging for larger sheep).',
 'Existing gameplay footprints and swept collision enforce flush construction; all old houses retain their positions.',
 'The exact native preview/build validator rejects intermediate cardinal and diagonal slits and checks swept passage clearance including an additional blocking building.',
 'The clearance overlay no longer labels a 0.90m navigationally unsafe lane SHEEP ONLY; it reports BLOCKED and the safe snapping width.',
 'Joysticks, movement, wolf routes, editor menu, insets and user-input gestures are unchanged.'
 ])
 html=html[:index]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[index+n:]
 raw=html.encode('utf8')
 print('SWRLZ_V11124_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
