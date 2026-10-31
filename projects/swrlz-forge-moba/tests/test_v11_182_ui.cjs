const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.join(__dirname,'..');
const js=fs.readFileSync(path.join(root,'runtime/engine_professional_ui_v11_182.js'),'utf8');
const css=fs.readFileSync(path.join(root,'runtime/engine_professional_ui_v11_182.css'),'utf8');
assert.match(css,/#projectHub\.project-hub\.show/);
assert.match(css,/z-index:2147483000!important/);
assert.match(css,/dialog\[open\]:modal/);
assert.match(css,/#st141LevelBar\.st141-levelbar/);
assert.match(css,/#modelAtelierPanel/);
assert.match(css,/\.app>\.topbar/);
assert.match(css,/\.app>\.workspace/);
assert.match(css,/\.se179-dialog/);
assert.match(css,/#seChatAccountPanel/);
assert.match(css,/prefers-reduced-motion/);
assert.doesNotMatch(js,/(?:\.click\(|requestSession|setAnimationLoop|appendChild|insertBefore|eval\()/);
const rect=(left,top,width,height)=>({left,top,width,height,right:left+width,bottom:top+height});
const els={
 '.app > .topbar':rect(0,0,390,48),
 '.app > .workspace > .viewport-wrap':rect(0,48,390,692),
 '#st141LevelBar':rect(4,54,370,54),
 '.viewport-wrap > .mobile-tabs':rect(4,119,230,45),
 '#projectHub':rect(0,0,390,740),
 '#projectHub .project-window':rect(7,7,376,726),
 '.se179-dialog':rect(5,5,380,730)
};
const sandbox={innerWidth:390,innerHeight:740,
 window:{},document:{querySelector(sel){const r=els[sel];if(!r)return null;
  return {id:sel,hidden:false,classList:{contains(x){return x==='show'}},
   getBoundingClientRect(){return r},clientWidth:r.width,clientHeight:r.height,
   scrollWidth:r.width,scrollHeight:r.height};}},
 getComputedStyle(){return {display:'block',visibility:'visible',opacity:'1',position:'fixed',zIndex:'2',overflowX:'auto',overflowY:'auto'}},
 Object,Math,Number
};
vm.createContext(sandbox);vm.runInContext(js,sandbox);
const a=sandbox.window.SWYRL_ENGINE_LAYOUT.audit();
assert.equal(a.ok,true,JSON.stringify(a.issues));assert.equal(a.rects.projectWindow.right,383);
els['.viewport-wrap > .mobile-tabs']=rect(4,90,230,45);
const bad=sandbox.window.SWYRL_ENGINE_LAYOUT.audit();
assert.equal(bad.ok,false);assert.equal(bad.issues[0].kind,'collision');
console.log('SE_V11_182_UI_FOCUSED_TESTS_PASS');
