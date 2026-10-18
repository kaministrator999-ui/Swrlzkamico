/* v284 unit tests: contract admission, arithmetic, no eval and DOM-only rendering.
 * Does not claim browser / live HF behavior.
 */
"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const path=require("node:path");
const fs=require("node:fs");
const widget=require("../hf_space/chat/§wyrlz/assets/rich-widgets-v284.js");
const common=(kind,data)=>({contract:"swrlz-widget-v1",version:1,kind,title:"Test",data});
test("explicit typed v1 only; missing and bad contracts rejected",()=>{
 assert.equal(widget.normalize({contract:"x",version:1,kind:"model-3d",data:{shape:"cube"}}),null);
 assert.equal(widget.normalize(common("arbitrary-html",{text:"<script>alert(1)</script>"})),null);
 assert.equal(widget.normalize(common("model-3d",{shape:"remote-mesh",src:"https://untrusted.example/a.glb"})),null);
 assert.equal(widget.normalize({...common("math-graph",{series:[{type:"polynomial",coefficients:[1]}]}),version:2}),null);
});
test("comparison bounded options/metrics, no invented winners",()=>{
 const input=common("comparison",{items:[
  {name:"A",values:{speed:12,weight:5}},
  {name:"B",values:{speed:24,weight:8}},
  {name:"C",values:{speed:0,weight:3}},
  {name:"D",values:{}},{name:"E",values:{speed:9000}}
 ],metrics:[{key:"speed",higherIsBetter:true},{key:"weight",higherIsBetter:false},{key:"not/valid"}],note:"Illustrative"});
 const a=widget.normalize(input);
 assert.equal(a.data.items.length,4);
 assert.equal(a.data.metrics.length,2);
 assert.equal(a.data.items[0].values.speed,12);
 assert.equal(widget.normalize(common("comparison",{items:[{name:"Only one"}],metrics:[{key:"x"}]})),null);
});
test("polynomial, sine and safe bounded input",()=>{
 const a=widget.normalize(common("math-graph",{series:[{type:"polynomial",coefficients:[-4,0,1]},{type:"sine",amplitude:2,frequency:1,phase:0,offset:3}],domain:[-8,8],range:[-9,10]}));
 assert.equal(widget.evaluate(a.data.series[0],3),5);
 assert.equal(widget.evaluate(a.data.series[1],Math.PI/2),5);
 assert.equal(widget.equation(a.data.series[0]),"y = x² − 4");
 assert.equal(widget.normalize(common("math-graph",{series:[{type:"polynomial",coefficients:[1,Infinity]}]})),null);
 assert.equal(widget.normalize(common("math-graph",{series:[{type:"javascript",code:"process.exit(1)"}]})),null);
 assert.equal(widget.normalize(common("math-graph",{series:[{type:"polynomial",coefficients:[1]}],domain:[2,2]})),null);
});
test("3D geometry is bounded, deterministic and rotates",()=>{
 for(const shape of ["cube","sphere","torus","pyramid"]){
  const valid=widget.normalize(common("model-3d",{shape,pitch:200,yaw:0}));
  assert.equal(valid.data.shape,shape);
  assert.ok(valid.data.pitch<=Math.PI/2);
  const mesh=widget.mesh(shape);
  assert.ok(mesh.vertices.length>0&&mesh.vertices.length<400,shape);
  assert.ok(mesh.edges.length>0&&mesh.edges.length<800,shape);
  for(const [a,b] of mesh.edges)assert.ok(a>=0&&b>=0&&a<mesh.vertices.length&&b<mesh.vertices.length);
 }
 assert.notDeepEqual(widget.project([1,1,1],0,0),widget.project([1,1,1],Math.PI/2,.4));
});
test("renderer builds using textContent and accessible interactive controls",()=>{
 const nodes=[];
 global.document={
  createElement(tag){
   const node={tagName:tag,childNodes:[],style:{},dataset:{},
    append(...children){this.childNodes.push(...children);},
    appendChild(child){this.childNodes.push(child);return child;},
    setAttribute(name,val){this[name]=val;},
    addEventListener(name,fn){this["on"+name]=fn;},
    getBoundingClientRect(){return {width:720,height:375};},
    getContext(tag){return tag==="2d"?{
     beginPath(){},moveTo(){},lineTo(){},stroke(){},fillRect(){},clearRect(){},
     set fillStyle(v){},set strokeStyle(v){},set lineWidth(v){}
    }:null;}
   };
   nodes.push(node);return node;
  }
 };
 for(const x of [
   common("comparison",{items:[{name:"<svg onload=alert(1)>",values:{x:2}},{name:"B",values:{x:3}}],metrics:[{key:"x"}]}),
   common("math-graph",{series:[{type:"polynomial",coefficients:[-4,0,1]}]}),
   common("model-3d",{shape:"cube"})
 ]){
   const node=global.document.createElement("section");
   assert.equal(widget.render(node,x),true);
   assert.ok(node.childNodes.length>0);
 }
 const unsafe=nodes.some(n=>Object.prototype.hasOwnProperty.call(n,"innerHTML"));
 assert.equal(unsafe,false,"Renderer never assigns untrusted HTML");
 const canvases=nodes.filter(n=>n.tagName==="canvas");
 assert.equal(canvases.length,2);
 assert.ok(canvases.every(n=>typeof n.onkeydown==="function"&&typeof n.onpointerdown==="function"));
 delete global.document;
});
test("integration owns only one canonical rendering slot",()=>{
 const src=fs.readFileSync(path.resolve(__dirname,"../chat/§wyrlz/index.html"),"utf8");
 const station=fs.readFileSync(path.resolve(__dirname,"../hf_space/station.py"),"utf8");
 const lab=fs.readFileSync(path.resolve(__dirname,"../hf_space/chat/§wyrlz/assets/widget-atelier-v284.html"),"utf8");
 assert.match(src,/SwrlzRichWidgetsV284\?\.render\(card,widget\)/);
 assert.match(station,/rich-widgets-v284\.js/);
 assert.match(station,/rich-widgets-v284\.css/);
 assert.match(lab,/invented sample data/);
 assert.equal((station.match(/rich-widgets-v284\.js/g)||[]).length,1);
 const moduleSource=fs.readFileSync(path.resolve(__dirname,"../hf_space/chat/§wyrlz/assets/rich-widgets-v284.js"),"utf8");
 assert.doesNotMatch(moduleSource,/\beval\s*\(|new Function\s*\(/);
 assert.doesNotMatch(moduleSource,/\.innerHTML\s*=/);
});
