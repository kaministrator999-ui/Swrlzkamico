#!/usr/bin/env python3
"""Deterministic native-stream tests for §C lifecycle patch (no actual model)."""
from __future__ import annotations
import ast,time
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
from hf_chat_coding_lifecycle_v1 import patch_engine

rev=HfApi().repo_info("kamiloki/Swyrlz",repo_type="space").sha
raw=Path(hf_hub_download("kamiloki/Swyrlz","qwen_coder_engine.py",repo_type="space",
     revision=rev)).read_bytes()
changed=patch_engine(raw).decode()
tree=ast.parse(changed)
selected=("_swrlz_code_candidate_preview","_swrlz_trim_code_resume",
          "_swrlz_resume_tail_messages")
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in selected]
assert {x.name for x in functions}==set(selected)
def observe(receipt,chunk):
    for choice in chunk.get("choices",[]):
        if choice.get("finish_reason") is not None:
            receipt["finishReason"]=choice["finish_reason"]
    if "usage" in chunk:receipt["usage"]=chunk["usage"]
ns={"time":time,"_token_count":lambda model,msg:120,
    "CONTEXT_TOKENS":16384,"CONTEXT_SAFETY_TOKENS":128,
    "MIN_OUTPUT_TOKENS":384,"observe_completion_chunk":observe}
exec(compile(ast.Module(body=functions,type_ignores=[]),
             "<source-tested-coding-lifecycle>","exec"),ns)
def drain(gen):
    events=[]
    while True:
        try:events.append(next(gen))
        except StopIteration as end:return events,end.value
class Fake:
    def __init__(self,source,piece=8):
        self.source=source;self.piece=piece;self.calls=0;self.count=0
    def create_chat_completion(self,**kwargs):
        self.calls+=1
        for i in range(0,len(self.source),self.piece):
            self.count+=1
            yield {"choices":[{"delta":{"content":self.source[i:i+self.piece]},
                               "finish_reason":None}]}
        yield {"choices":[{"delta":{},"finish_reason":"stop"}],
               "usage":{"prompt_tokens":100,"completion_tokens":len(self.source)//4,
                        "total_tokens":100+len(self.source)//4}}
html="<!DOCTYPE html><html><head><style>.a{color:red}</style></head><body>"
html+="X"*5100
html+="</body></html>"
model=Fake(html,4)
events,(produced,receipt)=drain(ns["_swrlz_code_candidate_preview"](
    model,[{"role":"user","content":"Generate HTML"}],4096,0.22,1,
    allow_continue=True))
deltas=[e["text"] for e in events if e.get("type")=="CANDIDATE_PREVIEW_DELTA"]
assert "".join(deltas)==html,(len(produced),len(html))
assert produced==html
assert receipt["finishReason"]=="stop" and receipt["continuationSegments"]==1
assert len(deltas)<max(20,model.count//8),(len(deltas),model.count)
print("SWRLZ_CODING_NATIVE_PREVIEW_COALESCING_PASS",
      len(deltas),"events vs",model.count,"native chunks",flush=True)

source_seed="SAVED_SOURCE_BEFORE_INTERRUPT_"*900
extension="CONTINUATION_ONLY" * 22
model=Fake(extension,3)
events,(assembled,receipt)=drain(ns["_swrlz_code_candidate_preview"](
    model,[],4096,0.2,1,allow_continue=True,seed_text=source_seed))
assert assembled==source_seed+extension
assert "".join(e["text"] for e in events if e.get("type")=="CANDIDATE_PREVIEW_DELTA")==extension
assert len(model.create_chat_completion.__code__.co_varnames)>0
print("SWRLZ_CODING_SEEDED_SOURCE_AND_NEW_DELTA_PASS",len(assembled),flush=True)

model=Fake("x"*10000,2)
def cancelled():return model.count>=18
events,(partial,receipt)=drain(ns["_swrlz_code_candidate_preview"](
    model,[],4096,0.2,1,allow_continue=True,cancel_check=cancelled))
assert receipt.get("finishReason")=="cancelled"
assert model.count<35
assert len(partial)<10000
print("SWRLZ_NATIVE_CODING_STOP_INTERRUPTS_NEXT_CHUNK_PASS",model.count,flush=True)

class FakeClock:
    def __init__(self):self.t=0
    def perf_counter(self):self.t+=9;return self.t
clock=FakeClock()
original=ns["time"];ns["time"]=clock
try:
    model=Fake("A"*1000,8)
    events,(partial,receipt)=drain(ns["_swrlz_code_candidate_preview"](
       model,[],4096,0.2,1,allow_continue=True))
    assert receipt["finishReason"]=="length",receipt
    assert len(partial)<1000
    print("SWRLZ_CODING_NATIVE_TIME_BUDGET_STOPS_AT_BOUNDARY_PASS",len(partial),flush=True)
finally:ns["time"]=original
print("SWRLZ_LIFECYCLE_DETERMINISTIC_STREAM_SUITE_PASS",flush=True)
