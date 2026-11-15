#!/usr/bin/env python3
"""Read-only inspect live HF §C routing around explanation-only code prompts."""
from pathlib import Path
import ast,json,re
from huggingface_hub import HfApi,hf_hub_download
space="kamiloki/Swyrlz"
api=HfApi()
rev=api.repo_info(space,repo_type="space").sha
print("LIVE_SPACE_SHA",rev,flush=True)
for fname in ("brain_programming.py","qwen_coder_engine.py","lfm2_700m_engine.py","station.py"):
    try:
        source=Path(hf_hub_download(space,fname,repo_type="space",revision=rev)).read_text(encoding="utf-8")
        tree=ast.parse(source)
    except Exception as exc:
        print("SOURCE_UNAVAILABLE",fname,type(exc).__name__,str(exc)[:120],flush=True)
        continue
    print("FILE",fname,"lines",len(source.splitlines()),flush=True)
    for node in ast.walk(tree):
        if not isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):continue
        name=node.name
        selected=(fname=="brain_programming.py" and re.search(r"programming|intent|code|source|reply|turn|signal",name,re.I)
                  or fname=="qwen_coder_engine.py" and re.search(r"programming|candidate|code.*mode|response_mode|contract|route",name,re.I)
                  or fname=="lfm2_700m_engine.py" and re.search(r"programming|route|intent",name,re.I))
        if not selected:continue
        s=ast.get_source_segment(source,node) or ""
        if len(s)>11000:s=s[:11000]+"\n[TRUNCATED]"
        print("ROUTE_FN",json.dumps({"file":fname,"name":name,"start":node.lineno,"body":s},ensure_ascii=False),flush=True)
    if fname=="qwen_coder_engine.py":
        lines=source.splitlines()
        picks=[i for i,l in enumerate(lines) if re.search(r"CANDIDATE_NOT_APPLICABLE|CODE_DRAFT_SAVED|code validation|programming contract|codingTask|source_change_mode",l,re.I)]
        for i in picks[:40]:
            print("CODE_ROUTING_CONTEXT",json.dumps({"line":i+1,"content":"\n".join(f"{j+1}: {lines[j]}" for j in range(max(0,i-3),min(len(lines),i+5)))},ensure_ascii=False),flush=True)
print("AUDIT_COMPLETE",rev,flush=True)
