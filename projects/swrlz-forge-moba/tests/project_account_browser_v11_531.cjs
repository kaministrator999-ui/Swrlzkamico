#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync(process.argv[2],'utf8');
function section(start,end){
 const a=html.indexOf(start),b=html.indexOf(end,a+start.length);
 assert(a>=0&&b>a,'Compiled output missing '+start);
 return html.slice(a,b);
}
const saving=section('/* SE529_NATIVE_PROJECT_ACCOUNT_SAVE_START',
 '/* SE529_NATIVE_PROJECT_ACCOUNT_SAVE_END');
const browser=section('/* SE529_MY_PROJECTS_BROWSER_UI_START',
 '/* SE529_MY_PROJECTS_BROWSER_UI_END');
const css=section('/* SE529_MY_PROJECTS_BROWSER_CSS_START',
 '/* SE529_MY_PROJECTS_BROWSER_CSS_END');
const native=section('/* SE528_ACCOUNT_PROJECT_REPAIR_START',
 '/* SE528_ACCOUNT_PROJECT_REPAIR_END');
const legacy=section('/* §E v11.488 — naming guard around existing account writes.',
 'window.SWYRL_ENGINE_SAFE_PROJECTS_371=Object.freeze');
assert(html.includes('SWYRL_ENGINE_DEPLOY_MARKER: V11_531_QUEST_GIZMO_CONTROLLER_MENU'));
assert(html.includes('<title>§wyrl§ Engine · Maker v11.531</title>'));
assert(legacy.includes("assets.save('modeler',true)"),'Standalone model asset save remains independent');
assert(saving.includes('await se371PreviousSaveCloud()===true'),'Full-project save must use native source, not model-asset dispatcher');
assert(!saving.includes("assets.save('modeler'")&&!saving.includes("await saveCloud()"),'Project command must not invoke asset wrapper');
assert(saving.includes("se488EnsureProjectNameForAccount()"),'Preserve original naming/clone protections');
assert(saving.includes('await se371SaveLocal()')&&
 saving.includes('Number.isInteger(linked.revision)'), 'Persist locally and require actual version receipt');
assert(saving.includes('se528SaveAccount=se529SaveNativeProjectToAccount')&&
 saving.includes('window.SWYRL_ENGINE_ACCOUNT_SAVE_528=Object.freeze'), 'Wire Chat, My Projects and immersive VR to same path');
assert(native.includes('SWYRL_ENGINE_ACCOUNT_SAVE_528=Object.freeze'),'Prior native VR facade retained');
for(const text of ['se529LibraryHero','se529SaveAccount','se529SaveLocal','se529Refresh',
 'se529Advanced','se529LocalHeading','se529CloudHeading',
 'se529AccountConnect','se529AccountFeedback','se529-card-more',
 'se529-card-more-actions','se184ProjectCard=function','se529PolishLibrary',
 'se184RenderLocalProjects=function','se184RenderCloudProjects=function'])
 assert(browser.includes(text),'Browser library missing '+text);
assert(browser.includes('for(const control of advanced)inner.append(control)'),
 'Existing per-card delete/export/update controls must retain original event handlers');
assert(browser.includes('legacyTools&&legacyTools.parentElement!==advancedBody')&&
 browser.includes('if(local&&local.parentElement!==advancedBody)advancedBody.append(local)'),
 'Legacy actions must remain mounted under Advanced');
assert(browser.includes('se528InstallAccountSave=function()'),
 'Prevent legacy duplicate Save to account injection');
assert(css.includes('#projectHub #se529Advanced button[hidden]')&&
 css.includes('#projectHub #se184LocalCards')&&
 css.includes('.se529-card-more-actions')&&
 css.includes('@media(max-width:690px)'),'Responsive advanced/control hierarchy missing');
assert(css.includes('#seChatAccountPanel #seChatStatus'),
 'Save errors should be readable in Chat panel');
let nextRevision=2;
const calls={asset:0,native:0,local:0,naming:0,notice:[],refresh:0};
const cloudRefs=new Map([['local-123',{id:'remote-123',revision:1}]]);
const sandbox={
 window:{dispatchEvent(){},SWYRL_ENGINE_ASSET_LIBRARY:{save(){calls.asset++;return true;}}},
 CustomEvent:class{constructor(name,opts){this.name=name;this.detail=opts.detail;}},
 document:{getElementById(){return null;}},
 se528SaveAccount:async()=>false,
 se176AccountConnected:true,ready:true,cloudBusy:false,se175Transition:false,
 se175LocalLoading:false,se371ActionBusy:false,playing:false,simulating:false,
 se175Saving:null,se170Active:'starter',
 se488EnsureProjectNameForAccount:async()=>{calls.naming++;return true;},
 se371HasSavedIdentity:()=>true,se371SaveLocal:async()=>{calls.local++;},
 se175RefreshLocal:async()=>{calls.refresh++;},
 se176RefreshProjects:async()=>{calls.refresh++;},
 se170Refresh:async()=>{calls.refresh++;},
 se371ProjectName:()=> 'Smooth Witch Hat Copy',
 se371Display:(message,bad)=>{calls.notice.push({message,bad});sandbox.status.textContent=message;},
 se371PreviousSaveCloud:async()=>{
  calls.native++;cloudRefs.set('local-123',{id:'remote-123',revision:nextRevision++});return true;
 },
 getProjectId:()=> 'local-123',
 cloudRefs,se371CloudLinks:new Map(),
 status:{textContent:'Your Chat account is connected.'},
 frame:{src:'https://kamiloki-swyrlz.hf.space'},CHAT_ORIGIN:'https://kamiloki-swyrlz.hf.space'
};
vm.runInNewContext(saving+'\nthis.runSave=se529SaveNativeProjectToAccount;',sandbox);
(async()=>{
 const good=await sandbox.runSave();
 assert.equal(good.ok,true);
 assert.equal(good.revision,2);
 assert.equal(calls.native,1);
 assert.equal(calls.asset,0,'Model asset path was invoked by project save');
 assert.equal(calls.local,1);
 assert.equal(calls.naming,1);
 assert(calls.notice.some(n=>n.message.includes('Saved to your account ·')&&!n.bad));
 sandbox.se371PreviousSaveCloud=async()=>{
  calls.native++;sandbox.status.textContent='Account save failed: storage quota reached';return false;
 };
 const bad=await sandbox.runSave();
 assert.equal(bad.ok,false,'Missing durable revision cannot pass');
 assert.equal(bad.error,'ACCOUNT_SAVE_UNCONFIRMED');
 assert.equal(calls.asset,0);
 assert(calls.notice.at(-1).message.includes('storage quota reached'),
  'Real cloud error must be propagated, not stale "Chat connected" status');
 sandbox.ready=false;
 const disconnected=await sandbox.runSave();
 assert.equal(disconnected.ok,false);
 assert.equal(disconnected.error,'ACCOUNT_NOT_CONNECTED');
 assert.equal(calls.asset,0);
 console.log('SE529_ACCOUNT_BROWSER_PASS: native project route, confirmed revision, truthful failure, preserved asset workflow, browser controls');
})().catch(e=>{console.error(e);process.exitCode=1;});
