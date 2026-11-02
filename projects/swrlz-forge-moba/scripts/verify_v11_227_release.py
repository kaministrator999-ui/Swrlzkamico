#!/usr/bin/env python3
"""Build and verify the exact §E v11.227 Astra wolf skeletal rig and Sheep Tag animation with preceding sheep houses and studios, with routed Game/Modeler pages."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--output',required=True)
p.add_argument('--request',action='store_true',help='Check the separate final deploy request')
args=p.parse_args()
out=Path(args.output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.227'
assert m['finalArtifact']=='swyrl_engine_v11_227.html'
assert len(m['patches'])==259 and m['patches'][-1]=='patches/v11_227_astra_wolf_rig_animations.py'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
s=raw.decode('utf-8')
r=json.loads((out/'SOURCE.json').read_text())
modeler=(out/'modeler.html').read_bytes()
assert modeler==raw, 'Modeler and Game routes must use the same verified native runtime'
assert r['workspacePages']=={'game':'index.html','modeler':'modeler.html'}
assert len(raw)==m['finalBytes']==r['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==r['finalSha256']
assert r['sourceVersion']==m['name'] and r['patches']==m['patches']
assert len(r['assets'])==68
for rel,meta in r['assets'].items():
    data=(out/rel).read_bytes()
    assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],rel
for text in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_227_ASTRA_WOLF_RIG_SHEEP_TAG',
             '<title>§wyrl§ Engine · Maker v11.226</title>',
             "window.SWRLZ_FORGE_BUILD={version:'v11.227'",
             "const PROTOCOL='swrlz-forge-chat-v1'",'seChatAccountPanel','chatAction:seChatAtelierApply',
             'se175ProjectProgress','project.create','se175ActiveProject','se176Install();','se176AccountState(payload);','se177ShowPicture','Continue to Google','se178Install();','se178EnrichContext(value);','host.analyze','Editing now · ','seMobileEditorViewportV11174','seQuestPanelV11168','SWYRL_ENGINE_DEVICE','se-levels-v1','swyrl-workspaces-v1']:
    assert text in s,text
for marker in ['se179VRControlsOpen','se179VRStudio','SWYRL_VR_CONTROLS','swyrl-engine-vr-controls-v1','testInput','immersiveCommandsActive:false']:
    assert marker in s,marker
for marker in ['seChatOutsideDismissV11180','se180InstallDismiss();','function se180Outside(event)','se180-chat-visible','closePanel(false)','se180CancelAnimation','transform:translate3d','se179VRControlsOpen']:
    assert marker in s,marker
for marker in ['seImmersiveXRV11181','se181EnterVR','window.SWYRL_ENGINE_XR=Object.freeze','renderer.setAnimationLoop(tick);',"requestSession('immersive-vr'",'se181XRRender();se192VRFrame();se193XRFrame();renderer.render(scene,camera);','se181XRSelect(record)','se181XRActiveModel()','se181XRMakeExitPanel','SWYRL_ENGINE_XR','se179VRControlsOpen']:
    assert marker in s,marker
for marker in ['se182ProfessionalUI','SWYRL_ENGINE_UI_AUDIT','se183ProjectUI','se184SavedGallery','SWYRL_ENGINE_SAVED_DEFAULT','se184ExtractPreview','se184RenderLocalProjects','se184RenderCloudProjects','se184KickCloudStartup','se185WispBootAtelier','se185InstallAtelierToggle','se185-top-collapsed','data-se186-early','se186StartupBeforeEngine','se186BootRecovery','se187SeparateWorkspaces','se188GameFirstTabs','se189MobilePerformance','se190RenderAudit','se190CountSubmittedFrame','window.SWYRL_ENGINE_XR_RECOVERY','se191XRInstallLanding();','se191XRRenderFrame();','window.SWYRL_ENGINE_VR_EDITOR','se192VRFrame();','se193XRFrame();','se193XRCleanup();','se193XRStart();','window.SWYRL_ENGINE_SHEEP_VR','se192VRCleanup();','se192VRStart();','se192FreezeBillboards();','se191XRMakeBeacon();','se191XRCleanup();','se191XRStartWatchdog(requested);','SWYRL_ENGINE_PERFORMANCE_V11190','se190ComparePresets','const ribBrass=new THREE.InstancedMesh(','se189MobileBoost','se189ResizeIfNeeded','SWYRL_ENGINE_PERFORMANCE_V11189','se187WorkspaceTabs','se187-modeler-page','se187-workspace-tabs','SWYRL_ENGINE_WORKSPACES','V11_227_ASTRA_WOLF_RIG_SHEEP_TAG','se183LevelsToggle','se183StartLoad','se183CloudListCached','SWYRL_ENGINE_PROJECT_LOAD','se179VRControlsOpen','se181EnterVR','seChatOutsideDismissV11180']:
    assert marker in s,marker
assert 'seLevelRawLoadProject(structuredClone(chosen.data)' not in s
assert 'const result=seLevelRawLoadProject(target,...options);' in s
assert s.index('data-se186-early="1"')<s.index('window.SWRLZ_FORGE_BUILD=')
assert s.count('renderer.setAnimationLoop(tick);')==1
for marker in ['window.SWYRL_ENGINE_XR_EDITOR_198', 'se198GrabFrame', 'se198AxisParam', 'se198FlyFrame', 'se198LegendCanvas', 'se198GizmoRayHit', 'se198FinishGrab','se198OldCapture','se198SaveSettings']:
    assert marker in s,marker
for marker in ['window.SWYRL_ENGINE_SHEEP_VISUAL_197','texture.minFilter=THREE.LinearMipmapLinearFilter','function se197MeadowInfo','const se197CameraPrevious=stUpdateCamera;','multiplayerFogOverwritePrevented','stWildwoodGroundTexture.minFilter=THREE.LinearMipmapLinearFilter','se197QuestDownsampled']:
    assert marker in s,marker
for marker in ['window.SWYRL_ENGINE_SHEEP_VR_THUMBSTICK_199','se199StickIntent','se199Drive','se199.defaultZoom','se195FollowCamera=function']:
    assert marker in s,marker
for marker in ['window.SWYRL_ENGINE_SHEEP_VR_SPOTLIGHT_200','se200CameraAnchor','se200MoveUnit','se200.referenceWrites','se200.anchorReady']:
    assert marker in s,marker
for marker in ['window.SWYRL_ENGINE_SHEEP_WARCRAFT_FOOTPRINTS_201','st201Foundation','st201GapState','st201PreviewUpdate','st201CollectGaps','st201Geometry','stClarityUpdateOverlay=function']:
    assert marker in s,marker
for marker in ['window.SWYRL_ENGINE_SHEEP_VR_FOLLOW_INPUT_202','se202ObstacleSnapshot','se202PreviewOwner','se202VisibleBuildings','se202ShouldRefreshPreview','se202FoundationFrame']:
    assert marker in s,marker
# The v11.207 XR-only ground select body must not emit click-to-move.
selection=s.split('function se193XRGameSelect(record){',1)[1].split('function se193XRSnapFollow(){',1)[0]
assert "stUiCommand('move'" not in selection,'Quest trigger still emits click-to-move'
for marker in ["stUiCommand('build'","stUiCommand('attack'","stUiCommand('rescue'","stUiCommand('select'","se202.noClickMoves++"]:
    assert marker in selection,marker
for marker in ['window.SWYRL_ENGINE_QUEST_SHEEP_AIM_203','se203GroundFromForwardRay','se203.menuPages','se203.menuTextures','se203HandEffects','se203DisposeCached']:
    assert marker in s,marker
assert "if(stUi.build&&!se195.visible&&!se195.photo&&!se210PanelHit(se192InputRecord('right'))&&now-se193.previewAt>100)" in s
assert 'if(!se200Active()||!stUi.shown||!stSession||se195.visible||se195.photo)return;' in s
assert 'se200.vertical=se203.vertical' in s
for marker in ['window.SWYRL_ENGINE_SHEEP_QUICK_GRID_204','se204Gameplay','se204RapidEnabled','se204GridPoint','se204HouseTap','se204SkillTap','se204WheelShow','se204InputFrame']:
    assert marker in s,marker
for marker in ['if(se204RapidEnabled())se204AfterBuild()','se204MenuToggle()','se204.anchor?.x','se204.anchor?.z','gridStep = se204RapidEnabled()']:
    assert marker in s,marker
for marker in ['window.SWYRL_ENGINE_SHEEP_VR_POLISH_205','se205ApplyCamera','se205DecorateMenu','se205MenuHover','se205OverlayActive','se205ApplyCamera(\'tactical\')','se205.menuPointerFrames']:
    assert marker in s,marker
assert 'c.width=384;c.height=192;' in s
assert 'g.scale(.75,.75);' in s
for marker in ['window.SWYRL_ENGINE_SHEEP_MEADOW_FOG_206','se206DecorStop','se206VisualFrame','se206AdjustFog','se206FinishDecor','se206RestoreFog']:
    assert marker in s,marker
assert 'mesh.userData.se206DecorOnly=true' in s
assert 'se206.textureUploads++' in s
for marker in ['window.SWYRL_ENGINE_SHEEP_VR_SPATIAL_207','se207BeginGrab','se207MoveGrab','se207EndGrab','se207Recenter','se207ApplySize','se207PlayMenu']:
    assert marker in s,marker
assert 'se207.pinned=true' in s
for marker in ['window.SWYRL_ENGINE_SHEEP_BIOMES_208','se208ArtBase','se208ArtSlice','se208ArtFinish','se208MakeProps','se208TightenFog','se208Dispose']:
    assert marker in s,marker
assert 'se208.nativeVisionUntouched' not in s or 'nativeVisionUntouched:true' in s
for marker in ['window.SWYRL_ENGINE_SHEEP_RADIAL_ICONS_209','se209IconTexture','se209DecorateWheel','se209OptionStatus','se209RefreshWheel','se209OldDispose']:
    assert marker in s,marker
assert 'A hold select / tap build' in s and 'X hold select / tap skill' in s
for marker in ['window.SWYRL_ENGINE_QUEST_PERFORMANCE_210','window.SWYRL_ENGINE_QUEST_WORKSPACE_210','function se210WorldFrame','function se210PanelHit','function se210PanelGrabFrame','function se210StatusSkill','function se210Held']:
    assert marker in s,marker
assert 'const pressed=se210Held(record,side)' in s
assert "!se210PanelHit(se192InputRecord('right'))" in s
for marker in ['window.SWYRL_ENGINE_QUEST_OS_STABILITY_211','function se211Visibility()','function se211SetState(next,now)','function se211OnFrame()','function se211ButtonsReleased()','function se211CameraSoftReturn()','se211OldControllerFrame']:
    assert marker in s,marker
assert 'const maxStep=timeStep*(se211CameraSoftReturn()?3.2:13);' in s
for marker in ['data-project-template="floating-hand-glove"','window.SWYRL_ENGINE_FLOATING_HAND',
               'se212HandScene','se212OpenHand','SWYRL_ENGINE_HAND_SURFACE',
               'floating-hand-glove','V11_227_ASTRA_WOLF_RIG_SHEEP_TAG']:
    assert marker in s,marker
assert "{position:center,scale,meshDensity:{u:32,v:1}}" not in s,'invalid hand cylinder metadata still present'
assert "return push(name,'cylinder',c,mat,group,{position:center,scale});" in s
assert "delete m.assemblies;m.poseFrames=[];m.poseNeutral=null;m.editedAt='local';" in s
for marker in ['window.SWYRL_ENGINE_SHEEP_WHEEL_COMFORT_214','function se214PositionWheel()','function se214WheelOpen()','function se214HideExtraRays()','function se214RestoreGamePointer()','se214PriorStickIntent','se214PriorFollow','se214PriorForwardGround']:
    assert marker in s,marker
assert 'se214WheelOpen()' in s
for marker in ['window.SWYRL_ENGINE_SHEEP_LIVE_WHEEL_216','se216NativeStickIntent','se216NativeFollow','wheelOpensWithoutCancelingMovement','sheepMovementAllowed:true']:
    assert marker in s,marker
assert 'se199StickIntent=function(...args)' in s
assert 'se195FollowCamera=function(dt)' in s
assert '512%30.72' not in s,'meadow moire crosshatch persists'
for needle in ['window.SWYRL_ENGINE_SHEEP_VR_FIX196','function se196FogRepair(s)','se195PositionRadial=function','se195MenuCamera=function','se195FollowCamera=function','se196ActionPrevious','recenter','se196FogRepair(stSession)']:
    assert needle in s,needle
for marker in ['window.SWYRL_ENGINE_VR_POLISH','function se195FollowCamera(dt)','function se195MoveRig(dx,dy,dz)','function se195RadialHit(record','function se195FogPrepare(s)','referenceDepth:\'fixed-base\'','const se195OldCapture=se193XRCapture']:
    assert marker in s,marker
for marker in ['data-project-template="emberfall-arpg"',"window.SWYRL_ENGINE_EMBERFALL",'ef194MakeStarter()','ef194Cast(\'slash\')',"if(currentProject.kind==='emberfall-arpg')ef194Update(dt);"]:
    assert marker in s, marker
assert "function se193XRMenuActive()" in s and "function se193XRCapture(" in s
assert "se193XRAction('editorCapture')" in s
for required in ['se215OrganicHandSkin','se215FingerSpec','se215HandAnatomicalTrim',
                 'Ulnar edge · curved silver fillet', 'Palm · hypothenar sweep',
                 'const skin=se217OrganicHandSkin(digit,{ell,cap,blend})',
                 'ops.surface(skin,[[-1.58,.53,-.56],[.88,3.51,.55]],.047)']:
    assert required in s,required
for required in ['se217FingerSpec','se217OrganicHandSkin','se217HandAnatomicalTrim',
                 'const digit=se218FingerSpec;', 'const skin=se217OrganicHandSkin(digit,{ell,cap,blend});',
                 'Palm · pinky-side flex crease','Ulnar · tapered edge piping',
                 'f.r*.48,f.r*.57,.030','V11_227_ASTRA_WOLF_RIG_SHEEP_TAG']:
    assert required in s,required
for required in ['se218FingerSpec','se218HandDetails',
                 'Thumb · continuous back-to-tip double helix',
                 'Thumb · dorsal joint to helix feed',
                 'Backhand · anchored digit ',
                 'rail retainer ',
                 'Wrist · ring light insert ',
                 'const digit=se218FingerSpec;',
                 'se218HandDetails({digits:digit,wire,sphere,color});']:
    assert required in s,required
assert "wire('Thumb · luminescent seam'," not in s,'old floating thumb rail still present'
for needle in ['function se219FingerRailPoint(f,t)',
               'function se219FingerRailPath(f)',
               'se219FingerRailPath(f),.014,color.accent',
               'for(const [j,t] of [.45,.77].entries())',
               'const [x,y,railZ]=se219FingerRailPoint(f,t)',
               'Thumb · continuous back-to-tip double helix']:
    assert needle in s,needle
assert 'for(const [j,t] of [.45,.69].entries())' not in s
for marker in ['function se220CreateHandRig(digits)', 'function se220RigWeights(pt,rig)',
               'function se220RigValidate(rig)', 'function se220RigInterpolate(rig,time)',
               'new THREE.SkinnedMesh(g,mat)','new THREE.Skeleton(bones)',
               'se220RigBind();se220RigRefresh();','se220RigControlsInstall();',
               'se220RigFrame();','m.rigging=se220CreateHandRig(digit);',
               'se220RigMesh(p)','Rig · Pose · Animate',
               "model().rigging=source.rigging?structuredClone(source.rigging):null;",
               'V11_227_ASTRA_WOLF_RIG_SHEEP_TAG']:
    assert marker in s,marker
for marker in [
    'function se221GesturePose(rig,kind)',
    'function se221ThumbInfluences(pt,rig)',
    'function se221StudioInstall()',
    'function se221ThumbSync()',
    'se221ThumbInfluences(pt,rig)',
    'se221StudioInstall();',
    'modelAtelierRigOppose','modelAtelierRigThumbCurl',
    'modelAtelierRigAnimateGesture',
    'se220Smooth((t-left.time)/(right.time-left.time))',
    'V11_227_ASTRA_WOLF_RIG_SHEEP_TAG']:
    assert marker in s,marker
assert 'const curled=kind===' not in s, 'legacy non-opposable thumb presets remain'
assert s.count('/* ATELIER_BRIDGE_START */')==1
if args.request:
    request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text())
    assert request['releaseVersion']=='v11.227'
    assert request['sourceIntegritySha256']==m['finalSha256']
    assert request['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_227_ASTRA_WOLF_RIG_SHEEP_TAG'
    repo=ROOT.parents[1]
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    paths=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',head],cwd=repo,text=True).splitlines()
    assert paths==['projects/swrlz-forge-moba/DEPLOY_REQUEST.json'],paths
    parent=subprocess.check_output(['git','rev-parse','HEAD^'],cwd=repo,text=True).strip()
    assert request['sourceCommit']==parent,'Deploy request must pin its exact preceding source commit'
for marker in ['function se222SheepPose(kind,time,seed=0)',
 'function se222SheepClips()', 'function se222SheepStudioInstall()',
 'function se222SheepPreviewFrame()', 'function se222FXBegin(session)',
 'function se222GameFrame(dt)', 'se222SheepPreviewFrame();',
 'se222SheepStudioInstall();','SE222_SHEEP_MOTIONS',
 'se222GameFrame(args[0]);','swyrl-sheep-joint-clips-v1',
 'V11_227_ASTRA_WOLF_RIG_SHEEP_TAG']:
    assert marker in s,marker
for marker in ['function se223WavePose(rig,side,flutter=0)',
               'function se223WaveTimeline(rig)',
               "digit('index',1.06,1.42,.87,.020)",
               "thumb([.37,1.18,-.48],[.34,.19,.20],[.25,.03,.28])",
               "rig.duration=kind==='wave'?2.20:1.5",
               "rig.timeline=kind==='wave'?se223WaveTimeline(rig)",
               'V11_227_ASTRA_WOLF_RIG_SHEEP_TAG']:
    assert marker in s,marker
for needle in ['const SE223_SCHEMA=', 'const SE223_PRESETS=Object.freeze',
 'function se223ValidateEmitter(value)', 'function se223ValidateModel(v)',
 'function se223Frame(dt,t)', 'se223Frame(dt,t);',
 'function se223Create(key=', 'function se223Update(id,changes)',
 'function se223Replace(model)', 'function se223UIOpen()',
 'function se223Install()', 'window.SWYRL_ENGINE_PARTICLES=Object.freeze',
 'window.SWYRL_ENGINE_PARTICLE_STUDIO=Object.freeze',
 'se223UIImport','se223UIAttach','se223UIExport',
 'SE223_MAX_EMITTERS=12','SE223_PER_EMITTER=96','SE223_TOTAL=576',
 'swyrl-particle-studio-v1','V11_227_ASTRA_WOLF_RIG_SHEEP_TAG']:
    assert needle in s,needle
assert s.count('se223Frame(dt,t);')==1
assert s.count('renderer.setAnimationLoop(tick);')==1
for token in [
 'function se225MaterialDefault(kind=', 'function se225ValidateLibrary(source)',
 'function se225MaterialCanvas(def)', 'function se225MaterialSync(force=false)',
 'function se225MaterialFrame(dt,t)', 'se225MaterialFrame(dt,t);',
 'function se225DecorateNativeTabs(nav)', 'se225DecorateNativeTabs(nav);',
 'function se225Open(mode,push=true)', 'window.SWYRL_ENGINE_STUDIOS=Object.freeze',
 'window.SWYRL_ENGINE_MATERIALS=Object.freeze',
 'window.SWYRL_ENGINE_MATERIAL_STUDIO=Object.freeze',
 'swyrl-material-studio-v1', 'se225MaterialUIPaintDown',
 'se225MaterialUIImportImage','V11_227_ASTRA_WOLF_RIG_SHEEP_TAG'
]:
    assert token in s, token
# Astra wolf (v11.227) coexists with sheep houses, PBR studios and Clover animations.
for token in [
 'function se224WolfPose(name,time,phase=0)',
 'function se224WolfRigSpec()',
 'function se224WolfRigValid(v)',
 'function se224WolfClips()',
 'function se224WolfClipsValid(v)',
 'function se224WolfVertexWeights(pos,rig,part,indexById=null)',
 'function se224WolfEnhanceModel(m)',
 'function se224WolfGameVisual(root)',
 'function se224WolfRigMesh(part)',
 'function se224WolfRigBind()',
 'function se224WolfStudioInstall()',
 'function se224WolfGameFrame(dt)',
 'se224WolfStudioInstall();',
 'se224WolfPreviewFrame();',
 'se224WolfGameFrame(args[0]);',
 'window.SWYRL_ENGINE_WOLF_RIG=Object.freeze',
 'window.SWYRL_ENGINE_WOLF_224=Object.freeze',
 'V11_227_ASTRA_WOLF_RIG_SHEEP_TAG',
]: assert token in s,token
assert s.count('se225MaterialFrame(dt,t);')==1,'Only one shared material update in the native renderer'
assert s.count('renderer.setAnimationLoop(tick);')==1,'No second WebGL render loop'
assert "source.version=11.227" in s
for marker in ['const SE226_BUILDINGS=',
               'function se226MakeBuildingScene(id)',
               'function se226OpenBuilding(id,force=false)',
               'window.SWYRL_ENGINE_SHEEP_BUILDING_STARTERS=Object.freeze',
               'data-project-template="sheep-free-shelter"',
               'data-project-template="sheep-thatched-hut"',
               'data-project-template="sheep-cottage"',
               'data-project-template="sheep-barn"',
               'data-project-template="sheep-ram-house"']:
    assert marker in s,marker
subprocess.run(['node',str(ROOT/'tests/test_v11_226_sheep_buildings.cjs')],check=True)
print(json.dumps({'status':'PASS','version':m['name'],'patches':len(m['patches']),'assets':len(r['assets']),'bytes':len(raw),'sha256':m['finalSha256'],'browserAcceptance':False}))
