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
 'banner.visible=sculpt','Direction · Falloff · Radius · Strength','controllerFollowMenu:true'])
 assert(source.includes(token),'Missing native scoped behavior: '+token);
assert(patch.includes("['sculpt-push','Push / Pull']"),'Unified signed sculpt operation must be preserved');
for(const token of ['SE530_VR_CONTINUOUS_GIZMO_AND_CONTROLLER_PALETTE_END',
 "['sculpt-push','Push / Pull']", 'V11_531_QUEST_MENU_GIZMO_ACCOUNT',
 "window.SWRLZ_FORGE_BUILD={version:'v11.531'"])
 assert(html.includes(token),'Not published in assembled release: '+token);
assert(html.includes('SE529_NATIVE_PROJECT_ACCOUNT_SAVE_START'),'Prior account project path was lost');

const fresh=fs.readFileSync(path.join(root,'runtime/model_vr_quest_interactions_v11_531.js'),'utf8');
const freshPatch=fs.readFileSync(path.join(root,'patches/v11_531_quest_menu_gizmo_account.py'),'utf8');
for(const token of [
 'Follow controller TRANSLATION, not wrist roll/pitch/yaw',
 'root.lookAt(face)',
 "root.scale.setScalar(.86)",
 "stats.capturedFrames++",
 "state.total+step*fine",
 "se350Tools().updateGroup",
 "params.position.set(0,-.505,.093)",
 "if(banner)banner.visible=false"
])assert(fresh.includes(token),'v531 VR source missing '+token);
assert(freshPatch.includes("se175Transition=source!=='cloud'"),'Cloud transition lock regression');
assert(freshPatch.includes('Account project list failed:'),'Account error masking regression');
assert(html.includes('SE531_QUEST_MENU_GIZMO_ACCOUNT_END'),'v531 layer not assembled');
console.log('SE531_QUEST_MENU_GIZMO_ACCOUNT_STATIC_CHECK_PASS');
