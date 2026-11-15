#!/usr/bin/env python3
"""Guarded source-preserving §C HTML coding-quality release.

Targets the canonical Hugging Face Space, not §E or a stale local mirror.
Preflight reads the live source, snapshots exact bytes and tests candidate.
Publish uses a parent-commit lease, verifies source and live 9B acceptance,
and rolls back if validation fails without a concurrent Space change.
"""
from __future__ import annotations

import ast
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import uuid

from html_code_quality_v1 import diagnose_html_candidate

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
ENGINE = "qwen_coder_engine.py"
HELPER = "html_code_quality_v1.py"
BACKUP = Path("swrlz-html-quality-v1-backup")
MARKER = "swrlz-html-code-quality-v1"
HEADER = {"User-Agent":"Swyrlz-HTML-Quality-Guard", "Cache-Control":"no-cache"}


def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def emit(stage: str, **fields):
    print("SWRLZ_HTML_QUALITY " + json.dumps({"stage":stage, **fields}, sort_keys=True), flush=True)


def patch_engine(raw: bytes) -> bytes:
    source = raw.decode("utf-8")
    if MARKER in source:
        raise RuntimeError("Quality patch already present; do not double wrap")
    tree = ast.parse(source, filename=ENGINE)
    declarations = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    names = {n.name:n.lineno for n in declarations}
    if not {"generate_events", "_response_mode"} <= names.keys():
        raise RuntimeError("Live coder engine lacks the expected generation hooks")
    if source.count("def generate_events(payload):") != 1:
        raise RuntimeError("Live source drift in generate_events signature")
    if "_candidate_structure_check" not in source:
        raise RuntimeError("The existing source validator is unavailable")
    line = names["generate_events"]
    if names["_response_mode"] >= line:
        raise RuntimeError("Response-mode hook is defined after generation")
    # Rebinding the existing helpers affects their future calls from
    # generate_events without rewriting source-dependent generation logic.
    # All other coding validation, model weights and streaming stay intact.
    overlay = '''# swrlz-html-code-quality-v1: bounded coding guidance and known-defect gate.
from html_code_quality_v1 import quality_guidance as _swrlz_html_guidance
from html_code_quality_v1 import extend_candidate_check as _swrlz_html_extend_check
_swrlz_before_quality_mode = _response_mode
_swrlz_before_quality_validator = _candidate_structure_check

def _response_mode(prompt, programming):
    original = _swrlz_before_quality_mode(prompt, programming)
    return original + _swrlz_html_guidance(prompt, programming)

def _candidate_structure_check(candidate, *args, **kwargs):
    original = _swrlz_before_quality_validator(candidate, *args, **kwargs)
    return _swrlz_html_extend_check(original, candidate)

'''
    anchor = "def generate_events(payload):"
    updated = source.replace(anchor, overlay+anchor, 1)
    ast.parse(updated, filename=ENGINE)
    return updated.encode("utf-8")


def test_overlay():
    fixture = b'''def _response_mode(prompt, programming):\n    return "BASE:"\ndef _candidate_structure_check(candidate, programming, history):\n    return {"status":"PASS", "reasons":[]}\ndef generate_events(payload):\n    return _response_mode(payload["prompt"],payload["programming"])\n'''
    updated = patch_engine(fixture)
    scope: dict = {}
    exec(compile(updated, "<quality-injection-test>", "exec"), scope)
    old = scope["generate_events"]({"prompt":"Improve HTML","programming":{"codingTask":True,"projectContext":"existing"}})
    assert "BASE:" in old and "Existing-source edit" in old and "Pointer Events" in old
    assert scope["generate_events"]({"prompt":"Hello","programming":{"codingTask":False}}) == "BASE:"
    bad = "<html><style>a{color:rgba(#fff,.2)}</style></html>"
    check = scope["_candidate_structure_check"](bad,{},[])
    assert check["status"]=="REJECT" and "invalid-css" in check["reasons"][0]
    assert scope["_candidate_structure_check"]("<html></html>",{},[])["status"]=="PASS"
    try:patch_engine(updated)
    except RuntimeError:pass
    else:raise AssertionError("Double wrapping not rejected")
    emit("OVERLAY_TEST_PASS", sourcePreserved=True, noncodingIsolated=True,
         highConfidenceDefectsRejected=True, warningsNotFatal=True)


def read_source(api, revision, path):
    from huggingface_hub import hf_hub_download
    return Path(hf_hub_download(SPACE, path, repo_type="space",
               revision=revision, token=api.token)).read_bytes()


def preflight(api):
    test_overlay()
    revision = api.repo_info(SPACE, repo_type="space").sha
    engine = read_source(api, revision, ENGINE)
    helper_source = Path(__file__).with_name(HELPER).read_bytes()
    existing = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if HELPER in existing:
        old_helper = read_source(api, revision, HELPER)
        if old_helper != helper_source:
            raise RuntimeError("Existing remote helper differs: refusing to overwrite")
    else:
        old_helper = None
    candidate = patch_engine(engine)
    BACKUP.mkdir(parents=True, exist_ok=True)
    (BACKUP/"old-engine.py").write_bytes(engine)
    (BACKUP/"new-engine.py").write_bytes(candidate)
    if old_helper is not None:
        (BACKUP/"old-helper.py").write_bytes(old_helper)
    (BACKUP/"new-helper.py").write_bytes(helper_source)
    receipt = {"revision": revision, "oldEngine":digest(engine),
               "newEngine":digest(candidate), "newHelper":digest(helper_source),
               "helperPreviouslyPresent":old_helper is not None,
               "modelWeightsChanged":False,"hardwareChanged":False,"userDataChanged":False}
    (BACKUP/"receipt.json").write_text(json.dumps(receipt,indent=2))
    emit("PREFLIGHT_PASS", **receipt)


def publish_commit(api, expected, files, message, delete=None):
    from huggingface_hub import CommitOperationAdd, CommitOperationDelete
    if api.repo_info(SPACE,repo_type="space").sha != expected:
        raise RuntimeError("HF Space source changed: refusing stale commit")
    with tempfile.TemporaryDirectory(prefix="swrlz-html-quality-") as folder:
        operations = []
        for name, blob in files.items():
            target=Path(folder)/name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(blob)
            operations.append(CommitOperationAdd(path_in_repo=name,path_or_fileobj=str(target)))
        for name in delete or []:
            operations.append(CommitOperationDelete(path_in_repo=name))
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=expected,
                                 operations=operations,commit_message=message)
    revision = str(result.oid)
    for name, blob in files.items():
        if digest(read_source(api,revision,name)) != digest(blob):
            raise RuntimeError("Published source hash mismatch for " + name)
    emit("SOURCE_HASH_PASS",revision=revision,files=list(files))
    return revision


def ready(api, revision, timeout_seconds=960):
    deadline=time.monotonic()+timeout_seconds
    while time.monotonic()<deadline:
        if api.repo_info(SPACE,repo_type="space").sha!=revision:
            raise RuntimeError("Concurrent Space update during readiness check")
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE+"/api/hf/qwen35-ready",
                         headers=HEADER),timeout=25) as response:
                status=json.load(response)
            if status.get("ready") is True and status.get("model")=="qwen3.5-9b":
                emit("MODEL_READY",revision=revision)
                return
        except Exception:
            pass
        time.sleep(12)
    raise TimeoutError("Resident Qwen3.5-9B did not become ready")


def live_smoke_once():
    """Require one request-ID-matched end-to-end acceptance, never a UI guess."""
    opener=urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    # Anonymous sessions can rotate during a Space rollout. Prime each new
    # attempt with its own cookie jar; never reuse a failed session.
    with opener.open(urllib.request.Request(BASE+"/api/lalm_station/sync",
                     headers=HEADER),timeout=35) as response:
        response.read()
    rid=str(uuid.uuid4())
    tid="swrlz-html-quality-smoke-"+uuid.uuid4().hex
    body={"modelId":"700m","requestId":rid,"threadId":tid,
          "prompt":"Write a short complete HTML page with a working toggle button and responsive CSS.",
          "profileId":"LALM","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
          data=json.dumps(body).encode(),
          headers={**HEADER,"Content-Type":"application/json"})
    with opener.open(req,timeout=45) as response:
        if response.status!=202:
            raise RuntimeError("Live coding request not accepted")
        accepted=json.load(response)
    if accepted.get("requestId")!=rid:
        raise RuntimeError("Synthetic request ID mismatch at acknowledgement")
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    terminal="";delta=[];counts={};last_phase=""
    with opener.open(urllib.request.Request(url,headers=HEADER),timeout=480) as response:
        for raw in response:
            try:event=json.loads(raw)
            except (UnicodeError,ValueError):continue
            if event.get("requestId") and event["requestId"]!=rid:
                raise RuntimeError("Cross-request stream detected")
            kind=str(event.get("type") or "")
            counts[kind]=counts.get(kind,0)+1
            last_phase=str(event.get("phase") or last_phase)
            if kind=="DELTA":delta.append(str(event.get("text") or ""))
            if kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind;break
    final="".join(delta)
    matching=False;validation="";synced_terminal=""
    for _ in range(35):
        with opener.open(urllib.request.Request(BASE+"/api/lalm_station/sync",
                         headers=HEADER),timeout=30) as response:
            state=json.load(response)
        active=state.get("activeGeneration") or {}
        if active.get("requestId")==rid:
            matching=True
            validation=(active.get("candidateValidation") or {}).get("status") or ""
            if not final:final=str(active.get("text") or "")
            if active.get("terminal") and not terminal:
                terminal=str(active.get("terminalType") or "COMPLETE").upper()
            if terminal and validation:break
        # A stale anonymous projection does NOT count as acceptance.
        time.sleep(2)
    findings=diagnose_html_candidate(final)
    emit("SMOKE_RESULT",terminal=terminal,validation=validation,
         finalLength=len(final),matchingRequest=matching,findings=findings,
         streamEvents=counts,lastPhase=last_phase,
         cookieNames=[c.name for handler in opener.handlers
            if hasattr(handler,"cookiejar") for c in handler.cookiejar])
    if terminal not in ("COMPLETE","COMPLETED") or validation!="PASS" or not matching:
        raise RuntimeError("Live coding request not matched to an accepted complete candidate")
    if "<html" not in final.lower() and "<!doctype html" not in final.lower():
        raise RuntimeError("Live output omitted complete HTML")
    if findings["blocking"]:
        raise RuntimeError("Accepted HTML contains definite quality defect")
    emit("LIVE_SMOKE_PASS",codeAccepted=True)


def live_smoke():
    # Known rollout issue: disposable anonymous sessions may disappear when
    # the HF Space restarts. Retry the WHOLE request, not a mismatched stream.
    for attempt in range(1,4):
        try:
            live_smoke_once()
            emit("LIVE_ACCEPTANCE_PASS",attempt=attempt)
            return
        except Exception as exc:
            emit("LIVE_ATTEMPT_FAILED",attempt=attempt,
                 errorType=type(exc).__name__,detail=str(exc)[:240])
            if attempt==3:raise
            time.sleep(12)


def main():
    from huggingface_hub import HfApi
    mode=sys.argv[1:]
    if mode not in (["preflight"],["publish"],["baseline"]):
        raise SystemExit("Usage: preflight|publish|baseline")
    token=os.environ.get("HF_TOKEN")
    if not token:raise RuntimeError("HF_TOKEN required for authoritative source read")
    api=HfApi(token=token)
    if mode==["preflight"]:
        preflight(api)
        return
    if mode==["baseline"]:
        live_smoke()
        return
    if os.environ.get("SWRLZ_HTML_QUALITY_APPROVED")!="1":
        raise RuntimeError("Explicit scoped release approval missing")
    receipt=json.loads((BACKUP/"receipt.json").read_text())
    old=(BACKUP/"old-engine.py").read_bytes()
    updated=(BACKUP/"new-engine.py").read_bytes()
    helper=(BACKUP/"new-helper.py").read_bytes()
    if (digest(old)!=receipt["oldEngine"] or digest(updated)!=receipt["newEngine"]
        or digest(helper)!=receipt["newHelper"]):
        raise RuntimeError("Preflight snapshot integrity failure")
    expected=receipt["revision"]
    if api.repo_info(SPACE,repo_type="space").sha!=expected:
        raise RuntimeError("Space modified since preflight; refuse publish")
    deployed=None
    try:
        deployed=publish_commit(api,expected,{ENGINE:updated,HELPER:helper},
            "§C: source-preserving HTML quality checks and cross-device coding guidance")
        ready(api,deployed)
        live_smoke()
        emit("LIVE_RELEASE_KEPT",revision=deployed,priorRevision=expected)
    except Exception:
        emit("RELEASE_REJECTED",revision=deployed)
        if deployed and api.repo_info(SPACE,repo_type="space").sha==deployed:
            restore={ENGINE:old}
            delete=[]
            if receipt["helperPreviouslyPresent"]:
                restore[HELPER]=(BACKUP/"old-helper.py").read_bytes()
            else:
                delete=[HELPER]
            previous=publish_commit(api,deployed,restore,
                "Rollback §C HTML quality release to exact previous engine",delete=delete)
            ready(api,previous)
            emit("ROLLBACK_APPLIED",revision=previous)
        elif deployed:
            emit("ROLLBACK_BLOCKED_CONCURRENT_SOURCE_CHANGE")
        raise

if __name__=="__main__":main()
