#!/usr/bin/env python3
"""Guarded §C conversational no-code routing and output finalization.

The Station selects lfm2_700m_engine for ordinary replies. Patching only
qwen_coder_engine therefore cannot enforce no-code explanatory prose.
"""
from __future__ import annotations
import ast,hashlib,json,os,re,sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
FILE="lfm2_700m_engine.py"
OUT=Path("reports/swrlz-lfm-prose-guard")
MARKER="swrlz-lfm-prose-delivery-v1"
PATCH=r'''
# swrlz-lfm-prose-delivery-v1: explicit prose output wins over coding-topic words.
_swrlz_prior_response_mode_prose_v1=_response_mode
def _response_mode(prompt,programming=None,history=None):
    if isinstance(programming,dict) and programming.get("source")=="prose-only-user-direction":
        return ("RESPONSE MODE: EXPLANATION-ONLY. The user requests a plain-language "
                "description, not a source implementation. Answer the topic directly "
                "without code fences, function bodies, source snippets or executable "
                "examples. Describe the operator or change in words. A future explicit "
                "implementation request follows the normal coding contract.")
    return _swrlz_prior_response_mode_prose_v1(prompt,programming,history)

def _swrlz_lfm_no_code_violation(text):
    return bool(re.search(
        r"(?m)^[ \t]*(?:\x60{3,}|~{3,}|def\s+[A-Za-z_]\w*\s*\(|"
        r"function\s+[A-Za-z_$][\w$]*\s*\(|"
        r"(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=|"
        r"return\s+\S|<(?:html|script|body)\b)",str(text or ""),re.I))

def _swrlz_lfm_prose_sanitize(text):
    source=str(text or "")
    # Do not echo model-authored executable source in a prose-only reply.
    source=re.sub(r"(?ms)^[ \t]*\x60{3,}[^\n]*\n.*?^[ \t]*\x60{3,}[ \t]*(?:\n|$)","\n",source)
    source=re.sub(r"(?ms)^[ \t]*~{3,}[^\n]*\n.*?^[ \t]*~{3,}[ \t]*(?:\n|$)","\n",source)
    lines=[]
    for line in source.splitlines():
        stripped=line.strip()
        if _swrlz_lfm_no_code_violation(stripped):continue
        if stripped.endswith(":") and re.search(
             r"(?i)(for example|as follows|looks like|the fix is|source code|code block)",stripped):
            continue
        lines.append(line)
    result=re.sub(r"\n{3,}","\n\n","\n".join(lines)).strip()
    if _swrlz_lfm_no_code_violation(result) or len(result)<25:
        return ("The change is to replace the incorrect operation with the "
                "intended one. This describes the repair without source code.")
    return result

_swrlz_prior_generate_events_prose_v1=generate_events
def generate_events(payload):
    if not isinstance(payload,dict) or payload.get("githubSourceChangeTask"):
        yield from _swrlz_prior_generate_events_prose_v1(payload)
        return
    current_text=str(payload.get("prompt") or "")
    # Evaluate the CURRENT instruction independently from inherited coding
    # metadata or old artifacts. The source classifier is already source-owned.
    direct_intent=programming_intent(current_text,[],[],{})
    if direct_intent.get("source")!="prose-only-user-direction":
        yield from _swrlz_prior_generate_events_prose_v1(payload)
        return
    effective_payload={**payload,"programmingIntent":direct_intent}
    draft=[]
    for event in _swrlz_prior_generate_events_prose_v1(effective_payload):
        kind=event.get("type") if isinstance(event,dict) else ""
        if kind=="DELTA":
            draft.append(str(event.get("text") or ""))
            continue
        if kind in ("CANDIDATE_PREVIEW_DELTA","CANDIDATE_PREVIEW_RESET"):
            continue
        if kind in ("COMPLETE","COMPLETED"):
            raw="".join(draft).strip()
            final=_swrlz_lfm_prose_sanitize(raw) if _swrlz_lfm_no_code_violation(raw) else raw
            if final:
                yield {"type":"DELTA","text":final}
            yield event
            return
        if kind in ("FAILED","CANCELLED"):
            yield event
            return
        yield event
'''
def digest(raw):return hashlib.sha256(raw).hexdigest()
def build(raw):
    source=raw.decode("utf-8")
    if MARKER in source:raise RuntimeError("Patch already present; refuse duplicate")
    if "def _response_mode(" not in source or "def generate_events(payload):" not in source:
        raise RuntimeError("Expected conversational engine entrypoints missing")
    candidate=source.rstrip()+"\n\n"+PATCH+"\n"
    compile(candidate,FILE,"exec")
    return candidate.encode("utf-8")
def static_acceptance(raw):
    s=raw.decode("utf-8")
    nodes={n.name:n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
    for name in ("_swrlz_lfm_no_code_violation","_swrlz_lfm_prose_sanitize","generate_events","_response_mode"):
        if name not in nodes:raise RuntimeError("Missing generated function "+name)
    ns={"re":re}
    helpers=ast.Module(body=[nodes["_swrlz_lfm_no_code_violation"],nodes["_swrlz_lfm_prose_sanitize"]],type_ignores=[])
    exec(compile(helpers,FILE,"exec"),ns)
    detect=ns["_swrlz_lfm_no_code_violation"];clean=ns["_swrlz_lfm_prose_sanitize"]
    tests=(("Use addition, not subtraction.",False),
      ("Use the plus operator (+).",False),
      ("Below is source:\n\x60\x60\x60python\ndef add(a,b):\n return a+b\n\x60\x60\x60",True),
      ("function square(n) { return n*n; }",True),
      ("def add(a,b):\n return a+b",True),
      ("The function add(a,b) should return the sum.",False))
    for x,y in tests:
        if detect(x)!=y:raise AssertionError("Violation detector mismatch "+repr(x))
    source="To repair it, change subtraction to addition.\n\nFor example:\n\x60\x60\x60python\ndef add(a,b):\n return a-b\n\x60\x60\x60\n\nThat produces the sum."
    result=clean(source)
    if detect(result) or "change subtraction to addition" not in result:
        raise AssertionError("Prose sanitizer failed to preserve explanation")
    # Validate original-event ownership without loading any model.
    def fake(prompt):
        yield {"type":"DELTA","text":"The fix is to use addition.\n\x60\x60\x60python\n"}
        yield {"type":"DELTA","text":"def add(a,b):\n return a+b\n\x60\x60\x60\n"}
        yield {"type":"COMPLETED","phase":"COMPLETE"}
    original=ns["_swrlz_lfm_prose_sanitize"]("".join(x["text"] for x in fake(None) if x["type"]=="DELTA"))
    if detect(original):raise AssertionError("Source leak survived sanitization")
    print("LFM_PROSE_GUARD_STATIC_ACCEPTED",len(tests)+2,flush=True)
def preflight(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    after=build(before);static_acceptance(after)
    (OUT/"before").mkdir(parents=True,exist_ok=True);(OUT/"after").mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).write_bytes(before);(OUT/"after"/FILE).write_bytes(after)
    (OUT/"manifest.json").write_text(json.dumps({"space":SPACE,"file":FILE,"oldRevision":rev,"before":digest(before),"after":digest(after)},indent=2))
    print("LFM_PROSE_GUARD_PREFLIGHT",rev,digest(before),digest(after),flush=True)
    return rev,before,after
def publish(api):
    if os.getenv("SWRLZ_LFM_PROSE_APPROVED")!="1":raise RuntimeError("Explicit owner approval missing")
    if not api.token:raise RuntimeError("Existing Hugging Face secret absent")
    rev,before,after=preflight(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:raise RuntimeError("Concurrent Space update")
    oid=None
    try:
        commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
           operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"after"/FILE))],
           commit_message="§C conversational engine: honor explicit no-code requests before output")
        oid=str(commit.oid)
        live=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=oid,token=api.token)).read_bytes()
        if live!=after:raise RuntimeError("Live source did not match checked candidate")
        print("LFM_PROSE_GUARD_PUBLISHED",rev,oid,flush=True)
    except Exception:
        if oid and api.repo_info(SPACE,repo_type="space").sha==oid:
            rollback=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=oid,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
                commit_message="Rollback §C conversational no-code guard to exact prior source")
            print("LFM_PROSE_GUARD_ROLLBACK",rollback.oid,flush=True)
        raise
if __name__=="__main__":
    mode=sys.argv[1:] or ["preflight"]
    if mode not in (["preflight"],["publish"]):raise SystemExit("Expected preflight|publish")
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    preflight(api) if mode==["preflight"] else publish(api)
