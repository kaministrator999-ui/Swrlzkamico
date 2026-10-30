#!/usr/bin/env python3
"""Build and verify the exact §E Chat project-workflow package, without browser/game suites."""
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
assert m['name']=='§wyrl§ Engine v11.175'
assert m['finalArtifact']=='swyrl_engine_v11_175.html'
assert len(m['patches'])==207 and m['patches'][-2:]==['patches/v11_174_mobile_editor_viewport.py','patches/v11_175_chat_project_workflow.py']
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
s=raw.decode('utf-8')
r=json.loads((out/'SOURCE.json').read_text())
assert len(raw)==m['finalBytes']==r['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==r['finalSha256']
assert r['sourceVersion']==m['name'] and r['patches']==m['patches']
assert len(r['assets'])==68
for rel,meta in r['assets'].items():
    data=(out/rel).read_bytes()
    assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],rel
for text in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_175_CHAT_PROJECT_WORKFLOW',
             '<title>§wyrl§ Engine · Maker v11.175</title>',
             "window.SWRLZ_FORGE_BUILD={version:'v11.175'",
             "const PROTOCOL='swrlz-forge-chat-v1'",'seChatAccountPanel','chatAction:seChatAtelierApply',
             'se175ProjectProgress','project.create','se175ActiveProject','seMobileEditorViewportV11174','seQuestPanelV11168','SWYRL_ENGINE_DEVICE','se-levels-v1','swyrl-workspaces-v1']:
    assert text in s,text
assert s.count('/* ATELIER_BRIDGE_START */')==1
if args.request:
    request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text())
    assert request['releaseVersion']=='v11.175'
    assert request['sourceIntegritySha256']==m['finalSha256']
    assert request['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_175_CHAT_PROJECT_WORKFLOW'
    repo=ROOT.parents[1]
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    paths=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',head],cwd=repo,text=True).splitlines()
    assert paths==['projects/swrlz-forge-moba/DEPLOY_REQUEST.json'],paths
    parent=subprocess.check_output(['git','rev-parse','HEAD^'],cwd=repo,text=True).strip()
    assert request['sourceCommit']==parent,'Deploy request must pin its exact preceding source commit'
print(json.dumps({'status':'PASS','version':m['name'],'patches':len(m['patches']),'assets':len(r['assets']),'bytes':len(raw),'sha256':m['finalSha256'],'browserAcceptance':False}))
