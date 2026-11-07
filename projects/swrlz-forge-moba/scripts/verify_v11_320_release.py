#!/usr/bin/env python3
"""Verify organized studio navigation, project routing and preserved native features."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_320_STUDIO_NAVIGATION_LAYOUT'
THREE_URL='https://cdn.jsdelivr.net/npm/three@0.169.0/+esm'
THREE_BYTES=684391
THREE_SHA256='260fdf7db2ecda0e726a82e37c829cdeb974015c9a4304ea9c51177b2c8b2c1a'


def verify_native_view(html_path,module_path=None,native_project=None):
    def run(module):
        subprocess.run(['node',str(ROOT/'tests/chat_loft_surface_normals_v11_295.mjs'),
                        str(html_path),str(module)],check=True)
        command=['node',str(ROOT/'tests/model_atelier_document_sync_v11_304.mjs'),
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
    assert manifest['name']=='§wyrl§ Engine v11.320'
    assert manifest['finalArtifact']=='swyrl_engine_v11_320.html'
    assert len(manifest['patches'])==341
    assert manifest['patches'][-3:]==[
       'patches/v11_308_arcane_grip_fit_hide_rays.py',
       'patches/v11_309_arcane_native_ray_aim.py',
       'patches/v11_320_studio_navigation_layout.py']
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
       'SE320_PROJECT_STUDIO_ROUTING_START','SE320_EDITOR_LAYOUT_START',
       'SE306_SHARED_APPROACH_CACHE','SE307_DORSAL_UP_CONTROLLER_GLOVES',
       'SE308_GRIP_ANCHOR','SE308_HIDE_XR_RAYS',
       "if(Array.isArray(data?.scene?.actors))initializedGame=true;",
       THREE_URL,MARKER,'<title>§wyrl§ Engine · Maker v11.320</title>',
       "window.SWRLZ_FORGE_BUILD={version:'v11.320'",
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
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.320';source.version=11.320;")==3
    assert html.count('SE304_MODELER_DOCUMENT_VIEW_SYNC_START')==1
    assert html.count('SE304_MODELER_DOCUMENT_VIEW_SYNC_END')==1
    assert html.count('renderer.setAnimationLoop(tick);')==1
    assert html.count('se291HeroScene=se296HeroScene;')==1
    assert html.count('se291HeroScene=function(){return se297Redesign(se297PreviousScene());};')==1
    subprocess.run(['node','--check',str(ROOT/'runtime/hooded_vanguard_painted_v11_297.js')],check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),
                    str(out/'index.html')],check=True)
    subprocess.run(['node','--check',str(ROOT/'runtime/model_atelier_document_sync_v11_304.js')],check=True)
    subprocess.run(['node',str(ROOT/'tests/chat_character_tools_v11_293.mjs'),str(out/'index.html')],check=True)
    verify_native_view(out/'index.html',args.three_module,args.native_project)
    subprocess.run(['node',str(ROOT/'tests/hooded_vanguard_facial_sculpt_v11_303.cjs')],check=True)
    subprocess.run(['node','--check',str(ROOT/'runtime/hooded_vanguard_full_mesh_uv_v11_305.js')],check=True)
    subprocess.run(['node',str(ROOT/'tests/hooded_vanguard_full_mesh_uv_v11_305.cjs')],check=True)
    subprocess.run(['node',str(ROOT/'tests/studio_project_routing_v11_320.cjs')],check=True)
    for file in ['studio_editor_layout_v11_320.js','studio_project_routing_v11_320.js']:
        subprocess.run(['node','--check',str(ROOT/'runtime'/file)],check=True)
    subprocess.run(['node',str(ROOT/'tests/arcane_grip_ray_v11_308.cjs'),str(out/'index.html')],check=True)
    subprocess.run(['node',str(ROOT/'tests/arcane_native_ray_v11_309.cjs'),str(out/'index.html')],check=True)
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
        assert request['releaseVersion']=='v11.320'
        assert request['deployMarker']==MARKER
        assert request['sourceIntegritySha256']==manifest['finalSha256']
        assert len(request['sourceCommit'])==40
    print(json.dumps({'status':'SEALED_SOURCE_VERIFIED',
     'version':'v11.320','patches':341,'htmlBytes':len(raw),
     'sha256':manifest['finalSha256'],'assets':len(receipt['assets']),
     'visualAppearanceOwnerAcceptance':False},indent=2))
if __name__=='__main__':
    main()
