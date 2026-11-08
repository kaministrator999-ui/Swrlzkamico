#!/usr/bin/env node
'use strict';
const fs=require('fs'),assert=require('assert'),path=require('path'),vm=require('vm');
const base=path.resolve(__dirname,'..','runtime');
const w=fs.readFileSync(path.join(base,'model_vr_workspace_v11_341.js'),'utf8');
const u=fs.readFileSync(path.join(base,'model_studio_vr_ui_v11_341.js'),'utf8');
new vm.Script(w);new vm.Script(u);
for(const key of ['record.nextHoverAt=now+55','cast.ray.intersectsBox','s.frameEntries=bridge.projection().meshes','se340Pressed(record,3)','se340XR.pitch+dy*dt'])assert(w.includes(key),key);
assert(!w.includes('turnLatched'),'right stick must not snap turn');
assert(u.includes('Orbit X/Y · press+Y zoom'));
console.log('MODEL_VR_341_SOURCE_CHECKS_PASS');
