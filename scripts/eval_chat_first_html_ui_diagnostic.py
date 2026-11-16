#!/usr/bin/env python3
"""Guest-only new HTML UI diagnostic with correct first-thread attribution.

This is evidence gathering, not an alternative production renderer. Synthetic
browser prompts only; never log cookies, account info or unrelated threads.
"""
from __future__ import annotations
import asyncio,json,time,sys
from pathlib import Path
from playwright.async_api import async_playwright
from scripts import eval_chat_guest_suite as ev
OUT=Path("reports/ui-html-first-turn")
OUT.mkdir(parents=True,exist_ok=True)
PROMPT=next(c for c in ev.CASES["2"] if c["id"]=="html-button-ui")["turns"][0]["prompt"]
async def main():
    data={"case":"first-html-ui","mode":"anonymous-chromium","pass":False}
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=["--disable-dev-shm-usage"])
        context=await browser.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
        page=await context.new_page()
        try:
            await ev.ensure_guest(context)
            await ev.sync(context)
            await page.goto(ev.BASE+"/",wait_until="domcontentloaded",timeout=30000)
            await page.locator("#prompt").wait_for(state="visible",timeout=25000)
            await ev.dismiss_update_overlay(page)
            start=time.perf_counter()
            await page.locator("#prompt").fill(PROMPT)
            await page.locator("#sendButton").click()
            await page.wait_for_function("(p)=>[...document.querySelectorAll('.user-message .user-bubble')].some(e=>e.textContent.trim()===p)",arg=PROMPT,timeout=15000)
            thread_id=None
            for i in range(18):
                snapshot=await ev.sync(context)
                for t in snapshot.get("threads") or []:
                    if any(x.get("role")=="user" and x.get("text")==PROMPT for x in t.get("messages") or []):
                        thread_id=t.get("id")
                        break
                if thread_id:break
                await asyncio.sleep(0.6)
            data["thread_registered"]=bool(thread_id)
            data["thread_resolve_ms"]=round((time.perf_counter()-start)*1000)
            data["server_has_active_generation"]=bool((snapshot.get("activeGeneration") or {}).get("requestId"))
            if not thread_id:
                data["error"]="USER_MESSAGE_NOT_FOUND_IN_SESSION"
                return 1
            elapsed=0
            phases=[]
            last={}
            while elapsed<170:
                snapshot=await ev.sync(context)
                gen=snapshot.get("activeGeneration") or {}
                if gen.get("threadId")==thread_id:
                    for stage in (gen.get("status") or []):
                        label=str(stage.get("phase") or "")
                        if label and label not in phases:phases.append(label)
                    last={"phase":gen.get("phase"),"terminal":gen.get("terminal"),
                          "preview_chars":len(str(gen.get("previewText") or "")),
                          "accepted_chars":len(str(gen.get("text") or "")),
                          "attempts":len(gen.get("candidateAttempts") or []),
                          "validation":(gen.get("candidateValidation") or {}).get("status")}
                reply=ev.committed(snapshot,prompt=PROMPT,thread_id=thread_id)
                if reply:
                    data["server_committed"]=True
                    data["response_chars"]=len(reply[1])
                    data["static_grade"]=ev.evaluate({"check":"html_interactive"},reply[1])["status"]
                    data["elapsed_ms"]=round((time.perf_counter()-start)*1000)
                    try:
                        await page.wait_for_function(
                            "document.querySelectorAll('#messageList .assistant-message.rendered-message:not(.station-live-message) .assistant-body').length>=1",
                            timeout=16000)
                        data["ui_visible"]=True
                    except Exception:data["ui_visible"]=False
                    data["pass"]=data["static_grade"]=="PASS_EVIDENCE" and data["ui_visible"]
                    break
                elapsed=time.perf_counter()-start
                await asyncio.sleep(1.5)
            data["phase_evidence"]=phases[-22:]
            data["generation_state"]=last
            if not data["pass"]:
                data["error"]=data.get("error") or "NO_COMPLETE_UI_HTML"
                await page.screenshot(path=str(OUT/"failure.png"),timeout=7000)
            return 0 if data["pass"] else 1
        except Exception as exc:
            data["error"]=type(exc).__name__+":"+str(exc)[:220]
            try:await page.screenshot(path=str(OUT/"failure.png"),timeout=7000)
            except Exception:pass
            return 1
        finally:
            await context.close();await browser.close()
            (OUT/"report.json").write_text(json.dumps(data,indent=2)+"\n")
            print("HTML_UI_FIRST_TURN_DIAGNOSTIC",json.dumps(data),flush=True)
if __name__=="__main__":
    sys.exit(asyncio.run(main()))
