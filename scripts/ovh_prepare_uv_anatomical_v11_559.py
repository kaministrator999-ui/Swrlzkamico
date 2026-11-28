#!/usr/bin/env python3
"""Experimental branch only: layer AI-friendly layout on the verified v11.558 repair."""
from pathlib import Path
import runpy,sys
sys.argv=['scripts/ovh_prepare_uv_functional.py','clean']
runpy.run_path(sys.argv[0],run_name='__main__')
root=Path('candidate-source/projects/swrlz-forge-moba/runtime')
p=root/'uv_auto_unwrap_v11_555.js';s=p.read_text()
def once(old,new):
 global s
 assert s.count(old)==1,old
 s=s.replace(old,new,1)
once('async function se557Prepare(t,core){','async function se557Prepare(t,core,layout="compact"){')
once(' const result=core.optimizeExistingUV(mesh,{resolution:2048,padding:8});',' const result=layout==="anatomical"?core.optimizeAnatomicalUV559(mesh,{resolution:2048,padding:8}):core.optimizeExistingUV(mesh,{resolution:2048,padding:8});')
once('async function se557Optimize(all=false){','async function se557Optimize(all=false,layout="compact"){')
once('await se557Prepare(t,core)','await se557Prepare(t,core,layout)')
once("confirm('Apply verified UV improvement to '","confirm((layout==='anatomical'?'Apply AI anatomical layout (may reduce atlas coverage for readability) to ':'Apply verified UV improvement to ')")
s+='\n'+Path('scripts/ovh_uv_paint_guide_v11_559.js').read_text()+'\n';p.write_text(s)
core=root/'uv_lscm_core_v11_555.mjs'
core.write_text(core.read_text()+'\n'+Path('scripts/ovh_uv_anatomical_v11_559.mjs').read_text()+'''
export function optimizeAnatomicalUV559(mesh,options={}){
 const before=se557Audit(mesh);
 if(before.degenerate||before.negativeWinding||before.positiveAreaOverlapPairs)throw Error('Existing UVs must pass the exact triangle audit');
 const r=anatomicalUV559(mesh,options),after=se557Audit(r);
 if(after.degenerate||after.negativeWinding||after.positiveAreaOverlapPairs)throw Error('Anatomical atlas failed exact triangle audit');
 return {...r,report:{...r.report,before,after,geometryChanged:false,seamsChanged:false}};
}
''')
