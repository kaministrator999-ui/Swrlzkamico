import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../runtime/',import.meta.url);
const source=fs.readFileSync(new URL('model_ring_vertex_highlight_v11_478.js',root),'utf8');
const height=fs.readFileSync(new URL('model_ring_height_v11_478.js',root),'utf8');
const heightCss=fs.readFileSync(new URL('model_ring_height_v11_478.css',root),'utf8');
new vm.Script(height);
for(const token of ["['Extrude','Inset']","['ring','fill']","preview?.active&&!owned",
 "preview.operation", "native?.preview?.('ringTransform'", "workshop()?.apply?.()",
 "workshop()?.cancel?.()", "ui.hidden=!choice||conflict", "window.SWYRL_ENGINE_RING_HEIGHT_478"])
 assert(height.includes(token),'Missing height control: '+token);
assert(heightCss.includes('#se478RingHeightSlider[hidden]'));
const patch=fs.readFileSync(new URL('../patches/v11_478_ring_vertex_highlight.py',import.meta.url),'utf8');
new vm.Script(source);
for(const token of [
 'previousChoose=atelierComponentChoose','atelierComponentChoose=function(slot)',
 "state.shape==='ring'?'outline':state.shape==='fill'?'fill':null",
 'atelierComponentIds=[slot]','workshop()?.setRingAnchor?.()',
 'workshop()?.selectRing?.(options(mode))',
 "part?.kind!=='topologyMesh'",'se478SelectedVertices','highlightedCount'
])assert(source.includes(token),'Missing '+token);
for(const token of [
 'selectedSlots.map(i=>top.vertices[i])','Math.fround(v)*100000',
 "shape==='fill'?0xffa56a","shape==='ring'?0xffe369",
 "marker.userData.se478SelectedVertices=true"
])assert(patch.includes(token),'Missing '+token);
const ring=fs.readFileSync(new URL('model_ring_kernel_v11_466.js',root),'utf8');
assert(ring.includes("mode==='outline'?dist[i]!==steps:dist[i]<0||dist[i]>steps"),
 'Native outline and filled radius must remain graph-distance selections.');
console.log('SE478_STATIC_PASS: native ring group, all selected points, topology slot mapping, no geometry changes');
