// Original native-edit design recipe. World forward is +Z; all dimensions are in model units.
export const design=[];
const sphere=(name,position,scale,tile='fur',extra={})=>design.push({name,kind:'sphere',position,scale,tile,...extra});
const loft=(name,path,radii,tile='fur',extra={})=>design.push({name,kind:'loft',position:[0,0,0],scale:[1,1,1],path,radii,tile,...extra});
const box=(name,position,scale,tile='leather',extra={})=>design.push({name,kind:'box',position,scale,tile,...extra});
// Compact quadruped body; a proud tilted head and four deliberately shaped limbs.
sphere('Fox · ribcage',[0,1.35,-.14],[.49,.57,.78]);
sphere('Fox · proud breast',[0,1.73,.34],[.40,.56,.41],'ivory');
sphere('Fox · cranial planes',[0,2.40,.48],[.46,.40,.40]);
sphere('Fox · nasal bridge',[0,2.33,.75],[.23,.18,.32],'ivory');
for(const s of [-1,1]){
 sphere('Fox · muzzle lobe '+s,[s*.105,2.27,.87],[.17,.12,.24],'ivory');
 sphere('Fox · haunch '+s,[s*.35,1.04,-.61],[.30,.44,.33]);
 loft('Fox · foreleg '+s,[[s*.28,1.58,.4],[s*.33,1.06,.50],[s*.35,.53,.47],[s*.36,.25,.58]],[.14,.12,.075,.09]);
 loft('Fox · hock '+s,[[s*.36,1.11,-.61],[s*.49,.75,-.43],[s*.44,.48,-.81],[s*.41,.20,-.65]],[.18,.135,.08,.09]);
 for(const [leg,z] of [['front',.63],['back',-.60]]){
  sphere('Paw · '+leg+' '+s,[s*(leg==='front'?.36:.41),.16,z],[.18,.14,.24],'lapis');
  for(let t=-1;t<=1;t++){
   sphere('Toe · '+leg+' '+s+' '+t,[s*(leg==='front'?.36:.41)+t*.088,.12,z+.15],[.065,.075,.12],'fur');
   sphere('Claw · '+leg+' '+s+' '+t,[s*(leg==='front'?.36:.41)+t*.088,.095,z+.244],[.022,.025,.047],'brass');
  }
 }
 loft('Ear · outer '+s,[[0,0,0],[s*.11,.37,-.02],[s*.16,.65,-.08]],[.205,.135,.002],'fur',{position:[s*.29,2.65,.36],scale:[1,1,.55]});
 loft('Ear · velvet '+s,[[0,.035,.12],[s*.10,.36,.08],[s*.15,.57,-.015]],[.145,.087,.0015],'cloth',{position:[s*.29,2.65,.36],scale:[1,1,.55]});
 for(let i=0;i<3;i++)loft('Ruff · cheek '+s+' '+i,[[s*.26,2.35-i*.10,.43],[s*(.43+i*.04),2.29-i*.10,.47],[s*(.56+i*.025),2.16-i*.12,.41]],[.13-i*.014,.12-i*.018,.0015],'ivory');
 sphere('Eye · dark almond '+s,[s*.245,2.48,.785],[.145,.090,.045],'lapis',{rotation:[0,s*.22,-s*.17],hd:'eye'});
 sphere('Eye · amber iris '+s,[s*.250,2.48,.824],[.066,.080,.020],'amber',{rotation:[0,s*.16,-s*.10],material:'gloss'});
 sphere('Eye · vertical pupil '+s,[s*.248,2.48,.845],[.018,.055,.010],null,{color:'#0b152b',material:'gloss'});
 sphere('Eye · catchlight '+s,[s*.236,2.507,.858],[.012,.015,.008],null,{color:'#fff9de',material:'emissive'});
 loft('Face · expressive brow '+s,[[s*.14,2.61,.774],[s*.26,2.64,.77],[s*.36,2.60,.72]],[.013,.026,.004],'ivory');
 loft('Face · smile corner '+s,[[0,2.215,1.02],[s*.12,2.20,1.01],[s*.23,2.24,.96]],[.004,.007,.002],null,{color:'#182b3c'});
}
sphere('Nose · graphite leather',[0,2.31,1.081],[.105,.073,.075],null,{color:'#102335',material:'gloss'});
loft('Nose · philtrum',[[0,2.28,1.08],[0,2.22,1.04]],[.006,.004],null,{color:'#182b3c'});
for(let i=0;i<5;i++)loft('Chest · fur blade '+i,[[(i-2)*.09,1.95,.59],[(i-2)*.10,1.65,.70],[(i-2)*.07,1.34,.55]],[.09,.095,.002],'ivory',{position:[0,0,.52],scale:[1,1,.18]});
// A large asymmetrical comet tail gives the character its recognisable silhouette.
loft('Comet · flowing tail',[[0,1.25,-.83],[.67,1.12,-1.02],[1.24,1.47,-.89],[1.62,2.09,-.63],[1.58,2.62,-.43],[1.25,2.98,-.25],[.89,3.13,-.10]],[.15,.29,.34,.31,.25,.15,.002],'fur');
loft('Comet · ivory inner sweep',[[.53,1.15,-.78],[1.09,1.45,-.65],[1.42,2.03,-.42],[1.43,2.59,-.21],[1.14,2.98,-.03],[.88,3.13,.0]],[.12,.20,.21,.17,.10,.002],'ivory');
loft('Comet · luminous leading edge',[[1.12,1.55,-.52],[1.51,2.11,-.35],[1.51,2.62,-.20],[1.23,3.02,-.04],[.88,3.14,.035]],[.045,.065,.07,.045,.001],'comet',{material:'emissive'});
for(let i=0;i<5;i++)loft('Comet · swept fur lock '+i,[[.98+i*.07,1.45+i*.19,-.64],[1.47+i*.025,1.75+i*.20,-.44],[1.67-i*.04,2.11+i*.19,-.32]],[.12,.14,.0015],i%2?'comet':'fur');
// Teal travelling mantle, leather harness and stitched satchel.
for(const s of [-1,1]){
 loft('Cape · shoulder fold '+s,[[s*.22,1.99,.16],[s*.46,1.82,-.08],[s*.57,1.42,-.44],[s*.46,1.09,-.72]],[.17,.25,.27,.04],'cloth',{scale:[1,1,.76],hd:'cloth',surface:'fabric-panel'});
 loft('Cape · gilded hem '+s,[[s*.30,1.94,.20],[s*.57,1.72,-.02],[s*.63,1.40,-.31],[s*.48,1.10,-.53]],[.016,.016,.014,.008],'brass');
 loft('Harness · collar '+s,[[0,1.92,.67],[s*.38,1.95,.36],[s*.40,1.98,.02],[0,2.03,-.08]],[.045,.045,.045,.045],'leather');
}
loft('Harness · diagonal strap',[[-.38,1.94,.41],[0,1.69,.75],[.48,1.22,.35]],[.055,.055,.055],'leather',{scale:[1,1,.95]});
box('Satchel · rounded body',[-.56,1.14,-.18],[.28,.48,.48],'leather',{rotation:[.08,0,-.10]});
box('Satchel · teal flap',[-.70,1.27,-.18],[.025,.25,.50],'cloth',{rotation:[.08,0,-.10]});
box('Satchel · gold clasp',[-.725,1.20,.04],[.035,.09,.075],'brass');
for(const z of [-.37,.02])loft('Satchel · stitched edge '+z,[[-.713,1.47,z],[-.738,1.23,z],[-.713,.96,z]],[.009,.009,.009],'brass');
sphere('Badge · compass disc',[0,1.91,.729],[.105,.105,.022],'brass',{material:'metal'});
for(const k of [-1,1])loft('Badge · compass needle '+k,[[0,1.91,.755],[k*.065,1.91+k*.065,.755]],[.018,.0015],'comet',{material:'emissive'});
// Rolled parchment and an articulated brass-and-blue lantern.
loft('Scroll · parchment roll',[[-.60,1.52,-.47],[-.60,1.52,-.02]],[.085,.085],'ivory');
for(const z of [-.43,-.06])sphere('Scroll · endcap '+z,[-.60,1.52,z],[.105,.105,.025],'brass');
loft('Lantern · hanging loop',[[.42,1.45,.32],[.65,1.40,.35],[.72,1.22,.36]],[.012,.012,.012],'brass');
sphere('Lantern · blue glass',[.72,1.06,.36],[.095,.17,.095],'comet',{material:'emissive'});
for(const y of [.88,1.24])sphere('Lantern · brass rim '+y,[.72,y,.36],[.12,.027,.12],'brass',{material:'metal'});
for(const x of [-1,1])loft('Lantern · frame '+x,[[.72+x*.09,.91,.36],[.72+x*.105,1.07,.36],[.72+x*.09,1.22,.36]],[.012,.012,.012],'brass');
// Detached stardust sits close to the comet tip rather than obscuring the face.
for(let i=0;i<5;i++)sphere('Stardust · '+i,[1.06+i*.12,3.11+(i%2)*.17,-.02],[.017+i*.004,.017+i*.004,.017+i*.004],'comet',{material:'emissive'});
