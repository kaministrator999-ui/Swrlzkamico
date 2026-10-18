/* §wyrlz v285: browser-level preview/interaction acceptance in an isolated localhost harness. */
"use strict";
const assert=require("node:assert/strict");
const {chromium}=require("playwright");
(async()=>{
  const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
  const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1,hasTouch:true,isMobile:true});
  const errors=[];
  page.on("pageerror",error=>errors.push(String(error.message||error)));
  await page.goto("http://127.0.0.1:8765/chat/§wyrlz/assets/widget-atelier-v284.html",{waitUntil:"networkidle"});
  await page.locator(".swrlz-widget").first().waitFor();
  assert.equal(await page.locator(".swrlz-widget").count(),4);
  assert.equal(await page.locator(".rich-compare-table tbody tr").count(),3);
  assert.equal(await page.locator(".rich-widget-canvas").count(),3,"one math canvas and two 3D previews");
  assert.ok(await page.locator(".rich-equation").first().innerText().then(x=>x.includes("x²")));
  const firstReadout=await page.locator(".math-graph .rich-widget-readout").innerText();
  await page.locator(".math-graph button[aria-label='Zoom in']").click();
  const nextReadout=await page.locator(".math-graph .rich-widget-readout").innerText();
  assert.notEqual(firstReadout,nextReadout,"zoom affects graph viewport");
  const shapeCanvas=page.locator(".model-3d .rich-widget-canvas").first();
  const before=await page.locator(".model-3d .rich-widget-readout").first().innerText();
  await shapeCanvas.focus();
  await shapeCanvas.press("ArrowRight");
  const after=await page.locator(".model-3d .rich-widget-readout").first().innerText();
  assert.notEqual(before,after,"keyboard changes model rotation");
  const image=await shapeCanvas.evaluate(canvas=>{
    const ctx=canvas.getContext("2d");
    const pixels=ctx.getImageData(0,0,canvas.width,canvas.height).data;
    let tinted=0;
    for(let i=0;i<pixels.length;i+=200){
      if(pixels[i+1]>150&&pixels[i+2]>160)tinted++;
    }
    return tinted;
  });
  assert.ok(image>0,"wireframe produced nonblank visible pixels");
  const mobile=await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,width:innerWidth}));
  assert.ok(mobile.scrollWidth<=mobile.width+3,"page has no horizontal overflow on narrow Android-style viewport");
  assert.deepEqual(errors,[],"no unhandled JS errors");
  console.log(JSON.stringify({status:"PASS",widgets:4,canvases:3,zoom:true,keyboardRotate:true,paintedPixels:image,mobile}));
  await browser.close();
})().catch(err=>{console.error(err);process.exitCode=1;});
