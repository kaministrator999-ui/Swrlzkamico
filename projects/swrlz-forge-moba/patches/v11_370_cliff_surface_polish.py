"""§E v11.370 — polish only the real WebXR Cliff Hand stone material, not anatomy."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_370_CLIFF_STONE_SURFACE_POLISH'

def one(src,old,new,name):
    n=src.count(old)
    if n!=1:raise AssertionError(('v11.370',name,n,old[:110]))
    return src.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/webxr_cliff_material_polish_v11_370.js').read_text('utf8')
    for token in ['function se370SurfaceUV(mesh,size){','function se370RefinePixel(',
                  'function se370BakeTiles(img,mesh){',
                  'function se370PolishedCliffMaterial(part){',
                  'window.SWYRL_ENGINE_CLIFF_POLISH_370']:
        if token not in js:raise AssertionError(('missing polish runtime',token))
    for needle in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_369_WEBXR_CLIFF_STONE_CLONE',
                   'se369CliffFromXRScene','se281RockScene=se367AnatomicalRockScene;',
                   'function se292WristMossKnuckleMaterial(part){',
                   'async function se358WebXRHandScene(side){']:
        if needle not in html:raise AssertionError(('missing source prerequisite',needle))
    html=one(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
             'add isolated stone map material after WebXR Cliff starter registration')
    html=one(html,
        """if(part?.cliffPBR?.variant==='webxr-cliff'){
  const stone=se290CliffMaterial(part);
  stone.name='Cliff Hand · WebXR UV + original sandstone PBR atlas';
  return stone;
 }""",
        """if(part?.cliffPBR?.variant==='webxr-cliff'){
  return se370PolishedCliffMaterial(part);
 }""",
        'replace only the WebXR Cliff material variant; leave all other materials')
    for old,new,name in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_369_WEBXR_CLIFF_STONE_CLONE',MARKER,'release marker'),
      ('ENGINE · MAKER v11.369','ENGINE · MAKER v11.370','header'),
      ('v11.369 · real WebXR mesh with Cliff stone PBR',
       'v11.370 · refined Cliff cracks, moss and worn cuff','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.369'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.370'",'build version'),
      ('<title>§wyrl§ Engine · Maker v11.369</title>',
       '<title>§wyrl§ Engine · Maker v11.370</title>','browser title')
    ]:
        html=one(html,old,new,name)
    old=" source.engine='§wyrl§ Engine · Maker v11.369';source.version=11.369;"
    if html.count(old)!=5:raise AssertionError(('v11.370 provenance count',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.370';source.version=11.370;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(item.get('version')=='v11.369' for item in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.369','changes':notes.get('changes',[])})
    notes.update(version='v11.370',date='2026-11-09',
      title='WebXR Cliff Hand surface polish: organic cracks, located moss and worn wrist',
      changes=[
       'Keep the approved 1360-vertex WebXR anatomical Cliff mesh, source UV islands, 25 joint landmarks and 17-bone rig entirely unchanged.',
       'Build a mapped 384px one-time Cliff PBR material pass from the original sandstone atlas: graded interrupted stone cracks instead of identical outlined tiles; slight mineral grain; normal-map relief moderated.',
       'Use actual WebXR mesh UV triangles to localize sparse moss near wrist, thumb web and dorsal creases, keeping fingertips and broad palm surfaces cleaner without assuming the UV islands follow world height.',
       'Use material-only wrist-edge erosion, subtle AO/roughness contrast and keep the source owner color/normal/roughness/AO channels aligned. No additional triangles, cliff objects, cuffs or new UI.',
       'Leave the improved 89-rock Rocky Anime Hand, independent WebXR hands, Quest controllers, saved projects and native UV editor untouched.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
