#!/usr/bin/env python3
"""§C explicit prose-only instructions override upstream coding metadata.

One-file source patch, exact HF revision pin, no model/weights/auth changes.
"""
import ast,hashlib,json,os,sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
FILE="qwen_coder_engine.py"
OUT=Path("reports/prose-intent-override-v1")
MARK="swrlz-prose-intent-payload-precedence-v1"
ANCHOR='''    programming=payload.get("programmingIntent") if isinstance(payload.get("programmingIntent"),dict) else programming_intent(prompt,history,payload.get("pinnedContext") if isinstance(payload.get("pinnedContext"),list) else [],payload.get("priorProgrammingState") if isinstance(payload.get("priorProgrammingState"),dict) else {})
    if source_change_mode:'''
PATCH='''    programming=payload.get("programmingIntent") if isinstance(payload.get("programmingIntent"),dict) else programming_intent(prompt,history,payload.get("pinnedContext") if isinstance(payload.get("pinnedContext"),list) else [],payload.get("priorProgrammingState") if isinstance(payload.get("priorProgrammingState"),dict) else {})
    # swrlz-prose-intent-payload-precedence-v1: a caller-provided codingTask
    # flag is metadata, not permission to disregard an explicit no-code turn.
    # The current user request wins; do not discard real coding requests.
    if not source_change_mode and programming.get("source")!="prose-only-user-direction":
        direct_intent=programming_intent(prompt,[],[],{})
        if direct_intent.get("source")=="prose-only-user-direction":
            programming=direct_intent
            yield {"type":"STATUS","phase":"PROSE_USER_OVERRIDE",
                   "reason":"Explicit explanation-only output contract took precedence over caller metadata."}
    if source_change_mode:'''

def digest(x):return hashlib.sha256(x).hexdigest()

def candidate(original):
    source=original.decode("utf-8")
    if MARK in source:raise RuntimeError("Patch already installed")
    if "swrlz-explicit-prose-finalizer-v1" not in source:
        raise RuntimeError("Expected no-code delivery guard not present")
    if source.count(ANCHOR)!=1:
        raise RuntimeError("Unsafe mutation: authoritative intent assignment changed")
    source=source.replace(ANCHOR,PATCH,1)
    compile(source,FILE,"exec")
    return source.encode("utf-8")

def tests(content):
    source=content.decode()
    tree=ast.parse(source)
    fn=next((x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="generate_events"),None)
    if not fn:raise RuntimeError("Model generation entrypoint missing")
    text=ast.get_source_segment(source,fn) or ""
    for check in ('direct_intent=programming_intent(prompt,[],[],{})',
                  'direct_intent.get("source")=="prose-only-user-direction"',
                  'yield {"type":"STATUS","phase":"PROSE_USER_OVERRIDE"',
                  'if not source_change_mode','if source_change_mode:'):
        if check not in text:raise RuntimeError("Missing intent-boundary contract: "+check)
    # Exercise the exact override condition without loading model weights.
    def decision(source_change_mode,caller_source,direct_source):
        return not source_change_mode and caller_source!="prose-only-user-direction" and direct_source=="prose-only-user-direction"
    for source_change,caller,direct,expected in [
      (False,"brain-router","prose-only-user-direction",True),
      (False,"brain-router","brain-router",False),
      (False,"prose-only-user-direction","prose-only-user-direction",False),
      ("candidate","brain-router","prose-only-user-direction",False),
      ("plan","brain-router","prose-only-user-direction",False)
    ]:
        if decision(source_change,caller,direct)!=expected:
            raise AssertionError("No-code precedence regression")
    print("PROSE_OVERRIDE_STATIC_ACCEPTED 10",flush=True)

def preflight(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    after=candidate(before)
    tests(after)
    (OUT/"before").mkdir(parents=True,exist_ok=True)
    (OUT/"after").mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).write_bytes(before)
    (OUT/"after"/FILE).write_bytes(after)
    (OUT/"manifest.json").write_text(json.dumps({"space":SPACE,"file":FILE,"revision":rev,
         "beforeSHA256":digest(before),"afterSHA256":digest(after)},indent=2)+"\n")
    print("PROSE_OVERRIDE_PREFLIGHT",json.dumps({"revision":rev,"before":digest(before),"after":digest(after)}),flush=True)
    return rev,before,after

def publish(api):
    if os.environ.get("SWRLZ_PROSE_OVERRIDE_APPROVED")!="1":
        raise RuntimeError("Explicit owner approval required")
    if not api.token:raise RuntimeError("Existing HF_TOKEN unavailable")
    rev,before,after=preflight(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("HF Space updated during guarded preparation")
    newrev=None
    try:
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
              operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"after"/FILE))],
              commit_message="§C respect no-code explanation over inherited programming intent")
        newrev=str(result.oid)
        live=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=newrev,token=api.token)).read_bytes()
        if live!=after:raise RuntimeError("Published bytes differed from candidate")
        print("PROSE_OVERRIDE_PUBLISHED",json.dumps({"before":rev,"after":newrev}),flush=True)
    except Exception:
        if newrev and api.repo_info(SPACE,repo_type="space").sha==newrev:
            back=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=newrev,
                 operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
                 commit_message="Rollback §C prose-intent metadata precedence to exact previous source")
            print("PROSE_OVERRIDE_ROLLED_BACK",str(back.oid),flush=True)
        raise

if __name__=="__main__":
    args=sys.argv[1:] or ["preflight"]
    if args not in (["preflight"],["publish"]):raise SystemExit("preflight|publish")
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    preflight(api) if args==["preflight"] else publish(api)
