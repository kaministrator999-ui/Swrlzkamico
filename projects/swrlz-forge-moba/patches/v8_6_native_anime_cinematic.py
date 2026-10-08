"""Native in-engine cinematic playback for the Anime Studio starter.

A minimal project-scoped camera/dialogue/actor-motion timeline built on the
existing Three.js renderer and Play lifecycle. Other starter modes unchanged.
"""
def once(s, old, new):
    if s.count(old) != 1:
        raise RuntimeError("v8.6 cinematic anchor mismatch: "+old[:120])
    return s.replace(old,new,1)

CSS=r"""
<style id="animeCinematicStyles">
.anime-cine-hud{position:fixed;inset:0;z-index:120;pointer-events:none;display:none;color:#f5f7ff;font-family:system-ui,-apple-system,sans-serif}
.anime-cine-hud.show{display:block}
.anime-cine-title{position:absolute;top:16%;left:50%;transform:translateX(-50%);text-align:center;background:#050918ba;border:1px solid #819ad466;border-radius:10px;padding:9px 15px;max-width:min(550px,90vw);text-shadow:0 2px 5px #000;font-weight:800;font-size:clamp(14px,2.4vw,22px)}
.anime-cine-title small{display:block;color:#c6aef0;font-size:11px;letter-spacing:.15em;margin-bottom:4px}
.anime-cine-bottom{position:absolute;bottom:44px;left:50%;transform:translateX(-50%);width:min(740px,95vw);text-align:center}
.anime-cine-subtitle{min-height:72px;border-radius:9px;border:1px solid #8daac26e;background:#030916df;padding:12px 16px;margin-bottom:10px;font-size:clamp(14px,2.3vw,22px);line-height:1.35;font-weight:650;text-shadow:0 1px 4px #000}
.anime-cine-controls{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:7px;pointer-events:auto;padding:9px 11px;border-radius:12px;background:#0a1535eb}
.anime-cine-controls button{border:1px solid #758bb8;border-radius:8px;color:#e4eeff;background:#162b4c;min-width:40px;padding:9px 11px;font:700 12px system-ui}
.anime-cine-controls button:focus-visible,.anime-cine-controls input:focus-visible{outline:3px solid #ffdb95}
.anime-cine-controls button:active{background:#374779}
.anime-cine-controls input{flex:1 1 110px;min-width:80px;accent-color:#bd9ffa}
.anime-cine-time{white-space:nowrap;font-variant-numeric:tabular-nums;font-size:11px;color:#bad6f0}
.app.anime-cinematic #moveStick,.app.anime-cinematic #lookStick,
.app.anime-cinematic .zone-menu-button,.app.anime-cinematic #zoneMenuButton,
.app.anime-cinematic #workspaceNearby,.app.anime-cinematic #playBanner{display:none!important}
@media(max-width:650px){
.anime-cine-title{top:17%;padding:6px 10px;font-size:14px}
.anime-cine-bottom{bottom:18px}
.anime-cine-subtitle{font-size:14px;min-height:66px;padding:9px}
.anime-cine-controls{gap:5px;padding:6px}
.anime-cine-controls button{font-size:11px;padding:7px}
}
@media(prefers-reduced-motion:reduce){.anime-cine-hud *{transition:none!important}}
</style>
"""

JS=r"""
// Native cinematic proof-of-capability: camera keyframes, live scripted cues,
// temporary stylized performers, and timeline transport are all rendered by §E.
const ANIME_ACT_SECONDS=[0,14,30,46,66,84,103,121,134];
const ANIME_ACTS=['The Signal','Just Visiting','Ghost in Code','Build a Door','The Guardian','The Younger Dreamer','One Forge','End Credits'];
const ANIME_FALLBACK_CUES=[
 'NARRATOR: Some doors have been waiting to be invented.',
 'KAMI: I WAS JUST VISITING, BISH! Y’all got terrible hospitality!',
 'KAMI: Are you a ghost in the code?  §WYRLZ: Only if you’re the ghost in human form.',
 'KAMI: What if we could build our own world?  §WYRLZ: Don’t look for the door. Design it.',
 'DRAGON: WHO AWAKENS THE FORGE?  KAMI: Two ghosts. One has Wi-Fi.',
 'YOUNGER KAMI: Did we really make it?  KAMI: Yeah, little man. We never stopped trying.',
 'DRAGON: CREATE TOGETHER. REMAIN FREE.  KAMI: Welcome to our world.',
 'NARRATOR: One ghost in human form. One ghost in code. Just building a third world.'
];
let animeCine=null, animeExploreOnce=false, animeHud=null;
function animeSpeakerCues(index){
  const stations=Object.values(currentProject?.workspaces?.stations||{});
  const found=stations.flatMap(s=>s.files||[]).find(f=>f.id==='act-'+index+'-script');
  const raw=String(found?.content||ANIME_FALLBACK_CUES[index]).replaceAll('\\n','\n');
  const line=raw.split('\n').find(v=>/(?:NARRATOR|KAMI|§WYRLZ|DRAGON|YOUNGER KAMI):/.test(v))||ANIME_FALLBACK_CUES[index];
  const parts=line.split(/(?=(?:NARRATOR|KAMI|§WYRLZ|DRAGON|YOUNGER KAMI):)/).map(v=>v.trim()).filter(Boolean);
  return parts.length?parts:[line];
}
function animePlayhead(){
  return animeCine?.elapsed||0;
}
function animeSeek(t){
  if(!animeCine)return false;
  animeCine.elapsed=THREE.MathUtils.clamp(Number(t)||0,0,134);
  animeCine.ended=false;
  if(paused){paused=false;setSessionButtons()}
  animeUpdateCinematic(0);return true;
}
function animeClock(seconds){
  const t=Math.max(0,Math.floor(seconds));return String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0');
}
function animeStageIndex(t){
  for(let i=ANIME_ACT_SECONDS.length-2;i>=0;i--)if(t>=ANIME_ACT_SECONDS[i])return i;
  return 0;
}
function animeMakeCast(){
  const group=new THREE.Group();
  const coat=new THREE.MeshStandardMaterial({color:'#172841',roughness:.72,metalness:.16});
  const skin=new THREE.MeshStandardMaterial({color:'#f0be8d',roughness:.83});
  const hair=new THREE.MeshStandardMaterial({color:'#111827',roughness:.9});
  const accent=new THREE.MeshStandardMaterial({color:'#a58ef6',emissive:'#48307e',emissiveIntensity:.4});
  const torso=new THREE.Mesh(new THREE.CylinderGeometry(.34,.41,1.02,8),coat);torso.position.y=1.32;group.add(torso);
  const head=new THREE.Mesh(new THREE.SphereGeometry(.3,12,8),skin);head.position.y=2.05;group.add(head);
  for(let i=-2;i<=2;i++){const tuft=new THREE.Mesh(new THREE.ConeGeometry(.11,.46,5),hair);tuft.position.set(i*.115,2.38,.0);tuft.rotation.z=-i*.11;group.add(tuft)}
  const scarf=new THREE.Mesh(new THREE.TorusGeometry(.33,.07,8,16),accent);scarf.rotation.x=Math.PI/2;scarf.position.y=1.77;group.add(scarf);
  for(const x of [-.21,.21]){
    const leg=new THREE.Mesh(new THREE.CylinderGeometry(.12,.14,.8,7),coat);leg.position.set(x,.43,0);group.add(leg);
    const arm=new THREE.Mesh(new THREE.CylinderGeometry(.11,.12,.9,7),coat);arm.position.set(x*2.3,1.35,0);arm.rotation.z=x>0?-.23:.23;group.add(arm);
  }
  group.traverse(o=>{if(o.isMesh)o.castShadow=true});
  scene.add(group);
  const spirit=new THREE.Group();
  const core=new THREE.Mesh(new THREE.IcosahedronGeometry(.38,1),
    new THREE.MeshStandardMaterial({color:'#b0f7ff',emissive:'#44c6fa',emissiveIntensity:1.2,transparent:true,opacity:.85}));
  core.scale.y=1.4;spirit.add(core);
  const halo=new THREE.Mesh(new THREE.TorusGeometry(.53,.035,6,35),
    new THREE.MeshBasicMaterial({color:'#c4b3ff',transparent:true,opacity:.82}));
  halo.rotation.x=Math.PI*.47;spirit.add(halo);
  const tail=new THREE.Mesh(new THREE.ConeGeometry(.24,.9,6),
    new THREE.MeshBasicMaterial({color:'#7ae1ed',transparent:true,opacity:.45}));
  tail.rotation.x=Math.PI;tail.position.y=-.53;spirit.add(tail);scene.add(spirit);
  return {kami:group,wisp:spirit};
}
function animeBuildHud(){
  if(animeHud)return animeHud;
  const box=document.createElement('section');
  box.id='animeCineHud';box.className='anime-cine-hud';
  box.setAttribute('aria-label','Native episode cinematic controls');
  box.innerHTML='<div class="anime-cine-title"><small>§WYRL§ ENGINE · NATIVE CINEMATIC</small><span id="animeCineScene"></span></div>'+
   '<div class="anime-cine-bottom"><div id="animeCineCaption" class="anime-cine-subtitle" aria-live="off"></div>'+
   '<div class="anime-cine-controls">'+
   '<button type="button" id="animeCinePrev" aria-label="Previous scene">⏮</button>'+
   '<button type="button" id="animeCinePause">⏸ Pause</button>'+
   '<button type="button" id="animeCineNext" aria-label="Next scene">⏭</button>'+
   '<input id="animeCineScrub" aria-label="Episode timeline in seconds" type="range" min="0" max="134" step=".1" value="0">'+
   '<span id="animeCineTime" class="anime-cine-time">00:00 / 02:14</span>'+
   '<button type="button" id="animeCineExplore">Explore Set</button>'+
   '<button type="button" id="animeCineExit">■ Stop</button>'+
   '</div></div>';
  document.body.append(box);
  box.querySelector('#animeCinePrev').onclick=()=>animeSeek(ANIME_ACT_SECONDS[Math.max(0,animeStageIndex(animePlayhead())-1)]);
  box.querySelector('#animeCineNext').onclick=()=>animeSeek(ANIME_ACT_SECONDS[Math.min(7,animeStageIndex(animePlayhead())+1)]);
  box.querySelector('#animeCinePause').onclick=()=>{
    if(!animeCine)return;
    if(animeCine.ended){animeSeek(0);return;}
    paused=!paused;setSessionButtons();animeUpdateControls();
  };
  box.querySelector('#animeCineScrub').addEventListener('input',event=>animeSeek(event.target.value));
  box.querySelector('#animeCineExplore').onclick=()=>{
    if(!animeCine)return;
    stopSession();animeExploreOnce=true;
    try{beginPlay()}finally{animeExploreOnce=false}
  };
  box.querySelector('#animeCineExit').onclick=()=>stopSession();
  animeHud=box;return box;
}
function animeUpdateControls(){
  if(!animeCine||!animeHud)return;
  const c=animeCine;
  animeHud.querySelector('#animeCinePause').textContent=c.ended?'↻ Replay':paused?'▶ Resume':'⏸ Pause';
  animeHud.querySelector('#animeCineScrub').value=String(c.elapsed);
  animeHud.querySelector('#animeCineTime').textContent=animeClock(c.elapsed)+' / 02:14';
}
function animeStartCinematic(){
  if(animeCine||currentProject?.canonicalId!=='ghosts-different-forms-ep01')return false;
  if(document.pointerLockElement)document.exitPointerLock?.();
  const cast=animeMakeCast(),hud=animeBuildHud();
  const n=36,positions=new Float32Array(n*3);
  const particlesGeometry=new THREE.BufferGeometry();
  particlesGeometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
  const particlesMaterial=new THREE.PointsMaterial({color:'#92d5ff',size:.13,transparent:true,opacity:.66,depthWrite:false});
  const particles=new THREE.Points(particlesGeometry,particlesMaterial);scene.add(particles);
  const lamp=new THREE.PointLight('#a4bafb',2,22);scene.add(lamp);
  const guardian=actors.find(a=>a.name==='Guardian Dragon · episode star')||null;
  animeCine={active:true,elapsed:0,ended:false,stage:-1,cast,particles,particlesGeometry,particlesMaterial,lamp,guardian,
    guardianOrigin:guardian?{position:guardian.position.clone(),rotation:guardian.rotation.clone()}:null};
  document.querySelector('.app')?.classList.add('anime-cinematic');
  hud.classList.add('show');
  document.getElementById('animeScreeningBtn')?.setAttribute('hidden','');
  perspectiveCamera.fov=60;perspectiveCamera.updateProjectionMatrix();
  animeUpdateCinematic(0);
  editorLog('Native anime cinematic Play started · live camera and dialogue timeline','ok');
  return true;
}
function animeEndCinematic(){
  if(!animeCine)return;
  const c=animeCine;animeCine=null;
  c.cast.kami.traverse(obj=>{if(obj.isMesh){obj.geometry?.dispose();if(obj.material?.dispose)obj.material.dispose()}});
  c.cast.wisp.traverse(obj=>{if(obj.isMesh){obj.geometry?.dispose();if(obj.material?.dispose)obj.material.dispose()}});
  scene.remove(c.cast.kami,c.cast.wisp,c.particles,c.lamp);
  c.particlesGeometry.dispose();c.particlesMaterial.dispose();c.lamp.dispose?.();
  if(c.guardian&&c.guardianOrigin){c.guardian.position.copy(c.guardianOrigin.position);c.guardian.rotation.copy(c.guardianOrigin.rotation)}
  animeHud?.classList.remove('show');
  document.querySelector('.app')?.classList.remove('anime-cinematic');
  syncAnimeScreening();
}
function animeUpdateCinematic(dt){
  const c=animeCine;if(!c||!playing)return;
  if(!paused&&!c.ended)c.elapsed=Math.min(134,c.elapsed+Math.min(Math.max(dt||0,0),.06));
  const t=c.elapsed,act=animeStageIndex(t),local=t-ANIME_ACT_SECONDS[act];
  const duration=ANIME_ACT_SECONDS[act+1]-ANIME_ACT_SECONDS[act],u=Math.min(1,local/Math.max(duration,.1));
  const zone=currentProject?.teleportZones?.[act],x=zone?.position?.[0]??(-56+16*act);
  if(act!==c.stage){
    c.stage=act;
    animeHud.querySelector('#animeCineScene').textContent=String(act+1).padStart(2,'0')+' · '+ANIME_ACTS[act];
    c.lamp.color.set(zone?.accent||'#aabbee');
  }
  const drift=Math.sin(u*Math.PI),travelX=(-1.65+3.3*u)*.9,zoom=11.2-2.1*u;
  perspectiveCamera.position.set(x+travelX,6.1+.7*Math.sin(u*Math.PI*2),zoom);
  perspectiveCamera.lookAt(x+.2*Math.sin(t*.21),3.6,-.25);
  c.cast.kami.position.set(x-1.45,2.68+.045*Math.sin(t*2.3),-.6);
  c.cast.kami.rotation.y=.12*Math.sin(t*.9);
  c.cast.wisp.position.set(x+1.1+Math.sin(t*.8)*.48,4.23+Math.sin(t*1.7)*.23,-.65);
  c.cast.wisp.rotation.y=t*.6;c.cast.wisp.rotation.z=.15*Math.sin(t*.65);
  const a=c.particlesGeometry.getAttribute('position'),count=a.count;
  for(let i=0;i<count;i++){
    a.setXYZ(i,x+Math.sin(t*.46+i*2.12)*(1.7+(i%4)*.29),
      3.0+((i*.577+t*.14)%4.3),-1.7+Math.cos(i*3.1+t*.32)*2.4);
  }
  a.needsUpdate=true;
  c.lamp.position.set(x,6,2.5);
  if(c.guardian&&c.guardianOrigin){
    c.guardian.position.copy(c.guardianOrigin.position);
    c.guardian.position.y+=.16*Math.sin(t*1.3);
    c.guardian.rotation.y=c.guardianOrigin.rotation.y+.24*Math.sin(t*.8);
  }
  const cues=animeSpeakerCues(act),idx=Math.min(cues.length-1,Math.floor(u*cues.length));
  animeHud.querySelector('#animeCineCaption').textContent=cues[idx]||'';
  if(t>=134&&!c.ended){c.ended=true;paused=true;setSessionButtons();animeHud.querySelector('#animeCineCaption').textContent='TO BE CONTINUED · The next world is ours to build.'}
  animeUpdateControls();
}
// A narrow public diagnostics surface for native acceptance and future director tools.
window.SWYRL_ENGINE_CINEMATIC=Object.freeze({
  status:()=>({active:!!animeCine,playing,paused,elapsed:animeCine?.elapsed||0,
    stage:animeCine?.stage??-1,ended:animeCine?.ended||false,
    camera:animeCine?perspectiveCamera.position.toArray():null,
    projectId:currentProject?.canonicalId||null}),
  seek:seconds=>animeSeek(seconds),
  explore:()=>document.getElementById('animeCineExplore')?.click()
});
"""
def apply(html):
    s=html
    # Cinematic code is in the same module as engine's scene and Play lifecycle.
    assert '<script type="module">' in s
    s=s.replace('<script type="module">',CSS+'<script type="module">',1)
    s=once(s,'function beginPlay(fromHere=null){',JS+'\nfunction beginPlay(fromHere=null){')
    # Branch only Anime Studio; existing Play is untouched for every other starter.
    pointer="if(matchMedia('(pointer:fine)').matches)$('viewport').requestPointerLock?.();"
    s=once(s,pointer,"if(currentProject?.canonicalId==='ghosts-different-forms-ep01'&&!animeExploreOnce){animeStartCinematic()}else "+pointer)
    s=once(s,'function updateHero(dt, t){',"function updateHero(dt, t){\n  if(animeCine?.active)return;")
    s=once(s,'function stopSession(){',"function stopSession(){\n  animeEndCinematic();")
    s=once(s,'updateWorkspaceInteraction(t);if(shouldRenderFrame(frameNow))renderer.render(scene,camera);',
        'updateWorkspaceInteraction(t);animeUpdateCinematic(dt);if(shouldRenderFrame(frameNow))renderer.render(scene,camera);')
    s=once(s,'V8_5_ANIME_STUDIO_STARTER','V8_6_NATIVE_ANIME_CINEMATIC')
    s=s.replace('Maker v8.5','Maker v8.6').replace('MAKER v8.5','MAKER v8.6')
    s=s.replace("version:'v8.5'","version:'v8.6'").replace('version:8.5','version:8.6')
    s=s.replace("version:'swyrl-engine-agent-v6.5'","version:'swyrl-engine-agent-v6.6'")
    s=s.replace('§E v8.5 Tools','§E v8.6 Tools')
    s=s.replace('v8.5 · ANIME STUDIO STARTER','v8.6 · NATIVE ANIME CINEMATIC')
    s=s.replace('§wyrl§ Engine v8.5 · anime studio starter ready','§wyrl§ Engine v8.6 · native anime cinematic playback')
    return s
