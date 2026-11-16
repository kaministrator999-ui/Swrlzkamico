import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
const required=[
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_472_FULL_RES_TEXTURES',
 'se336SlidePreview(part);\n  signalEdited();',
 'material.map.updateMatrix();',
 "root.querySelectorAll('.se336-uv-actions button')",
 "if(!se336SlideState().enabled)se336SlideToggle();",
 "window.SWYRL_ENGINE_ASSET_LIBRARY?.loadAccountAsset?.('modeler',id)",
 "window.SWYRL_ENGINE_WORKSPACES?.modelerActive?.()",
 "saved.textContent='Save to account'",
 'const se470Working=new Map();',
 'remote?.id||null,remote?.revision||0',
 "if(result.durable!==true||!result.project?.id||",
 "se470Working.set(type,{source:se470Source(type),id:record.id,remote:link});",
 'function se470SavedCloudProjects(rows)',
 "function se470VisibleCloud(list)",
 'loadAccountAsset,read,inspect',
 "window.dispatchEvent(new Event('swrlz:model-blank'))"
];
for(const t of required)assert(html.includes(t),'Missing v11.470 behavior: '+t);
const uv=html.slice(html.indexOf('function se336SlideSet(offset)'),html.indexOf('function se336SlideToggle()'));
assert(uv.indexOf('se336SlidePreview(part)')<uv.indexOf('signalEdited()'),'Nudge must update live material before rebuild');
const save=html.slice(html.indexOf(' async function save(type,cloud){'),html.indexOf(' async function loadAccountAsset(',html.indexOf(' async function save(type,cloud){')));
assert(!save.includes('persist(type,[record,...existing]'),'Cloud saves must not automatically make duplicate local entries');
assert(save.includes("if(cloud){")&&save.includes('persist(type,[record,...rows.filter(row=>row.id!==record.id)]'),'Local save is explicit and updates by ID');
assert(save.includes('api().save(payload.buffer,')&&save.includes('remote?.revision||0'),'Cloud save updates existing remote revisions');
const fnStart=html.indexOf('function se470SavedCloudProjects(rows){');
const fnEnd=html.indexOf('function se184RenderCloudProjects(rows){',fnStart);
const visible=vm.runInNewContext(html.slice(fnStart,fnEnd)+'\nse470SavedCloudProjects');
const rows=[
 {id:'older',name:'§E Asset · [Model] UFO',revision:1,updatedAt:'2026-01-01'},
 {id:'newer',name:'§E Asset · [Model] UFO',revision:2,updatedAt:'2026-02-01'},
 {id:'other',name:'§E Asset · [Model] Spaceship',revision:1,updatedAt:'2026-01-05'},
 {id:'game',name:'Sheep Tag',revision:2}
];
const shown=visible(rows);
assert.equal(shown.length,3);
assert(shown.some(x=>x.id==='newer')&&!shown.some(x=>x.id==='older'));
assert(shown.some(x=>x.id==='game'),'Existing game projects must remain visible');
const scope=html.slice(html.indexOf('function se371Run(mode)'),html.indexOf('function se371Buttons(host,scope)'));
assert(scope.includes("await api.save('modeler',true)"),'Model Save must explicitly write a model asset');
console.log('SE470_UV_MODEL_SAVE_PASS: immediate placement, explicit account save, revisions and legacy duplicate gallery');
