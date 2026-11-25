#!/usr/bin/env python3
"""Read-only startup diagnostics; no credential contents or raw runtime logs."""
import ast,json,re,urllib.request,urllib.error
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
SPACE="kamiloki/Swyrlz"
FAILED="ef81d8a9cd9116db9572a7e35c756bce5bc66373"
api=HfApi()
def out(tag,obj):print(tag,json.dumps(obj,ensure_ascii=False),flush=True)
def read(n,r):return Path(hf_hub_download(SPACE,n,repo_type="space",revision=r)).read_text()
def inspect(n,s):
    t=ast.parse(s); lines=s.splitlines()
    needles=("FastAPI(","uvicorn.run","mount_gradio_app","import station","from station","app =","app=","__main__","_swrlz_execute_model_repair_v7","_swrlz_v14_health","_swrlz_local_browser_v14.install","include_router","/runtime-check","launch(")
    matches=[]
    for i,l in enumerate(lines):
        if any(k in l for k in needles) and len(matches)<80:
            matches.append({"line":i+1,"source":l[:220]})
    out("STARTUP_SOURCE",{"file":n,"lines":len(lines),"matches":matches,
          "topLevelFunctions":[{"name":x.name,"line":x.lineno} for x in t.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and ("swrlz" in x.name or x.name in ("main","launch"))][-25:]})
info=api.repo_info(SPACE,repo_type="space")
out("SPACE_METADATA",{"revision":info.sha,"sdk":getattr(info,"sdk",None),"cardAppFile":getattr(getattr(info,"card_data",None),"app_file",None)})
try:
    runtime=api.get_space_runtime(SPACE)
    out("SPACE_RUNTIME",{"stage":str(runtime.stage),"hardware":str(runtime.hardware)})
except Exception as e:out("RUNTIME_UNAVAILABLE",type(e).__name__)
for r in (str(info.sha),FAILED):
    names=set(api.list_repo_files(SPACE,repo_type="space",revision=r))
    out("SOURCE_TREE",{"revision":r,"startup":[n for n in sorted(names) if "/" not in n and (n.endswith(".py") or n in ("README.md","requirements.txt","packages.txt","Dockerfile"))]})
    md=read("README.md",r)
    out("README_CONFIG",{"revision":r,"config":[l for l in md.splitlines()[:40] if re.match(r"^(sdk|sdk_version|app_file|python_version|app_port|title):",l)]})
    for n in ("app.py","station.py","main.py","server.py"):
        if n in names:inspect(n,read(n,r))
    for n in ("packages.txt","requirements.txt"):
        if n in names:
            s=read(n,r)
            out("DEPENDENCY_LINES",{"revision":r,"file":n,"browser":[l for l in s.splitlines() if re.match(r"^\s*(chromium|bubblewrap|fonts-liberation|playwright|fastapi|gradio|uvicorn)\b",l,re.I)]})
# Read only bounded diagnostic categories, never raw logs.
for kind in ("build","run"):
    url="https://huggingface.co/api/spaces/"+SPACE+"/logs/"+kind
    try:
        with urllib.request.urlopen(url,timeout=5) as response:
            raw=response.read(65536).decode(errors="replace")
        patterns=["ModuleNotFoundError","ImportError","NameError","SyntaxError","Permission denied","Operation not permitted","No usable sandbox","Failed to create","chromium","bubblewrap","playwright","Error loading ASGI app","Application startup complete","Uvicorn running","ERROR:","Traceback"]
        out("LOG_CATEGORIES",{"kind":kind,"matches":{p:raw.lower().count(p.lower()) for p in patterns if p.lower() in raw.lower()}})
    except Exception as exc:out("LOG_ACCESS",{"kind":kind,"status":getattr(exc,"code",None),"error":type(exc).__name__})
for route in ("/api/html-project-agent-v12/runtime-check","/api/html-project-agent-v14/runtime-check","/openapi.json"):
    try:
        with urllib.request.urlopen("https://kamiloki-swyrlz.hf.space"+route,timeout=10) as r:
            raw=r.read(2_000_000);d=json.loads(raw)
        out("ROUTE",{"path":route,"status":200,"schema":d.get("schema"),"state":d.get("state"),"browserPaths":[p for p in d.get("paths",{}) if "browser" in p or "html-project-agent" in p]})
    except Exception as e:out("ROUTE",{"path":route,"status":getattr(e,"code",None),"error":type(e).__name__})
