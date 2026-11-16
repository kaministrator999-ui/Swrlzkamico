#!/usr/bin/env python3
"""Verify the first synthetic guest HTML response actually changes the DOM."""
from __future__ import annotations
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
from scripts.test_guest_html_functionality import evaluate_page,extract_html
ROOT=Path("reports/chat-guest-eval")
async def main():
    report=json.loads((ROOT/"report.json").read_text())
    cases=[c for c in report.get("results",[]) if c.get("id")=="html-button-ui"]
    result={"schema":"swrlz-new-html-first-turn-browser-v1","pass":False}
    if len(cases)!=1 or len(cases[0].get("turns") or [])!=1:
        result["error"]="Expected one complete anonymous HTML response"
    else:
        case=cases[0]["turns"][0]
        try:
            html=extract_html(case.get("response") or "")
            async with async_playwright() as pw:
                browser=await pw.chromium.launch(headless=True,args=["--disable-dev-shm-usage"])
                try:
                    check=await evaluate_page(browser,html,require_reset=False)
                    result["browser"]=check
                    result["pass"]=bool(check["pass"] and
                        case.get("evaluation",{}).get("status")=="PASS_EVIDENCE")
                finally:await browser.close()
        except Exception as e:
            result["error"]=type(e).__name__+":"+str(e)[:180]
    (ROOT/"first-turn-browser-report.json").write_text(json.dumps(result,indent=2)+"\n")
    print("FIRST_HTML_BROWSER_ACCEPTANCE",json.dumps(result),flush=True)
    return 0 if result["pass"] else 1
if __name__=="__main__":sys.exit(asyncio.run(main()))
