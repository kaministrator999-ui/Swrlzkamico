"""§E v11.430 — visual instruction and native manual mesh modeling."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_430_MODEL_STUDIO_VISUAL_WORKSHOP'
def one(src,old,new):
    assert src.count(old)==1,('v11.430 anchor',old[:110],src.count(old))
    return src.replace(old,new,1)
def runtime(name):return (ROOT/'runtime'/name).read_text('utf8')
def apply(html):
    shared='\n'.join(runtime(n) for n in ['model_studio_teaching_v11_430.js','model_mesh_operations_v11_430.js','model_studio_beginner_ui_v11_430.js'])
    html=one(html,'const ModelAtelier=(()=>{',shared+'\nconst ModelAtelier=(()=>{')
    native='\n'.join(runtime(n) for n in ['model_studio_workshop_bridge_v11_430.js','model_studio_camera_v11_430.js'])
    html=one(html,'/* ATELIER_BRIDGE_END */',native+'\n/* ATELIER_BRIDGE_END */')
    html=one(html,'vrAccessory:se410ModelAccessory,chatAction:',
             'vrAccessory:se410ModelAccessory,workshop:se430ModelWorkshop,camera:se430ModelCamera,chatAction:')
    html=one(html,'window.SWYRL_ENGINE_MODEL_VR=Object.freeze',
             'window.SWYRL_ENGINE_MODEL_WORKSHOP=ModelAtelier.workshop;\nwindow.SWYRL_ENGINE_MODEL_CAMERA=ModelAtelier.camera;\nwindow.SWYRL_ENGINE_MODEL_VR=Object.freeze')
    html=one(html,"if(mode==='vertex'){\n   const key=topology.keys[id];",
             "if(mode==='vertex'){\n   const representative=topology.vertices[id],key=topology.keys[representative];")
    html=one(html,'function atelierComponentRefresh(){',
             'function atelierComponentRefresh(){\n if(se340ModelBridge.isBorrowed()){atelierComponentUIRefresh();return;}')
    a=html.index('function atelierComponentModeSet(next){');b=html.index('function atelierComponentUIRefresh(){',a)
    assert '(!se340ModelBridge.isBorrowed()&&renderer.render(world,camera))' in html[a:b]
    html=one(html,'orbit.pitch=Math.max(-.85,Math.min(1.1,pressed.pitch+dy*.006));',
             'orbit.pitch=THREE.MathUtils.clamp(pressed.pitch+dy*.006,-Math.PI/2+.001,Math.PI/2-.001);')
    html=one(html,'atelierRefreshPoseChoices();atelierAssemblyRefresh();loop();',
             'atelierRefreshPoseChoices();atelierAssemblyRefresh();se430ModelCamera.install();loop();')
    html=one(html,'    atelierAssemblyTick(performance.now());',
             '    atelierAssemblyTick(performance.now());se430BeginnerTick(performance.now());')
    html=one(html,' seAtelierTopMenuExclusivity(panel);\n}',
             " seAtelierTopMenuExclusivity(panel);\n se430BeginnerInstall(panel);\n window.SWYRL_E_UNIFIED_TOOLS?.select?.('Meshes','Select & organize');\n}")
    html=one(html,"['Select & organize',['Parts','Add','Duplicate','Delete','Undo','Redo']],",
             "['Select & organize',['Parts','PrimitiveKind','Add','Duplicate','Delete','Undo','Redo']],\n   ['Assemblies & selection',['GroupMulti','GroupAll','GroupClear','GroupScope','GroupPicker','GroupCreate','GroupUngroup','GroupUpdate','GroupRemove']],")
    html=one(html,'  Topology:[\n',"  Topology:[\n   ['Manual mesh modeling',['WorkshopOperation','WorkshopAmount','WorkshopConvert','WorkshopSelectRegion','WorkshopPreview','WorkshopApply','WorkshopCancel']],\n")
    html=one(html,"const row=document.createElement('div');row.className='atelier-context-field';",
             "const row=document.createElement('div');row.className='atelier-context-field';row.dataset.se430Native=native.id;")
    html=one(html,"group: 'VR created geometry'","group: 'Created geometry'")
    html=one(html,'level.data.project.instanceId=newId;\n    level.data.project.projectName=newName;',
             'level.data.project.instanceId=newId;\n    level.data.project.se371TemplateSource=false;\n    level.data.project.sourceStarterId=clone.project.sourceStarterId;\n    level.data.project.projectName=newName;')
    html=one(html,'se175StampProject(newId,newName,clone.project.sourceStarterId);\n  workspaceLocalAllowed=true;',
             'se175StampProject(newId,newName,clone.project.sourceStarterId);\n  currentProject.se371TemplateSource=false;\n  workspaceLocalAllowed=true;')
    html=one(html,'In flat Model Studio, Add sphere makes a sphere. Select that part, then use Shape → box. In VR, Create → Cube places a box directly.',
             'In flat Model Studio, choose Cube in the primitive picker, then Add cube. The Shape field remains available for supported primitives. In VR, Create → Cube previews a cube.')
    a=html.index('/* SE360_MODEL_VR_UI_START */');b=html.index('/* SE360_MODEL_VR_UI_END */',a)+len('/* SE360_MODEL_VR_UI_END */')
    html=html[:a]+runtime('model_studio_vr_ui_v11_430.js').rstrip()+html[b:]
    html=one(html,'/* SE410_MODEL_VR_ACCESSORY_WORKSHOP_END */',
             '/* SE410_MODEL_VR_ACCESSORY_WORKSHOP_END */\n'+runtime('model_vr_manual_workshop_v11_430.js'))
    hint="""const se430PreviousHint=se362CleanLabel;
se362CleanLabel=function(action,s){
 if(s.se430Manual){
  if(action==='select')return 'Select flat region';
  if(action==='multiselect'||action==='grab'||action==='fine')return '';
  if(action==='preview')return 'Preview geometry';
  if(action==='cancel')return 'Cancel preview / Inspect';
  if(action==='undo'&&ModelAtelier.workshop.inspect().preview.active)return 'Cancel mesh preview';
 }
 return se430PreviousHint(action,s);
};
"""
    html=one(html,'function se340ModelXRActive(){',hint+'\nfunction se340ModelXRActive(){')
    html=one(html,'...se410AccessoryUI(),creationActive:',
             '...se410AccessoryUI(),...se430VRUI(),creationActive:')
    html=one(html,'se410AccessoryFrame(s,dt);se350Dispatch(sample);se350Navigate(sample,dt);',
             'se410AccessoryFrame(s,dt);se430ManualFrame(s);se350Dispatch(sample);se350Navigate(sample,dt);')
    html=one(html,'point:hit.point,face:hit.face,normal:hit.normal});',
             'point:hit.point,face:hit.face,faceIndex:hit.faceIndex,normal:hit.normal});')
    styles='\n'.join(runtime(n) for n in ['model_studio_beginner_ui_v11_430.css','model_studio_camera_v11_430.css'])
    html=html.replace('</head>','<style id="se430ModelStudioStyles">\n'+styles+'\n</style>\n</head>',1)
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_425_LEVEL_OBSERVER_FEEDBACK_GUARD',MARKER),
        ('ENGINE · MAKER v11.425','ENGINE · MAKER v11.430'),
        ('v11.425 · stop level toolbar observer startup feedback','v11.430 · learn and build with real mesh tools'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.425'","window.SWRLZ_FORGE_BUILD={version:'v11.430'"),
        ('<title>§wyrl§ Engine · Maker v11.425</title>','<title>§wyrl§ Engine · Maker v11.430</title>')]:html=one(html,before,after)
    prior=" source.engine='§wyrl§ Engine · Maker v11.425';source.version=11.425;"
    assert html.count(prior)==5,('v11.430 provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.430';source.version=11.430;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,length=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.425' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.425','changes':notes.get('changes',[])})
    notes.update(version='v11.430',date='2026-11-12',title='A visual workshop for learning real manual modeling',changes=[
        'Optional collapsible tool lessons share semantic icons and generated Before/During/After diagrams across the existing inspector and world-space VR console. Requirements, availability reasons and practical examples stay connected to native commands; incomplete advanced operations are identified honestly.',
        'Direct primitive choice, visible component modes and persistent assembly controls improve discovery. A UV-seam vertex selection mapping defect is fixed. Existing advanced sculpt, UV, rig, animation, reference, save and export controls remain available.',
        'Plain primitives can explicitly convert to editable native topology with regenerated UVs. Connected planar-region inset and signed extrusion, selected face deletion and bounded planar Solidify use real validated geometry, source-safe previews and one native Undo transaction. Existing split/refine/fill/winding operations share the contextual workflow.',
        'True orthographic and perspective, exact six-axis views, selection-group/all framing and a compact orientation control reuse the existing native camera. Touch pan/zoom, clipping, reference alignment and the headset perspective camera remain supported.',
        'General bevel, weld/merge, loop bridging/cutting, unrestricted mirror and several advanced constraints remain incomplete. This first implementation teaches a manual cube-to-container workflow without an accessory generator or parallel editor.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+length:]
