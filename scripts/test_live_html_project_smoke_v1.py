#!/usr/bin/env python3
"""Real Chromium acceptance of the same-Space sandboxed HTML project smoke."""
from __future__ import annotations
import asyncio
import json
from playwright.async_api import async_playwright

URL="https://kamiloki-swyrlz.hf.space/api/html-projects/swrlz-html-smoke/index.html"

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=["--no-sandbox"])
        page=await browser.new_page(viewport={"width":390,"height":800})
        issues=[]
        page.on("pageerror",lambda exception:issues.append(str(exception)))
        response=await page.goto(URL,wait_until="domcontentloaded",timeout=60000)
        if not response or response.status!=200:
            raise RuntimeError("Published HTML route did not return 200")
        csp=response.headers.get("content-security-policy","")
        if ("sandbox allow-scripts" not in csp or "allow-same-origin" in csp
                or "connect-src 'none'" not in csp):
            raise RuntimeError("Browser did not receive isolated CSP")
        await page.locator("#increment").wait_for(timeout=12000)
        before=await page.locator("#counter").inner_text()
        if before.strip()!="0":
            raise RuntimeError("Expected initial counter zero")
        await page.locator("#increment").click()
        after=await page.locator("#counter").inner_text()
        if after.strip()!="1":
            raise RuntimeError("Interactive JS failed to increment count")
        font=await page.locator("h1").evaluate("(e)=>getComputedStyle(e).fontSize")
        if not font or font=="16px":
            raise RuntimeError("Project CSS not applied")
        isolation=await page.evaluate("""async () => {
          let cookieAccess;
          try { document.cookie; cookieAccess='allowed'; }
          catch(e){cookieAccess=e.name;}
          let network;
          try{await fetch('/api/account/status');network='allowed';}
          catch(e){network='blocked';}
          return {cookieAccess,network};
        }""")
        if isolation["cookieAccess"]=="allowed" or isolation["network"]!="blocked":
            raise RuntimeError("Opaque-origin isolation or network CSP bypass: "+str(isolation))
        if issues:
            raise RuntimeError("Browser JavaScript exceptions: "+str(issues[:3]))
        print("HTML_SMOKE_BROWSER_VERIFIED",json.dumps({
            "url":URL,"httpStatus":response.status,"counter":after.strip(),
            "styleFontSize":font,"isolation":isolation,
            "runtimeErrors":0,"mobileViewport":"390x800"},sort_keys=True),flush=True)
        await browser.close()

if __name__=="__main__":
    asyncio.run(main())
