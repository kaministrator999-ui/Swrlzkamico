"""Inspect source layout of the exact live Space revision without printing source text."""
from __future__ import annotations
import ast
import json
import os
import re
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download

TARGET="kamiloki/Swyrlz"
TARGET_FILES=("app.py","station.py","requirements.txt","chat/§wyrlz/index.html","chat/index.html","README.md")

def inspect_source(path, source):
    patterns = {
      "upstash":r"upstash|KV_REST_API|REDIS_REST",
      "redis":r"redis|valkey",
      "account_routes":r"account[_/-](?:google|state|thread|login)|/api/account",
      "browser_fetch":r"fetch\s*\(",
      "cross_origin_api":r"https?://[^/\s\"']+/api/",
      "proxy_forward":r"requests\.|httpx\.|urllib\.request",
      "iframe_embed":r"<iframe|iframe\.src",
      "login_google":r"google.*(?:sign|login|oauth)|oauth.*google",
      "cloud_persistence":r"blob|database|persist|durable|storage",
      "environment":r"os\.(?:getenv|environ)|process\.env",
    }
    info = {
      "filename":path,
      "line_count":len(source.splitlines()),
      "pattern_flags":{name:bool(re.search(p,source,re.I)) for name,p in patterns.items()},
    }
    if path.endswith(".py"):
        try:
            tree=ast.parse(source)
            funcs=[x.name for x in tree.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))]
            info["root_functions"]=[x for x in funcs if any(k in x.lower() for k in ("auth","login","account","redis","storage","session","chat","transcript","init"))][:35]
            info["fastapi_route_path_literals"] = sorted(set(re.findall(r'@(?:app|server|station_app|api)\.(?:get|post|put|delete|route)\(\s*[\"\']([^\"\']{1,100})',source)))[:100]
        except SyntaxError:
            info["ast"] = "syntax-unavailable"
    elif path.endswith(".html"):
        info["relative_api_strings"] = sorted(set(re.findall(r"/api/[a-zA-Z0-9/_-]{3,100}",source)))[:60]
        info["contains_absolute_https_origin"] = bool(re.search(r"https://[a-zA-Z0-9.-]+/api",source))
    return info

def main():
    token=os.getenv("HF_TOKEN","")
    if not token:
        raise RuntimeError("Missing HF_TOKEN")
    api=HfApi(token=token)
    info=api.repo_info(TARGET,repo_type="space")
    names=set(api.list_repo_files(TARGET,repo_type="space",revision=info.sha))
    result=[]
    for filename in TARGET_FILES:
        if filename not in names:
            continue
        raw=Path(hf_hub_download(repo_id=TARGET,filename=filename,repo_type="space",revision=info.sha,token=token)).read_text("utf-8")
        result.append(inspect_source(filename,raw))
    print("SWRLZ_LIVE_STORAGE_LAYOUT "+json.dumps({"revision":info.sha,"files":result,"operation":"READ_ONLY_NO_SECRET_VALUES"},ensure_ascii=True))

if __name__=="__main__":
    main()
