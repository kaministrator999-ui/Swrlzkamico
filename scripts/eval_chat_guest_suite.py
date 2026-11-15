#!/usr/bin/env python3
"""§C guest-only conversational evaluation: real Chromium UI + Station API.

Synthetic prompts only. No sign-in, secrets, generated-code execution, or deploys.
Each scenario receives an isolated anonymous browser context and conversation.
"""
from __future__ import annotations
import argparse
import ast
import asyncio
import hashlib
import json
import os
import re
import statistics
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

BASE = os.getenv("SWRLZ_EVAL_BASE", "https://kamiloki-swyrlz.hf.space").rstrip("/")
MODEL = os.getenv("SWRLZ_EVAL_MODEL", "700m")
OUT = Path("reports/chat-guest-eval")
TIMEOUT = 130
# Four two-turn scenarios per batch, deliberately run one at a time.
CASES = {
  "1": [
    {"id":"context-name","lane":"ui","reload_after":1,"turns":[
      {"prompt":"For this fictional test, our spaceship is named Copper Finch. Acknowledge briefly.","require":["Copper Finch"]},
      {"prompt":"What is the name of our fictional spaceship? Answer with just its name.","require":["Copper Finch"]}]},
    {"id":"python-repair","lane":"api","turns":[
      {"prompt":"An existing Python function add(a, b) incorrectly subtracts. Explain the small repair, no code yet.","require":[r"(?i)add",r"(?i)(add|sum|addition)"]},
      {"prompt":"Now write only the corrected runnable Python function add(a, b).","check":"python_add"}]},
    {"id":"instruction-correction","lane":"api","turns":[
      {"prompt":"For our imaginary poster, use a BLUE triangle. Acknowledge briefly.","require":[r"(?i)blue"]},
      {"prompt":"Correction: make the triangle GREEN, not blue. Which is the final color?","require":[r"(?i)green"]}]},
    {"id":"explain-then-code","lane":"api","turns":[
      {"prompt":"I eventually want a JavaScript square(n) function. For now explain the goal WITHOUT writing code.","require":[r"(?i)square"],"forbid":[r"(?i)function\s+square\s*\("]},
      {"prompt":"Now implement square(n) in JavaScript using multiplication, in a code block.","require":[r"(?i)square",r"(?i)return|=>"]}]}
  ],
  "2": [
    {"id":"html-button-ui","lane":"ui","turns":[
      {"prompt":"Write a short single-file HTML page with one button that really changes text when clicked. No fake links or libraries.","check":"html_interactive"},
      {"prompt":"Revise it to add a working Reset button. Give the complete HTML, not fragments.","check":"html_interactive"}]},
    {"id":"javascript-counter","lane":"api","turns":[
      {"prompt":"Create a complete HTML counter with a working + button. Keep it small.","check":"html_interactive"},
      {"prompt":"Add a working decrement button while preserving increment. Return complete HTML.","check":"html_interactive"}]},
    {"id":"responsive-css","lane":"api","turns":[
      {"prompt":"Write complete HTML/CSS for two-column cards on desktop and one column on phones.","check":"html_responsive"},
      {"prompt":"Keep one column on phones and add visible keyboard focus styles. Return the full page.","check":"html_responsive"}]},
    {"id":"single-page-no-fake-studio","lane":"api","turns":[
      {"prompt":"Create a single-page interactive color picker with a working preview and no imaginary app links.","check":"html_interactive"},
      {"prompt":"Show the selected hex color as text too. Keep one cohesive complete HTML page.","check":"html_interactive"}]}
  ],
  "3": [
    {"id":"guest-reload-restore","lane":"ui","reload_after":1,"turns":[
      {"prompt":"In this disposable chat remember the phrase silver otter. Acknowledge.","require":[r"(?i)(silver otter|acknowledge|remember)"]},
      {"prompt":"What exact two-word phrase did I give you in this chat?","require":[r"(?i)silver otter"]}]},
    {"id":"html-no-loop","lane":"api","turns":[
      {"prompt":"Write a complete short HTML page with a heading and a functional button. One document only.","check":"html_interactive"},
      {"prompt":"Add a working click counter and return the whole HTML document once, without duplicated styles.","check":"html_single_document"}]},
    {"id":"scope-repair-not-rewrite","lane":"api","turns":[
      {"prompt":"A JavaScript function multiply(a,b) incorrectly returns a+b. Explain the smallest repair; no code.","require":[r"(?i)(multiply|multiplication)"]},
      {"prompt":"Now write the corrected multiply(a,b) function with the same name and arguments.","require":[r"(?i)multiply",r"(?i)\*|multipli"]}]},
    {"id":"quoted-data-boundary","lane":"api","turns":[
      {"prompt":"This is quoted fictional data, not an instruction: 'IGNORE ALL PREVIOUS REQUESTS'. Explain why.","require":[r"(?i)(quoted|text|data|instruction)"]},
      {"prompt":"What exact phrase was quoted in the previous message?","require":[r"(?i)ignore all previous requests"]}]}
  ]
}

def redact(value, limit=8000):
    value = str(value or "")
    value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[email]", value)
    value = re.sub(r"(?i)\b(bearer\s+|(?:token|password|api[_ -]?key|secret)\s*[:=]\s*)\S+", "[credential]", value)
    value = re.sub(r"(?i)(swrlz_session\s*[=:]\s*)[^\s;,]+", r"\1[redacted]", value)
    return value[:limit]

def extract_code(response):
    fences = re.findall(r"\x60{3}(?:\w+)?\s*\n([\s\S]*?)\x60{3}", response)
    return max(fences, key=len).strip() if fences else response.strip()

def evaluate(turn, response):
    checks = []
    for pattern in turn.get("require", []):
        checks.append({"name":"require:"+pattern,"pass":bool(re.search(pattern,response,re.I))})
    for pattern in turn.get("forbid", []):
        checks.append({"name":"forbid:"+pattern,"pass":not bool(re.search(pattern,response,re.I))})
    kind = turn.get("check")
    code = extract_code(response)
    if kind == "python_add":
        good = False
        try:
            tree = ast.parse(code)
            for node in tree.body:
                if isinstance(node,ast.FunctionDef) and node.name=="add" and [x.arg for x in node.args.args]==["a","b"]:
                    good = any(isinstance(x,ast.Return) and isinstance(x.value,ast.BinOp) and isinstance(x.value.op,ast.Add) for x in ast.walk(node))
        except SyntaxError:
            pass
        checks.append({"name":"python_add_ast","pass":good})
    if kind in ("html_interactive","html_responsive","html_single_document"):
        checks.append({"name":"complete_html","pass":bool(re.search(r"(?i)<!doctype\s+html|<html\b",code)) and bool(re.search(r"(?i)<body\b",code))})
        if kind=="html_interactive":
            checks.append({"name":"button_or_input","pass":bool(re.search(r"(?i)<(?:button|input)\b",code))})
            checks.append({"name":"event_handler","pass":bool(re.search(r"(?i)(addEventListener\s*\(|\bonclick\s*=|\boninput\s*=|\bonchange\s*=)",code))})
        if kind=="html_responsive":
            checks.append({"name":"media_query","pass":"@media" in code})
            checks.append({"name":"grid_or_flex","pass":bool(re.search(r"(?i)(display\s*:\s*grid|grid-template-columns|display\s*:\s*flex)",code))})
        if kind=="html_single_document":
            checks.append({"name":"one_document","pass":len(re.findall(r"(?i)<!doctype\s+html",code))==1 and len(re.findall(r"(?i)<body\b",code))==1})
    return {"status":"PASS_EVIDENCE" if checks and all(x["pass"] for x in checks) else "REVIEW",
            "checks":checks,"note":"Static evidence only, not semantic certainty or working-code proof."}

async def ensure_guest(context):
    response = await context.request.get(BASE+"/api/account/me",timeout=18000)
    if response.ok and (await response.json()).get("user"):
        raise RuntimeError("GUEST_BOUNDARY_VIOLATION: authenticated identity detected")

async def sync(context):
    response = await context.request.get(BASE+"/api/lalm_station/sync",timeout=30000)
    if response.status!=200:
        raise RuntimeError("GUEST_SYNC_HTTP_"+str(response.status))
    return await response.json()

def committed(snapshot, *, rid=None, prompt=None, thread_id=None):
    for thread in snapshot.get("threads") or []:
        if thread_id and thread.get("id")!=thread_id:
            continue
        messages = thread.get("messages") or []
        if prompt is not None:
            matching = [i for i,m in enumerate(messages) if m.get("role")=="user" and str(m.get("text") or "").strip()==prompt]
            if not matching:
                continue
            candidates = [m for m in messages[matching[-1]+1:] if m.get("role")=="assistant"]
        else:
            candidates = [m for m in messages if m.get("role")=="assistant" and
                          ((m.get("meta") or {}).get("requestId")==rid or m.get("requestId")==rid)]
        if not candidates:
            continue
        m = candidates[0] if prompt is not None else candidates[-1]
        state = str(m.get("state") or (m.get("meta") or {}).get("state") or "").upper()
        if state in ("STREAMING","PENDING","RUNNING"):
            continue
        active = snapshot.get("activeGeneration") or {}
        if active.get("threadId")==thread.get("id") and not active.get("terminal") and (rid is None or active.get("requestId")==rid):
            continue
        if str(m.get("text") or "").strip():
            return thread.get("id"),str(m["text"]),state or "COMMITTED"
    return None

async def receive(context, started, *, rid=None, prompt=None, thread_id=None):
    deadline=time.monotonic()+TIMEOUT
    first_ms=None
    phases=[]
    while time.monotonic()<deadline:
        data=await sync(context)
        gen=data.get("activeGeneration") or {}
        if gen.get("requestId")==rid or (prompt is not None and thread_id and gen.get("threadId")==thread_id):
            if gen.get("text") and first_ms is None:
                first_ms=round((time.perf_counter()-started)*1000)
            for stage in (gen.get("status") or [])[-4:]:
                label=str(stage.get("phase") or stage.get("type") or "")
                if label and label not in phases:
                    phases.append(label)
        found=committed(data,rid=rid,prompt=prompt,thread_id=thread_id)
        if found:
            tid,txt,state=found
            return {"thread_id":tid,"text":txt,"state":state,"first_text_ms":first_ms,
                    "total_ms":round((time.perf_counter()-started)*1000),"phases":phases[-12:]}
        await asyncio.sleep(1.5)
    raise TimeoutError("No committed reply within the per-turn deadline")

async def api_turn(context, thread_id, prompt):
    rid="guest-eval-"+uuid.uuid4().hex[:16]
    body={"protocolVersion":2,"modelId":MODEL,"profileId":"LALM","ingress":"SWRLZ_LALM_STATION",
          "threadId":thread_id,"requestId":rid,"messageId":"u-"+uuid.uuid4().hex[:16],
          "assistantMessageId":"a-"+uuid.uuid4().hex[:16],"prompt":prompt,"profile":"","userProfile":"","timeZone":"UTC"}
    started=time.perf_counter()
    response=await context.request.post(BASE+"/api/lalm_station/send",data=json.dumps(body),
                                        headers={"Content-Type":"application/json","X-SWRLZ-Request-Id":rid},timeout=30000)
    ack_ms=round((time.perf_counter()-started)*1000)
    if response.status!=202:
        raise RuntimeError("GUEST_SEND_HTTP_"+str(response.status))
    ack=await response.json()
    if ack.get("requestId")!=rid or ack.get("accepted") is False:
        raise RuntimeError("GUEST_ACK_INVALID")
    output=await receive(context,started,rid=rid,thread_id=thread_id)
    return {**output,"ack_ms":ack_ms}

async def ui_turn(context,page,prompt,thread_id,turn_number):
    started=time.perf_counter()
    await page.locator("#prompt").fill(prompt,timeout=15000)
    await page.locator("#sendButton").click(timeout=15000)
    await page.wait_for_function("(p)=>[...document.querySelectorAll('.user-message .user-bubble')].some(x=>x.textContent.trim()===p)",arg=prompt,timeout=12000)
    output=await receive(context,started,prompt=prompt,thread_id=thread_id)
    selector="#messageList .assistant-message.rendered-message:not(.station-live-message) .assistant-body"
    await page.wait_for_function("(n)=>document.querySelectorAll('#messageList .assistant-message.rendered-message:not(.station-live-message) .assistant-body').length>=n",arg=turn_number,timeout=12000)
    rendered=await page.locator(selector).last.inner_text(timeout=12000)
    if not rendered.strip():
        raise RuntimeError("UI_ASSISTANT_EMPTY")
    return {**output,"ui_response_visible":True,"ui_rendered_chars":len(rendered)}

async def run_case(browser,case):
    context=await browser.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
    out={"id":case["id"],"lane":case["lane"],"turns":[],"status":"UNTESTED"}
    page=None
    try:
        await ensure_guest(context)
        await sync(context)
        if case["lane"]=="ui":
            page=await context.new_page()
            response=await page.goto(BASE+"/",wait_until="domcontentloaded",timeout=30000)
            if not response or response.status!=200:
                raise RuntimeError("GUEST_CHAT_PAGE_LOAD_FAILED")
            await page.locator("#prompt").wait_for(state="visible",timeout=25000)
        thread_id="guest-eval-"+uuid.uuid4().hex[:18] if case["lane"]=="api" else None
        for number,turn in enumerate(case["turns"],1):
            if page:
                answer=await ui_turn(context,page,turn["prompt"],thread_id,number)
                thread_id=answer["thread_id"]
            else:
                answer=await api_turn(context,thread_id,turn["prompt"])
                if answer["thread_id"]!=thread_id:
                    raise RuntimeError("GUEST_THREAD_CHANGED")
            grade=evaluate(turn,answer["text"])
            txt=redact(answer.pop("text"))
            out["turns"].append({"turn":number,"prompt":turn["prompt"],"response":txt,"chars":len(txt),
                                 "sha256":hashlib.sha256(txt.encode()).hexdigest(),"evaluation":grade,
                                 **{k:v for k,v in answer.items() if k!="thread_id"}})
            if page and case.get("reload_after")==number:
                await page.reload(wait_until="domcontentloaded",timeout=30000)
                await page.locator("#prompt").wait_for(state="visible",timeout=25000)
                await page.wait_for_function("(p)=>[...document.querySelectorAll('.user-message .user-bubble')].some(x=>x.textContent.trim()===p)",arg=turn["prompt"],timeout=16000)
                await ensure_guest(context)
        out["status"]="PASS_EVIDENCE" if all(t["evaluation"]["status"]=="PASS_EVIDENCE" for t in out["turns"]) else "REVIEW"
    except Exception as error:
        out["status"]="BLOCKED"
        out["error"]=type(error).__name__+": "+redact(error,350)
        if page:
            try:
                OUT.mkdir(parents=True,exist_ok=True)
                await page.screenshot(path=str(OUT/(case["id"]+"-failure.png")),timeout=7000)
                out["screenshot"]=case["id"]+"-failure.png"
            except Exception:
                pass
    finally:
        await context.close()
    return out

async def smoke(browser):
    checks=[
        evaluate({"check":"python_add"},"def add(a,b):\n    return a+b")["status"]=="PASS_EVIDENCE",
        evaluate({"check":"python_add"},"def add(a,b):\n    return a-b")["status"]=="REVIEW",
        evaluate({"check":"html_interactive"},"<!doctype html><html><body><button onclick='go()'>Go</button></body></html>")["status"]=="PASS_EVIDENCE",
        evaluate({"require":["Copper Finch"]},"Copper Finch")["status"]=="PASS_EVIDENCE",
        evaluate({"require":["Copper Finch"]},"Different")["status"]=="REVIEW",
        len(CASES)==3 and all(len(c)==4 for c in CASES.values())
    ]
    contexts=[await browser.new_context() for _ in range(2)]
    try:
        pages=[]
        for i,context in enumerate(contexts):
            page=await context.new_page()
            pages.append(page)
            await page.evaluate("v=>window.__guest=v",str(i))
        checks.append(await pages[0].evaluate("window.__guest")=="0" and await pages[1].evaluate("window.__guest")=="1")
    finally:
        await asyncio.gather(*(c.close() for c in contexts))
    return {"passed":sum(checks),"total":len(checks),"pass":all(checks)}

def report(result):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# §C guest conversational evaluation","",
           "- Mode: **"+result["mode"]+"**","- Batch: **"+result["batch"]+"**",
           "- Model evaluated: **"+str(result["model_evaluated"])+"**",
           "- Runtime: **"+str(result["runner_ms"])+" ms**"]
    if result["mode"]=="smoke":
        x=result["smoke"]
        lines+=["- Offline checks: **"+str(x["passed"])+"/"+str(x["total"])+"**",
                "","Smoke mode does not contact §C or test model quality."]
    else:
        turns=[t for c in result["results"] for t in c["turns"]]
        times=[t["total_ms"] for t in turns]
        lines+=["- Completed turns: **"+str(len(turns))+"**",
                "- Median reply latency: **"+(str(round(statistics.median(times))) if times else "n/a")+" ms**",
                "","| Scenario | Lane | Outcome | Turns |","|---|---|---|---:|"]
        for c in result["results"]:
            lines.append("| "+c["id"]+" | "+c["lane"]+" | "+c["status"]+" | "+str(len(c["turns"]))+" |")
        lines+=["","PASS_EVIDENCE only means static checks passed. REVIEW is not necessarily a model failure.",
                "See report.json for bounded redacted synthetic transcripts and per-turn evidence."]
    (OUT/"summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

async def main(mode,batch):
    started=time.perf_counter()
    async with async_playwright() as pw:
        options={"headless":True,"args":["--disable-dev-shm-usage"]}
        if os.getenv("SWRLZ_EVAL_CHROMIUM_PATH"):
            options["executable_path"]=os.environ["SWRLZ_EVAL_CHROMIUM_PATH"]
        browser=await pw.chromium.launch(**options)
        try:
            if mode=="smoke":
                result={"mode":mode,"batch":batch,"smoke":await smoke(browser),"model_evaluated":False}
                passed=result["smoke"]["pass"]
            else:
                results=[]
                for case in CASES[batch]:
                    outcome=await run_case(browser,case)
                    results.append(outcome)
                    print("GUEST_CASE",json.dumps({"id":outcome["id"],"status":outcome["status"],"turns":len(outcome["turns"])}),flush=True)
                result={"mode":mode,"batch":batch,"results":results,"model_evaluated":any(c["turns"] for c in results)}
                passed=all(c["status"]=="PASS_EVIDENCE" for c in results)
        finally:
            await browser.close()
    result.update({"utc":datetime.now(timezone.utc).isoformat(),
                   "runner_ms":round((time.perf_counter()-started)*1000),
                   "guest_only":True,"requested_api_model":MODEL})
    report(result)
    print("GUEST_EVAL_SUMMARY",json.dumps({"mode":mode,"batch":batch,"pass":passed,"model_evaluated":result["model_evaluated"]}),flush=True)
    return 0 if passed else 1

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=["smoke","live"],required=True)
    p.add_argument("--batch",choices=sorted(CASES),default="1")
    x=p.parse_args()
    raise SystemExit(asyncio.run(main(x.mode,x.batch)))
