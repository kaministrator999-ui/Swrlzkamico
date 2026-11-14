"""§E v11.446: Face mode selects complete planar surface regions on tap.

This links the phone/desktop component pointer path to the already supported
native connected-coplanar face selector used in VR. No new geometry operator.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_446_PLANAR_FACE_PICK'
def once(html,old,new):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.446 anchor',old[:160],count))
    return html.replace(old,new,1)

def apply(html):
    helper="""/* SE446_PLANAR_FACE_TAP_START */
function se446SelectPlanarFace(hitId){
 // A normal Face tap should pick a whole flat surface (two triangles on a
 // default cube), not expose its implementation triangulation to beginners.
 // Multi intentionally retains the existing individual-triangle precision.
 if(atelierComponentMode!=='face'||atelierComponentMulti||!Number.isInteger(hitId))
  return false;
 const result=se430ModelWorkshop.selectRegion(hitId,selection);
 if(!result?.ok){
  const reason=result?.reason||'Could not select the complete planar surface.';
  const hint=/Convert this plain primitive/.test(reason)?
   'Make mesh editable first, then tap anywhere on the square face.':reason;
  status(hint,true);
 }
 return true;
}
/* SE446_PLANAR_FACE_TAP_END */
"""
    html=once(html,'function atelierComponentPointerUp(e){',helper+'function atelierComponentPointerUp(e){')
    html=once(html,
     "if(!d.moved)atelierComponentChoose(atelierComponentHit(e));",
     "if(!d.moved){const hitId=atelierComponentHit(e);if(!se446SelectPlanarFace(hitId))atelierComponentChoose(hitId);}")
    # Keep the mobile UI honest: topology still contains triangles, but the
    # native region-selection flow treats a flat connected patch as one face.
    html=once(html,
      "selection.ids.length+' selected';",
      "(selection.mode==='face'?selection.ids.length+' underlying triangles selected':selection.ids.length+' selected');")
    html=once(html,
      "'Tap faces; Select flat region collects connected coplanar triangles.'",
      "'Tap once to select the whole connected flat face (both triangles on a cube). Multi selects individual triangles.'")
    html=once(html,
      "publish(result.triangleIds.length+' connected coplanar triangles selected. Inset creates an inner face; Extrude adds connected depth.');",
      "publish('1 flat face selected ('+result.triangleIds.length+' underlying triangles). Inset creates an inner face; Extrude adds connected depth.');")
    # VR already routes Trigger into the native region selector. Its status
    # must label the selection as one planar area rather than N face objects.
    html=once(html,
      "String(state.manualSelection?.faceCount||0)+' FACES · '",
      "(state.manualSelection?.faceCount?'1 FLAT FACE · '+state.manualSelection.faceCount+' TRIANGLES':'NO FACE SELECTED')+' · '")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_445_SHAPE_FACE_DISCOVERY',MARKER),
      ('ENGINE · MAKER v11.445','ENGINE · MAKER v11.446'),
      ('v11.445 · discoverable sculpt and face tools','v11.446 · whole flat face selection'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.445'","window.SWRLZ_FORGE_BUILD={version:'v11.446'"),
      ('<title>§wyrl§ Engine · Maker v11.445</title>','<title>§wyrl§ Engine · Maker v11.446</title>')
    ]:html=once(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.445';source.version=11.445;"
    assert html.count(old)==5,('v11.446 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.446';source.version=11.446;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[entry for entry in notes.get('history',[]) if entry.get('version')!='v11.445']
    notes['history'].insert(0,{'version':'v11.445','changes':notes.get('changes',[])})
    notes.update(version='v11.446',date='2026-11-14',
      title='Whole planar face selection for Inset and Extrude',
      changes=[
      'In phone/desktop Face mode a normal tap now selects the native connected coplanar region, so either triangle of a square cube side selects both triangles as one complete flat face.',
      'The native planar-region selector is reused; there is no new geometry algorithm, automatic primitive conversion, or unexpected Undo checkpoint.',
      'Face Multi mode retains precise individual-triangle picks for advanced mesh edits; Box/Lasso and Vertex/Edge selection are unchanged.',
      'The selection hints distinguish one flat face from its underlying triangles. VR already selects a planar region and now labels its status correctly.',
      'A plain primitive still needs Make mesh editable before native Inset/Extrude; the tap gives an actionable conversion hint rather than silently selecting a misleading triangle.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
