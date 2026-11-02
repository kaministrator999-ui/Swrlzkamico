#!/usr/bin/env python3
"""Build and verify the exact §E glitch-wisp boot and collapsible Model Atelier source package, with routed Game/Modeler pages."""
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
assert m['name']=='§wyrl§ Engine v11.204'
assert m['finalArtifact']=='swyrl_engine_v11_204.html'
assert len(m['patches'])==236 and m['patches'][-1]=='patches/v11_204_sheep_vr_rapid_grid_wheels.py'
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
for text in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_204_SHEEP_VR_RAPID_GRID_WHEELS',
             '<title>§wyrl§ Engine · Maker v11.204</title>',
             "window.SWRLZ_FORGE_BUILD={version:'v11.204'",
             "const PROTOCOL='swrlz-forge-chat-v1'",'seChatAccountPanel','chatAction:seChatAtelierApply',
             'se175ProjectProgress','project.create','se175ActiveProject','se176Install();','se176AccountState(payload);','se177ShowPicture','Continue to Google','se178Install();','se178EnrichContext(value);','host.analyze','Editing now · ','seMobileEditorViewportV11174','seQuestPanelV11168','SWYRL_ENGINE_DEVICE','se-levels-v1','swyrl-workspaces-v1']:
    assert text in s,text
for marker in ['se179VRControlsOpen','se179VRStudio','SWYRL_VR_CONTROLS','swyrl-engine-vr-controls-v1','testInput','immersiveCommandsActive:false']:
    assert marker in s,marker
for marker in ['seChatOutsideDismissV11180','se180InstallDismiss();','function se180Outside(event)','se180-chat-visible','closePanel(false)','se180CancelAnimation','transform:translate3d','se179VRControlsOpen']:
    assert marker in s,marker
for marker in ['seImmersiveXRV11181','se181EnterVR','window.SWYRL_ENGINE_XR=Object.freeze','renderer.setAnimationLoop(tick);',"requestSession('immersive-vr'",'se181XRRender();se192VRFrame();se193XRFrame();renderer.render(scene,camera);','se181XRSelect(record)','se181XRActiveModel()','se181XRMakeExitPanel','SWYRL_ENGINE_XR','se179VRControlsOpen']:
    assert marker in s,marker
for marker in ['se182ProfessionalUI','SWYRL_ENGINE_UI_AUDIT','se183ProjectUI','se184SavedGallery','SWYRL_ENGINE_SAVED_DEFAULT','se184ExtractPreview','se184RenderLocalProjects','se184RenderCloudProjects','se184KickCloudStartup','se185WispBootAtelier','se185InstallAtelierToggle','se185-top-collapsed','data-se186-early','se186StartupBeforeEngine','se186BootRecovery','se187SeparateWorkspaces','se188GameFirstTabs','se189MobilePerformance','se190RenderAudit','se190CountSubmittedFrame','window.SWYRL_ENGINE_XR_RECOVERY','se191XRInstallLanding();','se191XRRenderFrame();','window.SWYRL_ENGINE_VR_EDITOR','se192VRFrame();','se193XRFrame();','se193XRCleanup();','se193XRStart();','window.SWYRL_ENGINE_SHEEP_VR','se192VRCleanup();','se192VRStart();','se192FreezeBillboards();','se191XRMakeBeacon();','se191XRCleanup();','se191XRStartWatchdog(requested);','SWYRL_ENGINE_PERFORMANCE_V11190','se190ComparePresets','const ribBrass=new THREE.InstancedMesh(','se189MobileBoost','se189ResizeIfNeeded','SWYRL_ENGINE_PERFORMANCE_V11189','se187WorkspaceTabs','se187-modeler-page','se187-workspace-tabs','SWYRL_ENGINE_WORKSPACES','V11_204_SHEEP_VR_RAPID_GRID_WHEELS','se183LevelsToggle','se183StartLoad','se183CloudListCached','SWYRL_ENGINE_PROJECT_LOAD','se179VRControlsOpen','se181EnterVR','seChatOutsideDismissV11180']:
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
# The v11.204 XR-only ground select body must not emit click-to-move.
selection=s.split('function se193XRGameSelect(record){',1)[1].split('function se193XRSnapFollow(){',1)[0]
assert "stUiCommand('move'" not in selection,'Quest trigger still emits click-to-move'
for marker in ["stUiCommand('build'","stUiCommand('attack'","stUiCommand('rescue'","stUiCommand('select'","se202.noClickMoves++"]:
    assert marker in selection,marker
for marker in ['window.SWYRL_ENGINE_QUEST_SHEEP_AIM_203','se203GroundFromForwardRay','se203.menuPages','se203.menuTextures','se203HandEffects','se203DisposeCached']:
    assert marker in s,marker
assert 'if(stUi.build&&!se195.visible&&!se195.photo&&now-se193.previewAt>100)' in s
assert 'if(!se200Active()||!stUi.shown||!stSession||se195.visible||se195.photo)return;' in s
assert 'se200.vertical=se203.vertical' in s
for marker in ['window.SWYRL_ENGINE_SHEEP_QUICK_GRID_204','se204Gameplay','se204RapidEnabled','se204GridPoint','se204HouseTap','se204SkillTap','se204WheelShow','se204InputFrame']:
    assert marker in s,marker
for marker in ['if(se204RapidEnabled())se204AfterBuild()','se204MenuToggle()','se204.anchor?.x','se204.anchor?.z','gridStep = se204RapidEnabled()']:
    assert marker in s,marker
assert '512%30.72' not in s,'meadow moire crosshatch persists'
for needle in ['window.SWYRL_ENGINE_SHEEP_VR_FIX196','function se196FogRepair(s)','se195PositionRadial=function','se195MenuCamera=function','se195FollowCamera=function','se196ActionPrevious','recenter','se196FogRepair(stSession)']:
    assert needle in s,needle
for marker in ['window.SWYRL_ENGINE_VR_POLISH','function se195FollowCamera(dt)','function se195MoveRig(dx,dy,dz)','function se195RadialHit(record','function se195FogPrepare(s)','referenceDepth:\'fixed-base\'','const se195OldCapture=se193XRCapture']:
    assert marker in s,marker
for marker in ['data-project-template="emberfall-arpg"',"window.SWYRL_ENGINE_EMBERFALL",'ef194MakeStarter()','ef194Cast(\'slash\')',"if(currentProject.kind==='emberfall-arpg')ef194Update(dt);"]:
    assert marker in s, marker
assert "function se193XRMenuActive()" in s and "function se193XRCapture(" in s
assert "se193XRAction('editorCapture')" in s
assert s.count('/* ATELIER_BRIDGE_START */')==1
if args.request:
    request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text())
    assert request['releaseVersion']=='v11.204'
    assert request['sourceIntegritySha256']==m['finalSha256']
    assert request['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_204_SHEEP_VR_RAPID_GRID_WHEELS'
    repo=ROOT.parents[1]
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    paths=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',head],cwd=repo,text=True).splitlines()
    assert paths==['projects/swrlz-forge-moba/DEPLOY_REQUEST.json'],paths
    parent=subprocess.check_output(['git','rev-parse','HEAD^'],cwd=repo,text=True).strip()
    assert request['sourceCommit']==parent,'Deploy request must pin its exact preceding source commit'
print(json.dumps({'status':'PASS','version':m['name'],'patches':len(m['patches']),'assets':len(r['assets']),'bytes':len(raw),'sha256':m['finalSha256'],'browserAcceptance':False}))
