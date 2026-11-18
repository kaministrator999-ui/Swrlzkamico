const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
const source=fs.readFileSync(path.resolve(__dirname,'../runtime/model_uv_touch_resize_v11_502.js'),'utf8');
const attrs={},button={textContent:'',title:'',setAttribute:(key,val)=>{attrs[key]=val}};
const style={left:'180px',top:'120px',width:'280px',height:'250px'};
let saves=0;
const popup={
 hidden:false,style,
 querySelector:id=>id==='#se502UVMax'?button:null,
 classList:{toggle:()=>{},add:()=>{},remove:()=>{}},
 getBoundingClientRect(){return {
  left:Number.parseFloat(this.style.left),top:Number.parseFloat(this.style.top),
  width:Number.parseFloat(this.style.width),height:Number.parseFloat(this.style.height)
 }}
};
const bounds={left:6,top:6,right:394,bottom:740};
const context={popup,window:{visualViewport:null},document:{},
 safeBounds:()=>bounds,se473Clamp:(x,l,h)=>Math.max(l,Math.min(h,x)),
 se473RememberWindow:()=>{saves++;},fitWindow:()=>{},
 Math,Number,JSON};
vm.createContext(context);
vm.runInContext(source+'\nglobalThis.uv502={se502CalculateResize,se502ToggleMax,se502ApplyBox,se502Bounds,se502UpdateMaxButton};',context);
const uv=context.uv502;
assert.equal(uv.se502CalculateResize({left:180,top:120,width:280,height:250},'w',-80,0).left,100);
assert.equal(uv.se502CalculateResize({left:100,top:120,width:280,height:250},'e',400,0).width,294);
const right=uv.se502CalculateResize({left:180,top:120,width:280,height:250},'sw',-80,140);
assert.equal(right.left,100);assert.equal(right.width,360);
assert.equal(right.height,390);
uv.se502ToggleMax();
assert.equal(popup.style.width,'388px');
assert.equal(popup.style.height,'734px');
assert.equal(attrs['aria-pressed'],'true');
uv.se502ToggleMax();
assert.equal(popup.style.width,'280px');
assert.equal(popup.style.height,'250px');
assert.equal(popup.style.left,'114px'); // restored box is clamped to available screen
assert.equal(saves,1);
assert.equal(attrs['aria-pressed'],'false');
uv.se502ApplyBox(-200,-300,900,1500);
assert.equal(popup.style.left,'6px');
assert.equal(popup.style.top,'6px');
assert.equal(popup.style.width,'388px');
assert.equal(popup.style.height,'734px');
assert.ok(source.includes('pointermove'));
assert.ok(source.includes("['n','s','e','w','ne','nw','se','sw']"));
console.log('SE502_UV_POPUP_RESIZE_OK');
