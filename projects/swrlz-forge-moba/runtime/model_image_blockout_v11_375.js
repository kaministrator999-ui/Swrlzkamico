/* SE375_IMAGE_TO_MODEL_START
 * §E / integrated §C: local image silhouette -> editable native lofts.
 * A rough orthographic blockout, NOT neural 3D reconstruction or UV extraction.
 * User-selected image pixels never leave the browser. No new backend or renderer.
 */
let se375Sheet=null,se375Canvas=null,se375Busy=false;
const se375Id=id=>document.getElementById('se375'+id);
const se375Guides={front:.143,left:.329,right:.475,back:.692,top:.897,upper:.136,lower:.623};
function se375Note(message,error=false){
 const el=se375Id('Status');if(el){el.textContent=message;el.dataset.error=String(error);}
}
function se375PanelRects(){
 const g=se375Guides,y0=g.upper,y1=g.lower;
 return [
  {name:'Front',x:g.front-.073,y:y0,w:.150,h:y1-y0},
  {name:'Left',x:g.left-.058,y:y0,w:.120,h:y1-y0},
  {name:'Right',x:g.right-.058,y:y0,w:.120,h:y1-y0},
  {name:'Back',x:g.back-.098,y:y0,w:.190,h:y1-y0},
  {name:'Top',x:g.top-.086,y:.25,w:.17,h:.28}
 ];
}
function se375Draw(){
 const canvas=se375Id('Preview');if(!canvas||!se375Canvas)return;
 const ratio=se375Canvas.height/se375Canvas.width;
 canvas.width=460;canvas.height=Math.max(60,Math.round(canvas.width*ratio));
 const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);
 ctx.drawImage(se375Canvas,0,0,canvas.width,canvas.height);
 ctx.lineWidth=1.7;ctx.font='bold 12px sans-serif';
 for(const rect of se375PanelRects()){
  const x=canvas.width*rect.x,y=canvas.height*rect.y,w=canvas.width*rect.w,h=canvas.height*rect.h;
  ctx.strokeStyle=rect.name==='Top'?'#f6c26b':'#87e6e4';
  ctx.strokeRect(x,y,w,h);ctx.fillStyle='#121521dc';
  ctx.fillRect(x,y-17,Math.min(w,ctx.measureText(rect.name).width+10),17);
  ctx.fillStyle='#fff';ctx.fillText(rect.name,x+4,y-4);
 }
}
async function se375Load(file){
 se375Sheet=null;se375Canvas=null;
 if(!file)return;
 if(!/^image\/(?:png|jpeg|webp)$/.test(file.type)||file.size>12*1024*1024)
  throw Error('Use a PNG, JPEG or WebP reference under 12 MB.');
 let url=URL.createObjectURL(file);
 try{
  const image=new Image();
  await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(Error('Could not decode this image.'));image.src=url;});
  if(image.naturalWidth<320||image.naturalHeight<240||image.naturalWidth>10000||image.naturalHeight>10000)
   throw Error('Reference image dimensions are unsupported.');
  // Bound mobile memory and avoid storing image bytes in native account projects.
  const canvas=document.createElement('canvas');
  canvas.width=Math.min(960,image.naturalWidth);canvas.height=Math.round(image.naturalHeight*canvas.width/image.naturalWidth);
  const context=canvas.getContext('2d',{willReadFrequently:true});if(!context)throw Error('Canvas image tools unavailable.');
  context.drawImage(image,0,0,canvas.width,canvas.height);
  se375Sheet={name:file.name,width:image.naturalWidth,height:image.naturalHeight};
  se375Canvas=canvas;se375Draw();
  se375Note('Loaded '+file.name+'. Check the five view guides; adjust below if the characters are not centered.');
 }finally{URL.revokeObjectURL(url);}
}
function se375Foreground(data,x,y,w,h,bg){
 if(x<0||x>=w||y<0||y>=h)return false;
 const i=(y*w+x)*4,r=data[i],g=data[i+1],b=data[i+2],a=data[i+3];
 if(a<40)return false;
 const distance=Math.hypot(r-bg[0],g-bg[1],b-bg[2]);
 return distance>46 && Math.min(r,g,b)<245;
}
function se375Sample(){
 if(!se375Canvas)throw Error('Choose a turnaround reference first.');
 const w=se375Canvas.width,h=se375Canvas.height;
 const ctx=se375Canvas.getContext('2d',{willReadFrequently:true});
 const data=ctx.getImageData(0,0,w,h).data;
 // Background sampling uses the clean gap above the panels, not the labels.
 const refs=[[.10,.110],[.38,.112],[.79,.110],[.50,.695]];
 const bg=[0,1,2].map(c=>Math.round(refs.reduce((sum,p)=>{
  const x=Math.floor(p[0]*w),y=Math.floor(p[1]*h);
  return sum+data[(y*w+x)*4+c];},0)/refs.length));
 const rects=se375PanelRects();
 function scan(box,y){
  const row=Math.max(0,Math.min(h-1,Math.round(y*h)));
  const start=Math.max(0,Math.floor(box.x*w)),end=Math.min(w,Math.ceil((box.x+box.w)*w));
  let lo=end,hi=start,hits=0;
  // Ignore isolated sparkles; find the colored figure silhouette across a row.
  for(let x=start;x<end;x+=2){
   if(se375Foreground(data,x,row,w,h,bg)){lo=Math.min(lo,x);hi=Math.max(hi,x);hits++;}
  }
  return hits>=5?{lo,hi,center:(lo+hi)/2,width:Math.max(2,hi-lo)}:null;
 }
 function dominant(box,a,b){
  const votes=new Map(),y0=Math.round(h*a),y1=Math.round(h*b);
  const x0=Math.floor(w*box.x),x1=Math.ceil(w*(box.x+box.w));
  for(let y=y0;y<y1;y+=5)for(let x=x0;x<x1;x+=5){
   if(!se375Foreground(data,x,y,w,h,bg))continue;
   const i=(y*w+x)*4,r=data[i],g=data[i+1],bl=data[i+2];
   const key=[r,g,bl].map(n=>Math.min(15,Math.floor(n/16))).join(',');
   votes.set(key,(votes.get(key)||0)+1);
  }
  const best=[...votes.entries()].sort((a,b)=>b[1]-a[1])[0];
  return best?'#'+best[0].split(',').map(v=>(Number(v)*16+8).toString(16).padStart(2,'0')).join(''):'#80609a';
 }
 return {scan,dominant,rects,bg};
}
function se375Blockout(){
 const sample=se375Sample(),rect=sample.rects;
 const {upper,lower}=se375Guides;
 const slices=28,rows=[];
 for(let i=0;i<=slices;i++){
  const y=upper+(lower-upper)*i/slices;
  const front=sample.scan(rect[0],y),side=sample.scan(rect[1],y),right=sample.scan(rect[2],y),back=sample.scan(rect[3],y);
  rows.push({y,front,side,right,back});
 }
 const validF=rows.map(r=>r.front?.width||0).filter(n=>n>0);
 const validS=rows.map(r=>r.side?.width||0).filter(n=>n>0);
 const validR=rows.map(r=>r.right?.width||0).filter(n=>n>0);
 if(validF.length<14||validS.length<12||validR.length<12)throw Error('Could not isolate front and both side profiles. Adjust guides to fit full characters.');
 const widestF=Math.max(...validF),widestS=Math.max(...validS,...validR);
 const topRows=[.32,.35,.38,.41,.44].map(y=>sample.scan(rect[4],y)).filter(Boolean);
 const topWidth=topRows.length?Math.max(...topRows.map(r=>r.width)):0;
 // Top-view outline sets a bounded independent hood-depth cue.
 const topAspect=topWidth?Math.max(.75,Math.min(1.25,topWidth/(rect[4].w*se375Canvas.width)*1.15)):1;
 if(widestF<se375Canvas.width*.045||widestS<se375Canvas.width*.025)
  throw Error('View guides are not covering enough of the figure.');
 const projectRows=rows.map((r,i)=>{
  const near=sampleNearest(rows,i,'front'),side=sampleNearest(rows,i,'side'),right=sampleNearest(rows,i,'right'),rear=sampleNearest(rows,i,'back');
  const width=Math.max(near.width,rear?.width||0)*.5+(Math.min(near.width,rear?.width||near.width))*.5;
  const worldY=.15+4.15*(1-i/slices);
  return {worldY,
    x:(near.center-se375Guides.front*se375Canvas.width)/widestF*2.8,
    z:((side.center-se375Guides.left*se375Canvas.width)-(right.center-se375Guides.right*se375Canvas.width))/widestS*.8,
    radius:Math.max(.08,Math.min(1.44,width/widestF*1.42)),
    depth:Math.max(.18,Math.min(1.35,(side.width+right.width)/(2*widestS)*1.15))};
 });
 // Separate independently editable bands: these are geometric slices, not
 // claimed semantic recognition. Slice boundaries can be moved later by hand.
 const bands=[
  {name:'Upper silhouette',start:0,end:11,color:sample.dominant(rect[0],upper,.323)},
  {name:'Middle silhouette',start:11,end:18,color:sample.dominant(rect[0],.325,.455)},
  {name:'Lower silhouette',start:18,end:24,color:sample.dominant(rect[0],.455,.548)},
  {name:'Foot silhouette',start:24,end:28,color:sample.dominant(rect[0],.548,lower)}
 ];
 const operations=bands.map((band,index)=>{
  const ring=projectRows.slice(band.start,band.end+1);
  const ratio=ring.reduce((sum,p)=>sum+p.depth/(p.radius||.1),0)/ring.length;
  const zScale=Math.max(.38,Math.min(1.2,ratio*(index===0?topAspect:1)));
  return {op:'mesh.add',kind:'loft',name:'Reference blockout '+(index+1)+' · '+band.name,
   position:[0,0,0],rotation:[0,0,0],scale:[1,1,zScale],
   path:ring.map(p=>[round(p.x),round(p.worldY),round(p.z)]),
   radii:ring.map(p=>round(p.radius)),segments:32,color:band.color,material:'matte'};
 });
 // Detect a tall narrow separate prop to the left of the front-view figure.
 // Opt-in and source-derived; do not invent a staff on every turnaround.
 if(se375Id('Prop')?.checked){
  const propBox={x:Math.max(0,se375Guides.front-.124),y:.20,w:.054,h:.42};
  const observations=Array.from({length:16},(_,i)=>{
   const y=.225+(.61-.225)*i/15;
   return {y,shape:sample.scan(propBox,y)};
  }).filter(p=>p.shape);
  if(observations.length>=11){
   const xBase=se375Guides.front*se375Canvas.width;
   const staffPath=observations.map(p=>[
     round((p.shape.center-xBase)/widestF*2.8),
     round(.15+4.15*(lower-p.y)/(lower-upper)),.15]);
   const staffRadii=observations.map(p=>round(Math.max(.027,Math.min(.10,p.shape.width/widestF*.22))));
   operations.push({op:'mesh.add',kind:'loft',name:'Reference blockout · detached side prop',
    position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],path:staffPath,radii:staffRadii,
    segments:12,color:sample.dominant(propBox,.34,.60),material:'matte'});
  }
 }
 return operations;
}
function sampleNearest(rows,i,key){
 for(let delta=0;delta<rows.length;delta++){
  const a=rows[i-delta]?.[key],b=rows[i+delta]?.[key];
  if(a)return a;if(b)return b;
 }
 throw Error('Missing '+key+' silhouette.');
}
function round(value){return Number(value.toFixed(4));}
async function se375Run(){
 if(se375Busy)return;
 const button=se375Id('Generate');se375Busy=true;if(button)button.disabled=true;
 try{
  if(!se375Canvas)throw Error('Upload a reference sheet first.');
  if(currentProject?.kind!=='model-atelier'||!ModelAtelier.status().open)
   throw Error('Open a Blank 3D model in Model Studio before generating.');
  const source=String(currentProject.sourceStarterId||currentProject.template||'');
  if(!['blank-model','model-atelier'].includes(source))
   throw Error('Use a Blank 3D model project, not a character or game starter.');
  const existing=currentProject.modelAtelier?.parts||[];
  if(existing.length>1)throw Error('This project already has model parts. Open or clone a blank project; existing work will not be replaced.');
  const operations=se375Blockout();
  if(typeof ModelAtelier.chatAction!=='function')throw Error('Native mesh editor is not available.');
  // Starter identity must not receive a write. Clone first using existing
  // owner Save/Clone machinery; never overwrite canonical source projects.
  if(typeof se371HasSavedIdentity==='function'&&!se371HasSavedIdentity()){
   se375Note('Creating your independent blank model project…');
   await se371Clone('Image blockout · '+(se375Sheet?.name||'Reference').replace(/\.[^.]+$/,'').slice(0,65));
  }
  if(currentProject?.kind!=='model-atelier'||!ModelAtelier.status().open)
   throw Error('Blank model workspace changed during generation.');
  se375Note('Building editable mesh silhouettes, 0/'+operations.length+'…');
  let added=0;
  for(const op of operations){
   // Native actions use existing checkpoint/history, input validation, rendering,
   // project dirty-state tracking, and safe local project persistence.
   ModelAtelier.chatAction(op);
   added++;
   se375Note('Building editable mesh silhouettes, '+added+'/'+operations.length+'…');
   await new Promise(resolve=>requestAnimationFrame(resolve));
  }
  // Remove the one blank seed only once the new model safely exists.
  const candidate=currentProject.modelAtelier.parts.find(p=>!operations.some(op=>op.name===p.name)
      && !String(p.name).startsWith('Reference blockout '));
  if(existing.length===1&&candidate&&currentProject.modelAtelier.parts.length>1)
   ModelAtelier.chatAction({op:'mesh.remove',id:candidate.id});
  if(typeof se371SaveLocal==='function')await se371SaveLocal();
  se375Note('Generated '+added+' editable 3D silhouette sections. Orbit the viewport, refine with Model tools, then Save Project. The source image stays on this device.');
 }catch(error){
  se375Note('Blockout paused: '+String(error?.message||error)+'. Existing model edits were preserved.',true);
 }finally{se375Busy=false;if(button)button.disabled=false;}
}
function se375Install(){
 if(se375Id('Panel')||!document.getElementById('seChatAccountPanel'))return;
 const host=document.querySelector('#seChatAccountPanel .se-chat-account');if(!host)return;
 const style=document.createElement('style');
 style.textContent='#se375Panel{border:1px solid #655680;border-radius:9px;padding:5px 9px;max-width:100%;background:#211b32}#se375Panel summary{cursor:pointer;font-weight:700;padding:5px 0}#se375Panel .se375-body{display:grid;gap:7px;padding:4px 0}#se375Panel label{display:grid;gap:3px;font-size:12px}#se375Panel input[type=file]{max-width:100%;min-width:0}#se375Panel input[type=range]{width:100%}#se375Panel .se375-guides{display:grid;grid-template-columns:1fr 1fr;gap:5px}#se375Preview{width:100%;max-height:165px;object-fit:contain;background:#faf5ed;border-radius:5px}#se375Status{font-size:12px;line-height:1.35;margin:0;color:#dfd3f1}#se375Status[data-error=true]{color:#ffb6b6}';
 document.head.append(style);
 const section=document.createElement('details');section.id='se375Panel';
 section.innerHTML='<summary>✦ Image → editable 3D blockout</summary>'
  +'<div class="se375-body"><label>Five-view turnaround image<input id="se375File" type="file" accept="image/png,image/jpeg,image/webp"></label>'
  +'<canvas id="se375Preview" aria-label="Image preview with five view guides"></canvas>'
  +'<details><summary>Adjust view guides</summary><div id="se375Guides" class="se375-guides"></div></details>'
  +'<label><input id="se375Prop" type="checkbox" checked> Include a separate slender side prop if detected</label>'
  +'<button id="se375Generate" type="button">Build rough 3D in viewport</button>'
  +'<p id="se375Status" role="status" aria-live="polite">Open a Blank 3D model first. This local silhouette experiment makes separate editable mesh sections—not an exact textured scan.</p></div>';
 host.append(section);
 for(const [key,label] of [['front','Front X'],['left','Left X'],['right','Right X'],['back','Back X'],['top','Top X'],['upper','Figure top Y'],['lower','Figure bottom Y']]){
  const row=document.createElement('label');row.textContent=label;
  const input=document.createElement('input');input.type='range';input.min='0.04';input.max='0.96';input.step='.005';
  input.value=String(se375Guides[key]);input.setAttribute('aria-label',label);
  input.oninput=()=>{se375Guides[key]=Number(input.value);se375Draw();};row.append(input);se375Id('Guides').append(row);
 }
 se375Id('File').onchange=event=>{const file=event.target.files?.[0];se375Load(file).catch(error=>se375Note(String(error?.message||error),true));};
 se375Id('Generate').onclick=()=>void se375Run();
}

// §C mounts lazily. Attach once when the authenticated Chat host panel appears,
// rather than creating another editor window or altering its iframe transport.
const se375Observer=new MutationObserver(()=>{
 if(se375Id('Panel')){se375Observer.disconnect();return;}
 se375Install();
 if(se375Id('Panel'))se375Observer.disconnect();
});
if(document.documentElement)se375Observer.observe(document.documentElement,{childList:true,subtree:true});
queueMicrotask(se375Install);
