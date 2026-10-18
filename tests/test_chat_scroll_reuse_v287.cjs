/* v287 browser acceptance: real Chat DOM reuse under repeated Station sync.
 * Synthetic messages only. No accounts, no real model or private session data.
 */
"use strict";
const assert=require("node:assert/strict");
const {chromium}=require("playwright");

function sampleMessages(){
  const out=[];let stamp=1792350000000;
  for(let i=0;i<42;i++){
    out.push({id:"user-"+i,role:"user",createdAt:stamp++,text:"Question "+i+" about a long scroll. "+("Context ".repeat(i%5+2))});
    out.push({id:"assistant-"+i,role:"assistant",createdAt:stamp++,
      text:i===16?"Here is the graph of y=x²−4.":("### Reply "+i+"\n\n"+("Explained in the familiar Dragon Chat style. ".repeat(i%7+3))),
      meta:i===16?{state:"COMPLETE",widgets:[{
        contract:"swrlz-widget-v1",kind:"math-graph",version:1,
        title:"Equation explorer",provider:"Local",data:{
          series:[{type:"polynomial",coefficients:[-4,0,1]}],
          domain:[-5,5],range:[-6.5,23.5]}
      }]}:{state:"COMPLETE"}
    });
  }
  return out;
}

(async()=>{
  const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
  const page=await browser.newPage({
    viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true
  });
  const errors=[];page.on("pageerror",e=>errors.push(String(e.message||e)));
  let snapshotVersion=1,messages=sampleMessages(),syncCount=0;
  await page.route("**/api/lalm_station/sync*",async route=>{
    syncCount++;
    await route.fulfill({status:200,contentType:"application/json",body:JSON.stringify({
      revision:snapshotVersion,threads:[{id:"scroll-stability",title:"Scroll stability lab",
        createdAt:1792350000000,messages}],
      currentThread:{id:"scroll-stability"},state:{currentId:"scroll-stability"},
      activeGeneration:null
    })});
  });
  await page.route("**/api/chat_state",async route=>route.fulfill({
    status:200,contentType:"application/json",body:JSON.stringify({revision:snapshotVersion})
  }));
  await page.route("**/api/account/**",async route=>route.fulfill({
    status:401,contentType:"application/json",body:"{}"
  }));
  await page.route("**/api/chat?*",async route=>route.fulfill({status:204,body:""}));
  await page.goto("http://127.0.0.1:8765/chat/§wyrlz/index.html",{waitUntil:"domcontentloaded"});
  await page.waitForFunction(()=>[...document.querySelectorAll(".thread-row .thread-title")]
    .some(n=>n.textContent==="Scroll stability lab"));
  await page.evaluate(()=>{
    [...document.querySelectorAll(".thread-row .thread-main")]
      .find(n=>n.textContent.includes("Scroll stability lab")).click();
  });
  await page.waitForFunction(()=>document.querySelectorAll(".rendered-message:not(.station-live-message)").length===84);
  const initial=await page.evaluate(()=>{
    const elements=[...document.querySelectorAll(".rendered-message:not(.station-live-message)")];
    const graph=elements.find(n=>n.dataset.messageId==="assistant-16").querySelector("canvas");
    window.__stable={first:elements[1],middle:elements[42],last:elements[81],graph};
    const viewport=document.getElementById("chatViewport");
    viewport.scrollTop=Math.round((viewport.scrollHeight-viewport.clientHeight)*.44);
    return {count:elements.length,scrollTop:viewport.scrollTop,height:viewport.scrollHeight,graph:!!graph};
  });
  assert.equal(initial.count,84);
  assert.equal(initial.graph,true,"typed graph originally drew a real Canvas");
  // Repeated server hydration with unchanged thread should never remount canvases.
  const pre=syncCount;
  await page.evaluate(()=>window.dispatchEvent(new Event("focus")));
  await page.waitForFunction((n)=>window.__syncCountMarker===n,{},{timeout:400}).catch(()=>{});
  await page.waitForTimeout(150);
  assert.ok(syncCount>pre,"Station refresh was reached");

  // A new saved message changes the thread signature while 84 earlier entries
  // remain unchanged. It must not recreate any older DOM or reset graph zoom.
  messages=[...messages,{id:"user-new",role:"user",text:"One later message",createdAt:1792350999000}];
  snapshotVersion=2;
  const before=syncCount;
  await page.evaluate(()=>window.dispatchEvent(new Event("focus")));
  await page.waitForFunction(()=>document.querySelectorAll(".rendered-message:not(.station-live-message)").length===85);
  assert.ok(syncCount>before);
  const after=await page.evaluate(()=>{
    const viewport=document.getElementById("chatViewport");
    const all=[...document.querySelectorAll(".rendered-message:not(.station-live-message)")];
    const same=window.__stable.first===all[1]&&window.__stable.middle===all[42]&&
      window.__stable.last===all[81]&&
      window.__stable.graph===all.find(n=>n.dataset.messageId==="assistant-16").querySelector("canvas");
    document.body.dataset.companionState="responding";
    const historicalAvatar=all[1].querySelector(".assistant-head .kompanion-icon");
    return {same,scrollTop:viewport.scrollTop,count:all.length,
      historyAnimation:historicalAvatar?getComputedStyle(historicalAvatar).animationName:"missing",
      overflow:document.documentElement.scrollWidth>innerWidth+2};
  });
  assert.equal(after.same,true,"unchanged message nodes and widget canvas survive sync");
  assert.ok(Math.abs(after.scrollTop-initial.scrollTop)<120,"scroll anchor stays stable");
  assert.equal(after.historyAnimation,"none","historical avatars must not animate on generation state");
  assert.equal(after.overflow,false,"no horizontal overflow on 390px phone viewport");
  // A changed historic message should replace only that specific node.
  messages=messages.map(x=>x.id==="assistant-5"?{...x,text:x.text+"\nChanged paragraph."}:x);
  snapshotVersion=3;
  await page.evaluate(()=>window.dispatchEvent(new Event("focus")));
  await page.waitForFunction(()=>document.querySelector('[data-message-id="assistant-5"]')?.textContent.includes("Changed paragraph."));
  const changed=await page.evaluate(()=>{
    const mid=document.querySelector('[data-message-id="assistant-5"]');
    return {updated:!!mid,
      preserved:window.__stable.graph===document.querySelector('[data-message-id="assistant-16"] canvas'),
      unchanged:window.__stable.first===document.querySelector('[data-message-id="assistant-0"]')};
  });
  assert.ok(changed.updated&&changed.preserved&&changed.unchanged);
  assert.deepEqual(errors,[],"no JS runtime exceptions");
  console.log(JSON.stringify({status:"PASS",messages:after.count,canvasSurvives:true,
    scrollAnchorDelta:after.scrollTop-initial.scrollTop,historicalAnimation:after.historyAnimation,
    changedOnly:true,syncCount}));
  await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
