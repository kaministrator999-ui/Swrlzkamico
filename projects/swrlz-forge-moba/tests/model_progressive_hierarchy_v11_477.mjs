import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../runtime/',import.meta.url);
const hierarchy=fs.readFileSync(new URL('model_progressive_hierarchy_v11_477.js',root),'utf8');
const vertex=fs.readFileSync(new URL('model_vertex_entry_v11_477.js',root),'utf8');
const css=fs.readFileSync(new URL('model_progressive_hierarchy_v11_477.css',root),'utf8');
new vm.Script(hierarchy);new vm.Script(vertex);
for(const marker of ['TOOL_LIST','TOP_BARS','CHOOSE_TOOL','SPECIFIC_SELECTION']){
 assert(hierarchy.includes('SE477_'+marker+'_START'));
 assert(hierarchy.includes('SE477_'+marker+'_END'));
}
assert(hierarchy.includes("['extrude','Extrude']")&&hierarchy.includes("['inset','Inset']"));
assert(!hierarchy.includes("{name:'Vertex',kind:'vertex'}"),'Vertex is selection type, not flyout operation');
for(const s of ["['vertex','Vertex']","['edge','Edge']","['face','Face']",
 "['single','Single vertex']","['ring','Vertex ring']","['fill','Filled vertex ring']",
 "['single','Single face']","['region','Face region']",
 "renderShapes()","function selectShape(shape)","nativeMode('vertex')","selectRing("])
 assert(hierarchy.includes(s)||vertex.includes(s),'Missing '+s);
assert(vertex.includes('atelierComponentOverlay'),'Overlay still native-owned');
assert(vertex.includes('se350ModelTools.select(target.id)'),'Use one actual selected mesh');
assert(vertex.includes('raycaster.intersectObjects'),'Multiple parts still use the native raycast');
assert(vertex.includes('atelierComponentPointerUp'),'Original touch selection preserved');
assert(!vertex.includes('checkpoint()'),'Selection cannot mutate source geometry/history');
assert(css.includes('#se477SelectionShapes[hidden]'),'Secondary bar hides when there is no operation');
assert(css.includes('data-se477-selection-type=vertex'));
assert(css.includes('data-se477-selection-type=face'));
console.log('SE477_HIERARCHY_STATIC_PASS: operation flyout, native vertices, contextual rows, no destructive selection');
