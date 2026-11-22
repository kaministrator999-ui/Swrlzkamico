/* §E v11.545 — anatomy-aware view of the TRUE, existing UV atlas.
   READ ONLY: never alter UVs, paint, geometry, rig, or project state.
   This is an anatomy legend / inspectable overlay, not a new unwrap. */
const se545Zones=[
 {id:'head',name:'Head',color:'#e6aaee'},
 {id:'chest',name:'Torso front',color:'#56d5ef'},
 {id:'back',name:'Torso back',color:'#9ca9fa'},
 {id:'side',name:'Torso sides',color:'#86c5b7'},
 {id:'leftArm',name:'Left arm',color:'#ffcf72'},
 {id:'rightArm',name:'Right arm',color:'#f6a15e'},
 {id:'leftLeg',name:'Left leg',color:'#8fe49b'},
 {id:'rightLeg',name:'Right leg',color:'#52bd7b'}
];
let se545Active='all',se545LastPart=null,se545Showing=false;
function se545Target(){
 const t=se336SelectedMesh();
 return t?.part?.id==='humanoid-body-unified'&&
   currentProject?.canonicalId==='robotic-humanoid-mannequin'&&
   t.part.kind==='topologyMesh'?t.part:null;
}
function se545Zone(p0,p1,p2){
 const x=(p0[0]+p1[0]+p2[0])/3;
 const y=(p0[1]+p1[1]+p2[1])/3;
 if(y>=4.08)return 'head';
 if(Math.abs(x)>.69&&y>3.30)return x<0?'leftArm':'rightArm';
 if(y<=2.35)return x<0?'leftLeg':'rightLeg';
 const a=p1.map((v,i)=>v-p0[i]),b=p2.map((v,i)=>v-p0[i]);
 const nz=a[0]*b[1]-a[1]*b[0];
 const len=Math.hypot(a[1]*b[2]-a[2]*b[1],
                     a[2]*b[0]-a[0]*b[2],nz);
 return len>1e-12&&nz/len>.30?'chest':len>1e-12&&nz/len<-.30?'back':'side';
}
function se545Faces(part){
 const m=part?.topologyMesh,faces=[];
 if(!m||!Array.isArray(m.positions)||!Array.isArray(m.indices)||
    !Array.isArray(m.uvs)||m.positions.length%3||m.indices.length%3||
    m.uvs.length!==m.positions.length/3*2||
    m.indices.length>48000||m.positions.length>27000)
  throw Error('This mannequin does not have supported indexed UV geometry.');
 const n=m.positions.length/3;
 if(!m.positions.every(Number.isFinite)||!m.uvs.every(Number.isFinite)||
    !m.indices.every(i=>Number.isInteger(i)&&i>=0&&i<n))
  throw Error('Invalid mesh data; anatomy overlay was not generated.');
 const counts=Object.fromEntries(se545Zones.map(z=>[z.id,0]));
 for(let i=0;i<m.indices.length;i+=3){
  const ids=m.indices.slice(i,i+3);
  const p=ids.map(id=>m.positions.slice(id*3,id*3+3));
  const uv=ids.map(id=>m.uvs.slice(id*2,id*2+2));
  if(uv.some(q=>q.some(x=>x<0||x>1)))throw Error('UV values outside the 0–1 atlas.');
  const zone=se545Zone(...p);counts[zone]++;
  faces.push({uv,zone});
 }
 return {faces,counts,triangles:faces.length};
}
function se545Draw(canvas,data,filter,exporting){
 const ctx=canvas.getContext('2d');if(!ctx)throw Error('2D canvas unavailable.');
 const w=canvas.width,h=canvas.height;
 ctx.clearRect(0,0,w,h);ctx.fillStyle='#142131';ctx.fillRect(0,0,w,h);
 const palette=Object.fromEntries(se545Zones.map(z=>[z.id,z.color]));
 const inset=exporting?40:12,side=Math.min(w,h)-2*inset;
 const counts={};
 for(const face of data.faces){
  if(!counts[face.zone])counts[face.zone]=0;
  counts[face.zone]++;
  const highlighted=filter==='all'||filter===face.zone;
  ctx.globalAlpha=highlighted?.95:.08;
  ctx.fillStyle=palette[face.zone];
  ctx.beginPath();
  face.uv.forEach(([u,v],i)=>{
   const x=inset+u*side,y=inset+(1-v)*side;
   if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
  });
  ctx.closePath();ctx.fill();
 }
 ctx.globalAlpha=1;
 ctx.strokeStyle='#e4f5ff';ctx.globalAlpha=.46;ctx.lineWidth=exporting?1:.6;
 for(const face of data.faces){
  if(filter!=='all'&&face.zone!==filter)continue;
  ctx.beginPath();
  face.uv.forEach(([u,v],i)=>{
   const x=inset+u*side,y=inset+(1-v)*side;
   if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
  });
  ctx.closePath();ctx.stroke();
 }
 ctx.globalAlpha=1;ctx.strokeStyle='#859aad';ctx.lineWidth=1;ctx.strokeRect(inset,inset,side,side);
 if(exporting){
  ctx.fillStyle='#f1f5f9';ctx.font='24px system-ui';
  ctx.fillText('Actual humanoid UV anatomy · reference only · not a painted texture',48,32);
  let x=50,y=h-15;
  ctx.font='17px system-ui';
  for(const z of se545Zones){
   const label=z.name+' ('+(counts[z.id]||0)+')';
   const span=ctx.measureText(label).width+39;
   if(x+span>w-30){x=50;y-=28;}
   ctx.fillStyle=z.color;ctx.fillRect(x,y-13,14,14);
   ctx.fillStyle='#e7edf7';ctx.fillText(label,x+20,y);x+=span;
  }
 }
}
function se545Refresh(){
 const root=document.getElementById('se545AnatomyView');
 if(!root)return;
 const part=se545Target();
 const open=root.open;
 root.querySelector('#se545AnatomyExport').disabled=!part;
 root.querySelector('#se545AnatomyRegion').disabled=!part;
 if(!part){
  root.querySelector('#se545AnatomyInfo').textContent='Select the Futuristic Humanoid body to inspect its actual UV anatomy.';
  root.querySelector('#se545AnatomyCanvas').hidden=true;
  se545LastPart=null;
 }else if(open&&(se545LastPart!==part||!se545Showing)){
  se545Render();
 }
}
function se545Render(){
 const root=document.getElementById('se545AnatomyView'),part=se545Target();
 if(!root||!part)return;
 try{
  const data=se545Faces(part);
  const canvas=root.querySelector('#se545AnatomyCanvas');
  se545Draw(canvas,data,se545Active,false);canvas.hidden=false;
  root.querySelector('#se545AnatomyInfo').textContent=
    data.triangles.toLocaleString()+' actual UV triangles · '+
    se545Zones.map(z=>z.name+': '+data.counts[z.id]).join(' · ')+
    '. Colors are assigned from 3D anatomy, not guessed from island silhouettes.';
  se545LastPart=part;se545Showing=true;
 }catch(e){root.querySelector('#se545AnatomyInfo').textContent=e.message;se545Showing=false;}
}
function se545Export(){
 const part=se545Target();if(!part)return;
 try{
  const data=se545Faces(part),canvas=document.createElement('canvas');
  canvas.width=canvas.height=2048;
  se545Draw(canvas,data,se545Active,true);
  se336SaveCanvas(canvas,part.name+'-TRUE-UV-ANATOMY-REFERENCE-2048.png');
  status('Exported anatomical UV reference. This is a guide ONLY; do not import its colored triangles as the robot texture.');
 }catch(e){status('UV anatomy export: '+e.message,true);}
}
function se545Install(){
 const host=document.getElementById('se356UVPreview');
 if(!host||document.getElementById('se545AnatomyView'))return;
 const root=document.createElement('details');root.id='se545AnatomyView';
 root.style.cssText='margin:10px 0;padding:10px;border:1px solid #627b90;border-radius:8px';
 root.innerHTML='<summary>Humanoid UV anatomy · identify real mapped regions</summary>'+
  '<p>Read-only view of the current mesh UVs, colored by the real 3D head, front/back torso, arms and legs. Shows where to paint WITHOUT changing UV packing or detaching artwork.</p>'+
  '<label>Highlight region <select id="se545AnatomyRegion"><option value="all">All body regions</option>'+
  se545Zones.map(z=>'<option value="'+z.id+'">'+z.name+'</option>').join('')+'</select></label> '+
  '<button type="button" id="se545AnatomyExport">Export anatomy guide · 2048px</button>'+
  '<canvas id="se545AnatomyCanvas" width="640" height="640" hidden style="display:block;width:100%;max-width:640px;height:auto;margin:8px auto;touch-action:pan-y"></canvas>'+
  '<p id="se545AnatomyInfo" role="status">Open to inspect the current selected mannequin UVs.</p>'+
  '<p>Guides are reference overlays, not material textures. Existing UV coordinates, image, sculpt and Undo history remain untouched.</p>';
 host.append(root);
 root.addEventListener('toggle',()=>{if(root.open){se545Showing=false;se545Render();}});
 root.querySelector('#se545AnatomyRegion').addEventListener('change',e=>{
  se545Active=e.target.value;se545Render();
 });
 root.querySelector('#se545AnatomyExport').addEventListener('click',se545Export);
 se545Refresh();
}
const se545OldEnsurePanel=ensurePanel;
ensurePanel=function(){
 const result=se545OldEnsurePanel.apply(this,arguments);
 se545Install();return result;
};
const se545OldRefreshInspector=refreshInspector;
refreshInspector=function(){
 const result=se545OldRefreshInspector.apply(this,arguments);
 se545Refresh();return result;
};
window.SWYRL_E_UV_ANATOMY_545=Object.freeze({
 inspect:()=>{const p=se545Target();return p?se545Faces(p):null},
 render:se545Render,
 version:'v11.545'
});
/* SE545_UV_ANATOMY_VIEW_END */
