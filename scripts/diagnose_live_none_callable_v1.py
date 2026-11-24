#!/usr/bin/env python3
"""Print bounded production §C dispatcher source and callable resolution evidence.

Read-only: never logs prompts, users, tokens, or source contents outside
selected station.py function excerpts. Current HF Space revision is authoritative.
"""
from __future__ import annotations
import ast,json,os
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
SPACE="kamiloki/Swyrlz"
api=HfApi(token=os.getenv("HF_TOKEN") or None)
rev=str(api.repo_info(SPACE,repo_type="space").sha)
s=Path(hf_hub_download(SPACE,"station.py",repo_type="space",revision=rev,token=os.getenv("HF_TOKEN") or None)).read_text()
tree=ast.parse(s)
lines=s.splitlines()
for f in ast.walk(tree):
    if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name=="_run":
        print("RUN_LINE_RANGE",f.lineno,f.end_lineno)
        for n in range(f.lineno,min(f.lineno+115,f.end_lineno+1)):
            txt=lines[n-1]
            if "prompt" in txt or "token" in txt.lower():continue
            print("STATION_RUN_SOURCE",n,txt[:250])
    if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)) and f.name=="dispatch":
        print("DISPATCH_DEFINITION",f.lineno,f.end_lineno)
        for n in range(f.lineno,min(f.end_lineno+1,f.lineno+95)):
            txt=lines[n-1]
            if "prompt" in txt or "token" in txt.lower():continue
            print("DISPATCH_SOURCE",n,txt[:250])
for name in ("_generate","_stock_generate","_large_generate","_coder_generate","dispatch"):
    occurrences=[]
    for n,line in enumerate(lines,1):
        if name in line and n<1450 and ("=" in line or "import " in line):
            occurrences.append((n,line[:170]))
    print("CALLABLE_BINDINGS",name,json.dumps(occurrences[-12:]))
print("SOURCE_REVISION",rev)
