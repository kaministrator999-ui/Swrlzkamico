"""Live synthetic guest regression suite; no private user sessions or external actions."""
import http.cookiejar, urllib.request, urllib.parse, uuid, json, time, re, sys, statistics
BASE="http://127.0.0.1:8766"
def session():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())), "ovh-qa-"+uuid.uuid4().hex
def exact(x):
    return lambda s: s.strip().strip(".!").casefold()==x.casefold()
def has(*words):
    return lambda s: all(w.casefold() in s.casefold() for w in words)
def short(s): return 0<len(s)<=600
def lines3(s): return len([x for x in s.splitlines() if re.match(r"^\s*[123][.)]\s",x)])==3
def run_case(label,prompt,check,ctx=None):
    op,tid=ctx or session()
    rid=uuid.uuid4().hex
    body={"modelId":"700m","prompt":prompt,"threadId":tid,"requestId":rid,"profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    start=time.monotonic(); first=None; progress=None; profile=None; parts=[]; terminal=None; error=None; tokens=None; kept=None
    try:
        req=urllib.request.Request(BASE+"/api/lalm_station/send",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
        with op.open(req,timeout=10) as r: r.read()
        with op.open(BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid}),timeout=70) as r:
            for raw in r:
                event=json.loads(raw); kind=event.get("type")
                if kind=="STATUS":
                    if progress is None:progress=round(time.monotonic()-start,3)
                    if event.get("phase")=="OVH_PREFILL_PROFILE":profile=event.get("reason")
                if kind=="DELTA" and event.get("text"):
                    if first is None:first=round(time.monotonic()-start,2)
                    parts.append(str(event["text"]))
                if kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                    terminal=kind;break
                if time.monotonic()-start>75: raise TimeoutError("case deadline")
        with op.open(BASE+"/api/lalm_station/sync",timeout=10) as r:
            active=json.load(r).get("activeGeneration") or {}
        budget=active.get("contextBudget") or {};tokens=budget.get("estimatedInputTokens");kept=budget.get("historyMessagesKept")
        if terminal=="FAILED": error=next((x.get("reason") for x in reversed(active.get("status",[])) if x.get("phase")=="FAILED"),"failed")
    except Exception as e:
        error=type(e).__name__+": "+str(e)[:160]
        # Cancel only our own synthetic request. The server checks session ownership.
        try:
            req=urllib.request.Request(BASE+"/api/lalm_station/cancel",data=json.dumps({"requestId":rid}).encode(),headers={"Content-Type":"application/json"},method="POST")
            with op.open(req,timeout=5) as r:r.read()
        except Exception:pass
    answer="".join(parts)
    ok=terminal in ("COMPLETE","COMPLETED") and bool(answer) and check(answer)
    receipt={"case":label,"profile":profile,"tokens":tokens,"historyKept":kept,"first":first,"progress":progress,"total":round(time.monotonic()-start,2),"terminal":terminal,"accept":ok,"slow":first is None or first>20,"answer":answer[:500],"error":error}
    print("SWRLZ_EXTENDED "+json.dumps(receipt,ensure_ascii=False),file=sys.stderr,flush=True)
    return receipt
def main():
    rows=[]; chain=session()
    cases=[
      ("greet","Hey there!",short,chain),
      ("natural","I finally got some time to relax after work.",short,chain),
      ("name_fixture","For this test, my favorite color is teal. Reply OK.",exact("OK"),chain),
      ("recall","What is my favorite color? Reply with just the color.",exact("teal"),chain),
      ("correction","Actually, it's purple now. Reply OK.",exact("OK"),chain),
      ("recall_corrected","What is my favorite color now? Reply with just the color.",exact("purple"),chain),
      ("math_followup","What is 17 * 6? Reply with just the number.",exact("102"),chain),
      ("negative_math","-12 + 7",lambda s: bool(re.search(r"(?<!\d)-5(?!\d)",s)),None),
      ("decimal_math","2.5 * 4",lambda s: bool(re.search(r"(?<!\d)10(?!\d)",s)),None),
      ("definition","What is DNS? In one sentence.",has("domain","name"),None),
      ("factual","Why is ice less dense than liquid water? One sentence.",lambda s: bool(re.search(r"hydrogen|lattice|structure",s,re.I)),None),
      ("compare","In one sentence, compare RAM and storage.",lambda s: bool(re.search(r"volatile|temporary|power",s,re.I)) and bool(re.search(r"storage|persistent",s,re.I)),None),
      ("format","Give me exactly 3 numbered examples of fruits. No introduction.",lines3,None),
      ("translation","Translate 'good morning' into Spanish. Only the translation.",exact("buenos días"),None),
      ("code_py","Write a Python function triple(x) that returns x multiplied by 3. Return only code.",lambda s: bool(re.search(r"def\s+triple\s*\(\s*x\s*\)",s)) and bool(re.search(r"return\s+(?:x\s*\*\s*3|3\s*\*\s*x|x\s*\+\s*x\s*\+\s*x)",s)),None),
      ("code_js","Write a JavaScript function add(a, b) that returns their sum. Return only code.",lambda s: bool(re.search(r"function\s+add\s*\(\s*a\s*,\s*b\s*\)",s)) and bool(re.search(r"return\s+a\s*\+\s*b",s)),None),
      ("banter","That was actually pretty funny lol",short,chain),
      ("unknown","What is the serial number of my phone? One sentence.",lambda s: bool(re.search(r"don't|do not|cannot|can't|not have|unknown|not know|not provided|not access|unable",s,re.I)),None),
    ]
    for label,prompt,check,ctx in cases:
        rows.append(run_case(label,prompt,check,ctx))
    valid=[r["first"] for r in rows if r["first"] is not None]
    print("SWRLZ_EXTENDED_SUMMARY "+json.dumps({"cases":len(rows),"accepted":sum(r["accept"] for r in rows),"slow":sum(r["slow"] for r in rows),"medianFirst":statistics.median(valid) if valid else None,"failures":[r["case"] for r in rows if not r["accept"]],"slowCases":[r["case"] for r in rows if r["slow"]]}),file=sys.stderr,flush=True)
if __name__=="__main__":main()
