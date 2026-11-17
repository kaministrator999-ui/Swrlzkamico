import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../runtime/',import.meta.url);
const source=fs.readFileSync(new URL('model_textured_editable_copy_v11_481.js',root),'utf8');
const patch=fs.readFileSync(new URL('../patches/v11_481_textured_editable_copy.py',import.meta.url),'utf8');
new vm.Script(source);
for(const token of [
 'const MAX_VERTICES=9000,MAX_FACES=16000',
 'g.getAttribute(\'skinIndex\')',
 'g.getAttribute(\'color\')',
 "partById(selection)",
 "p.refinementLayers?.some",
 "sourceKeys=['uvPaintPNG','uvPaintOffset','uvPaintRepeat'",
 "values.join(',')",
 'new Set(triangle).size<3',
 'se430MeshOps.audit(data)',
 "checkpoint();",
 "p.se481SourceHidden=true;p.se481WorkId=id",
 "document.parts.push(copy)",
 "copy[key]=structuredClone(p[key])",
 "atelierComponentMode='vertex'",
 'window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481=Object.freeze({',
 'const baseRender=renderParts',
 'child.visible=false',
 'function switchSource()',
 'function inspectFidelity()',
 'positionDifferences',
 'uvDifferences',
 'sameUVRepeat'
])assert(source.includes(token),'Missing UV safety/working copy '+token);
for(const token of [
 "const ordinary=new Set",
 "'uvPaintPNG','uvPaintOffset','uvPaintRepeat'",
 "'se481SourceId','se481WorkHidden'",
 "window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481?.inspect?.()",
 "window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481.prepare()",
 'Make textured editable copy',
 "const already=part?.kind==='topologyMesh'||!!part?.se481WorkId",
 "V11_481_TEXTURED_EDITABLE_COPY",
 "No UV reprojection"
])assert(patch.includes(token),'Missing native entry bridge '+token);
console.log('SE481_STATIC_PASS: exact UV seam retention, immutable source, painted metadata, native topology bridge, UI mode.');
