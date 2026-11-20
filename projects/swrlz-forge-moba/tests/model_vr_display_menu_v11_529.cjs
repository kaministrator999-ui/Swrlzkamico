#!/usr/bin/env node
'use strict';
// Verify the emitted, real 3-stage WebXR UI, not a duplicate mock interface.
const fs=require('node:fs'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2],'utf8');
const slice=(a,b)=>{const i=html.indexOf(a),j=html.indexOf(b,i+a.length);
 assert(i>=0&&j>i,'Missing compiled section '+a);return html.slice(i,j);};
const stage=slice('/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END');
const ui=slice('/* SE360_MODEL_VR_UI_START','/* SE360_MODEL_VR_UI_END');
const tools=slice('/* SE345_MODEL_VR_DISPLAY_MODES_START','/* SE345_MODEL_VR_DISPLAY_MODES_END');
const pairs=s=>[...s.matchAll(/\['([^']+)','([^']+)'\]/g)].map(m=>[m[1],m[2]]);
assert(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_529_NATIVE_ACCOUNT_BROWSER_LIBRARY'));
assert(stage.includes("['views','Display','views']"),'Display still belongs in permanent top rail');
const group=stage.split('\n').find(x=>x.trim().startsWith('views:[['));
assert(group,'Missing Display middle rail');
assert.deepEqual(pairs(group),[['views-angles','View Angles'],['views-render','Render Modes']],
 'Display groups must be exactly View Angles and Render Modes');
assert(stage.includes("SE525_DISPLAY_DIVIDER"),'Compiled visible divider missing');
assert(stage.includes("paintMesh(submenu,'Display · angles / render separator'"),'Separator must be native world-space geometry');
assert(stage.includes(".200,.006,0,.246"),'Divider must be located between groups');
assert(stage.includes("item.mesh.position.y=category==='views'&&i===1?.212:category==='create-menu'&&i>=4?.280-i*.049-.027:.280-i*.049"),'Both Display and Create rows must leave their respective physical separator gaps');
assert(stage.includes("displayDivider.mesh.visible=category==='views'&&submenuOpen"),
 'Divider must only appear when Display is opened');
assert(stage.includes("if(action==='views-angles')return 'cameras'"));
assert(stage.includes("if(action==='views-render')return 'views'"));
assert(html.includes("if(action==='views-angles'||action==='views-render')"));
assert(html.includes("s.page=action==='views-angles'?'cameras':'views'"),
 'Both groups need to open their own native settings panel');
const getPage=(name)=>{const found=ui.match(new RegExp('^  '+name+':\\[\\n([\\s\\S]*?)^  \\],','m'));
 assert(found,'Missing native '+name+' settings');return pairs(found[1]);};
assert.deepEqual(getPage('cameras'),[
 ['view-front','Front'],['view-back','Back'],['view-left','Left'],
 ['view-right','Right'],['view-top','Top'],['view-bottom','Bottom'],
 ['view-iso','Isometric']
],'All seven original camera angles must be preserved');
assert.deepEqual(getPage('views'),[
 ['display-textured','Textured'],['display-solid','Solid'],['display-wireframe','Wireframe'],
 ['display-xray','X-Ray'],['display-normals','Normals']
],'Render modes need Textured, Solid, Wireframe, X-Ray, Normals with no nav duplicates');
assert(ui.includes("views:['Render modes','PREVIEW ONLY · ORIGINAL MATERIALS RETAINED']"));
assert(ui.includes("cameras:['View angles','MODEL ORIENTATION · RIGHT STICK TO ORBIT']"));
assert(tools.includes("const SE345_DISPLAY_OPTIONS=['textured','solid','wireframe','xray','normals']"));
assert(tools.includes("s.displayMode==='textured'?original:se345DisplayMaterial(s.displayMode)"),
 'Preview modes must never alter saved material values');
assert(tools.includes('for(const [mesh,material] of s.displayOriginals||[])mesh.material=material'),
 'VR exit must restore original model materials');
assert(html.includes('function se344SetView(view){')&&html.includes("if(view==='orbit'){s.viewMode='orbit'"),
 'Keep original camera presets and right-stick orbit');
for(const cmd of ['views-angles','views-render'])assert(!getPage('views').some(row=>row[0]===cmd)&&
 !getPage('cameras').some(row=>row[0]===cmd),'No duplicated group controls');
assert(stage.includes("['labs','Labs','labs']")&&stage.includes("['undo','Undo'],['redo','Redo']"),
 'Other permanent menu controls and edit journal must survive');
console.log('SE525_DISPLAY_MENU_PASS: separated angle/render groups, physical divider, 7 angles, 5 safe render modes');
