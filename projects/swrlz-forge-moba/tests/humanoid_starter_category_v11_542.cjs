#!/usr/bin/env node
'use strict';
// §E v11.542 regression: test actual assembled Projects category classifier,
// not a separate imitation. Prevent new model labels from hiding in Games.
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const file=process.argv[2];
assert.ok(file,'Pass the fully assembled index.html as the first argument');
const html=fs.readFileSync(file,'utf8');
const id='robotic-humanoid-mannequin';
const cardTag='<button class="project-card den" data-project-template="'+id+'">';
assert.equal(html.split(cardTag).length-1,1,'One and only one mannequin starter button');
assert.ok(html.includes('<strong>Futuristic Humanoid · UV-Ready Hands</strong>'));
const tag='STARTER MODEL · ONE BODY · RELAXED PAINT-READY UVS';
assert.ok(html.includes('<span class="template-tag">'+tag+'</span>'));
assert.ok(html.includes("'robotic-humanoid-mannequin':['Futuristic Humanoid · UV-Ready Hands','model-atelier','model-atelier']"),
    'VR index must use the same model identity and current name');
const start=html.indexOf('const gameIds=new Set([');
const end=html.indexOf(' function cardIn(node){',start);
assert.ok(start>0&&end>start,'Cannot locate live native Projects category classifier');
const js=html.slice(start,end);
const modelCard=vm.runInNewContext('(()=>{'+js+';return modelCard;})()',{}, {timeout:1500});
function card(template,label){
 return {dataset:{projectTemplate:template},
   querySelector:()=>label===null?null:{textContent:label}};
}
assert.equal(modelCard(card(id,tag)),true,'Mannequin is a model starter');
assert.equal(modelCard(card(id,'')),true,'Mannequin ID remains recognized without UI label');
assert.equal(modelCard(card('blank-vr-hands','STARTER GAME')),false,'Game templates remain games');
assert.equal(modelCard(card('plain-hand-base','STARTER MODEL')),true,'Existing model categories preserved');
console.log('SE541_HUMANOID_STARTER_MODEL_VISIBLE',JSON.stringify({
  template:id,modelTab:'se236StarterModels',hasCorrectLabel:true,
  modelIdRecognized:true,gameCategoryUnaffected:true}));
