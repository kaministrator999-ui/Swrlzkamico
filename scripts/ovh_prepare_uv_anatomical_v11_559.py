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

# SE560: visible feedback and in-panel confirmation for anatomical layout.
once(" if(se557Busy||se555Busy)return false;",
     " if(se557Busy||se555Busy){se560Feedback('Another UV operation is running.');return false;}")
once(" if(!targets.length){status('Select an editable topology mesh first');return false;}",
     " if(!targets.length){se560Feedback('Select an editable topology mesh first.');status('Select an editable topology mesh first');return false;}")
once(" se557Busy=true;const prepared=[],skipped=[];\n try{",
     """ se557Busy=true;const prepared=[],skipped=[];
 se560Feedback(layout==='anatomical'?'Preparing upright anatomical layout and preserving paint…':'Preparing UV optimization…');
 se560BusyControls(true);
 try{
  await new Promise(r=>setTimeout(r,60));""")
once("if(!prepared.length){status('No UV changes. '+skipped.join('; ').slice(0,200));return false;}",
     "if(!prepared.length){const message='No UV changes. '+skipped.join('; ').slice(0,350);se560Feedback(message);status(message);return false;}")
start=s.index("  if(!confirm((layout==='anatomical'")
end=s.index('\n',start)
line=s[start:end]
assert line.endswith('))return false;')
message=line[len('  if(!confirm('):-len('))return false;')]
s=s[:start]+"  const prompt="+message+";\n  const accepted=layout==='anatomical'?await se560Confirm(prompt):confirm(prompt);\n  if(!accepted){se560Feedback('Cancelled — UVs and paint unchanged.');return false;}"+s[end:]
once("  status('UV optimization applied to '+prepared.length",
     "  se560Feedback((layout==='anatomical'?'Applied anatomical layout. Face and chest upright; legs centered. ':'UV optimization applied. ')+summary.replace(/\\n/g,' · ')+'. Undo restores the previous layout.');\n  status('UV optimization applied to '+prepared.length")
once("}catch(e){status('UV optimization stopped: '+String(e.message||e).slice(0,220));return false;}",
     "}catch(e){const message='UV optimization stopped: '+String(e.message||e).slice(0,350);se560Feedback(message);status(message);return false;}")
once(" finally{se557Busy=false;}"," finally{se557Busy=false;se560BusyControls(false);}")

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

atlas=root/'uv_atlas_core_v11_555.mjs'
atlas.write_text(atlas.read_text()+"\nexport {optimizeAnatomicalUV559} from './uv_lscm_core_v11_555.mjs';\n")

if len(sys.argv)>0: # mode selected by dedicated QA runner; no test fixture in default build
    pass
