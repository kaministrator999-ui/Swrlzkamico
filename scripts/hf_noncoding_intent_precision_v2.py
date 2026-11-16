#!/usr/bin/env python3
"""Guarded §C non-code intent precedence: prose, planning and original songs.

Patch exactly one existing HF brain_programming.py function, preserve every
unrelated source byte, compile and test before publication. No credentials in
artifacts, and never overwrite a newer Space source revision.
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
MARK="swrlz-noncode-deliverable-precedence-v2"
ROOT=Path("reports/sc-noncode-intent-v2")
ANCHOR=("def programming_intent(prompt: str, history: list[dict[str, Any]], "
        "pinned_context: list[dict[str, Any]], prior_state: dict[str, Any] | None = None) -> dict[str, Any]:")

HELPER=r'''def _swrlz_noncode_deliverable_v2(text: str) -> bool:
    """Select what the user asks to RETURN, not technical nouns in the text.

    Explicit code creation/mutation wins. Songwriting, analyses, scenario
    planning, factual questions and modifications to TEXT lists are non-code.
    """
    body=" ".join(str(text or "").split())
    if not body:
        return False
    # Explicit list edits and debugging advice are text deliverables even
    # when the sentence quotes code names or says "not inspected the code".
    text_revision=bool(re.search(
        r"(?i)\b(?:list\s+exactly\s+(?:these|the|three|\d+)|"
        r"revise\s+only\s+task\s*\d+|"
        r"(?:update|revise)\s+(?:the\s+)?"
        r"(?:debugging|inspection|troubleshooting)\s+(?:checks|steps|advice))\b",
        body))
    if text_revision and not re.search(
        r"(?i)\b(?:write|generate|implement|patch|edit|modify)\b"
        r".{0,65}\b(?:code|source|script|file|function)\b",body):
        return True
    # Never override a request to produce or change executable source.
    code_delivery=bool(re.search(
        r"(?i)\b(?:write|generate|implement|build|create|make|fix|repair|"
        r"refactor|update|edit|modify|return|show|provide|patch|change|add)\b"
        r".{0,100}\b(?:code|source(?:\s+code)?|function|script|program|"
        r"web\s*app|application|webpage|web\s*page|website|component|"
        r"html|javascript|typescript|python|css|api\s+endpoint)\b",body)
        or re.search(r"(?i)\b(?:source\s+code|runnable\s+code|"
                     r"complete\s+html|implement\s+(?:the|this)\s+api)\b",body))
    if code_delivery:
        return False
    music_deliverable=bool(re.search(
        r"(?i)\b(?:write|compose|draft|create|make|generate|revise|rewrite|"
        r"remaster|remix|adapt|transform)\b.{0,200}"
        r"\b(?:original\s+)?(?:song|lyrics?|rap|ballad|lullaby|"
        r"verses?|chorus|hook|parody)\b",body))
    if music_deliverable:
        return True
    # A task-list edit is not the same as editing application source.
    text_list=bool(re.search(
        r"(?i)\b(?:list\s+(?:exactly\s+)?(?:these|the|three|\d+)|"
        r"(?:revise|update|change|replace)\s+(?:only\s+)?task\s*\d+|"
        r"tasks?\s+\d+\s+and\s+\d+|complete\s+updated\s+list)\b",body))
    if text_list:
        return True
    explicit_noncode=bool(re.search(
        r"(?i)\b(?:state|explain|describe|summari[sz]e|compare|report|list|"
        r"outline|discuss|acknowledge|answer|identify|recommend|plan|suggest|"
        r"what\s+is|what\s+are|what's|which\s+(?:one|is)|why|"
        r"how\s+(?:does|do|would)|can\s+we\s+claim|"
        r"give\s+(?:three|\d+)\s+concrete\s+checks|"
        r"change\s+just\s+one\s+constraint|update\s+the\s+checks)\b",body))
    return explicit_noncode
'''

REPLACEMENT=r'''    # swrlz-noncode-deliverable-precedence-v2:
    # A technical SUBJECT is not an instruction to GENERATE source.
    if _swrlz_noncode_deliverable_v2(text):
        return {
            "schema":"swrlz-programming-intent-v1",
            "codingTask":False,"projectContext":"none","changeClass":"none",
            "artifactContinuation":False,"artifactMutationRequested":False,
            "artifactTargetId":"","artifactTargetMessageId":"",
            "baseRevision":0,"baseSourceHash":"","newProject":False,
            "source":"explicit-noncode-deliverable-v2"
        }
    p=_norm(text)'''

def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def candidate(raw: bytes) -> bytes:
    source=raw.decode("utf-8")
    if MARK in source:
        raise RuntimeError("Refusing to repatch already installed intent override")
    tree=ast.parse(source)
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)
               and n.name=="programming_intent"]
    if len(functions)!=1 or source.count(ANCHOR)!=1:
        raise RuntimeError("Unexpected authoritative programming function")
    fn=ast.get_source_segment(source,functions[0])
    old='    p=_norm(text)'
    if not fn or fn.count(old)!=1:
        raise RuntimeError("Expected classifier routing anchor changed")
    amended=fn.replace(old,REPLACEMENT,1)
    source=source.replace(ANCHOR,HELPER+"\n"+ANCHOR,1)
    if source.count(fn)!=1:
        raise RuntimeError("Could not identify unique original classifier")
    source=source.replace(fn,amended,1)
    compile(source,FILE,"exec")
    return source.encode("utf-8")

NONCODE=(
    "In a toy web app the CLIENT browser sends JSON to a SERVER API. State the request direction in one short line.",
    "Now the server has produced its reply. What is the direction of the response? Say the direction directly.",
    "Plan a hypothetical two-device game lobby using phone and VR headset browsers, guest-only, no downloads. Give three checks.",
    "Change just one constraint: desktop browser joins as a third device. Keep guest-only and browser play. Update the checks.",
    "A synthetic build has two failing tests and one passing test. Report what is known and recommend the next verification.",
    "Now three tests pass but nobody has deployed the build. Summarize tests separately from deployment state.",
    "For a hypothetical chat project list exactly these three pending tasks: fix Stop button, improve lyric formatting, change logo.",
    "Revise ONLY task 3: replace change the logo with design a dark-theme icon. Give the complete updated list.",
    "Explain where the comic escalation occurs and what a human would judge about timing. No new lyrics.",
    "Remaster the wording of my original fictional song and preserve the chorus hook exactly.",
    "Adapt that fictional blues into an original pop song with Verse 1, Chorus, Bridge, Final Chorus.",
    "Write a complete original song titled Rain Glass Lantern, with a bridge and recurring chorus.",
    "Simply acknowledge these two original lyrics I wrote; don't produce new lyrics yet.",
    "Explain how to debug why a mobile touch button ignores taps; no code required.",
    "Research AAB blues structure and explain which phrase repeats, with citations.",
    "Suggest three things to inspect when a mobile web button ignores touch. You have not seen my code.",
    "Now the same issue also happens in desktop Chrome. Update the debugging checks to include overlapping elements. You have not inspected any code.",
    "A synthetic performance report shows version A at 140ms and B at 180ms on different hosts. Can we claim a speed improvement?",
)
CODE=(
    "Write the corrected runnable Python function add(a,b).",
    "Now implement square(n) in JavaScript.",
    "Build a working web app with a functional counter.",
    "Create a complete HTML webpage with one functional button.",
    "Fix the code in our web app to handle touches.",
    "Update this JavaScript function to return the correct value.",
    "Refactor the Python script without changing its API.",
    "Show the complete CSS source for this layout.",
    "Please provide code implementing a small song lyrics editor.",
    "Generate a script that tests a browser application.",
    "Write Python code to update debugging checks for the browser.",
    "Explain the fix without writing code, then write the complete Python function.",
)

def tests(raw: bytes) -> None:
    source=raw.decode("utf-8")
    tree=ast.parse(source)
    helper=[n for n in tree.body if isinstance(n,ast.FunctionDef)
            and n.name=="_swrlz_noncode_deliverable_v2"]
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)
               and n.name=="programming_intent"]
    if len(helper)!=1 or len(functions)!=1:
        raise RuntimeError("Source helper or function duplicated/missing")
    ns={"re":re,"_swrlz_explicit_prose_only_code_turn":lambda x:False}
    module=ast.Module(body=ast.parse("from __future__ import annotations").body+
                      helper+functions,type_ignores=[])
    exec(compile(module,FILE,"exec"),ns)
    for prompt in NONCODE:
        if not ns["_swrlz_noncode_deliverable_v2"](prompt):
            raise AssertionError("Non-code classifier rejected "+repr(prompt))
        actual=ns["programming_intent"](prompt,[],[],{})
        if actual.get("codingTask") is not False or actual.get("source")!="explicit-noncode-deliverable-v2":
            raise AssertionError("Classifier entered programming mode for "+repr(prompt))
    for prompt in CODE:
        if ns["_swrlz_noncode_deliverable_v2"](prompt):
            raise AssertionError("Actual code deliverable was suppressed: "+repr(prompt))
    print("NONCODE_DELIVERABLE_REGRESSIONS_PASS",
          len(NONCODE),len(CODE),flush=True)

def source_snapshot(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    raw=Path(hf_hub_download(SPACE,FILE,repo_type="space",
                            revision=rev,token=api.token)).read_bytes()
    return rev,raw

def stage(api):
    rev,original=source_snapshot(api)
    revised=candidate(original)
    tests(revised)
    (ROOT/"before").mkdir(parents=True,exist_ok=True)
    (ROOT/"after").mkdir(parents=True,exist_ok=True)
    (ROOT/"before"/FILE).write_bytes(original)
    (ROOT/"after"/FILE).write_bytes(revised)
    (ROOT/"manifest.json").write_text(json.dumps({
        "revision":rev,"file":FILE,"before":digest(original),
        "after":digest(revised),"marker":MARK},indent=2)+"\n")
    print("NONCODE_INTENT_PREFLIGHT",rev,digest(original),digest(revised),flush=True)
    return rev,original,revised

def publish(api):
    if os.getenv("SWRLZ_NONCODE_INTENT_APPROVED")!="1":
        raise RuntimeError("Explicit approved release gate absent")
    if not api.token:
        raise RuntimeError("Hugging Face connection token absent")
    rev,before,after=stage(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent live Space source modification")
    newrev=None
    try:
        commit=api.create_commit(repo_id=SPACE,repo_type="space",
            parent_commit=rev,operations=[CommitOperationAdd(
                path_in_repo=FILE,path_or_fileobj=str(ROOT/"after"/FILE))],
            commit_message="§C non-code deliverables must not enter code generation")
        newrev=str(commit.oid)
        check=Path(hf_hub_download(SPACE,FILE,repo_type="space",
                                  revision=newrev,token=api.token)).read_bytes()
        if check!=after:
            raise RuntimeError("Published source content mismatch")
        manifest=json.loads((ROOT/"manifest.json").read_text())
        manifest["publishedRevision"]=newrev
        (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
        print("NONCODE_INTENT_PUBLISHED",rev,newrev,flush=True)
    except Exception:
        if newrev and api.repo_info(SPACE,repo_type="space").sha==newrev:
            undo=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=newrev,
                operations=[CommitOperationAdd(path_in_repo=FILE,
                path_or_fileobj=str(ROOT/"before"/FILE))],
                commit_message="Rollback failed §C programming-intent patch")
            print("NONCODE_INTENT_PUBLISH_ROLLBACK",str(undo.oid),flush=True)
        raise

def rollback(api):
    if os.getenv("SWRLZ_NONCODE_INTENT_APPROVED")!="1":
        raise RuntimeError("Rollback requires the authorized release")
    manifest=json.loads((ROOT/"manifest.json").read_text())
    published=manifest.get("publishedRevision")
    if not published or api.repo_info(SPACE,repo_type="space").sha!=published:
        raise RuntimeError("Refuse to revert another actor's later Space revision")
    original=(ROOT/"before"/FILE).read_bytes()
    if digest(original)!=manifest["before"]:
        raise RuntimeError("Archived source integrity mismatch")
    commit=api.create_commit(repo_id=SPACE,repo_type="space",
        parent_commit=published,operations=[CommitOperationAdd(
            path_in_repo=FILE,path_or_fileobj=str(ROOT/"before"/FILE))],
        commit_message="Rollback §C non-code intent after failed live acceptance")
    published_bytes=Path(hf_hub_download(SPACE,FILE,repo_type="space",
          revision=str(commit.oid),token=api.token)).read_bytes()
    if published_bytes!=original:
        raise RuntimeError("Rollback source bytes not restored")
    print("NONCODE_INTENT_ACCEPTANCE_ROLLBACK",published,str(commit.oid),flush=True)

if __name__=="__main__":
    cmd=sys.argv[1:] or ["preflight"]
    if cmd not in (["preflight"],["publish"],["rollback"]):
        raise SystemExit("preflight|publish|rollback")
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    if cmd==["preflight"]:
        stage(api)
    elif cmd==["publish"]:
        publish(api)
    else:
        rollback(api)
