import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const file=process.env.SWYRL_REPLAY_HTML||'dist/swrlz-forge-moba/index.html';
const html=readFileSync(file,'utf8');
const start=html.indexOf('// Maul-specific, read-only spectator presentation');
const end=html.indexOf('window.SWRLZ_FORGE_BUILD=',start);
assert.ok(start>=0&&end>start,'Sealed engine must contain the appended Maul/gzip modules');
const builderBoundary=html.indexOf('// MAUL_WALK_BUILDER_MODULE_BEGIN',start);
const source=html.slice(start,builderBoundary>=0?builderBoundary:end);
assert.ok(source.includes('stRunInstallCompressedUI'),'Gzip integration missing');
assert.ok(source.includes('new CompressionStream(\'gzip\')'),'Native compression missing');
assert.ok(source.includes('new DecompressionStream(\'gzip\')'),'Native decompression missing');
assert.ok(html.includes("if(run.mode==='maul'){stRunDrawMaul("),'Native spectator route missing');
assert.ok(html.includes("const extent=run.mode==='maul'?54:"),'Maul spectator framing missing');
assert.ok(html.includes("stRunInstallUI();stRunInstallCompressedUI();"),'Recorder UI not installed');
const sandbox={CompressionStream,DecompressionStream,Blob,Response,Uint8Array,console};
vm.createContext(sandbox);vm.runInContext(source,sandbox,{filename:'sealed-replay-modules.js'});
const shape=(type,pos,min,max)=>({type,id:type,position:pos,
  worldBounds:{min,max},visible:true});
const entities=[
 shape('maul-water',[0,0,0],[-51,-.36,-53],[51,-.2,53]),
 shape('maul-snowfield',[-27,0,-22],[-37,-.27,-43],[-17,-.03,-1]),
 shape('maul-cliff',[-14,0,-22],[-16,0,-40],[-12,2,-4]),
 shape('maul-maze-wall',[-26,0,-16],[-27,0,-17],[-25,2,-15]),
 shape('maul-arrow',[-22,0,-16],[-23,0,-17],[-21,2,-15]),
 shape('maul-cannon',[-20,0,-16],[-21,0,-17],[-19,2,-15]),
 shape('maul-frost',[-18,0,-16],[-19,0,-17],[-17,2,-15]),
 shape('maul-storm',[-16,0,-16],[-17,0,-17],[-15,2,-15]),
 shape('maul-creep',[-24,0,-13],[-25,0,-14],[-23,1,-12]),
 shape('maul-builder',[-30,0,-24],[-31,0,-25],[-29,2,-23]),
 shape('maul-exit',[0,0,42],[-1,0,41],[1,2,43])
];
const fills=[],texts=[];
const ctx={
 beginPath(){},moveTo(){},lineTo(){},closePath(){},fill(){fills.push(this.fillStyle);},stroke(){},
 rect(){},arc(){},fillRect(){fills.push(this.fillStyle);},strokeRect(){},fillText(s){texts.push(s);},
 set fillStyle(v){this._fillStyle=v;},get fillStyle(){return this._fillStyle;},
 set strokeStyle(v){this._strokeStyle=v;},get strokeStyle(){return this._strokeStyle;}
};
const project=p=>({x:140+p[0]*2,y:150+p[2]*1.5-p[1],d:p[2],scale:2});
sandbox.stRunDrawMaul(ctx,entities,project,360,300,'maul-cannon',{wave:30,lives:30,gold:300});
for(const color of ['#24495c','#d9eaf0','#b9d1da','#f1d179','#f18d6e','#75cce9','#c99bf8','#d75f60'])
  assert.ok(fills.includes(color),'Missing Maul material/entity layer '+color);
assert.ok(texts.some(s=>s.includes('Wave 30/30')),'Recorded wave/lives HUD missing');
assert.ok(texts.some(s=>s.includes('maul-cannon')),'Recorded selection label missing');
const sample={schema:'swyrl-editor-play-run-v1',events:[{t:0,type:'test'}],
 frames:[{t:0,patch:{}}],checkpoints:[{t:0,game:{kind:'maul'}}],
 observations:[{text:'preserved'}]};
const raw=JSON.stringify(sample);
const compressed=await new Response(new Blob([raw]).stream().pipeThrough(new CompressionStream('gzip'))).blob();
const restored=await new Response(compressed.stream().pipeThrough(new DecompressionStream('gzip'))).text();
assert.equal(restored,raw,'Lossless compressed round-trip failed');
console.log('RUN_REPLAY_QUALITY_CPU_PASS maul-colors geometry HUD selection gzip-roundtrip');
