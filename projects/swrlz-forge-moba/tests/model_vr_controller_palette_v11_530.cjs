// Candidate static/regression checks. Physical Meta Quest acceptance remains separate.
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'runtime/model_vr_controller_palette_v11_530.js'),'utf8');
const patch=fs.readFileSync(path.join(root,'patches/v11_530_quest_gizmo_controller_menu.py'),'utf8');
const html=fs.readFileSync(process.argv[2],'utf8');
for(const token of ['se390UpdatePose=function(g,pose,gain)','g.se530Continuous',
 'if(state.worldAxis)','state.translation.add(localDelta','if(g.mode===\'move\')',
 'root.position.copy(pose.position).add(location)','root.scale.setScalar(.94)',
 "se372MenuDragStart=function(){return false;}","activeSculptOperation",
 'target.visible=false;ui.targets.splice(i,1)','parameters','controllerFollowMenu:true'])
 assert(source.includes(token),'Missing native scoped behavior: '+token);
assert(patch.includes("['sculpt-indent','Indent / Lower']"),'No inward sculpt operation');
for(const token of ['SE530_VR_CONTINUOUS_GIZMO_AND_CONTROLLER_PALETTE_END',
 "['sculpt-indent','Indent / Lower']", 'V11_530_QUEST_GIZMO_CONTROLLER_MENU',
 "window.SWRLZ_FORGE_BUILD={version:'v11.530'"])
 assert(html.includes(token),'Not published in assembled release: '+token);
assert(html.includes('SE529_NATIVE_PROJECT_ACCOUNT_SAVE_START'),'Prior account project path was lost');
console.log('SE530_CONTROLLER_MENU_STATIC_CHECK_PASS');
