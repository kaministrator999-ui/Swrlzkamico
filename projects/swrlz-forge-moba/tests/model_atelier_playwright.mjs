import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
const base=(process.env.SWYRL_ANIME_TEST_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const modes=[{name:'desktop',viewport:{width:1536,height:960},isMobile:false,hasTouch:false},
  {name:'mobile',viewport:{width:412,height:915},isMobile:true,hasTouch:true}];
const browser=await chromium.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
await mkdir('model-atelier-acceptance',{recursive:true});
try{
  for(const mode of modes){
    const context=await browser.newContext(mode);
    const page=await context.newPage();
    const faults=[];
    page.on('pageerror',e=>faults.push(String(e)));
    await page.goto(base+'/?project=model-atelier',{waitUntil:'domcontentloaded',timeout:60000});
    await page.locator('#modelAtelierPanel:not([hidden]) canvas').waitFor({timeout:30000});
    assert.match(await page.locator('.brand').innerText(),/ENGINE · MAKER v11\.62/,'Main editor brand must show live v11.62');
    assert.equal(await page.title(),'§wyrl§ Engine · Maker v11.62','Browser document title must identify the current release');
    assert.match(await page.locator('#modelAtelierPanel .atelier-head strong').innerText(),/v11\.62 · adaptive Model Atelier tools/,'Model Atelier panel must show live version');
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_BUILD.version),'v11.62','Runtime build version must match the live editor');
    // Preserve the full v11.12 editor regression on its exact legacy native fixture.
    await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.loadLegacy());
    await page.waitForFunction(()=>window.SWYRL_ENGINE_MODEL_ATELIER?.status().count===811,{timeout:20000});
    let state=await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status());
    assert.equal(state.active,true);assert.equal(state.open,true);assert.equal(state.count,811);
    assert.equal(await page.locator('[data-project-template="model-atelier"]').count(),1,'Starter card missing');
    assert.equal(await page.locator('#modelAtelierParts option').count(),811,'Not individually editable meshes');
    assert.equal(await page.locator('#modelAtelierPanel canvas').isVisible(),true,'3D viewport hidden');
    assert.equal(await page.locator('#modelAtelierPartCount').isVisible(),true);
    const geometryProof=await page.evaluate(()=>{
      const m=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier;
      return {lofts:m.parts.filter(p=>p.kind==='loft').length,fabric:m.parts.filter(p=>p.surfaceStyle==='fabric-panel').length,
              anatomy:m.parts.filter(p=>p.surfaceStyle==='anatomy-smooth').length,
              headNames:m.parts.filter(p=>p.name.includes('ferret · velvet head')).length,
              profile:m.parts.filter(p=>p.kind==='loft').map(p=>[p.path.length,p.radii.length]),
              paper:m.parts.filter(p=>p.surfaceStyle==='pinata-twisted').map(p=>[p.surfaceStyle,p.layers,p.facets,p.twistDegrees]),
              sculpted:m.parts.filter(p=>p.name.includes('head sculpt')).length,
              rear:m.parts.filter(p=>p.name.includes('rear')||p.name.includes('braided actual')).length};
    });
    assert.equal(geometryProof.lofts,16,'Missing native ferret, anatomical body and fabric lofts');
    assert.equal(geometryProof.fabric,8,'Fabric panel geometry missing');
    assert.equal(geometryProof.anatomy,6,'Continuous limb lofts missing');
    assert.equal(geometryProof.headNames,2,'Ferret heads failed to load');
    assert(geometryProof.profile.every(([p,r])=>p===r&&p>=3),'Loft control points lost');
    assert.equal(geometryProof.paper.length,2,'Both ferret sweeps must be twisted');
    assert(geometryProof.paper.every(([style,layers,facets])=>style==='pinata-twisted'&&layers===36&&facets===8),'Layered truncated-pyramid piñata profile missing');
    assert(geometryProof.sculpted>=30&&geometryProof.rear>=80,'Sculptural multiview detail missing');

    // v11.10: actual BufferGeometry metrics, not static part-count proxies.
    assert.equal(await page.locator('#modelAtelierMetrics summary').count(),1,'Geometry profiler missing');
    await page.locator('#modelAtelierMetrics summary').click();
    assert.equal(await page.locator('#modelAtelierMetricsBody').isVisible(),true,'Expanded profiler is hidden');
    const stats=page.locator('#modelAtelierMetricsBody .atelier-metric-row');
    const number=async index=>Number(((await stats.nth(index).locator('strong').textContent())||'').replaceAll(',','').replace(/[^0-9]/g,''));
    const originalTris=await number(1);
    assert.equal(await number(0),811,'Profiler did not count the native meshes');
    assert(originalTris>811,'Triangle counter should inspect generated geometry');
    assert((await page.locator('#modelAtelierMetricsBody').innerText()).includes('Azure frost'),'Ferret group breakdown missing');
    assert((await page.locator('#modelAtelierMetricsBody').innerText()).includes('Coral flare'),'Second ferret group missing');
    await page.locator('#modelAtelierMetrics summary').click();
    // v11.11: real native poses and camera frames are part of the editor,
    // not screenshots or a separate project shell.
    const neutralLeg=await page.evaluate(()=>{
      const p=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts;
      const byId=id=>p.find(x=>x.id===id);
      return {path:structuredClone(byId('atelier-v118-right-leg').path),
        mouthTilt:byId('model-0046').rotation[2],iris:byId('model-0026').scale[0]};
    });
    assert(neutralLeg.mouthTilt>.09&&neutralLeg.iris>.069,'Native face refinement did not load');
    await page.locator('#modelAtelierPoseDeck summary').click();
    await page.locator('#modelAtelierPoseSelect').selectOption('idle');
    await page.locator('#modelAtelierPoseApply').click();
    const idleLeg=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
      .find(x=>x.id==='atelier-v118-right-leg').path);
    // Screenshot rejection regression: support shin remains nearly straight while
    // relaxed foot moves sideways with its shoe assembly, soles never levitate.
    const idleGround=await page.evaluate(()=>{
      const p=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts;
      const get=id=>p.find(q=>q.id===id);
      return {left:get('atelier-v118-left-leg').path,right:get('atelier-v118-right-leg').path,
        soleL:get('v119-left-sole').position,soleR:get('v119-right-sole').position};
    });
    assert(Math.abs(idleLeg[3][2]-neutralLeg.path[3][2])<.04,'Idle support leg should NOT banana-bend');
    assert.equal(idleGround.soleL[1],.07,'Idle left foot left the floor');
    assert.equal(idleGround.soleR[1],.07,'Idle right foot left the floor');
    assert(idleGround.soleL[0]<-.315,'Relaxed foot should shift slightly outward');
    await page.locator('#modelAtelierPoseView').selectOption('back');
    await page.locator('#modelAtelierPoseViewApply').click();
    await page.locator('#modelAtelierPoseName').fill('Showcase back');
    await page.locator('#modelAtelierPoseSave').click();
    let frames=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.poseFrames);
    assert.equal(frames.length,1,'Native pose frame did not persist in source project');
    assert(frames[0].camera.yaw>3,'Saved frame did not keep back camera view');
    await page.locator('#modelAtelierPoseSelect').selectOption('victory');
    await page.locator('#modelAtelierPoseApply').click();
    const victoryLeg=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
      .find(x=>x.id==='atelier-v118-right-leg').path);
    assert(victoryLeg[3][2]>idleLeg[3][2]+.04,'Victory knee did not form a restrained anatomical bend');
    const victoryGround=await page.evaluate(()=>{
      const p=window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts;
      const get=id=>p.find(q=>q.id===id);
      return {rightSole:get('v119-right-sole').position,leftSole:get('v119-left-sole').position};
    });
    assert(victoryGround.rightSole[0]>.38,'Victory stance should shift right foot');
    assert.equal(victoryGround.rightSole[1],.07,'Victory foot lifted off the ground');
    assert.equal(victoryGround.leftSole[0],-.28,'Victory support foot wandered');
    await page.locator('#modelAtelierPoseSelect').selectOption('saved:Showcase back');
    await page.locator('#modelAtelierPoseApply').click();
    const restoredLeg=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
      .find(x=>x.id==='atelier-v118-right-leg').path);
    assert.deepEqual(restoredLeg,idleLeg,'Saved frame did not restore editable native spline');
    await page.locator('#modelAtelierPoseSelect').selectOption('neutral');
    await page.locator('#modelAtelierPoseApply').click();
    const afterNeutral=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts
      .find(x=>x.id==='atelier-v118-right-leg').path);
    assert.deepEqual(afterNeutral,neutralLeg.path,'Neutral preset did not restore original knee topology');
    await page.locator('#modelAtelierPoseDeck summary').click();
    const curveIndex=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.findIndex(p=>p.surfaceStyle==='pinata-twisted'));
    await page.locator('#modelAtelierParts').selectOption({index:curveIndex});
    assert.equal(await page.locator('#modelAtelierSculptEditor').isVisible(),true,'Sculpt tools hidden for loft');
    await page.locator('#modelAtelierSculptTwist').fill('115');
    await page.locator('#modelAtelierSculptDepth').fill('1.25');
    await page.locator('#modelAtelierSculptApply').click();
    const altered=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.find(p=>p.surfaceStyle==='pinata-twisted'));
    assert.equal(altered.twistDegrees,115,'Twist editor did not persist to project');
    assert.equal(altered.depthScale,1.25,'Depth editor did not persist to project');
    await page.locator('#modelAtelierSculptSmooth').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,811);
    // Exercise each newly exposed sculpt tool through the actual desktop/touch inspector.
    const beforeMirror=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.find(p=>p.surfaceStyle==='pinata-twisted'));
    await page.locator('#modelAtelierSculptMirror').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,812,'Mirror did not add a native editable loft');
    const mirrored=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.at(-1));
    assert.equal(mirrored.kind,'loft');
    assert(await number(1)>originalTris,'Mirrored loft did not update actual triangle count');
    assert.deepEqual(mirrored.path,beforeMirror.path.map(([x,y,z])=>[-x,y,z]),'Mirror failed to invert control-point X coordinates');
    assert.equal(mirrored.twistDegrees,-beforeMirror.twistDegrees,'Mirror failed to invert axial twist');
    await page.locator('#modelAtelierUndo').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,811);

    await page.locator('#modelAtelierParts').selectOption({index:curveIndex});
    await page.locator('#modelAtelierSculptFringe').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,825,'Paper fringe was not generated');
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.filter(p=>p.name.startsWith('Generated paper fringe ')).length),14);
    await page.locator('#modelAtelierUndo').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,811);

    await page.locator('#modelAtelierParts').selectOption({index:curveIndex});
    await page.locator('#modelAtelierSculptLimb').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,812,'Smooth anatomical loft action failed');
    assert.equal(await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene().project.modelAtelier.parts.at(-1).surfaceStyle),'anatomy-smooth');
    await page.locator('#modelAtelierUndo').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,811);
    await page.locator('#modelAtelierParts').selectOption({index:5});
    await page.locator('#modelAtelierColor').fill('#6dd5ff');
    await page.locator('#modelAtelierColor').dispatchEvent('change');
    await page.locator('#modelAtelierposition0').fill('1.4');
    await page.locator('#modelAtelierposition0').dispatchEvent('change');
    await page.locator('#modelAtelierDuplicate').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,812);
    await page.locator('#modelAtelierUndo').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,811);
    await page.locator('#modelAtelierRedo').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,812);
    const nativeSave=await page.evaluate(()=>window.SWYRL_ENGINE_AGENT.inspectScene());
    assert.equal(nativeSave.project.kind,'model-atelier','Native project identity lost');
    assert.equal(nativeSave.project.modelAtelier.parts.length,812,'Native save lost edited meshes');
    await page.locator('#modelAtelierClose').click();
    await page.evaluate(data=>window.SWYRL_ENGINE_AGENT.loadScene(data),nativeSave);
    await page.locator('#modelAtelierReopen').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,812,'Native load lost edited meshes');
    assert.equal(await page.locator('#modelAtelierPoseSelect option[value="saved:Showcase back"]').count(),1,'Saved pose frame lost after native project load');
    await page.locator('#modelAtelierParts').selectOption({index:811});
    await page.locator('#modelAtelierDelete').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).count,811);
    await page.locator('#modelAtelierOBJ').click();
    await page.locator('#modelAtelierExport').click();
    await page.locator('#modelAtelierResetCamera').click();
    await page.screenshot({path:resolve('model-atelier-acceptance',mode.name+'.png')});
    await page.locator('#modelAtelierClose').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).open,false);
    await page.locator('#modelAtelierReopen').click();
    assert.equal((await page.evaluate(()=>window.SWYRL_ENGINE_MODEL_ATELIER.status())).open,true);
    assert.equal(faults.length,0,'JavaScript runtime errors: '+JSON.stringify(faults));
    console.log('MODEL_ATELIER_CASE_PASS '+mode.name+' registered-native-starter');
    console.log('MODEL_ATELIER_CASE_PASS '+mode.name+' 3d-viewport-and-811-meshes');
    console.log('MODEL_ATELIER_CASE_PASS '+mode.name+' color-position-duplicate-history-delete');
    console.log('MODEL_ATELIER_CASE_PASS '+mode.name+' export-reopen');
    await context.close();
  }
  console.log('MODEL_ATELIER_ALL_VIEWPORTS_PASS');
}finally{await browser.close();}
