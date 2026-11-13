#!/usr/bin/env python3
"""Source-preserving latency v3 overlay for resident Qwen3.5-9B on existing §C Space.

A narrowly-scoped short SOCIAL turn uses a compact truthful conversation role
rather than sending the 700M-era code/creative rulebook to the 9B. All coding,
research, vision, §E, identity and source-change routes retain their originals.
Adds request-local tokenization reuse, explicit native prompt KV reuse, timings
without payload content, and memory-bounded larger CPU prompt batches.
"""
from __future__ import annotations
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory

from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
RUNTIME="qwen35_single_runtime.py"
STATION="station.py"
ENGINE="lfm2_700m_engine.py"
FILES=(RUNTIME,STATION,ENGINE)
MARKER="swrlz-qwen35-latency-v3"

TOKENIZE_OLD='''class SingleQwen35:
    def tokenize(self, text: bytes, add_bos: bool = False):
        content = text.decode("utf-8", errors="strict")
        with _post("/tokenize", {"content": content, "add_special": bool(add_bos)}, timeout=60) as response:
            data = json.load(response)
        tokens = data.get("tokens")
        if not isinstance(tokens, list):
            raise RuntimeError("QWEN35_TOKEN_COUNT_UNAVAILABLE")
        return tokens

    def create_chat_completion'''
TOKENIZE_NEW='''class SingleQwen35:
    def __init__(self):
        self._per_request = threading.local()

    def reset_token_cache(self):
        # Never carry user/profile/source content between chat requests.
        self._per_request.values = {}

    def tokenize(self, text: bytes, add_bos: bool = False):
        if not isinstance(text, bytes):
            raise TypeError("QWEN35_TOKENIZE_REQUIRES_UTF8_BYTES")
        cache = getattr(self._per_request, "values", None)
        if cache is None:
            cache = {}
            self._per_request.values = cache
        key = (text, bool(add_bos))
        if key in cache:
            return list(cache[key])
        content = text.decode("utf-8", errors="strict")
        with _post("/tokenize", {"content": content, "add_special": bool(add_bos)}, timeout=60) as response:
            data = json.load(response)
        tokens = data.get("tokens")
        if not isinstance(tokens, list):
            raise RuntimeError("QWEN35_TOKEN_COUNT_UNAVAILABLE")
        if len(text) <= 64000:
            if len(cache) >= 48:
                cache.clear()
            cache[key] = tuple(tokens)
        return tokens

    def create_chat_completion'''
EVENTS_OLD='''        def events():
            with _post("/v1/chat/completions", payload, timeout=900) as response:
                for raw in response:
                    if not raw.startswith(b"data:"):
                        continue
                    content = raw.split(b":", 1)[1].strip()
                    if content == b"[DONE]":
                        break
                    if content:
                        value = json.loads(content)
                        if value.get("error"):
                            raise RuntimeError("QWEN35_INFERENCE_ERROR")
                        yield value
        return events()'''
EVENTS_NEW='''        def events():
            started = time.perf_counter()
            first_delta_at = None
            native_timing = {}
            completed = False
            try:
                with _post("/v1/chat/completions", payload, timeout=900) as response:
                    for raw in response:
                        if not raw.startswith(b"data:"):
                            continue
                        content = raw.split(b":", 1)[1].strip()
                        if content == b"[DONE]":
                            completed = True
                            break
                        if content:
                            value = json.loads(content)
                            if value.get("error"):
                                raise RuntimeError("QWEN35_INFERENCE_ERROR")
                            if isinstance(value.get("timings"), dict):
                                native_timing = value["timings"]
                            delta = (value.get("choices") or [{}])[0].get("delta") or {}
                            if first_delta_at is None and delta.get("content"):
                                first_delta_at = time.perf_counter()
                            yield value
            finally:
                self.reset_token_cache()
                # Operational counters only: no prompts, text, user IDs or history.
                print(json.dumps({"event": "QWEN35_INFERENCE_TIMING_V3",
                    "complete": completed,
                    "totalMs": round((time.perf_counter()-started)*1000, 1),
                    "firstTextMs": (round((first_delta_at-started)*1000, 1)
                                    if first_delta_at is not None else None),
                    "cachedPromptTokens": native_timing.get("cache_n"),
                    "evaluatedPromptTokens": native_timing.get("prompt_n"),
                    "generatedTokens": native_timing.get("predicted_n"),
                    "promptMs": native_timing.get("prompt_ms"),
                    "decodeMs": native_timing.get("predicted_ms")}), flush=True)
        return events()'''

SOCIAL_FUNCTION='''def _qwen35_plain_social_turn(prompt, programming, payload, file_dialogue, identity_turn):
    """Only clearly conversational phrasings; specialized tasks keep full prompt."""
    if identity_turn or file_dialogue or programming.get("codingTask"):
        return False
    if any(payload.get(key) for key in (
        "nativeEditorEvidence","onlineContext","githubSourceChangeTask",
        "projectThreadEvidence","archiveEvidence","widgetPresentation",
        "forgeContext","githubAction","githubStart","sourceChangeIdentity")):
        return False
    clean=" ".join(str(prompt or "").split()).strip()
    if not clean or len(clean)>170:
        return False
    # Avoid broad keyword shortcuts: "hey, write code" MUST NOT match.
    return bool(re.fullmatch(
        r"(?:"
        r"(?:hi|hello|hey|yo|howdy)(?:[,! ]+(?:how (?:are|r) you|how'?s it going|what'?s up))?"
        r"|how (?:are|r) you|how'?s it going|how have you been|what'?s up"
        r"|(?:pretty|really) (?:good|great|fine|okay)(?: actually| thanks| today)?"
        r"|(?:doing|i'?m doing) (?:good|great|fine|okay|alright)(?: thanks)?"
        r"|that took (?:a while|forever|so long)(?: for you to respond)?(?: lol| lmao)?"
        r"|(?:lol|lmao|haha|hahaha|yep|yeah|exactly|nice|cool|awesome)"
        r")[!?. ,]*",clean,re.I))

'''

SOCIAL_OVERLAY='''    # swrlz-qwen35-latency-v3: short social turns do not need ~5K tokens of
    # historical 700M programming and creative directives. Preserve actual
    # conversation history and all user-supplied account preferences.
    if _qwen35_plain_social_turn(prompt, programming, payload,
                                file_dialogue, concise_identity_turn or identity_followup):
        system=(
            "You are §wyrlz (spoken Swurlz), the AI assistant. The human is "
            "a separate person. Answer the latest human message naturally, "
            "with continuity from actual supplied chat history, not invented "
            "shared memories or experiences. Be conversational, helpful and "
            "specific; match the human's humor when appropriate without "
            "forcing it. Never claim to be human, fabricate external facts "
            "or actions, or pretend that a tool, file or project was changed. "
            "If the human is simply greeting you, reply directly and briefly. "
            "Respect what the user actually asked rather than changing the topic.\\n"
            +_role_frame(user_profile))
        if custom_assistant_profile:
            system+="\\nCURRENT USER'S ASSISTANT CUSTOMIZATION:\\n"+custom_assistant_profile
        if user_profile:
            system+="\\nCURRENT USER PROFILE (user, not assistant):\\n"+user_profile
'''

def exactly(s,old,new,where):
    n=s.count(old)
    if n!=1:
        raise RuntimeError(f"{where} expected unique source anchor, found {n}: {old[:76]!r}")
    return s.replace(old,new,1)

def patch_runtime(s):
    s=exactly(s,'BATCH_THREADS = min(16, CPU_CAPACITY)\\n',
       'BATCH_THREADS = min(16, CPU_CAPACITY)\\n'
       'BATCH_SIZE = 1024 if CPU_CAPACITY >= 8 else 512\\n'
       'UBATCH_SIZE = 512 if CPU_CAPACITY >= 8 else 256\\n', RUNTIME)
    s=exactly(s,'"--batch-size", "512",\\n        "--ubatch-size", "256"',
                    '"--batch-size", str(BATCH_SIZE),\\n        "--ubatch-size", str(UBATCH_SIZE)',RUNTIME)
    s=exactly(s,TOKENIZE_OLD,TOKENIZE_NEW,RUNTIME)
    s=exactly(s,'"chat_template_kwargs": {"enable_thinking": False},',
         '"chat_template_kwargs": {"enable_thinking": False},\\n'
         '            "cache_prompt": True,',RUNTIME)
    s=exactly(s,EVENTS_OLD,EVENTS_NEW,RUNTIME)
    s=exactly(s,'        return _instance\\n',
        '        _instance.reset_token_cache()\\n'
        '        return _instance\\n',RUNTIME)
    s=exactly(s,'"profile": "swrlz-qwen35-cpu-v2"}',
                   '"profile": "swrlz-qwen35-latency-v3",\\n'
                   '            "batchSize": BATCH_SIZE, "microBatchSize": UBATCH_SIZE}',RUNTIME)
    ast.parse(s,filename=RUNTIME)
    return s

def patch_station(s):
    s=exactly(s,'from qwen35_single_runtime import CPU_CAPACITY, DECODE_THREADS, BATCH_THREADS',
                  'from qwen35_single_runtime import CPU_CAPACITY, DECODE_THREADS, BATCH_THREADS, BATCH_SIZE, UBATCH_SIZE',STATION)
    s=exactly(s,'"profile": "swrlz-qwen35-cpu-v2"',
                  '"profile": "swrlz-qwen35-latency-v3"',STATION)
    s=exactly(s,'"batchSize": 512, "microBatchSize": 256',
                  '"batchSize": BATCH_SIZE, "microBatchSize": UBATCH_SIZE',STATION)
    ast.parse(s,filename=STATION)
    return s

def patch_engine(s):
    s=exactly(s,"def generate_events(payload):",SOCIAL_FUNCTION+"def generate_events(payload):",ENGINE)
    anchor='''    if source_change_mode:
        # Keep source/plan tokens available and bypass ordinary response-shape'''
    s=exactly(s,anchor,SOCIAL_OVERLAY+anchor,ENGINE)
    ast.parse(s,filename=ENGINE)
    return s

def sha(data):
    return hashlib.sha256(data).hexdigest()

def prepare(api):
    revision=api.repo_info(SPACE,repo_type="space").sha
    before={}
    for name in FILES:
        path=hf_hub_download(SPACE,name,repo_type="space",revision=revision,
                             token=api.token)
        before[name]=Path(path).read_bytes()
    assert b'Qwen3.5-9B-Q4_K_M.gguf' in before[RUNTIME]
    patched={RUNTIME:patch_runtime,STATION:patch_station,ENGINE:patch_engine}
    after={name:patched[name](before[name].decode("utf-8")).encode("utf-8")
           for name in FILES}
    test_candidate(before,after)
    receipt={"space":SPACE,"beforeRevision":revision,"profile":MARKER,
             "files":{name:{"beforeSha256":sha(before[name]),
                             "afterSha256":sha(after[name])} for name in FILES},
             "modelUnchanged":True,"paidHardware":False}
    print(json.dumps({"stage":"LATENCY_V3_CANDIDATE_VERIFIED","receipt":receipt}),flush=True)
    return revision,before,after

def test_candidate(before,after):
    rt=after[RUNTIME].decode("utf-8")
    eng=after[ENGINE].decode("utf-8")
    sta=after[STATION].decode("utf-8")
    assert "Qwen3.5-9B-Q4_K_M.gguf" in rt
    assert "PARALLEL_REQUESTS = 1" in rt and "CONTEXT_TOKENS = 8192" in rt
    assert '"cache_prompt": True' in rt
    assert "BATCH_SIZE = 1024 if CPU_CAPACITY >= 8 else 512" in rt
    assert "self.reset_token_cache()" in rt
    assert "QWEN35_INFERENCE_TIMING_V3" in rt
    assert '"profile": "swrlz-qwen35-latency-v3"' in sta
    assert "nativeEditorEvidence" in eng and "onlineContext" in eng
    assert "_qwen35_plain_social_turn" in eng
    for original,new in ((ENGINE,"def _fit_messages("),(ENGINE,"def _fit_repair_messages("),
                         (ENGINE,"def _identity_followup_subject(")):
        assert new in before[original].decode() and new in after[original].decode()
    for name in FILES: ast.parse(after[name].decode("utf-8"),filename=name)
    print(json.dumps({"stage":"LATENCY_V3_STATIC_TEST_PASS","changed":list(after),
                      "modelUnchanged":True,"sourceUntouched":True}),flush=True)

def publish(api):
    if os.environ.get("SWRLZ_QWEN35_LATENCY_V3_APPROVED")!="1":
        raise RuntimeError("Not approved for release")
    revision,before,after=prepare(api)
    if api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("Concurrent Space mutation: refusing to publish")
    with TemporaryDirectory(prefix="swrlz-latency-v3-") as td:
        dest=Path(td)
        for name in FILES:
            (dest/name).write_bytes(after[name])
        result=api.create_commit(
            repo_id=SPACE,repo_type="space",parent_commit=revision,
            operations=[CommitOperationAdd(path_in_repo=name,
                 path_or_fileobj=str(dest/name)) for name in FILES],
            commit_message="§C 9B latency v3: compact social prefill + CPU batch + request-local tokens")
        updated=str(result.oid)
        print(json.dumps({"stage":"LATENCY_V3_SOURCE_PUBLISHED",
                          "oldRevision":revision,"revision":updated}),flush=True)
        for name in FILES:
            actual=Path(hf_hub_download(SPACE,name,repo_type="space",
               revision=updated,token=api.token)).read_bytes()
            if sha(actual)!=sha(after[name]):
                if api.repo_info(SPACE,repo_type="space").sha==updated:
                    rollback(api,updated,before)
                raise RuntimeError("Published source failed SHA verification: "+name)
        print(json.dumps({"stage":"LATENCY_V3_SOURCE_VERIFIED",
                          "revision":updated}),flush=True)
        return {"sourceRevision":revision,"revision":updated}

def rollback(api,changed_revision,original_files):
    if api.repo_info(SPACE,repo_type="space").sha!=changed_revision:
        raise RuntimeError("Concurrent publication prevents safe rollback")
    with TemporaryDirectory(prefix="swrlz-latency-v3-rollback-") as td:
        dest=Path(td)
        for name,data in original_files.items():
            (dest/name).write_bytes(data)
        res=api.create_commit(repo_id=SPACE,repo_type="space",
           parent_commit=changed_revision,
           operations=[CommitOperationAdd(path_in_repo=name,
                       path_or_fileobj=str(dest/name)) for name in FILES],
           commit_message="Rollback §C latency-v3 source to exact previous revision")
        print(json.dumps({"stage":"LATENCY_V3_ROLLBACK","revision":str(res.oid)}),flush=True)

def main():
    mode=sys.argv[1:]
    if mode not in (["inspect"],["publish"]):
        raise SystemExit("Usage: hf_chat_qwen35_latency_v3.py inspect|publish")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode==["inspect"]:
        prepare(api)
    else:
        if not api.token: raise RuntimeError("Existing HF_TOKEN required")
        publish(api)

if __name__=="__main__": main()
