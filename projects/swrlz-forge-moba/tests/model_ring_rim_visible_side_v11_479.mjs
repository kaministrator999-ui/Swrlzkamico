import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../runtime/',import.meta.url);
const src=fs.readFileSync(new URL('model_ring_rim_visibility_v11_479.js',root),'utf8');
const css=fs.readFileSync(new URL('model_ring_rim_visibility_v11_479.css',root),'utf8');
const patch=fs.readFileSync(new URL('../patches/v11_479_rim_visible_side.py',import.meta.url),'utf8');
new vm.Script(src);
const unit=src.split('/* SE479_RIM_KERNEL_START */')[1].split('/* SE479_RIM_KERNEL_END */')[0];
const context=vm.createContext({console,Math,Set,Array,Object,Number});
vm.runInContext(unit+'\nthis.kernel=se479ProjectedRim;',context);
const kernel=context.kernel;
const clean=v=>JSON.parse(JSON.stringify(v));
// Projected top rectangle plus bottom vertices at the SAME screen positions.
// The pure ring returns a connected screen rim. Occlusion pruning happens in
// the owning 3D view controller; no fake 2D depth inference is permitted.
const square=[[-1,-1],[1,-1],[1,1],[-1,1],[-1,-1],[1,-1],[1,1],[-1,1],[0,0]];
const edges=[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],
 [0,4],[1,5],[2,6],[3,7],[0,8],[1,8],[2,8],[3,8]];
const outline=kernel.choose(square,edges,0,[0,0],'outline');
assert(outline.ok);assert(outline.vertexSlots.includes(0),'Rim click must be selected');
assert(!outline.vertexSlots.includes(8),'Center must not be part of outline');
assert(outline.vertexSlots.length>=4,'Ring must expand beyond tapped point');
const fill=kernel.choose(square,edges,0,[0,0],'fill');
assert(fill.ok);assert(fill.vertexSlots.includes(0));assert(fill.vertexSlots.includes(8));
assert(fill.vertexSlots.length>outline.vertexSlots.length,'Filled ring includes interior');
const separated=kernel.choose([[0,1],[1,0],[0,-1],[-1,0],[0,1]],[[0,1],[1,2],[2,3],[3,0]],0,[0,0],'outline');
assert(separated.ok);assert(!separated.vertexSlots.includes(4),
 'Identical projected point in an unconnected island must not join');
assert.equal(kernel.choose(square,edges,-1,[0,0],'outline').ok,false);
for(const token of [
 'const originalChoose=atelierComponentChoose',
 "if(frontOnly&&!isVisible(mesh,slot))",
 'new THREE.Raycaster','intersectObject(mesh,false)[0]',
 'originalRegionPick.apply(this,arguments)',
 'atelierComponentOverlayBuild=function(...args)',
 'child.material.depthTest=!!frontOnly',
 'setCenterMode','setFrontOnly','materialVertices',
 'id=\'se479CenterToggle\'','Set Ring Center: OFF',
 'Material + Vertices','Visible Side Only',
 "window.SWYRL_ENGINE_RIM_VISIBILITY_479=Object.freeze"
])assert(src.includes(token),'Missing rim/occlusion source '+token);
assert(css.includes('#se479CenterToggle'));
assert(css.includes('#se479VisibleSideOnly'));
for(const token of [
 "if(window.SWYRL_ENGINE_RIM_VISIBILITY_479?.inspect?.()?.centerMode)",
 'SE479_RIM_VISIBILITY_STYLES_END','V11_479_RIM_VISIBLE_SIDE'
])assert(patch.includes(token),'Missing assembled patch '+token);
console.log('SE479_RIM_STATIC_PASS: rim-first connected group, fill, center toggle, occlusion guard, view UI');
