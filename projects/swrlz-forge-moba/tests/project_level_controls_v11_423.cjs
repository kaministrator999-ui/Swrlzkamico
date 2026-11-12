'use strict';
/* Focused regression for menu scroll and existing level chrome retention. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const levelSource=fs.readFileSync(path.join(root,'runtime/level_selector_recovery_v11_423.js'),'utf8');
const projectSource=fs.readFileSync(path.join(root,'runtime/project_menu_recovery_v11_423.js'),'utf8');
const css=fs.readFileSync(path.join(root,'runtime/project_menu_scroll_v11_423.css'),'utf8');
const toolbar={};
const play={parentElement:toolbar,before(node){node.parentElement=toolbar;node.nextSibling=play;}};
const stop={after(node){node.parentElement=toolbar;node.previousElementSibling=stop;}};
const viewport={parentElement:{appendChild(node){node.parentElement=this;}},appendChild(node){node.parentElement=this;}};
const bar={parentElement:null,nextSibling:null,hidden:false,isConnected:true};
const nextButton={parentElement:null,previousElementSibling:null};
const preview={parentElement:null},inspector={parentElement:null};
const level={data:{project:{name:'Existing saved level'}}};
const records=new Map([['level-1',level]]);
let nativeEnsure=0,nativeRefresh=0;
const context={
 window:{addEventListener(){}},document:{readyState:'loading',addEventListener(){}},
 queueMicrotask(fn){fn();},requestAnimationFrame(fn){fn();},
 MutationObserver:class{observe(){}disconnect(){}},
 seLevels:{bar,nextButton,preview,inspector,records,active:'level-1',root:'existing-root'},
 seLevelsOwns(){return true;},
 seLevelsEnsureUI(){nativeEnsure++;},
 seLevelsRefresh(){nativeRefresh++;},
 seLevelsHydrate(){return true;},
 $(id){return id==='playBtn'?play:id==='stopBtn'?stop:id==='viewport'?viewport:null;}
};
vm.createContext(context);
vm.runInContext(levelSource,context,{filename:'level_selector_recovery_v11_423.js'});
context.seLevelsEnsureUI();
assert.equal(nativeEnsure,1);
assert.equal(bar.parentElement,toolbar,'original level selector reattached');
assert.equal(bar.nextSibling,play,'selector restored immediately before Play');
assert.equal(nextButton.previousElementSibling,stop,'original next-level button reattached');
assert.equal(preview.parentElement,viewport,'menu preview reattached');
assert.equal(inspector.parentElement,viewport.parentElement,'inspector reattached');
context.seLevelsHydrate({});
assert.equal(level.data.project.levelProjectRoot,'existing-root','older saved level snapshot recovers root');
assert.equal(records.size,1,'no saved level replaced');
assert.equal(level.data.project.name,'Existing saved level');
context.seLevelsRefresh();
assert.equal(nativeRefresh,1);
assert.equal(context.window.SWYRL_ENGINE_LEVEL_UI_RECOVERY_423.inspect().barVisible,true);
assert.match(css,/touch-action:pan-y!important/);
assert.match(css,/overflow-y:auto!important/);
assert.match(css,/grid-template-columns:repeat\(3,minmax\(0,1fr\)\)/);
assert.match(projectSource,/se423RepairNativeProjects/);
assert.match(projectSource,/se170Select\('mine'\)/);
assert.match(projectSource,/SE423_PROJECT_MENU_RECOVERY_START/);
assert.doesNotMatch(levelSource,/setAnimationLoop\(/);
assert.doesNotMatch(projectSource,/setAnimationLoop\(/);
console.log('SE423_PROJECT_MENU_LEVEL_CONTROLS_PASS: detached level toolbar, saved level root, scroll contract, native tab actions.');
