// Reference tailoring is native editable geometry; the v11.91 saved outfit is
// untouched. Extend panels, their existing seams and their pendants together.
function atelierFestivalRefineDress(project){
 const model=project.project.modelAtelier,parts=model.parts,added=[];
 const byId=id=>parts.find(part=>part.id===id),round=v=>+v.toFixed(6);
 const panelIndex=id=>{const match=id.match(/^skirt-(?:panel|piping|inset)-(\d+)/);return match?+match[1]:null;};
 const lengthFor=index=>index===1?1.88:index===3?1.48:index===5?1.30:1.52;
 const extend=(x,y,z,index)=>{
  const t=THREE.MathUtils.clamp((2.92-y)/1.15,0,1),length=lengthFor(index);
  return [x*(1+.075*t),2.92+(y-2.92)*length,z*(1+.05*t)];
 };
 const originalSeams=[];for(const p of parts.filter(p=>p.id.startsWith('skirt-piping-')))for(let i=0;i<p.topologyMesh.positions.length;i+=30)originalSeams.push({position:p.topologyMesh.positions.slice(i,i+3),layer:panelIndex(p.id)});
 const before={};
 for(const part of parts){
  const index=panelIndex(part.id),side=part.id==='skirt-side-left'?0:part.id==='skirt-side-right'?1:null;
  if(index===null&&side===null&&!/^light(?:-cord)?-/.test(part.id))continue;
  const k=index??side??(part.id.startsWith('light--1')||part.id.startsWith('light-cord--1')?0:1);
  const matrix=new THREE.Matrix4().compose(new THREE.Vector3(...part.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)),new THREE.Vector3(...part.scale));
  const data=part.topologyMesh;
  if(part.id.startsWith('skirt-panel-'))before[part.id]=Math.min(...data.positions.filter((_,i)=>i%3===1));
  const isBauble=/^light-/.test(part.id)&&!/^light-cord-/.test(part.id);
  const world=[];const box=new THREE.Box3();
  for(let i=0;i<data.positions.length;i+=3){const p=new THREE.Vector3().fromArray(data.positions,i).applyMatrix4(matrix);world.push(p);box.expandByPoint(p);}
  const center=box.getCenter(new THREE.Vector3()),moved=extend(center.x,center.y,center.z,k);
  // Move hanging baubles with the hem without stretching their round shape.
  for(let i=0;i<world.length;i++){const p=world[i],point=isBauble?[p.x+moved[0]-center.x,p.y+moved[1]-center.y,p.z+moved[2]-center.z]:extend(p.x,p.y,p.z,k);data.positions.splice(i*3,3,...point.map(round));}
  part.position=[0,0,0];part.rotation=[0,0,0];part.scale=[1,1,1];
  if(index!==null||side!==null){part.name=part.name.replace('Layered pointed skirt panel','Festival · extended layered dress panel');part.tailoring={revision:'festival-reference-v11.92',lengthRatio:lengthFor(k),layer:k};}
 }
 const inset=byId('skirt-panel-3');inset.color='#b2e3e0';inset.name='Dress · long pale-cyan pleated inset with teal edging';
 byId('skirt-panel-0').color='#066e83';byId('skirt-panel-1').color='#f6d65c';
 // A real pleated cloth surface: small alternating folds grow away from the
 // sewn waist and settle at the pointed hem instead of merely tinting a flat panel.
 for(const id of ['skirt-panel-0','skirt-panel-1','skirt-panel-3','skirt-panel-5']){
  const part=byId(id),d=part.topologyMesh,index=panelIndex(id);
  for(let i=0;i<d.positions.length/3;i++){
   const u=d.uvs[i*2],v=d.uvs[i*2+1],amount=(index===3?.013:.006)*Math.sin(Math.PI*THREE.MathUtils.clamp(v,0,1))**.6;
   d.positions[i*3+2]=round(d.positions[i*3+2]+Math.sin(u*Math.PI*(index===3?20:12))*amount*(d.positions[i*3+2]>0?1:-1));
  }
 }
 const empty=()=>({positions:[],uvs:[],indices:[]});
 const append=(target,data)=>{const offset=target.positions.length/3;target.positions.push(...data.positions);target.uvs.push(...data.uvs);for(const i of data.indices)target.indices.push(i+offset);};
 const add=(id,name,data,color,material='silk')=>{const part={id,name,kind:'topologyMesh',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color,material,group:'Character',organicSurface:{species:'anime',region:'cloth'},tailoring:{revision:'festival-reference-v11.92',detail:true},topologyMesh:data};parts.push(part);added.push(part);return part;};
 const strand=(path,radius=.0018,rows=24)=>atelierAnimeStrand(path,[radius*.75,radius,radius*.75],rows,8,.72);
 // Resolve the actual baked cloth at a UV location, including its fold relief.
 // Front/back duplicates prefer the outer face so stitches never sit inside lining.
 const sample=(part,u,v,offset=.004)=>{
  const d=part.topologyMesh;let best=Infinity,p=[0,0,0];
  for(let i=0;i<d.uvs.length;i+=2){const score=(d.uvs[i]-u)**2+(d.uvs[i+1]-v)**2;
   if(score<best-1e-10||(Math.abs(score-best)<1e-10&&d.positions[i/2*3+2]>p[2])){best=score;p=d.positions.slice(i/2*3,i/2*3+3);}}
  p[2]+=offset;return p;
 };
 const pleats=empty();
 for(let column=1;column<12;column++){
  const u=column/12,path=[];for(let row=1;row<=27;row++)path.push(sample(inset,u,row/29,.005));
  append(pleats,strand(path,column%3===0?.0024:.0013,40));
 }
 add('girl-dress-inset-pleat-seams','Dress · eleven individually sewn cyan inset pleats',pleats,'#65b9bd');
 const embroidery=empty(),running=empty();
 for(const panelId of ['skirt-panel-0','skirt-panel-1','skirt-panel-3']){
  const panel=byId(panelId);
  for(let row=1;row<=5;row++)for(let column=1;column<=3;column++){
   const u=column/4,v=.14+row*.115,du=.025,dv=.025,path=[[u,v-dv],[u+du,v],[u,v+dv],[u-du,v],[u,v-dv]].map(([a,b])=>sample(panel,a,b,.008));
   append(embroidery,strand(path,.0012,16));
  }
  for(const edge of [.055,.945])for(let stitch=2;stitch<33;stitch++){
   const a=sample(panel,edge,(stitch-.25)/36,.007),b=sample(panel,edge,(stitch+.25)/36,.007);append(running,strand([a,b],.00085,4));
  }
 }
 add('girl-dress-brocade-diamonds','Dress · forty-five raised diamond brocade motifs',embroidery,'#e9d9a9');
 add('girl-dress-running-stitches','Dress · tailored double rows of fine running stitches',running,'#e6f5e8');
 // Soft pastel baubles follow the ivory diagonal apron edge seen in the
 // reference. Each is a closed, editable round mesh with a tiny sewn loop.
 const apron=byId('skirt-panel-2'),colors=['#d7f1e8','#f8d0df','#f5e5a5','#d4d8f6'];
 for(let i=0;i<15;i++){
  const u=.10+i*.055,v=.76,p=sample(apron,u,v,.025),r=.012+(i%3)*.0015;
  const sphere=new THREE.SphereGeometry(r,14,10);sphere.translate(...p);
  const data={positions:Array.from(sphere.attributes.position.array,round),uvs:Array.from(sphere.attributes.uv.array,round),indices:Array.from(sphere.index.array)};sphere.dispose();
  add('girl-dress-pastel-bauble-'+i,'Dress · pastel hem ornament '+(i+1),data,colors[i%colors.length],'silk');
  add('girl-dress-bauble-loop-'+i,'Dress · sewn ornament loop '+(i+1),strand([[p[0],p[1]+.025,p[2]-.008],[p[0],p[1]+r,p[2]]],.0014,6),'#e4d9b8');
 }
 const gold=byId('skirt-panel-1'),goldTip=sample(gold,.50,.985,.013),tassel=empty();
 for(let i=0;i<5;i++)append(tassel,atelierAnimeStrand([[goldTip[0]+(i-2)*.003,goldTip[1],goldTip[2]],[goldTip[0]+(i-2)*.005,goldTip[1]-.07-(i%2)*.015,goldTip[2]+.01]],[.0018,.0016,.0005],12,8,.72));
 // The tapered hem tassel is separate from the yellow cloth so the owner can
 // select/recolor it without changing the native dress panel.
 add('girl-dress-gold-tail-tassel','Dress · fine gold pointed-tail fringe',tassel,'#e3be55','metal');
 // Keep the existing broad tailoring object as the original bodice seam;
 // skirt stitches now have their own correctly lengthened owner above.
 const oldStitches=byId('girl-tailoring-stitches');if(oldStitches){oldStitches.name='Costume · fitted bodice and extended panel seam stitches';const d=oldStitches.topologyMesh;for(let i=0;i<d.positions.length;i+=3){const p=d.positions.slice(i,i+3);if(p[1]>2.925)continue;let nearest=Infinity,layer=0;for(const seam of originalSeams){const distance=p.reduce((sum,v,k)=>sum+(v-seam.position[k])**2,0);if(distance<nearest){nearest=distance;layer=seam.layer;}}d.positions.splice(i,3,...extend(...p,layer).map(round));}}
 model.meshGroups=model.meshGroups||[];
 for(let i=0;i<added.length;i+=30){const members=added.slice(i,i+30).map(p=>p.id);if(members.length>=2)model.meshGroups.push({id:'festival-dress-detail-'+i,name:'Festival dress · tailoring '+(i/30+1),members});}
 model.festivalDress={revision:'festival-reference-v11.92',style:'long asymmetric layered festival dress',referenceFeatures:['ivory wrap','dark teal outer panel','pale cyan pleated inset','long yellow pointed tail','pastel sewn ornaments','raised brocade and running stitches'],originalHemByPanel:before,detailParts:added.map(p=>p.id),pleatSeams:11,brocadeMotifs:45,pastelBaubles:15};
 return project;
}
