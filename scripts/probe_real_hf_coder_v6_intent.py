#!/usr/bin/env python3
"""Read-only 9B coding-intent regression probe; no chat or production mutations."""
import importlib.util, json, re, sys, tempfile, types
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download
from hf_chat_qwen35_coder_prefill_v6 import FAST_CODE_ROUTER, SPACE
def stub(name,**methods):
    m=types.ModuleType(name)
    for k,v in methods.items():setattr(m,k,v)
    sys.modules[name]=m
stub("source_answer_articulation_v230",lesson_kind=lambda prompt,history:None)
stub("programming_repair_context",candidate_source_fingerprint=lambda *a,**kw:"")
stub("response_cognition",requests_web_source=lambda *a,**kw:False,
     requests_source_project=lambda *a,**kw:False,
     classify_response_cognition=lambda *a,**kw:{})
stub("application_capabilities",apply_application_contract=lambda c,*a,**kw:c,
     application_source_gaps=lambda *a,**kw:[])
api=HfApi()
rev=api.repo_info(SPACE,repo_type="space").sha
path=hf_hub_download(SPACE,"brain_programming.py",repo_type="space",revision=rev)
spec=importlib.util.spec_from_file_location("swrlz_brain_intent_probe",path)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)
prompt="Write a short Python function that returns the square of an integer, and show one example."
intent=mod.programming_intent(prompt,[],[],{})
scope={"re":re,"json":json}
exec(FAST_CODE_ROUTER,scope)
qualifies=scope["_swrlz_standalone_code_prefill"]
def has_real_ledger(ledger):
    return {k:bool(ledger.get(k)) for k in (
        "suiteKey","currentFailingCases","knownPassingCases","preservePassingCases",
        "regressedCases","resolvedCases","currentTestedArtifact",
        "bestKnownArtifact","currentScore","bestKnownScore")}
result={
    "source":rev,
    "codingTask":intent.get("codingTask"),
    "changeClass":intent.get("changeClass"),
    "newProject":intent.get("newProject"),
    "historySize":0,
    "contractChars":len(json.dumps(intent.get("intentContract") or {},ensure_ascii=False)),
    "defaultLedgerActiveFields":has_real_ledger(intent.get("behaviorLedger") or {}),
    "repairConstraints":{k:int(bool((intent.get("repairConstraints") or {}).get(k))) for k in (
        "unavailableDependencies","forbiddenDependencies","currentReceiptDependencies",
        "carriedUnavailableDependencies","addedDependencies")},
    "programmingGuards":{k:bool(intent.get(k)) for k in (
        "failureEvidence","canonicalCarry","repairDirection","artifactContinuation",
        "artifactMutationRequested","artifactTargetId","needsFailureEvidence",
        "priorProgrammingState","newProject","failureHistory","activeRepairConstraints")},
    "compactRouteSelected":qualifies(prompt,intent,{},[],None),
}
print("REAL_BRAIN_CODER_V6_INTENT_CHECK",json.dumps(result),flush=True)
if not result["compactRouteSelected"]:
    raise RuntimeError("Actual source-shaped programming intent still does not activate compact route")
