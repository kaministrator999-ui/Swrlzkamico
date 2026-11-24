"""Read only the active account-store source structure; never print secret values."""
from __future__ import annotations
import ast, json, os, re
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download

TARGET="kamiloki/Swyrlz"

def main():
    token=os.environ["HF_TOKEN"]
    api=HfApi(token=token)
    info=api.repo_info(TARGET,repo_type="space")
    paths=api.list_repo_files(TARGET,repo_type="space",revision=info.sha)
    matches=[p for p in paths if re.search(r"account|redis|valkey|storage|github_connection",p,re.I) and p.endswith(".py")]
    report=[]
    for path in matches:
        if path.count("/") > 2: continue
        source=Path(hf_hub_download(TARGET,path,repo_type="space",revision=info.sha,token=token)).read_text("utf-8")
        tree=ast.parse(source)
        funcs=[]
        for node in tree.body:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                funcs.append({"name":node.name,"first":node.lineno,"last":node.end_lineno})
        envs=sorted(set(re.findall(r"['\"]((?:UPSTASH|SWRLZ|KV)_[A-Z_0-9]+)['\"]",source)))
        envs=[x for x in envs if any(s in x for s in ("REDIS","KV_","VALKEY","UPSTASH"))]
        lines=source.splitlines()
        excerpts=[]
        for i,line in enumerate(lines):
            if re.search(r"_redis|_config|UPSTASH|REDIS|rediss|requests\.post|redis\.|_key|expire|scan|ttl|parse",line,re.I):
                # Print source *shape* only; mask full HTTP/Redis URIs, long string literals.
                safe=line.strip()[:160]
                safe=re.sub(r"https?://[^'\"\s]+|rediss?://[^'\"\s]+","[uri omitted]",safe)
                safe=re.sub(r"(['\"])[^'\"]{28,}\1","[literal omitted]",safe)
                excerpts.append({"line":i+1,"shape":safe})
        report.append({"path":path,"lines":len(lines),"functions":funcs[:100],
                       "redis_environment_names":envs,"selected_source_shapes":excerpts[:150]})
    print("SWRLZ_ACTUAL_ACCOUNT_STORE "+json.dumps({"revision":info.sha,"report":report,
        "operation":"READ_ONLY_SOURCE","secrets": "not retrieved"},ensure_ascii=True))

if __name__=="__main__": main()
