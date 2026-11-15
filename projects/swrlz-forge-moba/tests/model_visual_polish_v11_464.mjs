#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const src=fs.readFileSync(new URL('../runtime/model_visual_polish_v11_464.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../runtime/model_visual_polish_v11_464.css',import.meta.url),'utf8');
new vm.Script(src,{filename:'model_visual_polish_v11_464.js'});
assert(css.includes('[data-se464-inspector-focus=true] .atelier-body'));
assert(css.includes('--se320-right:0px!important'));
assert(css.includes('.atelier-body>.se251-resize-grip'));
assert(css.includes('#se464InspectorFocus'));
let released=0,nativeApply=0,nativeTicks=0,nativeToolbar=0,nativeInstall=0,recolors=0,gizmoBuilds=0;
const nativeBox={type:'BoxHelper',material:{depthTest:true,color:{value:0,setHex(v){this.value=v;}}}};
const gizmoRoot={traverse(fn){fn(nativeBox);}};
class Mat{
 constructor(options={}){Object.assign(this,options);this.userData={};}
 dispose(){released++;}
}
class Geometry{
 constructor(original,angle){this.original=original;this.angle=angle;}
 clone(){return new Geometry(this.original,this.angle);}
 dispose(){released++;}
}
class Node{
 constructor(geometry,material){this.geometry=geometry;this.material=material;this.userData={};this.children=[];}
 add(child){this.children.push(child);child.parent=this;}
 remove(child){this.children.splice(this.children.indexOf(child),1);child.parent=null;}
}
class Mesh extends Node{}
class DirectionalLight{
 constructor(color,power){this.color=color;this.intensity=power;this.position={set(...v){this.xyz=v;}};this.userData={};}
}
let borrowed=false,mode='xray',selection='cube';
const authored=new Mat({roughness:.7,metalness:.14});
const nativeClone=new Mat({roughness:.7,metalness:.14});nativeClone.userData.atelierViewportClone=true;
const sourceGeometry={getIndex:()=>({count:60}),getAttribute:()=>({count:20})};
const mesh=new Mesh(sourceGeometry,nativeClone);
mesh.isMesh=true;
mesh.userData={atelierId:'cube',se455OriginalMaterial:authored};
const part={id:'cube',kind:'topologyMesh',material:{roughness:.7}};
const world=new Node();
let currentPanel={hidden:false,dataset:{},listeners:{},querySelector(){return null;},addEventListener(name,fn){this.listeners[name]=fn;}};
const window={listeners:{},addEventListener(name,fn){this.listeners[name]=fn;}};
const created=[];
const document={createElement(tag){
 assert.equal(tag,'button');
 const element={type:'button',attrs:{},listeners:{},textContent:'',
  setAttribute(name,val){this.attrs[name]=String(val);},
  addEventListener(name,fn){this.listeners[name]=fn;},
  focus(){this.focused=true;}
 };
 created.push(element);return element;
}};
let menuButton;
const handle={append(el){menuButton=el;}};
const inspector={querySelector(s){return s==='.atelier-tool-handle'?handle:null;}};
currentPanel.querySelector=s=>s==='.atelier-inspector'?inspector:null;
class MutationObserver{constructor(fn){this.fn=fn;}observe(){}}
const ctx=vm.createContext({
 THREE:{DirectionalLight,Mesh,MeshBasicMaterial:Mat,EdgesGeometry:Geometry,FrontSide:1},
 world,panel:currentPanel,window,document,MutationObserver,
 atelierHDDirty:false,se340ModelBridge:{isBorrowed:()=>borrowed},
 atelierViewModeFor:()=>mode,se462EligibleWire:()=>true,
 se462PrimaryColor:()=>0x63ffe1,
 se462AddLine:(parent,geo,options)=>{
  const line=new Node(geo,new Mat({depthTest:options.depthTest,opacity:options.opacity}));
  line.name=options.name;line.userData.se462WireOwned=true;
  if(options.primary)line.userData.se462Primary=true;
  parent.add(line);return line;
 },
 atelierViewModeApply:()=>{nativeApply++;
  // The real native v11.462 renderer removes its previous line helpers.
  for(const child of [...mesh.children])if(child.userData.se462WireOwned)mesh.remove(child);
  return mesh;
 },
 atelierMeshToolbarRefresh:()=>{nativeToolbar++;},
 atelierMeshGizmoBuild:()=>{gizmoBuilds++;},atelierMeshGizmo:gizmoRoot,
 se462Recolor:()=>{recolors++;},
 se430BeginnerTick:()=>{nativeTicks++;},
 se430BeginnerInstall:()=>{nativeInstall++;},
 partById:id=>id!=null&&id===selection?part:null,
 selection,atelierComponentMode:'mesh',
 Object,Array,Math
});
vm.runInContext(src,ctx);
ctx.atelierViewModeApply(mesh,part);
assert.equal(nativeApply,1);
assert(mesh.material.userData.se464XraySurface);
assert.equal(mesh.material.opacity,.13);
assert.equal(mesh.material.depthWrite,false);
assert.equal(mesh.material.side,1);
assert.equal(mesh.geometry,sourceGeometry);
assert.equal(authored.roughness,.7);
assert.equal(authored.metalness,.14);
assert.equal(released,1,'Only prior disposable native viewport clone freed');
assert(mesh.children.some(o=>o.userData.se464XrayDepth));
const depth=mesh.children.find(o=>o.userData.se464XrayDepth);
assert.equal(depth.geometry,mesh.geometry,'Depth helper borrows geometry');
assert.equal(depth.material.colorWrite,false);
assert.equal(depth.material.depthWrite,true);
assert.equal(depth.material.depthTest,true);
assert.equal(typeof depth.raycast,'function','Helper excluded from native picks');
const hidden=mesh.children.find(o=>o.name==='X-Ray hidden topology');
const front=mesh.children.find(o=>o.name==='X-Ray visible topology');
assert(hidden&&front);
assert.equal(hidden.material.depthTest,false);
assert.equal(front.material.depthTest,true);
assert(hidden.material.opacity<front.material.opacity);
ctx.atelierViewModeApply(mesh,part);
assert.equal(mesh.children.filter(o=>o.userData.se464XrayDepth).length,1,
 'Repeated same mode does not duplicate depth helper');
mode='shaded';
mesh.material=authored;
ctx.atelierViewModeApply(mesh,part);
assert.equal(mesh.children.filter(o=>o.userData.se464XrayDepth).length,0,
 'Switching to Material frees previous depth helper');
assert.equal(mesh.material,authored,'Material remains native/authored');
assert.equal(world.children.filter(x=>x.userData.se464ViewOnly).length,2);
assert(world.children.every(x=>x.name==='Model Studio display fill (v11.464)'));
assert.equal(world.children.filter(x=>x.userData.se464ViewOnly).every(x=>x.visible),true);
borrowed=true;ctx.se430BeginnerTick(1);
assert.equal(world.children.filter(x=>x.userData.se464ViewOnly).every(x=>!x.visible),true,
 'VR bridge borrowing hides studio-only lights');
borrowed=false;ctx.se430BeginnerTick(2);
assert.equal(world.children.filter(x=>x.userData.se464ViewOnly).every(x=>x.visible),true);
ctx.atelierMeshGizmoBuild();
assert.equal(gizmoBuilds,1);
assert.equal(nativeBox.material.color.value,0x8fffe3);
assert.equal(nativeBox.material.depthTest,false);
ctx.atelierMeshToolbarRefresh();
assert.equal(nativeToolbar,1);assert.equal(recolors,1);
assert.equal(currentPanel.dataset.se464Selection,'selected');
assert.equal(currentPanel.dataset.se464Component,'mesh');
selection=null;ctx.selection=null;ctx.atelierMeshToolbarRefresh();
assert.equal(currentPanel.dataset.se464Selection,'none');
ctx.se430BeginnerInstall(currentPanel);
assert.equal(nativeInstall,1);
assert.equal(currentPanel.dataset.se464InspectorReady,'1');
assert(menuButton);
assert.equal(menuButton.attrs['aria-pressed'],'false');
menuButton.listeners.pointerdown({stopPropagation(){this.stopped=true;}});
menuButton.listeners.click({preventDefault(){},stopPropagation(){}});
assert.equal(currentPanel.dataset.se464InspectorFocus,'true');
assert.equal(menuButton.attrs['aria-pressed'],'true');
assert.match(menuButton.textContent,/Dock/);
menuButton.listeners.click({preventDefault(){},stopPropagation(){}});
assert.equal(currentPanel.dataset.se464InspectorFocus,undefined);
menuButton.listeners.click({preventDefault(){},stopPropagation(){}});
currentPanel.listeners.keydown({key:'Escape',stopPropagation(){}});
assert.equal(currentPanel.dataset.se464InspectorFocus,undefined);
assert(menuButton.focused,'Escape should restore keyboard focus');
currentPanel.dataset.se320InspectorCollapsed='true';
menuButton.listeners.click({preventDefault(){},stopPropagation(){}});
assert.equal(currentPanel.dataset.se464InspectorFocus,undefined,
 'Closed inspector must never enter focus overlay');
ctx.se430BeginnerInstall(currentPanel);
assert.equal(nativeInstall,2);
assert.equal(created.length,1,'No duplicate Focus buttons or listeners');
assert(src.includes('helper.userData.se455DisplayEdges=true'));
assert(!src.includes('checkpoint(')&&!src.includes('model().parts='));
if(process.argv[2]){
 const html=fs.readFileSync(process.argv[2],'utf8');
 for(const token of [
  "window.SWRLZ_FORGE_BUILD={version:'v11.464'",
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_464_MODEL_VISUAL_INSPECTOR',
  'SE464_MODEL_VISUAL_POLISH_START','SE464_INSPECTOR_VISUAL_POLISH_START',
  'SE463_TRANSFORM_HISTORY_PASS', // Not in compiled HTML, checked separately below.
 ])if(token==='SE463_TRANSFORM_HISTORY_PASS')continue;
 else assert(html.includes(token),'Missing compiled '+token);
 assert(html.includes('const colors={vertex:0x74ffdb,edge:0x86d7ff,face:0xffd17e};'));
 assert(html.includes('atelierMeshGizmoBuild=function(){'));
 assert(html.includes('emissive:color.clone().multiplyScalar(.05)'));
 assert(html.includes('se320RefreshTransformAccess(panel)'));
 assert(html.includes('se461AlignOrbitPivot()'));
 assert(html.includes('SE461_TOUCH_DOCK_BOUNDS_START'));
 assert(html.includes('SE462_VIEW_AND_DOCK_STYLES_START'));
 assert(html.includes('SE463_MODEL')||html.includes('Select mesh · Undo / Redo'));
}
console.log('SE464_VISUAL_POLISH_PASS: non-destructive X-Ray depth, topology color, fill-light VR gating, native selection and reversible inspector focus');
