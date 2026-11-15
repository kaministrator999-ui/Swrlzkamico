#!/usr/bin/env python3
"""Execute synthetic §C HTML responses in isolated headless Chromium.

No user logins, network navigation, secrets or page assets are supplied. All
external requests are blocked. This adds behavioral evidence beyond regex gates.
"""
import argparse,asyncio,json,re,sys
from pathlib import Path
from playwright.async_api import async_playwright

HTML_RE=re.compile(r"(?is)<!doctype\s+html[^>]*>.*?</html\s*>")
def extract_html(text):
    matches=HTML_RE.findall(str(text or ""))
    if len(matches)!=1:raise ValueError("Expected exactly one complete HTML document")
    return matches[0]
async def evaluate_page(browser,markup,require_reset):
    context=await browser.new_context(viewport={"width":390,"height":844},
        java_script_enabled=True,service_workers="block",accept_downloads=False,
        permissions=[])
    page=await context.new_page()
    runtime_errors=[]
    page.on("pageerror",lambda e:runtime_errors.append(str(e)[:180]))
    await page.route("**/*",lambda route:route.abort())
    out={"pass":False,"button_count":0,"initial_changed":False,"reset_restored":False,
         "runtime_errors":[]}
    try:
        await page.set_content(markup,wait_until="domcontentloaded",timeout=12000)
        await page.wait_for_timeout(350)
        buttons=page.locator("button, input[type='button']")
        out["button_count"]=await buttons.count()
        if out["button_count"]<2 if require_reset else out["button_count"]<1:
            out["error"]="Requested interactive controls missing"
            return out
        async def body_text():
            return (await page.locator("body").inner_text()).strip()
        initial=await body_text()
        reset_buttons=buttons.filter(has_text=re.compile(r"\breset\b",re.I))
        reset=reset_buttons.first if await reset_buttons.count() else None
        if require_reset and reset is None:
            out["error"]="Revision did not supply a Reset button"
            return out
        trigger=None
        for index in range(out["button_count"]):
            candidate=buttons.nth(index)
            label=(await candidate.inner_text()).strip()
            if not re.search(r"\breset\b",label,re.I):
                trigger=candidate
                break
        if trigger is None:
            out["error"]="No action button available for test"
            return out
        await trigger.click(timeout=6000)
        await page.wait_for_timeout(350)
        changed=await body_text()
        out["initial_changed"]=bool(changed and changed!=initial)
        if require_reset:
            await reset.click(timeout=6000)
            await page.wait_for_timeout(350)
            restored=await body_text()
            out["reset_restored"]=bool(restored==initial)
            if out["reset_restored"]:
                # Check reset did not permanently disable the original action.
                await trigger.click(timeout=6000)
                await page.wait_for_timeout(350)
                out["repeat_click_works"]=((await body_text())!=initial)
        out["runtime_errors"]=runtime_errors[:5]
        out["pass"]=(out["initial_changed"] and not runtime_errors and
                      (not require_reset or (out["reset_restored"] and out.get("repeat_click_works",False))))
        return out
    except Exception as e:
        out["error"]=type(e).__name__+": "+str(e)[:200]
        out["runtime_errors"]=runtime_errors[:5]
        return out
    finally:
        await context.close()

async def main(report_path,output_path):
    data=json.loads(Path(report_path).read_text())
    case=next((c for c in data.get("results",[]) if c.get("id")=="html-button-ui"),None)
    summary={"schema":"swrlz-html-functional-evidence-v1","guest_only":True,"outcomes":[],"pass":False}
    if not case:
        summary["error"]="HTML case missing from guest report"
    elif len(case.get("turns") or [])!=2:
        summary["error"]="Two completed synthetic HTML turns required"
    else:
        async with async_playwright() as pw:
            browser=await pw.chromium.launch(headless=True,args=["--disable-dev-shm-usage"])
            try:
                for index,turn in enumerate(case["turns"]):
                    result={"turn":index+1,"prompt_type":"initial" if index==0 else "reset-revision"}
                    try:
                        markup=extract_html(turn.get("response") or "")
                        result.update(await evaluate_page(browser,markup,require_reset=index==1))
                    except Exception as e:
                        result.update({"pass":False,"error":type(e).__name__+": "+str(e)[:160]})
                    summary["outcomes"].append(result)
                summary["pass"]=all(x["pass"] for x in summary["outcomes"])
            finally:
                await browser.close()
    path=Path(output_path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(summary,indent=2)+"\n")
    print("HTML_FUNCTIONAL_SUMMARY",json.dumps(summary),flush=True)
    return 0 if summary["pass"] else 1
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--report",default="reports/chat-guest-eval/report.json")
    parser.add_argument("--output",default="reports/chat-guest-eval/functional-report.json")
    x=parser.parse_args()
    sys.exit(asyncio.run(main(x.report,x.output)))
