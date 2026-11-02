// §E v11.226: five original editable sheep-faction building model starters.
// Model Atelier only. Existing Sheep Tag collision/building authority is untouched.
const SE226_BUILDINGS=Object.freeze([
 {id:'sheep-free-shelter',name:'Sheep · Free Shelter',type:'shelter',tag:'FREE · OPEN LEAN-TO',roof:'#617ea5',wall:'#805c42',trim:'#a67b54',stone:'#948b7e'},
 {id:'sheep-thatched-hut',name:'Sheep · Thatched Starter Hut',type:'hut',tag:'FREE-HOUSE · STRAW HUT',roof:'#e6b74f',wall:'#a4825e',trim:'#65442f',stone:'#96908a'},
 {id:'sheep-cottage',name:'Sheep · Cozy Cottage',type:'cottage',tag:'BASIC · COTTAGE',roof:'#e2b75c',wall:'#e4d4b9',trim:'#8d5939',stone:'#89878b'},
 {id:'sheep-barn',name:'Sheep · Flock Barn',type:'barn',tag:'BASIC · RED BARN',roof:'#64799c',wall:'#a54f43',trim:'#f2d6a2',stone:'#8a8079'},
 {id:'sheep-ram-house',name:'Sheep · Ram House',type:'ram',tag:'BASIC · RAM HOUSE',roof:'#efbb58',wall:'#bc936c',trim:'#69472d',stone:'#7b7b77'}
]);
const se226BuildingIds=new Set(SE226_BUILDINGS.map(d=>d.id));
let se226Cached=new Map();
function se226MakeBuildingScene(id){
 const d=SE226_BUILDINGS.find(x=>x.id===id);
 if(!d)throw Error('Unknown sheep building starter');
 if(se226Cached.has(id))return structuredClone(se226Cached.get(id));
 const source=structuredClone(MODEL_ATELIER_CANONICAL_PROJECT);
 const m=source.project.modelAtelier,parts=[];
 const P={wood:'#765039',dark:'#392b25',light:'#e9d6b4',glass:'#f6ca6d',hay:'#f5d27a',flower:'#fff1c4',leaf:'#75a768',red:'#b65b50',wool:'#fff2d5'};
 const groupPrefix='Sheep Building / ';
 const number=v=>Math.round(v*10000)/10000;
 function part(name,kind,color,material,group,extra){
  parts.push({id:'sheep-building-'+parts.length.toString().padStart(3,'0'),name,kind,color,
    material:material||'matte',group:groupPrefix+group,
    position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],...extra});
 }
 // Six independently shaded faces; real indexed geometry, never a textured billboard.
 function box(name,x,y,z,w,h,depth,color,group,angle=0,material='matte'){
  if(w<=0||h<=0||depth<=0)throw Error('Invalid building part');
  const X=w/2,Y=h/2,Z=depth/2;
  const vertices=[[-X,-Y,-Z],[X,-Y,-Z],[X,Y,-Z],[-X,Y,-Z],
                  [-X,-Y,Z],[X,-Y,Z],[X,Y,Z],[-X,Y,Z]];
  const indices=[0,2,1,0,3,2,4,5,6,4,6,7,0,4,7,0,7,3,
                 1,2,6,1,6,5,3,7,6,3,6,2,0,1,5,0,5,4];
  part(name,'topologyMesh',color,material,group,{
   position:[number(x),number(y),number(z)],rotation:[0,0,number(angle)],
   topologyMesh:{positions:vertices.flat(),indices,uvs:vertices.flatMap(v=>[(v[0]/w)+.5,(v[1]/h)+.5])}
  });
 }
 function orb(name,x,y,z,sx,sy,sz,color,group,material='matte'){
  part(name,'sphere',color,material,group,{
   position:[number(x),number(y),number(z)],scale:[sx,sy,sz],meshDensity:{u:12,v:8}
  });
 }
 function roofGable(width,depth,eaveY,rise,thatch){
  const angle=Math.atan2(rise,width/2),slope=Math.hypot(width/2,rise);
  for(const side of [-1,1]){
   box('Roof · '+(side<0?'left':'right')+' pitch',side*width/4,eaveY+rise/2,0,
       slope+.19,.17,depth+.42,d.roof,'Roof',-side*angle);
   // At mobile resolution, a few raised sheaves read better than hundreds of fibers.
   if(thatch){
    for(let i=0;i<4;i++)for(let j=0;j<2;j++){
     const xx=side*(width*.19+(i-1.5)*.085);
     const yy=eaveY+rise*(1-Math.abs(xx)/(width/2))+.115;
     box('Straw · '+side+' / '+i+' / '+j,xx,yy,-depth*.30+j*depth*.52,
         .11,.055,depth*.36,'#f7d587','Roof / straw',-side*angle);
    }
   }
  }
  box('Roof · ridge beam',0,eaveY+rise+.03,0,.19,.18,depth+.56,d.trim,'Roof / beams');
  for(const z of [-depth/2,depth/2]){
   box('Eave · left end',-width*.25,eaveY+rise*.49,z,.10,.12,depth*.01+.12,d.trim,'Roof / beams',angle);
   box('Eave · right end',width*.25,eaveY+rise*.49,z,.10,.12,depth*.01+.12,d.trim,'Roof / beams',-angle);
  }
 }
 function woolBadge(y,z){
  for(const [i,offset] of [-.31,-.11,.11,.31].entries())
   orb('Sheep crest · fleece '+i,offset,y+.075+Math.sin(i)*.075,z,.18,.17,.10,P.wool,'Sheep crest');
  orb('Sheep crest · face',0,y-.085,z+.07,.19,.17,.105,'#866149','Sheep crest');
  for(const side of [-1,1])
   orb('Sheep crest · ear '+side,side*.19,y-.09,z+.08,.10,.065,.045,'#866149','Sheep crest');
 }
 function windowAt(x,y,z){
  box('Window · wooden backing',x,y,z,.72,.73,.095,P.wood,'Windows');
  box('Window · amber glow',x,y,z+.065,.58,.57,.055,P.glass,'Windows','gloss');
  box('Window · divider vertical',x,y,z+.101,.065,.60,P.trim,'Windows');
  box('Window · divider horizontal',x,y,z+.106,.62,.06,.04,d.trim,'Windows');
  box('Window · lower sill',x,y-.40,z+.13,.85,.12,.21,d.trim,'Windows');
 }
 function lantern(x,y,z){
  box('Lantern · metal top',x,y+.21,z,.22,.08,.23,P.dark,'Decor / lantern');
  box('Lantern · glowing glass',x,y,z,.15,.28,.15,P.glass,'Decor / lantern','emissive');
  box('Lantern · metal bottom',x,y-.17,z,.20,.07,.20,P.dark,'Decor / lantern');
 }
 function ground(width,depth){
  box('Stone plinth',0,.12,0,width+.35,.24,depth+.35,d.stone,'Foundation');
  box('Doorstep',0,.16,depth/2+.37,1.28,.21,.61,'#ae9d86','Foundation');
  for(const side of [-1,1])
   box('Corner foundation '+side,side*(width/2-.18),.35,depth/2-.12,.36,.36,.40,'#858280','Foundation');
 }
 function woodenWall(width,height,depth,openDoor=false){
  // Front faces +Z, open door has a genuine gap instead of a fake image.
  for(const z of [-depth/2,depth/2]){
   if(z>0&&openDoor){
    for(const side of [-1,1])box('Front wall '+side,side*(width+1.26)/4,1.25,z,(width-1.26)/2,2.5,.20,d.wall,'Walls');
    box('Front lintel',0,2.53,z,width,.24,.20,d.wall,'Walls');
   }else box('Front / rear wall',0,height/2+.26,z,width,height,.20,d.wall,'Walls');
  }
  for(const side of [-1,1])box('Side wall '+side,side*width/2,height/2+.26,0,.20,height,depth,d.wall,'Walls');
  for(const x of [-width/2,width/2])for(const z of [-depth/2,depth/2])
   box('Timber corner '+x+' / '+z,x,height/2+.25,z,.22,height+.20,.23,d.trim,'Frames / posts');
  box('Front timber lintel',0,height+.17,depth/2+.02,width+.23,.16,.25,d.trim,'Frames / posts');
  box('Rear timber lintel',0,height+.17,-depth/2-.02,width+.23,.16,.25,d.trim,'Frames / posts');
 }
 function doors(depth,double=false,open=false){
  if(open)return;
  const z=depth/2+.135;
  box('Door · walnut body',0,1.12,z,double?1.62:1.10,1.74,.15,P.wood,'Door');
  if(double)box('Doors · center seam',0,1.12,z+.094,.065,1.71,.045,P.dark,'Door / trim');
  for(const x of (double?[-.38,.38]:[0])){
   box('Door · diagonal upper '+x,x,1.45,z+.105,.095,.95,.05,d.trim,'Door / trim',.57);
   box('Door · diagonal lower '+x,x,.82,z+.105,.095,.95,.05,d.trim,'Door / trim',-.57);
  }
  orb('Door · bronze handle',double?.13:.34,1.12,z+.13,.08,.09,.06,'#d4b36e','Door / trim','metal');
  box('Door · overhead header',0,2.09,z+.02,double?1.93:1.39,.23,.31,d.trim,'Door / trim');
 }
 function flowers(width,depth){
  for(let i=0;i<4;i++){
   const x=(i-1.5)*.23+width*.26,z=depth/2+.37;
   orb('Flower · leaves '+i,x,.32,z,.13,.09,.15,P.leaf,'Decor / garden');
   orb('Flower · bloom '+i,x,.42,z,.06,.045,.06,i%2?'#f2a8a3':P.flower,'Decor / garden');
  }
 }
 const w=d.type==='barn'?5.1:d.type==='shelter'?3.4:d.type==='hut'?3.3:4.2;
 const depth=d.type==='barn'?4.7:d.type==='shelter'?3.0:d.type==='hut'?3.25:3.8;
 const tall=d.type==='barn'?3.1:d.type==='shelter'?2.4:2.65;
 ground(w,depth);
 if(d.type==='shelter'){
  // Three-sided open lean-to with a clear playable opening.
  box('Open shelter · back wall',0,1.33,-depth/2,w,2.18,.20,d.wall,'Walls');
  for(const side of [-1,1]){
   box('Open shelter · corner post '+side,side*(w/2-.12),1.45,depth/2-.10,.20,2.65,.20,d.trim,'Frames / posts');
   box('Open shelter · side windbreak '+side,side*w/2,.88,-.48,.15,1.12,depth*.53,d.wall,'Walls');
  }
  box('Shelter · blue sloping roof',0,2.73,0,w+.40,.17,depth+.45,d.roof,'Roof',-.105);
  for(let i=0;i<5;i++)box('Hay bedding '+i,(i-2)*.45,.37,-.36,.33,.10,.62,P.hay,'Decor / straw',.02*(i-2));
  lantern(w*.37,1.89,depth*.35);
 }else{
  const open=d.type==='barn'||d.type==='ram';
  woodenWall(w,tall,depth,open);
  roofGable(w+.45,depth,tall+.30,d.type==='hut'?1.65:1.70,d.type!=='barn');
  doors(depth,d.type==='barn',open);
  if(open){
   box('Open doorway · deep shadow',0,1.11,depth/2-.045,d.type==='barn'?1.72:1.45,1.83,.06,P.dark,'Door / interior');
   box('Open doorway · hay threshold',0,.33,depth/2+.14,1.35,.13,.48,P.hay,'Decor / straw');
  }
  if(d.type==='barn'){
   windowAt(0,2.96,depth/2+.14);
   for(const side of [-1,1]){
    box('Barn · white diagonal frame '+side,side*(w*.32),1.31,depth/2+.16,.16,2.21,.07,d.trim,'Frames / posts',side*.42);
    box('Barn · upper white brace '+side,side*(w*.31),2.13,depth/2+.17,.17,1.01,.07,d.trim,'Frames / posts',-side*.60);
   }
   for(let i=0;i<3;i++)box('Hay bale '+i,w/2+.20+i*.20,.34+i*.31,depth*.30,.64,.31,.72,P.hay,'Decor / hay');
  }else{
   windowAt(-w*.31,1.43,depth/2+.16);
   lantern(w*.34,1.85,depth/2+.31);
   woolBadge(tall+.34,depth/2+.32);
   if(d.type==='cottage'){
    box('Cottage · flower box',-w*.31,.98,depth/2+.30,.87,.16,.29,d.trim,'Windows / flowers');
    flowers(w,depth);
    box('Cottage · chimney',w*.25,tall+1.38,-depth*.19,.44,1.04,.40,d.stone,'Roof / chimney');
    box('Cottage · chimney cap',w*.25,tall+1.90,-depth*.19,.58,.13,.55,d.stone,'Roof / chimney');
   }else if(d.type==='hut'){
    for(const side of [-1,1])
     orb('Hut · curly ram roof ornament '+side,side*.67,tall+.88,depth/2+.24,.31,.29,.20,'#9d673c','Sheep crest');
   }else if(d.type==='ram'){
    box('Ram house · side covered porch',w*.45,1.27,0,1.2,.13,depth*.76,P.hay,'Porch');
    for(const z of [-depth*.28,depth*.28])box('Ram house · porch post',w*.77,1.20,z,.20,2.10,.20,d.trim,'Porch');
    box('Ram house · porch awning',w*.57,2.33,0,1.95,.17,depth*.88,d.roof,'Porch');
   }
  }
 }
 // All pieces remain individually editable and groupable in native Model Atelier.
 m.name=d.name;
 m.parts=parts;
 m.meshGroups=[...new Set(parts.map(p=>p.group))].map((name,i)=>({
   id:'sheep-building-group-'+i,name,members:parts.filter(p=>p.group===name).map(p=>p.id)
 })).filter(x=>x.members.length>=2);
 m.poseFrames=[];m.poseNeutral=null;m.editedAt='local';
 m.reference='Original Sheep Tag faction house concepts: native geometry, front/side/top 3D viewing, no image planes.';
 source.project.name=d.name;
 source.project.canonicalId=d.id;source.project.template=d.id;
 source.project.kind='model-atelier';
 source.project.environmentSettings={...source.project.environmentSettings,
   showTerrain:false,showScenery:false,background:'#b6d8df'};
 source.engine='§wyrl§ Engine · Maker v11.226';source.version=11.226;
 se226Cached.set(id,source);
 return structuredClone(source);
}
function se226OpenBuilding(id,force=false){
 if(!se226BuildingIds.has(id))return false;
 if(dirty&&!force&&!confirm('Open this sheep house starter and discard unsaved changes?'))return false;
 try{
  const source=se226MakeBuildingScene(id);
  ModelAtelier.close();loadProject(source,{workspaceLocal:true});
  initializeHistory('Opened '+source.project.name+' starter');markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  ModelAtelier.syncProject();ModelAtelier.open();
  const panel=document.getElementById('modelAtelierPanel');
  const edit=document.getElementById('modelAtelierCourierStudio');
  panel?.classList.add('courier-studio');
  if(edit){edit.hidden=false;edit.textContent='Edit model';edit.setAttribute('aria-pressed','true');}
  requestAnimationFrame(()=>requestAnimationFrame(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view?.('three')));
  toast(source.project.name+' · editable mesh groups ready');
  return true;
 }catch(error){console.error('Sheep building starter',error);toast('Sheep starter unavailable: '+error.message);return false;}
}
const se226OriginalTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 return se226BuildingIds.has(template)?se226OpenBuilding(template,force):se226OriginalTemplate(template,force);
};
window.SWYRL_ENGINE_SHEEP_BUILDING_STARTERS=Object.freeze({
 list:()=>SE226_BUILDINGS.map(({id,name,tag})=>({id,name,tag})),
 createScene:(id)=>se226MakeBuildingScene(id),
 open:(id,force=false)=>se226OpenBuilding(id,force)
});
