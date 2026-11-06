// §E v11.297 — character-art materials and UV-aware modeling pass.
// The earlier generated UV board is an illustration, not a valid mesh UV bake.
// This renders purpose-authored 2D surface artwork directly against each existing
// part's [0..1] UVs. Keeps the original mesh/part IDs and saved scenes intact.
const se297MaterialCache=new Map();
const se297Palette={
 skin:{base:'#cca18b',rough:.87,metal:0},
 hair:{base:'#382820',rough:.78,metal:0},
 hood:{base:'#e6e2d8',rough:.89,metal:0},
 scarf:{base:'#e7e9e5',rough:.91,metal:0},
 uniform:{base:'#363e46',rough:.87,metal:.02},
 armor:{base:'#3e4c54',rough:.48,metal:.68},
 pauldron:{base:'#48525b',rough:.48,metal:.72},
 teal:{base:'#1d7479',rough:.82,metal:0},
 leather:{base:'#493328',rough:.85,metal:0},
 gloves:{base:'#e9e9e2',rough:.83,metal:0},
 boots:{base:'#39332e',rough:.8,metal:.05}
};
const se297Size=384;
function se297Canvas(){
 const canvas=document.createElement('canvas');
 canvas.width=canvas.height=se297Size;
 return canvas;
}
function se297Stroke(c,points,color,width=2,close=false){
 c.beginPath();c.moveTo(points[0][0],points[0][1]);
 for(let i=1;i<points.length;i++)c.lineTo(points[i][0],points[i][1]);
 if(close)c.closePath();
 c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';c.lineJoin='round';c.stroke();
}
function se297Curve(c,start,control1,control2,end,color,width=2){
 c.beginPath();c.moveTo(...start);c.bezierCurveTo(...control1,...control2,...end);
 c.lineWidth=width;c.strokeStyle=color;c.lineCap='round';c.stroke();
}
function se297Poly(c,pts,fill,stroke,width=1){
 c.beginPath();c.moveTo(...pts[0]);for(let i=1;i<pts.length;i++)c.lineTo(...pts[i]);
 c.closePath();if(fill){c.fillStyle=fill;c.fill();}
 if(stroke){c.strokeStyle=stroke;c.lineWidth=width;c.stroke();}
}
function se297Oval(c,x,y,rx,ry,fill,stroke,width=1){
 c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);
 if(fill){c.fillStyle=fill;c.fill();}
 if(stroke){c.lineWidth=width;c.strokeStyle=stroke;c.stroke();}
}
function se297Linear(c,points){
 const g=c.createLinearGradient(0,0,se297Size,se297Size);
 for(const [t,color] of points)g.addColorStop(t,color);
 return g;
}
function se297Star(c,x,y,r,color){
 se297Poly(c,[[x,y-r],[x+r*.2,y-r*.2],[x+r,y],[x+r*.2,y+r*.2],
 [x,y+r],[x-r*.2,y+r*.2],[x-r,y],[x-r*.2,y-r*.2]],color);
}
function se297Artwork(tile){
 const name=tile.split(':')[1],spec=se297Palette[name];if(!spec)return null;
 const canvas=se297Canvas(),c=canvas.getContext('2d',{willReadFrequently:true}),W=se297Size;
 c.fillStyle=spec.base;c.fillRect(0,0,W,W);
 // Broad material-specific shade gradients make the painted design read under
 // either direct lighting or §E's flat mobile viewport, unlike gray noise.
 c.fillStyle=se297Linear(c,[
   [0,'rgba(255,255,255,.27)'],[.35,'rgba(255,255,255,.04)'],
   [.75,'rgba(11,16,23,.12)'],[1,'rgba(0,0,0,.34)']]);
 c.fillRect(0,0,W,W);
 const gold='#d5b47b',bronze='#977147',shine='#f4d8a0',ink='#253038';
 const paintFold=(y,shift=0)=> {
  se297Curve(c,[0,y+10],[125,y-18+shift],[243,y+19-shift],[384,y-2],
   'rgba(60,71,77,.19)',9);
  se297Curve(c,[0,y+3],[125,y-26+shift],[243,y+12-shift],[384,y-10],
   'rgba(255,255,255,.48)',5);
 };
 if(name==='skin'){
   // Face front occupies u=.25..75 around cylindrical head. Skin shoulders
   // blend to neutral sides: brow at y~190, lips at y~289 (atlas pixels).
   se297Oval(c,192,204,118,178,'rgba(255,237,221,.15)');
   for(const s of [-1,1]){
     const x=192+s*49;
     se297Oval(c,x,202,25,13,'rgba(97,57,53,.24)');
     se297Oval(c,x,201,22,11,'#f1e9df','#76524d',1.8);
     se297Oval(c,x,201,10,11,'#5a8190','#2c4250',1.3);
     se297Oval(c,x,201,4,8,'#283038');
     se297Oval(c,x-3,198,3,3,'#fffdf5');
     se297Curve(c,[x-27,186],[x-8,177],[x+9,175],[x+27,184],'#53362f',4);
     se297Curve(c,[x-19,216],[x-5,222],[x+11,219],[x+19,217],'rgba(133,79,75,.25)',2);
     se297Oval(c,192+s*92,254,31,12,'rgba(205,120,110,.12)');
   }
   se297Curve(c,[186,247],[187,258],[195,261],[199,253],'rgba(135,82,77,.58)',2.4);
   se297Curve(c,[169,285],[179,291],[205,292],[217,284],'#955d59',3);
   se297Curve(c,[175,288],[186,295],[201,294],[212,289],'#c68d83',1.5);
   se297Curve(c,[168,283],[189,279],[203,279],[216,283],'rgba(87,54,53,.33)',1.2);
   se297Curve(c,[143,151],[161,140],[176,146],[183,154],'rgba(109,72,60,.2)',3);
   se297Curve(c,[203,154],[215,146],[233,141],[244,151],'rgba(109,72,60,.2)',3);
 }
 if(name==='hair'){
   // Large overlapping strands, not evenly spaced racing stripes.
   for(let i=0;i<29;i++){
     const x=(i*17+5)%392,sway=Math.sin(i*2.65)*15;
     se297Curve(c,[x-10,-20],[x+18+sway,112],[x-23+sway,232],[x+24,410],
       i%4===0?'#795643':i%3===0?'#5a3d30':'#261b18',i%5===0?17:10);
     se297Curve(c,[x-5,-15],[x+9+sway,105],[x-14+sway,249],[x+18,399],
       'rgba(223,176,120,.22)',2.4);
   }
 }
 if(name==='hood'){
   c.fillStyle='rgba(255,255,255,.22)';c.fillRect(0,0,384,384);
   for(let x=10;x<384;x+=43){
     se297Curve(c,[x+7,-20],[x-5,115],[x+12,238],[x,405],
       'rgba(120,127,128,.09)',4);
   }
   for(const x of [9,375]){
     se297Stroke(c,[[x,0],[x,384]],'#8f7955',16);
     se297Stroke(c,[[x,0],[x,384]],shine,5);
     se297Stroke(c,[[x+(x<100?12:-12),0],[x+(x<100?12:-12),384]],
       'rgba(75,54,35,.4)',3);
   }
   for(let y=28;y<384;y+=81){
     se297Star(c,39,y,9,gold);
     se297Curve(c,[48,y+22],[65,y+18],[62,y-7],[80,y-12],bronze,2.7);
     se297Curve(c,[337,y-12],[319,y-7],[319,y+18],[336,y+22],bronze,2.7);
   }
   se297Stroke(c,[[35,12],[191,17],[348,12]],gold,5);
 }
 if(name==='scarf'){
   for(let j=0;j<7;j++)paintFold(30+j*52,Math.sin(j*2)*24);
   for(let i=0;i<3;i++)se297Curve(c,[52+i*27,14],[70,144],[99+i*84,280],[360-i*25,347],
     'rgba(106,116,119,.12)',5);
   se297Curve(c,[15,360],[100,348],[260,350],[375,362],gold,4);
   // Flat painted chain + amber medallion following the drape, not 20 meshes.
   for(let i=0;i<11;i++){
     const x=58+i*26,y=98+27*Math.sin(i/10*Math.PI);
     se297Oval(c,x,y,11,14,null,bronze,3);
     se297Oval(c,x-1,y-2,5,8,null,'rgba(250,227,167,.85)',1.5);
   }
   se297Oval(c,64,105,22,22,'#583c28',gold,6);
   se297Oval(c,64,103,13,13,'#d7822f',shine,3);
 }
 if(name==='uniform'){
   for(let i=0;i<14;i++)se297Curve(c,[i*37-12,-12],[i*35+6,116],
     [i*35-8,254],[i*39,390],'rgba(154,170,171,.07)',3);
   se297Stroke(c,[[39,0],[50,110],[31,210],[46,384]],'rgba(16,21,26,.4)',6);
   se297Stroke(c,[[346,0],[329,110],[351,210],[338,384]],'rgba(14,22,25,.4)',6);
   for(let y=16;y<384;y+=94){
     se297Curve(c,[25,y],[142,y+9],[270,y-5],[357,y+11],
      'rgba(193,206,209,.17)',3);
     se297Curve(c,[30,y+9],[148,y+20],[270,y+3],[352,y+20],
      'rgba(12,20,23,.25)',2);
   }
 }
 if(name==='armor'){
   // Bespoke center breastplate lines. Upper V transitions into lower
   // abdominal bands; edge strokes have metallic shading and highlight.
   se297Poly(c,[[49,14],[192,40],[335,14],[366,90],[327,323],
     [192,368],[57,323],[18,90]],'rgba(18,29,36,.39)',gold,8);
   se297Poly(c,[[71,41],[191,66],[311,41],[334,98],[309,283],
     [192,330],[75,284],[49,98]],'rgba(103,125,135,.27)','#18252e',7);
   for(let i=0;i<4;i++){
     const y=73+i*54,a=38+i*8;
     se297Stroke(c,[[a,y],[192,y+41],[384-a,y]],i%2?bronze:gold,6);
     se297Stroke(c,[[a+3,y-6],[192,y+35],[381-a,y-6]],shine,2);
   }
   se297Poly(c,[[181,72],[204,72],[217,164],[192,185],[167,164]],
     'rgba(10,24,32,.7)',gold,3);
   se297Stroke(c,[[192,199],[192,329]],'rgba(202,161,87,.55)',3);
   for(const s of [-1,1])for(let j=0;j<4;j++){
     const x=192+s*(61+j*17);
     se297Curve(c,[x,148],[x+s*11,176],[x-s*6,204],[x,230],
       'rgba(198,181,131,.52)',2);
   }
 }
 if(name==='pauldron'){
   for(let i=0;i<4;i++){
     const y=38+i*86;
     se297Poly(c,[[17,y+16],[192,y-18],[369,y+14],[341,y+77],
       [192,y+98],[44,y+77]],i%2?'#3b4551':'#535965',gold,8);
     se297Stroke(c,[[31,y+15],[192,y-11],[352,y+15]],shine,3);
     se297Stroke(c,[[49,y+68],[192,y+88],[332,y+68]],bronze,4);
   }
   se297Star(c,192,220,28,gold);
 }
 if(name==='teal'){
   const g=c.createLinearGradient(0,0,384,0);
   g.addColorStop(0,'#0e4a56');g.addColorStop(.32,'#1d8388');
   g.addColorStop(.64,'#287e83');g.addColorStop(1,'#0d3d4a');
   c.fillStyle=g;c.fillRect(0,0,384,384);
   for(let j=0;j<13;j++){
     const x=j*34;
     se297Curve(c,[x,0],[x+20,110],[x-9,280],[x+21,388],
      'rgba(134,208,198,.09)',5);
   }
   for(const x of [13,371]){
     se297Stroke(c,[[x,0],[x,384]],bronze,13);
     se297Stroke(c,[[x+2,0],[x+2,384]],shine,4);
   }
   for(const s of [-1,1]){
    const x=192+s*68;
    se297Curve(c,[x,305],[x-s*26,240],[x+s*60,209],[x+s*52,161],
       gold,5);
    se297Curve(c,[x+s*10,322],[x+s*25,286],[x-s*20,272],[x-s*16,241],
       'rgba(221,195,131,.7)',3);
    se297Star(c,x,333,11,shine);
   }
   for(let y=24;y<384;y+=68){
     se297Curve(c,[34,y+19],[151,y-13],[239,y+42],[350,y+9],
      'rgba(183,219,203,.12)',2);
   }
 }
 if(name==='leather'){
   for(let i=0;i<10;i++){
     const x=i*43;
     se297Stroke(c,[[x,0],[x-6,384]],'rgba(177,120,74,.16)',2);
   }
   se297Poly(c,[[8,122],[376,122],[376,275],[8,275]],
     'rgba(18,17,19,.34)',bronze,7);
   for(let x=25;x<384;x+=21){
     se297Stroke(c,[[x,138],[x+9,145]],'rgba(215,176,112,.58)',2);
     se297Stroke(c,[[x,258],[x+9,251]],'rgba(215,176,112,.58)',2);
   }
   se297Poly(c,[[133,139],[251,139],[251,262],[133,262]],'#9d774c',shine,6);
   se297Poly(c,[[157,160],[228,160],[228,242],[157,242]],'#2f2926',bronze,3);
   se297Oval(c,192,200,13,13,'#7ea3a3',gold,3);
 }
 if(name==='gloves'){
   for(let i=0;i<5;i++){
    const x=52+i*69;
    se297Curve(c,[x-23,17],[x-10,90],[x+10,196],[x+3,374],
      'rgba(124,139,151,.13)',5);
    for(const y of [125,154,214,242]){
     se297Curve(c,[x-19,y],[x-5,y+7],[x+12,y+8],[x+21,y],
      'rgba(112,121,130,.36)',2);
     se297Curve(c,[x-18,y-4],[x,y+1],[x+18,y-3],[x+21,y-5],
      'rgba(255,255,255,.75)',2);
    }
   }
   se297Poly(c,[[163,285],[192,260],[222,285],[192,318]],
     'rgba(119,133,143,.15)',gold,3);
 }
 if(name==='boots'){
   for(let x=34;x<384;x+=52)se297Stroke(c,[[x,5],[x-18,383]],
     'rgba(171,134,93,.14)',2);
   se297Poly(c,[[44,17],[339,17],[362,66],[320,140],
      [333,272],[192,360],[51,272],[64,140],[19,66]],
     'rgba(14,20,27,.43)',gold,7);
   for(let y=73;y<340;y+=83){
     se297Stroke(c,[[75,y],[192,y+37],[307,y]],'#a5a7a9',6);
     se297Stroke(c,[[81,y-4],[192,y+29],[300,y-4]],'#5c6065',3);
   }
 }
 // Paint subtle deterministic woven/leather grain without masking the artwork.
 const img=c.getImageData(0,0,W,W);
 const pix=img.data;let seed=name.length*397;
 for(let y=0;y<W;y++)for(let x=0;x<W;x++){
  const k=(y*W+x)*4;
  seed=(Math.imul(seed,1664525)+1013904223)|0;
  const grain=((seed>>>17)&31)-15;
  const strength=name==='skin' ? 0.12 : ((name==='armor'||name==='pauldron') ? 0.2 : 0.33);
  for(let j=0;j<3;j++)pix[k+j]=Math.max(0,Math.min(255,pix[k+j]+grain*strength));
 }
 c.putImageData(img,0,0);
 return canvas;
}
function se297MakePBR(tile){
 const name=tile.split(':')[1];if(!se297Palette[name])return null;
 if(se297MaterialCache.has(tile))return se297MaterialCache.get(tile);
 const color=se297Artwork(tile),roughness=se297Canvas(),normal=se297Canvas(),W=se297Size;
 const src=color.getContext('2d').getImageData(0,0,W,W).data;
 const rc=roughness.getContext('2d'),nc=normal.getContext('2d');
 const r=rc.createImageData(W,W),n=nc.createImageData(W,W),base=se297Palette[name];
 const lum=i=>src[i]*.299+src[i+1]*.587+src[i+2]*.114;
 for(let y=0;y<W;y++)for(let x=0;x<W;x++){
  const i=(y*W+x)*4,x0=(y*W+Math.max(x-1,0))*4,
   x1=(y*W+Math.min(x+1,W-1))*4,
   y0=(Math.max(y-1,0)*W+x)*4,
   y1=(Math.min(y+1,W-1)*W+x)*4;
  // Conservative normal relief: pigment/shading detail must not become rocks.
  const dx=(lum(x1)-lum(x0))*.011,dy=(lum(y1)-lum(y0))*.011,
   len=Math.hypot(dx,dy,1);
  n.data[i]=127.5*(1-dx/len);n.data[i+1]=127.5*(1-dy/len);
  n.data[i+2]=127.5*(1+1/len);n.data[i+3]=255;
  const grain=((x*17+y*43+name.length*29)%17-8)*.58;
  const rough=Math.max(25,Math.min(250,255*(base.rough+grain/255)));
  r.data[i]=r.data[i+1]=r.data[i+2]=rough;r.data[i+3]=255;
 }
 nc.putImageData(n,0,0);rc.putImageData(r,0,0);
 const result={color,normal,roughness};
 se297MaterialCache.set(tile,result);
 return result;
}
const se297PriorTextures=se296TextureSet;
se296TextureSet=function(tile){
 if(!tile.startsWith('v296:'))return se297PriorTextures(tile);
 return se297MakePBR(tile);
};
// Actual 3D remodeling with the same 17 part identities. The face, cloth
// and hood receive new geometry; existing explicit UVs remain matched to art.
function se297Ribbon(rows,cols,fn){
 const g={positions:[],uvs:[],indices:[]},R=x=>+x.toFixed(5);
 for(let i=0;i<=rows;i++)for(let j=0;j<=cols;j++){
  const u=i/rows,v=j/cols,p=fn(u,v);
  g.positions.push(...p.map(R));g.uvs.push(R(v),R(u));
  if(i<rows&&j<cols){
   const a=i*(cols+1)+j,b=a+cols+1;
   g.indices.push(a,a+1,b,a+1,b+1,b);
  }
 }return g;
}
function se297Join(items){
 const all={positions:[],uvs:[],indices:[]};
 for(const g of items){
  const offset=all.positions.length/3;
  all.positions.push(...g.positions);all.uvs.push(...g.uvs);
  for(const i of g.indices)all.indices.push(i+offset);
 }return all;
}
function se297Redesign(scene){
 const model=scene.project.modelAtelier,p=model.parts;
 if(p.length!==17||!p[1].id.startsWith('vanguard-rebuilt-'))
  throw Error('Vanguard remaster expects current 17-part native starter');
 // Round the needle-chin into a jaw; preserve existing face UV longitude.
 p[1].topologyMesh=se297Ribbon(48,96,(u,v)=>{
  const theta=(v-.5)*Math.PI*2;
  const profile=Math.sqrt(Math.max(.01,Math.sin(Math.PI*(.065+.87*u))));
  const jaw=.81+.19*Math.min(1,u/.38);
  const width=.263*profile*jaw,front=Math.max(0,Math.cos(theta));
  const nose=Math.exp(-Math.pow((u-.40)/.078,2)-Math.pow(theta/.17,2));
  const lip=Math.exp(-Math.pow((u-.235)/.043,2)-Math.pow(theta/.18,2));
  return [width*Math.sin(theta),3.79+.70*u,
    .046+.225*profile*Math.cos(theta)+.029*nose+.006*lip];
 });
 // Separate head-covering crown, lower side/back drape and tucked edges;
 // all remain ONE hood part with authored per-sheet UVs.
 const crown=se297Ribbon(22,72,(u,v)=>{
  const theta=(v-.5)*Math.PI*2,phi=u*Math.PI*.59;
  const r=Math.sin(phi),cap=Math.cos(phi);
  return [.373*r*Math.sin(theta),4.24+.39*cap,
   -.068+.309*r*Math.cos(theta)];
 });
 const drape=se297Ribbon(28,70,(u,v)=>{
  const a=.86+v*(Math.PI*2-1.72);
  const y=3.75+.61*u;
  const r=.353+.035*Math.sin(u*Math.PI);
  return [r*Math.sin(a),y,
   -.077+(.29+.009*Math.sin(Math.PI*u))*Math.cos(a)];
 });
 const edges=se297Ribbon(8,48,(u,v)=>{
  const x=(v-.5)*.64,arch=Math.sin(v*Math.PI);
  return [x,4.34+.16*arch+.012*u,
   .220+.044*arch+.007*u];
 });
 p[4].topologyMesh=se297Join([crown,drape,edges]);
 // Narrow the stacked-paper bib: cloth now drapes naturally below collar.
 p[6].topologyMesh=se297Ribbon(30,44,(u,v)=>{
  const x=(v-.5)*(.73-.13*u),
   fold=.025*Math.sin(2*Math.PI*v+7*u),
   drop=.41*u+.11*u*(1-Math.pow(Math.abs(2*v-1),.85));
  return [x,3.62-drop+.025*Math.sin(Math.PI*v),
   .253+fold+.03*Math.sin(Math.PI*v)];
 });
 // Softer tapered front hair strands rather than straight hanging planks.
 const locks=[];
 for(const side of [-1,1])for(let row=0;row<2;row++)
  locks.push(se297Ribbon(27,9,(u,v)=>{
   const x=side*(.212+row*.046+.028*Math.sin(u*4.8+row)),
    w=(.068-row*.014)*Math.pow(1-u,.85);
   return [x+(v-.5)*w,4.36-u*(.56+row*.09),
     .169+.046*Math.sin(u*3.2+row)+.017*Math.sin(Math.PI*v)];
  }));
 p[3].topologyMesh=se297Join(locks);
 // Ragged flowing lower cloth instead of two symmetrical leaf blades.
 for(const k of [10,11]){
  const side=k===10?-1:1;
  p[k].topologyMesh=se297Ribbon(44,20,(u,v)=>{
    const x=side*(.30+.24*u+.052*Math.sin(u*Math.PI))+
      (v-.5)*(.28+.12*u)*(1-.60*Math.pow(u,5));
    const y=2.48-2.09*u+.03*Math.sin(Math.PI*v)*u;
    const z=-.14-.18*u+.055*Math.sin(u*6.5+v*Math.PI);
    return [x,y,z];
  });
 }
 // Only this new starter is transformed; saved previous user models unchanged.
 model.name='Hooded Vanguard · Painted Remaster';
 model.reference='v11.297: fitted head/hood/scarf/hair/coat geometry with individually UV-mapped painted armor, teal embroidery, skin, hair, ivory cloth, dark cloth, leather and gloves. Hand-painted Warcraft-style reference workflow, not direct mapping of a presentation board; static character. No rig, weapon or bird.';
 scene.project.name=model.name;
 scene.engine='§wyrl§ Engine · Maker v11.297';scene.version=11.297;
 return scene;
}
const se297PreviousScene=se291HeroScene;
se291HeroScene=function(){return se297Redesign(se297PreviousScene());};
window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({
 id:'hooded-vanguard',createScene:se291HeroScene,open:se291OpenHero,
 status:()=>({...se291Stats,textureTiles:Object.keys(se297Palette),
  paintedTileCount:se297MaterialCache.size,textureTechnique:'UV-painted-albedo-normal-roughness',
  version:'v11.297',weapon:false,bird:false,rigged:false})
});
