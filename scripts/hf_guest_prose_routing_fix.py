#!/usr/bin/env python3
"""§C explicit prose-only programming intent repair (one-file HF guarded patch).

Only modifies the existing Space brain_programming.py. No model changes, no new
Space, no auth changes. Preserve exact before bytes and reject concurrent edits.
"""
from __future__ import annotations
import ast
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download

SPACE="kamiloki/Swyrlz"
FILE="brain_programming.py"
MARKER="swrlz-explicit-prose-only-programming-v1"
OUT=Path("reports/chat-prose-routing-release")
ANCHOR="def programming_intent(prompt: str, history: list[dict[str, Any]], pinned_context: list[dict[str, Any]], prior_state: dict[str, Any] | None = None) -> dict[str, Any]:"
OLD='    text=str(prompt or "").strip()\n    p=_norm(text)'
NEW='''    text=str(prompt or "").strip()
    # swrlz-explicit-prose-only-programming-v1: the desired output medium
    # takes precedence over mentioned language names and repair vocabulary.
    if _swrlz_explicit_prose_only_code_turn(text):
        return {
            "schema":"swrlz-programming-intent-v1",
            "codingTask":False,"projectContext":"none","changeClass":"none",
            "artifactContinuation":False,"artifactMutationRequested":False,
            "artifactTargetId":"","artifactTargetMessageId":"","baseRevision":0,
            "baseSourceHash":"","newProject":False,"source":"prose-only-user-direction"
        }
    p=_norm(text)'''
HELPER=r'''def _swrlz_explicit_prose_only_code_turn(text: str) -> bool:
    """An explicit no-source explanation wins over a code topic or language name."""
    source=str(text or "").strip()
    explain=bool(re.search(
        r"\b(?:explain|describe|outline|summari[sz]e|review|discuss|analy[sz]e|tell me|what|how)\b",
        source,re.I))
    no_source=bool(re.search(
        r"\b(?:"
        r"no\s+(?:code|source)(?:\s+yet)?\s*(?=[.!?,;]|$)|"
        r"without\s+(?:writing|showing|providing|generating|including|returning|producing)\s+(?:any\s+)?(?:code|source)\b|"
        r"(?:do\s+not|don't|dont)\s+(?:write|show|provide|generate|include|return|produce)\s+(?:any\s+)?(?:code|source)\b"
        r")",source,re.I))
    # An explicit request to produce source in the same reply still requires
    # the code-generation contract; a prose preface must not override it.
    same_turn_delivery=bool(re.search(
        r"\b(?:then|after(?:ward)?|followed by)\s+(?:also\s+)?"
        r"(?:write|generate|provide|show|implement|return)\s+(?:the\s+)?(?:code|source|function|program)\b",
        source,re.I))
    return explain and no_source and not same_turn_delivery
'''

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def make_candidate(original: bytes) -> bytes:
    source=original.decode("utf-8")
    if MARKER in source:
        raise RuntimeError("Patch marker already present; refuse duplicate change")
    tree=ast.parse(source)
    target=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="programming_intent"),None)
    if target is None:
        raise RuntimeError("Programming intent classifier missing")
    fn=ast.get_source_segment(source,target)
    if not fn or fn.count(OLD)!=1:
        raise RuntimeError("Expected classifier input shape has changed; refuse ungrounded edit")
    if source.count(ANCHOR)!=1:
        raise RuntimeError("Programming intent function anchor ambiguous")
    candidate=source.replace(ANCHOR,HELPER+"\n"+ANCHOR,1)
    candidate=candidate.replace(fn,fn.replace(OLD,NEW,1),1)
    ast.parse(candidate)
    compile(candidate,FILE,"exec")
    return candidate.encode("utf-8")

def static_test(candidate: bytes) -> None:
    code=candidate.decode("utf-8")
    tree=ast.parse(code)
    helper=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_swrlz_explicit_prose_only_code_turn"),None)
    route=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="programming_intent"),None)
    if helper is None or route is None:
        raise RuntimeError("Route/helper missing")
    ns={"re":re}
    exec(compile(ast.Module(body=[helper],type_ignores=[]),FILE,"exec"),ns)
    classifier=ns[helper.name]
    examples=(
        ("An existing Python function add(a, b) incorrectly subtracts. Explain the small repair, no code yet.",True),
        ("I eventually want a JavaScript square(n) function. For now explain the goal WITHOUT writing code.",True),
        ("Describe how to debug this function, don't show code.",True),
        ("Explain this algorithm without providing any source.",True),
        ("Write only the corrected runnable Python function add(a, b).",False),
        ("Now implement square(n) in JavaScript using multiplication.",False),
        ("Write HTML with no code comments.",False),
        ("Explain the fix without writing code; then provide code.",False),
        ("Explain why this code is wrong and then show the corrected function.",False),
        ("What's the weather?",False),
    )
    for prompt,expected in examples:
        actual=classifier(prompt)
        if actual!=expected:
            raise RuntimeError("Prose intent regression "+repr(prompt)+" got="+str(actual))
    body=ast.get_source_segment(code,route) or ""
    if "if _swrlz_explicit_prose_only_code_turn(text):" not in body:
        raise RuntimeError("Classifier does not call helper")
    print("PROSE_ROUTING_STATIC_ACCEPTED",len(examples),flush=True)

def source_state(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    raw=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    return rev,raw

def preflight(api):
    before_rev,before=source_state(api)
    after=make_candidate(before)
    static_test(after)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).parent.mkdir(parents=True,exist_ok=True)
    (OUT/"after"/FILE).parent.mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).write_bytes(before)
    (OUT/"after"/FILE).write_bytes(after)
    (OUT/"manifest.json").write_text(json.dumps({
        "space":SPACE,"path":FILE,"beforeRevision":before_rev,
        "beforeSHA256":sha(before),"afterSHA256":sha(after),"marker":MARKER,
        "scope":"single-file source patch","credentials_in_artifacts":False
    },indent=2)+"\n")
    print("PROSE_ROUTING_PREFLIGHT",json.dumps({"revision":before_rev,"before":sha(before),
         "after":sha(after),"static":"PASS"}),flush=True)
    return before_rev,before,after

def publish(api):
    if os.environ.get("SWRLZ_PROSE_ROUTING_APPROVED")!="1":
        raise RuntimeError("Explicit release approval missing")
    if not api.token:
        raise RuntimeError("Existing HF_TOKEN missing")
    rev,before,after=preflight(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("HF Space changed during candidate build")
    new_rev=None
    try:
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
          operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"after"/FILE))],
          commit_message="§C prose-only intent: honor explain/no-code before coding validation")
        new_rev=str(result.oid)
        live=Path(hf_hub_download(SPACE,FILE,repo_type="space",
                  revision=new_rev,token=api.token)).read_bytes()
        if sha(live)!=sha(after):
            raise RuntimeError("Published exact-source checksum mismatch")
        print("PROSE_ROUTING_PUBLISHED",json.dumps({"before":rev,"after":new_rev,"file":FILE}),flush=True)
        return
    except Exception:
        if new_rev and api.repo_info(SPACE,repo_type="space").sha==new_rev:
            result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new_rev,
              operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
              commit_message="Rollback §C prose routing to exact prior source")
            print("PROSE_ROUTING_ROLLED_BACK",str(result.oid),flush=True)
        raise

def main():
    mode=sys.argv[1:] or ["preflight"]
    if mode not in (["preflight"],["publish"]):
        raise SystemExit("Expected preflight or publish")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode==["preflight"]:
        preflight(api)
    else:
        publish(api)
if __name__=="__main__":
    main()
