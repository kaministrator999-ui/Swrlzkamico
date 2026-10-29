#!/usr/bin/env python3
"""Rebuild and validate the exact §E dialog-layer package and 68 assets."""
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
assert m['name']=='§wyrl§ Engine v11.173'
assert m['finalArtifact']=='swyrl_engine_v11_173.html'
assert len(m['patches'])==205 and m['patches'][-2:]==['patches/v11_172_clean_chat_header.py','patches/v11_173_dialog_stack.py']
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
for text in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_173_DIALOG_LAYER_PRIORITY',
             '<title>§wyrl§ Engine · Maker v11.173</title>',
             "window.SWRLZ_FORGE_BUILD={version:'v11.173'",
             "const PROTOCOL='swrlz-forge-chat-v1'",'seChatAccountPanel','chatAction:seChatAtelierApply',
             'se171-project-hub-layer','se170Install','se170AccountStatus','se170-project-library','seQuestPanelV11168','SWYRL_ENGINE_DEVICE','se-levels-v1','swyrl-workspaces-v1']:
    assert text in s,text
assert s.count('/* ATELIER_BRIDGE_START */')==1
assert '<style id="se173-editor-layer-priority">' in s
assert 'function se173PromoteProjectDialog()' in s
assert 'document.body.appendChild(hub)' in s
assert '<a href="https://kamiloki-swyrlz.hf.space" target="_blank" rel="noopener">Open Chat</a>' not in s
assert '<strong>§wyrlz Chat</strong><button type="button" id="seChatClose"' in s
assert 'id="seChatSignIn"' in s and 'id="seChatLoad"' in s and 'se170Install' in s
if args.request:
    request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text())
    assert request['releaseVersion']=='v11.173'
    assert request['sourceIntegritySha256']==m['finalSha256']
    assert request['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_173_DIALOG_LAYER_PRIORITY'
    repo=ROOT.parents[1]
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    paths=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',head],cwd=repo,text=True).splitlines()
    assert paths==['projects/swrlz-forge-moba/DEPLOY_REQUEST.json'],paths
    parent=subprocess.check_output(['git','rev-parse','HEAD^'],cwd=repo,text=True).strip()
    assert request['sourceCommit']==parent,'Deploy request must pin its exact preceding source commit'
print(json.dumps({'status':'PASS','version':m['name'],'patches':len(m['patches']),'assets':len(r['assets']),'bytes':len(raw),'sha256':m['finalSha256'],'browserAcceptance':False}))
