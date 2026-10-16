import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source=readFileSync(process.argv[2],'utf8');
const start=source.indexOf('function atelierValidPoseFrame('),end=source.indexOf('function atelierPoseCamera()',start);
assert.ok(start>=0&&end>start,'Generated native frame validator is missing');
const ctx={MODEL_ATELIER_LIMIT:1200,structuredClone};vm.createContext(ctx);vm.runInContext(source.slice(start,end),ctx);
const validate=vm.runInContext('atelierValidatedFrameStore',ctx);
for(const neutral of [undefined,null]){
 const once=validate({poseFrames:[],poseNeutral:neutral}),twice=validate(once);
 assert.equal(once.poseNeutral,null);assert.deepEqual(JSON.parse(JSON.stringify(twice)),{poseFrames:[],poseNeutral:null});
}
const frame={poses:[{id:'head',position:[0,4,0],rotation:[0,0,0],scale:[1,1,1]}]};
assert.deepEqual(JSON.parse(JSON.stringify(validate({poseNeutral:frame}).poseNeutral)),frame);
for(const bad of [false,0,'null',{}, {poses:[{...frame.poses[0],scale:[0,1,1]}]}])assert.throws(()=>validate({poseNeutral:bad}),/Invalid neutral pose/);
assert.throws(()=>validate({poseFrames:null}),/Invalid saved pose frames/);
console.log('NATIVE_REPEATED_MODEL_IMPORT_EMPTY_NEUTRAL_AND_INVALID_FRAME_REJECTION_PASS');
