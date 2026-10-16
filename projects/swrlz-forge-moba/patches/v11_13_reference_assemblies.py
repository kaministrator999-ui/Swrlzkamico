"""Native reference sculpt and reversible independently animated piñata assemblies."""
from pathlib import Path
import json,re

def once(s,a,b):
 n=s.count(a)
 assert n==1,(a[:100],n)
 return s.replace(a,b,1)

def apply(html):
 r=Path(__file__).resolve().parent.parent
 scene=json.loads((r/'scenes/model-atelier-festival-reference-v11-13.swyrl.json').read_text())
 enc=json.dumps(scene,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 # Preserve the exact v11.12 generated default as a loadable legacy fixture.
 pat=r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)'
 match=re.search(pat,html,re.S);assert match
 html=html[:match.start()]+'const MODEL_ATELIER_LEGACY_V1112='+match.group(1)+';\nconst MODEL_ATELIER_CANONICAL_PROJECT='+enc+';\n'+html[match.end():]
 code=(r/'runtime/model_atelier_reference_v11_13.js').read_text()
 html=once(html,'  function refreshList(){',code+'\n  function refreshList(){')
 html=once(html,'  function geometry(part){','  function geometry(part){\n    const reference=atelierReferenceGeometry(part);if(reference)return reference;')
 html=once(html,'n<.025||n>5','n<.001||n>5')
 html=once(html,'    const h=Math.cos(orbit.pitch);','    const h=Math.cos(orbit.pitch),focusY=model()?.assemblies?2.8:2.35;')
 html=once(html,'2.45+orbit.distance*Math.sin(orbit.pitch)','focusY+.1+orbit.distance*Math.sin(orbit.pitch)')
 html=once(html,'camera.lookAt(0,2.35,0);','camera.lookAt(0,focusY,0);')
 html=once(html,'orbit={yaw,pitch,distance};cameraUpdate();','orbit={yaw,pitch:model()?.assemblies ? .08 : pitch,distance:model()?.assemblies?Math.max(11.2,distance,6.1/(2*Math.tan(camera.fov*Math.PI/360)*camera.aspect)):distance};cameraUpdate();')
 html=once(html,'ensurePanel();if(!panel.hidden)return true;','ensurePanel();if(!panel.hidden)return true;\n    if(model()?.assemblies)orbit={yaw:.18,pitch:.08,distance:11.2};')
 html=once(html,"left:['model-0020'", "left:['sock-left','shoe-left','heel-left','sole-left','bow-left--1','bow-left-1','sock-fold-left-0','sock-fold-left-1','sock-fold-left-2','sock-fold-left-3','model-0020'")
 html=once(html,"right:['model-0037'", "right:['sock-right','shoe-right','heel-right','sole-right','bow-right--1','bow-right-1','sock-fold-right-0','sock-fold-right-1','sock-fold-right-2','sock-fold-right-3','model-0037'")
 html=once(html,'renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();','renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();\n    if(model()?.assemblies){orbit.distance=Math.max(orbit.distance,6.1/(2*Math.tan(camera.fov*Math.PI/360)*camera.aspect));cameraUpdate();}')
 html=once(html,"orbit={yaw:0,pitch:.08,distance:8.2};cameraUpdate();","orbit={yaw:0,pitch:.08,distance:model()?.assemblies?Math.max(11.2,6.1/(2*Math.tan(camera.fov*Math.PI/360)*camera.aspect)):8.2};cameraUpdate();")
 html=once(html,'function atelierSetPoseCamera(view){','function atelierSetPoseCamera(view){\n  if(!camera)return false;')
 html=once(html,'orbit.distance=window.innerWidth<=700?10.2:8.2;cameraUpdate();','orbit.distance=model()?.assemblies?11.2:(window.innerWidth<=700?10.2:8.2);cameraUpdate();')
 # Smaller detail primitives retain silhouette without burning a full sphere per highlight.
 html=once(html,'default:return new THREE.SphereGeometry(1,30,22);',"default:return new THREE.SphereGeometry(1,model()?.assemblies?16:30,model()?.assemblies?10:22);")
 html=once(html,'    const current=partById(selection);','    atelierBindAssemblyMeshes();\n    const current=partById(selection);')
 html=once(html,'    renderer.render(world,camera);raf=requestAnimationFrame(loop);','    atelierAssemblyTick(performance.now());\n    renderer.render(world,camera);raf=requestAnimationFrame(loop);')
 html=once(html,'    panel.hidden=true;cancelAnimationFrame(raf);','    atelierAssemblyPlaying=false;atelierAssemblyRestart=true;atelierAssemblyMeshes.clear();\n    panel.hidden=true;cancelAnimationFrame(raf);')
 html=once(html,'function modelSnapshot(){return JSON.stringify(model().parts);}','function modelSnapshot(){return JSON.stringify(model());}')
 html=once(html,'dst.push(modelSnapshot());model().parts=JSON.parse(src.pop());selection=null;signalEdited();','dst.push(modelSnapshot());currentProject.modelAtelier=JSON.parse(src.pop());selection=null;signalEdited();atelierAssemblyRefresh();')
 html=once(html,'    atelierPoseDeckInstall();','    atelierPoseDeckInstall();atelierAssemblyInstall();')
 html=once(html,'    resize();renderParts();refreshList();refreshInspector();atelierRefreshPoseChoices();loop();','    resize();renderParts();refreshList();refreshInspector();atelierRefreshPoseChoices();atelierAssemblyRefresh();loop();')
 html=once(html,"      const frames=atelierValidatedFrameStore(source);", "      const assemblies=atelierValidateAssemblies(source.assemblies,source.parts);\n      const frames=atelierValidatedFrameStore(source);")
 html=once(html,'      model().poseFrames=frames.poseFrames;model().poseNeutral=frames.poseNeutral;', '      model().poseFrames=frames.poseFrames;model().poseNeutral=frames.poseNeutral;\n      if(assemblies)model().assemblies=assemblies;else delete model().assemblies;atelierAssemblyPlaying=false;')
 html=once(html,"selection=null;signalEdited();atelierRefreshPoseChoices();status('Validated model and saved frames imported. You can undo the part import.');", "selection=null;signalEdited();atelierRefreshPoseChoices();atelierAssemblyRefresh();status('Validated model, poses and independent attachments imported. Undo restores all model data.');")
 # Keep native loading/import strict before any current-project mutation.
 html=once(html,'  const result=modelAtelierPreviousLoad(...args);',"  if(args[0]?.project?.modelAtelier?.assemblies)atelierValidateAssembliesPublic(args[0].project.modelAtelier);\n  const result=modelAtelierPreviousLoad(...args);")
 html=once(html,'ModelAtelier.install();',"function atelierValidateAssembliesPublic(m){return ModelAtelier.validateAssemblies(m);}\nModelAtelier.install();")
 html=once(html,'return Object.freeze({open,close,install,syncProject,status:', "return Object.freeze({validateAssemblies:m=>{if(!validParts(m.parts))throw Error('Invalid editable model parts.');return atelierValidateAssemblies(m.assemblies,m.parts);},assemblyStatus:atelierAssemblyStatus,view:atelierSetPoseCamera,metrics:atelierGeometryStats,open,close,install,syncProject,status:")
 html=once(html,"status:()=>ModelAtelier.status()});", "status:()=>ModelAtelier.status(),assemblies:()=>ModelAtelier.assemblyStatus(),metrics:()=>ModelAtelier.metrics(),view:name=>ModelAtelier.view(name),loadLegacy:()=>{ModelAtelier.close();loadProject(structuredClone(MODEL_ATELIER_LEGACY_V1112),{workspaceLocal:true});ModelAtelier.open();}});")
 deck='''<details id="modelAtelierAssemblyDeck" class="atelier-assembly-deck"><summary>Living models · sockets & motion</summary><div class="atelier-assembly-controls">
 <label>Independent model<select id="modelAtelierAssemblyComponent"></select></label><div class="atelier-pair"><button id="modelAtelierAssemblyAttach">Snap to pigtail</button><button id="modelAtelierAssemblyDetach">Detach · keep pose</button></div>
 <label>Transformation <span id="modelAtelierAssemblyTimeLabel">4.00 s</span><input id="modelAtelierAssemblyTime" type="range" min="0" max="6" step=".01" value="4"></label>
 <div class="atelier-pair"><button id="modelAtelierAssemblyPlay">▶ Play transform</button><button id="modelAtelierAssemblyStop">Stop / rest</button></div>
 <div class="atelier-pair"><label>Paper flex<input id="modelAtelierAssemblyAmplitude" type="number" min="0" max=".3" step=".01"></label><label>Motion speed<input id="modelAtelierAssemblySpeed" type="number" min=".1" max="4" step=".1"></label></div>
 <details><summary>Model transform keys</summary><div class="atelier-assembly-controls"><span id="modelAtelierAssemblyKeyCount"></span><label>Offset X / Y / Z</label><div class="atelier-key-xyz"><input id="modelAtelierAssemblyoffset0" type="number" step=".05" aria-label="Model offset X"><input id="modelAtelierAssemblyoffset1" type="number" step=".05" aria-label="Model offset Y"><input id="modelAtelierAssemblyoffset2" type="number" step=".05" aria-label="Model offset Z"></div><label>Rotation X / Y / Z · radians</label><div class="atelier-key-xyz"><input id="modelAtelierAssemblyrotation0" type="number" step=".05" aria-label="Model rotation X"><input id="modelAtelierAssemblyrotation1" type="number" step=".05" aria-label="Model rotation Y"><input id="modelAtelierAssemblyrotation2" type="number" step=".05" aria-label="Model rotation Z"></div><label>Scale<input id="modelAtelierAssemblyScale" type="number" step=".05" min=".1" max="3"></label><button id="modelAtelierAssemblySaveKey">Save key at playhead</button><button id="modelAtelierAssemblyClearKeys">Clear this model’s keys</button></div></details>
 <button id="modelAtelierAssemblyMotionApply">Apply independent motion</button><button id="modelAtelierAssemblyExport">Export this model</button><small>Separate native models; socket transforms and procedural paper flex. Save model JSON to retain controls.</small></div></details>'''
 html=once(html,'<aside class="atelier-inspector"><h3>', '<aside class="atelier-inspector">'+''.join(deck.splitlines())+'<h3>')
 html=once(html,'Original modeled study, not an extracted or exact game asset. Model parts are editable; vertex sculpting, UV painting, skinning and animation remain future tools.', 'Native editable reference sculpt. Separate socketed models and paper motion are available. Skeletal weight painting and texture painting are not part of this editor.')
 html=once(html,'v11.12 · grounded anatomical pose studio','v11.13 · reference sculpt & living piñatas')
 html=html.replace('Maker v11.12','Maker v11.13').replace('MAKER v11.12','MAKER v11.13').replace("version:'v11.12'","version:'v11.13'").replace('version:11.12','version:11.13')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_12_GROUNDED_STANCE_POSES','SWYRL_ENGINE_DEPLOY_MARKER: V11_13_REFERENCE_ASSEMBLIES')
 style=(r/'runtime/model_atelier_reference_v11_13.css').read_text()
 html=once(html,'/* v11.8 procedural sculpt tools:',style+'\n/* v11.8 procedural sculpt tools:')
 return html
