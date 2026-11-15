#!/usr/bin/env python3
"""§C compact, source-preserving HTML generation profile.

Keep the coder's existing full output budget, code validator, checkpointing,
repair policy, model runtime and actual project source intact. Only replace
unrelated prompt boilerplate for bounded standalone HTML tasks and revisions.
"""
import ast,hashlib,json,os,re,sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
FILE="qwen_coder_engine.py"
OUT=Path("reports/swrlz-compact-web-profile")
MARK="swrlz-compact-web-profile-v1"
FUNC=r'''def _swrlz_compact_web_profile_eligible(prompt,programming,payload,history,source_change_mode):
    """Only ordinary small HTML pages: not projects, imports, repairs or large source."""
    if source_change_mode or not isinstance(programming,dict) or not programming.get("codingTask"):
        return False
    if not isinstance(payload,dict):
        return False
    contract=programming.get("intentContract") or {}
    language=contract.get("languageContract") or {}
    if language.get("artifactType")!="web-page":
        return False
    if len(str(prompt or ""))>500:
        return False
    if not re.search(
        r"(?i)\b(?:small|short|simple|single[- ]file|single[- ]page|one[- ]page|"
        r"html|counter|color picker|two[- ]column|button|reset|decrement)\b",prompt):
        return False
    if re.search(
        r"(?i)\b(?:3d|vr|engine|studio|dashboard|framework|multi[- ]page|"
        r"complex|enterprise|production[- ]grade|repository|deploy|backend|"
        r"database|api integration|next\.?js|three\.?js|unity)\b",prompt):
        return False
    if any(payload.get(k) for k in (
        "projectThreadEvidence","projectFileEvidence","githubSourceChangeTask",
        "githubContext","githubAction","nativeEditorEvidence","uploadedFiles",
        "attachments","fileDialogue","codeContinuation","forgeContext",
        "projectImportManifest","visionJobId")):
        return False
    if any(programming.get(k) for k in (
        "failureEvidence","canonicalCarry","needsFailureEvidence",
        "repairDirection","artifactMutationRequested","artifactTargetId")):
        return False
    if len(json.dumps(contract,ensure_ascii=False))>5000:
        return False
    # A small revision can reuse its own full previous source; never compact
    # large or deeply rooted projects just because the latest instruction is short.
    for m in history[-8:]:
        if m.get("role")=="assistant" and len(str(m.get("content") or ""))>10000:
            return False
    return True

def _swrlz_compact_web_system(programming,custom_assistant_profile,user_profile):
    """Brief task-specific system; original user request and source stay in messages."""
    text=(
        "You are §wyrlz. Deliver one COMPLETE, working single-file HTML5 page "
        "in ONE fenced html code block. Use inline CSS and JavaScript, no "
        "frameworks or dependencies unless the user requests them. "
        "Implement every requested interaction using real wired DOM events. "
        "No fake navigation, placeholder buttons, TODOs or invented studios. "
        "Keep scope small when the user requests a small page. "
        "For a revision, preserve ALL existing working functions, names, "
        "styles and controls from the previous complete HTML source in chat "
        "and add exactly the requested change. Return the FULL revised file, "
        "never a fragment, diff, duplicated document or continuation prompt. "
        "Close all tags and code fences. Do not claim execution without a receipt. "
        "Avoid explanatory preambles and redundant CSS. "
        "The user prompt, original constraints and existing source take priority.\n"
        "MANDATORY CODE-TRUTH POLICY:\n"+CODE_TRUTH_POLICY
    )
    contract=(programming.get("intentContract") or {})
    if isinstance(contract,dict):
        # Do not duplicate the original prompt, but retain structured negatives
        # and named API constraints as mandatory acceptance targets.
        constraints={k:v for k,v in contract.items()
                     if k not in ("originalRequest","acceptanceEvidence")}
        if constraints:
            text+="\nUSER ACCEPTANCE CONSTRAINTS:\n"+json.dumps(
                constraints,ensure_ascii=False,separators=(",",":"))
    if custom_assistant_profile:
        text+="\nSAVED CUSTOMIZATION (style only):\n"+custom_assistant_profile[:600]
    if user_profile:
        text+="\nUSER PREFERENCES (non-authoritative):\n"+user_profile[:600]
    return text
'''
INSERT_BEFORE="def _swrlz_compact_standalone_code_system(prompt,programming,"
PROFILE_ANCHOR='''    started=time.perf_counter()
    yield {"type":"STATUS","phase":"LOADING"}'''
PROFILE_REPLACE='''    # swrlz-compact-web-profile-v1: preserve all source and validation paths,
    # but avoid unrelated multi-domain instructions for small HTML pages.
    compact_web_profile=False
    if not simple_code_prefill:
        compact_web_profile=_swrlz_compact_web_profile_eligible(
            prompt,programming,payload,history,source_change_mode)
        if compact_web_profile:
            system=_swrlz_compact_web_system(
                programming,custom_assistant_profile,user_profile)
            yield {"type":"STATUS","phase":"COMPACT_WEB_PROFILE",
                   "reason":"Small HTML source-preserving prompt; existing output budget retained"}
    started=time.perf_counter()
    yield {"type":"STATUS","phase":"LOADING"}'''
FIT_ANCHOR="preserve_latest_code=preserve_existing_source(programming))"
FIT_REPLACE="preserve_latest_code=(preserve_existing_source(programming) or compact_web_profile))"

def one(s,old,new,label):
    n=s.count(old)
    if n!=1:raise RuntimeError(f"Unsafe source mutation, {label} matched {n} times")
    return s.replace(old,new,1)
def sha(b):return hashlib.sha256(b).hexdigest()
def build(raw):
    source=raw.decode("utf-8")
    if MARK in source:raise RuntimeError("Profile already installed")
    source=one(source,INSERT_BEFORE,FUNC+"\n"+INSERT_BEFORE,"helper insertion")
    source=one(source,PROFILE_ANCHOR,PROFILE_REPLACE,"system selection")
    source=one(source,FIT_ANCHOR,FIT_REPLACE,"full previous source retention")
    compile(source,FILE,"exec")
    return source.encode("utf-8")
def tests(after):
    s=after.decode("utf-8")
    tree=ast.parse(s)
    funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    elig=funcs["_swrlz_compact_web_profile_eligible"]
    make=funcs["_swrlz_compact_web_system"]
    gen=funcs["generate_events"]
    ns={"re":re,"json":json,"CODE_TRUTH_POLICY":"Keep complete working code and do not claim to have executed it."}
    exec(compile(ast.Module(body=[elig,make],type_ignores=[]),FILE,"exec"),ns)
    checker=ns[elig.name]
    programming={"codingTask":True,"intentContract":{"languageContract":{"artifactType":"web-page"},
       "negativeConstraints":["no fake links"]}}
    plain={"codingTask":True,"intentContract":{"languageContract":{"artifactType":"script"}}}
    cases=[
      ("Write a short single-file HTML page with one button.",programming,{},[],False,True),
      ("Revise it to add a working Reset button. Give complete HTML.",programming,{},[{"role":"assistant","content":"\x60\x60\x60html\n<html></html>\n\x60\x60\x60"}],False,True),
      ("Create a complete HTML counter with a working + button.",programming,{},[],False,True),
      ("Add responsive two-column CSS cards with one-column mobile layout.",programming,{},[],False,True),
      ("Build a VR studio with a button.",programming,{},[],False,False),
      ("Create a complex dashboard in HTML.",programming,{},[],False,False),
      ("Write a short JavaScript function with one button.",plain,{},[],False,False),
      ("Write a short HTML page",programming,{"githubSourceChangeTask":"candidate"},[],False,False),
      ("Write a short HTML page",programming,{},[],True,False),
      ("Write a short HTML page",programming,{},[{"role":"assistant","content":"a"*10001}],False,False),
      ("Write a short HTML page",programming,{},[],False,True),
    ]
    for p,pr,pl,hi,sc,want in cases:
        actual=checker(p,pr,pl,hi,sc)
        if actual is not want:raise AssertionError(f"Profile scope {p!r} {actual}!={want}")
    msg=ns[make.name](programming,"","")
    for phrase in ("FULL revised file","No fake navigation","MANDATORY CODE-TRUTH","no frameworks".upper()):
        if phrase.lower() not in msg.lower():raise RuntimeError("Missing concise code requirement "+phrase)
    fn=ast.get_source_segment(s,gen) or ""
    if "or compact_web_profile" not in fn:raise RuntimeError("Existing source not protected")
    if '"phase":"COMPACT_WEB_PROFILE"' not in fn:raise RuntimeError("No observable routing")
    if "budget_policy" not in fn or "source_sized_budget(" not in fn:
        raise RuntimeError("Output budget unexpectedly removed")
    print("COMPACT_WEB_PROFILE_STATIC_PASS",len(cases)+6,flush=True)
def preflight(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    source=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    dest=build(source);tests(dest)
    (OUT/"before").mkdir(parents=True,exist_ok=True)
    (OUT/"after").mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).write_bytes(source)
    (OUT/"after"/FILE).write_bytes(dest)
    (OUT/"manifest.json").write_text(json.dumps({"revision":rev,"before":sha(source),
      "after":sha(dest),"file":FILE,"scope":"small HTML profile only"},indent=2)+"\n")
    print("COMPACT_WEB_PREFLIGHT",rev,sha(source),sha(dest),flush=True)
    return rev,source,dest
def publish(api):
    if os.getenv("SWRLZ_COMPACT_WEB_APPROVED")!="1":
        raise RuntimeError("Owner release approval missing")
    if not api.token:raise RuntimeError("Existing HF_TOKEN missing")
    rev,old,new=preflight(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent Space revision changed")
    oid=None
    try:
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
             operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"after"/FILE))],
             commit_message="§C compact web prompt, keep source, budgets, validation intact")
        oid=str(result.oid)
        live=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=oid,token=api.token)).read_bytes()
        if live!=new:raise RuntimeError("Post-publication source checksum mismatch")
        manifest=json.loads((OUT/"manifest.json").read_text())
        manifest["publishedRevision"]=oid
        (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
        print("COMPACT_WEB_PUBLISHED",rev,oid,flush=True)
    except Exception:
        if oid and api.repo_info(SPACE,repo_type="space").sha==oid:
            back=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=oid,
               operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
               commit_message="Rollback §C compact web profile to exact previous source")
            print("COMPACT_WEB_ROLLED_BACK",str(back.oid),flush=True)
        raise
def rollback(api):
    if os.getenv("SWRLZ_COMPACT_WEB_APPROVED")!="1":raise RuntimeError("Missing rollback approval")
    manifest=json.loads((OUT/"manifest.json").read_text())
    published=manifest.get("publishedRevision")
    if not published or api.repo_info(SPACE,repo_type="space").sha!=published:
        raise RuntimeError("Refuse rollback: later HF source modifications exist")
    original=(OUT/"before"/FILE).read_bytes()
    if sha(original)!=manifest["before"]:raise RuntimeError("Rollback snapshot mismatch")
    back=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
       operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
       commit_message="Rollback §C compact web after incomplete guest acceptance")
    verify=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=str(back.oid),token=api.token)).read_bytes()
    if verify!=original:raise RuntimeError("Rollback bytes differ from previous source")
    print("COMPACT_WEB_ACCEPTANCE_ROLLBACK",published,str(back.oid),flush=True)
if __name__=="__main__":
    args=sys.argv[1:] or ["preflight"]
    if args not in (["preflight"],["publish"],["rollback"]):
        raise SystemExit("Use preflight, publish or rollback")
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    if args==["preflight"]:preflight(api)
    elif args==["publish"]:publish(api)
    else:rollback(api)
