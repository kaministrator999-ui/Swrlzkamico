"""§E v11.369: replace ONLY the Cliff starter mesh with WebXR reference + original stone PBR maps."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_369_WEBXR_CLIFF_STONE_CLONE'
def one(s,a,b,label):
 n=s.count(a)
 if n!=1:raise AssertionError(('v11.369',label,n,a[:100]))
 return s.replace(a,b,1)
def apply(html):
 js=(ROOT/'runtime/webxr_cliff_stone_v11_369.js').read_text('utf8')
 for token in ['async function se369CliffFromXRScene(){','se358WebXRHandScene(\'right\')',
               'function se369MapReferenceVertex(x,y,z){',
               'se284OpenPlainHand=se369OpenCliffHand;',
               'SWYRL_ENGINE_WEBXR_CLIFF_369']:
  if token not in js:raise AssertionError(('missing v11.369 runtime',token))
 for needle in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_368_UV_CAMERA_ALIGNMENT',
   'async function se358WebXRHandScene(side){',
   'function se220CreateHandRig(digits){',
   'function se292WristMossKnuckleMaterial(part){',
   'const se365OriginalStoneScene=se281RockScene;',
   'se281RockScene=se367AnatomicalRockScene;',
   'window.SWYRL_ENGINE_WEBXR_HAND_STARTERS=Object.freeze']:
  if needle not in html:raise AssertionError(('missing Cliff clone prerequisite',needle))
 html=one(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
   'register isolated Cliff clone loader after original WebXR hand and rock models')
 # The Cliff material path uses the original PBR maps without obsolete
 # knuckle crystal overlays mapped for the old procedural UV topology.
 html=one(html,'function se292WristMossKnuckleMaterial(part){',
  """function se292WristMossKnuckleMaterial(part){
 if(part?.cliffPBR?.variant==='webxr-cliff'){
  const stone=se290CliffMaterial(part);
  stone.name='Cliff Hand · WebXR UV + original sandstone PBR atlas';
  return stone;
 }""",'use unchanged cliff PBR tiles on genuine WebXR UV islands')
 # Update the original card instead of adding a confusing extra project.
 html=one(html,'<strong>Plain Hand Base · Smooth Cliff Hand</strong>',
  '<strong>Cliff Hand · WebXR Anatomical Stone</strong>',
  'accurately label replacement in model starters')
 for old,new,label in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_368_UV_CAMERA_ALIGNMENT',MARKER,'marker'),
  ('ENGINE · MAKER v11.368','ENGINE · MAKER v11.369','header'),
  ('v11.368 · auto-align visible UV front and up',
   'v11.369 · real WebXR mesh with Cliff stone PBR','headline'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.368'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.369'",'build'),
  ('<title>§wyrl§ Engine · Maker v11.368</title>',
   '<title>§wyrl§ Engine · Maker v11.369</title>','title')
 ]:html=one(html,old,new,label)
 before=" source.engine='§wyrl§ Engine · Maker v11.368';source.version=11.368;"
 if html.count(before)!=5:raise AssertionError(('scene provenance',html.count(before)))
 html=html.replace(before,
  " source.engine='§wyrl§ Engine · Maker v11.369';source.version=11.369;")
 at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
 notes,count=json.JSONDecoder().raw_decode(html[at:])
 if not any(x.get('version')=='v11.368' for x in notes.get('history',[])):
  notes.setdefault('history',[]).insert(0,{'version':'v11.368','changes':notes.get('changes',[])})
 notes.update(version='v11.369',date='2026-11-09',
  title='Cliff Hand replaced with real WebXR hand topology and cliff material',
  changes=[
   'Replace the Plain Hand Base / Cliff Hand starter with a newly cloned WebXR right-hand mesh, not another procedurally reshaped SDF. The source right/left WebXR reference projects remain unchanged.',
   'Retain the 1360 authentic WebXR hand vertices, 2314 triangles, source UV islands and transformed 25 joint landmarks; orient and position the mesh against our 17-bone hand rig.',
   'Apply the original owner-derived Cliff sandstone color, tangent normal, roughness and AO maps via the existing PBR material. Old UV-specific decorative crystal overlays are disabled because they do not align with the new hand UVs.',
   'Only the Cliff starter is replaced. The improved complete 89-rock Rocky Anime Hand, UV Editor alignment controls, Quest controllers, native model tools and previously saved projects are untouched.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+count:]
