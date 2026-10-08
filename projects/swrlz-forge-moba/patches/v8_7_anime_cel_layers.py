"""2.5D anime cel compositor, depth/parallax layer controls and screen-safe dialogue.

Editor source scene is unchanged. Runtime-only 2D animated sprites and layered
scenery are rendered through the existing perspective Three.js camera.
"""
def once(s, old, new):
    if s.count(old)!=1:
        raise RuntimeError("v8.7 cel-layer anchor absent/ambiguous: "+old[:100])
    return s.replace(old,new,1)

CSS=r"""
<style id="animeCelLayerStyles">
.app.anime-cinematic .anime-cine-hud .anime-cine-title{top:11%;max-width:min(400px,88vw)}
.app.anime-cinematic .anime-cine-bottom{bottom:22px}
.app.anime-cinematic .anime-cine-subtitle{
  width:100%;box-sizing:border-box;min-height:48px;max-height:22vh;overflow-wrap:anywhere;
  white-space:normal;font-size:clamp(13px,2.4vw,20px);line-height:1.35;padding:10px 14px;
  border:1px solid #7da4d180;border-radius:12px;background:#060c1be9;
}
.anime-cine-controls .anime-layers-btn{background:#243351}
.anime-layer-popover{
  position:absolute;right:8px;bottom:57px;pointer-events:auto;background:#0c1931f5;
  border:1px solid #6685b4;border-radius:12px;padding:12px;
  width:min(295px,85vw);box-shadow:0 8px 30px #0009;color:#ecf3ff
}
.anime-layer-popover[hidden]{display:none!important}
.anime-layer-popover strong{display:block;margin-bottom:8px;font-size:13px}
.anime-layer-popover label{display:flex;align-items:center;gap:10px;padding:7px 4px;
  border-bottom:1px solid #324054;font-size:12px;cursor:pointer}
.anime-layer-popover input{accent-color:#b396f6;min-width:17px;min-height:17px}
.anime-layer-popover small{display:block;color:#a9bdd5;font-size:10px;line-height:1.45;margin-top:9px}
@media(max-width:650px){
  .app.anime-cinematic .anime-cine-bottom{bottom:15px;width:min(740px,96vw)}
  .app.anime-cinematic .anime-cine-subtitle{font-size:13px;min-height:45px;padding:9px}
  .app.anime-cinematic .anime-cine-controls{gap:4px}
  .app.anime-cinematic .anime-cine-controls button{padding:6px}
  .anime-layer-popover{bottom:53px}
}
</style>
"""

JS=r"""
// 2.5D production stack: separately composited illustrated cels at real Z depths.
// The 3D camera supplies parallax; canvas textures supply hand-drawn-style lines.
// Runtime visibility changes must be restored on Stop or Explore Set.
const ANIME_2D_LAYER_SPECS=Object.freeze([
  ['background','01 · Background / sky'],
  ['atmosphere','02 · Atmosphere / distant lights'],
  ['midground','03 · Midground / architecture'],
  ['characters','04 · Character cels'],
  ['effects','05 · FX / magical accents'],
  ['foreground','06 · Foreground / framing']
]);
function animeDefaultLayers(){
  return Object.fromEntries(ANIME_2D_LAYER_SPECS.map(([id])=>[id,true]));
}
function animeCleanLayers(value){
  const input=value&&typeof value==='object'&&!Array.isArray(value)?value:{};
  return Object.fromEntries(ANIME_2D_LAYER_SPECS.map(([id])=>[id,input[id]!==false]));
}
function animeDrawSurface(draw,width=768,height=512){
  const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
  const ctx=canvas.getContext('2d');
  if(!ctx)throw new Error('Anime cel compositor needs 2D canvas support.');
  draw(ctx,width,height);
  const texture=new THREE.CanvasTexture(canvas);
  texture.colorSpace=THREE.SRGBColorSpace;
  texture.anisotropy=2;
  texture.needsUpdate=true;
  return texture;
}
function animeCelSprite(draw,width,height,scale,opacity=1){
  const tex=animeDrawSurface(draw,width,height);
  const mat=new THREE.SpriteMaterial({map:tex,transparent:true,opacity,depthTest:true,depthWrite:false});
  const sprite=new THREE.Sprite(mat);
  sprite.scale.set(scale[0],scale[1],1);
  sprite.userData.animeCel=true;
  return sprite;
}
function animeCloudscape(c,w,h){
  const g=c.createLinearGradient(0,0,0,h);
  g.addColorStop(0,'#080f2a');g.addColorStop(.57,'#243760');g.addColorStop(1,'#765d88');
  c.fillStyle=g;c.fillRect(0,0,w,h);
  c.globalAlpha=.2;for(let i=0;i<5;i++){c.fillStyle=i%2?'#a5a9e5':'#c4daed';c.beginPath();c.ellipse(100+i*160,100+(i%3)*70,160,27,-.08,0,Math.PI*2);c.fill()}
  c.globalAlpha=1;
  const moon=c.createRadialGradient(574,117,15,574,117,145);moon.addColorStop(0,'#e6f6ffbd');moon.addColorStop(.27,'#9eb4ea55');moon.addColorStop(1,'#9eb4ea00');
  c.fillStyle=moon;c.fillRect(390,0,365,330);
  c.fillStyle='#e5eeff';c.beginPath();c.arc(574,117,30,0,Math.PI*2);c.fill();
  for(let i=0;i<67;i++){const x=(i*137+41)%w,y=(i*97+29)%(h*.77);c.fillStyle=i%5===0?'#e6b4ff':'#d4eeff';c.fillRect(x,y,i%6===0?3:1.5,i%6===0?3:1.5)}
}
function animeMidscape(c,w,h){
  const g=c.createLinearGradient(0,0,0,h);g.addColorStop(0,'#20274700');g.addColorStop(1,'#283b66d8');c.fillStyle=g;c.fillRect(0,0,w,h);
  c.lineJoin='round';for(let i=0;i<17;i++){
    const x=i*55-20,top=140+((i*71)%135),height=h-top;
    c.fillStyle=i%3?'#1b2545':'#242c4e';c.strokeStyle='#50628b';c.lineWidth=3;
    c.beginPath();c.moveTo(x,top+21);c.lineTo(x+15,top);c.lineTo(x+49,top+20);c.lineTo(x+49,h);c.lineTo(x,h);c.closePath();c.fill();c.stroke();
    c.fillStyle='#f7cbaa9a';for(let y=top+37;y<h-20;y+=37){for(let k=0;k<2;k++)if((i+y+k)%3!==0)c.fillRect(x+10+k*22,y,8,15)}
  }
  c.fillStyle='#6e83b45e';c.fillRect(0,h-40,w,40);
}
function animeForegroundArt(c,w,h){
  c.clearRect(0,0,w,h);c.lineWidth=7;c.strokeStyle='#a7b7e25f';
  c.fillStyle='#171c40e5';
  c.beginPath();c.moveTo(0,0);c.lineTo(100,0);c.bezierCurveTo(62,h*.38,95,h*.72,0,h);c.closePath();c.fill();c.stroke();
  c.beginPath();c.moveTo(w,0);c.lineTo(w-108,0);c.bezierCurveTo(w-80,h*.35,w-105,h*.78,w,h);c.closePath();c.fill();c.stroke();
  c.fillStyle='#e9a4ff';for(let i=0;i<13;i++){
    const x=(i*139+80)%w,y=(i*109+90)%h;
    c.globalAlpha=.2+((i%4)*.13);c.beginPath();c.arc(x,y,3+(i%3)*2,0,Math.PI*2);c.fill();
  }c.globalAlpha=1;
}
function animeLine(c,color='#121b39',width=8){c.lineWidth=width;c.lineJoin='round';c.lineCap='round';c.strokeStyle=color}
function animeHumanCel(c,w,h,young=false){
  c.clearRect(0,0,w,h);
  // Drawn cels: thick ink outlines and flat shadow/value shapes.
  animeLine(c);c.fillStyle=young?'#273a64':'#1b2751';
  c.beginPath();c.moveTo(95,700);c.quadraticCurveTo(85,445,180,420);c.lineTo(330,420);c.quadraticCurveTo(426,470,418,700);c.closePath();c.fill();c.stroke();
  c.fillStyle='#a78bf3';c.beginPath();c.moveTo(165,435);c.lineTo(260,535);c.lineTo(341,437);c.closePath();c.fill();
  c.fillStyle='#eaba99';c.beginPath();c.moveTo(207,397);c.lineTo(305,397);c.lineTo(297,472);c.lineTo(222,470);c.closePath();c.fill();c.stroke();
  c.fillStyle='#f2c79e';c.beginPath();c.moveTo(136,224);c.bezierCurveTo(130,85,372,80,378,232);c.lineTo(359,333);
  c.quadraticCurveTo(334,408,258,432);c.quadraticCurveTo(183,412,156,345);c.closePath();c.fill();c.stroke();
  c.fillStyle='#e4a87e';c.beginPath();c.moveTo(300,337);c.quadraticCurveTo(348,325,362,288);c.quadraticCurveTo(362,384,260,417);c.closePath();c.fill();
  c.fillStyle='#171d37';c.beginPath();c.moveTo(139,232);c.lineTo(126,150);c.lineTo(169,179);c.lineTo(173,96);
  c.lineTo(225,155);c.lineTo(270,75);c.lineTo(299,146);c.lineTo(359,104);c.lineTo(355,171);
  c.lineTo(390,196);c.lineTo(361,255);c.lineTo(339,205);c.lineTo(266,175);c.lineTo(193,211);c.closePath();c.fill();c.stroke();
  c.strokeStyle='#28314b';c.lineWidth=8;c.beginPath();c.moveTo(160,285);c.quadraticCurveTo(206,271,235,285);
  c.moveTo(289,285);c.quadraticCurveTo(331,265,358,278);c.stroke();
  c.fillStyle='#f5f6ff';c.beginPath();c.ellipse(205,300,28,16,-.06,0,Math.PI*2);
  c.ellipse(327,295,24,16,-.08,0,Math.PI*2);c.fill();
  c.fillStyle='#556bc2';c.beginPath();c.arc(209,300,12,0,Math.PI*2);c.arc(322,297,12,0,Math.PI*2);c.fill();
  c.fillStyle='#10162c';c.beginPath();c.arc(209,300,6,0,Math.PI*2);c.arc(322,297,6,0,Math.PI*2);c.fill();
  c.strokeStyle='#b36569';c.lineWidth=5;c.beginPath();c.moveTo(246,371);c.quadraticCurveTo(260,378,283,369);c.stroke();
  c.fillStyle='#f2e7ff';c.font='bold 24px sans-serif';c.fillText(young?'YOUNGER KAMI':'KAMI',165,590);
}
function animeSpiritCel(c,w,h){
  c.clearRect(0,0,w,h);c.save();
  c.shadowColor='#6beaff';c.shadowBlur=35;c.fillStyle='#61ddeb66';
  c.beginPath();c.ellipse(258,345,160,250,0,0,Math.PI*2);c.fill();c.restore();
  animeLine(c,'#91e5ff',9);c.fillStyle='#35366de8';
  c.beginPath();c.moveTo(125,665);c.quadraticCurveTo(106,450,153,402);c.lineTo(366,401);
  c.quadraticCurveTo(412,500,389,668);c.lineTo(313,627);c.lineTo(264,700);
  c.lineTo(205,632);c.closePath();c.fill();c.stroke();
  c.fillStyle='#cdf5fc';c.beginPath();c.ellipse(261,275,114,157,0,0,Math.PI*2);c.fill();c.stroke();
  c.fillStyle='#5d74af';c.beginPath();c.moveTo(147,263);c.lineTo(132,176);c.lineTo(199,165);
  c.lineTo(247,105);c.lineTo(295,167);c.lineTo(382,164);c.lineTo(370,270);
  c.quadraticCurveTo(330,212,262,205);c.quadraticCurveTo(185,225,147,263);c.fill();
  c.strokeStyle='#2d4168';c.lineWidth=7;c.beginPath();c.moveTo(174,302);c.lineTo(232,305);
  c.moveTo(290,305);c.lineTo(349,300);c.stroke();
  c.fillStyle='#4c629a';c.beginPath();c.ellipse(213,318,14,22,0,0,Math.PI*2);
  c.ellipse(318,315,14,22,0,0,Math.PI*2);c.fill();
  c.strokeStyle='#5469a0';c.lineWidth=5;c.beginPath();c.arc(265,347,24,.22,Math.PI-.2);c.stroke();
  c.fillStyle='#f7ebff';c.font='bold 22px sans-serif';c.fillText('§WYRLZ',214,571);
  c.strokeStyle='#d4bcff';c.lineWidth=10;c.beginPath();c.ellipse(255,208,161,45,-.07,0,Math.PI*2);c.stroke();
}
function animeDragonCel(c,w,h){
  c.clearRect(0,0,w,h);animeLine(c,'#1d2553',9);
  c.fillStyle='#9b8ce7';c.beginPath();c.moveTo(105,575);c.lineTo(58,211);c.lineTo(197,339);
  c.lineTo(260,115);c.lineTo(337,340);c.lineTo(478,186);c.lineTo(406,567);c.closePath();c.fill();c.stroke();
  c.fillStyle='#c1abf9';c.beginPath();c.ellipse(264,389,135,178,0,0,Math.PI*2);c.fill();c.stroke();
  c.fillStyle='#e4eafa';c.beginPath();c.ellipse(257,391,96,128,0,0,Math.PI*2);c.fill();c.stroke();
  c.fillStyle='#35456b';c.beginPath();c.ellipse(207,348,25,20,0,0,Math.PI*2);c.ellipse(317,350,25,20,0,0,Math.PI*2);c.fill();
  c.fillStyle='#f8ffff';c.beginPath();c.arc(211,344,7,0,Math.PI*2);c.arc(323,348,7,0,Math.PI*2);c.fill();
  c.strokeStyle='#37456e';c.lineWidth=6;c.beginPath();c.moveTo(234,425);c.quadraticCurveTo(266,447,299,425);c.stroke();
  c.fillStyle='#e1ddff';c.font='bold 25px sans-serif';c.fillText('GUARDIAN',188,615);
}
function animeCelGroup(draw,scale){
  const group=new THREE.Group();
  group.add(animeCelSprite(draw,512,720,scale));scene.add(group);return group;
}
function animeMakeCast(){
  const kami=animeCelGroup(c=>animeHumanCel(c,512,720),[2.5,3.6]);
  const wisp=animeCelGroup(c=>animeSpiritCel(c,512,720),[2.55,3.65]);
  const dragon=animeCelGroup(c=>animeDragonCel(c,512,720),[3.5,4.6]);
  return {kami,wisp,dragon};
}
function animeCreateCelLayers(){
  const groups={};
  for(const [key] of ANIME_2D_LAYER_SPECS){const g=new THREE.Group();g.userData.animeLayer=key;scene.add(g);groups[key]=g}
  const make=(id,draw,z,size)=>{
    const g=groups[id],s=animeCelSprite(draw,768,512,size);
    s.position.z=z;g.add(s);return s;
  };
  make('background',animeCloudscape,-21,[31,19]);
  make('atmosphere',(c,w,h)=>{
    c.clearRect(0,0,w,h);c.strokeStyle='#aac4eb44';c.lineWidth=4;
    for(let i=0;i<9;i++){c.beginPath();c.arc((i*157)%w,(i*67)%h,35+(i%4)*17,0,Math.PI*2);c.stroke()}
  },-16,[27,15]);
  make('midground',animeMidscape,-9,[23,13]);
  make('effects',(c,w,h)=>{
    c.clearRect(0,0,w,h);for(let i=0;i<70;i++){
      c.fillStyle=i%3?'#e3c9ffbb':'#8fdbffbb';c.beginPath();c.arc((i*157)%w,(i*113)%h,2+(i%4),0,Math.PI*2);c.fill();
    }
  },1,[18,10]);
  make('foreground',animeForegroundArt,4.7,[17,10]);
  return groups;
}
function animeDisposeGroup(group){
  if(!group)return;
  group.traverse(obj=>{
    if(obj.isSprite){obj.material?.map?.dispose();obj.material?.dispose()}
    else if(obj.isMesh){obj.geometry?.dispose();if(Array.isArray(obj.material)){for(const m of obj.material){m.map?.dispose();m.dispose()}}
      else{obj.material?.map?.dispose();obj.material?.dispose()}}
  });
  scene.remove(group);
}
function animeLayerVisible(id,flag){
  if(!animeCine||!animeCine.layers)return false;
  const group=animeCine.layers[id];if(!group)return false;
  animeCine.layerSettings[id]=flag!==false;group.visible=flag!==false;
  if(id==='characters'){animeCine.cast.kami.visible=flag!==false;animeCine.cast.wisp.visible=flag!==false;animeCine.cast.dragon.visible=flag!==false}
  const cb=animeHud?.querySelector('input[data-anime-layer="'+id+'"]');if(cb)cb.checked=flag!==false;
  return true;
}
function animeInstallLayerUI(){
  const controls=animeHud?.querySelector('.anime-cine-controls');
  if(!controls||animeHud.querySelector('#animeCineLayers'))return;
  const btn=document.createElement('button');btn.type='button';btn.id='animeCineLayers';
  btn.className='anime-layers-btn';btn.textContent='▧ Layers';controls.append(btn);
  const panel=document.createElement('div');panel.id='animeCineLayerPanel';panel.className='anime-layer-popover';panel.hidden=true;
  const title=document.createElement('strong');title.textContent='2.5D anime layers';panel.append(title);
  for(const [id,label] of ANIME_2D_LAYER_SPECS){
    const row=document.createElement('label'),input=document.createElement('input');
    input.type='checkbox';input.dataset.animeLayer=id;input.checked=true;
    input.onchange=()=>animeLayerVisible(id,input.checked);
    row.append(input,document.createTextNode(label));panel.append(row);
  }
  const small=document.createElement('small');
  small.textContent='Separate depth planes and character cels. Toggle a layer to see the 2D/3D parallax stack; original editor actors are preserved.';
  panel.append(small);animeHud.querySelector('.anime-cine-bottom').append(panel);
  btn.onclick=()=>{panel.hidden=!panel.hidden};
}
function animeUpdateCelLayers(c,x,t,act){
  const stage=ANIME_ACT_SECONDS[act],local=t-stage,delta=c.cameraDelta||0;
  c.layers.background.position.set(x+delta*.06,5.8,0);
  c.layers.atmosphere.position.set(x+delta*.13,5.5+.07*Math.sin(t*.14),0);
  c.layers.midground.position.set(x+delta*.31,4.2,0);
  c.layers.effects.position.set(x+.2*Math.sin(t*.2),5.1+.12*Math.sin(t*.65),0);
  c.layers.foreground.position.set(x+delta*.65,4.8,0);
  c.cast.kami.position.set(x-1.05,4.35+.034*Math.sin(t*1.3),-.45);
  c.cast.kami.rotation.set(0,0,.017*Math.sin(t*.9));
  c.cast.wisp.position.set(x+1.05+.12*Math.sin(t*.5),4.55+.11*Math.sin(t*1.8),-.3);
  c.cast.wisp.rotation.set(0,0,.04*Math.sin(t*.6));
  c.cast.dragon.position.set(x,4.3+.15*Math.sin(t*.6),-2.2);
  c.cast.dragon.visible=c.layerSettings.characters&&(act===4||act===6);
  c.cast.kami.visible=c.layerSettings.characters&&act!==7;
  c.cast.wisp.visible=c.layerSettings.characters&&act!==7;
  for(const [id,group] of Object.entries(c.layers))group.visible=c.layerSettings[id]!==false;
}
"""
def apply(html):
    s=html
    assert '<script type="module">' in s
    s=s.replace('<script type="module">',CSS+'<script type="module">',1)
    start=s.index('function animeMakeCast(){')
    end=s.index('function animeBuildHud(){',start)
    s=s[:start]+JS+'\n'+s[end:]
    s=once(s,'  const cast=animeMakeCast(),hud=animeBuildHud();',
      """  const hiddenActors=actors.map(actor=>[actor,actor.visible]);
  for(const [actor] of hiddenActors)actor.visible=false;
  const cast=animeMakeCast(),layers=animeCreateCelLayers(),hud=animeBuildHud();
  animeInstallLayerUI();""")
    s=once(s,'  animeCine={active:true,elapsed:0,ended:false,stage:-1,cast,particles,particlesGeometry,particlesMaterial,lamp,guardian,',
      '  animeCine={active:true,elapsed:0,ended:false,stage:-1,cast,layers,layerSettings:animeDefaultLayers(),hiddenActors,particles,particlesGeometry,particlesMaterial,lamp,guardian,')
    old="""  c.cast.kami.traverse(obj=>{if(obj.isMesh){obj.geometry?.dispose();if(obj.material?.dispose)obj.material.dispose()}});
  c.cast.wisp.traverse(obj=>{if(obj.isMesh){obj.geometry?.dispose();if(obj.material?.dispose)obj.material.dispose()}});
  scene.remove(c.cast.kami,c.cast.wisp,c.particles,c.lamp);"""
    new="""  animeDisposeGroup(c.cast.kami);animeDisposeGroup(c.cast.wisp);animeDisposeGroup(c.cast.dragon);
  for(const group of Object.values(c.layers))animeDisposeGroup(group);
  for(const [actor,wasVisible] of c.hiddenActors)actor.visible=wasVisible;
  scene.remove(c.particles,c.lamp);"""
    s=once(s,old,new)
    start=s.index('  const drift=Math.sin(u*Math.PI),travelX=',s.index('function animeUpdateCinematic(dt){'))
    end=s.index("  const a=c.particlesGeometry.getAttribute('position'),count=a.count;",start)
    s=s[:start]+"""  // Perspective camera remains genuinely 3D; 2D cels occupy independently
  // animated depth planes. No large in-world text sign can obscure a shot.
  const travelX=(-.55+1.1*u);
  c.cameraDelta=travelX;
  const zoom=12.8-.5*Math.sin(u*Math.PI);
  perspectiveCamera.position.set(x+travelX,4.85+.16*Math.sin(u*Math.PI*2),zoom);
  perspectiveCamera.lookAt(x,4.45,-1.7);
  animeUpdateCelLayers(c,x,t,act);
"""+s[end:]
    s=once(s,'  c.lamp.position.set(x,6,2.5);','  c.lamp.position.set(x,6,2.5);')
    # Guardian 3D may animate but stays hidden during movie; restore original on exit.
    s=once(s,'  const cues=animeSpeakerCues(act),idx=Math.min(cues.length-1,Math.floor(u*cues.length));',
      '  const cues=animeSpeakerCues(act),idx=Math.min(cues.length-1,Math.floor(u*cues.length));')
    s=once(s,"    projectId:currentProject?.canonicalId||null}),",
      "    projectId:currentProject?.canonicalId||null,\n    layers:animeCine?Object.fromEntries(Object.entries(animeCine.layerSettings)):null,\n    celCount:animeCine?animeCine.cast.kami.children.length+animeCine.cast.wisp.children.length+animeCine.cast.dragon.children.length:0}),")
    s=once(s,'  explore:()=>document.getElementById(\'animeCineExplore\')?.click()',
       "  explore:()=>document.getElementById('animeCineExplore')?.click(),\n  setLayer:(name,visible)=>animeLayerVisible(name,visible)")
    # Move HUD to stable center and supply safe wrapping for every subtitle.
    s=once(s,'V8_6_NATIVE_ANIME_CINEMATIC','V8_7_ANIME_CEL_PARALLAX')
    s=s.replace('Maker v8.6','Maker v8.7').replace('MAKER v8.6','MAKER v8.7')
    s=s.replace("version:'v8.6'","version:'v8.7'").replace('version:8.6','version:8.7')
    s=s.replace("version:'swyrl-engine-agent-v6.6'","version:'swyrl-engine-agent-v6.7'")
    s=s.replace('§E v8.6 Tools','§E v8.7 Tools')
    s=s.replace('v8.6 · NATIVE ANIME CINEMATIC','v8.7 · ANIME CEL LAYERS')
    s=s.replace('§wyrl§ Engine v8.6 · native anime cinematic playback','§wyrl§ Engine v8.7 · layered 2.5D anime cinematic')
    return s
