#!/usr/bin/env python3
"""Guarded v6: reduce coding prefill on the shared resident Qwen3.5-9B.

Applies only to the §C coding workflow, not model weights or CPU batch settings.
Coder and conversation use the same 9B GGUF weights and 8K model context.
§E integration, auth, code contracts, and candidate validation remain unchanged.
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
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
CODER="qwen_coder_engine.py"
CONFIG="coder_model_config.py"
GENERAL="lfm2_700m_engine.py"
STATION="station.py"
RUNTIME="qwen35_single_runtime.py"
PROFILE_MARKER="swrlz-coder-prefill-v6"
MANAGED=(CODER,)
VERIFY_FILES=(CODER,CONFIG,GENERAL,STATION,RUNTIME)

# No coarse keyword routing to a different model; the existing classifier
# decides whether code matters. Only a new, isolated *small* code artifact may
# use shortened, source-grounded authoring instructions.
FAST_CODE_ROUTER=r'''def _swrlz_standalone_code_prefill(prompt,programming,payload,history,source_change_mode):
    if source_change_mode or not programming.get("codingTask") or history:
        return False
    if any(programming.get(k) for k in (
        "failureEvidence","canonicalCarry","repairDirection",
        "artifactContinuation","artifactMutationRequested","artifactTargetId",
        "needsFailureEvidence","priorProgrammingState","newProject",
        "failureHistory","activeRepairConstraints",
    )):
        return False
    # The router ALWAYS supplies a schema-only behavior ledger and a repair
    # constraints dictionary, even for a brand new standalone function.  Do
    # not mistake empty metadata wrappers for active repair evidence.
    ledger=programming.get("behaviorLedger")
    if isinstance(ledger,dict) and any(ledger.get(k) for k in (
        "suiteKey","currentFailingCases","knownPassingCases","preservePassingCases",
        "regressedCases","resolvedCases","currentTestedArtifact",
        "bestKnownArtifact","currentScore","bestKnownScore",
    )):
        return False
    repair_constraints=programming.get("repairConstraints")
    if isinstance(repair_constraints,dict) and any(repair_constraints.get(k) for k in (
        "unavailableDependencies","forbiddenDependencies",
        "currentReceiptDependencies","carriedUnavailableDependencies",
        "addedDependencies",
    )):
        return False
    if any(payload.get(k) for k in (
        "nativeEditorEvidence","onlineContext","projectThreadEvidence",
        "archiveEvidence","githubContext","githubAction","githubSourceChangeTask",
        "forgeContext","forgeLeaseId","visionJobId","visionReceipt",
        "fileDialogue","pinnedContext","uploadedFiles","attachments",
    )):
        return False
    cleaned=" ".join(str(prompt or "").split())
    if not cleaned or len(cleaned)>230 or "\x60" in cleaned:
        return False
    if re.search(r"https?://|www\.|§[eEcC]\b|\\\\|/api/|[{}]",cleaned,re.I):
        return False
    if not re.search(r"\b(?:write|create|implement|generate|show|make)\b",cleaned,re.I):
        return False
    if not re.search(r"\b(?:function|method|short|simple|small|snippet|hello world|example)\b",
                     cleaned,re.I):
        return False
    if re.search(
        r"\b(?:fix|debug|repair|refactor|rewrite|edit|modify|update|change|"
        r"extend|import|repository|repo|github|commit|deploy|existing|"
        r"project|integration|integrate|engine|server|database|"
        r"frontend|backend|file|directory|folder|component|"
        r"error|stack trace|test failure|"
        r"architecture|library|framework|api endpoint|endpoint)\b",
        cleaned,re.I
    ):
        return False
    contract=programming.get("intentContract")
    if isinstance(contract,dict):
        # Never truncate a hard user constraint for a supposed speed shortcut.
        if len(json.dumps(contract,ensure_ascii=False))>4500:
            return False
        if (contract.get("artifactType") in ("web-page","application","repository")
            or (contract.get("languageContract") or {}).get("artifactType")
              in ("web-page","application","repository")):
            return False
    return True


def _swrlz_compact_standalone_code_system(prompt,programming,
                                         custom_assistant_profile,user_profile):
    """Grounded original role and nonoptional code-truth/acceptance policy."""
    text=(
        "You are §wyrlz. Implement the user's exact coding request as usable "
        "code, respecting its requested language, names, signatures, examples "
        "and negative constraints. Do not claim to have run tests without a "
        "verified execution receipt. The deterministic code validator remains "
        "authoritative. Keep the answer focused; no unasked extras.\n"
        "AUTHORED §WYRLZ CORE:\n"
        +_wyrlz_active_profile(prompt,programming,brief=True)
        +"\nMANDATORY CODE-TRUTH POLICY:\n"+CODE_TRUTH_POLICY
        +"\nRESPONSE MODE:\n"+_response_mode(prompt,programming)
    )
    contract=programming.get("intentContract")
    if isinstance(contract,dict) and contract:
        # The latest user utterance already holds originalRequest. Deduplicate
        # that one field, but retain every authored language/negative constraint.
        constraints={k:v for k,v in contract.items()
                     if k not in ("originalRequest","acceptanceEvidence")}
        if constraints:
            text+="\nSTRUCTURED ACCEPTANCE CONSTRAINTS:\n"+json.dumps(
                constraints,ensure_ascii=False,separators=(",",":"))
    if custom_assistant_profile:
        text+="\nSAVED ASSISTANT CUSTOMIZATION:\n"+custom_assistant_profile
    if user_profile:
        text+="\nUSER PROFILE (human only):\n"+user_profile
    return text

'''
FAST_POLICY_OLD=r'''    if not source_change_mode:
        system+=project_delivery_policy(programming,prompt)+long_delivery_policy(budget_policy)
    started=time.perf_counter()'''
FAST_POLICY_NEW=r'''    if not source_change_mode:
        system+=project_delivery_policy(programming,prompt)+long_delivery_policy(budget_policy)
    # swrlz-coder-prefill-v6: isolated tiny artifacts skip large unrelated
    # programming-project tutorials. Preserve mandatory code-truth rules,
    # exact source/repair workflow for all other requests, and full validation.
    simple_code_prefill=_swrlz_standalone_code_prefill(
        prompt,programming,payload,history,source_change_mode)
    if simple_code_prefill:
        system=_swrlz_compact_standalone_code_system(
            prompt,programming,custom_assistant_profile,user_profile)
    started=time.perf_counter()'''

RESOURCE_OLD=r'''        yield {"type":"RESOURCE","cpuCapacity":_cpu_capacity(),"decodeThreads":_thread_plan()[0],"batchThreads":_thread_plan()[1],"maxResponseTokens":response_tokens}'''
RESOURCE_NEW=r'''        if simple_code_prefill:
            # Small isolated functions do not require 4096 output tokens;
            # no change to source-grounded/repair and other coding tasks.
            response_tokens=min(response_tokens,1024)
        yield {"type":"RESOURCE","cpuCapacity":_cpu_capacity(),"decodeThreads":_thread_plan()[0],"batchThreads":_thread_plan()[1],"maxResponseTokens":response_tokens}'''

def one(s,needle,replacement,name):
    n=s.count(needle)
    if n!=1:raise RuntimeError(f"Live coding source drift at {name}: {n} matches")
    return s.replace(needle,replacement,1)

def patch_coder(s):
    s=one(s,"def generate_events(payload):",
          FAST_CODE_ROUTER+"def generate_events(payload):","new safe prefill router")
    s=one(s,FAST_POLICY_OLD,FAST_POLICY_NEW,"small standalone policy")
    s=one(s,RESOURCE_OLD,RESOURCE_NEW,"small isolated response budget")
    s=one(s,
      '"cpuCapacity":_cpu_capacity(),"decodeThreads":_thread_plan()[0],"batchThreads":_thread_plan()[1],',
      '"cpuCapacity":SHARED_CPU_CAPACITY,"decodeThreads":SHARED_DECODE_THREADS,"batchThreads":SHARED_BATCH_THREADS,',
      "correct stale coder resource telemetry")
    s=one(s,
      '"""Dedicated Qwen2.5-Coder GGUF route for programming tasks."""',
      '"""Dedicated coding workflow over the shared resident Qwen3.5-9B runtime."""',
      "stale coder route documentation")
    s=one(s,
      'from qwen35_single_runtime import MODEL_REPO, MODEL_FILE',
      'from qwen35_single_runtime import MODEL_REPO, MODEL_FILE, CPU_CAPACITY as SHARED_CPU_CAPACITY, DECODE_THREADS as SHARED_DECODE_THREADS, BATCH_THREADS as SHARED_BATCH_THREADS',
      "use actual shared 9B CPU profile")
    s=one(s,
      '    yield {"type":"STATUS","phase":"PROFILE_CONTEXT_READY","reason":"swrlz-qwen35-profile-v5"}',
      '    yield {"type":"STATUS","phase":"PROFILE_CONTEXT_READY","reason":"swrlz-qwen35-profile-v5"}\n'
      '    yield {"type":"STATUS","phase":"CODER_PREFILL_PROFILE","reason":'
      '("swrlz-coder-prefill-v6-compact" if simple_code_prefill '
      'else "swrlz-coder-prefill-v6-standard")}',
      "status instrumentation")
    ast.parse(s,filename=CODER)
    return s

def sha(b):return hashlib.sha256(b).hexdigest()

def test_patched(before,after):
    old=before[CODER].decode("utf-8")
    updated=after[CODER].decode("utf-8")
    original_profile=old.split('BUILTIN_ASSISTANT_PROFILE="""',1)[1].split('"""',1)[0]
    revised_profile=updated.split('BUILTIN_ASSISTANT_PROFILE="""',1)[1].split('"""',1)[0]
    assert original_profile==revised_profile
    assert 'from qwen35_single_runtime import load as qwen35_load' in updated
    assert 'return qwen35_load()' in updated
    assert "CONTEXT_TOKENS=8192" in updated
    assert "SHARED_CPU_CAPACITY" in updated and "SHARED_DECODE_THREADS" in updated
    assert "BATCH_SIZE = 2048 if CPU_CAPACITY >= 8 else 512" in before[RUNTIME].decode("utf-8")
    assert "UBATCH_SIZE = 1024 if CPU_CAPACITY >= 8 else 256" in before[RUNTIME].decode("utf-8")
    assert "DECODE_THREADS = min(16, CPU_CAPACITY)" in before[RUNTIME].decode("utf-8")
    assert "buffered_chat_completion(model,messages,response_tokens,temperature)" in updated
    assert "_candidate_structure_check(text_value,programming,history)" in updated
    assert "enforce_strategy_change(" in updated
    assert "CANDIDATE_VALIDATION" in updated
    assert "strict_language" in updated and "repair_turn" in updated
    assert "_swrlz_compact_standalone_code_system" in updated
    assert "CODER_PREFILL_PROFILE" in updated
    assert "from lfm2_700m_engine import _wyrlz_active_profile" in updated
    assert before[GENERAL] == after[GENERAL]
    assert before[RUNTIME] == after[RUNTIME]
    assert before[STATION] == after[STATION]
    assert before[CONFIG] == after[CONFIG]
    assert b'Qwen3.5-9B-Q4_K_M.gguf' in before[RUNTIME]
    # The historic coder catalog remains on disk, but this live route must
    # import and use the same Qwen3.5-9B GGUF weights as text/chat.
    assert "from qwen35_single_runtime import MODEL_REPO, MODEL_FILE" in updated
    assert '"""Dedicated coding workflow over the shared resident Qwen3.5-9B runtime."""' in updated
    ast.parse(updated,filename=CODER)
    print(json.dumps({"status":"CODER_V6_SOURCE_CHECK_PASS",
           "originalCoderProfilePreserved":True,"sharedResident9B":True,"sameHardwareTier":True,
           "candidateValidationPreserved":True,
           "residentBatch":2048,"residentMicroBatch":1024,
           "filesChanged":[CODER]}),flush=True)

def candidate(api):
    revision=api.repo_info(SPACE,repo_type="space").sha
    before={}
    for name in VERIFY_FILES:
        path=hf_hub_download(SPACE,name,repo_type="space",revision=revision,
                             token=api.token)
        before[name]=Path(path).read_bytes()
    after=before.copy()
    after[CODER]=patch_coder(before[CODER].decode("utf-8")).encode("utf-8")
    test_patched(before,after)
    result={"revision":revision,"target":SPACE,
            "beforeSha256":sha(before[CODER]),
            "afterSha256":sha(after[CODER]),
            "modifiedFiles":[CODER],"paidHardware":False}
    print("CODER_V6_CANDIDATE",json.dumps(result),flush=True)
    return revision,before,after

def publish(api):
    if os.environ.get("SWRLZ_QWEN35_CODER_V6_APPROVED")!="1":
        raise RuntimeError("Missing explicit owner-approved source release")
    revision,before,after=candidate(api)
    if api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("Concurrent Space deployment: refuse mutation")
    with TemporaryDirectory(prefix="swrlz-coder-v6-") as td:
        path=Path(td)/CODER
        path.write_bytes(after[CODER])
        res=api.create_commit(repo_id=SPACE,repo_type="space",
            parent_commit=revision,
            operations=[CommitOperationAdd(path_in_repo=CODER,path_or_fileobj=str(path))],
            commit_message="§C 9B: compact safe standalone coding instructions, correct shared CPU telemetry")
        published=str(res.oid)
        uploaded=Path(hf_hub_download(SPACE,CODER,revision=published,
                              repo_type="space",token=api.token)).read_bytes()
        if sha(uploaded)!=sha(after[CODER]):
            raise RuntimeError("New coder source SHA differs from validated candidate")
        print("CODER_V6_SOURCE_PUBLISHED",
              json.dumps({"oldRevision":revision,"revision":published}),flush=True)
        return published,before

def rollback(api,revision,before):
    if api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("Concurrent Space update prevents safe rollback")
    with TemporaryDirectory(prefix="swrlz-coder-v6-rollback-") as td:
        path=Path(td)/CODER
        path.write_bytes(before[CODER])
        res=api.create_commit(repo_id=SPACE,repo_type="space",
             parent_commit=revision,
             operations=[CommitOperationAdd(path_in_repo=CODER,path_or_fileobj=str(path))],
             commit_message="Rollback coder prefill-v6 experiment to exact previous source")
        rev=str(res.oid)
        restored=Path(hf_hub_download(SPACE,CODER,revision=rev,repo_type="space",
                        token=api.token)).read_bytes()
        if sha(restored)!=sha(before[CODER]):
            raise RuntimeError("Coder rollback SHA mismatch")
        print("CODER_V6_ROLLBACK_VERIFIED",json.dumps({"revision":rev}),flush=True)

if __name__=="__main__":
    mode=sys.argv[1:] or []
    if mode not in (["inspect"],["publish"]):
        raise SystemExit("Usage: hf_chat_qwen35_coder_prefill_v6.py inspect|publish")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode==["inspect"]:
        candidate(api)
    else:
        if not api.token:raise RuntimeError("No existing HF Space release secret")
        publish(api)
