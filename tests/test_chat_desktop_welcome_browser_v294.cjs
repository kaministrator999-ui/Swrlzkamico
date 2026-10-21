/* v294 browser layout verification using the canonical Chat CSS.
 * Fixture mirrors the existing first-run DOM only; no login, inference or mutating API.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const {chromium}=require("playwright");
const html=fs.readFileSync("chat/§wyrlz/index.html","utf8");
const style=html.match(/<style>\s*([\s\S]*?)<\/style>/i)?.[1];
assert.ok(style&&style.includes(".first-run-welcome"),"Canonical Chat stylesheet available");
const escapeHtml=text=>text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
const heading="Hey there 👋 Welcome to the Dragon Den. 🐉";
const fixture='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1">'+
  '<style>'+style+'</style></head><body><main class="chat-viewport" aria-label="Conversation">'+
  '<div class="message-list"><section class="first-run-welcome rendered-message">'+
  '<div class="first-run-kicker">First conversation</div>'+
  '<h2 class="first-run-title">'+escapeHtml(heading)+'</h2>'+
  '<p class="first-run-copy">I’m §wyrlz, your Glitch Dragon Kompanion. What should I call you? You can also tell me anything you want me to know about you as we chat.</p>'+
  '<div class="first-run-hint">You can change your profile, preferences, and companion settings later from Settings.</div>'+
  '</section></div></main></body></html>';
(async()=>{
  const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
  try{
    for(const [width,height,mode] of [[1440,900,"desktop-wide"],[1024,768,"desktop-laptop"],[800,680,"desktop-small"],[390,844,"mobile"]]){
      const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
      await page.setContent(fixture,{waitUntil:"domcontentloaded"});
      const dims=await page.evaluate(()=>{
        const card=document.querySelector(".first-run-welcome"),list=document.querySelector(".message-list");
        const c=card.getBoundingClientRect(),l=list.getBoundingClientRect(),cs=getComputedStyle(card);
        return {cardX:c.x,cardY:c.y,cardWidth:c.width,cardHeight:c.height,listX:l.x,
          listWidth:l.width,titleSize:parseFloat(getComputedStyle(card.querySelector(".first-run-title")).fontSize),
          divider:getComputedStyle(card.querySelector(".first-run-hint")).borderTopStyle,
          glass:cs.backdropFilter,marginLeft:cs.marginLeft,
          overflow:document.documentElement.scrollWidth>innerWidth,
          greeting:card.querySelector("h2").textContent};
      });
      assert.equal(dims.greeting,heading,mode+" greeting preserved");
      assert.equal(dims.overflow,false,mode+" no horizontal overflow");
      if(width>=761){
        assert.ok(dims.cardWidth<=561&&dims.cardWidth>=450,mode+" medium sized welcome card: "+JSON.stringify(dims));
        assert.ok(Math.abs((dims.cardX+dims.cardWidth/2)-(dims.listX+dims.listWidth/2))<=2,
          mode+" centered within conversation: "+JSON.stringify(dims));
        assert.ok(dims.cardY>60&&dims.cardY+dims.cardHeight<height-35,mode+" clear header/composer");
        assert.ok(dims.titleSize>=22,mode+" heading hierarchy");
        assert.equal(dims.divider,"solid",mode+" hint separator");
      }else{
        assert.ok(dims.cardWidth>=dims.listWidth*.97,mode+" retain mobile full width");
        assert.ok(dims.titleSize<=21,mode+" preserve mobile typography");
      }
      if(mode==="desktop-wide"){
        await page.evaluate(()=>document.body.classList.add("a11y-reduced-transparency"));
        const reduced=await page.locator(".first-run-welcome").evaluate(node=>getComputedStyle(node).backdropFilter);
        assert.equal(reduced,"none","Reduced-transparency accessibility override");
      }
      console.log(mode+" PASS "+JSON.stringify(dims));
      await page.close();
    }
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1});
