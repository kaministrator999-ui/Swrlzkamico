import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const src=fs.readFileSync(new URL('../runtime/model_atelier_reference_studio_v11_22.js',import.meta.url),'utf8');
const c=vm.createContext({console,structuredClone});vm.runInContext(src,c);
const r=id=>({id,name:id,data:'data:image/png;base64,AAAA',angle:id==='front'?'front':'right',
 zoom:1,offsetX:0,offsetY:0,rotation:0,opacity:.87,mirror:false,visible:true});
const refs=[r('front'),r('profile')];
const layout={x:12,y:35,open:true,collapsed:false,active:'front',compareId:'profile',
 width:390,height:480,pinned:true};
assert(c.atelierRefLayoutValid(layout));
const imported=c.atelierRefReadImport({references:refs,referenceLayout:layout});
assert.equal(imported.referenceLayout.compareId,'profile');
assert.notEqual(imported.referenceLayout,layout);
assert.deepEqual(JSON.parse(JSON.stringify(imported.references)),refs);
assert(c.atelierRefLayoutValid({...layout,compareId:null}));
assert(c.atelierRefLayoutValid({...layout,compareId:undefined}));
for(const bad of [{compareId:123},{compareId:''+'x'.repeat(73)},
 {compareId:{}},{compareId:Infinity}])
 assert(!c.atelierRefLayoutValid({...layout,...bad}));
assert.throws(()=>c.atelierRefReadImport({references:refs,
 referenceLayout:{...layout,compareId:'missing'}}),/comparison/);
assert.throws(()=>c.atelierRefReadImport({references:refs,
 referenceLayout:{...layout,compareId:'front'}}),/comparison/);
const legacy={x:12,y:25,open:true,collapsed:false,active:'front'};
assert(c.atelierRefLayoutValid(legacy));
assert(c.atelierRefReadImport({references:refs,referenceLayout:legacy}));
console.log('V1145_REFERENCE_GRID_TWO_INDEPENDENT_NATIVE_IMAGES_COMPARISON_SCHEMA_PASS');
