import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const code=fs.readFileSync(root+'runtime/engine_menu_sheep_camera_v11_144.js','utf8');
const sheep=[0,1,2].map(i=>({position:{x:-4-i*4,y:0,z:6+i},visible:true}));
const cam={position:{set(x,y,z){this.x=x;this.y=y;this.z=z;}},lookAt(x,y,z){this.focus={x,y,z};},updateMatrixWorld(){}};
let active=false;
const bar={button:true,querySelector(sel){if(sel==='#se142PlayGame'&&this.button)return {remove:()=>{this.button=false;}};return null;}};
const ctx={window:{SWYRL_ENGINE_LEVELS:{status:()=>({base:true})}},
 seLevels:{bar,playingMenu:false,time:0},se142EnsureGameEntry(){throw Error('duplicate should retire')},
 seLevelsMenuTick(dt){if(active)ctx.seLevels.time+=dt;},
 seLevelsPlayMenu(){active=true;ctx.seLevels.playingMenu=true;return true;},
 seLevelsStopMenu(){active=false;ctx.seLevels.playingMenu=false;return true;},
 seLevelsMenuActors(type){return type==='st-sheep'?sheep:[];},
 seLevelsCurrent(){return {role:'menu'};},
 seLevelsMenuText(){return {orbitSeconds:60};},perspectiveCamera:cam,Math,Number};
vm.createContext(ctx);vm.runInContext(code,ctx);
assert.equal(bar.button,false,'remove level-strip duplicate Play Game');
assert.equal(ctx.window.SWYRL_ENGINE_LEVELS.status().extraLevelPlayButton,false);
ctx.seLevelsMenuTick(1);assert.equal(cam.focus,undefined,'edit mode remains static');
ctx.seLevelsPlayMenu();
const frames=[];
for(let n=0;n<480;n++){ctx.seLevelsMenuTick(.05);if(n%100===0)frames.push({...cam.focus});}
assert.ok(frames[0].x<-3&&frames[0].x>-5,'first sheep is framed');
assert.ok(frames[2].x<-6,'camera visits second sheep');
assert.ok(frames[3].x<-8,'camera visits third sheep');
assert.ok(Math.abs(cam.position.x)>0,'camera orbit updates viewpoint');
ctx.seLevelsStopMenu();
const last={...cam.focus};ctx.seLevelsMenuTick(.05);
assert.deepEqual(cam.focus,last,'no movement after Stop');
console.log('SE144_DUPLICATE_PLAY_RETIRED_SHEEP_PORTRAIT_ORBIT_EDITOR_STATIC_PASS');
