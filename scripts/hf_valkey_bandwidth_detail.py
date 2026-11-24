"""Read-only targeted source audit of live account/history traffic.

Outputs capped source surrounding relevant call sites, constant values and
high-volume route triggers, not any user data or environment secret values.
"""
import ast, json, os, re
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download
SPACE="kamiloki/Swyrlz"
PATHS=("station.py","account_chat_store.py","chatgpt_archive.py",
       "chatgpt_account_memory.py","github_connection.py","chat/§wyrlz/index.html")
KEYS=("CHAT_CHUNK_BYTES","CHAT_MAX_RAW","CHAT_MAX_CIPHER",
      "CHAT_MAX_CHUNKS","LOGIN_TTL","MAX_DOCS")
def main():
    api=HfApi(token=os.environ["HF_TOKEN"])
    info=api.repo_info(SPACE,repo_type="space")
    names=set(api.list_repo_files(SPACE,repo_type="space",revision=info.sha))
    allrows=[]
    for name in PATHS:
        if name not in names:continue
        source=Path(hf_hub_download(SPACE,name,repo_type="space",revision=info.sha,token=api.token)).read_text("utf-8")
        lines=source.splitlines()
        constants=[]
        contexts=[]
        for i,line in enumerate(lines):
            if name=="account_chat_store.py" and re.match(r"\s*(?:"+"|".join(KEYS)+r")\s*=",line):
                constants.append({"line":i+1,"source":line.strip()[:160]})
            relevant=False
            if name=="station.py":
                relevant=bool(re.search(r"(?:_persist_chat_snapshot|_restore_chat_from_store|_refresh_account_chat|persist_runtime_diagnostic)\(",line)) and not line.lstrip().startswith("def ")
            elif name=="chat/§wyrlz/index.html":
                relevant=bool(re.search(r"setInterval|visibilitychange|/api/lalm_station/sync|/api/chat_state|/api/account/status",line))
            elif name=="chatgpt_archive.py":
                relevant=bool(re.search(r"gh\._redis|archive|CHUNK|_upload|SET|GET",line)) and (
                    "gh._redis" in line or "CHUNK" in line or "MAX" in line)
            elif name=="chatgpt_account_memory.py":
                relevant=bool(re.search(r"gh\._redis",line))
            if relevant:
                start=max(0,i-3)
                end=min(len(lines),i+4)
                excerpt=" \n".join(f"{k+1}: {lines[k].strip()[:170]}" for k in range(start,end))
                excerpt=re.sub(r"(rediss?://|https?://)[^'\"\s]+","[URL omitted]",excerpt)
                contexts.append({"line":i+1,"context":excerpt[:950]})
        allrows.append({"file":name,"constants":constants,
                        "context_count":len(contexts),
                        "contexts":contexts[:75]})
    for file in allrows:
        print("SWRLZ_BANDWIDTH_DETAIL "+json.dumps(file,ensure_ascii=True,sort_keys=True))
    print("SWRLZ_BANDWIDTH_AUDIT_DONE "+json.dumps({"spaceRevision":info.sha,
         "filesAnalyzed":len(allrows),"readOnly":True},sort_keys=True))
if __name__=="__main__":main()
