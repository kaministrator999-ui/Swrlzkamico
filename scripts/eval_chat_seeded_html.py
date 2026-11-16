#!/usr/bin/env python3
"""Isolated guest-only test: revise a seeded HTML source without generating it first.

Uses the source import contract owned by Station. No authenticated identity,
connected account, repository modification or user file is touched.
"""
from __future__ import annotations
import asyncio,hashlib,json,os,re,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path
from playwright.async_api import async_playwright
from scripts import eval_chat_guest_suite as common
from scripts.test_guest_html_functionality import evaluate_page,extract_html

OUT=Path("reports/chat-seeded-html")
OUT.mkdir(parents=True,exist_ok=True)
HTML="""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Guest Fixture</title><style>body{font-family:sans-serif;padding:2rem}button{padding:.7rem;margin-right:.6rem}</style></head>
<body><p id="output">Ready</p><button id="change" type="button">Change</button>
<script>document.getElementById('change').addEventListener('click',()=>{document.getElementById('output').textContent='Changed';});</script>
</body></html>"""
PROMPT=("I imported an existing single-file HTML page in index.html. Add a working Reset "
        "button that restores the original 'Ready' text. Preserve the existing Change "
        "button, its click handler, layout and styles. Return the FULL revised HTML file, "
        "not a diff or fragment. No other features, links, libraries, or extra pages.")
TIMEOUT=int(os.getenv("SWRLZ_SEEDED_TIMEOUT_SECONDS","165"))

def safe_status(snapshot,thread_id):
    gen=snapshot.get("activeGeneration") or {}
    stages=[str(x.get("phase") or x.get("type") or "")[:50] for x in
            (gen.get("status") or [])[-18:] if isinstance(x,dict)]
    intent=gen.get("programmingIntent") or {}
    return {
        "revision":snapshot.get("revision"),
        "thread_found":any(t.get("id")==thread_id for t in snapshot.get("threads") or []),
        "phase":str(gen.get("phase") or "")[:80],
        "terminal":gen.get("terminal"),
        "status":stages,
        "change_class":intent.get("changeClass"),
        "coding_task":intent.get("codingTask"),
        "canonical_carry":bool(intent.get("canonicalCarry")),
        "import_target":bool(intent.get("artifactTargetId")),
        "preview_chars":len(str(gen.get("previewText") or "")),
        "accepted_chars":len(str(gen.get("text") or "")),
        "candidate_attempts":len(gen.get("candidateAttempts") or []),
        "validation_status":(gen.get("candidateValidation") or {}).get("status"),
        "response_budget":((gen.get("contextBudget") or {}).get("reservedOutputTokens")),
    }

async def main():
    result={"schema":"swrlz-seeded-html-revision-v1",
            "mode":"guest-only","case":"single-import-and-revise","created":datetime.now(timezone.utc).isoformat(),
            "source_sha256":hashlib.sha256(HTML.encode()).hexdigest(),
            "source_chars":len(HTML),"pass":False}
    start=time.perf_counter()
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True,args=["--disable-dev-shm-usage"])
        ctx=await browser.new_context()
        try:
            await common.ensure_guest(ctx)
            tid="guest-seeded-"+uuid.uuid4().hex[:18]
            rid="seeded-html-"+uuid.uuid4().hex[:16]
            body={"protocolVersion":2,"modelId":common.MODEL,"profileId":"LALM",
                  "ingress":"SWRLZ_LALM_STATION","threadId":tid,"requestId":rid,
                  "messageId":"u-"+uuid.uuid4().hex[:16],
                  "assistantMessageId":"a-"+uuid.uuid4().hex[:16],
                  "prompt":PROMPT,"profile":"","userProfile":"","timeZone":"UTC",
                  "projectFiles":[{"path":"index.html","language":"html","content":HTML}]}
            ack=await ctx.request.post(common.BASE+"/api/lalm_station/send",
                data=json.dumps(body),headers={"Content-Type":"application/json",
                                               "X-SWRLZ-Request-Id":rid},timeout=30000)
            result["http_status"]=ack.status
            if ack.status!=202:
                result["error"]="IMPORT_OR_SEND_REJECTED:"+str(ack.status)+
                    ":"+(await ack.text())[:300]
                return 1
            payload=await ack.json()
            if payload.get("requestId")!=rid or payload.get("accepted") is False:
                result["error"]="INVALID_STATION_ACCEPTANCE"
                return 1
            snapshot=await common.sync(ctx)
            threads=snapshot.get("threads") or []
            target=next((t for t in threads if t.get("id")==tid),{})
            arts=target.get("codeArtifacts") or []
            result["import_registered"]=bool(
                any(a.get("importedUserSource") and a.get("title")=="index.html" for a in arts))
            result["imported_artifact_count"]=len(arts)
            last=None;trace=[];reply=None
            while time.perf_counter()-start<TIMEOUT:
                snapshot=await common.sync(ctx)
                current=safe_status(snapshot,tid)
                if current!=last:
                    trace.append({"elapsed_ms":int((time.perf_counter()-start)*1000),**current})
                    last=current
                found=common.committed(snapshot,prompt=PROMPT,thread_id=tid)
                if found:
                    reply=found[1]
                    result["committed_state"]=found[2]
                    break
                generation=snapshot.get("activeGeneration") or {}
                if generation.get("terminal") and generation.get("requestId")==rid:
                    result["terminal_without_answer"]=True
                    break
                await asyncio.sleep(1.7)
            result["timeline"]=trace[-45:]
            result["elapsed_ms"]=int((time.perf_counter()-start)*1000)
            if not reply:
                result["error"]="NO_COMMITTED_HTML"
                return 1
            result["response_chars"]=len(reply)
            result["response_sha256"]=hashlib.sha256(reply.encode()).hexdigest()
            (OUT/"synthetic-response.txt").write_text(reply)
            grade=common.evaluate({"check":"html_interactive"},reply)
            result["static_evaluation"]=grade
            try:
                html=extract_html(reply)
                result["html_document_count"]=len(re.findall(r"(?i)<!doctype\s+html",reply))
                ui=await evaluate_page(browser,html,True)
                result["chromium"]=ui
                result["preserves_change_id"]="id=\"change\"" in html or "id='change'" in html
                result["pass"]=bool(result["import_registered"] and
                    grade["status"]=="PASS_EVIDENCE" and ui["pass"] and
                    result["preserves_change_id"] and result["html_document_count"]==1)
            except Exception as exc:
                result["chromium_error"]=type(exc).__name__+":"+str(exc)[:180]
            return 0 if result["pass"] else 1
        except Exception as exc:
            result["error"]=type(exc).__name__+":"+str(exc)[:280]
            return 1
        finally:
            await ctx.close()
            await browser.close()
            (OUT/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
            print("SEEDED_HTML_RESULT",json.dumps({k:v for k,v in result.items()
                if k not in ("timeline","static_evaluation","chromium")},ensure_ascii=False),flush=True)
            if result.get("timeline"):
                print("SEEDED_HTML_PHASES",json.dumps(result["timeline"][-6:],ensure_ascii=False),flush=True)
if __name__=="__main__":
    sys.exit(asyncio.run(main()))
