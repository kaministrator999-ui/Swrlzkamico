#!/usr/bin/env python3
"""Fix one §C routing bug: a positive feature edit is not a failed repair.

Works against the exact existing Brain source. Preserves the original intent
contract, source, code validation, guest access, and real repair evidence.
"""
from __future__ import annotations
import ast,hashlib,json,os,re,sys,types
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
FILE="brain_programming.py"
OUT=Path("reports/swrlz-feature-vs-repair")
TAG="swrlz-positive-source-edit-not-repair-v1"
OLD='''    canonical_carry=bool(prior_contract) and not new_failure_evidence and not vague_failure and correction_direction and not any(x in p for x in _NEW_PROJECT)'''
NEW='''    # swrlz-positive-source-edit-not-repair-v1: "keep/preserve the page"
    # accompanying a NEW feature is a preservation requirement, not a
    # report of a failed candidate. A genuine bug/error/correction still
    # follows the existing canonical repair lifecycle.
    positive_source_edit=bool(last_artifact or pins) and bool(re.search(
        r"(?i)\\b(?:add|include|introduce|extend|revise|update|change|modify|rename|adjust)\\b",
        text)) and not bool(re.search(
        r"(?i)\\b(?:bug|broken|fails?|failed|failure|error|incorrect|wrong|"
        r"fix|repair|regress(?:ion|ed)?|exception|crash|compil(?:e|ation)|"
        r"not\\s+working|doesn['’]?t\\s+work|still\\s+(?:wrong|broken))\\b",
        text))
    canonical_carry=(bool(prior_contract) and not new_failure_evidence
        and not vague_failure and correction_direction
        and not any(x in p for x in _NEW_PROJECT) and not positive_source_edit)'''
def digest(x):return hashlib.sha256(x).hexdigest()
def candidate(raw):
    s=raw.decode("utf-8")
    if TAG in s:raise RuntimeError("Already applied")
    if s.count(OLD)!=1:raise RuntimeError(f"Live Brain classifier changed: {s.count(OLD)} anchors")
    updated=s.replace(OLD,NEW,1)
    compile(updated,FILE,"exec")
    return updated.encode("utf-8")

def test(actual):
    src=actual.decode("utf-8")
    ast.parse(src)
    import contextlib
    import unittest.mock as mock
    modules={}
    for name in ("source_answer_articulation_v230","programming_repair_context",
                 "response_cognition","application_capabilities"):
        modules[name]=types.ModuleType(name)
    modules["source_answer_articulation_v230"].lesson_kind=lambda *a,**kw:""
    modules["programming_repair_context"].candidate_source_fingerprint=lambda s,*a: digest(str(s).encode())
    modules["response_cognition"].requests_web_source=lambda s:bool(re.search(r"html|web ?page|website",str(s),re.I))
    modules["response_cognition"].requests_source_project=lambda *a:False
    modules["response_cognition"].classify_response_cognition=lambda *a,**kw:{"deliverable":"code"}
    modules["application_capabilities"].apply_application_contract=lambda c,*a,**kw:c
    modules["application_capabilities"].application_source_gaps=lambda *a,**kw:[]
    scope={"__file__":FILE,"__name__":"swrlz_brain_fixture"}
    with mock.patch.dict(sys.modules,modules):
        exec(compile(src,FILE,"exec"),scope)
        scope["_strip_fenced_code"]=lambda value:str(value)
        scope["_candidate_primary_code"]=lambda value:str(value)
        scope["_code_fingerprint"]=lambda value:digest(str(value).encode())
        classify=scope["programming_intent"]
        first="Write a short single-file HTML page with one button that really changes text when clicked. No fake links or libraries."
        html="\x60\x60\x60html\n<!doctype html><html><body><p id='text'>Ready</p><button>Change</button><script>document.querySelector('button').onclick=()=>document.querySelector('#text').textContent='Changed';</script></body></html>\n\x60\x60\x60"
        begin=classify(first,[],[],{})
        assert begin["codingTask"] and begin["changeClass"]=="create"
        hist=[{"role":"user","content":first},{"role":"assistant","content":html}]
        prior={"intentContract":begin["intentContract"]}
        tests=(
            ("Keep the same page and add a Reset button that restores original text. Return complete corrected HTML.","feature",False),
            ("Now add a Reset button, preserving the existing Change button and styling.","feature",False),
            ("Please change only the button label in the existing HTML page.","feature",False),
            ("Still wrong; keep the page and change the button.","create",True),
            ("Please keep everything but make it responsive.","feature",True),
        )
        for text,change,carry in tests:
            outcome=classify(text,hist,[],prior)
            if outcome.get("changeClass")!=change or bool(outcome.get("canonicalCarry"))!=carry:
                raise AssertionError(f"Routing {text!r}: {outcome.get('changeClass')}, {outcome.get('canonicalCarry')}")
            if outcome.get("codingTask") and change=="feature" and not carry:
                original=outcome.get("intentContract") or {}
                if (original.get("languageContract") or {}).get("artifactType")!="web-page":
                    raise AssertionError("Original web-page contract lost")
        broken=classify("Still broken! Keep everything and fix the reset button.",hist,[],prior)
        assert broken.get("changeClass")=="fix" and broken.get("needsFailureEvidence"), broken
        prose=classify("Explain how to fix Python add(a,b), no code yet.",hist,[],prior)
        assert not prose.get("codingTask")
        unrelated=classify("What is the capital of France?",[],[],{})
        assert not unrelated.get("codingTask")
    print("POSITIVE_EDIT_ROUTING_ACCEPTED",len(tests)+4,flush=True)

def preflight(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    old=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    new=candidate(old);test(new)
    (OUT/"before").mkdir(parents=True,exist_ok=True)
    (OUT/"after").mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).write_bytes(old)
    (OUT/"after"/FILE).write_bytes(new)
    (OUT/"manifest.json").write_text(json.dumps({"revision":rev,"file":FILE,
       "before":digest(old),"after":digest(new)},indent=2)+"\n")
    print("POSITIVE_EDIT_PREFLIGHT",rev,digest(old),digest(new),flush=True)
    return rev,old,new
def publish(api):
    if os.getenv("SWRLZ_POSITIVE_EDIT_APPROVED")!="1":
        raise RuntimeError("No explicit release approval")
    if not api.token:raise RuntimeError("Existing HF_TOKEN unavailable")
    rev,old,new=preflight(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent HF release; refuse overwrite")
    oid=None
    try:
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
             operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"after"/FILE))],
             commit_message="§C route new HTML feature edits without unnecessary repair lineage")
        oid=str(result.oid)
        check=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=oid,token=api.token)).read_bytes()
        if check!=new:raise RuntimeError("Published classifier checksum mismatch")
        data=json.loads((OUT/"manifest.json").read_text())
        data["publishedRevision"]=oid
        (OUT/"manifest.json").write_text(json.dumps(data,indent=2)+"\n")
        print("POSITIVE_EDIT_PUBLISHED",rev,oid,flush=True)
    except Exception:
        if oid and api.repo_info(SPACE,repo_type="space").sha==oid:
            undo=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=oid,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
                commit_message="Restore §C prior classifier after unsuccessful publication")
            print("POSITIVE_EDIT_ROLLED_BACK",undo.oid,flush=True)
        raise
def rollback(api):
    if os.getenv("SWRLZ_POSITIVE_EDIT_APPROVED")!="1":raise RuntimeError("No rollback approval")
    data=json.loads((OUT/"manifest.json").read_text())
    oid=data.get("publishedRevision")
    if not oid or api.repo_info(SPACE,repo_type="space").sha!=oid:
        raise RuntimeError("Cannot revert after a concurrent HF update")
    original=(OUT/"before"/FILE).read_bytes()
    if digest(original)!=data["before"]:raise RuntimeError("Prior bytes corrupted")
    result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=oid,
         operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
         commit_message="Rollback §C positive feature routing after live regression")
    actual=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=str(result.oid),token=api.token)).read_bytes()
    if actual!=original:raise RuntimeError("Post-rollback source mismatch")
    print("POSITIVE_EDIT_ACCEPTANCE_ROLLBACK",oid,str(result.oid),flush=True)
if __name__=="__main__":
    mode=sys.argv[1:] or ["preflight"]
    if mode not in (["preflight"],["publish"],["rollback"]):raise SystemExit("preflight|publish|rollback")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode==["preflight"]:preflight(api)
    elif mode==["publish"]:publish(api)
    else:rollback(api)
