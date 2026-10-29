import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=p=>fs.readFileSync(new URL('../runtime/'+p,import.meta.url),'utf8');
const ctx=vm.createContext({console,stage:{clientWidth:1000,clientHeight:900}});
vm.runInContext(source('model_atelier_floating_references_v11_57.js')+'\n'+
 source('model_atelier_reference_studio_v11_22.js'),ctx);
const v={open:true,pinned:false,x:40,y:100,width:290,height:280};
const ref=(layout=v)=>({id:'photo1',name:'face',
 data:'data:image/png;base64,AAAA',angle:'front',
 zoom:1,offsetX:0,offsetY:0,rotation:0,mirror:false,opacity:.9,visible:true,
 floatWindow:layout});
assert(ctx.atelierFloatingLayoutValid(v));
assert(ctx.atelierRefValid([ref()]));
assert(ctx.atelierRefValid([{...ref(),floatWindow:undefined}]),'prior image refs remain valid');
for(const bad of [{...v,x:-1},{...v,y:6001},{...v,width:100},
 {...v,height:601},{...v,pinned:'no'},{...v,unknown:'data'},
 {...v,open:1},{...v,x:Infinity},null]){
 assert(!ctx.atelierFloatingLayoutValid(bad),'reject invalid native per-image layout');
 assert(!ctx.atelierRefValid([ref(bad)]),'invalid layouts cannot enter native JSON');
}
assert(!ctx.atelierRefValid([ref(),{...ref(),id:'photo1'}]),'no duplicate refs');
const first=ctx.atelierFloatingDefault(0),second=ctx.atelierFloatingDefault(1);
assert(ctx.atelierFloatingLayoutValid(first)&&ctx.atelierFloatingLayoutValid(second));
assert(first.x>500,'default desktop reference not covering upper-left dock tabs');
assert(second.x<first.x&&second.y<first.y);
assert.deepEqual(JSON.parse(JSON.stringify(ref())),ref(),'native floating image survives Save/Load');
console.log('V1157_INDEPENDENT_PHOTO_WINDOW_LAYOUT_SCHEMA_DEFAULT_PORTABLE_PASS');
