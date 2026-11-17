#!/usr/bin/env python3
"""Verify exact §E v11.486 ring topology, UV-safe transforms and Sorting Hat source provenance."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
arg=argparse.ArgumentParser()
arg.add_argument('--output',required=True)
arg.add_argument('--request',action='store_true')
args=arg.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.486'
assert m['finalArtifact']=='swyrl_engine_v11_486.html'
assert len(m['patches'])==463 and m['patches'][-3:]==['patches/v11_484_ring_detail_transforms.py','patches/v11_485_one_cloth_sorting_hat.py','patches/v11_486_project_revisions.py']
assert isinstance(m['finalBytes'],int) and isinstance(m['finalSha256'],str)
for file in ('sorting_hat_starter_v11_483.js','model_ring_detail_kernel_v11_483.js','model_ring_detail_studio_v11_483.js','model_vertex_entry_v11_477.js','model_progressive_hierarchy_v11_477.js','model_ring_vertex_highlight_v11_478.js','model_ring_height_v11_478.js','model_ring_rim_visibility_v11_479.js','model_editable_entry_v11_480.js','model_textured_editable_copy_v11_481.js','model_geometric_ring_v11_482.js','model_ring_height_layout_v11_482.js',
             'model_progressive_rail_fix_v11_475.js','model_progressive_tools_v11_474.js',
             'project_revisions_v11_486.js','project_revision_actions_v11_486.js','studio_asset_revisions_v11_486.js',
             'model_ring_kernel_v11_466.js','model_ring_ui_v11_466.js'):
 subprocess.run(['node','--check',str(ROOT/'runtime'/file)],check=True)
subprocess.run([sys.executable,str(ROOT/'tests/sorting_hat_single_mesh_v11_485.py')],check=True)
subprocess.run(['node',str(ROOT/'tests/project_revisions_v11_486.cjs')],check=True)
for file in ('model_progressive_hierarchy_v11_477.mjs','model_ring_vertex_highlight_v11_478.mjs','model_ring_rim_visible_side_v11_479.mjs','model_editable_entry_v11_480.mjs','model_textured_editable_copy_v11_481.mjs','model_geometric_ring_height_v11_482.mjs',
             'model_ring_detail_transforms_v11_483.mjs','model_progressive_rail_fix_v11_475.mjs',
             'model_progressive_tools_v11_474.mjs',
             'model_ring_kernel_v11_466.mjs'):
 subprocess.run(['node',str(ROOT/'tests'/file)],check=True)
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
source=(out/'index.html').read_bytes()
assert source==(out/'modeler.html').read_bytes()
assert len(source)==m['finalBytes']
assert hashlib.sha256(source).hexdigest()==m['finalSha256']
html=source.decode('utf8')
for token in (
 "window.SWRLZ_FORGE_BUILD={version:'v11.486'",
 '<title>§wyrl§ Engine · Maker v11.486</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_486_PROJECT_REVISIONS',
 'se486NativeProjectHistory','se486ImportProjectUpdate','se486AssetHistory',
 'SWYRL_ENGINE_REVISIONS_486','se486History','se486InstallAssetActions',
 'SE477_VERTEX_ENTRY_START','SE477_SELECTION_HIERARCHY_STYLES_START',
 'SE478_RING_VERTEX_HIGHLIGHT_START','se478SelectedVertices',
 'SE478_RING_HEIGHT_SLIDER_START','SE478_RING_HEIGHT_STYLES_START',
 'SE479_RIM_KERNEL_START','SE479_RIM_VISIBILITY_START',
 'SE479_RIM_VISIBILITY_STYLES_START','se479CenterToggle',
 'SE480_EDITABLE_ENTRY_START','SE480_EDITABLE_ENTRY_STYLES_START',
 'SE481_TEXTURED_EDITABLE_COPY_START','SE481_TEXTURED_EDITABLE_COPY_STYLES_START',
 'SE483_SORTING_HAT_END','se483OpenSortingHat','se483ValidateSortingHat',
 'parts.length!==1||!Array.isArray(scene?.scene?.actors)',
 'SE483_RING_DETAIL_KERNEL_START','SE483_RING_DETAIL_STUDIO_START',
 'SE483_RING_DETAIL_STUDIO_STYLES_START','se483RingDetailStudio',
 'se483Rings','window.SWYRL_ENGINE_RING_DETAIL_483=Object.freeze(',
 'data-project-template="sorting-hat"','SE482_GEOMETRIC_RING_START','SE482_RING_HEIGHT_LAYOUT_START',
 'SE482_RING_HEIGHT_LAYOUT_STYLES_START','se482CircleControl',
 'se482HeightGrip',
 'se481OriginalSourceToggle','se481SourceHidden','se481SourceId',
 'se480EditableEntry','se480MakeEditable','se480EditableReason',
 'se479MaterialVertices','se479VisibleSideOnly',
 'se478RingHeightSlider','se478HeightRange',
 'window.SWYRL_ENGINE_RING_HIGHLIGHT_478=Object.freeze(',
 'window.SWYRL_ENGINE_RIM_VISIBILITY_479=Object.freeze(',
 'window.SWYRL_ENGINE_EDITABLE_ENTRY_480=Object.freeze(',
 'window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481=Object.freeze(',
 'window.SWYRL_ENGINE_GEOMETRIC_RING_482=Object.freeze(',
 'window.SWYRL_ENGINE_RING_HEIGHT_LAYOUT_482=Object.freeze(',
 'function renderShapes(){','function selectShape(shape){',
 'id=\'se477SelectionShapes\'',
 "state.selectionType=operation?'vertex':''",
 "['ring','Vertex ring']","['fill','Filled vertex ring']",
 'window.SWYRL_ENGINE_VERTEX_ENTRY_477=Object.freeze(',
 'window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474=Object.freeze(',
 'SE476_ENGINE_ACCOUNT_START_START','id="se476StartupGate"',
 'SE475_PROGRESSIVE_RAIL_VISIBILITY_START','SE474_PROGRESSIVE_MODEL_TOOLS_START',
 'SE466_RING_UI_START','SE466_RING_BRIDGE_START',
 'SE430_MODEL_WORKSHOP_BRIDGE_START','se474SpecificModes','se474ToolFlyout'
):assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.486';source.version=11.485;")==5
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),
 str(out/'index.html')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,value in (
 ('sourceVersion',m['name']),('finalBytes',len(source)),
 ('finalSha256',m['finalSha256']),('patches',m['patches'])
):assert receipt[key]==value,key
assert len(receipt['assets'])==78
assert 'scenes/model-atelier-sorting-hat.swyrl.json' in receipt['assets']
scene=json.loads((out/'scenes/model-atelier-sorting-hat.swyrl.json').read_text('utf8'))
assert len(scene['project']['modelAtelier']['parts'])==1
assert len(scene['project']['modelAtelier']['parts'][0]['uvPaintPNG'])<=360000
for file,expected in receipt['assets'].items():
 raw=(out/file).read_bytes()
 assert len(raw)==expected['bytes']
 assert hashlib.sha256(raw).hexdigest()==expected['sha256'],file
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']=='v11.486'
 assert request['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_486_PROJECT_REVISIONS'
 assert request['target']=='kamiloki/swrlz-forge-moba'
 assert request['sourceIntegritySha256']==m['finalSha256']
 assert request['sourceCommit']
print(json.dumps({'status':'SOURCE_VERIFIED','version':'v11.486',
 'bytes':len(source),'sha256':m['finalSha256'],'patches':463,
 'assets':78,'physicalMobileTested':False,'physicalVRTested':False}),flush=True)
