"""Read-only cost-driver audit of live Redis and chat state code.

Reports source-level call paths and file counts only, never environment values
or Redis contents. Source lines are emitted only for selected public Python methods.
"""
from __future__ import annotations
import ast
import json
import os
import re
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download

SPACE="kamiloki/Swyrlz"
FILES=["station.py","account_chat_store.py","github_connection.py",
       "account_profile_store.py","chatgpt_account_memory.py",
       "chatgpt_archive.py","account_rapport_store.py","account_lore_store.py",
       "account_proposal_store.py"]
NEEDED={
 "station.py":{"_persist_chat_snapshot","_restore_chat_from_store","_refresh_account_chat","_chat_document","_account_session","chat","_session"},
 "account_chat_store.py":{"_config","configured","load_chat","save_chat","load_login","save_login","_native_chat_parts","_decode_native_chat"},
 "github_connection.py":{"_redis","_settings","_config"},
}

def main():
    api=HfApi(token=os.environ["HF_TOKEN"])
    info=api.repo_info(SPACE,repo_type="space")
    paths=set(api.list_repo_files(SPACE,repo_type="space",revision=info.sha))
    entries=[]
    for name in FILES:
        if name not in paths:continue
        source=Path(hf_hub_download(SPACE,name,repo_type="space",revision=info.sha,token=api.token)).read_text("utf-8")
        lines=source.splitlines()
        tree=ast.parse(source)
        call_counts={}
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                fn = ast.unparse(node.func)
                if fn in ("gh._redis","_redis","_persist_chat_snapshot","_restore_chat_from_store",
                          "account_chat_store.load_chat","account_chat_store.save_chat",
                          "_refresh_account_chat","account_chat_store.load_login",
                          "account_chat_store.save_login"):
                    call_counts[fn]=call_counts.get(fn,0)+1
        targets=[]
        for n in tree.body:
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
                if n.name in NEEDED.get(name,set()):
                    fragment="\n".join(f"{i+1}: {lines[i]}" for i in range(n.lineno-1,n.end_lineno))
                    # Only source (never dynamic environment values); mask long literal credentials as defense.
                    fragment=re.sub(r"(rediss?://|https?://)[^'\"\\s]+","[URL redacted]",fragment)
                    targets.append({"name":n.name,"line":n.lineno,"code":fragment[:17000]})
        keywords={}
        for phrase,pattern in {
            "readsEntireState":r"load_chat|_restore_chat_from_store",
            "writesEntireState":r"save_chat|_persist_chat_snapshot",
            "focusEvents":r"focus|visibilitychange",
            "pollLoops":r"while\s+True|setInterval|asyncio\.sleep",
            "compressesState":r"gzip|zlib|compress",
            "storesLargeData":r"json\.dumps|base64\.b64encode",
            "redisGets":r"gh\._redis\s*\([^,\n]+,\s*['\"]GET['\"]",
            "redisSets":r"gh\._redis\s*\([^,\n]+,\s*['\"]SET['\"]",
            "redisEvals":r"gh\._redis\s*\([^,\n]+,\s*['\"]EVAL['\"]",
        }.items():
            keywords[phrase]=len(re.findall(pattern,source,re.I))
        entries.append({"file":name,"totalLines":len(lines),"callCounts":call_counts,
                        "keywordCounts":keywords,"functions":targets})
    print("SWRLZ_REDIS_TRAFFIC_CODE_AUDIT "+json.dumps({
      "revision":info.sha,"operation":"READ_ONLY_SOURCE_NO_REDIS_CALLS",
      "files":entries},ensure_ascii=True))

if __name__=="__main__":main()
