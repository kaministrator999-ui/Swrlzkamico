#!/usr/bin/env node
// Current native three-stage menu test: list project names and dynamic updates
// Tests menu hierarchy / action targets, never copies or alters model data.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const html=fs.readFileSync(process.argv[2],'utf8');
const START='/* SE445_VR_PROGRESSIVE_TOOLS_START */',END='/* SE445_VR_PROGRESSIVE_TOOLS_END */';
const begin=html.indexOf('/* SE443_MODEL_VR_VERTICAL_DOCK_START */');
const end=html.indexOf('/* SE443_MODEL_VR_VERTICAL_DOCK_END */',begin);
assert.ok(begin>=0&&end>begin&&html.includes(START)&&html.includes(END),'Three-stage VR dock missing');
const source=html.slice(begin,end+'/* SE443_MODEL_VR_VERTICAL_DOCK_END */'.length);

class Vec {
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z});}
 set(x,y,z){Object.assign(this,{x,y,z});return this;}
}
class Group{
 constructor(){this.children=[];this.position=new Vec();this.scale=new Vec(1,1,1);this.visible=true;this.name='';this.userData={};this.parent=null;}
 add(child){child.removeFromParent?.();child.parent=this;this.children.push(child);}
 removeFromParent(){if(this.parent){this.parent.children=this.parent.children.filter(x=>x!==this);this.parent=null;}}
 updateWorldMatrix(){}
}
class Mesh extends Group{
 constructor(geometry,material){super();this.geometry=geometry;this.material=material;}
}
class CanvasTexture{dispose(){}}
class PlaneGeometry{dispose(){}}
class MeshBasicMaterial{dispose(){}}
const T={Group,Mesh,CanvasTexture,PlaneGeometry,MeshBasicMaterial,DoubleSide:2,SRGBColorSpace:'sRGB',LinearFilter:'linear'};
const canvasContext={clearRect(){},fillRect(){},strokeRect(){},fillText(){},beginPath(){},arc(){},fill(){},stroke(){},moveTo(){},lineTo(){},roundRect(){}};
const root=new Group();root.visible=true;
const nativeSurface=new Mesh();root.add(nativeSurface);
const observed=[];
const nativeUI={
 root,targets:[nativeSurface],update:state=>observed.push(state.page),hitTest:()=>null,
 press:()=>true,hover:()=>null,tick:()=>{},dispose:()=>{},
 inspect:()=>({native:true}),openWheel:()=>true,drawGuideIcon:()=>{}
};
let currentList=[['project-source-local','● On device'],['project-source-cloud','Google account'],
 ['project-source-starter','Starters'],['project-page-prev','Previous page'],
 ['project-page-next','Next page'],['project-pick-0','Sorting Hat'],['project-pick-1','Wolf Model'],
 null,null,['project-open','Open: Sorting Hat'],['project-cancel','Cancel selection']];
let started=0;
const projectBrowser={start:()=>{started++;},operations:()=>currentList};
const sandbox=vm.createContext({se517XRProjects:projectBrowser,
 se340CreateModelVRUI:()=>nativeUI,
 se340Hit:()=>null,se340Poll:()=>null,se374GizmoContact:()=>null,
 window:{},
 document:{createElement:()=>({width:0,height:0,getContext:()=>canvasContext})}
});
vm.runInContext(source,sandbox);
assert.equal(sandbox.window.SWYRL_ENGINE_MODEL_VR_PROGRESSIVE_445.defaultPanels,'primary only');
const ui=sandbox.se340CreateModelVRUI({THREE:T});
const rail=root.children.find(x=>x.name==='Model VR · far-right primary tools');
const sub=root.children.find(x=>x.name==='Model VR · operation submenu');
const detail=root.children.find(x=>x.name==='Model VR · native modifier panel');
assert(rail&&sub&&detail,'Three world-space menu tiers not present');
assert.equal(ui.inspect().submenuOpen,false);
assert.equal(ui.inspect().settingsOpen,false);
assert.equal(sub.visible,false);
assert.equal(detail.visible,false);
const find=(parent,action)=>parent.children.find(x=>x.userData?.se340Action===action&&x.visible);
const tick=()=>{for(let i=0;i<4;i++)ui.tick(.06);};
assert.equal(ui.press(find(rail,'projects')),true);
ui.update({page:'projects',projectBrowserRevision:1});tick();
assert.equal(started,1,'project list request must originate from existing Projects primary rail');
assert(find(sub,'project-source-local')&&find(sub,'project-source-cloud')&&find(sub,'project-source-starter'));
assert(find(sub,'project-pick-0')&&find(sub,'project-pick-1'));
assert(find(sub,'project-open')&&find(sub,'project-cancel'));
assert.equal(ui.press(find(sub,'project-pick-0')),true,'name is a real native Trigger target');
currentList=currentList.map(([action,label] = [])=>action==='project-pick-0'?[action,'Sorting Hat edited']:action==='project-open'?[action,'Open: Sorting Hat edited']:action?[action,label]:null);
ui.update({page:'projects',projectBrowserRevision:2});tick();
assert(find(sub,'project-pick-0')&&find(sub,'project-open'));
assert.equal(ui.press(find(rail,'projects')),true);tick();
assert.equal(ui.inspect().submenuOpen,false,'Projects category closes through original rail');
assert.equal(ui.press(find(rail,'sculpt')),true);
ui.update({page:'sculpt'});tick();
assert.equal(ui.inspect().category,'sculpt');
assert.equal(ui.inspect().submenuOpen,true);
assert.equal(ui.inspect().settingsOpen,false);
assert.equal(sub.visible,true);
assert.equal(detail.visible,false);
assert.ok(Math.abs(sub.position.x-.29)<1e-9);
assert.ok(Math.abs(rail.position.x-.51)<1e-9);
for(const op of ['sculpt-push','sculpt-smooth','sculpt-flatten','sculpt-inflate','sculpt-pinch','sculpt-translate','manual-inset','manual-extrude','manual-solidify','manual-subdivide'])
 assert(find(sub,op),'Missing sculpt subtool '+op);
assert.equal(ui.press(find(sub,'manual-extrude')),true);
ui.update({page:'manual-operation'});tick();
assert.equal(ui.inspect().settingsOpen,true);
assert.equal(ui.inspect().drawerPage,'manual-operation');
assert.equal(detail.visible,true);
assert.ok(Math.abs(detail.position.x+.16)<1e-9);
assert.equal(detail.children.includes(nativeSurface),true,'Native inspector lost from hierarchy');
assert.equal(-.16+.63/2<.29-.223/2,true,'Large inspector overlaps operation list');
assert.equal(.29+.223/2<.51-.192/2,true,'Operation list overlaps primary rail');
const closeDetail=detail.children.find(x=>x.name==='Close modifier settings');
assert.equal(ui.press(closeDetail),false);
tick();
assert.equal(ui.inspect().settingsOpen,false);
assert.equal(ui.inspect().submenuOpen,true);
assert.equal(detail.visible,false);
const closeSub=sub.children.find(x=>x.name==='Close operation list');
assert.equal(ui.press(closeSub),false);tick();
assert.equal(ui.inspect().submenuOpen,false);
assert.equal(sub.visible,false);
assert.equal(rail.visible,true);
assert.equal(ui.press(find(rail,'manual-mesh')),true);ui.update({page:'manual-mesh'});tick();
assert(find(sub,'manual-inset')&&find(sub,'manual-extrude')&&find(sub,'manual-deleteFaces'),'Native face submenu inaccessible');
assert.equal(ui.press(find(rail,'delete-selected')),true,'Permanent Delete action must stay reachable');
assert.equal(ui.inspect().settingsOpen,false);
ui.dispose();
console.log('SE517_NATIVE_PROJECT_MENU_PASS:  primary right > operations > native modifiers, independent close and no overlap');
