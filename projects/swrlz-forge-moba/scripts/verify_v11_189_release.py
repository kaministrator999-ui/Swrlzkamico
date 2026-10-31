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
assert m['name']=='§wyrl§ Engine v11.189'
assert m['finalArtifact']=='swyrl_engine_v11_189.html'
assert len(m['patches'])==221 and m['patches'][-1]=='patches/v11_189_mobile_performance.py'
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
for text in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_189_MOBILE_RENDER_BOOST',
             '<title>§wyrl§ Engine · Maker v11.189</title>',
             "window.SWRLZ_FORGE_BUILD={version:'v11.189'",
             "const PROTOCOL='swrlz-forge-chat-v1'",'seChatAccountPanel','chatAction:seChatAtelierApply',
             'se175ProjectProgress','project.create','se175ActiveProject','se176Install();','se176AccountState(payload);','se177ShowPicture','Continue to Google','se178Install();','se178EnrichContext(value);','host.analyze','Editing now · ','seMobileEditorViewportV11174','seQuestPanelV11168','SWYRL_ENGINE_DEVICE','se-levels-v1','swyrl-workspaces-v1']:
    assert text in s,text
for marker in ['se179VRControlsOpen','se179VRStudio','SWYRL_VR_CONTROLS','swyrl-engine-vr-controls-v1','testInput','immersiveCommandsActive:false']:
    assert marker in s,marker
for marker in ['seChatOutsideDismissV11180','se180InstallDismiss();','function se180Outside(event)','se180-chat-visible','closePanel(false)','se180CancelAnimation','transform:translate3d','se179VRControlsOpen']:
    assert marker in s,marker
for marker in ['seImmersiveXRV11181','se181EnterVR','window.SWYRL_ENGINE_XR=Object.freeze','renderer.setAnimationLoop(tick);',"requestSession('immersive-vr'",'se181XRRender();renderer.render(scene,camera);','se181XRSelect(record)','se181XRActiveModel()','se181XRMakeExitPanel','SWYRL_ENGINE_XR','se179VRControlsOpen']:
    assert marker in s,marker
for marker in ['se182ProfessionalUI','SWYRL_ENGINE_UI_AUDIT','se183ProjectUI','se184SavedGallery','SWYRL_ENGINE_SAVED_DEFAULT','se184ExtractPreview','se184RenderLocalProjects','se184RenderCloudProjects','se184KickCloudStartup','se185WispBootAtelier','se185InstallAtelierToggle','se185-top-collapsed','data-se186-early','se186StartupBeforeEngine','se186BootRecovery','se187SeparateWorkspaces','se188GameFirstTabs','se189MobilePerformance','se189MobileBoost','se189ResizeIfNeeded','SWYRL_ENGINE_PERFORMANCE_V11189','se187WorkspaceTabs','se187-modeler-page','se187-workspace-tabs','SWYRL_ENGINE_WORKSPACES','V11_189_MOBILE_RENDER_BOOST','se183LevelsToggle','se183StartLoad','se183CloudListCached','SWYRL_ENGINE_PROJECT_LOAD','se179VRControlsOpen','se181EnterVR','seChatOutsideDismissV11180']:
    assert marker in s,marker
assert 'seLevelRawLoadProject(structuredClone(chosen.data)' not in s
assert 'const result=seLevelRawLoadProject(target,...options);' in s
assert s.index('data-se186-early="1"')<s.index('window.SWRLZ_FORGE_BUILD=')
assert s.count('renderer.setAnimationLoop(tick);')==1
assert s.count('/* ATELIER_BRIDGE_START */')==1
if args.request:
    request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text())
    assert request['releaseVersion']=='v11.189'
    assert request['sourceIntegritySha256']==m['finalSha256']
    assert request['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_189_MOBILE_RENDER_BOOST'
    repo=ROOT.parents[1]
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    paths=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',head],cwd=repo,text=True).splitlines()
    assert paths==['projects/swrlz-forge-moba/DEPLOY_REQUEST.json'],paths
    parent=subprocess.check_output(['git','rev-parse','HEAD^'],cwd=repo,text=True).strip()
    assert request['sourceCommit']==parent,'Deploy request must pin its exact preceding source commit'
print(json.dumps({'status':'PASS','version':m['name'],'patches':len(m['patches']),'assets':len(r['assets']),'bytes':len(raw),'sha256':m['finalSha256'],'browserAcceptance':False}))
