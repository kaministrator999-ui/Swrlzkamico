#!/usr/bin/env python3
"""Check UI integration, selection semantics and VR shell lifecycle without headset."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
icon=load('se415',ROOT/'patches/v11_415_model_vr_iconography.py')
index=load('se417',ROOT/'patches/v11_417_model_vr_object_index.py')
base=(ROOT/'runtime/model_studio_vr_ui_v11_410.js').read_text(encoding='utf8')
script=index.enhance_ui(icon.enhance_ui(base))
assert script.count('SE417_MODEL_VR_OBJECT_INDEX_UI')==1
for value in ["objects:[]","['objects','Objects']", "indexEntries","indexSelected","indexPage","indexMulti","index-part-", "index-next","index-prev","if(type==='layers')","state.indexSelected.includes"]:
    assert value in script,value
helper=ROOT/'runtime/model_vr_object_index_v11_417.js'
h=helper.read_text(encoding='utf8')
for value in ["SE417_MODEL_VR_OBJECT_INDEX_START", "se350Tools().select(item.id,{additive:!!s.se417IndexMulti})",
 "new THREE.SkinnedMesh", "new THREE.Mesh", "side:THREE.BackSide",
 "se417DisposeHighlights", "se417IndexState"]:
    assert value in h,value
with TemporaryDirectory() as temp:
    p=Path(temp)/'ui.js'
    p.write_text(script,encoding='utf8')
    subprocess.run(['node','--check',str(p)],check=True)
subprocess.run(['node','--check',str(helper)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_vr_object_index_v11_417.cjs')],check=True)
print('MODEL_VR_OBJECT_INDEX_TESTS_PASS')
