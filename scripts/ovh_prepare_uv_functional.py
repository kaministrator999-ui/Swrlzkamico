#!/usr/bin/env python3
"""Apply narrowly scoped UV layout delivery patch and optional isolated functional fixture."""
import sys
from pathlib import Path
root=Path('candidate-source/projects/swrlz-forge-moba/runtime')
p=root/'uv_auto_unwrap_v11_555.js'
s=p.read_text()
assert s.count('/* SE557_UNIVERSAL_UV_END */')==1
# Modify only the saved UV candidate delivery runtime, not the sealed engine.
def once(old,new):
    global s
    assert s.count(old)==1,old
    s=s.replace(old,new,1)
once("uv=t.mesh.geometry.getAttribute('uv'),mat=t.mesh.material;",
     "uv=t.mesh.geometry.getAttribute('uv'),mat=t.mesh.userData.se455OriginalMaterial||t.mesh.material;")
once(" const map=paint?new THREE.CanvasTexture(paint.canvas):null;\n if(map&&THREE.SRGBColorSpace)map.colorSpace=THREE.SRGBColorSpace;\n if(map){map.wrapS=map.wrapT=THREE.RepeatWrapping;}\n return {t,mesh,result,paint,map,",
     """ let paintFields=null;
 if(paint){
  const b64=paint.data.split(',')[1];
  const bytes=Math.floor(b64.length*3/4)-(b64.endsWith('==')?2:b64.endsWith('=')?1:0);
  paintFields={uvPaintPNG:paint.data,uvPaintOffset:[0,0],uvPaintSourceW:paint.canvas.width,uvPaintSourceH:paint.canvas.height,uvPaintSourceBytes:bytes};
 }
 const probe={...t.part,topologyMesh:{...mesh,uvs:result.uvs},...(paintFields||{})};
 if(!checkPart(probe))throw Error('Optimized mesh or texture exceeds native save schema; original preserved');
 return {t,mesh,result,paintFields,""")
once("   const {t,mesh,result,paint,map}=p;\n   mesh.uvs=result.uvs.slice();\n   const uv=t.mesh.geometry.getAttribute('uv');for(let i=0;i<uv.count;i++)uv.setXY(i,result.uvs[i*2],result.uvs[i*2+1]);uv.needsUpdate=true;\n   if(paint){t.part.uvPaintPNG=paint.data;t.part.uvPaintOffset=[0,0];t.mesh.material.map=map;t.mesh.material.needsUpdate=true;p.map=null;}",
     """   const {t,mesh,result,paintFields}=p;
   mesh.uvs=result.uvs.slice();
   if(paintFields)Object.assign(t.part,paintFields);
   // signalEdited rebuilds geometry and native material from these persisted fields.
   // Never attach a disposable texture to the old mesh or its display-only clone.""")
once("  signalEdited();se356UVPreviewSchedule();\n  status('UV optimization applied",
     "  const selected=selection;signalEdited();if(selected&&partById(selected))select(selected);se356UVPreviewSchedule();\n  status('UV optimization applied")
once(" finally{for(const p of prepared)p.map?.dispose();se557Busy=false;}"," finally{se557Busy=false;}")

# No mutation to sealed source; this file is injected by the existing delivery transform.
s+='\n'+Path('scripts/ovh_uv_layout_v11_558.js').read_text()+'\n'
if sys.argv[1]=='qa':
    s+=Path('scripts/ovh_uv_functional_fixture_v11_558.js').read_text()+'\n'
else:
    assert sys.argv[1]=='clean'
p.write_text(s)
