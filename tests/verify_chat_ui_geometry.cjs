// Browser geometry smoke test for the canonical Chat surface. Mocked endpoints are not API acceptance.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');

(async () => {
  const browser = await chromium.launch({headless:true,args:['--no-sandbox']});
  fs.mkdirSync('reports/chat-ui-v1060', {recursive:true});
  for (const [width,height] of [[320,700],[390,844],[768,1024],[1440,900]]) {
    const page = await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
    page.setDefaultTimeout(15000);
    await page.route('https://accounts.google.com/**', route => route.abort());
    await page.route('**/api/**', route => route.fulfill({
      status:200,contentType:'application/json',body:'{}'
    }));
    await page.goto('http://127.0.0.1:8765/chat/%C2%A7wyrlz/index.html',
      {waitUntil:'domcontentloaded',timeout:20000});
    const m = await page.evaluate(() => {
      const rect=id => {
        const el=document.getElementById(id);
        if (!el) return null;
        const r=el.getBoundingClientRect();
        return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};
      };
      return {
        innerWidth:innerWidth,innerHeight:innerHeight,scrollWidth:document.documentElement.scrollWidth,
        header:rect('topEdge'),menu:rect('menuButton'),chat:rect('chatViewport'),
        composer:rect('composerShell'),prompt:rect('prompt'),send:rect('sendButton')
      };
    });
    assert(m.header && m.menu && m.chat && m.composer && m.prompt && m.send);
    assert(m.scrollWidth <= width+2, `Page overflow at ${width}: ${JSON.stringify(m)}`);
    assert(m.header.left>=0 && m.header.right<=width+1, `Header clips at ${width}`);
    assert(m.menu.left>=0 && m.menu.right<=width+1, `Menu clips at ${width}`);
    assert(m.chat.width>0 && m.prompt.width>=130, `Chat/composer unusable at ${width}`);
    assert(Math.abs(m.composer.bottom-height)<2, `Composer not bottom anchored at ${width}`);
    assert(m.send.right<=width+1, `Send action clips at ${width}`);

    await page.evaluate(() => document.body.classList.add('menu-open'));
    await page.waitForTimeout(390);
    const menuRect = await page.locator('#sideMenu').boundingBox();
    assert(menuRect && menuRect.x>=-1 && menuRect.width>200, `Drawer not visible at ${width}`);
    await page.evaluate(() => document.body.classList.remove('menu-open'));

    await page.evaluate(() => document.body.classList.add('settings-open'));
    await page.waitForTimeout(390);
    const s = await page.evaluate(() => {
      const a=document.getElementById('settingsSheet').getBoundingClientRect();
      const n=document.querySelector('.settings-nav').getBoundingClientRect();
      return {left:a.left,right:a.right,top:a.top,bottom:a.bottom,navWidth:n.width,
        pageWidth:document.documentElement.scrollWidth,
        groups:[...document.querySelectorAll('.settings-nav-group-label')].length};
    });
    assert(s.left>=-1 && s.right<=width+1, `Settings clip at ${width}: ${JSON.stringify(s)}`);
    assert(s.pageWidth<=width+2 && s.navWidth<=width+1, `Settings cause page overflow at ${width}`);
    assert.equal(s.groups,4);
    await page.emulateMedia({reducedMotion:'reduce'});
    const anim = await page.evaluate(() => {
      const node=document.createElement('div');
      node.className='rendered-message';
      document.body.appendChild(node);
      const name=getComputedStyle(node).animationName;
      node.remove();
      return name;
    });
    assert.equal(anim,'none',`Reduced motion ignored at ${width}`);
    if (width===390 || width===1440) {
      await page.screenshot({path:`reports/chat-ui-v1060/chat-settings-${width}.png`,fullPage:false});
      await page.evaluate(() => document.body.classList.remove('settings-open'));
      await page.screenshot({path:`reports/chat-ui-v1060/chat-main-${width}.png`,fullPage:false});
    }
    console.log(`OK: §C UI geometry ${width}x${height}, nav, drawer, composer, reduced motion`);
    await page.close();
  }
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
