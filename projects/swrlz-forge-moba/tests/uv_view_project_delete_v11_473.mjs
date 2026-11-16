import assert from 'node:assert/strict';
import fs from 'node:fs';
const html=fs.readFileSync(process.argv[2],'utf8');
const expected=[
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_473_FOLDING_WORKSPACE',
 'SE471_PROJECT_DELETE_CONFIRM_START',
 'SE471_PROJECT_DELETE_STYLES_START',
 "window.SWYRL_ENGINE_VIEW_READABILITY_455?.choose?.('shaded')",
 "window.SWYRL_ENGINE_MODEL_VIEW?.setMode?.('shaded')",
 "const bound=!!selectedMesh()?.material?.map;",
 "if(current.uvPaintPNG&&!selectedMesh()?.material?.map)renderParts();",
 "const tx=db.transaction(['projects','metadata'],'readwrite')",
 "data.delete(id);meta.delete(id)",
 "record.updatedAt&&saved.updatedAt!==record.updatedAt",
 "rpc('cloud.delete',{projectId:id,expectedRevision:record.revision})",
 "receipt?.ok!==true||receipt.projectId!==id||receipt.deletedRevision!==record.revision",
 "dialog.showModal();cancel.focus()",
 "removeDefault(source,record.id);",
 "se184ProjectCard=function(record,source)",
 "window.SWYRL_ENGINE_PROJECT_DELETE_471",
 "new CustomEvent('swrlz:account-project-deleted'"
];
for(const token of expected)assert(html.includes(token),'Missing UV or project delete contract '+token);
const imp=html.slice(html.indexOf('/* SE471_UV_IMPORT_DISPLAY_START */'),
 html.indexOf('/* SE471_UV_IMPORT_DISPLAY_END */'));
assert(imp.includes('const result=await se471UVImportBase.apply(this,arguments);'));
assert(imp.includes('current.uvPaintPNG===before'),'Do not switch view if import failed');
assert(imp.indexOf('const result=await')<imp.indexOf("window.SWYRL_ENGINE_VIEW_READABILITY_455?.choose?.('shaded')"),'Material view change must follow a successful native import');
const cardStart=html.indexOf('/* SE471_PROJECT_DELETE_CONFIRM_START */');
const cardEnd=html.indexOf('/* SE471_PROJECT_DELETE_CONFIRM_END */');
const deletion=html.slice(cardStart,cardEnd);
assert(deletion.includes("const receipt=source==='local'?await deleteLocal(record):await deleteCloud(record);"));
assert(deletion.includes("if(cloudBusy)throw Error("),'Protect against concurrent account changes');
assert(!deletion.includes('deleteDatabase('),'Do not delete the full project library');
assert(!deletion.includes('fetch(CHAT_ORIGIN'),'Account deletion must only use authenticated Chat iframe');
assert(deletion.includes("This action cannot be undone."),'Show destructive impact in confirmation');
assert(deletion.includes('if(selectionIsActive('),'Guard active projects');
console.log('SE471_UV_DISPLAY_PROJECT_DELETE_PASS: native material mode, one atomic local record, cloud revision receipt, confirmation and default safety');
