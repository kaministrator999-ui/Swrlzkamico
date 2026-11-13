#!/usr/bin/env python3
"""Read-only source and profile composition inspection on CURRENT §C HF Space.
Print only source structure / code excerpts; no private profile or account data.
"""
import ast,json,inspect,re
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
space="kamiloki/Swyrlz"
api=HfApi()
rev=api.repo_info(space,repo_type="space").sha
files=("lfm2_700m_engine.py","station.py","app.py","model_router.py","qwen35_single_runtime.py","programming_repair_context.py")
print("SPACE_SHA",rev,flush=True)
for filename in files:
    try:
        path=hf_hub_download(space,filename,repo_type="space",revision=rev)
        content=Path(path).read_text("utf-8")
    except Exception as err:
        print("FILE_ERROR",filename,type(err).__name__,flush=True)
        continue
    print("FILE",filename,len(content),flush=True)
    if filename=="lfm2_700m_engine.py":
        for needle in ("BUILTIN_ASSISTANT_PROFILE=", "def _identity_context_profile(", "def _role_frame(", "def _qwen35_plain_social_turn(", "def generate_events(", "BUILT-IN §WYRLZ PROFILE", "if _qwen35_plain_social_turn", "model=load()", "messages,dropped_history", "system_tokens=_token_count", "source_sized_budget(", "response_budget("):
            found=content.count(needle)
            lines=content.splitlines()
            places=[i for i,l in enumerate(lines) if needle in l]
            for i in places[:2]:
                sample=lines[max(0,i-2):i+(25 if needle.startswith("def ") and needle!="def generate_events(" else 5)]
                if needle=="BUILTIN_ASSISTANT_PROFILE=":
                    sample=lines[i:i+4]
                print("ANCHOR",needle,"occurrences",found,"line",i+1,"code",json.dumps(sample,ensure_ascii=False),flush=True)
        # Print exact all profile/system reassignment sites, not data values.
        lines=content.splitlines()
        select=[(i+1,s.strip()[:150]) for i,s in enumerate(lines) if "system=" in s or "system+=" in s or "_role_frame(" in s or "_identity_context_profile(" in s]
        print("SYSTEM_ASSIGNMENTS",json.dumps(select[-75:],ensure_ascii=False),flush=True)
    if filename=="station.py":
        lines=content.splitlines()
        needles=("saved_profile","userProfile","profileId","profile=","BUILTIN_ASSISTANT_PROFILE","companion_profile", "relation", "model_id")
        for needle in needles:
            places=[i for i,l in enumerate(lines) if needle in l]
            print("STATION_MARKERS",needle,len(places),places[-8:],flush=True)
        for i,s in enumerate(lines):
            if "saved_profile[\"version\"]" in s:
                print("PROFILE_HANDOFF_CODE",json.dumps(lines[i:i+27],ensure_ascii=False),flush=True)
    if filename=="app.py":
        lines=content.splitlines()
        for needle in ("_warm_backends","set_generator","def generate_events","PROFILE","profile"):
            matches=[i+1 for i,line in enumerate(lines) if needle in line]
            print("APP_MARKERS",needle,matches[:12],flush=True)
    if filename=="qwen35_single_runtime.py":
        for needle in ("cache_prompt","ctx-size","DECODE_THREADS", "BATCH_THREADS","BATCH_SIZE","UBATCH_SIZE","PARALLEL_REQUESTS"):
            matches=[line.strip()[:180] for line in content.splitlines() if needle in line]
            print("RUNTIME",needle,json.dumps(matches[:6]),flush=True)
print("AUDIT_COMPLETE_READ_ONLY",flush=True)
