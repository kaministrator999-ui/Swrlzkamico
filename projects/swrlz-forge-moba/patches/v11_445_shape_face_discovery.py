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
    # Replace only the generated v11.443 presentation wrapper. Keep the
    # historical patch/runtime unchanged and preserve native XR controllers,
    # world-space menu gripping, gizmo priority and native UI details.
    a=html.index('/* SE443_MODEL_VR_VERTICAL_DOCK_START */')
    b=html.index('/* SE443_MODEL_VR_VERTICAL_DOCK_END */',a)+len('/* SE443_MODEL_VR_VERTICAL_DOCK_END */')
    current=html[a:b]
    assert 'SWYRL_ENGINE_MODEL_VR_DOCK_443' in current
    assert 'se374GizmoContact(record)' in current
    progressive=(ROOT/'runtime/model_vr_three_stage_v11_445.js').read_text(encoding='utf8')
    assert progressive.startswith('/* SE443_MODEL_VR_VERTICAL_DOCK_START */')
    assert progressive.rstrip().endswith('/* SE443_MODEL_VR_VERTICAL_DOCK_END */')
    html=html[:a]+progressive+html[b:]
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
    assert '</head>' in html
    html=html.replace('</head>','<style id="se445ShapeDiscoveryStyles">\n'+css+'\n</style>\n</head>',1)
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
    notes.update(version='v11.445',date='2026-11-14',title='Three-stage right-side VR modeling tools',
      changes=[
      'The main VR tools become a permanent vertical rail on the far right. Selecting Sculpt, Face tools, Create or another category slides a smaller operation list out to its left; the former large console stays hidden until a specific operation is selected.',
      'Choosing Inset, Extrude, Solidify, Subdivide or another operation opens the existing native modifier/preview controls in a third panel to the left. Each tier can be closed without hiding the primary tools, and each remains part of one grabbable world-space menu.',
      'Sculpt operations include the six original brushes and direct face-modeling shortcuts. Face tools expose conversion, flat region picking and the supported topology actions. Existing gestures, selection, native Apply/Cancel, Undo/Redo, account Save and gizmo-first selection remain unchanged.',
      'Phone and desktop place a compact Shape / Face tools group in the existing selection inspector: Inset, Extrude, Solidify and All face tools. Shortcut selection opens the native manual workshop rather than an independent geometry editor.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
