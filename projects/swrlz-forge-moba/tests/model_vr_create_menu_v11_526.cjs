#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2],'utf8');
function between(a,b){const i=html.indexOf(a),j=html.indexOf(b,i+a.length);
 assert(i>=0&&j>i,'Missing compiled VR section '+a);return html.slice(i,j);}
const stage=between('/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END');
const native=between('/* SE360_MODEL_VR_UI_START','/* SE360_MODEL_VR_UI_END');
const primitive=between('/* SE390_MODEL_VR_QUICK_CREATE_START','/* SE390_MODEL_VR_QUICK_CREATE_END');
const accessory=between('/* SE410_MODEL_VR_ACCESSORY_WORKSHOP_START','/* SE410_MODEL_VR_ACCESSORY_WORKSHOP_END');
const pairs=s=>[...s.matchAll(/\['([^']+)','([^']+)'\]/g)].map(m=>[m[1],m[2]]);
const createRow=stage.split('\n').find(s=>s.trim().startsWith("'create-menu':[["));
assert(createRow,'Missing native Create operation row');
assert.deepEqual(pairs(createRow),[
 ['create-box','Cube'],['create-sphere','Sphere'],['create-cylinder','Cylinder'],
 ['create-cone','Cone'],['create-pouch','Hip Pouch']
],'Create must expose five nonduplicated actions');
const drawRow=stage.split('\n').find(s=>s.trim().startsWith('draw:[['));
assert(drawRow&&pairs(drawRow).some(x=>x[0]==='draw'),'Draw must own Draw Outline');
const objectsRow=stage.split('\n').find(s=>s.trim().startsWith('objects:[['));
assert(objectsRow&&pairs(objectsRow).some(x=>x[0]==='duplicate'),'Objects must own Duplicate');
assert(stage.includes('SE526_CREATE_DIVIDER'),'Missing Create physical separator');
assert(stage.includes("paintMesh(submenu,'Create · primitives / accessories separator'"));
assert(stage.includes('.200,.006,0,.095'),'Divider needs actual world-space geometry at the gap');
assert(stage.includes("createDivider.mesh.userData.se340Block=true"),'Divider must be noninteractive');
assert(stage.includes("createDivider.mesh.visible=category==='create-menu'&&submenuOpen"),'Divider needs page-scoped visibility');
assert(stage.includes("item.mesh.position.y=category==='views'&&i===1?.212:category==='create-menu'&&i>=4?.280-i*.049-.027:.280-i*.049"),
 'Pouch needs enough physical gap for separator');
assert(stage.includes("detailsOpen=category==='inspect'?item.action==='selector-lasso':category==='create-menu'?item.action==='create-pouch':true"),
 'Only Pouch may open Create context settings');
assert(stage.includes("if(action==='create-pouch')return 'accessory'"),'Pouch must open its actual accessory settings');
assert(native.includes('SE526_CREATE_CONTEXT'));
assert(native.includes("if(['accessory-body','accessory-details','accessory-fit'].includes(id))return !!state.accessoryActive;"),'Pouch editing should be disabled until preview is valid');
assert(native.includes('  create:[],'));
const match=native.match(/^\s*accessory:\[\n([\s\S]*?)^\s*\],/m);
assert(match,'Missing pouch settings page');
assert.deepEqual(pairs(match[1]),[
 ['accessory-body','Body Shape'],['accessory-details','Flap & Details'],
 ['accessory-fit','Fit & Attach'],['accessory-material','Leather'],
 ['accessory-stitches','Stitching'],['accessory-emblem','Emblem'],
 ['accessory-reset','Reset Shape']
],'Pouch settings must be contextual, with no duplicate Create, Exit or navigation');
assert(primitive.includes("new Set(['box', 'sphere', 'cylinder', 'cone'])"),
 'Four real primitive geometries must survive');
assert(primitive.includes("function previewGeometry(handle)")&&
 primitive.includes('function commit(handle')&&
 primitive.includes('function cancel(handle')&&
 primitive.includes('checkpoint(); model().parts.push(part);'),
 'Primitive preview/cancel/commit must retain native model checkpoint');
assert(accessory.includes('function se410ArmAccessory(')&&
 accessory.includes('function se410CommitAccessory(')&&
 accessory.includes("if(action==='create-pouch')return se410ArmAccessory(record);"),
 'Pouch workflow must retain actual creation and confirmation');
assert(accessory.includes("s.mode='accessory';s.page='accessory'")&&
 accessory.includes('se410RebuildAccessory(c,params)'),
 'Pouch preview and customization must remain');
assert(native.includes("'accessory-body':[" )&&native.includes("'accessory-details':[" )&&native.includes("'accessory-fit':[" ),
 'Existing accessory subpanels must remain');
assert(stage.includes("['labs','Labs','labs']")&&
 stage.includes("['projects','Projects','projects']")&&
 stage.includes("['views','Display','views']")&&stage.includes("['undo','Undo'],['redo','Redo']"),
 'Permanent rail and model edit history must remain');
assert(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_526_CREATE_MENU_CLEANUP'));
console.log('SE526_CREATE_MENU_PASS: 5 actions, real spatial divider, no duplicated controls, native previews and pouch settings');
