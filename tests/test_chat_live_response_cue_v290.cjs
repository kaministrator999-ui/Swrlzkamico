/* v290 mobile/browser acceptance: only an ACTIVE Station generation shimmers.
   Controlled synthetic Station snapshots; no account, GitHub, model or writes.
*/
"use strict";
const assert=require("node:assert/strict");
const {chromium}=require("playwright");

(async()=>{
  const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
  try{
    const page=await browser.newPage({
      viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true
    });
    const errors=[];
    page.on("pageerror",err=>errors.push(String(err.message||err)));
    const threadId="live-cue-v290",rid="request-v290",now=1792528000000;
    let generation={requestId:rid,threadId,text:"",
      status:[{type:"QUEUED",phase:"QUEUED",atUnixMs:now}],widgets:[],
      terminal:false,lastSeq:1,createdAt:now,acceptedAtUnixMs:now};
    let messages=[
      {id:"user-test",role:"user",createdAt:now,text:"Explain the source file"},
      {id:"historic-reply",role:"assistant",createdAt:now-200,
       text:"A historical reply must stay still.",meta:{state:"COMPLETE"}}
    ];
    let revision=1;
    await page.route("**/api/lalm_station/sync*",async route=>route.fulfill({
      status:200,contentType:"application/json",
      body:JSON.stringify({revision,threads:[{id:threadId,title:"Live animation lab",
        createdAt:now,messages}],currentThread:{id:threadId},
        state:{currentId:threadId},activeGeneration:generation})
    }));
    await page.route("**/api/chat_state",async route=>route.fulfill({
      status:200,contentType:"application/json",body:JSON.stringify({revision})
    }));
    await page.route("**/api/account/**",async route=>route.fulfill({
      status:401,contentType:"application/json",body:"{}"
    }));
    await page.route("**/api/chat?*",async route=>route.fulfill({status:204,body:""}));
    await page.goto("http://127.0.0.1:8765/chat/§wyrlz/index.html",{waitUntil:"domcontentloaded"});
    await page.waitForFunction(()=>[...document.querySelectorAll(".thread-row .thread-title")]
      .some(n=>n.textContent==="Live animation lab"));
    await page.evaluate(()=>[...document.querySelectorAll(".thread-row .thread-main")]
      .find(n=>n.textContent.includes("Live animation lab")).click());
    // Selecting an existing thread is presentation-only. The next Station
    // hydration is what associates its acknowledged active generation.
    await page.evaluate(()=>window.dispatchEvent(new Event("focus")));
    try {
      await page.waitForSelector('.station-live-message[data-response-live="true"] .response-live-tail',{timeout:12000});
    }catch(err){
      const diagnosis=await page.evaluate(()=>({
        threadList:[...document.querySelectorAll(".thread-row .thread-title")].map(n=>n.textContent),
        activeThreadTitle:document.getElementById("topThreadTitle")?.textContent,
        liveNodes:[...document.querySelectorAll(".station-live-message")].map(n=>({
          live:n.dataset.responseLive,request:n.dataset.requestId,html:n.outerHTML.slice(0,900)})),
        responseTails:document.querySelectorAll(".response-live-tail").length,
        renderedMessages:document.querySelectorAll(".rendered-message").length,
        topState:document.getElementById("topEdge")?.dataset.state,
        notice:document.body.innerText.slice(-350)
      }));
      console.error("v290 DIAG FIRST-LIVE",JSON.stringify({diagnosis,errors}));
      throw err;
    }
    let state=await page.evaluate(()=>{
      const live=document.querySelector('.station-live-message');
      const tail=live?.querySelector(".response-live-tail");
      return {tail:tail?.innerText,bodyHidden:live?.querySelector(".assistant-body")?.hidden,
        dots:tail?.querySelectorAll(".response-live-dots span").length,
        historical:document.querySelector('[data-message-id="historic-reply"] .response-live-tail')!==null};
    });
    assert.ok(state.tail.includes("Preparing response"),JSON.stringify(state));
    assert.equal(state.bodyHidden,true,"pre-token body remains hidden");
    assert.equal(state.dots,3);
    assert.equal(state.historical,false);

    // Real generation evidence arrives: the body shimmers and the tail moves
    // to the end of the response, without claiming any completion percentage.
    generation={...generation,text:"### Explanation\n\nThe source dependency is verified.",
      status:[...generation.status,{type:"STATUS",phase:"GENERATING",atUnixMs:now+1000}],
      lastSeq:2};
    revision++;
    await page.evaluate(()=>window.dispatchEvent(new Event("focus")));
    await page.waitForFunction(()=>document.querySelector('.response-live-label')?.textContent==="Still responding");
    state=await page.evaluate(()=>{
      const live=document.querySelector('.station-live-message');
      const bubble=live.querySelector(".assistant-body");
      const tail=live.querySelector(".response-live-tail");
      return {text:bubble.innerText,visible:!bubble.hidden,
        bodyAnimation:getComputedStyle(bubble,"::after").animationName,
        dotAnimation:getComputedStyle(tail.querySelector(".response-live-dots span")).animationName,
        overflow:document.documentElement.scrollWidth>innerWidth+2};
    });
    assert.ok(state.text.includes("source dependency"),JSON.stringify(state));
    assert.equal(state.visible,true);
    assert.equal(state.bodyAnimation,"swrlzReplySheenV290");
    assert.equal(state.dotAnimation,"swrlzReplyDotV290");
    assert.equal(state.overflow,false,"no horizontal mobile overflow");

    // User and operating system motion preferences keep status informational
    // but make every animation static.
    await page.evaluate(()=>{
      document.body.classList.remove("motion-full");
      document.body.classList.add("motion-reduced");
    });
    state=await page.evaluate(()=>{
      const live=document.querySelector('.station-live-message');
      return {tail:!!live.querySelector(".response-live-tail"),
        animation:getComputedStyle(live.querySelector(".assistant-body"),"::after").animationName,
        dots:getComputedStyle(live.querySelector(".response-live-dots span")).animationName};
    });
    assert.equal(state.tail,true);
    assert.equal(state.animation,"none");
    assert.equal(state.dots,"none");
    await page.evaluate(()=>document.body.classList.remove("motion-reduced"));

    // A Station terminal event must remove the active shimmer and tail even
    // before the committed answer is hydrated.
    generation={...generation,terminal:true,terminalType:"COMPLETED",
      status:[...generation.status,{type:"COMPLETED",phase:"COMPLETE",atUnixMs:now+2000}],lastSeq:3};
    revision++;
    await page.evaluate(()=>window.dispatchEvent(new Event("focus")));
    await page.waitForFunction(()=>{
      const n=document.querySelector(".station-live-message");
      return !!n && n.dataset.responseLive!=="true" && !n.querySelector(".response-live-tail");
    });
    state=await page.evaluate(()=>{
      const n=document.querySelector(".station-live-message");
      return {tail:!!n.querySelector(".response-live-tail"),
        animation:getComputedStyle(n.querySelector(".assistant-body"),"::after").animationName};
    });
    assert.equal(state.tail,false);
    assert.equal(state.animation,"none");

    // Committing the response replaces the live DOM. Re-hydrating an older
    // thread must never resurrect shimmer, even with a saved activity trace.
    messages=[...messages,{id:"committed-v290",role:"assistant",createdAt:now+2000,
      text:generation.text,meta:{requestId:rid,state:"COMPLETE",progressTrace:{
        schema:"swrlz-chat-activity-timeline-v1",requestId:rid,
        events:[{index:1,phase:"GENERATING",atUnixMs:now+1000},
                {index:2,phase:"COMPLETE",atUnixMs:now+2000}]}}}];
    generation=null;revision++;
    await page.evaluate(()=>window.dispatchEvent(new Event("focus")));
    await page.waitForFunction(()=>document.querySelector('[data-message-id="committed-v290"]')!==null);
    assert.equal(await page.locator('.rendered-message[data-response-live="true"]').count(),0);
    assert.equal(await page.locator(".response-live-tail").count(),0);

    // The same bounded terminal cleanup applies to failed, stopped messages.
    for(const kind of ["FAILED","CANCELLED"]){
      generation={requestId:rid+"-"+kind,threadId,text:"partial",widgets:[],
        status:[{type:kind,phase:kind,atUnixMs:now+4000}],terminal:true,
        terminalType:kind,lastSeq:4,createdAt:now+4000};
      revision++;
      await page.evaluate(()=>window.dispatchEvent(new Event("focus")));
      await page.waitForFunction((kind)=>{
        const n=document.querySelector(".station-live-message");
        return n && n.dataset.requestId.endsWith(kind) && !n.querySelector(".response-live-tail");
      },kind);
      assert.equal(await page.locator(".station-live-message[data-response-live='true']").count(),0);
    }
    assert.deepEqual(errors,[],"no page script crashes");
    console.log("v290 browser: pre-token, in-stream, mobile shimmer, reduced motion, terminal, historical, failure/cancel PASS");
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
