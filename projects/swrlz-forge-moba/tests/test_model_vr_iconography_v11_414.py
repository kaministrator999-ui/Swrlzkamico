#!/usr/bin/env python3
"""Focused icon and JavaScript checks against the newly patched Model VR UI."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import subprocess

ROOT = Path(__file__).resolve().parents[1]
patch_file = ROOT / "patches/v11_414_model_vr_iconography.py"
spec = importlib.util.spec_from_file_location("vr_icon_patch",patch_file)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
before = (ROOT/"runtime/model_studio_vr_ui_v11_410.js").read_text(encoding="utf8")
after = mod.enhance_ui(before)
assert after != before
assert after.count("SE414_MODEL_VR_ICONOGRAPHY") == 1
assert "fillText('?',0,1)" not in after
assert "se414Icons" in after
assert "if(type==='rotate')" in after
assert "if(/-(?:plus|minus)$/.test(item.id))" in after
assert "function se340CreateModelVRUI(options)" in after
with TemporaryDirectory() as folder:
    script=Path(folder)/"model_vr_ui_v11_414.js"
    script.write_text(after,encoding="utf8")
    subprocess.run(["node","--check",str(script)],check=True)
    test= r"""
const fs=require('node:fs'), assert=require('node:assert/strict');
const src=fs.readFileSync(process.argv[1],'utf8');
const a=src.indexOf('function iconType(id){'),b=src.indexOf('function icon(c,type',a);
assert(a>0&&b>a,'icon routing must exist');
const iconType=new Function('state',src.slice(a,b)+'return iconType;')({accessoryParams:{emblem:'leaf'}});
const expected={
 'selector':'select','selector-sweep':'sweep','selector-lasso-front':'lasso-front',
 'selector-lasso-through':'lasso-through','projects':'folder','grab':'grab',
 'save-local':'save','save-account':'cloud','clone-project':'clone',
 'menu-reset':'reset-menu','menu-hide':'hide-menu',
 'display-textured':'texture','display-solid':'solid',
 'display-wireframe':'wire','display-xray':'xray','display-normals':'normals',
 'aim-hand':'controller','aim-yaw-plus':'yaw','aim-pitch-minus':'pitch',
 'aim-reset-all':'reset-both','view-front':'view-front','view-back':'view-back',
 'view-left':'view-left','view-right':'view-right','view-top':'view-top',
 'view-bottom':'view-bottom','view-iso':'view-iso',
 'move':'move','rotate':'rotate','undo':'undo','redo':'redo',
 'sculpt':'brush','create-box':'cube','create-sphere':'sphere',
 'accessory-width-minus':'width','accessory-width-plus':'width'
};
for(const [id,want] of Object.entries(expected))
 assert.equal(iconType(id),want,id);
assert.notEqual(iconType('rotate'),iconType('undo'));
const s=src.indexOf('function icon(c,type'),e=src.indexOf('const plate=surface(',s);
assert(s>0&&e>s,'renderer exists');
const drawIcon=new Function('rounded',src.slice(s,e)+'return icon;')(()=>{});
const c=new Proxy({}, {get(o,k){return k in o?o[k]:()=>{};},set(o,k,v){o[k]=v;return true;}});
for(const [id] of Object.entries(expected))drawIcon(c,iconType(id),10,10,40,'#ffffff');
console.log('MODEL_VR_ICONOGRAPHY_PASS',Object.keys(expected).length,'controls');
"""
    subprocess.run(["node","-e",test,str(script)],check=True)
print("MODEL_VR_ICONOGRAPHY_SYNTAX_AND_ROUTING_PASS")
