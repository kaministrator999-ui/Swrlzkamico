"""§E v11.360 — readable spatial menus and bounded VR interaction motion."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_360_MODEL_VR_SPATIAL_MENUS'
def one(html,old,new):
    assert html.count(old)==1,('v11.360 anchor',old[:100],html.count(old))
    return html.replace(old,new,1)
def apply(html):
    html=one(html,(ROOT/'runtime/model_studio_vr_ui_v11_350.js').read_text('utf8'),
             (ROOT/'runtime/model_studio_vr_ui_v11_360.js').read_text('utf8'))
    helper=(ROOT/'runtime/model_vr_menu_motion_v11_360.js').read_text('utf8')
    html=one(html,'function se340Poll(record,frame,dt){',helper+'\nfunction se340Poll(record,frame,dt){')
    html=one(html,'se350UpdateBrush();se350UpdateLassoGuide();se340SyncUI();renderer.render(s.scene,s.camera);',
             'se350UpdateBrush();se350UpdateLassoGuide();se340SyncUI();se360AdvanceMenu(dt);renderer.render(s.scene,s.camera);')
    html=one(html,'lastAction:se340XR.lastAction,error:se340XR.error,',
             'lastAction:se340XR.lastAction,error:se340XR.error,menu:se340XR.ui?.inspect?.()||null,')
    html=one(html,'result.paletteActions=(se340XR.ui?.targets||[]).filter(',
             'result.paletteActions=(se340XR.ui?.root.visible?se340XR.ui.targets:[]).filter(')
    html=one(html,'addScaledVector(forward,1.0).addScaledVector(right,-.47);',
             'addScaledVector(forward,1.02).addScaledVector(right,-.56);')
    html=one(html,'viewer.position.y-.08,.85,1.65','viewer.position.y-.06,.85,1.65')
    html=one(html,"const cancelled=se340CancelGesture();if(!cancelled)s.mode='inspect';",
             "const cancelled=se340CancelGesture();s.helpVisible=false;if(!cancelled){s.mode='inspect';s.page='tools';}")
    html=one(html,"se340Notice('Right trigger selects · Left trigger adds · Left grip moves view · Hold A for tools.');",
             "se340Notice('Ready · Right trigger selects · Left trigger adds.');")
    # Pointer feedback for menus remains responsive at headset frame cadence;
    # the existing reduced model-surface picking remains bounded to ~18Hz.
    html=one(html,'const now=performance.now();\n   if(now>=record.nextHoverAt){',
      '''const now=performance.now(),menuHit=se360MenuContact(record);
   if(menuHit){
    const key=menuHit.action;
    if(key&&key!==record.hoverKey)se340Pulse(record,.08,12);
    record.hoverKey=key;record.hit=menuHit;record.nextHoverAt=now+55;
   }else if(record.hit?.ui){record.hit=null;record.nextHoverAt=0;record.hoverKey=null;}
   if(!menuHit&&now>=record.nextHoverAt){''')
    html=one(html,'record.ray.material.color.setHex(hit?.ui?0xe1bbff:hit?.id?0x80f0c4:0xbda0ff);',
      '''record.ray.material.color.setHex(hit?.ui?0x98f2dc:hit?.id?0x80f0c4:0xbda0ff);
   record.ray.material.opacity=hit?.ui ? .85 : .62;
   record.dot.scale.setScalar(hit?.ui?1.2:1);
   record.dot.material.color.setHex(hit?.ui?0xb9ffe8:0xc9afff);''')
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_358_WEBXR_HAND_STARTERS',MARKER),
        ('ENGINE · MAKER v11.358','ENGINE · MAKER v11.360'),
        ('v11.358 · WebXR left and right hand reference starters','v11.360 · spatial menus, tactile buttons and smooth VR feedback'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.358'","window.SWRLZ_FORGE_BUILD={version:'v11.360'"),
        ('<title>§wyrl§ Engine · Maker v11.358</title>','<title>§wyrl§ Engine · Maker v11.360</title>')]:html=one(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.358';source.version=11.358;"
    assert html.count(old)==4,('v11.360 native provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.360';source.version=11.360;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,size=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.358' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.358','changes':notes.get('changes',[])})
    notes.update(version='v11.360',date='2026-11-09',title='Spatial menus with clear states and tactile feedback',changes=[
        'Model VR menus gain a larger readable spatial console, persistent studio navigation, clear line icons, descriptive tool cards and more distinct enabled, disabled and selected states.',
        'Subtle hover lift, press depth, selection accents, panel reveals and page transitions run in the existing headset frame loop. Motion respects reduced-motion preferences; hidden menus stop animating and idle frames do not repaint canvas textures.',
        'Tool, sculpt-brush and studio wheels retain controller hold-and-release selection. Opaque menu plates block geometry behind buttons and gaps while visual feedback responds at headset frame cadence.',
        'The native editing, camera orbit, selected-only grip behavior, custom controller profiles, saved lasso/sculpt history and wireframe-first UV painting remain unchanged.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+size:]
