#!/usr/bin/env python3
"""§C full create/revise test with canonical stored code-artifact revision checks.

Tests the intended app contract: on a code-artifact mutation the assistant's
short prose is a receipt; full revised source lives in the revision-bound
artifact. Never substitute chat prose for the actual saved code.
"""
from __future__ import annotations
import asyncio,hashlib,json,re,sys,time
from datetime import datetime,timezone
from pathlib import Path
from playwright.async_api import async_playwright
from scripts import eval_chat_guest_suite as ev
from scripts.test_guest_html_functionality import evaluate_page

OUT=Path("reports/html-two-turn-artifact")
OUT.mkdir(parents=True,exist_ok=True)
CASE=next(c for c in ev.CASES["2"] if c["id"]=="html-button-ui")
PROMPTS=[turn["prompt"] for turn in CASE["turns"]]

def source_hash(files):
    norm=[{"path":str(f.get("path") or ""),"language":str(f.get("language") or ""),
           "content":str(f.get("content") or "")}
          for f in files if isinstance(f,dict)]
    data=json.dumps(norm,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    return hashlib.sha256(data.encode()).hexdigest()

def html_file(artifact):
    files=[f for f in artifact.get("files") or []
           if isinstance(f,dict) and str(f.get("path") or "").endswith(".html")]
    if len(files)!=1:
        raise AssertionError("Expected exactly one HTML file in this synthetic project")
    return str(files[0].get("content") or "")

def matching_artifact(snapshot,tid):
    thread=next((t for t in snapshot.get("threads") or [] if t.get("id")==tid),None)
    if not thread:
        raise AssertionError("Synthetic guest thread was not found")
    artifacts=[a for a in thread.get("codeArtifacts") or []
               if a.get("type")=="code" and a.get("title")=="index.html"]
    if len(artifacts)!=1:
        raise AssertionError("Expected exactly one canonical index.html artifact")
    return thread,artifacts[0]

async def main():
    report={"schema":"swrlz-html-code-artifact-same-thread-v1",
            "created_utc":datetime.now(timezone.utc).isoformat(),
            "scope":"two-turn anonymous mobile Chat; source belongs only to this synthetic session",
            "pass":False,"turns":[]}
    t0=time.perf_counter()
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True,args=["--disable-dev-shm-usage"])
        context=await browser.new_context(viewport={"width":390,"height":844},
                                          is_mobile=True,has_touch=True)
        page=await context.new_page()
        try:
            await ev.ensure_guest(context)
            await ev.sync(context)
            loaded=await page.goto(ev.BASE+"/",wait_until="domcontentloaded",timeout=30000)
            if not loaded or loaded.status!=200:
                raise AssertionError("Guest UI did not load")
            await page.locator("#prompt").wait_for(state="visible",timeout=25000)
            await ev.dismiss_update_overlay(page)
            first=await ev.ui_turn(context,page,PROMPTS[0],None,1)
            tid=first["thread_id"]
            snap1=await ev.sync(context)
            thread1,art1=matching_artifact(snap1,tid)
            if art1.get("currentRevision")!=1:
                raise AssertionError("First HTML artifact was not revision 1")
            files1=art1.get("files") or []
            if source_hash(files1)!=art1.get("currentSourceHash"):
                raise AssertionError("First source hash mismatch")
            html1=html_file(art1)
            if "<html" not in html1.lower() or "</html>" not in html1.lower():
                raise AssertionError("First artifact source is not a full HTML file")
            first_ui=await evaluate_page(browser,html1,require_reset=False)
            if not first_ui["pass"]:
                raise AssertionError("Initial HTML button did not work in Chromium")
            (OUT/"initial.html").write_text(html1)
            report["turns"].append({
                "turn":1,"duration_ms":first.get("total_ms"),
                "source_bytes":len(html1.encode()),"artifact_revision":1,
                "source_sha256":hashlib.sha256(html1.encode()).hexdigest(),
                "browser":first_ui})
            second=await ev.ui_turn(context,page,PROMPTS[1],tid,2)
            if second["thread_id"]!=tid:
                raise AssertionError("Revision changed the guest thread")
            snap2=await ev.sync(context)
            thread2,art2=matching_artifact(snap2,tid)
            if art2.get("id")!=art1.get("id") or art2.get("currentRevision")!=2:
                raise AssertionError("Revised source not committed as same artifact revision 2")
            files2=art2.get("files") or []
            if source_hash(files2)!=art2.get("currentSourceHash"):
                raise AssertionError("Revision 2 source hash mismatch")
            revisions=art2.get("revisions") or []
            rev1=next((r for r in revisions if r.get("revision")==1),None)
            rev2=next((r for r in revisions if r.get("revision")==2),None)
            if not rev1 or not rev2 or (rev2.get("parentSourceHash")!=rev1.get("sourceHash")):
                raise AssertionError("Revision parent identity or lineage missing")
            html2=html_file(art2)
            if len(html2)<=100 or html1==html2:
                raise AssertionError("Revision did not change complete HTML source")
            second_ui=await evaluate_page(browser,html2,require_reset=True)
            if not second_ui["pass"]:
                raise AssertionError("Revised Change/Reset/Change interactions failed in Chromium")
            report["turns"].append({
                "turn":2,"duration_ms":second.get("total_ms"),
                "source_bytes":len(html2.encode()),"artifact_revision":2,
                "source_sha256":hashlib.sha256(html2.encode()).hexdigest(),
                "reply_is_short_receipt":second["text"].startswith("Updated code artifact to revision"),
                "browser":second_ui})
            (OUT/"revised.html").write_text(html2)
            latest=next((m for m in reversed(thread2.get("messages") or [])
                         if m.get("role")=="assistant"),None)
            meta=(latest or {}).get("meta") or {}
            if (meta.get("codeArtifactId")!=art2["id"] or
                meta.get("updatedCodeArtifactId")!=art2["id"] or
                int(meta.get("artifactRevision") or 0)!=2):
                raise AssertionError("Second assistant receipt not linked to saved revision")
            download=await context.request.get(
                ev.BASE+"/api/lalm_station/artifacts/"+tid+"/"+art2["id"]+
                "/download?revision=2",timeout=25000)
            report["revision_download_http"]=download.status
            report["revision_download_header"]=download.headers.get("x-swrlz-artifact-revision")
            if download.status!=200 or report["revision_download_header"]!="2":
                raise AssertionError("Stored revision 2 archive was not downloadable")
            report["artifact_revision_count"]=len(revisions)
            report["pass"]=True
            return 0
        except Exception as error:
            report["error"]=type(error).__name__+": "+str(error)[:240]
            try:await page.screenshot(path=str(OUT/"failure.png"),timeout=7000)
            except Exception:pass
            return 1
        finally:
            report["elapsed_ms"]=round((time.perf_counter()-t0)*1000)
            (OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
            print("HTML_ARTIFACT_TWO_TURN_RESULT",json.dumps(report),flush=True)
            await context.close()
            await browser.close()
if __name__=="__main__":
    sys.exit(asyncio.run(main()))
