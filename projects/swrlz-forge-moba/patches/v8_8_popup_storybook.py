"""v8.8: Anime Studio 3D pop-up storybook, individually authorable wizard cels.

Continues the existing project; does not overwrite other starter projects.
Configurations are kept under project.animePopUp so Save/Load exports them.
All art is drawn as native CanvasTextures. No remote images or paid runtimes.
"""
def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError("v8.8 integration anchor missing/ambiguous "+a[:90])
    return s.replace(a,b,1)
CSS=r"""
<style id="animePopUpCss">
.anime-director-button{position:fixed;right:16px;bottom:59px;z-index:81;background:#362442;
 border:1px solid #c8a276;border-radius:9px;padding:10px;color:#fff1d5;font-weight:700;font-size:12px}
.anime-director-button[hidden]{display:none!important}
.anime-director{position:fixed;z-index:440;top:8vh;right:12px;width:min(360px,94vw);max-height:82dvh;
 overflow:auto;background:#101322f5;color:#f5e6cf;border:1px solid #ad8966;box-shadow:0 15px 55px #000c;
 border-radius:14px;padding:15px;font:13px system-ui}
.anime-director[hidden]{display:none!important}
.anime-director header{display:flex;align-items:center;justify-content:space-between;gap:8px}
.anime-director header strong{font-size:16px}
.anime-director button{background:#282a42;color:#e9e5ec;border:1px solid #9988aa;border-radius:6px;padding:7px 11px}
.anime-director p{font-size:11px;line-height:1.4;color:#dac5a7}
.anime-director label{display:flex;justify-content:space-between;gap:8px;padding:6px 0;align-items:center}
.anime-director input[type=range]{width:150px;accent-color:#d5a864}
.anime-director select{width:100%;padding:9px;background:#1b2634;color:#ffe5c3;border:1px solid #978466}
.anime-director .readout{min-width:45px;text-align:right;font-variant-numeric:tabular-nums}
.anime-director footer{display:flex;justify-content:space-between;margin-top:9px;gap:6px}
@media(max-width:640px){.anime-director{top:16dvh;right:3vw;max-height:70dvh}.anime-director-button{right:8px;bottom:61px}}
</style>
"""
JS=r"""
// The saved project's paper-theatre data is independent of camera movement.
// Every layer is a separate draw plane. Both wizards are separate cels.
const ANIME_POP_KEYS=['background','atmosphere','midground','kami','swyrlz','guardian','effects','foreground'];
const ANIME_POP_DEFAULT={
  background:{depth:-21,offsetX:0,parallax:.05,delay:0,duration:1.8},
  atmosphere:{depth:-16,offsetX:0,parallax:.13,delay:.28,duration:1.7},
  midground:{depth:-9,offsetX:0,parallax:.31,delay:.55,duration:1.5},
  kami:{depth:-.65,offsetX:1.32,parallax:.56,delay:1.05,duration:1.4},
  swyrlz:{depth:-.45,offsetX:-1.48,parallax:.68,delay:1.4,duration:1.2},
  guardian:{depth:-2,offsetX:0,parallax:.4,delay:1.6,duration:1.2},
  effects:{depth:1,offsetX:0,parallax:.8,delay:1.8,duration:1.0},
  foreground:{depth:4.2,offsetX:0,parallax:.96,delay:2.1,duration:1.0}
};
const ANIME_POP_LIMITS={depth:[-28,6],offsetX:[-4,4],parallax:[0,1.5],delay:[0,4],duration:[.25,4]};
function animePopSanitize(config){
  const input=config&&typeof config==='object'?config:{},raw=input.layers||{};
  const layers={};
  for(const id of ANIME_POP_KEYS){
    const original=raw[id]&&typeof raw[id]==='object'?raw[id]:{},base=ANIME_POP_DEFAULT[id],out={};
    for(const key of Object.keys(base)){
      const candidate=Number(original[key]),v=Number.isFinite(candidate)?candidate:base[key],
        [lo,hi]=ANIME_POP_LIMITS[key];out[key]=Math.max(lo,Math.min(hi,v));
    }layers[id]=out;
  }
  return {schema:'anime-popup-v1',layers};
}
function animePopConfig(){
  if(!currentProject||currentProject.canonicalId!=='ghosts-different-forms-ep01')
    return animePopSanitize({});
  if(!currentProject.animePopUp||currentProject.animePopUp.schema!=='anime-popup-v1')
    currentProject.animePopUp=animePopSanitize(currentProject.animePopUp);
  return currentProject.animePopUp;
}
function animePopEase(v){const t=Math.max(0,Math.min(1,v));return t*t*(3-2*t)}
function animePopRise(key,local){
  const config=animePopConfig().layers[key],progress=animePopEase((local-config.delay)/config.duration);
  return progress;
}
// Drawing helpers use stroke and shapes so the artwork is asset-free and portable.
function popStroke(c,color='#2c1d22',width=7){
  c.strokeStyle=color;c.lineWidth=width;c.lineJoin='round';c.lineCap='round';
}
function popPath(c,points,color,outline='#2b1821',width=5){
  c.beginPath();c.moveTo(points[0][0],points[0][1]);
  for(let i=1;i<points.length;i++)c.lineTo(points[i][0],points[i][1]);
  c.closePath();c.fillStyle=color;c.fill();if(outline){popStroke(c,outline,width);c.stroke()}
}
function popCurl(c,x,y,s=1){
  c.save();c.translate(x,y);c.scale(s,s);
  popStroke(c,'#d89b4f99',8);c.beginPath();c.moveTo(0,110);
  c.bezierCurveTo(-70,65,75,65,14,12);c.bezierCurveTo(-38,-22,-12,-75,50,-105);c.stroke();
  c.strokeStyle='#ffdc9f66';c.lineWidth=3;c.beginPath();c.moveTo(6,90);
  c.bezierCurveTo(-40,48,61,47,17,10);c.stroke();c.restore();
}
function popRune(c,x,y,r){
  c.save();c.translate(x,y);popStroke(c,'#b88656bd',3);
  c.beginPath();c.arc(0,0,r,0,7);c.stroke();c.beginPath();c.arc(0,0,r*.7,0,7);c.stroke();
  for(let i=0;i<9;i++){const a=i*Math.PI*2/9;c.beginPath();c.moveTo(Math.cos(a)*r*.72,Math.sin(a)*r*.72);
    c.lineTo(Math.cos(a)*r*1.2,Math.sin(a)*r*1.2);c.stroke()}
  c.restore();
}
function popBackArt(c,w,h){
  const g=c.createLinearGradient(0,0,0,h);g.addColorStop(0,'#080c16');g.addColorStop(.5,'#242234');g.addColorStop(1,'#785040');
  c.fillStyle=g;c.fillRect(0,0,w,h);
  const glow=c.createRadialGradient(455,168,25,455,168,240);
  glow.addColorStop(0,'#d49a5266');glow.addColorStop(1,'#d49a5200');c.fillStyle=glow;c.fillRect(200,0,500,450);
  for(let i=0;i<9;i++){
    const x=i*103-90,roof=83+(i*43)%160;
    popPath(c,[[x,h],[x,roof+58],[x+41,roof],[x+80,roof+55],[x+80,h]],i%2?'#171724':'#22202b','#7d594459',5);
    c.fillStyle='#dca35b77';
    for(let y=roof+90;y<h-28;y+=61)for(let j=0;j<2;j++)if((j+y+i)%4!==0)c.fillRect(x+18+j*30,y,12,26);
  }
  popRune(c,450,138,83);
  for(let i=0;i<60;i++){const x=(i*107)%w,y=(i*83)%(h*.7);c.fillStyle=i%4?'#ddac74':'#ffeac2';c.fillRect(x,y,1+i%2,1+i%2)}
}
function popCathedralArt(c,w,h){
  c.clearRect(0,0,w,h);
  for(let i=0;i<5;i++){
    const x=36+i*167,base=h-20;
    c.fillStyle='#1b1c28';popStroke(c,'#977250',8);
    c.beginPath();c.moveTo(x,base);c.lineTo(x,150);c.quadraticCurveTo(x+80,-10,x+160,150);
    c.lineTo(x+160,base);c.closePath();c.fill();c.stroke();
    c.fillStyle='#0a0e1d';c.beginPath();c.moveTo(x+32,base);
    c.lineTo(x+32,165);c.quadraticCurveTo(x+80,70,x+128,165);
    c.lineTo(x+128,base);c.closePath();c.fill();
    popStroke(c,'#c48a46',3);
    for(let y=205;y<h-25;y+=59){c.beginPath();c.moveTo(x+30,y);c.lineTo(x+131,y);c.stroke()}
  }
  c.fillStyle='#855b38';
  for(let i=0;i<4;i++){c.fillRect(i*182+145,30,8,156);c.fillRect(i*182+164,30,5,116)}
  for(let i=0;i<3;i++)popCurl(c,165+i*248,211+i*18,.44);
}
function popWorkshopArt(c,w,h){
  c.clearRect(0,0,w,h);
  c.fillStyle='#28202a';popStroke(c,'#a07646',7);
  c.fillRect(15,160,192,310);c.strokeRect(15,160,192,310);
  c.fillRect(568,160,185,310);c.strokeRect(568,160,185,310);
  for(const x of [20,574]){
    for(let y=240;y<460;y+=105){c.strokeStyle='#966439';c.lineWidth=12;c.beginPath();c.moveTo(x,y);c.lineTo(x+170,y);c.stroke();
      for(let j=0;j<7;j++){let a=x+14+j*24;c.fillStyle=['#694c36','#c58e50','#38344a'][j%3];
        c.fillRect(a,y-44,16,40);c.fillStyle='#e5b26f';c.fillRect(a+3,y-30,2,16)}}
  }
  c.fillStyle='#32242c';c.beginPath();c.ellipse(385,460,250,52,0,0,7);c.fill();
  c.fillStyle='#6e4430';c.fillRect(125,451,530,45);c.fillRect(175,490,40,87);c.fillRect(564,490,40,87);
  popRune(c,380,110,70);
  for(let i=0;i<7;i++){const x=80+i*101;c.fillStyle='#c88c4d';c.beginPath();c.arc(x,448,6,0,7);c.fill()}
}
function popDeskArt(c,w,h){
  c.clearRect(0,0,w,h);
  popPath(c,[[6,314],[66,249],[700,248],[763,310],[763,454],[6,454]],'#4c2d27','#c48b55',11);
  for(let j=0;j<6;j++){c.fillStyle=j%2?'#e1bb80':'#b99267';c.fillRect(55,313+j*15,650,7)}
  for(let i=0;i<5;i++){const x=105+i*105,ht=105+i%3*19;
    c.fillStyle='#271f2b';c.fillRect(x,145,41,ht);popStroke(c,'#986d43',5);c.strokeRect(x,145,41,ht);
    c.fillStyle='#d69e54';c.fillRect(x+11,164,18,7)}
  popPath(c,[[504,227],[545,131],[595,225],[565,271]],'#e2ac62','#e7c997',6);
  popRune(c,328,205,45);
  popCurl(c,218,230,.45);popCurl(c,652,205,.42);
}
function popKamiArt(c,w,h){
  c.clearRect(0,0,w,h);
  // Tall imposing hooded horn wizard from the user's charcoal fantasy concepts.
  c.save();
  popPath(c,[[100,712],[68,570],[91,415],[164,330],[335,323],[431,401],[464,710]],'#261f2a','#110f1b',11);
  for(let j=0;j<4;j++){popStroke(c,'#96704d',5);c.beginPath();c.moveTo(140+j*46,390);c.lineTo(93+j*77,687);c.stroke()}
  popPath(c,[[175,364],[210,439],[259,478],[309,423],[348,351]],'#7a573e','#c39b68',5);
  // Tall hood, mature face, hair fully covering hairline.
  popPath(c,[[130,330],[105,204],[154,105],[265,79],[358,132],[384,276],[348,371]],
    '#312734','#b68e60',9);
  popPath(c,[[138,163],[92,56],[178,105],[181,143]],'#80634f','#cda376',8);
  popPath(c,[[329,145],[397,48],[418,145],[377,194]],'#80634f','#d1a16f',8);
  c.fillStyle='#d7ae85';popStroke(c,'#2d1d21',7);
  c.beginPath();c.moveTo(160,222);c.quadraticCurveTo(239,150,339,210);c.lineTo(323,341);
  c.quadraticCurveTo(251,391,179,336);c.closePath();c.fill();c.stroke();
  for(let i=0;i<7;i++){
    const x=145+i*30,y=143+(i%3)*15;popStroke(c,i%2?'#463b3c':'#ad8d76',17-i%3*3);
    c.beginPath();c.moveTo(x,y);c.quadraticCurveTo(x+14,215,x-12,244+(i%3)*11);c.stroke();
  }
  c.fillStyle='#2c2631';c.beginPath();c.ellipse(207,276,14,10,0,0,7);
  c.ellipse(291,274,14,10,0,0,7);c.fill();
  popStroke(c,'#7f4741',5);c.beginPath();c.moveTo(233,324);c.quadraticCurveTo(258,335,280,321);c.stroke();
  // Ring brooch, leather belts and inked stitched garment details.
  popRune(c,254,426,34);
  popStroke(c,'#ddac6b',8);c.beginPath();c.moveTo(133,532);c.lineTo(380,552);c.moveTo(142,619);c.lineTo(381,647);c.stroke();
  c.fillStyle='#a87945';for(let j=0;j<6;j++)c.fillRect(170+j*39,540,17,16);
  // Staff and burning skull, engraved with magical arcs.
  popStroke(c,'#b78b5e',19);c.beginPath();c.moveTo(433,688);c.lineTo(398,132);c.stroke();
  popStroke(c,'#e7bf78',6);c.beginPath();c.moveTo(433,688);c.lineTo(398,132);c.stroke();
  c.fillStyle='#d19a54';c.beginPath();c.ellipse(398,91,58,62,0,0,7);c.fill();
  c.fillStyle='#3b2830';c.beginPath();c.ellipse(380,79,12,16,0,0,7);c.ellipse(417,79,12,16,0,0,7);c.fill();
  for(let i=0;i<4;i++)popCurl(c,395+(i-2)*18,55,.28);
  c.restore();
}
function popSwyrlzArt(c,w,h){
  c.clearRect(0,0,w,h);c.save();
  // Compact book-wielding skeletal companion in asymmetric mage garments.
  popPath(c,[[108,641],[96,426],[163,357],[324,366],[400,438],[402,630],
    [342,595],[306,658],[233,607],[173,674]],'#292332','#e0a662',10);
  for(let i=0;i<5;i++){popStroke(c,'#aa8654',4);c.beginPath();c.moveTo(146+i*45,445);c.lineTo(102+i*66,622);c.stroke()}
  c.fillStyle='#e3d7b5';popStroke(c,'#282130',8);
  c.beginPath();c.ellipse(251,292,91,104,0,0,7);c.fill();c.stroke();
  c.fillStyle='#291f2e';c.beginPath();c.ellipse(222,282,23,33,0,0,7);c.ellipse(277,282,23,33,0,0,7);c.fill();
  popPath(c,[[230,334],[248,320],[263,335]],'#53414b',null);
  // Deliberately pointed wizard hat and gold trim, not a mistaken 'halo'.
  popPath(c,[[128,234],[176,119],[335,95],[401,253],[360,269]],'#2d2230','#d4a261',11);
  popPath(c,[[120,221],[226,182],[334,216],[424,250],[345,274],[200,256]],'#483446','#e9ba6a',8);
  popPath(c,[[192,137],[275,27],[323,170]],'#503748','#c79b60',7);
  // Hovering magic grimoire, at an independent position in this character cel.
  popPath(c,[[65,439],[156,429],[234,471],[233,557],[153,531],[54,559]],'#d1b18a','#261e29',8);
  popPath(c,[[234,471],[309,433],[408,439],[428,557],[335,535],[233,557]],'#e5c18c','#281e28',8);
  popRune(c,235,480,34);popCurl(c,400,378,.4);popCurl(c,104,403,.29);
  c.restore();
}
function animeMakeCast(){
  const kami=animeCelGroup(c=>popKamiArt(c,512,720),[3.6,5.1]);
  const wisp=animeCelGroup(c=>popSwyrlzArt(c,512,720),[2.25,3.5]);
  const dragon=animeCelGroup(c=>animeDragonCel(c,512,720),[2,2.5]);
  // No unexplained 'third mascot': the dragon is hidden in cinematic;
  // its original 3D studio actor remains editable when exploring.
  dragon.visible=false;
  return {kami,wisp,dragon};
}
function animeMakePaperBook(){
  const group=new THREE.Group(),paper=new THREE.MeshStandardMaterial({color:'#d6ab72',roughness:.9,side:THREE.DoubleSide}),
    leather=new THREE.MeshStandardMaterial({color:'#352630',roughness:.8,side:THREE.DoubleSide}),
    edge=new THREE.MeshStandardMaterial({color:'#976342',roughness:.7,side:THREE.DoubleSide});
  const body=new THREE.Mesh(new THREE.BoxGeometry(8.9,.24,2.7),leather);group.add(body);
  for(let side of [-1,1]){
    const half=new THREE.Group();group.add(half);half.position.x=side*.04;
    const page=new THREE.Mesh(new THREE.BoxGeometry(4.1,.13,2.5),paper);page.position.x=side*2.08;page.rotation.z=side*.035;half.add(page);
    const trim=new THREE.Mesh(new THREE.BoxGeometry(4.1,.04,.13),edge);trim.position.set(side*2.08,.11,1.2);half.add(trim);
    for(let j=0;j<3;j++){
      const line=new THREE.Mesh(new THREE.BoxGeometry(3.7,.01,.017),edge);
      line.position.set(side*2.08,.14,-.85+j*.32);half.add(line);
    }
  }
  group.position.set(0,1.85,2.9);group.userData.animePopupBook=true;
  return group;
}
function animeCreateCelLayers(){
  const groups={};for(const [key] of ANIME_2D_LAYER_SPECS){
    const g=new THREE.Group();g.userData.animeLayer=key;scene.add(g);groups[key]=g;
  }
  function plate(id,draw,z,size,height){
    const hinge=new THREE.Group();const sprite=animeCelSprite(draw,768,576,size);
    sprite.position.y=height;hinge.add(sprite);groups[id].add(hinge);
    hinge.userData.popupHinge=true;hinge.userData.baseZ=z;
    return hinge;
  }
  // Layer planes are deliberately independent pivoting paper scenery cards.
  plate('background',popBackArt,-21,[33,21],7.3);
  plate('atmosphere',(c,w,h)=>{c.clearRect(0,0,w,h);
    for(let j=0;j<11;j++)popCurl(c,90+j*75,330+j%3*55,.38);
  },-16,[30,18],6.3);
  plate('midground',popCathedralArt,-9,[21,14],5.4);
  plate('midground',popWorkshopArt,-7.4,[19,12],4.8);
  plate('effects',(c,w,h)=>{c.clearRect(0,0,w,h);
    for(let j=0;j<16;j++){popRune(c,30+j*46,110+(j*73)%350,8+(j%4)*7)}
    for(let j=0;j<6;j++)popCurl(c,95+j*114,250+(j%2)*93,.39);
  },1,[15,11],4.7);
  plate('foreground',popDeskArt,3.4,[11.5,8],2.8);
  const book=animeMakePaperBook();
  groups.foreground.add(book);
  return groups;
}
function animeUpdateCelLayers(c,x,t,act){
  const local=t-ANIME_ACT_SECONDS[act],cfg=animePopConfig().layers,delta=c.cameraDelta||0;
  const elevation=(id)=>animePopRise(id,local);
  const spec=[
    ['background',5.8],['atmosphere',5.1],['midground',4.5],['effects',4.2],['foreground',2.0]
  ];
  for(const [id,baseY] of spec){
    const group=c.layers[id],setting=cfg[id],rise=elevation(id);
    group.position.set(x+setting.offsetX+delta*setting.parallax,baseY,0);
    for(const [index,hinge] of group.children.entries()){
      if(!hinge.userData.popupHinge)continue;
      const stagger=Math.max(0,Math.min(1,(local-setting.delay-index*.24)/setting.duration));
      const progress=animePopEase(stagger);
      hinge.position.set(0,-1.3+progress*1.3,setting.depth+(index%2)*1.6);
      hinge.rotation.x=(1-progress)*(-Math.PI/2*.87);
      hinge.scale.y=.3+.7*progress;
    }
    group.visible=c.layerSettings[id]!==false;
  }
  // Physical book opens at the beginning of each shot, separate from plane art.
  const book=c.layers.foreground.children.find(z=>z.userData.animePopupBook);
  if(book){
    const t0=animePopEase(local/.85);
    book.position.set(delta*.73,1.9-1.3*(1-t0),3.2);
    book.scale.set(1,.1+.9*t0,1);
    book.visible=c.layerSettings.foreground!==false;
  }
  const kamiRise=elevation('kami'),swyrlzRise=elevation('swyrlz');
  c.cast.kami.position.set(x+cfg.kami.offsetX+delta*cfg.kami.parallax,
    2.0+kamiRise*2.08+.045*Math.sin(t*.9),cfg.kami.depth);
  c.cast.kami.rotation.z=(1-kamiRise)*-.31+.016*Math.sin(t*.78);
  c.cast.kami.scale.setScalar(.3+.7*kamiRise);
  c.cast.wisp.position.set(x+cfg.swyrlz.offsetX+delta*cfg.swyrlz.parallax,
    2.9+swyrlzRise*1.5+.14*Math.sin(t*1.3),cfg.swyrlz.depth);
  c.cast.wisp.rotation.z=(1-swyrlzRise)*.43+.035*Math.sin(t*.7);
  c.cast.wisp.scale.setScalar(.4+.6*swyrlzRise);
  c.cast.kami.visible=c.layerSettings.characters!==false&&c.layerSettings.kami!==false&&act!==7;
  c.cast.wisp.visible=c.layerSettings.characters!==false&&c.layerSettings.swyrlz!==false&&act!==7;
  c.cast.dragon.visible=false;
  c.layers.kami.visible=c.layerSettings.kami!==false;
  c.layers.swyrlz.visible=c.layerSettings.swyrlz!==false;
  c.layers.guardian.visible=c.layerSettings.guardian!==false;
  c.layers.characters.visible=c.layerSettings.characters!==false;
}
function animeDirectorInstall(){
  if(document.getElementById('animeDirectorBtn'))return;
  const button=document.createElement('button');button.id='animeDirectorBtn';
  button.type='button';button.className='anime-director-button';button.textContent='✦ Pop-Up Director';
  const panel=document.createElement('section');panel.className='anime-director';panel.id='animeDirectorPanel';panel.hidden=true;
  panel.setAttribute('aria-label','Edit Anime Studio pop-up scenery and character layers');
  panel.innerHTML='<header><strong>✦ Pop-Up Director</strong><button id="animeDirectorClose" type="button">✕</button></header>'+
    '<p>Edit independent fantasy scenery and wizard layers. Settings are stored in this project and included in Save Project.</p>'+
    '<select id="animeDirectorLayer" aria-label="Select a scenery or character layer"></select>'+
    '<div id="animeDirectorFields"></div><footer><button type="button" id="animeDirectorReset">Reset layer</button><button type="button" id="animeDirectorDone">Done</button></footer>';
  document.body.append(button,panel);
  for(const id of ANIME_POP_KEYS){const opt=document.createElement('option');opt.value=id;
    opt.textContent=(id==='swyrlz'?'§wyrlz':id==='kami'?'Kami':id)+' · '+(id==='kami'||id==='swyrlz'?'character cel':'pop-up scenery');panel.querySelector('#animeDirectorLayer').append(opt)}
  const fieldNames={depth:'Depth Z',offsetX:'Side position',parallax:'Parallax',delay:'Unfold delay',duration:'Unfold time'};
  for(const [key,label] of Object.entries(fieldNames)){
    const row=document.createElement('label'),title=document.createElement('span'),input=document.createElement('input'),out=document.createElement('span');
    title.textContent=label;input.type='range';input.dataset.popField=key;const [min,max]=ANIME_POP_LIMITS[key];
    input.min=String(min);input.max=String(max);input.step=key==='depth'||key==='offsetX'?'.1':'.05';
    out.className='readout';out.dataset.popValue=key;
    input.addEventListener('input',()=>{
      const id=panel.querySelector('#animeDirectorLayer').value,setting=animePopConfig().layers[id];
      setting[key]=Number(input.value);out.textContent=Number(input.value).toFixed(2);
      if(currentProject?.canonicalId==='ghosts-different-forms-ep01')markDirty();
      if(animeCine)animeUpdateCinematic(0);
    });
    row.append(title,input,out);panel.querySelector('#animeDirectorFields').append(row);
  }
  const sync=()=>{
    const id=panel.querySelector('#animeDirectorLayer').value,conf=animePopConfig().layers[id];
    for(const el of panel.querySelectorAll('input[data-pop-field]')){
      el.value=String(conf[el.dataset.popField]);
      panel.querySelector('[data-pop-value="'+el.dataset.popField+'"]').textContent=Number(el.value).toFixed(2);
    }
  };
  panel.querySelector('#animeDirectorLayer').addEventListener('change',sync);
  button.onclick=()=>{panel.hidden=!panel.hidden;if(!panel.hidden)sync()};
  panel.querySelector('#animeDirectorClose').onclick=()=>panel.hidden=true;
  panel.querySelector('#animeDirectorDone').onclick=()=>panel.hidden=true;
  panel.querySelector('#animeDirectorReset').onclick=()=>{
    const id=panel.querySelector('#animeDirectorLayer').value;
    animePopConfig().layers[id]={...ANIME_POP_DEFAULT[id]};markDirty();sync();
    if(animeCine)animeUpdateCinematic(0);
  };
  button.hidden=currentProject?.canonicalId!=='ghosts-different-forms-ep01';
}
"""
def apply(html):
    s=html
    assert '<script type="module">' in s
    s=s.replace('<script type="module">',CSS+'<script type="module">',1)
    # Character visibility controls remain independent of the 6 original
    # historical compositor layers. Extend rather than removing aliases.
    s=once(s,"  ['characters','04 · Character cels'],",
         "  ['characters','04 · All character cels'],\n  ['kami','05 · Kami wizard'],\n  ['swyrlz','06 · §wyrlz wizard'],\n  ['guardian','07 · Guardian'],")
    start=s.index('function animeMakeCast(){')
    end=s.index('function animeBuildHud(){',start)
    # v8.7 declares other helpers between functions. Keep them by replacing
    # only three complete named function bodies, not their neighbors.
    s=once(s,'function animeMakeCast(){\n  const kami=animeCelGroup(c=>animeHumanCel(c,512,720),[2.5,3.6]);\n  const wisp=animeCelGroup(c=>animeSpiritCel(c,512,720),[2.55,3.65]);\n  const dragon=animeCelGroup(c=>animeDragonCel(c,512,720),[3.5,4.6]);\n  return {kami,wisp,dragon};\n}',
      '/* v8.8 pop-up animated wizard cels */')
    oldcreate=s[s.index('function animeCreateCelLayers(){'):s.index('function animeDisposeGroup(',s.index('function animeCreateCelLayers(){'))]
    s=once(s,oldcreate,'/* v8.8 replaces old layered scenery */\n')
    oldupdate=s[s.index('function animeUpdateCelLayers('):s.index('function animeBuildHud(',s.index('function animeUpdateCelLayers('))]
    s=once(s,oldupdate,'/* v8.8 replaces plane staging */\n')
    # New drawing and scene functions are placed after v8.7 canvas helpers.
    s=once(s,'function animeBuildHud(){',JS+'\nfunction animeBuildHud(){')
    s=once(s,'document.body.dataset.projectKind=currentProject.kind;',
      "document.body.dataset.projectKind=currentProject.kind;\n  if(meta.canonicalId==='ghosts-different-forms-ep01')currentProject.animePopUp=animePopSanitize(meta.animePopUp);")
    s=once(s,"  if(button)button.hidden=currentProject?.canonicalId!=='ghosts-different-forms-ep01';",
      "  if(button)button.hidden=currentProject?.canonicalId!=='ghosts-different-forms-ep01';\n  const director=document.getElementById('animeDirectorBtn');\n  if(director)director.hidden=currentProject?.canonicalId!=='ghosts-different-forms-ep01';\n  if(currentProject?.canonicalId!=='ghosts-different-forms-ep01'){const panel=document.getElementById('animeDirectorPanel');if(panel)panel.hidden=true;}")
    s=once(s,"else loadCanonicalGlitchDen();installAnimeStarterUI();",
      "else loadCanonicalGlitchDen();installAnimeStarterUI();animeDirectorInstall();")
    s=once(s,"  setLayer:(name,visible)=>animeLayerVisible(name,visible)",
      "  setLayer:(name,visible)=>animeLayerVisible(name,visible),\n  director:()=>animePopConfig(),\n  setPopUp:(layer,field,value)=>{if(!ANIME_POP_KEYS.includes(layer)||!Object.hasOwn(ANIME_POP_LIMITS,field))return false;\n    const n=Number(value),bounds=ANIME_POP_LIMITS[field];if(!Number.isFinite(n))return false;\n    animePopConfig().layers[layer][field]=Math.max(bounds[0],Math.min(bounds[1],n));markDirty();if(animeCine)animeUpdateCinematic(0);return true;},\n  popUpStatus:()=>{const c=animeCine;if(!c)return null;\n    const groups=Object.values(c.layers);\n    return {bookCount:groups.reduce((n,g)=>n+g.children.filter(z=>z.userData.animePopupBook).length,0),\n      hinges:groups.reduce((n,g)=>n+g.children.filter(z=>z.userData.popupHinge).length,0),\n      characterCels:{kami:c.cast.kami.children.length,swyrlz:c.cast.wisp.children.length},\n      sceneZ:{background:animePopConfig().layers.background.depth,midground:animePopConfig().layers.midground.depth,foreground:animePopConfig().layers.foreground.depth}};}")
    s=once(s,'V8_7_ANIME_CEL_PARALLAX','V8_8_POPUP_STORYBOOK_DIRECTOR')
    s=s.replace('Maker v8.7','Maker v8.8').replace('MAKER v8.7','MAKER v8.8')
    s=s.replace("version:'v8.7'","version:'v8.8'").replace('version:8.7','version:8.8')
    s=s.replace('§E v8.7 Tools','§E v8.8 Tools')
    s=s.replace('v8.7 · ANIME CEL LAYERS','v8.8 · POP-UP STORYBOOK DIRECTOR')
    s=s.replace('§wyrl§ Engine v8.7 · layered 2.5D anime cinematic','§wyrl§ Engine v8.8 · animated 3D pop-up storybook cinema')
    return s
