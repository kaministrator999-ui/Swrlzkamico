#!/usr/bin/env python3
"""Read-only §C Qwen3.5-9B real coding-quality and latency benchmark.

Anonymous, fresh synthetic sessions; no Space writes or paid hardware.
Function outputs are tested in short-lived isolated processes; only synthetic
code previews and result summaries appear in CI logs.
"""
from __future__ import annotations
import ast, hashlib, http.cookiejar, json, os, re, subprocess, sys
import tempfile, time, urllib.parse, urllib.request, uuid

BASE = "https://kamiloki-swyrlz.hf.space"
HEAD = {"User-Agent":"Swyrlz-Live-Coding-Quality-Speed-20261113",
        "Cache-Control":"no-cache"}
CASES = (
    {
      "id":"python_square",
      "language":"python", "function":"square",
      "prompt":"Write a short Python function named square(n) that returns n squared. Include one example call.",
      "tests":[ [[[3],9]], [[[-4],16]], [[[0],0]], [[[1.5],2.25]] ],
    },
    {
      "id":"python_repair",
      "language":"python", "function":"square",
      "prompt":("Fix this Python function while preserving its name and argument. "
                "square(3) must return 9. Return corrected code.\n"
                "def square(n):\n    return n + n"),
      "tests":[ [[[3],9]], [[[4],16]], [[[-4],16]], [[[0],0]] ],
    },
    {
      "id":"python_prime",
      "language":"python", "function":"is_prime",
      "prompt":("Implement Python function is_prime(n), returning a boolean. "
                "Handle negative numbers, 0, 1, primes and composites. "
                "Return complete Python code and one example."),
      "tests":[ [[[-3],False]], [[[0],False]], [[[1],False]], [[[2],True]],
               [[[3],True]], [[[4],False]], [[[9],False]], [[[49],False]],
               [[[97],True]], [[[121],False]], [[[9973],True]] ],
    },
    {
      "id":"python_intervals",
      "language":"python", "function":"merge_intervals",
      "prompt":("Implement a Python function merge_intervals(intervals) returning "
                "a newly sorted list of merged [start,end] pairs. Merge overlapping "
                "or touching intervals, handle empty input, and do not mutate the "
                "input. Provide complete runnable code."),
      "tests":[ [[[[]],[]]], [[[[[1,3],[2,6],[8,10],[15,18]]],[[1,6],[8,10],[15,18]]]],
                [[[[[1,4],[4,5]]],[[1,5]]]],
                [[[[[5,7],[1,2],[3,4]]],[[1,2],[3,4],[5,7]]]],
                [[[[[1,10],[2,3]]],[[1,10]]]] ],
      "noMutation": True,
    },
    {
      "id":"javascript_palindrome",
      "language":"javascript", "function":"isPalindrome",
      "prompt":("Write a complete JavaScript function isPalindrome(text) that returns "
                "true when text is a palindrome ignoring case and non-alphanumeric "
                "characters. Include one example. No libraries."),
      "tests":[ [[["A man, a plan, a canal: Panama"],True]],
                [[["race a car"],False]], [[[""],True]],
                [[["No 'x' in Nixon"],True]], [[["12321"],True]],
                [[["hello"],False]] ],
    },
)

def emit(label, data):
    print(label+" "+json.dumps(data, ensure_ascii=False, sort_keys=True), flush=True)

def ready():
    with urllib.request.urlopen(urllib.request.Request(
            BASE+"/api/hf/qwen35-ready", headers=HEAD), timeout=22) as resp:
        return json.load(resp)

def probe(case):
    opener=urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    rid=str(uuid.uuid4())
    thread="swrlz-live-quality-"+str(uuid.uuid4())
    t0=time.monotonic()
    req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
        data=json.dumps({"modelId":"700m","prompt":case["prompt"],"threadId":thread,
            "requestId":rid,"profileId":"LALM","profile":"","userProfile":"",
            "timeZone":"UTC"}).encode("utf-8"),
        headers={**HEAD,"Content-Type":"application/json"})
    with opener.open(req,timeout=35) as response:
        if response.status!=202:
            raise RuntimeError("Synthetic request not accepted")
        response.read()
    accepted=round(time.monotonic()-t0,3)
    chunks=[]
    first=None
    terminal=None
    phases=[]
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    with opener.open(urllib.request.Request(url,headers=HEAD),timeout=255) as response:
        for raw in response:
            if time.monotonic()-t0>245:
                raise TimeoutError("Model response exceeded live coding benchmark limit")
            try: ev=json.loads(raw)
            except (ValueError,UnicodeError): continue
            kind=ev.get("type")
            if kind=="STATUS":
                phases.append(str(ev.get("phase") or ""))
            elif kind=="DELTA":
                text=str(ev.get("text") or "")
                if text and first is None:first=round(time.monotonic()-t0,3)
                chunks.append(text)
            elif kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind
                break
    wall=round(time.monotonic()-t0,3)
    reply="".join(chunks)
    # Only this test's disposable cookie-scoped session. No personal records.
    with opener.open(urllib.request.Request(
            BASE+"/api/lalm_station/sync",headers=HEAD),timeout=25) as response:
        snapshot=json.load(response)
    active=snapshot.get("activeGeneration") or {}
    if str(active.get("requestId") or "")!=rid:
        raise RuntimeError("Returned session request does not match synthetic test")
    budget=active.get("contextBudget") or {}
    attempts=active.get("candidateAttempts") or []
    validation=active.get("candidateValidation") or {}
    gen=active.get("generationTelemetry") or {}
    return {
        "id":case["id"],"language":case["language"],
        "acceptedSec":accepted,"firstTextSec":first,"totalSec":wall,
        "terminal":terminal,"outputChars":len(reply),
        "coderAutoRoute":"CODER_AUTO_ROUTE" in phases,
        "contextTokens":budget.get("estimatedInputTokens"),
        "systemTokens":(budget.get("tokenBreakdown") or {}).get("system"),
        "historyMessagesKept":budget.get("historyMessagesKept"),
        "candidateStatus":validation.get("status"),
        "firstNativeTokenMs":attempts[-1].get("firstTokenLatencyMs") if attempts else None,
        "generationMs":gen.get("totalCandidateGenerationMs"),
        "response":reply,
    }

def fenced(text,langs):
    delim=chr(96)*3
    blocks=re.findall(re.escape(delim)+r"[ \t]*(?:[^\n]*)\n(.*?)"+
                      re.escape(delim),text,flags=re.S)
    matching=[]
    # Markdown fences are preferred, but plain code is also acceptable.
    for block in blocks:
        if block.strip():matching.append(block.strip())
    matching.append(text.strip())
    return matching

def extract_py(reply, function):
    errors=[]
    for candidate in fenced(reply,("python","py")):
        try: tree=ast.parse(candidate)
        except SyntaxError as err:
            errors.append("syntax_error")
            continue
        funcs=[node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))]
        if any(node.name==function for node in funcs):
            return candidate
        errors.append("requested_function_not_found")
    raise ValueError("No extractable Python function named "+function+
                     " ("+",".join(sorted(set(errors)))+")")

PY_TEST_RUNNER=r'''
import ast,builtins,copy,json,resource,sys
resource.setrlimit(resource.RLIMIT_CPU,(3,3))
resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
case=json.loads(sys.stdin.read())
tree=ast.parse(case["source"])
allowed={"math","typing","collections","itertools","functools","bisect","re"}
body=[]
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
        body.append(node)
    elif isinstance(node,(ast.Import,ast.ImportFrom)):
        mod=(node.module if isinstance(node,ast.ImportFrom) else node.names[0].name)
        if mod.split(".")[0] not in allowed: raise RuntimeError("Disallowed import")
        body.append(node)
for node in ast.walk(ast.Module(body=body,type_ignores=[])):
    if isinstance(node,(ast.Global,ast.Nonlocal)):raise RuntimeError("Unsafe scope")
    if isinstance(node,ast.Attribute) and node.attr.startswith("__"):
        raise RuntimeError("Unsafe attribute")
    if isinstance(node,ast.Name) and node.id in {"eval","exec","open","input","breakpoint","globals","locals","vars","__import__"}:
        raise RuntimeError("Unsafe operation")
def safe_import(name,globals=None,locals=None,fromlist=(),level=0):
    if name.split(".")[0] not in allowed:raise ImportError("Module disallowed")
    return builtins.__import__(name,globals,locals,fromlist,level)
allow=("range","len","sum","sorted","enumerate","min","max","list","dict",
       "set","tuple","int","str","bool","float","abs","all","any","zip",
       "isinstance","reversed","map","filter","round","Exception",
       "ValueError","TypeError","IndexError","ZeroDivisionError","object")
permitted={k:getattr(builtins,k) for k in allow}
permitted["__import__"]=safe_import
g={"__builtins__":permitted,"__name__":"__synthetic_test__"}
exec(compile(ast.Module(body=body,type_ignores=[]),"<model-response>","exec"),g)
fn=g.get(case["function"])
if not callable(fn):raise RuntimeError("Missing requested function")
results=[]
for args,expect in case["tests"]:
    cloned=copy.deepcopy(args)
    observed=fn(*cloned)
    passed=observed==expect
    if case.get("noMutation") and cloned!=args: passed=False
    results.append({"ok":passed,"input":args,"expected":expect,
                    "observed":observed,"mutated":cloned!=args})
print(json.dumps({"tests":results}))
'''

def python_tests(source,case):
    payload={"source":source,"function":case["function"],
             "tests":[item[0] for item in case["tests"]],
             "noMutation":case.get("noMutation",False)}
    with tempfile.TemporaryDirectory(prefix="swrlz-synthetic-python-") as cwd:
        proc=subprocess.run([sys.executable,"-I","-S","-c",PY_TEST_RUNNER],
            cwd=cwd, input=json.dumps(payload),encoding="utf-8",
            capture_output=True,timeout=8,env={"PYTHONDONTWRITEBYTECODE":"1"})
    if proc.returncode:raise RuntimeError("Isolated code execution: "+
               proc.stderr.splitlines()[-1][:180] if proc.stderr else "Child returned nonzero")
    return json.loads(proc.stdout)["tests"]

JS_RUNNER=r'''
const vm=require("vm"), fs=require("fs");
const data=JSON.parse(fs.readFileSync(0,"utf8"));
const source=data.source;
if (/\b(?:require|import|process|fetch|eval|Function|globalThis|module|exports)\b|__/.test(source))
  throw new Error("Unsafe external runtime dependency");
const sandbox=vm.createContext(Object.create(null));
vm.runInContext(source,sandbox,{timeout:1000});
const tests=[];
for (const [args,expect] of data.tests) {
 const call="isPalindrome("+JSON.stringify(args[0])+")";
 const observed=vm.runInContext(call,sandbox,{timeout:1000});
 tests.push({ok:observed===expect,input:args,expected:expect,observed});
}
console.log(JSON.stringify({tests}));
'''

def javascript_tests(reply,case):
    candidates=fenced(reply,("javascript","js"))
    best=next((s for s in candidates if
              re.search(r"\b(?:function\s+isPalindrome\b|(?:const|let|var)\s+isPalindrome\b)",s)),None)
    if best is None:raise RuntimeError("Requested JS function not extractable")
    with tempfile.TemporaryDirectory(prefix="swrlz-synthetic-js-") as cwd:
        file=os.path.join(cwd,"candidate.js")
        with open(file,"w",encoding="utf-8") as f:f.write(best)
        check=subprocess.run(["node","--check",file],capture_output=True,
                text=True,timeout=5,cwd=cwd)
        if check.returncode:raise RuntimeError("JavaScript syntax invalid: "+
                                             check.stderr[-160:])
        data={"source":best,"tests":[item[0] for item in case["tests"]]}
        result=subprocess.run(["node","-e",JS_RUNNER],input=json.dumps(data),
                  capture_output=True,text=True,timeout=8,cwd=cwd)
        if result.returncode:
            raise RuntimeError("JavaScript behavior test failed: "+result.stderr[-160:])
        return json.loads(result.stdout)["tests"]

def score(case, result):
    response=result.pop("response")
    result["responseHash"]=hashlib.sha256(response.encode()).hexdigest()[:12]
    result["codePreview"]=""
    if result["terminal"] not in ("COMPLETE","COMPLETED"):
        result["quality"]={"passed":0,"total":len(case["tests"]),
                           "reason":"No complete response"}
        return result
    try:
        if case["language"]=="python":
            source=extract_py(response,case["function"])
            results=python_tests(source,case)
        else:
            results=javascript_tests(response,case)
            source=next((s for s in fenced(response,("js",)) if "isPalindrome" in s),response)
        passed=sum(x["ok"] for x in results)
        result["quality"]={"passed":passed,"total":len(results),
            "failedCases":[x for x in results if not x["ok"]][:5]}
        result["codePreview"]=source[:1200]
    except (ValueError,RuntimeError,subprocess.TimeoutExpired,json.JSONDecodeError) as exc:
        result["quality"]={"passed":0,"total":len(case["tests"]),
            "reason":type(exc).__name__+": "+str(exc)[:240]}
        result["codePreview"]=response[:600]
    return result

def main():
    head=ready()
    emit("LIVE_CODER_READINESS",{k:head.get(k) for k in (
          "model","ready","cpuCapacity","decodeThreads","batchThreads",
          "batchSize","microBatchSize","profile")})
    if (head.get("ready"),head.get("model"),head.get("cpuCapacity"))!=(True,"qwen3.5-9b",16):
        raise RuntimeError("Expected resident Qwen3.5-9B with 16 CPU quota")
    summary=[]
    for case in CASES:
        try:
            result=score(case,probe(case))
            emit("LIVE_CODER_TEST",result)
            summary.append(result)
        except Exception as exc:
            entry={"id":case["id"],"errorType":type(exc).__name__,
                   "error":str(exc)[:230]}
            emit("LIVE_CODER_TEST_ERROR",entry)
            summary.append(entry)
    counted=[s for s in summary if "quality" in s]
    passed=sum(1 for s in counted if
               s["quality"]["passed"]==s["quality"]["total"])
    emit("LIVE_CODER_SUMMARY",{
        "cases":len(CASES),"completed":len(counted),"fullyPassed":passed,
        "perCase":[{"id":s["id"],"firstTextSec":s.get("firstTextSec"),
                    "totalSec":s.get("totalSec"),"quality":s.get("quality"),
                    "coderAutoRoute":s.get("coderAutoRoute"),
                    "candidateStatus":s.get("candidateStatus")}
                   for s in summary],
        "sourceMutated":False,"paidHardwareChanged":False})
    if not counted:
        raise RuntimeError("No live coding tests completed")
if __name__=="__main__":
    main()
