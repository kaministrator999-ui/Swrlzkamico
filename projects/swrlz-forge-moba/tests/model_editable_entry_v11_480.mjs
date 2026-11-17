import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../runtime/',import.meta.url);
const source=fs.readFileSync(new URL('model_editable_entry_v11_480.js',root),'utf8');
const css=fs.readFileSync(new URL('model_editable_entry_v11_480.css',root),'utf8');
const patch=fs.readFileSync(new URL('../patches/v11_480_visible_make_editable.py',import.meta.url),'utf8');
new vm.Script(source);
for(const tok of [
 "const workshop=()=>window.SWYRL_ENGINE_MODEL_WORKSHOP",
 "const progressive=()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()",
 "['Extrude','Inset'].includes(state.tool)",
 "part?.kind==='topologyMesh'",
 "native?.convert?.available",
 "s?.convert?.available",
 "window.confirm(prompt)",
 'const result=api.convert()',
 "api.setComponentMode(mode)",
 "window.SWYRL_ENGINE_VERTEX_ENTRY_477?.activate?.()",
 "button.disabled=!converting",
 "card.dataset.se480Blocked=part&&!converting?'true':'false'",
 'window.SWYRL_ENGINE_EDITABLE_ENTRY_480=Object.freeze('
])assert(source.includes(tok),'Missing native conversion safety '+tok);
assert(css.includes('>#se480EditableEntry[hidden]'));
assert(css.includes('#se480MakeEditable:disabled'));
assert(patch.includes('/* SE479_RIM_VISIBILITY_END */'));
assert(patch.includes("V11_480_EDITABLE_ENTRY"));
assert(patch.includes("Convert this mesh to editable topology before selecting a rim."));
console.log('SE480_STATIC_PASS: native guarded conversion, source protection, contextual visibility, vertex mode restoration');
