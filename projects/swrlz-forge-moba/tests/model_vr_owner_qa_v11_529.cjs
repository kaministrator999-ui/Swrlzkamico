#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const html=fs.readFileSync(process.argv[2],'utf8');
function section(a,b){const start=html.indexOf(a),end=html.indexOf(b,start+a.length);
 assert(start>=0&&end>start,'Missing compiled '+a);return html.slice(start,end);}
const menu=section('/* SE528_XR_PROJECT_DIALOG_START','/* SE528_XR_PROJECT_DIALOG_END');
const input=section('/* SE528_XR_RAY_AND_PARAMETER_CONTROLS_START','/* SE528_XR_RAY_AND_PARAMETER_CONTROLS_END');
const account=section('/* SE528_ACCOUNT_PROJECT_REPAIR_START','/* SE528_ACCOUNT_PROJECT_REPAIR_END');
const older=section('/* SE517_XR_PROJECT_BROWSER_START','/* SE517_XR_PROJECT_BROWSER_END');
const cloud=section('/* SE372_VR_PROJECTS_IN_CHAT_CLOSURE_START','/* SE372_VR_PROJECTS_IN_CHAT_CLOSURE_END');
const workflow=section('/* SE350_MODEL_VR_SURFACE_START','/* SE350_MODEL_VR_SURFACE_END');
const native=section('/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END');
for(const tag of ['V11_529_NATIVE_ACCOUNT_BROWSER_LIBRARY','<title>§wyrl§ Engine · Maker v11.529</title>'])
 assert(html.includes(tag),'release identity '+tag);
assert(menu.includes("const priorCreate=se340CreateModelVRUI")&&menu.includes("const ui=priorCreate(options)"));
assert(menu.includes("modal.position.set(-.205,0,.155)"),'Project dialog must have independent, sizeable world-space geometry');
assert(menu.includes("const canvas=document.createElement('canvas')")&&menu.includes("CW=1504,CH=1232"),
 'Large dialog must render with native CanvasTexture');
for(const action of ['project-source-local','project-source-cloud','project-source-starter',
 'project-pick-0','project-pick-1','project-pick-2','project-pick-3','project-page-prev',
 'project-page-next','project-open','project-refresh','project-save-local',
 'project-save-account','project-clone','project-dialog-close'])
 assert(menu.includes("'"+action+"'"),'Missing project card action '+action);
assert(menu.includes('se517XRProjects.operations()')&&menu.includes('se517XRProjects.action(id)')&&
 menu.includes('se517XRProjects.refresh()'), 'Dialog must use the existing VR project library');
assert(menu.includes("if(target?.userData?.se340Action==='projects')")&&
 menu.includes("se340XR.ui?.openProjects?.()"),'Projects category must actually open modal');
assert(menu.includes("if(se340XR.ui?.isModalOpen?.())")&&menu.includes('return false; // no model selection/sculpt behind a modal'),
 'Modal must block background edits');
assert(menu.includes("if(action==='cancel'&&se340XR.ui?.isModalOpen?.())")&&
 menu.includes('closeDialog:close'), 'B cancellation must close modal safely');
assert(menu.includes("if(se340XR.ui?.isModalOpen?.())return true")&&
 menu.includes("if(se340XR.ui?.isModalOpen?.())return false"),
 'Modal must block global controller actions and grip transformations');
assert(menu.includes('SCULPT_REQUIRES_BIND_POSE')&&menu.includes('showRestPose')&&
 menu.includes('project-rest-confirm')&&menu.includes('project-rest-cancel'),
 'Push/Pull pose rejection should open confirmation');
assert(menu.includes('access.remember()')&&menu.includes('access.touched(')&&
 menu.includes('access.playing=false')&&menu.includes('rig.pose=neutral')&&
 menu.includes('access.validate?.({...rig,pose:neutral})'),
 'Rest conversion must validate, stop animation, journal and preserve original rig owner');
assert(workflow.includes('SCULPT_REQUIRES_BIND_POSE'),'Native rig guard must remain');
assert(older.includes('se517ProjectBusy')&&older.includes('se340Bridge().releaseRoot()')&&
 older.includes('bridge.borrowRoot(se340XR.pivot)'), 'Native VR project switching must remain a single borrowed root');
assert(input.includes('se390UpdatePose=function(g,pose,gain)')&&input.includes('g?.se512Trigger')&&
 input.includes('ray.intersectPlane(')&&input.includes('state.axisWorld')&&
 input.includes('se350Tools().updateGroup('),'Ray must drive original native group updates');
assert(input.includes('se372Constrain(g,translation,rotation)')&&
 input.includes('se372GuideUpdate(g,translation,rotation,scale)'), 'Existing gizmo constraints/guide retained');
assert(input.includes("buttons?.[6]")&&input.includes("se340ModelXRAction('palette',left)"),
 'Left Quest Menu should toggle existing menu when exposed');
assert(html.includes("['palette','tap:X'"),'Fallback X menu binding remains for OS-reserved Menu button');
assert(input.includes('se528Parameter:true')&&input.includes('const pairs=new Map()')&&
 input.includes('t.visible=false')&&input.includes('const vals=groups.map('),
 'Paired native +/- inputs must become contextual grouped toolbar with live values');
assert(input.includes('const result=priorUpdate(next)')&&menu.includes('const result=priorUpdate(next)'),
 'Existing native UI updates must be retained');
assert(account.includes('const se528PriorGetProjectId=getProjectId')&&
 account.includes('projectIds.set(currentProject,currentProject.instanceId)'),
 'Project identity must stay stable when saved locally');
assert(account.includes("prior.startsWith('cloud:')")&&account.includes('se528PriorLoadCloud.call(this)'),
 'Account loading must normalize prefixed picker IDs through the same importer');
assert(account.includes("const ok=await saveCloud()===true")&&
 account.includes("if(!ok)")&&account.includes('se371Display('),
 'Account saving must require durable acknowledgement and show failures');
assert(account.includes("document.addEventListener('click',()=>requestAnimationFrame(se528InstallAccountSave),true)"),
 'My Projects save-to-account must appear after lazy panel mount');
assert(account.includes("chat.onclick=()=>void se528SaveAccount()")&&
 account.includes("button.onclick=()=>void se528SaveAccount()"),
 'Both Chat and My Projects must use one save-to-account path');
assert(cloud.includes('saveAccount:se372VRSaveAccount'), 'Existing XR account-save facade remains');
assert(native.includes("['undo','Undo'],['redo','Redo']"),'Global Undo/Redo must remain');
console.log('SE528_OWNER_QA_PASS: card dialog, pose confirmation, ray transform, parameter groups, left Menu and shared account save wiring');
