#!/usr/bin/env node
'use strict';
// Inspect the actual generated WebXR source, then execute the Draw availability
// predicate from that source rather than reproducing its decisions here.
const assert=require('node:assert/strict'),fs=require('node:fs');
const html=fs.readFileSync(process.argv[2],'utf8');
function section(a,b){const i=html.indexOf(a),j=html.indexOf(b,i+a.length);
 assert(i>=0&&j>i,'Missing compiled source '+a);return html.slice(i,j);}
const stage=section('/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END');
const surface=section('/* SE350_MODEL_VR_SURFACE_START','/* SE350_MODEL_VR_SURFACE_END');
const xr=section('/* SE340_MODEL_VR_WORKSPACE_START','/* SE340_MODEL_VR_WORKSPACE_END');
const native=section('/* SE360_MODEL_VR_UI_START','/* SE360_MODEL_VR_UI_END');
const drawLine=stage.split('\n').find(x=>x.trim().startsWith('draw:[['));
assert(drawLine,'Draw category must exist in native three-stage rail');
const actions=[...drawLine.matchAll(/\['([^']+)','([^']+)'\]/g)].map(m=>[m[1],m[2]]);
assert.deepEqual(actions,[['draw','Draw Outline'],['draw-finish','Make Face'],
 ['extrude','Thicken Outline'],['draw-clear','Discard Outline']]);
assert(!drawLine.includes("'undo'")&&!drawLine.includes("'redo'"));
assert(stage.includes("['undo','Undo'],['redo','Redo']"),'Global project history must stay');
assert(stage.includes("['create-pouch','Hip Pouch']"),'Earlier Create cleanup must stay');
assert(stage.includes('SE527_DRAW_STATE')&&stage.includes('se527Disabled=disabled'));
assert(stage.includes("if(category==='draw'&&!drawEnabled(secondary.action))return false;"),
 'Disabled Draw action cannot dispatch via controller');
assert(stage.includes("category==='draw'?false:true"),'Draw must not open duplicate controls');
const a=stage.indexOf('function drawEnabled(action){'),b=stage.indexOf('function paintRow(item){',a);
assert(a>=0&&b>a,'Extract real Draw eligibility code');
const code=stage.slice(a,b);
function allowed(state,category,action){
 return Function('lastState','category',code+'\nreturn drawEnabled;')(state,category)(action);
}
const fresh={drawGestureActive:false,drawPointCount:0,canExtrudeOutline:false};
assert(allowed(fresh,'draw','draw'));
for(const op of ['draw-finish','extrude','draw-clear']) assert(!allowed(fresh,'draw',op),op+' unavailable initially');
assert(!allowed({...fresh,drawGestureActive:true,drawPointCount:2},'draw','draw-finish'));
assert(allowed({...fresh,drawGestureActive:true,drawPointCount:3},'draw','draw-finish'));
assert(allowed({...fresh,drawGestureActive:true,drawPointCount:1},'draw','draw-clear'));
assert(!allowed({...fresh,drawPointCount:5},'draw','draw-clear'),'Discard requires live draw gesture');
assert(allowed({...fresh,canExtrudeOutline:true},'draw','extrude'));
assert(allowed(fresh,'create-menu','extrude'),'Other labs are unaffected');
assert(surface.includes('SE527_DRAW_OUTLINE_ELIGIBILITY'));
assert(surface.includes('function canExtrude(id)'));
assert(surface.includes('outlineEligibility(part,mesh).ok'),'Availability must check real topology');
assert(surface.includes('const eligibility=outlineEligibility(g.part,g.mesh)'),'Extrude must use identical validation');
const eligibility=surface.slice(surface.indexOf('function outlineEligibility('),surface.indexOf('function canExtrude('));
assert(!eligibility.includes('checkpoint(')&&!eligibility.includes('signalEdited(')&&!eligibility.includes('capture('),
 'Eligibility must not commit, begin preview or select');
for(const reason of ['EXTRUDE_REQUIRES_NATIVE_OUTLINE_FACE','EXTRUDE_REQUIRES_BIND_POSE',
 'EXTRUDE_REQUIRES_UNDEFORMED_OUTLINE','EXTRUDE_REQUIRES_SINGLE_OPEN_OUTLINE',
 'EXTRUDE_REQUIRES_PLANAR_OUTLINE'])assert(eligibility.includes(reason),'Lost native extrusion constraint '+reason);
assert(xr.includes("drawGestureActive:s.gesture?.kind==='draw'"));
assert(xr.includes("canExtrudeOutline:selectedIds.size===1&&se350Surface().canExtrude(native.selectedId)"));
assert(xr.includes("if(s.gesture||se350Tools().selection().ids.length!==1||!se350Surface().canExtrude(id))return false"));
assert(xr.includes("if(s.gesture?.kind==='draw'&&s.gesture.points.length>=3)"));
assert(xr.includes("if(s.gesture?.kind!=='draw'||!s.gesture.points.length)return false"));
assert(surface.includes('function extrudeBegin(id)')&&surface.includes('function extrudeEnd(commit')&&xr.includes("s.mode='extrude'"),'Existing native Grip extrusion retained');
assert(surface.includes('checkpoint(); g.part.topologyMesh = g.next'),
 'Original native extrusion checkpoint retained');
assert(native.includes("id==='extrude'?!!state.canExtrudeOutline:true"),'Native modifier state must agree');
assert(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_528_IMMERSIVE_UX_ACCOUNT_REPAIR'));
assert(html.includes('<title>§wyrl§ Engine · Maker v11.527</title>'));
console.log('SE527_DRAW_MENU_PASS: four actions; dynamic enabled states; no duplicate settings/history; single native extrusion validator');
