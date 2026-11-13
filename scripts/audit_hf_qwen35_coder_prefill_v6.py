#!/usr/bin/env python3
"""Inspect exact production 9B coding path; no user data, never mutates Space."""
from __future__ import annotations
import ast
import json
import re
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
SPACE="kamiloki/Swyrlz"
api=HfApi()
revision=api.repo_info(SPACE,repo_type="space").sha
print("LIVE_CODER_SOURCE_REVISION",revision,flush=True)
for filename in ("qwen_coder_engine.py","lfm2_700m_engine.py","qwen35_single_runtime.py",
                 "station.py","programming_telemetry.py","programming_repair_context.py"):
    try:
        path=hf_hub_download(SPACE,filename,repo_type="space",revision=revision)
        lines=Path(path).read_text("utf-8").splitlines()
    except Exception as err:
        print("SOURCE_UNAVAILABLE",filename,type(err).__name__,flush=True)
        continue
    print("SOURCE_FILE",filename,"lines",len(lines),flush=True)
    if filename=="qwen_coder_engine.py":
        for i,line in enumerate(lines):
            if ("n_batch" in line or "n_ubatch" in line or "n_threads_batch" in line or "_thread_plan" in line):
                print("LIVE_CODER_BATCH_SOURCE",json.dumps({"line":i+1,"code":line[:450]}),flush=True)
        needles=[
         "def generate_events(", "def _fit_messages(", "def _token_count(",
         "def _chat_token_count(", "def _profile", "def _wyrlz",
         "def load(", "model=load()", "buffered_chat_completion(",
         "complete_longform(", "candidate_contract_gate(",
         "response_budget(", "source_sized_budget(", "_fit_messages(",
         "reset_token_cache", "CODE_TRUTH_POLICY", "_wyrlz_active_profile(",
         'yield {"type":"CONTEXT"', 'yield {"type":"STATUS","phase":"PROFILE_CONTEXT_READY"',
         '"type":"GENERATION_TELEMETRY"', '"type":"CANDIDATE_VALIDATION"',
         "prompt_tokens=_token_count", "system_tokens=_token_count",
         "max_tokens=", "response_tokens", "retry",
        ]
        for n in needles:
            hits=[i for i,l in enumerate(lines) if n in l]
            print("CODER_MARKER",json.dumps({"find":n,"lines":[i+1 for i in hits[:12]]},
                                            ensure_ascii=False),flush=True)
        select=[]
        for i,line in enumerate(lines):
            if any(s in line for s in (
                "started=time.perf_counter()","loaded=time.perf_counter()",
                "system_tokens=_token_count", "yield {\"type\":\"STATUS\",\"phase\":\"GENERATING\"",
                "stream=model.create_chat_completion(", "model.create_chat_completion(",
                "buffered_chat_completion(", "completion_validation(",
                "candidate_contract_gate(", "for chunk in ","for event in",
                "first_delta=", "yield {\"type\":\"GENERATION_TELEMETRY\"",
                "generation_summary(", "source_sized_budget(","_fit_messages(")):
                select.append((i+1,lines[max(0,i-3):i+8]))
        for i,chunk in select[:80]:
            print("CODER_EXCERPT",json.dumps({"line":i,"code":chunk},ensure_ascii=False),flush=True)
    elif filename=="qwen35_single_runtime.py":
        for i,line in enumerate(lines):
            if any(k in line for k in ("create_chat_completion","cachedPromptTokens",
                 "QWEN35_INFERENCE_TIMING_V3","chat_template_kwargs","cache_prompt",
                 "batchThreads","DECODE_THREADS","CONTEXT_TOKENS","max_tokens","_post(")):
                print("RUNTIME_MARKER",json.dumps({"line":i+1,"code":line[:260]}),flush=True)
    elif filename=="station.py":
        for i,line in enumerate(lines):
            if any(k in line for k in ('elif kind=="GENERATION_TELEMETRY"',
                 'elif kind=="CONTEXT"', "def _snapshot(", "def stream_generation(",
                 'engineCompletionTelemetry',"generationTelemetry","contextBudget")):
                print("STATION_MARKER",json.dumps({"line":i+1,"code":lines[max(0,i-2):i+12]}),flush=True)
    elif filename=="programming_telemetry.py":
        for i,line in enumerate(lines):
            if "def buffered_chat_completion(" in line or "def candidate_attempt_receipt(" in line:
                print("TELEMETRY_FUNCTION",json.dumps({"line":i+1,"code":lines[i:i+45]}),flush=True)
print("CODER_SOURCE_INSPECTION_DONE",flush=True)
