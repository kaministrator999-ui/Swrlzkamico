#!/usr/bin/env python3
"""Read-only audit of the live Hugging Face repair runtime and HTML handoff."""
from __future__ import annotations
import ast
import json
import re
from pathlib import Path

def main():
    from huggingface_hub import HfApi, hf_hub_download
    repo = "kamiloki/Swyrlz"
    api = HfApi()
    rev = str(api.repo_info(repo, repo_type="space").sha)
    files = set(api.list_repo_files(repo,repo_type="space",revision=rev))
    print("REPAIR_V7_SPACE_REVISION",rev,flush=True)
    for name in ("station.py","html_project_agent_runtime_v1.py","html_project_agent_v1.py","github_html_project_handoff_v1.py","html_project_repair_v1.py"):
        if name not in files:
            print("REPAIR_V7_MODULE_ABSENT",name,flush=True)
            continue
        src = Path(hf_hub_download(repo,name,repo_type="space",revision=rev)).read_text()
        ast.parse(src,filename=name)
        lines = src.splitlines()
        terms = ("NOVERIFIEDHTMLCODEARTIFACT","htmlProjectIntent","htmlProject","handoff","_swrlz_model_repair","github_html","endswith(","frozenset(","TEXT_EXTENSIONS","_coder_generate", "workstation")
        idx=[i for i,line in enumerate(lines) if any(t.lower() in line.lower() for t in terms)]
        if name=="station.py":
            idx=[i for i in idx if i>1200 and i<3700]
        selected=idx[:110]
        records=[]
        for i in selected:
            excerpt=[f"{j+1}: {lines[j][:230]}" for j in range(max(0,i-3),min(len(lines),i+5))]
            records.append({"line":i+1,"excerpt":excerpt})
        print("REPAIR_V7_SOURCE_MATCHES",json.dumps({"file":name,"total":len(idx),"items":records},ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
