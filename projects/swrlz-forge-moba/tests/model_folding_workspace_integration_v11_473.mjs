import assert from 'node:assert/strict';
import fs from 'node:fs';
const html=fs.readFileSync(process.argv[2],'utf8');
const required=[
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_473_FOLDING_WORKSPACE',
 'SE473_UV_SCREEN_DRAG_START',
 'SE473_MODEL_TOOL_RAIL_FOLD_START',
 'SE473_MODEL_FOLDING_WORKSPACE_STYLES_START',
 "const se473UVWindowKey='swyrl.engine.modeler.uv-window.v1'",
 "const v=window.visualViewport;",
 'const b=safeBounds();',
 "if(!open&&isOpen())se473RememberWindow();",
 "se473RememberWindow();",
 'start.moved||layout()!=='desktop'',
 "state[what][flag]=!state[what][flag]",
 'Math.hypot(e.clientX-start.x,e.clientY-start.y)<9',
 "e.key==='Enter'||e.key===' '",
 "node.title='Tap to collapse / restore · Drag to resize'",
 'SE472_NATIVE_TEXTURE_RESOLUTION_START',
 'SE471_UV_FINE_FIT_START',
 'SE469_UV_SHAPE_FIT_START',
 'modelAtelierToolRail',
 'se473RailFold',
 '--se320-rail:42px!important',
 "display:block!important;pointer-events:auto!important"
];
for(const token of required)assert(html.includes(token),'Missing folding workspace contract '+token);
const start=html.indexOf('/* SE473_UV_SCREEN_DRAG_START */');
const end=html.indexOf('/* SE473_UV_SCREEN_DRAG_END */');
assert(end>start);
const uv=html.slice(start,end);
assert(!uv.includes("q('.atelier-scene'"),'UV must no longer be clamped to canvas');
assert(uv.includes('localStorage.setItem(se473UVWindowKey'),'UV position should persist');
const idx=html.indexOf('function dragResize(node,what,side,dir){');
const drag=html.slice(idx,html.indexOf('function addSeparator(parent,what,side,dir)',idx));
assert(drag.includes('if(!start.moved&&Math.hypot'),'Drag/tap threshold protects resizing');
assert(drag.includes('state[what][flag]=!state[what][flag]'));
assert(drag.includes("const next=start.width+(e.clientX-start.x)*dir"),'Original resize remains');
assert(drag.includes('save();window.dispatchEvent'),'Existing native pointerup saves widths and fold state');
assert(drag.includes('},true);'),'Tap is captured before native pointerup clears state');
const foldStart=html.indexOf('/* SE473_MODEL_TOOL_RAIL_FOLD_START */');
const foldEnd=html.indexOf('/* SE473_MODEL_TOOL_RAIL_FOLD_END */',foldStart);
const fold=html.slice(foldStart,foldEnd);
assert(fold.includes("rail.prepend(toggle)"),'Top handle should be part of rail');
assert(fold.includes('aria-expanded'));
assert(fold.includes("localStorage.setItem(key,collapsed?'collapsed':'expanded')"));
const cssStart=html.indexOf('/* SE473_MODEL_FOLDING_WORKSPACE_STYLES_START */');
const css=html.slice(cssStart,html.indexOf('/* SE473_MODEL_FOLDING_WORKSPACE_STYLES_END */',cssStart));
assert(css.includes('position:fixed!important;z-index:18000!important'));
assert(css.includes('data-se251-right-collapsed=true'));
assert(css.includes('button:not(#se473RailFold)'));
assert(css.includes('data-se251-layout=compact'),'Compact layouts retain rail handle');
console.log('SE473_FOLDING_WORKSPACE_INTEGRATION_PASS: free UV bounds, tap-versus-drag, saved widths, rail and viewport controls');
