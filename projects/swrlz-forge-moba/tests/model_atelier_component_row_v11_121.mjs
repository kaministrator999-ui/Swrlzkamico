import assert from 'node:assert/strict';
import fs from 'node:fs';
const source=fs.readFileSync('/tmp/se-v11121.mjs','utf8');
const css=fs.readFileSync('projects/swrlz-forge-moba/runtime/model_atelier_uncovered_components_v11_121.css','utf8');
const start=source.indexOf('function atelierComponentInstall(){');
const end=source.indexOf(' atelierComponentUIRefresh();\n}',start);
assert.ok(start>=0 && end>start, 'missing native component toolbar');
const s=source.slice(start,end);
for(const token of [
 "const seComponentToolbarAnchor=panel.querySelector('#modelAtelierViewportModes');",
 "seComponentToolbarAnchor.after(row);",
 "row.classList.add('se-component-inline');",
 "else parent.append(row);",
 "row.addEventListener('click'",
 'data-component-mode="mesh"','data-component-mode="vertex"',
 'data-component-mode="edge"','data-component-mode="face"',
 'data-component-multi','data-component-tool="tap"',
 'data-component-tool="box"','data-component-tool="lasso"',
 'data-component-clear','data-component-nudge'
])assert.ok(s.includes(token),token);
assert.ok(css.includes('position:relative!important'));
assert.ok(css.includes('max-height:min(178px,30dvh)'));
assert.ok(!css.includes('pointer-events:none'));
assert.ok(!css.includes('position:fixed'));
console.log('SE_V11121_COMPONENT_ROW_BELOW_TOP_REFERENCES_PASS');

