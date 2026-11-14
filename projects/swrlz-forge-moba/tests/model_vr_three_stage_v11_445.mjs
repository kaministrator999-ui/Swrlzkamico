#!/usr/bin/env node
// Three-stage VR presentation test with a headless native console stub.
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
const sandbox=vm.createContext({
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
assert.equal(ui.press(find(rail,'sculpt')),true);
ui.update({page:'sculpt'});tick();
assert.equal(ui.inspect().category,'sculpt');
assert.equal(ui.inspect().submenuOpen,true);
assert.equal(ui.inspect().settingsOpen,false);
assert.equal(sub.visible,true);
assert.equal(detail.visible,false);
assert.equal(sub.position.x,.29);
assert.equal(rail.position.x,.51);
for(const op of ['sculpt-push','sculpt-smooth','sculpt-flatten','sculpt-inflate','sculpt-pinch','sculpt-translate','manual-inset','manual-extrude','manual-solidify','manual-subdivide'])
 assert(find(sub,op),'Missing sculpt subtool '+op);
assert.equal(ui.press(find(sub,'manual-extrude')),true);
ui.update({page:'manual-operation'});tick();
assert.equal(ui.inspect().settingsOpen,true);
assert.equal(ui.inspect().drawerPage,'manual-operation');
assert.equal(detail.visible,true);
assert.equal(detail.position.x,-.16);
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
console.log('§E v11.445 three-stage VR tool UI PASS: primary right > operations > native modifiers, independent close and no overlap');
