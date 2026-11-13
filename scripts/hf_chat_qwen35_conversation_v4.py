#!/usr/bin/env python3
"""§C Qwen3.5-9B v4: natural chat context, separate technical policies, bounded CPU tune.

Modify the exact current production Space source, not stale GitHub files.
No model weight, inference provider, auth, billing, §E or voice changes.
"""
from __future__ import annotations
import ast, hashlib, json, os, sys
from pathlib import Path
from tempfile import TemporaryDirectory
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
from hf_chat_qwen35_latency_v3 import SOCIAL_FUNCTION, SOCIAL_OVERLAY

SPACE="kamiloki/Swyrlz"
RUNTIME="qwen35_single_runtime.py"
ENGINE="lfm2_700m_engine.py"
STATION="station.py"
FILES=(RUNTIME,ENGINE,STATION)
PROFILE="swrlz-qwen35-conversation-v4"

CONVERSATION_FUNCTION=r'''def _qwen35_plain_social_turn(prompt, programming, payload, file_dialogue, identity_turn):
    """Ordinary conversational follow-ups should not load code/research manuals."""
    if identity_turn or file_dialogue or programming.get("codingTask"):
        return False
    if programming.get("needsFailureEvidence") or programming.get("newProject"):
        return False
    if any(payload.get(k) for k in (
        "nativeEditorEvidence", "onlineContext", "widgetPresentation",
        "projectThreadEvidence", "archiveEvidence", "githubAction",
        "githubStart", "githubContext", "githubSourceChangeTask",
        "sourceChangeIdentity", "forgeContext", "forgeLeaseId",
        "visionJobId", "visionReceipt", "visionEvidence",
        "imageEvidence", "attachments", "uploadedFiles",
    )):
        return False
    clean=" ".join(str(prompt or "").split()).strip().replace("’", "'")
    if not clean or len(clean)>440 or "{" in clean or "}" in clean:
        return False
    if re.search(r"(https?://|www\.|[\x60]|/api/)",clean,re.I):
        return False
    # Explicit technical/agentic/medical/financial/research intent keeps the
    # original detailed prompt. A chat statement isn't a coding request.
    if re.search(
        r"(?:§[eEcC]\b|\b(?:"
        r"code|coding|program|programming|debug|error|exception|bug|"
        r"script|function|compile|test suite|patch|fix|repository|repo|"
        r"github|commit|pull request|deploy|deployment|server|hardware|"
        r"cpu|gpu|ram|model|inference|latency|engine|editor|studio|"
        r"rigging|mesh|texture|animation|research|source|citation|"
        r"reference|verify|fact.?check|search|browse|look up|website|"
        r"article|news|weather|image|photo|picture|screenshot|diagram|"
        r"video|audio|analy[sz]e|translate|summari[sz]e|calculate|"
        r"convert|finance|investment|bank|bill|medication|symptom|"
        r"emergency|doctor|hospital|suicide|hurt myself|"
        r"write|generate|build|create|design|edit|implement|"
        r"change the|update the|modify|delete|send|book|schedule|"
        r"find|show me|recommend|buy|purchase|price|cost|email|draft|"
        r"resume|calendar|appointment|dizzy|chest pain|sick|self.harm"
        r")\b)",clean,re.I):
        return False
    # Factual lookup or consequential questions retain research/specialist routing.
    if re.search(
        r"\b(?:what is|who is|where is|when is|why does|how do|"
        r"how much|how many|what happened|which one|tell me about|"
        r"explain|compare|what are the|is it true|can you|could you|"
        r"would you please|please (?:help|make|do|show|find))\b",
        clean,re.I
    ):
        return False
    return True

'''

CONVERSATION_OVERLAY=r'''    # swrlz-qwen35-conversation-v4: natural nontechnical chat needs no old
    # 700M coding manual. Actual conversation and user profile remain intact.
    # Technical, factual, image, §E, identity and file work keep full policy.
    if _qwen35_plain_social_turn(prompt, programming, payload,
                                file_dialogue, concise_identity_turn or identity_followup):
        system=(
            "You are §wyrlz (spoken Swurlz), the AI assistant. "
            "The human is a separate person. Respond naturally to the latest "
            "message using the actual chat history. Be specific, helpful and "
            "conversational; don't reintroduce yourself or repeat generic "
            "questions on every turn. Mirror appropriate humor without "
            "forcing it. Never invent personal memories, facts, research, "
            "tool results or completed actions. Do not claim human "
            "experiences. A friendly check-in deserves a direct reply.\n"
            +_role_frame(user_profile))
        if custom_assistant_profile:
            system+="\nASSISTANT CUSTOMIZATION FOR THIS USER:\n"+custom_assistant_profile
        if user_profile:
            system+="\nCURRENT USER PROFILE (user, not assistant):\n"+user_profile
'''

def one(text,old,new,label):
    n=text.count(old)
    if n!=1: raise RuntimeError(f"Live source drift {label}: {n} matches")
    return text.replace(old,new,1)

def patch_engine(s):
    s=one(s,SOCIAL_FUNCTION,CONVERSATION_FUNCTION,"chat classifier")
    s=one(s,SOCIAL_OVERLAY,CONVERSATION_OVERLAY,"chat system")
    ast.parse(s,filename=ENGINE)
    return s

def patch_runtime(s):
    s=one(s,"DECODE_THREADS = min(10, CPU_CAPACITY)",
             "DECODE_THREADS = min(16, CPU_CAPACITY)","decode CPU")
    s=one(s,"BATCH_SIZE = 1024 if CPU_CAPACITY >= 8 else 512",
             "BATCH_SIZE = 2048 if CPU_CAPACITY >= 8 else 512","prompt batch")
    s=one(s,"UBATCH_SIZE = 512 if CPU_CAPACITY >= 8 else 256",
             "UBATCH_SIZE = 1024 if CPU_CAPACITY >= 8 else 256","micro batch")
    s=one(s,'"profile": "swrlz-qwen35-latency-v3"',
             '"profile": "'+PROFILE+'"',"warmup profile")
    ast.parse(s,filename=RUNTIME)
    return s

def patch_station(s):
    s=one(s,'"profile": "swrlz-qwen35-latency-v3"',
             '"profile": "'+PROFILE+'"',"readiness profile")
    ast.parse(s,filename=STATION)
    return s

def sha(data):
    return hashlib.sha256(data).hexdigest()

def validate(before,after):
    engine=after[ENGINE].decode()
    runtime=after[RUNTIME].decode()
    station=after[STATION].decode()
    assert '"profile": "'+PROFILE+'"' in station
    assert '"model": "qwen3.5-9b"' in station
    assert "Qwen3.5-9B-Q4_K_M.gguf" in runtime
    assert "CONTEXT_TOKENS = 8192" in runtime
    assert "PARALLEL_REQUESTS = 1" in runtime
    assert '"cache_prompt": True' in runtime
    assert "DECODE_THREADS = min(16, CPU_CAPACITY)" in runtime
    assert "BATCH_THREADS = min(16, CPU_CAPACITY)" in runtime
    assert "BATCH_SIZE = 2048 if CPU_CAPACITY >= 8 else 512" in runtime
    assert "UBATCH_SIZE = 1024 if CPU_CAPACITY >= 8 else 256" in runtime
    for snippet in ("def _fit_repair_messages(","def _fit_messages(",
                    "source_sized_budget","nativeEditorEvidence",
                    "def generate_events(payload):"):
        assert snippet in engine
    for name in FILES:
        ast.parse(after[name].decode(),filename=name)
    print(json.dumps({"stage":"CONVERSATION_V4_STATIC_PASS",
        "model":"Qwen3.5-9B Q4_K_M", "CPU":16,
        "decodeThreads":16,"prefillThreads":16,"batch":2048,"microBatch":1024,
        "paidHardware":False}),flush=True)

def prepare(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before={}
    for name in FILES:
        src=hf_hub_download(SPACE,name,repo_type="space",revision=rev,token=api.token)
        before[name]=Path(src).read_bytes()
    after={RUNTIME:patch_runtime(before[RUNTIME].decode()).encode(),
           ENGINE:patch_engine(before[ENGINE].decode()).encode(),
           STATION:patch_station(before[STATION].decode()).encode()}
    validate(before,after)
    print(json.dumps({"stage":"CONVERSATION_V4_PREFLIGHT_PASS",
         "revision":rev,"files":{name:{"before":sha(before[name]),"after":sha(after[name])}
                  for name in FILES}}),flush=True)
    return rev,before,after

def publish(api):
    if os.environ.get("SWRLZ_QWEN35_CONVERSATION_V4_APPROVED")!="1":
        raise RuntimeError("Explicit production approval missing")
    oldrev,before,after=prepare(api)
    if api.repo_info(SPACE,repo_type="space").sha!=oldrev:
        raise RuntimeError("Concurrent deployment; refusing mutation")
    with TemporaryDirectory(prefix="swrlz-conv-v4-") as td:
        root=Path(td)
        for name,data in after.items():
            (root/name).write_bytes(data)
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=oldrev,
             operations=[CommitOperationAdd(path_in_repo=name,
                              path_or_fileobj=str(root/name)) for name in FILES],
             commit_message="§C 9B conversation v4: natural followup context and maximum quota-aware CPU")
        newrev=str(result.oid)
        for name in FILES:
            data=Path(hf_hub_download(SPACE,name,repo_type="space",
                         revision=newrev,token=api.token)).read_bytes()
            if sha(data)!=sha(after[name]):
                raise RuntimeError("Published source SHA mismatch "+name)
        print(json.dumps({"stage":"CONVERSATION_V4_PUBLISHED",
                           "before":oldrev,"after":newrev}),flush=True)
        return newrev,before

def rollback(api,rev,before):
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent update; unsafe to roll back")
    with TemporaryDirectory(prefix="swrlz-conv-v4-rollback-") as td:
        root=Path(td)
        for name,data in before.items(): (root/name).write_bytes(data)
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
             operations=[CommitOperationAdd(path_in_repo=name,
                        path_or_fileobj=str(root/name)) for name in FILES],
             commit_message="Rollback §C conversation v4 to exact prior source")
        rerev=str(result.oid)
        for name in FILES:
            data=Path(hf_hub_download(SPACE,name,repo_type="space",
                         revision=rerev,token=api.token)).read_bytes()
            if sha(data)!=sha(before[name]): raise RuntimeError("Rollback SHA mismatch "+name)
        print(json.dumps({"stage":"CONVERSATION_V4_ROLLED_BACK","revision":rerev}),flush=True)

def main():
    mode=sys.argv[1:]
    if mode not in (["inspect"],["publish"]):
        raise SystemExit("Usage: hf_chat_qwen35_conversation_v4.py inspect|publish")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode==["inspect"]:prepare(api)
    else:
        if not api.token:raise RuntimeError("No HF release credential")
        publish(api)

if __name__=="__main__": main()
