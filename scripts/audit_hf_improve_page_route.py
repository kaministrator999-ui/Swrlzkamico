#!/usr/bin/env python3
"""Read-only synthetic source-continuation intent routing regression."""
from __future__ import annotations
import json,sys
from unittest.mock import patch
from huggingface_hub import snapshot_download
folder=snapshot_download("kamiloki/Swyrlz",repo_type="space",
    allow_patterns=["*.py","programming_references/**"],
    ignore_patterns=["*.gguf","*.bin","*.safetensors"],max_workers=5)
sys.path.insert(0,folder)
from brain_programming import programming_intent
from test_github_change_model_context import load_engine
from test_generation_completion_budget import Responses
from programming_repair_context import preserve_existing_source
FENCE=chr(96)*3
SOURCE=FENCE+"html\n<!DOCTYPE html><html><head><style>body{background:#030917;color:white}</style></head><body><header>Old title</header><main><button>Test</button></main></body></html>\n"+FENCE
HISTORY=[
 {"role":"user","text":"Can you generate a coding demonstrational html page make it look good"},
 {"role":"assistant","text":SOURCE},
 {"role":"user","text":"Now improve it"},
 {"role":"assistant","text":"Generation failed: OUTPUT_TOKEN_LIMIT"},
 {"role":"user","text":"Now improve the page"},
 {"role":"assistant","text":"Generation failed: OUTPUT_TOKEN_LIMIT"},
]
def compact(v):
    return {k:v.get(k) for k in ("codingTask","changeClass","projectContext",
      "artifactContinuation","artifactMutationRequested","newProject",
      "canonicalCarry","needsFailureEvidence")}
for count in (2,4,6):
    subset=HISTORY[:count]
    for prompt in ("Now improve it","Now improve the page","Improve this HTML page"):
        intent=programming_intent(prompt,subset,[],{})
        print("IMPROVE_INTENT",json.dumps({"historyCount":count,"prompt":prompt,
            "intent":compact(intent),
            "preserve":preserve_existing_source(intent),
            "sourceTextInRecent8":any(FENCE+"html" in x["text"] for x in subset[-8:] if x["role"]=="assistant")}),flush=True)
engine=load_engine("qwen_coder_engine")
for count in (2,4,6):
    subset=HISTORY[:count]
    model=Responses([(SOURCE.replace("Old title","New title"),"length"),
                     (SOURCE.replace("Old title","Refined title"),"stop"),
                     (SOURCE.replace("Old title","Updated title"),"stop")])
    with patch.object(engine,"load",return_value=model):
        events=list(engine.generate_events({"prompt":"Now improve the page","history":subset}))
    print("IMPROVE_ENGINE",json.dumps({
        "historyCount":count,
        "candidateReceipts":[{"finishReason":e["attempt"].get("finishReason"),
           "validationStatus":e["attempt"].get("validationStatus"),
           "validationReasons":e["attempt"].get("validationReasons"),
           "continuationSegments":e["attempt"].get("continuationSegments")}
           for e in events if e["type"]=="CANDIDATE_ATTEMPT"],
        "modelCalls":len(model.calls),
        "modelPrompts":[{"context":len(c.get("messages",[])),
            "isResume":"NEXT_BYTES_ONLY" in str(c.get("messages",[])[-1].get("content","")),
            "maxTokens":c.get("max_tokens")} for c in model.calls],
        "terminal":events[-1].get("type"),"reason":events[-1].get("reason"),
        "phases":[e.get("phase") for e in events if e.get("type")=="STATUS"][-7:]
      },ensure_ascii=False),flush=True)
print("IMPROVE_ROUTE_AUDIT_DONE",flush=True)
