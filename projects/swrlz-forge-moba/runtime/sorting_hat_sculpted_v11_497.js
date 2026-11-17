const se497SculptedHatId='sorting-hat-sculpted';
let se497HatLoading=false;
function se497DeformHat(scene){
const project=scene?.project,model=project?.modelAtelier;
const part=model?.parts?.[0],mesh=part?.topologyMesh;
if(project?.canonicalId!=='sorting-hat'||model?.parts?.length!==1||
part?.kind!=='topologyMesh'||mesh?.positions?.length!==7859*3||
mesh?.uvs?.length!==7859*2||mesh?.indices?.length!==15714*3||
typeof part.uvPaintPNG!=='string')
throw Error('Expected the verified single-cloth Sorting Hat starter.');
const coords=mesh.positions, before=coords.slice(), TAU=Math.PI*2;
const smooth=(a,b,t)=>{const v=Math.max(0,Math.min(1,(t-a)/(b-a)));return v*v*(3-2*v);};
const gauss=(a,b,s)=>Math.exp(-Math.pow((a-b)/s,2));
const STRIDE=97, ROWS=81, N=96, means=[];
for(let row=0;row<ROWS;row++){
let x=0,z=0;
for(let j=0;j<N;j++){const k=(row*STRIDE+j)*3;x+=before[k];z+=before[k+2];}
means.push([x/N,z/N]);
}
for(let row=0;row<ROWS;row++){
for(let j=0;j<=N;j++){
const k=(row*STRIDE+j)*3;
const x=before[k],y=before[k+1],z=before[k+2];
const theta=-Math.PI/2+TAU*j/N;
const c=Math.cos(theta),s=Math.sin(theta);
const front=Math.pow(Math.max(0,s),4);
const back=Math.pow(Math.max(0,-s),3);
const wave=Math.sin(3*theta+2.65*y);
const lean=smooth(2.45,4.08,y);
let dx=0,dy=0,dz=0;
if(row<60){
const band1=y-(.60+.084*Math.sin(2*theta+1.4));
const band2=y-(.89+.120*Math.sin(3*theta-.5));
const band3=y-(2.31+.145*Math.sin(2*theta+1.0));
const band4=y-(2.65+.085*Math.sin(4*theta-.7));
const crease =
.090*gauss(band1,0,.080)-.052*gauss(band1-.085,0,.050)
+.075*gauss(band2,0,.089)-.050*gauss(band2+.080,0,.044)
+.115*gauss(band3,0,.105)-.074*gauss(band3+.120,0,.068)
+.071*gauss(band4,0,.092)-.047*gauss(band4+.076,0,.053);
const preserveFace=1-.73*front*gauss(y,1.50,.54);
const sideFlutter=(.020*Math.sin(11*theta+5.1*y)+
.014*Math.sin(17*theta-3.9*y));
const faceMouth=gauss(y,1.105+.065*x,.072)*gauss(x,0,.52)*front;
const mouthCorner=gauss(Math.abs(x),.46,.12)*gauss(y,1.07,.12)*front;
const brow=gauss(y,1.875,.110)*(
gauss(x,-.355,.24)+gauss(x,.355,.24))*front;
const eye=gauss(y,1.655,.14)*(
gauss(x,-.355,.20)+gauss(x,.355,.20))*front;
let radial=preserveFace*(crease+sideFlutter*(1-.70*lean)
+.027*wave*gauss(y,2.07,.76))
+.027*brow-.026*eye-.022*faceMouth+.030*mouthCorner;
dx += .68*lean-.075*gauss(y,3.32,.30);
dz += .10*lean-.065*Math.sin(theta+1.0)*gauss(y,3.18,.40);
dy -= .25*smooth(3.22,4.08,y);
const squash=1-.065*gauss(y,2.78,.32);
dx += c*radial*squash;
dz += .93*s*radial*squash;
dy += preserveFace*(.022*wave*gauss(y,2.30,.80));
if(y>3.72){const blend=smooth(3.72,4.08,y);dx-=c*radial*blend;dz-=.93*s*radial*blend;}
}else if(row<73){
const radius=Math.hypot(x,z/.90);
const edge=smooth(.87,1.66,radius);
const ripple=.082*Math.sin(3*theta+.55)+.062*Math.sin(5*theta-1.35)
+.045*Math.sin(2*theta+1.7);
dx += c*edge*(.035*Math.sin(4*theta+.8)+.018*Math.sin(9*theta));
dz += .90*s*edge*(.035*Math.sin(4*theta+.8)+.018*Math.sin(9*theta));
dy += edge*ripple;
}else{
dx += .68*smooth(2.45,4.08,y)-.075*gauss(y,3.32,.30);
dz += .10*smooth(2.45,4.08,y);
}
coords[k]=Math.round((x+dx)*1e5)/1e5;
coords[k+1]=Math.round((y+dy)*1e5)/1e5;
coords[k+2]=Math.round((z+dz)*1e5)/1e5;
}
}
const apex=7857*3,liner=7858*3;
coords[apex]=Math.round((before[apex]+.68)*1e5)/1e5;
coords[apex+1]=Math.round((before[apex+1]-.25)*1e5)/1e5;
coords[apex+2]=Math.round((before[apex+2]+.10)*1e5)/1e5;
coords[liner]=Math.round((before[liner]+.68*smooth(2.45,4.08,before[liner+1])
-.075*gauss(before[liner+1],3.32,.30))*1e5)/1e5;
coords[liner+2]=Math.round((before[liner+2]+.10*smooth(2.45,4.08,before[liner+1]))*1e5)/1e5;
part.id='sorting-hat-sculpted-cloth';
part.name='Sorting Hat · expressive single-surface sculpt';
part.group='One connected woven cloth mesh';
project.canonicalId=se497SculptedHatId;
project.template=se497SculptedHatId;
project.name='The Sorting Hat · Sculpted';
model.name='The Sorting Hat · Sculpted Cloth';
model.reference='Alternative original Sorting Hat starter: one continuous, sealed, editable UV-painted cloth surface. Deformed crown folds, side-bent tip, asymmetric double-sided brim and integrated facial recesses are vertex geometry, not assembled objects or texture-only fake folds. The original Sorting Hat starter is preserved.';
model.editedAt='local';
if(!Array.isArray(scene.scene?.actors)||model.parts.length!==1)throw Error('Invalid sculpted starter scene.');
if(coords.some(n=>!Number.isFinite(n)||Math.abs(n)>20))throw Error('Invalid sculpted geometry.');
return scene;
}
async function se497OpenSculptedHat(force=false){
if(se497HatLoading)return false;
if(dirty&&!force&&!confirm('Open sculpted Sorting Hat and discard unsaved changes?'))return false;
se497HatLoading=true;
try{
toast('Sculpting one continuous Sorting Hat mesh…');
const url=new URL('scenes/model-atelier-sorting-hat.swyrl.json',document.baseURI);
const response=await fetch(url.href,{cache:'no-cache'});
if(!response.ok)throw Error('Sorting Hat source asset HTTP '+response.status);
const scene=await response.json();
se483ValidateSortingHat(scene);
se497DeformHat(scene);
if(typeof ModelAtelier?.close!=='function'||typeof loadProject!=='function')
throw Error('Native Model Studio is unavailable.');
ModelAtelier.close();
loadProject(scene,{workspaceLocal:true});
if(currentProject?.canonicalId!==se497SculptedHatId||
currentProject?.modelAtelier?.parts?.length!==1)
throw Error('Sculpted project failed to load into native Model Studio.');
se232ActivateSelectedModelWorkspace();
if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
ModelAtelier.syncProject();
if(!ModelAtelier.status()?.open)throw Error('Model Studio did not open.');
initializeHistory('Opened Sculpted Sorting Hat native starter');
markSaved();
document.getElementById('projectHub')?.classList.remove('show');
requestAnimationFrame(()=>requestAnimationFrame(()=>window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('three')));
toast('Sculpted Sorting Hat · one editable cloth mesh ready');
return true;
}catch(error){
console.error('§E sculpted Sorting Hat load failed',error);
toast('Sculpted Sorting Hat failed: '+String(error?.message||error).slice(0,150));
return false;
}finally{se497HatLoading=false;}
}
const se497PreviousTemplateCreate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
if(template===se497SculptedHatId)return se497OpenSculptedHat(force);
return se497PreviousTemplateCreate(template,force);
};
function se497InstallStarterCard(){
const hub=document.getElementById('projectHub');
if(!hub||hub.dataset.se497SculptedInstalled)return;
hub.dataset.se497SculptedInstalled='true';
hub.addEventListener('click',event=>{
const button=event.target?.closest?.('button[data-project-template="sorting-hat-sculpted"]');
if(!button)return;
event.preventDefault();event.stopImmediatePropagation();
void se497OpenSculptedHat();
},true);
}
if(document.readyState==='loading')
document.addEventListener('DOMContentLoaded',se497InstallStarterCard,{once:true});
else se497InstallStarterCard();
window.SWYRL_ENGINE_SORTING_HAT_SCULPTED_497=Object.freeze({
open:se497OpenSculptedHat,deform:se497DeformHat,
status:()=>({busy:se497HatLoading,active:currentProject?.canonicalId===se497SculptedHatId,
cardExists:!!document.querySelector('button[data-project-template="sorting-hat-sculpted"]')})
});
/* SE497_SCULPTED_SORTING_HAT_END */
