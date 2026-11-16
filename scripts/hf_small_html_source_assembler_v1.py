#!/usr/bin/env python3
"""§C source-assembled HTML for short standalone pages, with safe fallback.

Avoid decoding a redundant full document wrapper on new, small HTML requests:
generate only one bounded page-body insertion, check its exact skeleton SHA,
assemble a complete file on the host, then apply all normal program validators.
Large/new projects, non-HTML and account-owned source remain unchanged.
"""
from __future__ import annotations
import ast,hashlib,json,os,re,sys,types
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
FILE="qwen_coder_engine.py"
OUT=Path("reports/small-html-source-assembler")
MARK="swrlz-small-html-source-assembly-v1"
HELPERS=r'''# swrlz-small-html-source-assembly-v1
_SW_SITE_STARTER=(
    "\x60\x60\x60html file=index.html\n"
    "<!doctype html>\n<html lang=\"en\">\n<head>\n"
    "<meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
    "<title>Interactive Page</title>\n</head>\n<body>\n</body>\n</html>\n"
    "\x60\x60\x60"
)

def _swrlz_small_html_starter_eligible(prompt,programming,payload,history,source_change_mode):
    """Opt-in by actual small standalone HTML request; never source-grounded jobs."""
    if source_change_mode or history or not isinstance(programming,dict):
        return False
    if not programming.get("codingTask") or programming.get("changeClass") not in ("create","feature"):
        return False
    contract=programming.get("intentContract") or {}
    if ((contract.get("languageContract") or {}).get("artifactType")!="web-page"):
        return False
    if not isinstance(prompt,str) or len(prompt)>350:
        return False
    if not re.search(
        r"(?i)\b(?:short|simple|small|single[- ]file|single[- ]page|"
        r"one[- ]page|one button|one page|counter|color picker)\b",prompt):
        return False
    if re.search(
        r"(?i)\b(?:large|complex|studio|dashboard|engine|vr|3d|"
        r"repository|github|framework|multipage|multi-page|"
        r"game|backend|full stack|enterprise|many components|"
        r"import|upload|existing|revise|previous|keep the same|"
        r"production|deployment|next\.js|vue|react)\b",prompt):
        return False
    if isinstance(payload,dict) and any(payload.get(k) for k in (
        "projectFileEvidence","projectImportManifest","uploadedFiles","attachments",
        "codeContinuation","githubSourceChangeTask","githubContext",
        "projectThreadEvidence","projectImportManifest","projectFileEvidence")):
        return False
    if any(programming.get(k) for k in ("canonicalCarry","failureEvidence",
                                        "artifactContinuation","artifactMutationRequested",
                                        "artifactTargetId","newProject")):
        # A simple 'new project' flag may be set by broad standalone prompts,
        # but the only supported case here is a clearly isolated page.
        if any(programming.get(k) for k in ("canonicalCarry","failureEvidence",
                                            "artifactContinuation","artifactMutationRequested",
                                            "artifactTargetId")):
            return False
    return True

def _swrlz_small_html_starter_patch(model,prompt,programming,cancel_check):
    """Generate one SHA-checked body insertion, not a replacement whole project."""
    import hashlib as _hash
    from project_code_targeted_repair_v1 import apply_patch,parse_patch,TargetedRepairError
    from programming_telemetry import observe_completion_chunk,completion_validation
    import time as _clock
    import re as _re
    source=_SW_SITE_STARTER
    sha=_hash.sha256(source.encode("utf-8")).hexdigest()
    messages=[
      {"role":"system","content":(
        "Write ONE JSON source-patch object, and nothing else. "
        "A complete working HTML5 file exists already with head/viewport/title "
        "and an empty body. Only fill the body. Do NOT regenerate the HTML wrapper. "
        "Return EXACT fields sourceSha256, op, anchor, code. "
        "sourceSha256 must be the exact supplied hexadecimal SHA; "
        "op MUST be insert_before; anchor MUST be </body>; "
        "code MUST be one HTML string with all requested working DOM elements, "
        "responsive inline CSS (<style>) and functional inline JavaScript "
        "(<script>) as needed. Implement EVERY requested interaction, "
        "with actual event handlers. Avoid unrelated features, imaginary menus, "
        "new pages, TODOs, filler or excessive CSS. "
        "Never include <!doctype>, <html>, </html>, <body>, or </body> in code. "
        "The host will insert this code into the preexisting HTML and verify it. "
        "No testing or execution claims."
      )},
      {"role":"user","content":(
        "SOURCE SHA256: "+sha+"\n"
        "EXACT ANCHOR: </body>\n"
        "CURRENT HTML: \n"+source+"\n"
        "TASK: "+prompt+"\n"
        "JSON PATCH ONLY:"
      )}
    ]
    allowance=min(2100,CONTEXT_TOKENS-_token_count(model,messages)-CONTEXT_SAFETY_TOKENS)
    if allowance<MIN_OUTPUT_TOKENS:return None
    started=_clock.perf_counter()
    timing={"requestedMaxTokens":int(allowance),"finishReason":None}
    pieces=[];first=None
    for item in model.create_chat_completion(messages=messages,max_tokens=allowance,
                                             temperature=0.18,stream=True):
        if cancel_check():return None
        if _clock.perf_counter()-started>=110:return None
        observe_completion_chunk(timing,item)
        choices=item.get("choices") or []
        part=(choices[0].get("delta") or {}).get("content") if choices else None
        if part:
            if first is None:first=_clock.perf_counter()
            pieces.append(str(part))
    if timing["finishReason"]!="stop":return None
    try:
        patch=parse_patch("".join(pieces))
        if patch["op"]!="insert_before" or patch["anchor"]!="</body>":
            return None
        code=patch["code"]
        if _re.search(r"(?i)<!doctype\b|</?(?:html|body)\b|"
                      r"\x60{3}|<iframe\b|<base\b",code):
            return None
        if len(code)>8000:return None
        candidate,receipt=apply_patch(source,patch)
    except (TargetedRepairError,ValueError):
        return None
    checked=completion_validation(_candidate_structure_check(candidate,programming,[]),
                                  timing)
    if checked.get("status")!="PASS":return None
    timing["durationMs"]=round((_clock.perf_counter()-started)*1000,3)
    timing["firstTokenLatencyMs"]=(round((first-started)*1000,3) if first is not None else None)
    timing["deltaChunks"]=len(pieces)
    return {"source":candidate,"timing":timing,"check":checked,"receipt":receipt}
'''
BEFORE='''def generate_events(payload):'''
ENTRY='''        if guarded_turn:
            repair_target_fp=repair_diagnostic.get("candidateFingerprint") if repair_diagnostic else None'''
INSERT=r'''        # swrlz-small-html-source-assembly-v1: skip full-file decoding
        # only for new, deliberately small pages; preserve the entire normal
        # generation/validation path as fallback when a patch is unsafe.
        if _swrlz_small_html_starter_eligible(
            prompt,programming,payload,history,source_change_mode
        ):
            yield {"type":"STATUS","phase":"SMALL_HTML_SOURCE_PATCH",
                   "reason":"Composing a small page from a verified HTML shell"}
            starter=_swrlz_small_html_starter_patch(model,prompt,programming,cancel_check)
            if cancel_check():return
            if starter:
                candidate_text=starter["source"]
                candidate_check=starter["check"]
                timing=starter["timing"]
                receipt=starter["receipt"]
                fp=_candidate_fingerprint(candidate_text)
                attempt=candidate_attempt_receipt(
                    1,"source-assembled-small-html",timing,candidate_check,fp)
                candidate_attempts.append(attempt)
                yield {"type":"CANDIDATE_ATTEMPT","attempt":attempt}
                yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":1}
                yield {"type":"CANDIDATE_PREVIEW_DELTA",
                       "text":candidate_text,"attempt":1}
                yield {"type":"CANDIDATE_VALIDATION","validation":candidate_check}
                first_delta=round((time.perf_counter()-started)*1000,3)
                yield {"type":"DELTA","text":candidate_text}
                telemetry=generation_summary(
                    candidate_attempts,
                    total_latency_ms=round((time.perf_counter()-started)*1000,3),
                    load_latency_ms=round((loaded-started)*1000,3),
                    visible_first_delta_latency_ms=first_delta,
                    guarded_turn=True,repair_turn=False,strict_language=strict_language)
                yield {"type":"GENERATION_TELEMETRY","telemetry":telemetry}
                yield {"type":"COMPLETED","phase":"COMPLETE",
                       "sourceAssembly":"sha-checked-single-body-insertion",
                       "sourceBytesAdded":receipt["addedBytes"],
                       "totalLatencyMs":telemetry["engineTotalLatencyMs"],
                       "loadLatencyMs":telemetry["modelLoadLatencyMs"],
                       "firstDeltaLatencyMs":first_delta}
                return
            yield {"type":"STATUS","phase":"SMALL_HTML_PATCH_FALLBACK",
                   "reason":"A complete validated source edit was not available; using normal generation"}
'''
def sha(x):return hashlib.sha256(x).hexdigest()
def replace(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"Live coder anchor {label} matched {n}, refuse changes")
    return s.replace(a,b,1)
def candidate(raw):
    s=raw.decode("utf-8")
    if MARK in s:raise RuntimeError("Small HTML assembler already present")
    s=replace(s,BEFORE,HELPERS+"\n\n"+BEFORE,"helper functions")
    s=replace(s,ENTRY,INSERT+ENTRY,"streaming decision")
    compile(s,FILE,"exec")
    return s.encode("utf-8")
def static_tests(raw):
    s=raw.decode("utf-8")
    nodes={n.name:n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
    for name in ("_swrlz_small_html_starter_eligible",
                 "_swrlz_small_html_starter_patch","generate_events"):
        if name not in nodes:raise RuntimeError("Missing compiled function "+name)
    flags={"re":re}
    exec(compile(ast.Module(body=[nodes["_swrlz_small_html_starter_eligible"]],type_ignores=[]),FILE,"exec"),flags)
    eligible=flags["_swrlz_small_html_starter_eligible"]
    pr={"codingTask":True,"changeClass":"create",
        "intentContract":{"languageContract":{"artifactType":"web-page"}}}
    valid=[
        "Write a short single-file HTML page with one working button.",
        "Make a small interactive HTML counter.",
        "Create a simple single-page color picker."
    ]
    invalid=[
        "Build an advanced 3D game engine.",
        "Make a large studio dashboard.",
        "Update my existing HTML project.",
        "Write a complete multi-page web application with backend.",
        "Create a responsive enterprise page with many components."
    ]
    for q in valid:
        if not eligible(q,pr,{},[],""):raise AssertionError("Missed scoped small page "+q)
    for q in invalid:
        if eligible(q,pr,{},[],""):raise AssertionError("Scoped unrelated work "+q)
    if eligible(valid[0],pr,{"projectFileEvidence":"existing"},[],""):
        raise AssertionError("Ignored existing user source")
    if eligible(valid[0],pr,{},[{"role":"user","content":"prior"}],""):
        raise AssertionError("Ignored project conversation history")
    if eligible(valid[0],{"codingTask":False,"changeClass":"none",
       "intentContract":{"languageContract":{"artifactType":"web-page"}}},{},[],""):
        raise AssertionError("Ignored non-coding explanation route")
    fn=ast.get_source_segment(s,nodes["generate_events"]) or ""
    for token in ("SMALL_HTML_SOURCE_PATCH","SMALL_HTML_PATCH_FALLBACK",
                  "sha-checked-single-body-insertion","if starter:"):
        if token not in fn:raise AssertionError("Missing bounded patch branch "+token)
    # Source validity and anti-stale behavior exercise the existing project
    # patch module in the deployment workflow (rather than faking its API).
    print("SMALL_HTML_ASSEMBLER_STATIC_ACCEPTED",len(valid)+len(invalid)+7,flush=True)
def preflight(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    after=candidate(before);static_tests(after)
    (OUT/"before").mkdir(parents=True,exist_ok=True)
    (OUT/"after").mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).write_bytes(before)
    (OUT/"after"/FILE).write_bytes(after)
    (OUT/"manifest.json").write_text(json.dumps(
        {"revision":rev,"file":FILE,"beforeSha256":sha(before),
         "afterSha256":sha(after),"scope":"short standalone HTML generation only"},indent=2)+"\n")
    print("SMALL_HTML_ASSEMBLER_PREFLIGHT",rev,sha(before),sha(after),flush=True)
    return rev,before,after
def publish(api):
    if os.getenv("SWRLZ_SMALL_ASSEMBLER_APPROVED")!="1":raise RuntimeError("Owner approval missing")
    if not api.token:raise RuntimeError("Existing HF_TOKEN unavailable")
    rev,before,after=preflight(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent source edit; refuse to publish")
    newrev=None
    try:
        published=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
           operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"after"/FILE))],
           commit_message="§C assemble small HTML from single SHA-checked functional body patch")
        newrev=str(published.oid)
        actual=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=newrev,token=api.token)).read_bytes()
        if actual!=after:raise RuntimeError("Published bytes mismatch")
        data=json.loads((OUT/"manifest.json").read_text());data["publishedRevision"]=newrev
        (OUT/"manifest.json").write_text(json.dumps(data,indent=2)+"\n")
        print("SMALL_HTML_ASSEMBLER_PUBLISHED",rev,newrev,flush=True)
    except Exception:
        if newrev and api.repo_info(SPACE,repo_type="space").sha==newrev:
            undone=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=newrev,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
                commit_message="Rollback §C short HTML assembler to exact previous source")
            print("SMALL_HTML_ASSEMBLER_ROLLED_BACK",undone.oid,flush=True)
        raise
def rollback(api):
    if os.getenv("SWRLZ_SMALL_ASSEMBLER_APPROVED")!="1":raise RuntimeError("Rollback approval missing")
    data=json.loads((OUT/"manifest.json").read_text())
    published=data.get("publishedRevision")
    if not published or api.repo_info(SPACE,repo_type="space").sha!=published:
        raise RuntimeError("Refuse rollback when HF source has changed elsewhere")
    original=(OUT/"before"/FILE).read_bytes()
    if sha(original)!=data["beforeSha256"]:raise RuntimeError("Source snapshot checksum mismatch")
    undone=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
        operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
        commit_message="Rollback §C small HTML assembler after failed live acceptance")
    actual=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=str(undone.oid),token=api.token)).read_bytes()
    if actual!=original:raise RuntimeError("Rollback source verification failed")
    print("SMALL_HTML_ASSEMBLER_ACCEPTANCE_ROLLBACK",published,str(undone.oid),flush=True)
if __name__=="__main__":
    args=sys.argv[1:] or ["preflight"]
    if args not in (["preflight"],["publish"],["rollback"]):
        raise SystemExit("preflight|publish|rollback")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if args==["preflight"]:preflight(api)
    elif args==["publish"]:publish(api)
    else:rollback(api)
