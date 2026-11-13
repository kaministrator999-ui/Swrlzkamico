"""Offline guard tests for §C Qwen3.5-9B latency-v3 changes."""
from __future__ import annotations
import io
import json
from pathlib import Path
import re
import types
from unittest.mock import patch
from hf_chat_qwen35_latency_v3 import (
    SOCIAL_FUNCTION, SOCIAL_OVERLAY, patch_runtime, test_candidate,
    TOKENIZE_OLD, EVENTS_OLD,
)

scope={"re":re}
exec(SOCIAL_FUNCTION,scope)
social=scope["_qwen35_plain_social_turn"]

for prompt in ("Hey how are you?", "Hi!", "What’s up".replace("’","'"),
               "Pretty good actually", "That took a while for you to respond lol",
               "How are you?", "Lmfao"):
    assert social(prompt,{}, {}, None,False),prompt
for prompt in ("Hey write a Python program", "What's the weather in Kansas?",
               "Make a model in §E", "Explain this error",
               "Who created your AI system?", "Can you search the web?",
               "What is your name?"):
    assert not social(prompt,{}, {}, None,False), prompt
assert not social("Hi",{"codingTask":True},{},None,False)
assert not social("Hi",{},{"nativeEditorEvidence":{"selectedId":"a"}},None,False)
assert not social("Hi",{},{"onlineContext":{"status":"OK"}},None,False)
assert not social("Hi",{},{"projectThreadEvidence":"a"},None,False)
assert not social("Hi",{}, {},{"file":"hello"},False)
assert not social("Hi",{}, {},None,True)
assert "user_profile" in SOCIAL_OVERLAY and "custom_assistant_profile" in SOCIAL_OVERLAY
assert len(SOCIAL_OVERLAY) < 2200

# Compile the fully patched versioned runtime with no model download.
old=Path("scripts/hf_chat_qwen35_9b_runtime.py").read_text("utf-8")
assert TOKENIZE_OLD in old and EVENTS_OLD in old
new=patch_runtime(old)
module=types.ModuleType("test_qwen35_local")
exec(compile(new,"<patched-qwen35>", "exec"), module.__dict__)
assert module.MODEL_REPO=="twoody/Qwen3.5-9B-GGUF"
assert module.CONTEXT_TOKENS==8192
assert module.PARALLEL_REQUESTS==1
assert module.BATCH_SIZE==(1024 if module.CPU_CAPACITY>=8 else 512)
assert module.UBATCH_SIZE==(512 if module.CPU_CAPACITY>=8 else 256)

class Dummy:
    def __init__(self,data): self.body=io.BytesIO(data)
    def __enter__(self): return self.body
    def __exit__(self,*args): self.body.close()

calls=[]
def fake_post(path, payload, timeout=600):
    calls.append((path,payload))
    if path=="/tokenize":
        return Dummy(json.dumps({"tokens":[1,2,3]}).encode())
    return Dummy(b'data: {"choices":[{"delta":{"content":"hello"}}]}\n\n'
                 b'data: {"choices":[{"delta":{}}],"timings":{"cache_n":4000,"prompt_n":120,"predicted_n":7}}\n\n'
                 b'data: [DONE]\n\n')

model=module.SingleQwen35()
with patch.object(module,"_post",fake_post):
    assert model.tokenize(b"sample")==[1,2,3]
    assert model.tokenize(b"sample")==[1,2,3]
    assert [p for p,_ in calls].count("/tokenize")==1
    output=list(model.create_chat_completion(
        messages=[{"role":"user","content":"Hi"}],
        max_tokens=32,temperature=0.3,stream=True))
    assert len(output)==2
    assert calls[-1][1]["cache_prompt"] is True
    assert model._per_request.values == {}
    assert model.tokenize(b"sample")==[1,2,3]
    assert [p for p,_ in calls].count("/tokenize")==2
    model.reset_token_cache()
    assert model._per_request.values=={}

print(json.dumps({"status":"QWEN35_LATENCY_V3_UNIT_PASS",
                  "eligibleSocialCases":7,"disallowedCases":7,
                  "requestScopedTokenCache":True,"kvCacheExplicit":True,
                  "responsiveBatch":True}),flush=True)
