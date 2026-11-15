#!/usr/bin/env python3
"""Inspect live §C no-code routing without mutating owner Space or showing private data."""
import ast,os,re,json
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
SPACE="kamiloki/Swyrlz"
api=HfApi(token=os.environ.get("HF_TOKEN") or None)
rev=api.repo_info(SPACE,repo_type="space").sha
print("CURRENT_HF_REV",rev,flush=True)
for name in ("qwen_coder_engine.py","brain_programming.py","station.py"):
    try:s=Path(hf_hub_download(SPACE,name,repo_type="space",revision=rev,token=api.token)).read_text()
    except Exception as e:
        print("SOURCE_ERROR",name,type(e).__name__,str(e)[:120],flush=True)
        continue
    markers=("swrlz-prose-intent-payload-precedence-v1","swrlz-explicit-prose-finalizer-v1",
       "swrlz-prose-only-response-mode-v1","swrlz-explicit-prose-only-programming-v1")
    print("SOURCE_META",json.dumps({"name":name,"lines":len(s.splitlines()),"markers":{x:x in s for x in markers}},ensure_ascii=False),flush=True)
    for key in ("def generate_events(payload)", "programming=payload.get(", "def programming_intent(", "def _current_programming_signal(",
      "prose_only_output","def _response_mode(", "def _swrlz_prose_source_breach", "elif mode.startswith", "code_delivery=bool("):
        idx=s.find(key)
        if idx>=0:print("SOURCE_CONTEXT",json.dumps({"name":name,"key":key,
            "line":s.count("\n",0,idx)+1,"text":s[max(0,idx-180):idx+1050]},ensure_ascii=False),flush=True)
    if name=="station.py":
        for key in ("@app.route('/api/lalm_station/sync'", '@app.get("/api/lalm_station/sync"', "def lalm_station_sync",
          "def station_sync", "guest", "session_cookie","currentThread"):
            idx=s.find(key)
            if idx>=0:print("STATION_CONTEXT",json.dumps({"key":key,"line":s.count("\n",0,idx)+1,
                     "text":s[max(0,idx-120):idx+360]},ensure_ascii=False),flush=True)
