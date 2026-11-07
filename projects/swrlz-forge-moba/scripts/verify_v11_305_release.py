#!/usr/bin/env python3
"""Verify open Modeler document synchronization and preserved native features."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_305_VANGUARD_COMPLETE_MESH_UV'
THREE_URL='https://cdn.jsdelivr.net/npm/three@0.169.0/+esm'
THREE_BYTES=684391
THREE_SHA256='260fdf7db2ecda0e726a82e37c829cdeb974015c9a4304ea9c51177b2c8b2c1a'


def verify_native_view(html_path,module_path=None,native_project=None):
    def run(module):
        subprocess.run(['node',str(ROOT/'tests/chat_loft_surface_normals_v11_295.mjs'),
                        str(html_path),str(module)],check=True)
        command=['node',str(ROOT/'tests/model_atelier_document_sync_v11_305.mjs'),
                 str(html_path),str(module)]
        if native_project:command.append(str(Path(native_project).resolve()))
        subprocess.run(command,check=True)
    if module_path:
        module=Path(module_path).resolve();data=module.read_bytes()
        assert len(data)==THREE_BYTES and hashlib.sha256(data).hexdigest()==THREE_SHA256
        run(module);return
    # This exact app dependency is test-only and never enters the HF output.
    with tempfile.TemporaryDirectory(prefix='swrlz-three-169-') as directory:
        with urllib.request.urlopen(THREE_URL,timeout=30) as response:
            data=response.read(THREE_BYTES+1)
        assert len(data)==THREE_BYTES and hashlib.sha256(data).hexdigest()==THREE_SHA256
        module=Path(directory)/'three-0.169.0.mjs';module.write_bytes(data);run(module)


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--output',required=True)
    cli.add_argument('--request',action='store_true')
    cli.add_argument('--three-module',help='Optional exact pinned Three ESM for offline verification')
    cli.add_argument('--native-project',help='Optional private native fixture, read-only and never packaged')
    args=cli.parse_args()
    manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
    assert manifest['name']=='§wyrl§ Engine v11.305'
    assert manifest['finalArtifact']=='swyrl_engine_v11_305.html'
    assert len(manifest['patches'])==336
    assert manifest['patches'][-3:]==[
       'patches/v11_303_vanguard_face_geometry_uv_portrait.py',
       'patches/v11_304_modeler_document_sync.py',
       'patches/v11_305_vanguard_complete_mesh_uv.py']
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
       'SE304_MODELER_DOCUMENT_VIEW_SYNC_START','SE304_MODELER_DOCUMENT_VIEW_SYNC_END',
       THREE_URL,MARKER,'<title>§wyrl§ Engine · Maker v11.305</title>',
       "window.SWRLZ_FORGE_BUILD={version:'v11.305'",
       'function se296HeroScene(){',
       'function se297Redesign(scene){',
       'function se297Artwork(tile){',
       'function se297MakePBR(tile){',
       'function se303HeadSurface(t,v){',
       'function se303DrawPortrait(canvas){',
       'faceAtlasPixels:768',
       'function se302BuildSet(family){',
       'const se298AtlasDataURL="data:image/jpeg;base64,',
       'se296TextureSet=function(tile){',
       '<strong>Hooded Vanguard · Whole Mesh &amp; UV Reconstruction</strong>',
       'function se305Body(){',
       'function se305Glove(side){',
       'function se305Hood(){',
       'correctedWristAxes:true',
       'se291HeroScene=se296HeroScene;',
       'function se296TextureSet(tile){',
       'se291HeroMaterial=function(part){',
       'vanguard-rebuilt-',
       'model.parts=parts;model.meshGroups=[];model.assemblies=null;',
       'se291HeroScene=function(){return se297Redesign(se297PreviousScene());};',
       'function seChatAtelierApply(op)',
       'SE295_CHAT_LOFT_SURFACE_NORMALS_START',
       'SWYRL_ENGINE_HAND_SURFACE',
    ):
        assert token in html,token
    for item in ('skin','hair','hood','scarf','uniform','armor','pauldron','teal',
                 'leather','gloves','boots'):
        assert "'v296:"+item+"'" in html,item
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.305';source.version=11.305;")==3
    assert html.count('SE304_MODELER_DOCUMENT_VIEW_SYNC_START')==1
    assert html.count('SE304_MODELER_DOCUMENT_VIEW_SYNC_END')==1
    assert html.count('renderer.setAnimationLoop(tick);')==1
    assert html.count('se291HeroScene=se296HeroScene;')==1
    assert html.count('se291HeroScene=function(){return se297Redesign(se297PreviousScene());};')==1
    subprocess.run(['node','--check',str(ROOT/'runtime/hooded_vanguard_painted_v11_297.js')],check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),
                    str(out/'index.html')],check=True)
    subprocess.run(['node','--check',str(ROOT/'runtime/model_atelier_document_sync_v11_305.js')],check=True)
    subprocess.run(['node',str(ROOT/'tests/chat_character_tools_v11_293.mjs'),str(out/'index.html')],check=True)
    verify_native_view(out/'index.html',args.three_module,args.native_project)
    subprocess.run(['node',str(ROOT/'tests/hooded_vanguard_facial_sculpt_v11_303.cjs')],check=True)
    subprocess.run(['node','--check',str(ROOT/'runtime/hooded_vanguard_full_mesh_uv_v11_305.js')],check=True)
    subprocess.run(['node',str(ROOT/'tests/hooded_vanguard_full_mesh_uv_v11_305.cjs')],check=True)
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
        assert request['releaseVersion']=='v11.305'
        assert request['deployMarker']==MARKER
        assert request['sourceIntegritySha256']==manifest['finalSha256']
        assert len(request['sourceCommit'])==40
    print(json.dumps({'status':'SEALED_SOURCE_VERIFIED',
     'version':'v11.305','patches':336,'htmlBytes':len(raw),
     'sha256':manifest['finalSha256'],'assets':len(receipt['assets']),
     'visualAppearanceOwnerAcceptance':False},indent=2))
if __name__=='__main__':
    main()
