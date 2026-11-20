#!/usr/bin/env node
'use strict';
// Source-backed regression for the real compiled immersive 3-stage UI.
const fs=require('node:fs');
const assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2],'utf8');
const between=(begin,end)=>{
 const a=html.indexOf(begin),b=html.indexOf(end,a+begin.length);
 assert(a>=0&&b>a,'Missing section: '+begin);
 return html.slice(a,b);
};
const menu=between('/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END');
const native=between('/* SE360_MODEL_VR_UI_START','/* SE360_MODEL_VR_UI_END');
const entries=line=>[...line.matchAll(/\['([^']+)','([^']+)'\]/g)].map(x=>[x[1],x[2]]);
const findRow=(source,label)=>{
 const lines=source.split('\n');
 const row=lines.find(x=>x.trim().startsWith(label));
 assert(row,'Missing '+label);
 return row;
};
assert(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_530_QUEST_GIZMO_CONTROLLER_MENU'));
assert(menu.includes('SE522_SCULPT_BRUSH_MENU'));
assert(native.includes('SE522_SCULPT_SETTINGS'));
assert.deepEqual(entries(findRow(menu,'sculpt:[[')),[
 ['sculpt-push','Push / Pull'],['sculpt-translate','Translate'],['sculpt-inflate','Inflate'],
 ['sculpt-pinch','Pinch'],['sculpt-flatten','Flatten'],['sculpt-smooth','Smooth']
],'Sculpt operation rail must contain exactly six ordered surface brushes');
const face=findRow(menu,"'manual-mesh':[[");
for(const command of ['manual-convert','manual-pick','manual-inset','manual-extrude',
                      'manual-solidify','manual-deleteFaces','manual-subdivide','manual-repairNormals'])
 assert(face.includes("'"+command+"'"),'Face Tools lost '+command);
assert(native.includes("['sculpt-direction','Pull Out']"));
assert(!native.includes("['sculpt-indent','Indent']"));
assert(!native.includes("['exit','Exit VR']"));
assert(html.includes("const SE350_BRUSHES=['push','smooth','flatten','inflate','pinch','translate'];"));
assert(html.includes("s.sculptDirection=s.sculptDirection==='in'?'out':'in'"));
assert(html.includes("s.sculptTool==='push'&&s.sculptDirection==='in'?-Math.abs(s.brushStrength):s.brushStrength"));
assert(html.includes("se340XR.sculptTool==='push'&&se340XR.sculptDirection==='in'?-Math.abs(se340XR.brushStrength):se340XR.brushStrength"));
assert(html.includes("sculptDirection:s.sculptDirection"));
const impl=html.slice(html.indexOf('function atelierSculptApplyOperator'),html.indexOf('function atelierSculptApplyOperator')+5500);
assert(impl.includes("operation==='inflate'")&&impl.includes("normal.getX(i)")&&impl.includes("move.copy(axis).multiplyScalar(amount*weight)"),'Inflate per-vertex normal differs from axial Push');
const nativeSculpt=native.match(/^\s*sculpt:\[\n([\s\S]*?)^\s*\],/m);
assert(nativeSculpt,'Missing native Sculpt settings');
const modifiers=entries(nativeSculpt[1]);
console.log('SE522_NATIVE_SCULPT_MODIFIERS',JSON.stringify(modifiers));
for(const [id,label] of [
 ['brush-radius-minus','Radius −'],['brush-radius-plus','Radius +'],
 ['brush-strength-minus','Strength −'],['brush-strength-plus','Strength +']
])assert(modifiers.some(row=>row[0]===id&&row[1]===label),'Missing Sculpt setting '+id);
for(const id of ['sculpt-push','sculpt-translate','sculpt-inflate','sculpt-pinch','sculpt-flatten','sculpt-smooth'])
 assert(!modifiers.some(row=>row[0]===id),'Duplicate brush selector in settings: '+id);
for(const id of ['sculpt-direction','sculpt-falloff'])
 assert(modifiers.some(row=>row[0]===id),'Previously available Sculpt modifier lost: '+id);
assert(menu.includes("['manual-mesh','Face Tools','manual-mesh']"),
 'Contextual Modeling Lab must keep Face Tools reachable');
assert(menu.includes("['labs','Labs','labs']")&&menu.includes("['projects','Projects','projects']"),
 'Do not lose permanent lab/project navigation');
assert(menu.includes("['undo','Undo'],['redo','Redo']"),
 'Do not lose persistent Undo/Redo actions');
console.log('SE523_SCULPT_DIRECTION_PASS: six ordered brushes; native radius/strength; Face Tools retained');
