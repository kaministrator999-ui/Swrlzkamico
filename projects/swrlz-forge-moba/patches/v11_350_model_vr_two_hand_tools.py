"""§E v11.350 — two-hand Model VR, live profiles and native surface tools."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_350_MODEL_VR_TWO_HAND_TOOLS'
def one(src,old,new):
    assert src.count(old)==1,('v11.350 anchor',old[:100],src.count(old))
    return src.replace(old,new,1)
def apply(html):
    for name in ['model_vr_native_tools_v11_350.js','model_vr_sculpt_draw_v11_350.js']:
        html=one(html,'/* ATELIER_BRIDGE_END */',(ROOT/'runtime'/name).read_text('utf8')+'\n/* ATELIER_BRIDGE_END */')
    html=one(html,'return Object.freeze({xrBridge:se340ModelBridge,chatAction:',
             'return Object.freeze({xrBridge:se340ModelBridge,vrTools:se350ModelTools,vrSurface:se350ModelSurface,chatAction:')
    a=html.index('/* SE340_MODEL_VR_WORKSPACE_START */');b=html.index('/* SE340_MODEL_VR_WORKSPACE_END */',a)+len('/* SE340_MODEL_VR_WORKSPACE_END */')
    assert 'SE344_MODEL_VR_AIM_VIEWS_START' in html[a:b] and 'SE345_MODEL_VR_DISPLAY_MODES_START' in html[a:b]
    html=html[:a]+(ROOT/'runtime/model_vr_workspace_v11_350.js').read_text('utf8').rstrip()+html[b:]
    html=one(html,(ROOT/'runtime/model_studio_vr_ui_v11_345.js').read_text('utf8'),(ROOT/'runtime/model_studio_vr_ui_v11_350.js').read_text('utf8'))
    # Live dispatcher shares Controller Studio's validated profile, without a second XR loop.
    anchor='// §E v11.179 — VR Controller Studio foundation, no pretend immersive editor.'
    html=one(html,anchor,(ROOT/'runtime/model_vr_input_profile_v11_350.js').read_text('utf8')+'\n'+anchor)
    a=html.index('const BASE={',html.index(anchor));b=html.index('const PARAMS=',a)
    base=html[a:b];start=base.index('model:[');end=base.index('play:[',start)
    base=base[:start]+"model:SE350_MODEL_VR_BINDINGS.model.map(row=>row.slice()),\nsculpt:SE350_MODEL_VR_BINDINGS.sculpt.map(row=>row.slice()),\n"+base[end:]
    html=html[:a]+base+html[b:]
    html=one(html,"const ACTIONS=new Set(['open-settings'","const ACTIONS=new Set(['tool-wheel','category-wheel','open-settings'")
    html=one(html,'schema:SCHEMA,open,close,read:',
        "schema:SCHEMA,open,close,currentProfile:()=>Object.fromEntries(['schema','profileId','profileName','profileVersion','createdAt','modifiedAt','dominantHand','thresholds','bindings'].map(k=>[k,clone(state[k])])),read:")
    html=one(html,'immersiveCommandsActive:false}),',"immersiveCommandsActive:!!window.SWYRL_ENGINE_MODEL_VR?.inspect?.().active}),")
    html=one(html,'liveNativeDispatch:false}),',"liveNativeDispatch:!!window.SWYRL_ENGINE_MODEL_VR?.inspect?.().active,dispatchWorkspace:'modeler'}),")
    # Model capabilities accurately describe the active native surface adapter.
    html=one(html,"modelAtelierXR:true,sculptXR:false,locomotionXR:false", "modelAtelierXR:true,sculptXR:true,locomotionXR:false")
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_346_MODEL_MULTI_UV_SHEETS',MARKER),
        ('ENGINE · MAKER v11.346','ENGINE · MAKER v11.350'),
        ('v11.346 · complete multi-sheet UV export for complex characters','v11.350 · two-hand VR modeling, live profiles, sculpt and draw'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.346'","window.SWRLZ_FORGE_BUILD={version:'v11.350'"),
        ('<title>§wyrl§ Engine · Maker v11.346</title>','<title>§wyrl§ Engine · Maker v11.350</title>')]:html=one(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.346';source.version=11.346;"
    assert html.count(old)==3
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.350';source.version=11.350;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,size=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.346' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.346','changes':notes.get('changes',[])})
    notes.update(version='v11.350',date='2026-11-08',title='Two-hand VR modeling and native creation',changes=[
        'Right-hand editing and left-hand view controls use the real Controller Studio profile. Hold A for tools, hold X for categories, X+Y for Redo, stick clicks for focus and precision, and left grip plus right stick for zoom.',
        'Add or remove parts with the left trigger. Native multi-part and explicitly armed two-hand transforms preview together and commit one Undo step; Inspect gestures change only presentation. Cancel and tracking loss discard previews.',
        'Sculpt in VR with Push, Smooth, Flatten, Inflate, Pinch and Translate using native sparse edits. Trace planar outlines with a trigger and grip-extrude the resulting native mesh into a closed solid. Lasso surface regions save native masks that constrain subsequent sculpt strokes.',
        'Readable spatial tool pages, brush footprint, outline preview and selection bounds show what is active. Camera presets, calibrated rays, display modes and whole-character UV sheets remain available.',
        'Portable native geometry and edit budgets are enforced. Posed skins and refined geometry require a safe source correspondence before sculpting; unsupported operations show a reason instead of saving incorrect edits.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+size:]
