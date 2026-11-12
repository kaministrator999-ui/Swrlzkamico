/* SE430_MODEL_BEGINNER_UI_START */
// One educational layer on the existing native inspector. It never owns a
// document or geometry; all commands delegate to the Model Studio bridge.
const se430BeginnerState={panel:null,help:null,canvas:null,context:null,tool:'select',study:null,lastFrame:-1,observer:null,scheduled:false,lastState:'',installed:false};
const se430BeginnerOps=['inset','extrude','deleteFaces','solidify','splitEdge','subdivide','fillHole','repairNormals'];
const se430BeginnerTeaching=()=>window.SWYRL_MODEL_TEACHING;
const se430BeginnerAPI=()=>window.SWYRL_ENGINE_MODEL_WORKSHOP||ModelAtelier?.workshop;
function se430BeginnerWrite(node,value){if(node&&node.textContent!==String(value))node.textContent=String(value);}
function se430BeginnerTool(){
 const s=se430BeginnerState,current=window.SWYRL_E_CONTEXT?.current?.()||{},op=document.getElementById('modelAtelierWorkshopOperation');
 if(current.group==='Topology'&&/manual mesh/i.test(current.operation||''))return op?.value||'inset';
 const text=(current.group+' '+current.operation).toLowerCase();
 if(/extrud/.test(text))return 'extrude';if(/boundary/.test(text))return 'fillHole';if(/audit/.test(text))return 'repairNormals';
 if(/refinement|density/.test(text))return 'subdivide';if(/reference/.test(text))return 'reference';if(/sculpt|brush/.test(text))return 'sculpt';
 if(/group|assembl/.test(text))return 'group';if(/transform/.test(text))return 'move';if(/select|organize|mesh/.test(text))return 'primitive';return 'select';
}
function se430BeginnerQueue(){
 const s=se430BeginnerState;if(s.scheduled)return;s.scheduled=true;
 queueMicrotask(()=>{s.scheduled=false;se430BeginnerRefresh();});
}
function se430BeginnerResult(result){
 if(result?.ok===false){const note=se430BeginnerState.panel?.querySelector('#se430WorkshopFeedback');se430BeginnerWrite(note,result.reason||result.error||'This action is unavailable.');}
 se430BeginnerRefresh();return result;
}
function se430BeginnerAmount(operation){
 return {inset:{min:.03,max:.8,step:.05,value:.2,label:'Inset fraction · 0.2 = 20%'},extrude:{min:-4,max:4,step:.05,value:.15,label:'Depth · negative goes inward'},solidify:{min:.005,max:4,step:.025,value:.1,label:'Thickness · local units'},subdivide:{min:.025,max:4,step:.05,value:.25,label:'Target edge length · local units'}}[operation]||null;
}
function se430BeginnerSetOperation(id,amount){
 const p=se430BeginnerState.panel,select=p?.querySelector('#modelAtelierWorkshopOperation'),input=p?.querySelector('#modelAtelierWorkshopAmount');
 if(!select||!se430BeginnerOps.includes(id))return;
 select.value=id;se430BeginnerState.study=null;select.dispatchEvent(new Event('change',{bubbles:true}));
 if(amount!==undefined&&input){input.value=amount;input.dispatchEvent(new Event('change',{bubbles:true}));}se430BeginnerRefresh();
}
function se430BeginnerNavigate(id){
 const api=window.SWYRL_E_UNIFIED_TOOLS;
 if(id==='primitive'){api?.select?.('Meshes','Select & organize');const select=document.getElementById('modelAtelierPrimitiveKind');if(select){select.value='box';select.dispatchEvent(new Event('change',{bubbles:true}));}}
 else{api?.select?.('Topology','Manual mesh modeling');if(id==='face'){se430BeginnerAPI()?.setComponentMode?.('face');window.SWYRL_ENGINE_MODEL_CAMERA?.setView?.('top');}else if(id!=='convert')se430BeginnerSetOperation(id,id==='extrude'?-.35:undefined);}
 se430BeginnerState.study=null;se430BeginnerQueue();
}
function se430BeginnerArrangeHeader(){
 const p=se430BeginnerState.panel,actions=p?.querySelector('.atelier-actions'),box=p?.querySelector('#seAtelierExportMenu .se-export-options');
 if(!actions||!box)return;
 const summary=box.parentElement?.querySelector(':scope>summary');
 if(summary){if(summary.textContent!=='File ▾')summary.textContent='File ▾';summary.setAttribute('aria-label','Save, clone, import and export options');summary.title='Save, clone, import and export options';}
 // Save/Clone and account buttons may be installed by the existing project
 // modules after this inspector. Move their original nodes, including nested
 // wrapper children, once they arrive; their native handlers remain intact.
 for(const b of actions.querySelectorAll(':scope>button,:scope>[data-se371-controls]>button')){
  if(box.contains(b)||['modelAtelierClose','se340EnterModelVR','se185AtelierTopToggle'].includes(b.id))continue;
  if(/^(?:save project|save model)$/i.test(b.textContent.trim()))continue;
  box.append(b);
 }
 const vr=p.querySelector('#se340EnterModelVR');
 if(vr&&vr.parentNode!==actions){const close=actions.querySelector('#modelAtelierClose');if(close)close.before(vr);else actions.append(vr);}
 if(vr&&vr.textContent!=='VR'){vr.textContent='VR';vr.setAttribute('aria-label','Enter Model Studio VR');}
}
function se430BeginnerSyncProxies(){
 const p=se430BeginnerState.panel,fields=p?.querySelector('#atelierContextFields');if(!fields)return;
 for(const row of fields.querySelectorAll('[data-se430-native]')){
  const native=p.querySelector('#'+row.dataset.se430Native),proxy=row.querySelector('button,input,select,textarea');if(!native||!proxy)continue;
  proxy.disabled=!!native.disabled||!!native.closest('[hidden]');
  proxy.title=native.title||'';
  if(native.getAttribute('aria-description'))proxy.setAttribute('aria-description',native.getAttribute('aria-description'));
  if(native.tagName==='BUTTON'){
   const label=native.textContent.replace(/\s+/g,' ').trim(),wanted='Run · '+label;
   // SVG icons carry no text. Compare text before replacing a changed native
   // label, then let the normal icon decorator attach the matching icon once.
   if(proxy.textContent.trim()!==wanted){proxy.textContent=wanted;delete proxy.dataset.se430Icon;}
   proxy.setAttribute('aria-label',label);
   for(const attr of ['aria-pressed','aria-expanded']){const value=native.getAttribute(attr);if(value!==null)proxy.setAttribute(attr,value);else proxy.removeAttribute(attr);}
  }else{
   for(const attr of ['min','max','step'])if(native.hasAttribute(attr))proxy.setAttribute(attr,native.getAttribute(attr));
   if(native.tagName==='SELECT'){
    const signature=n=>[...n.options].map(o=>[o.value,o.textContent,o.disabled]);
    if(JSON.stringify(signature(native))!==JSON.stringify(signature(proxy))){proxy.replaceChildren(...[...native.options].map(o=>o.cloneNode(true)));}
   }
   if(document.activeElement!==proxy){if(proxy.type==='checkbox')proxy.checked=native.checked;else if(proxy.value!==native.value)proxy.value=native.value;}
  }
 }
}
function se430BeginnerInstall(panel){
 if(!panel||panel.dataset.se430Beginner)return;const inspector=panel.querySelector('.atelier-inspector'),context=panel.querySelector('#atelierContextWorkbench');
 if(!inspector||!context)return;panel.dataset.se430Beginner='1';const s=se430BeginnerState;s.panel=panel;s.installed=true;
 const native=document.createElement('fieldset');native.id='modelAtelierTopologyWorkshop';native.className='se430-native-workshop';
 native.innerHTML='<legend>Manual mesh modeling</legend><p>These commands edit your selected native mesh. A preview never commits geometry until Apply.</p>'+
  '<label>Operation<select id="modelAtelierWorkshopOperation" aria-label="Manual mesh operation"></select></label>'+
  '<label><span id="se430AmountLabel">Inset fraction · 0.2 = 20%</span><input id="modelAtelierWorkshopAmount" type="number" min=".03" max=".8" step=".05" value=".2" aria-label="Operation amount"></label>'+
  '<div class="se430-native-actions"><button type="button" id="modelAtelierWorkshopConvert">Make mesh editable</button><button type="button" id="modelAtelierWorkshopSelectRegion">Select flat region</button><button type="button" id="modelAtelierWorkshopPreview">Preview geometry</button><button type="button" id="modelAtelierWorkshopApply">Apply geometry</button><button type="button" id="modelAtelierWorkshopCancel">Cancel preview</button></div>'+
  '<output id="se430WorkshopFeedback" role="status" aria-live="polite"></output>';
 inspector.append(native);
 const operation=native.querySelector('#modelAtelierWorkshopOperation');
 for(const id of se430BeginnerOps){const o=document.createElement('option');o.value=id;o.textContent=se430BeginnerTeaching()?.get(id)?.name||id;operation.append(o);}
 operation.addEventListener('change',()=>{
  const config=se430BeginnerAmount(operation.value),input=native.querySelector('#modelAtelierWorkshopAmount');
  if(config){for(const key of ['min','max','step'])input[key]=config[key];input.value=config.value;}s.study=null;se430BeginnerRefresh();
 });
 const amountChanged=()=>{const api=se430BeginnerAPI();if(api?.inspect().preview.active){api.cancel('Amount changed. Preview again to review the new geometry before Apply.');se430BeginnerRefresh();}};
 for(const event of ['input','change'])native.querySelector('#modelAtelierWorkshopAmount').addEventListener(event,amountChanged);
 native.querySelector('#modelAtelierWorkshopConvert').addEventListener('click',()=>se430BeginnerResult(se430BeginnerAPI()?.convert()));
 native.querySelector('#modelAtelierWorkshopSelectRegion').addEventListener('click',()=>{const state=se430BeginnerAPI()?.inspect();se430BeginnerResult(se430BeginnerAPI()?.selectRegion(state?.selection.faceIds[0],state?.selection.partId));});
 native.querySelector('#modelAtelierWorkshopPreview').addEventListener('click',()=>{const amount=Number(native.querySelector('#modelAtelierWorkshopAmount').value);se430BeginnerResult(se430BeginnerAPI()?.preview(operation.value,se430BeginnerAmount(operation.value)?{amount}:{}));});
 native.querySelector('#modelAtelierWorkshopApply').addEventListener('click',()=>se430BeginnerResult(se430BeginnerAPI()?.apply()));
 native.querySelector('#modelAtelierWorkshopCancel').addEventListener('click',()=>se430BeginnerResult(se430BeginnerAPI()?.cancel()));
 // Keep the original Add button and its position in the native catalog. The
 // selected primitive is created through the same one-checkpoint native API.
 const add=panel.querySelector('#modelAtelierAdd');
 if(add&&!panel.querySelector('#modelAtelierPrimitiveKind')){
  const kind=document.createElement('select');kind.id='modelAtelierPrimitiveKind';kind.setAttribute('aria-label','New primitive shape');
  for(const [value,label]of [['box','Cube'],['sphere','Sphere'],['cylinder','Cylinder'],['cone','Cone']]){const o=document.createElement('option');o.value=value;o.textContent=label;kind.append(o);}
  add.before(kind);const label=()=>{add.textContent='Add '+kind.options[kind.selectedIndex].text.toLowerCase();add.setAttribute('aria-label',add.textContent);};kind.addEventListener('change',label);label();
  add.addEventListener('click',event=>{event.preventDefault();event.stopImmediatePropagation();const result=se430BeginnerResult(se430BeginnerAPI()?.create(kind.value));if(result?.ok)window.SWYRL_ENGINE_MODEL_CAMERA?.frame?.('selected');},true);
 }
 const strip=document.createElement('section');strip.id='se430SelectionContext';strip.className='se430-selection-context';strip.setAttribute('aria-label','Current selection and component modes');
 strip.innerHTML='<output id="se430SelectionSummary" role="status" aria-live="polite">Object mode · choose a mesh</output><p id="se430SelectionHint"></p><button type="button" id="se430ContextTools">Object tools</button>';
 strip.querySelector('#se430ContextTools').addEventListener('click',()=>{
  const state=se430BeginnerAPI()?.inspect(),api=window.SWYRL_E_UNIFIED_TOOLS;if(!state||!api)return;
  const mode=state.selection.mode;
  if(mode==='face'||mode==='edge'){
   api.select?.('Topology','Manual mesh modeling');
   if(!state.preview.active){const current=panel.querySelector('#modelAtelierWorkshopOperation')?.value;if(mode==='edge')se430BeginnerSetOperation('splitEdge');else if(['splitEdge','fillHole'].includes(current))se430BeginnerSetOperation('inset');}
  }else if(mode==='mesh')api.select?.('Meshes',(state.selection.objectCount||0)>1?'Assemblies & selection':'Select & organize');
  se430BeginnerQueue();
 });
 const components=panel.querySelector('[data-component-controls]');if(components){
  strip.append(components);components.querySelector('[data-component-mode="mesh"]').textContent='Object';
  const tools=components.querySelector('.atelier-component-tools');
  if(tools){const options=document.createElement('details');options.className='se430-component-options';options.open=innerWidth>699;const summary=document.createElement('summary');summary.textContent='Selection options · Multi / Box / Lasso';tools.before(options);options.append(summary,tools);}
 }
 const assemblyDock=panel.querySelector('[data-atelier-groups]');if(assemblyDock&&!inspector.contains(assemblyDock))inspector.append(assemblyDock);
 // Give existing assembly controls stable catalog identities. Their original
 // dataset-based handlers and persistent native group implementation stay in
 // charge; this only makes them discoverable through the same mode inspector.
 for(const [suffix,attribute]of Object.entries({Multi:'multi',All:'all',Clear:'clear',Scope:'scope',Picker:'picker',Create:'create',Ungroup:'ungroup',Update:'update',Remove:'remove'})){
  const control=panel.querySelector('[data-group-'+attribute+']');if(control&&!control.id)control.id='modelAtelierGroup'+suffix;
 }
 const handle=inspector.querySelector('.atelier-tool-handle');if(handle)handle.after(strip);else inspector.prepend(strip);
 const right=context.querySelector('.atelier-context-right'),help=document.createElement('details');help.id='se430ToolHelp';help.className='se430-tool-help';
 help.innerHTML='<summary><span id="se430HelpIcon"></span><span id="se430HelpTitle">Learn this tool</span><span class="se430-help-toggle">Show / hide</span></summary><div class="se430-help-content"><p id="se430HelpExplanation"></p><canvas id="se430ToolDemo" width="540" height="190" role="img" aria-label="Before, during and after illustration of the selected modeling operation"></canvas><dl><dt>Selection</dt><dd id="se430HelpSelection"></dd><dt>How to enable</dt><dd id="se430HelpRequires"></dd><dt>Try it for</dt><dd id="se430HelpUse"></dd></dl><p id="se430HelpLimitation" class="se430-help-limit"></p><label class="se430-study-label">Study another tool · explanation only<select id="se430StudyTool" aria-label="Study a modeling tool"></select></label></div>';
 right?.querySelector('#atelierContextHelp')?.after(help);s.help=help;s.canvas=help.querySelector('canvas');s.context=s.canvas.getContext('2d');
 const study=help.querySelector('#se430StudyTool');for(const entry of se430BeginnerTeaching()?.list()||[]){const o=document.createElement('option');o.value=entry.id;o.textContent=entry.name+(entry.status==='incomplete'?' · incomplete':'');study.append(o);}
 study.addEventListener('change',()=>{s.study=study.value;se430BeginnerRefresh();});
 try{help.open=localStorage.getItem('swyrlz-model-visual-help-v430')==='open';}catch{}
 help.addEventListener('toggle',()=>{try{localStorage.setItem('swyrlz-model-visual-help-v430',help.open?'open':'closed');}catch{}s.lastFrame=-1;se430BeginnerTick(performance.now(),true);});
 const lesson=document.createElement('details');lesson.id='se430ManualLesson';lesson.className='se430-manual-lesson';
 lesson.innerHTML='<summary>Learn a manual workflow · cube to container</summary><p>Use your own geometry. These steps select tools and views; you preview and apply each edit yourself.</p><ol>'+[['primitive','Add a cube','Choose Cube in Meshes, then Add cube.'],['convert','Make it editable','Review UV regeneration, then Make mesh editable.'],['face','Choose the top surface','Face mode: tap the top, then Select flat region.'],['inset','Make a rim','Inset about 0.2. Preview, inspect, then Apply. Keep the new inner faces selected.'],['extrude','Create the cavity','Choose Extrude without reselecting the flat region. Push the retained inner faces inward (for example −0.35). Keep a floor; preview and Apply.']].map(([id,title,text])=>'<li><button type="button" data-se430-step="'+id+'">'+title+'</button><span>'+text+'</span></li>').join('')+'</ol><p>Undo reverses an applied step. Cancel discards only the current preview. Bevel and general loop tools remain incomplete; this workflow does not pretend to use them.</p>';
 help.after(lesson);lesson.addEventListener('click',event=>{const b=event.target.closest('[data-se430-step]');if(b)se430BeginnerNavigate(b.dataset.se430Step);});
 // Use a single bounded observer for newly rendered native-control proxies.
 // Selection changes arrive as native bridge events; no secondary render loop.
 s.observer=new MutationObserver(se430BeginnerQueue);s.observer.observe(context.querySelector('#atelierContextFields'),{childList:true,subtree:true});
 const head=panel.querySelector('.atelier-head');if(head)s.observer.observe(head,{childList:true,subtree:true});
 window.addEventListener('swrlz:model-workshop-change',se430BeginnerQueue);
 panel.addEventListener('click',event=>{if(event.target.closest('[data-component-controls],#modelAtelierToolRail,#seAtelierModes,.atelier-context-op')){s.study=null;se430BeginnerQueue();}});
 panel.addEventListener('change',event=>{if(event.target.id?.startsWith('atelierContextProxy_')||event.target.id==='modelAtelierParts')se430BeginnerQueue();});
 // Fold only secondary original buttons into the existing Export menu. Moving
 // nodes retains their authenticated/native handlers and accessible names.
 se430BeginnerArrangeHeader();
 se430BeginnerRefresh();se430BeginnerQueue();
}
function se430BeginnerDecorate(){
 const s=se430BeginnerState,p=s.panel,teaching=se430BeginnerTeaching();if(!p||!teaching)return;
 const map=text=>/inset/i.test(text)?'inset':/extrud/i.test(text)?'extrude':/thick|solidify/i.test(text)?'solidify':/subdiv|refin|density/i.test(text)?'subdivide':/split/i.test(text)?'splitEdge':/boundar|hole/i.test(text)?'fillHole':/normal|audit/i.test(text)?'repairNormals':/sculpt|brush/i.test(text)?'sculpt':/group|assembl/i.test(text)?'group':/reference/i.test(text)?'reference':/rotate/i.test(text)?'rotate':/scale/i.test(text)?'scale':/transform|move/i.test(text)?'move':/delete/i.test(text)?'deleteFaces':/select/i.test(text)?'select':'primitive';
 for(const button of p.querySelectorAll('#modelAtelierToolRail button,#seAtelierModes button,.atelier-context-op,.atelier-context-field>button')){
  if(button.dataset.se430Icon)continue;const text=button.textContent.trim();button.dataset.se430Icon=map(text);button.insertAdjacentHTML('afterbegin',teaching.iconSVG(map(text),18));
  if(!button.getAttribute('aria-label'))button.setAttribute('aria-label',text.replace(/^Run · /,''));
 }
}
function se430BeginnerRefresh(){
 const s=se430BeginnerState,p=s.panel,api=se430BeginnerAPI();if(!p||!api)return;let state;try{state=api.inspect();}catch{return;}if(!state)return;
 // The existing responsive-layout upgrade can finish in the same microtask
 // turn as initial installation. Retain these original controls in the one
 // inspector after that upgrade, rather than duplicating or polling them.
 const strip=p.querySelector('#se430SelectionContext'),components=p.querySelector('[data-component-controls]'),inspector=p.querySelector('.atelier-inspector');
 if(strip&&components&&components.parentNode!==strip)strip.append(components);
 const assemblyDock=p.querySelector('[data-atelier-groups]');if(assemblyDock&&inspector&&!inspector.contains(assemblyDock))inspector.append(assemblyDock);
 se430BeginnerArrangeHeader();
 const selection=state.selection,preview=state.preview,operation=p.querySelector('#modelAtelierWorkshopOperation'),amount=p.querySelector('#modelAtelierWorkshopAmount');if(!operation)return;
 const op=operation.value,available=state.operations?.[op],config=se430BeginnerAmount(op),title=se430BeginnerTeaching()?.get(op)?.name||op;
 const objectCount=selection.objectCount??(selection.partId?1:0),scope=p.querySelector('[data-group-scope]')?.value;
 const summary=selection.mode==='mesh'?(objectCount>1?objectCount+' objects selected · primary: '+selection.name:(selection.name||'No mesh selected'))+' · Object mode'+(objectCount>1&&scope?' · edit '+scope:''):
  (selection.name||'No mesh selected')+' · '+({face:'Face',edge:'Edge',vertex:'Vertex'}[selection.mode]||'Object')+' mode · '+selection.ids.length+' selected';
 const transform=p.querySelector('[data-mesh-mode][aria-pressed="true"]')?.dataset.meshMode,axis=p.querySelector('[data-mesh-axis][aria-pressed="true"]')?.dataset.meshAxis;
 se430BeginnerWrite(p.querySelector('#se430SelectionSummary'),summary+(transform?' · '+transform.charAt(0).toUpperCase()+transform.slice(1)+(axis?' '+axis.toUpperCase():''):''));
 if(strip)strip.dataset.mode=selection.mode;
 const modes=p.querySelector('#seAtelierModes');if(modes)modes.setAttribute('aria-label','Choose '+(window.SWYRL_E_CONTEXT?.current?.().group||'modeling')+' tool mode; swipe horizontally for more tools');
 const contextTools=p.querySelector('#se430ContextTools');if(contextTools){contextTools.hidden=selection.mode==='vertex';se430BeginnerWrite(contextTools,selection.mode==='face'?'Face tools · Inset / Extrude':selection.mode==='edge'?'Edge tools · Split':objectCount>1?'Assemblies · Group selected':'Object tools · Create / Transform');}
 se430BeginnerWrite(p.querySelector('#se430SelectionHint'),preview.active?'Preview only · Apply commits one Undo step; Cancel keeps the source.':selection.mode==='face'?'Tap faces; Select flat region collects connected coplanar triangles.':selection.mode==='edge'?'Choose one edge for midpoint Split. Add selection is available with Multi.':selection.mode==='vertex'?'Tap a point, then use the existing axis handles or numeric nudge.':'Select an object. Component modes let you shape its vertices, edges and faces.');
 operation.disabled=!!preview.active;amount.disabled=!config;
 se430BeginnerWrite(p.querySelector('#se430AmountLabel'),config?.label||'This operation has no amount parameter');
 const settings={Convert:{disabled:!!preview.active||!state.convert?.available,reason:state.convert?.reason},SelectRegion:{disabled:!!preview.active||!selection.faceIds.length,reason:selection.faceIds.length?'Expand the first selected triangle to its connected coplanar region. After Inset, keep the inner selection for Extrude; expanding again also selects the coplanar rim.':'Choose Face mode and tap a face first.'},Preview:{disabled:!available?.available,reason:available?.reason},Apply:{disabled:!preview.active,reason:preview.active?'Commit the displayed geometry as one native Undo step.':'Preview geometry before applying.'},Cancel:{disabled:!preview.active,reason:'Discard the uncommitted geometry preview.'}};
 for(const [id,setting]of Object.entries(settings)){const node=p.querySelector('#modelAtelierWorkshop'+id);node.disabled=setting.disabled;node.title=setting.reason||'';node.setAttribute('aria-description',setting.reason||'');}
 const feedback=preview.active?title+' preview · '+preview.stats.facesBefore+' → '+preview.stats.facesAfter+' triangles. Apply or Cancel.':available?.available?(state.message||available.reason):available?.reason;
 se430BeginnerWrite(p.querySelector('#se430WorkshopFeedback'),feedback||'Select a mesh to begin.');
 // Existing proxies remain the only displayed command controls in mode view.
 const fields=p.querySelector('#atelierContextFields');for(const id of ['WorkshopOperation','WorkshopAmount','WorkshopConvert','WorkshopSelectRegion','WorkshopPreview','WorkshopApply','WorkshopCancel','PrimitiveKind']){
  const native=p.querySelector('#modelAtelier'+id),proxy=p.querySelector('#atelierContextProxy_modelAtelier'+id);if(proxy&&native){proxy.disabled=native.disabled;proxy.title=native.title;for(const attr of ['min','max','step'])if(native.hasAttribute(attr))proxy.setAttribute(attr,native.getAttribute(attr));if(proxy.value!==native.value&&document.activeElement!==proxy)proxy.value=native.value;}
 }
 if(fields&&/manual mesh/i.test(window.SWYRL_E_CONTEXT?.current?.().operation||'')){
  const nativeButtons=[...p.querySelectorAll('#modelAtelierTopologyWorkshop button')];
  for(const proxy of fields.querySelectorAll('.atelier-context-field>button')){const text=proxy.textContent.replace(/^Run · /,'').trim(),native=nativeButtons.find(n=>text===n.textContent.trim());if(native){proxy.disabled=native.disabled;proxy.title=native.title;proxy.setAttribute('aria-description',native.title);}}
  let reason=fields.querySelector('#se430VisibleReason');if(!reason){reason=document.createElement('p');reason.id='se430VisibleReason';reason.setAttribute('role','status');fields.append(reason);}se430BeginnerWrite(reason,feedback||'');
 }
 const tool=s.study||se430BeginnerTool(),entry=se430BeginnerTeaching()?.get(tool);if(entry){
  const changed=s.tool!==tool;s.tool=tool;if(changed)s.lastFrame=-1;
  const icon=p.querySelector('#se430HelpIcon');if(icon?.dataset.tool!==tool){icon.innerHTML=se430BeginnerTeaching().iconSVG(tool,22);icon.dataset.tool=tool;}
  se430BeginnerWrite(p.querySelector('#se430HelpTitle'),'Learn '+entry.name);
  se430BeginnerWrite(p.querySelector('#se430HelpExplanation'),entry.explanation);
  se430BeginnerWrite(p.querySelector('#se430HelpSelection'),entry.selection);
  se430BeginnerWrite(p.querySelector('#se430HelpRequires'),entry.requires);
  se430BeginnerWrite(p.querySelector('#se430HelpUse'),entry.use);
  se430BeginnerWrite(p.querySelector('#se430HelpLimitation'),entry.status==='incomplete'?'Explanation only · incomplete in this release. '+entry.limitation:s.study?'Studying this diagram does not change the active tool or your geometry.':'');
  p.querySelector('#se430StudyTool').value=tool;
  const help=p.querySelector('#atelierContextHelp');if(help)se430BeginnerWrite(help,entry.summary);
  if(s.canvas)s.canvas.setAttribute('aria-label',entry.name+' demonstration: before, during and after. '+entry.summary);
 }
 se430BeginnerSyncProxies();se430BeginnerDecorate();se430BeginnerTick(performance.now());
}
function se430BeginnerTick(now=0,force=false){
 const s=se430BeginnerState;if(!s.panel||s.panel.hidden||!s.help?.open||!s.help.isConnected||!s.context||s.help.closest('[hidden]'))return;
 const rect=s.help.getBoundingClientRect();if(rect.width<=0||rect.height<=0||rect.bottom<0||rect.top>innerHeight||rect.right<0||rect.left>innerWidth)return;
 const reduced=window.matchMedia?.('(prefers-reduced-motion: reduce)').matches,frame=reduced?0:Math.floor(now/125);
 if(!force&&frame===s.lastFrame)return;s.lastFrame=frame;se430BeginnerTeaching()?.drawDemo(s.context,s.tool,reduced?.75:now/1000,s.canvas.width,s.canvas.height);
}
/* SE430_MODEL_BEGINNER_UI_END */
