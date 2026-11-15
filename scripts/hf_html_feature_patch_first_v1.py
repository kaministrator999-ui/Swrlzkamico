#!/usr/bin/env python3
"""§C source-owned small HTML feature patch fast path.

Reuses existing exact-SHA single-edit project patch module, deterministic
candidate checks, and full-generation fallback. Never rewrites account files.
"""
import ast,hashlib,json,os,re,sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
FILE="qwen_coder_engine.py"
OUT=Path("reports/swrlz-html-feature-patch")
TAG="swrlz-web-feature-patch-first-v1"

HELPERS=r'''# swrlz-web-feature-patch-first-v1
def _swrlz_web_feature_source(history,prompt,programming):
    """Use only the last completed, small, authored HTML file as edit base."""
    if not isinstance(programming,dict) or not programming.get("codingTask"):
        return ""
    if programming.get("changeClass") not in ("feature","refactor"):
        return ""
    if any(programming.get(k) for k in ("failureEvidence","canonicalCarry","needsFailureEvidence")):
        return ""
    if not re.search(r"(?i)\b(?:add|revise|update|change|modify|edit|keep|preserve)\b",prompt):
        return ""
    if re.search(r"(?i)\b(?:new project|new page|from scratch|replace the whole|redesign|"
                 r"rewrite completely|new studio|full application)\b",prompt):
        return ""
    for message in reversed(history[-8:]):
        if message.get("role")!="assistant":
            continue
        source=str(message.get("content") or "").strip()
        if len(source)>9000 or len(source)<90:
            continue
        if not source.lower().startswith("\x60\x60\x60html"):
            continue
        source,closed=_swrlz_close_complete_html_fence(source)
        if closed:
            return source
    return ""

def _swrlz_web_feature_patch(model,source,prompt,programming,cancel_check):
    """One bounded JSON edit; the existing host SHA/anchor validator owns it."""
    from project_code_targeted_repair_v1 import patch_context,apply_patch,TargetedRepairError
    from programming_telemetry import completion_validation,observe_completion_chunk
    import time as _swrlz_time
    current=patch_context(source,[],prompt)
    current[0]["content"]=(
        "You are editing an existing HTML source, NOT regenerating the page. "
        "The source is saved by the host, and the requested edit is the only scope. "
        "Return only ONE valid JSON object with exactly the existing patch fields: "
        "sourceSha256, op (insert_before|insert_after|replace_once|append), "
        "anchor (unique exact source substring), code (minimal replacement or insertion). "
        "Use the exact source SHA supplied in the user context. "
        "Preserve all prior working behavior, CSS, IDs, labels and accessibility. "
        "If adding a control needs DOM wiring too, a single script insertion can "
        "create the control and its event handler together without rewriting "
        "the document. Do not duplicate the HTML file, do not claim any tests "
        "ran, and do not invent features outside the newest user request."
    )
    current[1]["content"]=(
        "CURRENT USER EDIT REQUEST (must be fulfilled): "+str(prompt)[:1000]+
        "\nSOURCE PREVIEW, EXACT SHA AND STRUCTURAL MARKERS:\n"+
        current[1]["content"][:9000]
    )
    allowance=min(1100,CONTEXT_TOKENS-_token_count(model,current)-CONTEXT_SAFETY_TOKENS)
    if allowance<MIN_OUTPUT_TOKENS:
        return None
    started=_swrlz_time.perf_counter()
    observation={"finishReason":None,"requestedMaxTokens":allowance}
    pieces=[]
    for item in model.create_chat_completion(
        messages=current,max_tokens=allowance,temperature=0.12,stream=True
    ):
        if cancel_check():
            return None
        if _swrlz_time.perf_counter()-started>=95:
            return None
        observe_completion_chunk(observation,item)
        choices=item.get("choices") or []
        delta=(choices[0].get("delta") or {}).get("content") if choices else None
        if delta:
            pieces.append(str(delta))
    if observation.get("finishReason")!="stop":
        return None
    try:
        changed,receipt=apply_patch(source,"".join(pieces))
    except (TargetedRepairError,ValueError):
        return None
    validation=completion_validation(
        _candidate_structure_check(changed,programming,[]),observation)
    if validation.get("status")!="PASS":
        return None
    return {
        "source":changed,
        "validation":validation,
        "receipt":receipt,
        "timing":{
            "finishReason":"stop",
            "durationMs":round((_swrlz_time.perf_counter()-started)*1000,3),
            "firstTokenLatencyMs":None,
            "deltaChunks":len(pieces),
            "requestedMaxTokens":allowance
        }
    }
'''
ANCHOR='''def generate_events(payload):'''
INSERT='''            # swrlz-web-feature-patch-first-v1: bounded source-preserving
            # edits are cheaper than regenerating every old HTML byte.
            # A rejected/ambiguous patch changes no source and falls through
            # to the normal coder, validator and checkpoint pipeline.
            if code_delivery and not repair_turn and not source_change_mode:
                feature_source=_swrlz_web_feature_source(history,prompt,programming)
                if feature_source:
                    yield {"type":"STATUS","phase":"SOURCE_FEATURE_PATCH",
                           "reason":"Proposing a single reversible edit against existing HTML"}
                    fast_result=_swrlz_web_feature_patch(
                        model,feature_source,prompt,programming,cancel_check)
                    if cancel_check():return
                    if fast_result:
                        candidate_text=fast_result["source"]
                        candidate_check=fast_result["validation"]
                        attempt=candidate_attempt_receipt(
                            1,"source-preserving-feature-patch",
                            fast_result["timing"],candidate_check,
                            _candidate_fingerprint(candidate_text))
                        candidate_attempts.append(attempt)
                        yield {"type":"CANDIDATE_ATTEMPT","attempt":attempt}
                        yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":1}
                        yield {"type":"CANDIDATE_PREVIEW_DELTA","text":candidate_text,"attempt":1}
                        yield {"type":"CANDIDATE_VALIDATION","validation":candidate_check}
                        first_delta=round((time.perf_counter()-started)*1000,3)
                        yield {"type":"DELTA","text":candidate_text}
                        telemetry=generation_summary(
                            candidate_attempts,
                            total_latency_ms=round((time.perf_counter()-started)*1000,3),
                            load_latency_ms=round((loaded-started)*1000,3),
                            visible_first_delta_latency_ms=first_delta,
                            guarded_turn=True,repair_turn=False,
                            strict_language=strict_language)
                        yield {"type":"GENERATION_TELEMETRY","telemetry":telemetry}
                        yield {"type":"COMPLETED","phase":"COMPLETE",
                               "featurePatch":True,
                               "totalLatencyMs":telemetry["engineTotalLatencyMs"],
                               "loadLatencyMs":telemetry["modelLoadLatencyMs"],
                               "firstDeltaLatencyMs":first_delta}
                        return
                    yield {"type":"STATUS","phase":"SOURCE_FEATURE_PATCH_FALLBACK",
                           "reason":"No fully validated edit; using standard complete-code generation"}
'''
TARGET='''        if guarded_turn:
            repair_target_fp=repair_diagnostic.get("candidateFingerprint") if repair_diagnostic else None'''

def sha(raw):return hashlib.sha256(raw).hexdigest()
def one(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError("Source changed for "+label+" matched="+str(n))
    return s.replace(a,b,1)
def build(raw):
    source=raw.decode("utf-8")
    if TAG in source:raise RuntimeError("Feature patch fast path already installed")
    source=one(source,ANCHOR,HELPERS+"\n\n"+ANCHOR,"functions")
    source=one(source,TARGET,INSERT+TARGET,"guarded coder branch")
    compile(source,FILE,"exec")
    return source.encode("utf-8")
def tests(after):
    s=after.decode("utf-8")
    root=ast.parse(s)
    byname={n.name:n for n in root.body if isinstance(n,ast.FunctionDef)}
    for name in ("_swrlz_web_feature_source","_swrlz_web_feature_patch","generate_events"):
        if name not in byname:raise AssertionError("Missing feature patch function "+name)
    sourcecheck=byname["_swrlz_web_feature_source"]
    ns={"re":re,"_swrlz_close_complete_html_fence":lambda s:(s,True)}
    exec(compile(ast.Module(body=[sourcecheck],type_ignores=[]),FILE,"exec"),ns)
    fn=ns[sourcecheck.name]
    sample="\x60\x60\x60html\n<!doctype html><html><head></head><body><button>Change</button><script>console.log(1)</script></body></html>\n\x60\x60\x60"
    history=[{"role":"user","content":"Write a page"},{"role":"assistant","content":sample}]
    intent={"codingTask":True,"changeClass":"feature"}
    cases=[
      ("Add a Reset button.",intent,history,True),
      ("Revise the page with a Reset button.",intent,history,True),
      ("Write a new page from scratch.",intent,history,False),
      ("Add a Reset button.",{"codingTask":True,"changeClass":"fix"},history,False),
      ("Add a Reset button.",{"codingTask":True,"changeClass":"feature","canonicalCarry":True},history,False),
      ("Add a Reset button.",{"codingTask":False,"changeClass":"feature"},history,False),
      ("Add a Reset button.",intent,[{"role":"assistant","content":"No existing HTML here"}],False),
      ("Add a Reset button.",intent,[{"role":"assistant","content":"\x60\x60\x60html\n"+"x"*9001}],False),
    ]
    for p,intent,history,want in cases:
        got=bool(fn(history,p,intent))
        if got!=want:raise AssertionError(f"Feature patch scope error: {p} {got} != {want}")
    gen=ast.get_source_segment(s,byname["generate_events"]) or ""
    for snippet in ('"phase":"SOURCE_FEATURE_PATCH"', '"phase":"SOURCE_FEATURE_PATCH_FALLBACK"',
                    "if fast_result:", "yield from _swrlz_code_candidate_preview"):
        if snippet not in gen and not (snippet.startswith("yield from") and "_swrlz_code_candidate_preview(" in gen):
            raise AssertionError("Missing feature patch or fallback "+snippet)
    print("HTML_FEATURE_PATCH_STATIC_ACCEPTED",len(cases)+4,flush=True)
def preflight(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    after=build(before);tests(after)
    (OUT/"before").mkdir(parents=True,exist_ok=True)
    (OUT/"after").mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).write_bytes(before);(OUT/"after"/FILE).write_bytes(after)
    (OUT/"manifest.json").write_text(json.dumps({"revision":rev,"before":sha(before),
         "after":sha(after),"file":FILE,"scope":"small HTML revision only"},indent=2)+"\n")
    print("HTML_FEATURE_PATCH_PREFLIGHT",rev,sha(before),sha(after),flush=True)
    return rev,before,after
def publish(api):
    if os.getenv("SWRLZ_FEATURE_PATCH_APPROVED")!="1":
        raise RuntimeError("Explicit release approval missing")
    if not api.token:raise RuntimeError("No HF_TOKEN")
    rev,before,after=preflight(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent Space update")
    oid=None
    try:
        created=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
            operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"after"/FILE))],
            commit_message="§C HTML revise: guarded source-SHA feature patch before full re-generation")
        oid=str(created.oid)
        latest=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=oid,token=api.token)).read_bytes()
        if latest!=after:raise RuntimeError("Published model source differs from checked candidate")
        manifest=json.loads((OUT/"manifest.json").read_text())
        manifest["publishedRevision"]=oid
        (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
        print("HTML_FEATURE_PATCH_PUBLISHED",rev,oid,flush=True)
    except Exception:
        if oid and api.repo_info(SPACE,repo_type="space").sha==oid:
            back=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=oid,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
                commit_message="Rollback §C feature patch fast path to previous source")
            print("HTML_FEATURE_PATCH_ROLLED_BACK",back.oid,flush=True)
        raise
def rollback(api):
    if os.getenv("SWRLZ_FEATURE_PATCH_APPROVED")!="1":raise RuntimeError("Rollback approval missing")
    manifest=json.loads((OUT/"manifest.json").read_text())
    rev=manifest.get("publishedRevision")
    if not rev or api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Refuse rollback after other Space changes")
    original=(OUT/"before"/FILE).read_bytes()
    if sha(original)!=manifest["before"]:raise RuntimeError("Rollback source corrupted")
    done=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
        commit_message="Rollback §C source-preserving feature patch after failed acceptance")
    now=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=str(done.oid),token=api.token)).read_bytes()
    if now!=original:raise RuntimeError("Rolled back bytes not verified")
    print("HTML_FEATURE_PATCH_ACCEPTANCE_ROLLBACK",rev,str(done.oid),flush=True)
if __name__=="__main__":
    args=sys.argv[1:] or ["preflight"]
    if args not in (["preflight"],["publish"],["rollback"]):
        raise SystemExit("Use preflight/publish/rollback")
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    if args==["preflight"]:preflight(api)
    elif args==["publish"]:publish(api)
    else:rollback(api)
