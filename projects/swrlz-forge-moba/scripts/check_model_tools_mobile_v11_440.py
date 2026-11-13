#!/usr/bin/env python3
"""Native Model Studio mobile tool audit using guest fixtures and real UI.

Shares transport and math helpers with the v430 harness. No modeling operation
is executed through evaluate; evaluate reads source/history/UI state only.
Android-sized Chromium emulation is not physical Android or Quest acceptance.
The report distinguishes functional cases, catalog navigation and untested tools.
"""
import asyncio, copy, hashlib, importlib.util, json, os, re, traceback
from pathlib import Path
from playwright.async_api import async_playwright
SPEC=importlib.util.spec_from_file_location('model_browser430',Path(__file__).with_name('check_model_studio_v11_430.py'))
H=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(H)
HTML,OUT,SHA,ARGS=H.HTML,H.OUT,H.SHA,H.ARGS
TEXT=HTML.read_text();VERSION=re.search(r"window.SWRLZ_FORGE_BUILD=\{version:'([^']+)'",TEXT).group(1)
assert VERSION in ('v11.437','v11.440'),VERSION
CASE_DIR=OUT/'android-tools';CASE_DIR.mkdir(exist_ok=True)
async def tap_visible(locator):
 n=await H.first_visible(locator);await n.scroll_into_view_if_needed();await n.tap()
H.click_visible=tap_visible

def part(kind='box',name='Practice cube'):
 return {'id':'mobile438-seed','name':name,'kind':kind,'position':[0,1.1,0],'rotation':[0,0,0],'scale':[.6,.6,.6],'color':'#77c6cf','material':'matte','group':'Practice'}
def plane():
 p=part('topologyMesh','Practice planar flap');p['topologyMesh']={'positions':[-.5,0,-.5,.5,0,-.5,.5,0,.5,-.5,0,.5],'uvs':[0,0,1,0,1,1,0,1],'indices':[0,2,1,0,3,2]};return p

def same_parts(a,b):return a['parts']==b['parts']
async def field(page,suffix,value):
 n=page.locator('#atelierContextProxy_modelAtelier'+suffix)
 if await n.evaluate('(n)=>n.tagName')=='SELECT':await n.select_option(str(value))
 else:await n.fill(str(value));await n.dispatch_event('change')
async def selected_part(page):
 s=await H.workshop(page);return next(p for p in (await H.source(page))['parts'] if p['id']==s['selection']['partId'])
async def show_inspector(page,show=True):
 n=page.get_by_role('button',name='Show inspector' if show else 'Hide inspector',exact=True)
 if await n.count() and await n.is_visible():await tap_visible(n)
async def viewport_points(page,points,p):
 state=await H.camera(page);rect=await page.locator('#modelAtelierViewport > canvas').bounding_box();assert rect
 ndc=[H.project_world(H.transform_xyz(v,p),state) for v in points]
 candidates=[{'x':rect['x']+(v[0]+1)*rect['width']/2,'y':rect['y']+(1-v[1])*rect['height']/2} for v in ndc]
 for v in candidates:assert await page.evaluate('(p)=>document.elementFromPoint(p.x,p.y)?.tagName==="CANVAS"',v),('Viewport target covered',v)
 return candidates
async def touch_points(page,points,p):
 await H.view_ui(page,'top');await H.projection_ui(page,'orthographic');await H.close_views(page);await show_inspector(page,False);await tap_visible(page.locator('#modelAtelierFrameSelected'));await page.wait_for_timeout(180)
 targets=await viewport_points(page,points,p)
 for q in targets:await page.touchscreen.tap(q['x'],q['y']);await page.wait_for_timeout(90)
 await show_inspector(page,True)

async def main():
 result={'version':VERSION,'sourceSha256':SHA,'runtime':'Chromium Android 390x844 touch profile / actual native editor','physicalAndroidMeasured':False,'physicalQuestMeasured':False,'accountWrites':False,'checks':[],'catalog':{},'pageErrors':[],'untested':['Physical Android browser, soft-keyboard and device comfort','Physical Meta Quest controllers and compositor (separate VR checks)','Authenticated cloud save/account session','Every numeric parameter combination and every procedural or rigged project','Advanced lasso boolean/paint/curve/morph combinations','UV paint file picker and every texture/export format','Authored animation rig playback and interpolation; blank-fixture controls only','Continuous flat/mobile sculpt strokes: native flat editor exposes picked/numeric stamps, not the VR live-stroke interaction']}
 def save(): (CASE_DIR/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path=ARGS.chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--enable-webgl','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--disk-cache-size=1','--media-cache-size=1'])
  ctx=await browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1,accept_downloads=True)
  for origin in (H.FORGE,H.CHAT,H.CDN):await ctx.route(origin+'/**',H.transport)
  page=await ctx.new_page();page.set_default_timeout(12000)
  page.on('pageerror',lambda error:result['pageErrors'].append(str(error)))
  async def dialog(d):await d.accept('Mobile practice copy' if d.type=='prompt' else None)
  page.on('dialog',lambda d:asyncio.create_task(dialog(d)))
  serial=0
  async def reset(parts=None,assemblies=None):
   nonlocal serial
   serial+=1;data=H.fixture();parts=copy.deepcopy(parts or [part()]);parts[0]['id']='mobile438-'+str(serial);data['project']['modelAtelier']['parts']=parts;data['project']['name']=data['project']['projectName']='Mobile tool audit '+str(serial);data['project']['canonicalId']='mobile438-fixture-'+str(serial)
   if assemblies is not None:data['project']['modelAtelier']['assemblies']=copy.deepcopy(assemblies)
   f=CASE_DIR/'practice.swyrl.json';f.write_text(json.dumps(data));await page.locator('#fileInput').set_input_files(str(f));await page.wait_for_function('(id)=>window.SWYRL_ENGINE_AGENT.inspectScene().project?.modelAtelier?.parts?.[0]?.id===id',arg=parts[0]['id']);await page.locator('#modelAtelierPanel:not([hidden])').wait_for();await show_inspector(page,True);await H.choose_category(page,'Meshes','Select & organize');await page.locator('#atelierContextProxy_modelAtelierParts').select_option(parts[0]['id']);await tap_visible(page.locator('[data-component-mode="mesh"]'));return parts[0]['id']
  async def editable():
   await reset();await H.manual(page);await H.native_action(page,'Make mesh editable');p=await selected_part(page);await H.projection_ui(page,'orthographic');await H.click_top_face(page,p);await H.native_action(page,'Select flat region');assert len((await H.workshop(page))['selection']['faceIds'])==2;return p
  async def case(name,fn):
   if os.environ.get('MODEL_MOBILE_CASES') and not any(t.lower() in name.lower() for t in os.environ['MODEL_MOBILE_CASES'].split(',')):return
   print('MOBILE438 STAGE '+name,flush=True);row={'name':name,'status':'RUNNING'};result['checks'].append(row);save()
   try:
    details=await fn();row.update(status='PASS',details=details);print('MOBILE438 PASS '+name,flush=True)
   except Exception as e:
    row.update(status='FAIL',error=str(e),trace=traceback.format_exc(limit=3));print('MOBILE438 FAIL '+name+': '+str(e),flush=True)
    try:row['workshop']=await H.workshop(page);row['modelSource']=await H.source(page);row['context']=await page.evaluate('()=>window.SWYRL_E_CONTEXT.current()');await page.screenshot(path=str(CASE_DIR/('failure-'+str(len(result['checks']))+'.png')))
    except Exception:pass
   save()
  try:
   await page.goto(H.FORGE+'/modeler.html',wait_until='domcontentloaded',timeout=90000);await page.wait_for_function('(v)=>window.SWRLZ_FORGE_BUILD?.version===v&&!!window.SWYRL_ENGINE_MODEL_WORKSHOP&&!!window.SWYRL_ENGINE_MODEL_CAMERA',arg=VERSION,timeout=90000)
   notes=page.locator('#seReleaseNotesDialog[open]');
   if await notes.count():await notes.locator('button').last.tap()
   await reset()
   async def catalog():
    cats=['Meshes','Sculpt','Lasso','Topology','Face','Appearance','Motion','References']
    for cat in cats:
     await H.choose_category(page,cat);groups=await page.evaluate('()=>window.SWYRL_E_CONTEXT.groups()');rows=[]
     for op in groups.get(cat,[]):
      await H.choose_category(page,cat,op);controls=await page.locator('#atelierContextFields').evaluate('(f)=>[...f.querySelectorAll("button,input,select,textarea")].map(n=>({id:n.id,label:n.getAttribute("aria-label")||n.closest(".atelier-context-field")?.textContent?.trim().slice(0,130)||n.textContent?.trim(),disabled:n.disabled,visible:!!n.getClientRects().length}))');rows.append({'operation':op,'controls':controls})
     result['catalog'][cat]=rows;save()
    return {'categories':len(result['catalog']),'modes':sum(len(v) for v in result['catalog'].values()),'coverage':'navigation/control discoverability only; not every action executed'}
   await case('Enumerate actual contextual modes and controls',catalog)
   async def primitives():
    await reset();base=await H.source(page)
    for kind in ('box','sphere','cylinder','cone'):
     await H.choose_category(page,'Meshes','Select & organize');await field(page,'PrimitiveKind',kind);await H.native_action(page,'Add '+('cube' if kind=='box' else kind));source=await H.source(page);p=await selected_part(page);assert len(source['parts'])==2 and p['kind']==kind;await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base)
    return 'All four native primitives create through UI and Undo restores exact source'
   await case('Cube sphere cylinder cone creation and Undo',primitives)
   async def duplicates():
    await reset();base=await H.source(page);await H.native_action(page,'Duplicate');copied=await H.source(page);assert len(copied['parts'])==2 and len({p['id'] for p in copied['parts']})==2;await H.native_action(page,'Delete');assert len((await H.source(page))['parts'])==1;await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),copied);await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base);return 'Native duplicate/delete and exact Undo'
   await case('Duplicate delete and source-restoring Undo',duplicates)
   async def stale_preview():
    await editable();base=await H.source(page);hist=await H.history(page);await H.set_operation(page,'extrude',.15);await H.native_action(page,'Preview geometry');assert (await H.workshop(page))['preview']['active'];guide=page.locator('#se430ManualLesson');
    if not await guide.evaluate('(n)=>n.open'):await tap_visible(guide.locator('summary'))
    await tap_visible(page.locator('[data-se430-step="inset"]'));state=await H.workshop(page);assert not state['preview']['active'],'Make a rim relabeled the old Extrude preview instead of canceling it';assert same_parts(await H.source(page),base) and await H.history(page)==hist;return 'Actual lesson button cancels prior Extrude preview without source/history writes'
   await case('Guide operation switch cancels old Extrude preview',stale_preview)
   async def manual_edits():
    await editable();base=await H.source(page)
    for op,amount in [('deleteFaces',None),('subdivide',.25)]:
     # Undo retains selection on current native mesh; reselect its top region.
     await H.manual(page);p=await selected_part(page);await tap_visible(page.locator('[data-component-mode="face"]'));await H.click_top_face(page,p);await H.native_action(page,'Select flat region');await H.set_operation(page,op,amount);hist=await H.history(page);await H.native_action(page,'Preview geometry');preview=await H.workshop(page);assert preview['preview']['active'] and same_parts(await H.source(page),base);await H.native_action(page,'Apply geometry');changed=await H.source(page);before=len(base['parts'][0]['topologyMesh']['indices']);after=len(changed['parts'][0]['topologyMesh']['indices']);assert (after<before if op=='deleteFaces' else after>before),(op,before,after);assert (await H.history(page))['undo']==hist['undo']+1;await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base)
    return 'Delete faces and triangle refinement Preview/Apply perform real topology edits, each one Undo step'
   await case('Manual Delete faces Subdivide Apply and Undo',manual_edits)
   async def solidify():
    await reset([plane()]);await H.manual(page);await tap_visible(page.locator('[data-component-mode="face"]'));await H.click_top_face(page,await selected_part(page));await H.native_action(page,'Select flat region');base=await H.source(page);hist=await H.history(page);await H.set_operation(page,'solidify',.1);await H.native_action(page,'Preview geometry');assert (await H.workshop(page))['preview']['active'] and same_parts(await H.source(page),base);await H.native_action(page,'Apply geometry');p=await selected_part(page);assert len(p['topologyMesh']['positions'])==24 and len(p['topologyMesh']['indices'])==36;assert abs(H.signed_volume(p['topologyMesh']))>.05;assert (await H.history(page))['undo']==hist['undo']+1;await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base);return 'Actual open flap gains two layers/rim and closed volume; Undo restores it'
   await case('Manual planar Solidify preview Apply Undo',solidify)
   async def components():
    findings=[]
    for mode,points in [('vertex',[[-.5,.5,-.5],[.5,.5,-.5],[.5,.5,.5],[-.5,.5,.5]]),('edge',[[0,.5,-.5],[.5,.5,0],[0,.5,.5],[-.5,.5,0]]),('face',[[.18,.5,.1]])]:
     await editable();await H.manual(page);base=await H.source(page);p=await selected_part(page);await tap_visible(page.locator('[data-component-mode="'+mode+'"]'));await touch_points(page,[points[0]],p);state=await H.workshop(page);assert state['selection']['mode']==mode and state['selection']['ids'],(mode,state);options=page.locator('.se430-component-options');
     if not await options.evaluate('(n)=>n.open'):await tap_visible(options.locator('summary'))
     await tap_visible(page.locator('[data-component-nudge="1"]'));changed=await H.source(page);assert not same_parts(changed,base) and changed['parts'][0].get('sculptVertexEdits');await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base);findings.append(mode)
    return {'selectedAndNudgedWithUndo':findings}
   await case('Vertex edge face touch selection and component nudge Undo',components)
   async def split_edge():
    await editable();base=await H.source(page);await H.choose_category(page,'Topology','Edge, vertex & face');await field(page,'TopologyFace',0);await field(page,'TopologyEdge',0);await H.native_action(page,'split');changed=await H.source(page);assert len(changed['parts'][0]['topologyMesh']['positions'])>len(base['parts'][0]['topologyMesh']['positions']);await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base);return 'Original numeric edge splitter adds native vertices/faces and Undo restores geometry'
   await case('Native advanced Split edge and Undo',split_edge)
   async def fill_boundary():
    await editable();await H.set_operation(page,'deleteFaces');await H.native_action(page,'Preview geometry');await H.native_action(page,'Apply geometry');base=await H.source(page);data=base['parts'][0]['topologyMesh'];edges={}
    for i in range(0,len(data['indices']),3):
     tri=data['indices'][i:i+3]
     for j in range(3):
      pair=tuple(sorted((tri[j],tri[(j+1)%3])));edges[pair]=edges.get(pair,0)+1
    vertex=next(a for (a,b),count in edges.items() if count==1)
    await H.choose_category(page,'Topology','Repair boundary');await field(page,'BoundaryCapVertex',vertex);await H.native_action(page,'preview');await H.native_action(page,'Fill one safe boundary loop');changed=await H.source(page);assert len(changed['parts'][0]['topologyMesh']['indices'])>len(data['indices']);await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base);return 'Original boundary-cap Preview/Apply closes selected cube opening with native triangles'
   await case('Native Fill boundary Preview Apply Undo',fill_boundary)
   async def uv():
    await reset([plane()]);base=await H.source(page)
    button=page.locator('#se355UVEditorOpen')
    if not await button.is_visible():
     menu=page.locator('#seAtelierExportMenu')
     if not await menu.evaluate('(n)=>n.open'):await tap_visible(menu.locator(':scope > summary'))
    await tap_visible(button);await page.locator('#se355UVPopup:not([hidden])').wait_for()
    control=page.locator('#modelAtelierUVPlane')
    for _ in range(4):
     if await control.is_visible():break
     closed=control.locator('xpath=ancestor::details[not(@open)]')
     if not await closed.count():break
     await tap_visible(closed.first.locator(':scope > summary'))
    await control.select_option('XZ');await page.locator('#modelAtelierUVMirror').check();await tap_visible(page.locator('#modelAtelierUVPreview'));assert same_parts(await H.source(page),base)
    await tap_visible(page.locator('#modelAtelierUVApply'));changed=await H.source(page);a,b=base['parts'][0]['topologyMesh'],changed['parts'][0]['topologyMesh'];assert a['positions']==b['positions'] and a['indices']==b['indices'] and a['uvs']!=b['uvs']
    await tap_visible(page.locator('#se355UVClose'));await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base);return 'Native UV Editor popup previews/reprojects a supported open planar mesh; Apply changes UVs only and Undo restores them'
   await case('Native planar UV Preview Apply Undo',uv)
   async def brushes():
    await reset([part('sphere','Practice sculpt sphere')]);base=await H.source(page);steps=[]
    for mode in ('extrude','smooth','flatten','inflate','pinch','translate'):
     await H.choose_category(page,'Sculpt','Brush & falloff');await field(page,'SculptBrushMode',mode);await field(page,'SculptBrushRadius',.8);await field(page,'SculptBrushAmount',.1);await H.native_action(page,'^Run.*apply|^apply');source=await H.source(page);stroke=source['parts'][0].get('sculptBrushes',[]);assert len(stroke)==1 and stroke[0]['operation']==('push' if mode=='extrude' else mode),(mode,stroke);await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base);steps.append(mode)
    return {'nativeStampApplyAndUndo':steps,'continuousFlatStroke':'Not exposed by this native stamp workflow; no unsupported claim'}
   await case('All six native mobile sculpt stamps and Undo',brushes)
   async def lasso():
    await reset();base=await H.source(page);await H.choose_category(page,'Lasso','Create region');await H.native_action(page,'Start polygon lasso');await touch_points(page,[[-.2,.5,-.2],[.2,.5,-.2],[.2,.5,.2],[-.2,.5,.2]],await selected_part(page));await H.native_action(page,'Finish polygon');source=await H.source(page);regions=source['parts'][0].get('sculptLassos',[]);assert len(regions)==1 and len(regions[0]['pins'])>=3;await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base);return 'Surface taps construct a real saved lasso region; native Undo removes only the region'
   await case('Actual mobile surface lasso and Undo',lasso)
   async def material():
    await reset();base=await H.source(page);await H.choose_category(page,'Meshes','Material & shape');await field(page,'Color','#55aade');assert (await selected_part(page))['color']=='#55aade';await field(page,'Material','gloss');assert (await selected_part(page))['material']=='gloss';await H.undo_redo(page,'Undo');assert (await selected_part(page))['material']==base['parts'][0]['material'];await H.undo_redo(page,'Undo');assert same_parts(await H.source(page),base);return 'Real source color/material updates and two exact native Undo steps'
   await case('Material color and source-restoring Undo',material)
   async def motion():
    assemblies={'schema':'swyrl-assemblies-v1','sockets':[],'components':[{'id':'mobile438-motion','group':'Practice','name':'Keyed practice cube','state':'free','pivot':[0,1.1,0],'offset':[0,0,0],'rotation':[0,0,0],'amplitude':0,'speed':1,'scale':1,'keys':[{'time':0,'offset':[0,0,0],'rotation':[0,0,0],'scale':1},{'time':1,'offset':[.4,.1,0],'rotation':[0,.3,0],'scale':1.1}]}],'time':0,'duration':2}
    await reset(assemblies=assemblies);base=await H.source(page);await H.choose_category(page,'Meshes','Additional meshes controls');await field(page,'AssemblyComponent','mobile438-motion')
    await H.native_action(page,'Play transform');await page.wait_for_function('()=>document.querySelector("#modelAtelierAssemblyPlay").textContent.includes("Pause")');await page.wait_for_timeout(180)
    await H.native_action(page,'Pause');assert 'Play transform' in await page.locator('#modelAtelierAssemblyPlay').text_content();await H.native_action(page,'^Stop.*rest$');assert same_parts(await H.source(page),base);assert (await H.source(page))['assemblies']['components'][0]['keys']==assemblies['components'][0]['keys'];return {'keyedAssemblyPlaybackControls':['play','pause','stop'],'sourceGeometryAndKeysPreserved':True,'skeletalRigPlayback':'Not tested by this assembly fixture'}
   await case('Motion playback controls without authored geometry edits',motion)
   layout=await page.evaluate('()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,panelWidth:document.querySelector("#modelAtelierPanel").clientWidth,panelScrollWidth:document.querySelector("#modelAtelierPanel").scrollWidth})');result['layout']=layout;result['status']='PASS' if all(c['status']=='PASS' for c in result['checks']) and not result['pageErrors'] else 'FAIL';await page.screenshot(path=str(CASE_DIR/'final-layout.png'));save();print(json.dumps({'status':result['status'],'version':VERSION,'sha256':SHA,'passed':sum(c['status']=='PASS' for c in result['checks']),'failed':[c['name'] for c in result['checks'] if c['status']=='FAIL'],'output':str(CASE_DIR)},indent=2),flush=True)
  finally:
   save();await ctx.close();await browser.close()
 if result['status']!='PASS':raise SystemExit(1)

if __name__=='__main__':asyncio.run(main())
