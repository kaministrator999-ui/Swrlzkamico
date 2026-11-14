"""§E v11.445: discoverable Sculpt/Face tools, native behavior unchanged."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_445_SHAPE_FACE_DISCOVERY'
def once(s,old,new):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.445 anchor',old[:130],n))
    return s.replace(old,new,1)

def apply(html):
    # Clear, direct VR access; leave brush controls, their order, and all
    # underlying manual face transactions under native ownership.
    html=once(html,"['manual-mesh','Mesh edit','manual-mesh']",
                   "['manual-mesh','Face tools','manual-mesh']")
    html=once(html,"['brush-strength-plus','Strength +'],['studio','Studio'],['exit','Exit VR']",
                   "['brush-strength-plus','Strength +'],['manual-inset','Inset face'],['manual-extrude','Extrude face']")
    html=once(html,"'manual-mesh':['Manual mesh tools','SELECT A REAL FACE REGION']",
                   "'manual-mesh':['Shape / Face tools','INSET · EXTRUDE · SOLIDIFY · SUBDIVIDE']")
    # Keep the existing phone/desktop selection context the sole home for
    # these shortcuts, avoiding an extra dock or independent tool state.
    quick=""" const faceQuick=document.createElement('section');
 faceQuick.id='se445ShapeQuick';faceQuick.setAttribute('aria-label','Shape and face modeling tools');
 faceQuick.innerHTML='<strong class="se445-shape-caption">Shape · Face tools</strong>'+
  '<div class="se445-shape-actions">'+
  '<button type="button" data-se445-op="inset">Inset</button>'+
  '<button type="button" data-se445-op="extrude">Extrude</button>'+
  '<button type="button" data-se445-op="solidify">Solidify</button>'+
  '<button type="button" data-se445-op="more">All face tools</button></div>'+
  '<small class="se445-shape-hint" role="status">Pick a tool, select a face region, then Preview and Apply. Plain primitives need Make mesh editable first.</small>';
 strip.querySelector('#se430ContextTools').after(faceQuick);
 faceQuick.addEventListener('click',event=>{
  const button=event.target.closest('[data-se445-op]');if(!button)return;
  const api=se430BeginnerAPI(),state=api?.inspect(),operation=button.dataset.se445Op;
  const hint=faceQuick.querySelector('.se445-shape-hint');
  if(!state){se430BeginnerWrite(hint,'Open a Model Studio project first.');return;}
  if(state.preview.active){se430BeginnerWrite(hint,'Apply or Cancel the current preview before changing face tools.');return;}
  if(state.selection.objectCount>1){se430BeginnerWrite(hint,'Choose one mesh before editing its faces.');return;}
  if(state.selection.partId&&state.selection.mode!=='face')api.setComponentMode('face');
  if(operation==='more')window.SWYRL_E_UNIFIED_TOOLS?.select?.('Topology','Manual mesh modeling');
  else se430BeginnerNavigate(operation);
  se430BeginnerWrite(hint,(operation==='more'?'All face tools':button.textContent)+' · select a flat region. Convert a plain primitive first, then Preview / Apply.');
  se430BeginnerQueue();
 });
"""
    html=once(html," strip.querySelector('#se430ContextTools').after(deleteSelected);",
                   " strip.querySelector('#se430ContextTools').after(deleteSelected);\n"+quick)
    refresh=""" const faceQuick=p.querySelector('#se445ShapeQuick');
 if(faceQuick){
  const selectedOp=operation.value;
  for(const btn of faceQuick.querySelectorAll('[data-se445-op]')){
   btn.disabled=!!preview.active;
   btn.setAttribute('aria-pressed',String(!preview.active&&selection.mode==='face'&&btn.dataset.se445Op===selectedOp));
   btn.title=preview.active?'Apply or Cancel the current preview first.':btn.dataset.se445Op==='more'?'Open all native face modeling tools.':'Choose '+btn.textContent+' in the native manual modeling workshop.';
  }
 }
"""
    html=once(html," const modes=p.querySelector('#seAtelierModes');if(modes)modes.setAttribute('aria-label',",
                   refresh+" const modes=p.querySelector('#seAtelierModes');if(modes)modes.setAttribute('aria-label',")
    # Adapter is loaded after every native XR patch. Never intercept or
    # reproduce native Inset/Extrude or the Undo stack.
    js=(ROOT/'runtime/model_face_tool_shortcuts_v11_445.js').read_text(encoding='utf8')
    html=once(html,'/* SE444_DELETE_SELECTED_VR_ACTION_END */',
              '/* SE444_DELETE_SELECTED_VR_ACTION_END */\n'+js)
    css=(ROOT/'runtime/model_shape_discovery_v11_445.css').read_text(encoding='utf8')
    html=once(html,'</head>','<style id="se445ShapeDiscoveryStyles">\n'+css+'\n</style>\n</head>')
    for a,b in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_444_DELETE_SELECTED',MARKER),
      ('ENGINE · MAKER v11.444','ENGINE · MAKER v11.445'),
      ('v11.444 · delete selected meshes everywhere','v11.445 · discoverable sculpt and face tools'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.444'","window.SWRLZ_FORGE_BUILD={version:'v11.445'"),
      ('<title>§wyrl§ Engine · Maker v11.444</title>','<title>§wyrl§ Engine · Maker v11.445</title>')
    ]:html=once(html,a,b)
    old=" source.engine='§wyrl§ Engine · Maker v11.444';source.version=11.444;"
    assert html.count(old)==5,('v11.445 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.445';source.version=11.445;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[v for v in notes.get('history',[]) if v.get('version')!='v11.444']
    notes['history'].insert(0,{'version':'v11.444','changes':notes.get('changes',[])})
    notes.update(version='v11.445',date='2026-11-14',title='Discoverable Sculpt and Shape / Face tools',
      changes=[
      'Sculpt in VR now shows direct Inset face and Extrude face cards alongside the six existing brushes and radius/strength controls. Each card enters the native manual face-edit workflow, not an imitation brush.',
      'The permanent VR vertical dock says Face tools rather than the ambiguous Mesh edit, and its right-side page explicitly labels the original Inset, Extrude, Solidify and Subdivide controls.',
      'Phone and desktop place a compact Shape / Face tools group in the existing model selection inspector: Inset, Extrude, Solidify and All face tools. Selecting a shortcut opens the existing native manual workshop and Face mode.',
      'Every face operation still needs a valid selected flat region and, when necessary, explicit primitive conversion; Preview, Apply, Cancel, checkpoints and Undo remain unchanged. No new geometry or project state is created by navigation.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
