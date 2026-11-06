#!/usr/bin/env python3
"""Verify the sealed v11.296 native Vanguard rebuild with narrow source checks."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_296_VANGUARD_REBUILT'

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--output',required=True)
    cli.add_argument('--request',action='store_true')
    args=cli.parse_args()
    manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
    assert manifest['name']=='§wyrl§ Engine v11.296'
    assert manifest['finalArtifact']=='swyrl_engine_v11_296.html'
    assert len(manifest['patches'])==327
    assert manifest['patches'][-3:]==[
       'patches/v11_294_vanguard_socket_loader_fix.py',
       'patches/v11_295_chat_loft_surface_normals.py',
       'patches/v11_296_vanguard_rebuild.py']
    assert isinstance(manifest['finalBytes'],int) and manifest['finalBytes']>0
    assert len(manifest['finalSha256'])==64
    out=Path(args.output).resolve()
    subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
    raw=(out/'index.html').read_bytes()
    assert raw==(out/'modeler.html').read_bytes()
    assert len(raw)==manifest['finalBytes']
    assert hashlib.sha256(raw).hexdigest()==manifest['finalSha256']
    html=raw.decode('utf8')
    for token in (
       MARKER,'<title>§wyrl§ Engine · Maker v11.296</title>',
       "window.SWRLZ_FORGE_BUILD={version:'v11.296'",
       'function se296HeroScene(){',
       'se291HeroScene=se296HeroScene;',
       'function se296TextureSet(tile){',
       'se291HeroMaterial=function(part){',
       'vanguard-rebuilt-',
       'model.parts=parts;model.meshGroups=[];model.assemblies=null;',
       '<strong>Hooded Vanguard · Rebuilt Character</strong>',
       'function seChatAtelierApply(op)',
       'SE295_CHAT_LOFT_SURFACE_NORMALS_START',
       'SWYRL_ENGINE_HAND_SURFACE',
    ):
        assert token in html,token
    for item in ('skin','hair','hood','scarf','uniform','armor','pauldron','teal',
                 'leather','gloves','boots'):
        assert "'v296:"+item+"'" in html,item
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.296';source.version=11.296;")==3
    assert html.count('se291HeroScene=se296HeroScene;')==1
    subprocess.run(['node','--check',str(ROOT/'runtime/hooded_vanguard_rebuild_v11_296.js')],check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),
                    str(out/'index.html')],check=True)
    receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
    assert receipt['sourceVersion']==manifest['name']
    assert receipt['patches']==manifest['patches']
    assert receipt['finalSha256']==manifest['finalSha256']
    assert receipt['finalBytes']==manifest['finalBytes']
    assert len(receipt['assets'])==71
    for name,meta in receipt['assets'].items():
        data=(out/name).read_bytes()
        assert len(data)==meta['bytes']
        assert hashlib.sha256(data).hexdigest()==meta['sha256']
    if args.request:
        request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
        assert request['releaseVersion']=='v11.296'
        assert request['deployMarker']==MARKER
        assert request['sourceIntegritySha256']==manifest['finalSha256']
        assert len(request['sourceCommit'])==40
    print(json.dumps({'status':'SEALED_SOURCE_VERIFIED',
     'version':'v11.296','patches':327,'htmlBytes':len(raw),
     'sha256':manifest['finalSha256'],'assets':len(receipt['assets']),
     'visualAppearanceOwnerAcceptance':False},indent=2))
if __name__=='__main__':
    main()
