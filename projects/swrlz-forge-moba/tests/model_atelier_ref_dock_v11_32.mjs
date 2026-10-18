import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const src=fs.readFileSync(new URL('../runtime/model_atelier_reference_studio_v11_22.js',import.meta.url),'utf8');
const c=vm.createContext({console,structuredClone});vm.runInContext(src,c);
const old={x:12,y:25,open:true,collapsed:false,active:null};
const ok=v=>c.atelierRefLayoutValid(v);
assert(ok(old),'Original portable reference layouts must remain valid');
assert(ok({...old,width:255,height:380,pinned:false}));
assert(ok({...old,width:680,height:680,pinned:true}));
for(const extra of[
 {width:199},{width:681},{width:200.5},{width:Infinity},{width:'320'},
 {height:219},{height:681},{height:NaN},{height:'380'},
 {pinned:0},{pinned:'true'}
])assert(!ok({...old,...extra}),JSON.stringify(extra));
assert.equal(ok({...old,open:'yes'}),false);
const accepted=c.atelierRefReadImport({references:[],
 referenceLayout:{...old,width:320,height:460,pinned:true}});
assert.equal(accepted.referenceLayout.width,320);
assert.equal(accepted.referenceLayout.pinned,true);
assert(c.atelierRefLayoutValid(accepted.referenceLayout));
assert.notEqual(accepted.referenceLayout,old);
assert.throws(()=>c.atelierRefReadImport({
 references:[],referenceLayout:{...old,width:1,pinned:true}
}),/layout is invalid/);
console.log('V1132_REFERENCE_DOCK_LAYOUT_BACKCOMPAT_STRICT_BOUNDS_AND_IMPORT_PASS');
