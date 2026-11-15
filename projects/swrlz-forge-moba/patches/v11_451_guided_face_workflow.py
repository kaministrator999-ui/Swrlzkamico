"""§E v11.451: guided native face tools and live modifier previews.

The original model workshop remains the sole geometry/Undo owner. Hide its
duplicate proxy controls only while the guided Face workflow is open; users
can expose all advanced native controls on demand.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_451_GUIDED_FACE_WORKFLOW'

def one(src,old,new):
 n=src.count(old)
 if n!=1:raise AssertionError(('v11.451 anchor',old[:160],n))
 return src.replace(old,new,1)

def apply(html):
 guide=(ROOT/'runtime/model_guided_face_workflow_v11_451.js').read_text('utf8')
 style=(ROOT/'runtime/model_guided_face_workflow_v11_451.css').read_text('utf8')
 html=one(html,'/* SE430_MODEL_BEGINNER_UI_END */',
  '/* SE430_MODEL_BEGINNER_UI_END */\n'+guide)
 html=one(html,'</head>',
  '<style id="se451GuidedFaceStyles">\n'+style+'\n</style>\n</head>')
 # Changing a numeric modifier must refresh the transient preview, not cancel
 # it; the native Apply step remains the only document mutation.
 html=one(html,
  """const amountChanged=()=>{const api=se430BeginnerAPI();if(api?.inspect().preview.active){api.cancel('Amount changed. Preview again to review the new geometry before Apply.');se430BeginnerRefresh();}};""",
  """const amountChanged=()=>{
  const api=se430BeginnerAPI(),state=api?.inspect?.();
  const control=native.querySelector('#modelAtelierWorkshopAmount');
  const config=se430BeginnerAmount(operation.value),amount=Number(control?.value);
  if(state?.preview.active&&state.preview.operation===operation.value&&config&&Number.isFinite(amount)&&amount>=config.min&&amount<=config.max){
   se430BeginnerResult(api.preview(operation.value,{amount}));
  }
  window.SWYRL_ENGINE_GUIDED_FACE_451?.refresh?.();
 };""")
 # The secondary advanced operation list is opt-in, rather than being an
 # always-visible duplicated ladder of Run buttons and hidden native fields.
 html=one(html,
  """if(operation==='more'){
   window.SWYRL_E_UNIFIED_TOOLS?.select?.('Topology','Manual mesh modeling');""",
  """if(operation==='more'){
   window.SWYRL_E_UNIFIED_TOOLS?.select?.('Topology','Manual mesh modeling');
   window.se451GuidedShowAdvanced?.();""")
 html=one(html,'Face mode: tap the top, then Select flat region.',
  'Face mode: tap the top square; connected coplanar triangles select as one region.')
 html=one(html,'Inset about 0.2. Preview, inspect, then Apply. Keep the new inner faces selected.',
  'Select Inset, drag the live amount slider, then Apply. Keep the inner region selected.')
 html=one(html,'Choose Extrude without reselecting the flat region. Push the retained inner faces inward (for example −0.35). Keep a floor; preview and Apply.',
  'Choose Extrude on the retained inner face, adjust the signed depth to push inward (for example −0.35), then Apply.')
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_450_CAMERA_INSET_PREVIEW',MARKER),
  ('ENGINE · MAKER v11.450','ENGINE · MAKER v11.451'),
  ('v11.450 · stable dock zoom and visible Inset preview','v11.451 · guided face tools and live modifiers'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.450'","window.SWRLZ_FORGE_BUILD={version:'v11.451'"),
  ('<title>§wyrl§ Engine · Maker v11.450</title>','<title>§wyrl§ Engine · Maker v11.451</title>')
 ]:html=one(html,before,after)
 old=" source.engine='§wyrl§ Engine · Maker v11.450';source.version=11.450;"
 assert html.count(old)==5,('v11.451 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.451';source.version=11.451;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.450']
 notes['history'].insert(0,{'version':'v11.450','changes':notes.get('changes',[])})
 notes.update(version='v11.451',date='2026-11-14',
  title='Guided Face workflow with live Inset and Extrude modifiers',
  changes=[
   'Face modeling now shows a compact progressive inspector: original Inset, Extrude, Solidify and All face tools actions plus one contextual modifier row and Apply/Cancel, without the redundant advanced workshop Run button stack.',
   'Advanced tools remains one tap away, exposing the original native topology controls and preserving edge, vertex, selection, UV, rigging and VR tools.',
   'Amount slider and exact value update the same validated transient native preview on a frame-coalesced basis. Changing the original advanced numeric input also rebuilds its preview instead of cancelling it.',
   'One selected square is still represented by connected coplanar triangles. No separate geometry, history or persistence layer is introduced: Apply commits one Undo checkpoint and Cancel discards the candidate.',
   'The model camera, original touch gestures, resize grips, native create/convert safeguards and VR world-space interaction remain unchanged.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
