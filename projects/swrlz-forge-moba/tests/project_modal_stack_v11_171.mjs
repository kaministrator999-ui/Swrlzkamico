// Focused regression for the Sheep Tag menu appearing above the Projects dialog.
import assert from 'node:assert/strict';
import fs from 'node:fs';
const root='projects/swrlz-forge-moba/';
const css=fs.readFileSync(root+'runtime/project_hub_layer_v11_171.css','utf8');
const menu=fs.readFileSync(root+'runtime/engine_canvas_overlay_host_v11_143.css','utf8');
const oldHub=fs.readFileSync(root+'patches/v5_projects.py','utf8');
const tabs=fs.readFileSync(root+'runtime/project_hub_my_projects_v11_170.js','utf8');
assert.match(menu,/st141RuntimeMenu\.st141-menu-ui/);
assert.match(menu,/z-index:3900/);
assert.match(oldHub,/\.project-hub\{[^}]*z-index:30/);
const m=css.match(/#projectHub\.project-hub\.show\s*\{([^}]+)\}/);
assert(m,'modal layer rule must target only the OPEN hub');
assert.match(m[1],/position:\s*fixed\s*!important/);
assert.match(m[1],/inset:\s*0\s*!important/);
const z=Number(m[1].match(/z-index:\s*(\d+)\s*!important/)?.[1]);
assert(z>9703&&z<2147482200,'Projects outranks all native sheep menu/HUD overlays but not Chat');
assert(!/st141RuntimeMenu|st140MainMenu|sheepTagHUD/.test(m[0]),'never mutate the game menu itself');
assert(tabs.includes("se170Select('starter')")&&tabs.includes("se170Refresh()"),'starter and account tabs remain');
if(process.env.SE171_ASSEMBLED_HTML){
 const html=fs.readFileSync(process.env.SE171_ASSEMBLED_HTML,'utf8');
 assert(html.includes('se171-project-hub-layer'));
 assert(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_171_PROJECT_MODAL_PRIORITY'));
 assert(html.includes('se170Install'));
 assert(html.includes('st141RuntimeMenu'));
 assert.equal((html.match(/id="se171-project-hub-layer"/g)||[]).length,1);
}
console.log('SE171_PROJECT_MODAL_STACKING_PASS z='+z);
