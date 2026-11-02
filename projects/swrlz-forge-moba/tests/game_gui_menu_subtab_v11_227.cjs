#!/usr/bin/env node
'use strict';
// Focused §E GUI/Menu unit checks. Does not launch Chromium, VR or deployment.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'runtime/game_gui_menu_subtab_v11_227.js'),'utf8');
const ctx={
 console,Math,Date,structuredClone,setTimeout,
 currentProject:{name:'Fixture',canonicalId:'fixture',kind:'sheep-tag'},
 playing:false,simulating:false,stSession:false,
 seLevels:{active:'menu',root:'fixture',playingMenu:false,records:new Map()},
 seLevelsCurrent(){return ctx.seLevels.records.get(ctx.seLevels.active);},
 seLevelsOwns(){return true;},
 se143ViewportHost(){return null;},
 beginTransaction(){ctx.transactions++},commitTransaction(){ctx.commits++},
 transactions:0,commits:0,toast(message){ctx.toasts.push(message)},toasts:[],
 projectData(){return {project:{name:ctx.currentProject.name},scene:{actors:[]}}},
 loadProject(data){ctx.currentProject={name:data.project.name,kind:'sheep-tag'};return true;},
 seLevelsCapture(){const rec=ctx.seLevelsCurrent();rec.data={project:{name:ctx.currentProject.name},scene:{actors:[]}};},
 seLevelsSwitch(id){if(!ctx.seLevels.records.has(id))return false;ctx.seLevels.active=id;ctx.currentProject={name:'Fixture',kind:'sheep-tag'};return true;},
 stLoadStarter(){return true;},seLevelsRefresh(){},seLevelsEnsureUI(){},
 beginPlay(){ctx.playing=true;return true;},beginSimulate(){ctx.simulating=true;return true;},
 stopSession(){ctx.playing=false;ctx.simulating=false;return true;},
 seLevelsPlayMenu(){ctx.seLevels.playingMenu=true;return true;},
 seLevelsStopMenu(){ctx.seLevels.playingMenu=false;return true;},
 document:{readyState:'loading',addEventListener(){},querySelector(){return null;}},
 window:{addEventListener(){}}
};
ctx.seLevels.records.set('menu',{id:'menu',role:'menu',data:{project:{name:'Fixture'},scene:{actors:[]}}});
ctx.seLevels.records.set('game',{id:'game',role:'game',data:{project:{name:'Fixture'},scene:{actors:[]}}});
vm.createContext(ctx);
vm.runInContext(source,ctx,{filename:'game_gui_menu_subtab_v11_227.js'});
const api=ctx.window.SWYRL_ENGINE_GUI_STUDIO;
assert.ok(api);
assert.equal(api.create('button'),true);
assert.equal(ctx.currentProject.guiStudio.schema,'swyrl-gui-studio-v1');
const id=ctx.currentProject.guiStudio.items[0].id;
assert.equal(api.edit(id,{name:'Build',text:'Construct',action:'next',x:95,width:100,inPlay:false}),true);
const item=ctx.currentProject.guiStudio.items[0];
assert.equal(item.name,'Build');assert.equal(item.action,'next');
assert.equal(item.inPlay,false);assert.equal(item.x,95);
assert.equal(api.toggleEditor(id),false); // initial toggle hides only the editor preview
assert.equal(api.inspect().hidden.length,1);
api.showAll();assert.equal(api.inspect().hidden.length,0);
const serialized=ctx.projectData();
assert.equal(serialized.project.guiStudio.items[0].text,'Construct');
ctx.seLevelsCapture();
assert.equal(ctx.seLevels.records.get('menu').data.project.guiStudio.items[0].name,'Build');
assert.equal(ctx.seLevelsSwitch('game'),true);
assert.equal(api.inspect().count,0);
assert.equal(ctx.seLevelsSwitch('menu'),true);
assert.equal(api.inspect().count,1);
assert.equal(api.inspect().project.startsWith('Fixture:'),true);
// Imported project metadata is bounded. Never evaluate HTML/script as markup.
ctx.loadProject({project:{name:'External',guiStudio:{
 schema:'swyrl-gui-studio-v1',items:[{
 id:'safe',kind:'label',name:'Safe',text:'<img src=x onerror=alert(1)>',
 x:4,y:10,width:90,height:15,foreground:'#ffffff',background:'#000000',
 action:'none',inPlay:true
 }]}},scene:{actors:[]}});
assert.equal(ctx.currentProject.guiStudio.items[0].text,'<img src=x onerror=alert(1)>');
assert.equal(api.create('script'),false);
ctx.playing=true;assert.equal(api.create('panel'),false);ctx.playing=false;
assert.ok(ctx.transactions>=2&&ctx.transactions===ctx.commits);
console.log('PASS: author/edit/editor-only eye/play flag/projectData/level snapshots/schema/Play guard');
