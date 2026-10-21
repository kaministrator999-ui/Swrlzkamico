import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';

// Native editor input and the actual renderer share one deterministic RAF clock.
// No pose, effect, timeline or Three.js production function is replaced.
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const query=new URLSearchParams(process.env.SWYRL_ANIME_TEST_QUERY||'');query.set('project','anime-ghosts-ep01');
const output=resolve(process.env.SWYRL_ANIME_SCREENSHOTS_DIR||'episode-performance-acceptance');
await mkdir(output,{recursive:true});
const modes=[
  {name:'desktop',viewport:{width:1440,height:900},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:390,height:844},isMobile:true,hasTouch:true}
].filter(mode=>!process.env.SWYRL_ANIME_TEST_MODE||process.env.SWYRL_ANIME_TEST_MODE===mode.name);
assert.ok(modes.length,'SWYRL_ANIME_TEST_MODE must be desktop or mobile');
const browser=await chromium.launch({headless:true,
  ...(process.env.SWYRL_CHROMIUM_PATH?{executablePath:process.env.SWYRL_CHROMIUM_PATH}:{}),
  args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const receipts=[],touchPages=new WeakSet();
const saved=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.serializedProject());
const state=page=>page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.status());
const performanceModel=page=>page.evaluate(()=>window.SWYRL_ENGINE_PERFORMANCE.model());
const effectsModel=page=>page.evaluate(()=>window.SWYRL_ENGINE_STORY_EFFECTS.model());
const frames=(page,count=1,ms=50)=>page.evaluate(({count,ms})=>window.__episodePerformanceClock.step(count,ms),{count,ms});
const close=(a,b,label,tolerance=1e-5)=>assert.ok(Number.isFinite(a)&&Math.abs(a-b)<=tolerance,label+': expected '+b+', received '+a);
const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
const authored=data=>({scene:data.scene,layers:data.editor.layers,project:data.project});
const models=data=>Object.fromEntries(['animeTimeline','animeRigs','animeSockets','animeScenery','animeRelief','animeEmergence','animePerformance','animeStoryEffects'].map(key=>[key,data.project[key]]));
async function press(page,selector){const el=page.locator(selector);await el.scrollIntoViewIfNeeded();
  assert.equal(await el.isVisible(),true,'Native control is hidden: '+selector);
  if(touchPages.has(page))await el.tap({force:true});else await el.click({force:true});}
const tap=(page,id)=>press(page,'#'+id);
async function input(page,id,value){await page.locator('#'+id).evaluate((el,value)=>{el.value=String(value);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));},value);}
async function studio(page){if(!await page.locator('#storyStudioPanel').isVisible())await tap(page,'storyStudioBtn');}
async function closeStudio(page){if(await page.locator('#storyStudioPanel').isVisible())await tap(page,'storyClose');}
async function openDetails(page,id){await studio(page);if(!await page.locator('#'+id).evaluate(el=>el.open))await press(page,'#'+id+' > summary');}
async function exitPreview(page){await closeStudio(page);await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());await frames(page,1);}
async function history(page,kind){await exitPreview(page);const quick=page.locator(kind==='undo'?'#quickUndoBtn':'#quickRedoBtn');
  if(await quick.isVisible())await press(page,kind==='undo'?'#quickUndoBtn':'#quickRedoBtn');else{
    if(!await page.locator('#mobileToolsPanel').isVisible())await tap(page,'mobileToolsBtn');await press(page,'#mobileToolsPanel [data-click="'+kind+'Btn"]');}
  await frames(page,2);}
async function seek(page,time){assert.equal(await page.evaluate(t=>window.SWYRL_ENGINE_ANIMATION.seek(t),time),true,'Native seek failed at '+time);await frames(page,1);return observation(page);}
async function stop(page){await closeStudio(page);if(await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus().preview))await page.evaluate(()=>window.SWYRL_ENGINE_STORYBOARD.exitPreview());else if((await state(page)).active)await tap(page,'animeCineExit');else if((await state(page)).playing)await page.evaluate(()=>document.getElementById('stopBtn').click());
  await frames(page,1);assert.equal((await state(page)).playing,false);assert.equal((await state(page)).active,false);}
async function observation(page){return page.evaluate(()=>{
  const rigs=Object.fromEntries(['kami','swyrlz'].map(ch=>{const r=window.SWYRL_ENGINE_RIG.renderStatus(ch),d=window.SWYRL_ENGINE_RELIEF.renderStatus(ch);
    return [ch,{rigged:r.rigged,joints:r.joints,bounds:r.bounds,face:{expression:r.face?.expression,mouth:r.face?.mouth,speech:r.face?.speech,
      blink:r.face?.blink,gazeX:r.face?.gazeX,gazeY:r.face?.gazeY,brow:r.face?.brow,minFeatureClearance:r.face?.minFeatureClearance,pixelCount:r.face?.pixelCount},
      connections:r.connections?.map(c=>({child:c.child,connected:c.connected,error:c.error,parentSocketWorld:c.parentSocketWorld,childAttachWorld:c.childAttachWorld})),
      staff:r.staffGrip?{gripError:r.staffGrip.gripError,shaftLength:r.staffGrip.shaftLength,shaftTop:r.staffGrip.shaftTopWorld,shaftBase:r.staffGrip.shaftBaseWorld,
        gripFacingRight:r.staffGrip.gripFacingRight,fullStyle:r.staffGrip.fullStaff?.style,ready:r.staffGrip.fullStaff?.ready,
        cardHeight:r.staffGrip.fullStaff?.card?.height,core:r.staffGrip.shaftGeometry?.type}:null,
      relief:{schema:d.schema,rigged:d.rigged,sectionCount:d.sectionCount,parts:Object.fromEntries(Object.entries(d.parts||{}).filter(([,p])=>p.rendered).map(([id,p])=>[id,
        {secondaryFlex:p.secondaryFlex,thickness:p.thickness,sections:p.sections.map(s=>({id:s.id,depth:s.localBounds.depthSpan,worldBounds:s.worldBounds}))}]))}}];}));
  return {stage:window.SWYRL_ENGINE_STORYBOARD.stageStatus(),rigs,performance:window.SWYRL_ENGINE_PERFORMANCE.status(),
    effects:window.SWYRL_ENGINE_STORY_EFFECTS.status(),emergence:window.SWYRL_ENGINE_EMERGENCE.status(),scenery:window.SWYRL_ENGINE_SCENERY.renderStatus()};});}
function safe(o,label,{readable=true}={}){const s=o.stage;
  assert.equal(s.assetsReady,true,'Artwork is not ready: '+label);assert.deepEqual(s.assetErrors,[],'Artwork failed: '+label);
  assert.equal(s.occlusionSafe,true,'Scenery hides the camera/cast: '+label);assert.ok(s.safeCameraGap>1,'Scenery enters camera: '+label);
  assert.ok(s.camera.position.every(Number.isFinite),'Camera contains non-finite coordinates: '+label);
  for(const ch of ['kami','swyrlz']){const r=o.rigs[ch];assert.equal(r.rigged,true,'Rig lost: '+label+' '+ch);
    assert.ok(r.connections.length>=18,'Anatomical sockets missing: '+label+' '+ch);
    for(const c of r.connections){assert.equal(c.connected,true,'Disconnected '+c.child+': '+label);assert.ok(c.error<1e-5,'Detached '+c.child+': '+label);
      close(c.error,distance(c.parentSocketWorld,c.childAttachWorld),'Independent socket distance '+c.child,1e-7);}
    assert.equal(r.relief.schema,'anime-character-relief-v1');assert.ok(r.relief.sectionCount>=54,'Costume loses per-piece depth: '+label);
    for(const p of Object.values(r.relief.parts)){assert.ok(p.thickness>0);assert.equal(p.sections.length,3);for(const section of p.sections)assert.ok(section.depth>0,'Flat paper section: '+label);}
    if(readable){const cast=s.castBounds.find(c=>c.id===ch);assert.ok(cast&&cast.visible,'Mage hidden: '+label+' '+ch);
      const rect=cast.screen||cast.rect||cast;if(['left','right','top','bottom'].every(k=>Number.isFinite(rect[k])))
        assert.ok(rect.right>rect.left&&rect.bottom>rect.top,'Mage has no projected area: '+label+' '+ch);
      assert.ok(r.face.pixelCount>50&&r.face.minFeatureClearance>.008,'Facial features buried in the head: '+label+' '+ch);}}
  const staff=o.rigs.kami.staff;assert.equal(staff.fullStyle,'painted-full-v1','Full staff replaced by a wand: '+label);
  assert.equal(staff.ready,true,'Full staff texture not ready: '+label);assert.ok(staff.cardHeight>4.5&&staff.cardHeight<6.5,'Staff lost its full-length proportions: '+label);
  assert.equal(staff.core,'CylinderGeometry','Staff is a rectangular prop: '+label);assert.ok(staff.gripError<1e-5,'Staff left the holding hand: '+label);
  for(const e of o.effects.items.filter(e=>e.visible)){assert.equal(e.behindCast,true,'Magic covers faces: '+label+' '+e.id);assert.ok(e.cameraGap>=7-1e-5,'Effect enters camera near field: '+label);assert.ok(e.depthSpan>0);}
}
function pose(o){return {rigs:Object.fromEntries(Object.entries(o.rigs).map(([ch,r])=>[ch,{joints:r.joints,face:r.face,relief:r.relief,staff:r.staff}])),
  effects:o.effects.items.map(e=>({id:e.id,visible:e.visible,matrix:e.matrix,bounds:e.bounds,parts:e.parts,sample:e.sample}))};}
function assertScaled(before,after,ratio){
  const keys=(a,b,label)=>{assert.equal(b.length,a.length,'Duration changes key count: '+label);a.forEach((k,i)=>{
    close(b[i].time,k.time*ratio,'Scaled '+label+' time');const {time:ta,...va}=k,{time:tb,...vb}=b[i];assert.deepEqual(vb,va,'Duration changes '+label+' pose');});};
  close(after.animeTimeline.duration,before.animeTimeline.duration*ratio,'Episode duration');
  for(const [id,list] of Object.entries(before.animeTimeline.tracks))keys(list,after.animeTimeline.tracks[id],'stage '+id);
  before.animeTimeline.beats.forEach((beat,i)=>{const next=after.animeTimeline.beats[i];close(next.time,beat.time*ratio,'Beat start');close(next.end,beat.end*ratio,'Beat end');keys(beat.cues,next.cues,'dialogue');});
  for(const ch of ['kami','swyrlz']){const a=before.animeRigs.characters[ch],b=after.animeRigs.characters[ch];keys(a.face,b.face,ch+' face');for(const [part,list] of Object.entries(a.joints))keys(list,b.joints[part],ch+' '+part);}
  for(const [id,obj] of Object.entries(before.animeScenery.objects))keys(obj.keys,after.animeScenery.objects[id].keys,'scenery '+id);
  for(const name of ['animePerformance','animeStoryEffects']){const field=name==='animePerformance'?'clips':'cues';assert.equal(after[name][field].length,before[name][field].length);
    before[name][field].forEach((clip,i)=>{const next=after[name][field][i];close(next.time,clip.time*ratio,'Scaled '+name+' start');close(next.duration,clip.duration*ratio,'Scaled '+name+' span');
      const {time:ta,duration:da,...va}=clip,{time:tb,duration:db,...vb}=next;assert.deepEqual(vb,va,'Duration changes action/effect parameters');});}
  for(const name of ['animeSockets','animeRelief','animeEmergence'])assert.deepEqual(after[name],before[name],'Duration mutates physical '+name);
}
async function start(page){await page.goto(base+'/index.html?'+query,{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_PERFORMANCE&&window.SWYRL_ENGINE_STORY_EFFECTS&&window.SWYRL_ENGINE_ANIMATION?.status().projectId==='ghosts-different-forms-ep01',undefined,{timeout:60000,polling:100});
  await page.waitForFunction(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus().assetsReady&&window.SWYRL_ENGINE_RIG.renderStatus('kami').staffGrip?.fullStaff?.ready,undefined,{timeout:60000,polling:100});
  await page.locator('#perfPreset').selectOption('medium',{force:true});await page.evaluate(()=>window.__episodePerformanceClock.freeze());await frames(page,2);}
async function actualSave(page,name){await studio(page);const pending=page.waitForEvent('download',{timeout:15000});await tap(page,'storySaveProject');const download=await pending;
  const path=resolve(output,name+'.swyrl.json');await download.saveAs(path);return {path,data:JSON.parse(await readFile(path,'utf8'))};}
async function actualLoad(page,path){await stop(page);await page.locator('#fileInput').setInputFiles(path);
  await page.waitForFunction(()=>document.getElementById('fileInput').value==='',undefined,{timeout:15000,polling:100});await frames(page,2);
  await page.waitForFunction(()=>window.SWYRL_ENGINE_STORYBOARD.stageStatus().assetsReady,undefined,{timeout:45000,polling:100});}

try{for(const mode of modes){const context=await browser.newContext({viewport:mode.viewport,isMobile:mode.isMobile,hasTouch:mode.hasTouch,acceptDownloads:true});
  await context.addInitScript(()=>{const nativeRAF=requestAnimationFrame.bind(window),nativeCancel=cancelAnimationFrame.bind(window),nativeNow=performance.now.bind(performance),queue=new Map();let frozen=false,now=0,next=1000000000;
    Object.defineProperty(performance,'now',{configurable:true,value:()=>frozen?now:nativeNow()});
    window.requestAnimationFrame=callback=>{if(!frozen)return nativeRAF(callback);const id=next++;queue.set(id,callback);return id;};
    window.cancelAnimationFrame=id=>{queue.delete(id);nativeCancel(id);};
    window.__episodePerformanceClock={freeze:()=>{frozen=true;now=nativeNow();return new Promise(resolve=>nativeRAF(()=>nativeRAF(resolve)));},
      step:(count,ms)=>{if(!frozen)throw Error('Frame clock is not frozen');for(let i=0;i<count;i++){now+=ms;const pending=[...queue.values()];queue.clear();if(!pending.length)throw Error('Actual engine RAF stopped');for(const callback of pending)callback(now);}return {now,pending:queue.size};}};});
  let page=await context.newPage();const errors=[],cases=[],samples=[];
  const attach=p=>{p.setDefaultTimeout(30000);if(mode.hasTouch)touchPages.add(p);p.on('pageerror',e=>errors.push(String(e)));p.on('response',r=>{if(r.status()>=400&&r.url().startsWith(base)&&/\.(png|webp|jpe?g)(\?|$)/i.test(r.url()))errors.push('Artwork '+r.status()+' '+r.url());});};attach(page);
  const pass=name=>{assert.equal(cases.includes(name),false,'Duplicate acceptance case');cases.push(name);console.log('EPISODE_PERFORMANCE_CASE_PASSED',mode.name,name);};
  try{const response=await page.request.get(base+'/index.html?'+query);assert.equal(response.status(),200);const sourceSha256=createHash('sha256').update(await response.body()).digest('hex');
    console.log('EPISODE_PERFORMANCE_SOURCE_SHA256',mode.name,sourceSha256);await start(page);
    assert.equal(await page.evaluate(()=>window.SWRLZ_FORGE_BUILD.version),'v11.62');
    await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.openProjects());await frames(page,1);await press(page,'[data-project-template="anime-ghosts-ep01"]');await frames(page,2);
    const canonical=await saved(page),timeline=canonical.project.animeTimeline,performance=await performanceModel(page),effects=await effectsModel(page);
    assert.equal(canonical.scene.actors.length,70);assert.equal(canonical.editor.layers.length,11);assert.equal(timeline.duration,134);assert.equal(timeline.beats.length,8);
    assert.deepEqual(timeline.beats.map(b=>b.title),['The Sleeping Book','A Ghost in the Margins','A World Coming Undone','Too Much Fire','Hold the Light','A Door Made Together','Two Mages, One World','The First Step']);
    const text=timeline.beats.flatMap(b=>b.cues.map(c=>c.text)).join('\n');assert.match(text,/way home/);assert.match(text,/too much fire/i);assert.match(text,/fading/);assert.match(text,/write our names/i);assert.match(text,/your light.*my words/i);assert.match(text,/continued/i);
    assert.equal(performance.enabled,true);assert.equal(performance.limitDialogue,true);assert.ok(performance.clips.length>=30);assert.equal(effects.enabled,true);assert.ok(effects.cues.length>=10);
    assert.equal(canonical.project.animeRigs.characters.kami.staffArt,'painted-full-v1');assert.equal(canonical.project.animeEmergence.duration,12);
    const historicalIds=['layer-ep-sets','layer-ep-fx','layer-ep-cast'];assert.ok(canonical.editor.layers.filter(l=>historicalIds.includes(l.id)).every(l=>l.visible===false));
    pass('native_projects_opens_causal_eight_chapter_episode_with_separate_saved_cast_and_scenery');

    const opening=[];for(const time of [0,4,8,12]){const o=await seek(page,time);safe(o,'opening '+time,{readable:time>=12});opening.push(o.emergence);}
    for(const id of ['book','kami','swyrlz','background','midground']){const progresses=opening.map(o=>o.layers.find(l=>l.id===id).progress);assert.ok(progresses.every((p,i)=>i===0||p>=progresses[i-1]),'Opening reverses '+id);close(progresses.at(-1),1,'Opening finishes '+id);assert.ok(progresses[0]<progresses.at(-1));}
    const stars=(await observation(page)).scenery.starLayers;assert.equal(stars.length,3);assert.equal(new Set(stars.map(s=>s.z.toFixed(2))).size,3,'Star shells collapsed to one depth');
    pass('twelve_second_book_emergence_preserves_articulated_depth_full_staff_and_connected_sockets');

    const actionChecks=[{action:'reach',character:'kami',time:27.5,part:'rightUpperArm'},
      {action:'brace',character:'kami',time:43.3,part:'leftLowerLeg'},
      {action:'cast',character:'kami',time:52.5,part:'leftUpperArm'},
      {action:'write',character:'swyrlz',time:79,part:'rightForearm'},
      {action:'step',character:'kami',time:126.37,part:'leftUpperLeg'}];
    const expressions=new Set(),capeFlex=[];
    for(const check of actionChecks){const o=await seek(page,check.time);safe(o,check.action);assert.ok(o.performance.active.some(a=>a.character===check.character&&a.action===check.action&&a.weight>0));
      const key=await page.evaluate(({character,part,time})=>({base:window.SWYRL_ENGINE_RIG.sample(character,part,time),applied:window.SWYRL_ENGINE_PERFORMANCE.sample(character,part,time)}),check);
      const rendered=o.rigs[check.character].joints[check.part].rotation,expected=['rotationX','rotationY','rotationZ'].map(k=>key.applied[k]),baseRotation=['rotationX','rotationY','rotationZ'].map(k=>key.base[k]);
      assert.ok(distance(expected,baseRotation)>.005,'Action has no actual limb movement: '+check.action);close(distance(rendered,expected),0,'Renderer did not apply '+check.action,1e-6);
      capeFlex.push(o.rigs[check.character].relief.parts.cape.secondaryFlex);for(const r of Object.values(o.rigs))expressions.add(r.face.expression);samples.push({time:check.time,action:check.action,character:check.character,rotation:rendered});}
    assert.ok(expressions.size>=3,'Story actions have no distinct facial reactions');assert.ok(new Set(capeFlex.map(v=>v.toFixed(5))).size>=3,'Costume depth remains static while limbs move');
    const a=await page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.sample('kami',125)),b=await page.evaluate(()=>window.SWYRL_ENGINE_ANIMATION.sample('kami',129));assert.ok(distance([a.x,a.y,a.z],[b.x,b.y,b.z])>.5,'Walking limbs do not travel toward the doorway');
    await page.screenshot({path:resolve(output,mode.name+'-performed-walk.png')});
    pass('reach_brace_cast_write_and_walk_apply_distinct_joint_costume_and_face_performances');

    const speaking=await seek(page,14.35);assert.equal(speaking.rigs.kami.face.speech,true);assert.ok(speaking.rigs.kami.face.mouth>.07);assert.equal(speaking.rigs.swyrlz.face.speech,false);
    const quiet=await seek(page,19.2);assert.equal(quiet.rigs.kami.face.speech,false);assert.equal(quiet.rigs.swyrlz.face.speech,false);close(quiet.rigs.kami.face.mouth,0,'Mouth remains open after finite dialogue');
    assert.match(await page.locator('#animeCineCaption').innerText(),/floating skull|librarian/i,'Persistent caption vanished before the next line');
    const narrator=await seek(page,1);for(const r of Object.values(narrator.rigs)){assert.equal(r.face.speech,false);close(r.face.mouth,0,'Narrator animates a mage mouth');}
    pass('dialogue_mouth_stops_between_persistent_captions_and_narrator_leaves_both_mages_silent');

    for(const effect of ['page','burst','ink','portal']){const cue=effects.cues.find(c=>c.effect===effect&&(effect!=='page'||c.time>=14)&&(effect!=='portal'||c.duration>20));assert.ok(cue,'Missing '+effect+' story action');
      const early=await seek(page,cue.time+cue.duration*.16),lateTime=cue.time+cue.duration*.68,late=await seek(page,lateTime);safe(early,'early '+effect);safe(late,'late '+effect);
      const first=early.effects.items.find(i=>i.id===cue.id),last=late.effects.items.find(i=>i.id===cue.id);assert.equal(first.visible,true);assert.equal(last.visible,true);assert.ok(last.meshCount>=2,'Effect has no actual paper geometry: '+effect);
      if(effect==='page')assert.notDeepEqual(first.parts.hingeRotation,last.parts.hingeRotation,'Page hinge is static');
      if(effect==='burst')assert.notDeepEqual(first.parts.chipWorldPositions,last.parts.chipWorldPositions,'Failed cast fragments are static');
      if(effect==='ink'){assert.ok(last.parts.strokeDrawRange.count>first.parts.strokeDrawRange.count,'Ink is not progressively drawn');assert.ok(last.parts.strokeDrawRange.count<=last.parts.strokeVertexCount);}
      if(effect==='portal'){assert.ok(last.parts.traceDrawRange.count>first.parts.traceDrawRange.count,'Portal outline is not progressively drawn');assert.ok(last.parts.doors.some(d=>Math.abs(d.rotationY)>.5),'Door never physically opens');assert.equal(last.parts.starsVisible,true);}
      await seek(page,cue.time+cue.duration*.3);const repeated=await seek(page,lateTime);assert.deepEqual(pose(repeated),pose(late),'Backward/direct seek changes rendered '+effect);
      samples.push({effect,id:cue.id,time:lateTime,geometry:last.parts});}
    for(const beat of timeline.beats){const time=Math.max(12,Math.min(133.5,(beat.time+beat.end)/2)),o=await seek(page,time);safe(o,'chapter '+beat.title);}
    await page.screenshot({path:resolve(output,mode.name+'-shared-door.png')});
    pass('page_backfire_ink_and_opening_portal_progress_in_actual_geometry_and_seek_without_camera_occlusion');

    await exitPreview(page);const baseRigs=structuredClone((await saved(page)).project.animeRigs),beforeActions=await performanceModel(page);
    await openDetails(page,'storyPerformanceSection');await tap(page,'performanceNew');
    await page.locator('#performanceCharacter').selectOption('kami',{force:true});await page.locator('#performanceAction').selectOption('reach',{force:true});await page.locator('#performanceSide').selectOption('right',{force:true});
    for(const [id,value] of Object.entries({performanceTime:31.137,performanceDuration:2.2,performanceStrength:.8,performanceLabel:'Acceptance reach'}))await input(page,id,value);
    await tap(page,'performanceSave');const added=(await performanceModel(page)).clips.find(c=>!beforeActions.clips.some(b=>b.id===c.id));assert.ok(added);assert.equal(added.action,'reach');
    const baseAt=await page.evaluate(t=>window.SWYRL_ENGINE_RIG.sample('kami','rightUpperArm',t),32.137);
    await page.locator('#storyTrack').selectOption('kami',{force:true});await input(page,'storyTime',32.137);await page.locator('#rigPart').selectOption('rightUpperArm',{force:true});
    await tap(page,'rigAddKey');const inserted=(await saved(page)).project.animeRigs.characters.kami.joints.rightUpperArm.find(k=>Math.abs(k.time-32.137)<1e-6);assert.ok(inserted);
    for(const field of ['rotationX','rotationY','rotationZ','depth'])close(inserted[field],baseAt[field],'Pose editor double-bakes active action '+field,.000002);
    await history(page,'undo');assert.deepEqual((await saved(page)).project.animeRigs,baseRigs,'Undo pose key does not restore base curves');
    await openDetails(page,'storyPerformanceSection');await page.locator('#performanceClip').selectOption(added.id,{force:true});await input(page,'performanceStrength',.45);await input(page,'performanceLabel','Edited reach');await tap(page,'performanceSave');
    const edited=(await performanceModel(page)).clips.find(c=>c.id===added.id);close(edited.strength,.45,'Native action update');assert.equal(edited.label,'Edited reach');
    await tap(page,'performanceDelete');assert.equal((await performanceModel(page)).clips.some(c=>c.id===added.id),false);
    await history(page,'undo');assert.deepEqual((await performanceModel(page)).clips.find(c=>c.id===added.id),edited);
    await history(page,'undo');assert.deepEqual((await performanceModel(page)).clips.find(c=>c.id===added.id),added);
    await history(page,'undo');assert.deepEqual(await performanceModel(page),beforeActions);
    for(let i=0;i<3;i++)await history(page,'redo');assert.deepEqual(await performanceModel(page),beforeActions);assert.deepEqual((await saved(page)).project.animeRigs,baseRigs);
    pass('native_action_add_update_delete_and_history_preserve_unbaked_independent_limb_keys');

    await openDetails(page,'storyEffectsSection');const cue=effects.cues.find(c=>c.effect==='ink');await page.locator('#effectCue').selectOption(cue.id,{force:true});await input(page,'effectLabel','Kami · §wyrlz · remembered');await tap(page,'effectApply');
    const editedEffect=(await effectsModel(page)).cues.find(c=>c.id===cue.id);assert.equal(editedEffect.label,'Kami · §wyrlz · remembered');
    await history(page,'undo');assert.deepEqual(await effectsModel(page),effects);await history(page,'redo');assert.deepEqual((await effectsModel(page)).cues.find(c=>c.id===cue.id),editedEffect);await history(page,'undo');
    const beforeDuration=models(await saved(page));await openDetails(page,'storyPerformanceSection');await input(page,'performanceEpisodeDuration',268);await tap(page,'performanceApplyDuration');
    assertScaled(beforeDuration,models(await saved(page)),2);await history(page,'undo');assert.deepEqual(models(await saved(page)),beforeDuration,'One Undo does not restore all models from duration edit');
    await history(page,'redo');assertScaled(beforeDuration,models(await saved(page)),2);await history(page,'undo');assert.deepEqual(models(await saved(page)),beforeDuration);
    pass('native_effect_edit_and_episode_duration_rescale_share_complete_single_step_undo');

    await seek(page,93);const exportPreview=await actualSave(page,mode.name+'-performed-episode');assert.deepEqual(models(exportPreview.data),models(await saved(page)));
    assert.deepEqual(exportPreview.data.scene,canonical.scene,'Transient preview geometry contaminates native Save');assert.deepEqual(exportPreview.data.editor.layers,canonical.editor.layers);
    assert.equal(exportPreview.data.scene.actors.length,70);assert.ok(exportPreview.data.scene.actors.every(a=>!String(a.type).includes('storyEffect')));
    await closeStudio(page);await page.close();page=await context.newPage();attach(page);await start(page);await actualLoad(page,exportPreview.path);
    assert.deepEqual(models(await saved(page)),models(exportPreview.data),'Actual project file Load drops independent authored animation');assert.deepEqual((await saved(page)).scene,exportPreview.data.scene);
    const restored=await seek(page,93);safe(restored,'fresh file Load');
    pass('actual_native_save_download_and_fresh_file_load_preserve_curves_without_runtime_nodes');

    await exitPreview(page);const beforePlay=await saved(page);await tap(page,'playBtn');await frames(page,4);assert.equal((await state(page)).playing,true);assert.equal((await state(page)).active,true);
    await tap(page,'animeCinePause');const pausedTime=(await state(page)).elapsed;await frames(page,4);close((await state(page)).elapsed,pausedTime,'Native Pause advances the story');
    const performed=await seek(page,93);safe(performed,'native Play');const nativePose=pose(performed);await stop(page);assert.deepEqual(authored(await saved(page)),authored(beforePlay));
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_STORY_EFFECTS.status())).poolSize,0,'Stop leaks transient effect nodes');
    await tap(page,'animeScreeningBtn');await frames(page,2);assert.equal(await page.locator('#storyCinemaStage canvas').count(),1);await tap(page,'animeCinePause');
    const watched=await seek(page,93);safe(watched,'native Watch');assert.deepEqual(pose(watched),nativePose,'Watch uses different performed poses or magic from native Play');
    await input(page,'animeCineScrub',60);await tap(page,'animeCinePause');const deltas=[];
    for(const direction of ['animeCineFastForward','animeCineRewind'])for(const rate of direction==='animeCineFastForward'?[2,4,8,1]:[-2,-4,-8,1]){
      await tap(page,direction);const a=await page.evaluate(()=>window.SWYRL_ENGINE_TRANSPORT.status());close(a.rate,rate,'Signed Watch speed');await frames(page,2);
      const b=await page.evaluate(()=>window.SWYRL_ENGINE_TRANSPORT.status());close(b.elapsed-a.elapsed,rate*.1,'Actual performed RAF at '+rate+'x');deltas.push({rate,delta:b.elapsed-a.elapsed});}
    await input(page,'animeCineScrub',93.4);await tap(page,'animeCineRewind');await frames(page,4);await tap(page,'animeCinePause');close((await state(page)).elapsed,93,'Rewind misses authored frame');
    const reversed=await observation(page);
    const compareRewound=(actual,expected,path='pose')=>{
      if(typeof actual==='number'&&typeof expected==='number'){
        close(actual,expected,'Signed rewind numeric pose '+path,1e-8);return;
      }
      if(actual&&expected&&typeof actual==='object'&&typeof expected==='object'){
        assert.deepEqual(Object.keys(actual),Object.keys(expected),'Signed rewind structure '+path);
        for(const key of Object.keys(expected))compareRewound(actual[key],expected[key],path+'.'+key);
        return;
      }
      assert.equal(actual,expected,'Signed rewind discrete pose '+path);
    };
    // Signed RAF integration lands within floating-point epsilon of a key time.
    // Preserve exact strings/flags/structure while comparing geometric numbers.
    compareRewound(pose(reversed),nativePose);
    for(const clip of (await performanceModel(page)).clips){for(const time of [clip.time,clip.time+clip.duration]){
      const same=await page.evaluate(({character,time})=>['torso','leftUpperLeg','rightUpperArm','cape'].every(part=>{
        const a=window.SWYRL_ENGINE_RIG.sample(character,part,time),b=window.SWYRL_ENGINE_PERFORMANCE.sample(character,part,time);
        // Overlapping clips may remain active; only inspect boundaries without
        // another contributing performance for this character.
        const active=window.SWYRL_ENGINE_PERFORMANCE.status(time).active.filter(c=>c.character===character);
        return active.length||['rotationX','rotationY','rotationZ','depth'].every(k=>Math.abs(a[k]-b[k])<1e-6);
      }),{character:clip.character,time});assert.equal(same,true,'Performance endpoint fails to settle to authored curves');}}
    await stop(page);assert.deepEqual(authored(await saved(page)),authored(beforePlay));assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_STORY_EFFECTS.status())).poolSize,0);
    samples.push({signedRates:deltas});pass('native_play_watch_pause_and_signed_shuttles_rebuild_identical_performances_and_stop_restores_editor');

    const historicalResponse=await page.request.get(base+'/scenes/ghosts-in-different-forms-ep01-full-staff.swyrl.json');assert.equal(historicalResponse.status(),200);
    const historical=await historicalResponse.json(),historicalPath=resolve(output,mode.name+'-published-full-staff.swyrl.json');await writeFile(historicalPath,JSON.stringify(historical));await actualLoad(page,historicalPath);
    assert.equal((await performanceModel(page)).enabled,false,'Old saved episode silently opts into new actions');assert.equal((await effectsModel(page)).enabled,false,'Old saved episode silently opts into new magic');
    const oldFrame=await seek(page,52.5);safe(oldFrame,'published full staff');assert.equal(oldFrame.effects.poolSize,0);assert.deepEqual((await saved(page)).scene,historical.scene);
    await exitPreview(page);await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.openProjects());await frames(page,1);await press(page,'[data-project-template="anime-ghosts-ep01"]');await frames(page,2);
    assert.deepEqual(models(await saved(page)),models(canonical),'Native Projects does not return the improved default');
    await seek(page,93);await stop(page);await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.openProjects());await frames(page,1);await press(page,'[data-project-template="maul-frostveil"]');await frames(page,2);
    const other=await saved(page);assert.equal(other.project.canonicalId,'maul-frostveil');assert.equal(other.project.animePerformance,undefined);assert.equal(other.project.animeStoryEffects,undefined);
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_STORY_EFFECTS.status())).poolSize,0);assert.equal((await performanceModel(page)).enabled,false);
    await tap(page,'playBtn');await frames(page,3);assert.equal((await state(page)).active,false,'Maul starts anime performance');await page.evaluate(()=>document.getElementById('stopBtn').click());await frames(page,1);assert.deepEqual((await saved(page)).scene,other.scene);
    pass('published_episode_import_keeps_opt_out_profiles_and_other_starters_dispose_performance_geometry');

    assert.deepEqual(errors,[],'Unhandled native browser errors');assert.equal(cases.length,10,'All focused performance proofs must execute');
    const receipt={mode:mode.name,viewport:mode.viewport,version:'v11.62',sourceSha256,cases,nativeProject:canonical.project.canonicalId,actors:70,layers:11,duration:134,chapters:timeline.beats.map(b=>b.title),actions:performance.clips.length,effectCues:effects.cues.length,samples};
    receipts.push(receipt);await writeFile(resolve(output,mode.name+'-receipt.json'),JSON.stringify(receipt,null,2));console.log(mode.name==='desktop'?'EPISODE_PERFORMANCE_DESKTOP_PASS':'EPISODE_PERFORMANCE_MOBILE_PASS');
  }catch(error){await page.screenshot({path:resolve(output,mode.name+'-failure.png')}).catch(()=>{});await writeFile(resolve(output,mode.name+'-failure.json'),JSON.stringify({message:String(error),cases,errors,state:await state(page).catch(()=>null),observation:await observation(page).catch(()=>null)},null,2));throw error;}
  finally{await context.close();}}
  await writeFile(resolve(output,'receipt.json'),JSON.stringify(receipts,null,2));console.log('EPISODE_PERFORMANCE_ALL_VIEWPORTS_PASS');
}finally{await browser.close();}
