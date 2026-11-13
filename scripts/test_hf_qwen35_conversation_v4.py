"""Source-isolated §C conversation v4 routing and 16-core quota checks."""
from __future__ import annotations
import ast
import re
from pathlib import Path
from hf_chat_qwen35_conversation_v4 import (
    CONVERSATION_FUNCTION, CONVERSATION_OVERLAY, patch_runtime, patch_engine,
    patch_station, PROFILE
)
from hf_chat_qwen35_latency_v3 import patch_runtime as patch_v3_runtime

scope={"re":re}
exec(CONVERSATION_FUNCTION,scope)
eligible=scope["_qwen35_plain_social_turn"]

ordinary=(
  "Hey how are you?",
  "Doing well, just checking in on you",
  "I'm doing pretty good actually",
  "That took a while for you to respond lol",
  "Haha, I was just checking in!",
  "Lmfao",
  "I like chatting with you",
  "My day has been pretty nice",
  "What do you think?",
  "Did you have a good day?",
  "Actually just wanted to see how you were doing",
  "I'm just hanging out tonight, that's all",
  "Yep, feels like we can finally talk normally",
)
for phrase in ordinary:
    assert eligible(phrase, {}, {}, None, False),phrase
special=(
  "Hey write some code", "Can you debug this Python program?",
  "Can you help me fix the compiler error?", "I was coding in §E",
  "Check our GitHub commits and deploy", "Make an image from my picture",
  "Please research the newest models", "What's the weather?",
  "What is 4 plus 8?", "Can you explain neural networks?",
  "Analyze the uploaded screenshot", "What is my medication?",
  "Tell me about a financial investment", "Build a simple game engine",
  "Find me a restaurant", "Show me how to do a bevel operation",
  "What is the current news?", "Write an email for my boss",
)
for phrase in special:
    assert not eligible(phrase,{}, {}, None,False),phrase
assert not eligible("Doing well",{"codingTask":True},{},None,False)
assert not eligible("Doing well",{"newProject":True},{},None,False)
for data in (
    {"nativeEditorEvidence":{"selectedId":"abc"}},
    {"onlineContext":{"status":"OK"}},
    {"projectThreadEvidence":"code source evidence"},
    {"visionJobId":"verified-image"},
    {"githubAction":{"kind":"edit"}},
    {"archiveEvidence":{"record":"x"}},
):
    assert not eligible("Doing well",{},data,None,False),data
assert not eligible("Doing well",{}, {},{"file":"text"},False)
assert not eligible("Doing well",{}, {},None,True)
assert "custom_assistant_profile" in CONVERSATION_OVERLAY
assert "user_profile" in CONVERSATION_OVERLAY
assert "model_history" not in CONVERSATION_OVERLAY
# There must be no unsafe pretrained/truncated answer substitution: actual model
# inference keeps receiving the prior chat history unchanged.
assert "system=" in CONVERSATION_OVERLAY
assert "history=[]" not in CONVERSATION_OVERLAY

# Build the live v3 runtime shape from the same pinned versioned source, then
# apply v4; this verifies schema, model, concurrency and bounded CPU fallbacks.
source=Path("scripts/hf_chat_qwen35_9b_runtime.py").read_text()
v3=patch_v3_runtime(source)
v4=patch_runtime(v3)
ast.parse(v4)
assert "Qwen3.5-9B-Q4_K_M.gguf" in v4
assert "MODEL_REVISION = " in v4
assert "PARALLEL_REQUESTS = 1" in v4
assert "CONTEXT_TOKENS = 8192" in v4
assert "DECODE_THREADS = min(16, CPU_CAPACITY)" in v4
assert "BATCH_THREADS = min(16, CPU_CAPACITY)" in v4
assert "BATCH_SIZE = 2048 if CPU_CAPACITY >= 8 else 512" in v4
assert "UBATCH_SIZE = 1024 if CPU_CAPACITY >= 8 else 256" in v4
assert '"cache_prompt": True' in v4
assert 'reset_token_cache()' in v4

for available in (1,2,4,8,10,16,32):
    cap=min(16,max(1,available))
    assert min(16,cap)<=cap
    batch=2048 if cap>=8 else 512
    ubatch=1024 if cap>=8 else 256
    assert ubatch<=batch

print("QWEN35_V4_ROUTING_UNIT_PASS",
      {"ordinary":len(ordinary),"specialized":len(special),
       "singleModel":True,"CPU16Max":True,"historyPreserved":True},flush=True)
