#!/usr/bin/env python3
"""§C explicit prose-only instructions override upstream coding metadata.

One-file source patch, exact HF revision pin, no model/weights/auth changes.
"""
import ast,hashlib,json,os,sys,re
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

HELPER=r'''# swrlz-current-operation-noncode-v2: current requested operation outranks stale coding hints.
def _swrlz_operation_is_noncode(prompt):
    text=" ".join(str(prompt or "").split())[:4000]
    code_ask=bool(re.search(
        r"(?i)\b(?:write|generate|provide|return|show|create|make|build)\b.{0,65}"
        r"\b(?:code|source file|html|css|javascript|typescript|python|script|function|"
        r"app|program|component|webpage|website|api|patch)\b"
        r"|\b(?:implement|compile|commit|deploy|push|fix|patch|edit|modify|update)\b"
        r".{0,85}\b(?:code|source|file|script|function|component|project|"
        r"repository|repo|github|api|html|javascript|python|website|webpage)\b",
        text))
    if code_ask:return False
    music=bool(re.search(r"(?i)\b(?:songs?|music|lyrics?|rap|blues|verses?|chorus|"
                         r"hook|bridge|lullaby|remix|parody|remaster|synth.pop)\b",text))
    operation=bool(re.search(r"(?i)\b(?:write|create|compose|draft|remix|remaster|"
                             r"adapt|parody|revise|rewrite|keep|preserve|change|"
                             r"compare|explain|research|acknowledge|remember|"
                             r"critique|discuss|analy[sz]e|feedback)\b",text))
    advice=bool(re.search(
        r"(?i)\b(?:suggest|list|give|provide|explain|describe|update|revise)\b"
        r".{0,140}\b(?:debugging checks?|checks?|things to inspect|"
        r"diagnostic|causes?|explanation|advice|tips?|steps?)\b",
        text))
    # Explaining message flow, restating a list, or changing one listed task
    # is not permission to generate a source file for the chat project.
    factual_direction=bool(re.search(
        r"(?i)\b(?:state|say|give|explain|what(?:'s| is)|which)\b.{0,170}"
        r"\b(?:client|server|request|response|direction|flow)\b",
        text))
    task_listing=bool(re.search(
        r"(?i)\b(?:list|state|show|give|revise|replace|change|update)\b"
        r".{0,120}\b(?:pending tasks?|tasks?|item\s*[1-9]|numbered list|entry)\b",
        text))
    return bool((music and operation) or advice or factual_direction or task_listing)


'''


# swrlz-standalone-followup-prefill-v1: explain -> compact standalone function.
PREFILL_OLD = '''    if source_change_mode or not programming.get("codingTask") or history:
        return False'''
PREFILL_NEW = r'''    if source_change_mode or not programming.get("codingTask"):
        return False
    # A fresh tiny function after one explanation is not a project edit.
    # Accept only one bounded user/assistant exchange with no prior source.
    if history:
        if not isinstance(history,list) or len(history)!=2:
            return False
        if [str(h.get("role") or "") for h in history if isinstance(h,dict)]!=["user","assistant"]:
            return False
        previous=" ".join(str(h.get("content") or h.get("text") or "") for h in history)
        if len(previous)>1800 or not re.search(
            r"(?i)\b(?:explain|without\s+(?:writing\s+)?code|no\s+code)\b",
            str(history[0].get("content") or history[0].get("text") or "")):
            return False
        if re.search(r"(?i)\x60\x60\x60|<script|(?:def|function|class)\s+\w+\s*\(",
                     previous):
            return False
        if re.search(r"(?i)\b(?:existing\s+(?:file|project)|repository|github|"
                     r"source\s+file|error\s+trace|patch|deployment|refactor)\b",
                     previous):
            return False'''
SIGNATURE_OLD = r'''    if not re.search(r"\b(?:function|method|short|simple|small|snippet|hello world|example)\b",
                     cleaned,re.I):
        return False'''
SIGNATURE_NEW = r'''    if not (re.search(r"\b(?:function|method|short|simple|small|snippet|hello world|example)\b",
                      cleaned,re.I)
            or re.search(r"\b[A-Za-z_]\w{0,32}\(\s*[A-Za-z_]\w{0,32}"
                         r"(?:\s*,\s*[A-Za-z_]\w{0,32}){0,3}\s*\)",cleaned)):
        return False'''
BUDGET_OLD = '''            response_tokens=min(response_tokens,1024)'''
BUDGET_NEW = '''            response_tokens=min(response_tokens,384 if history else 1024)'''
RESUME_OLD = '''    auto_resume_existing_source=bool(code_delivery)'''
RESUME_NEW = '''    # No long-code continuation for a self-contained small function.
    auto_resume_existing_source=bool(code_delivery and not simple_code_prefill)'''

def _replace_once(source, old, new, label):
    if source.count(old)!=1:
        raise RuntimeError("SMALL_FOLLOWUP_SOURCE_DRIFT:"+label+":"+str(source.count(old)))
    return source.replace(old,new,1)


def candidate(original):
    source=original.decode("utf-8")
    if "swrlz-current-operation-noncode-v2" in source:
        raise RuntimeError("Operation-aware classifier already installed")
    if "swrlz-prose-only-response-mode-v1" not in source or "prose_only_output=" not in source:
        raise RuntimeError("Expected live response mode and final output guard absent")
    if MARK not in source:
        if source.count(ANCHOR)!=1:
            raise RuntimeError("Original prose-only precedence seam changed")
        source=source.replace(ANCHOR,PATCH,1)
    # Upgrade deployed original patch; never delete or replace its prior behavior.
    installed='''    if source_change_mode:
        programming={"codingTask":False}'''
    if source.count(installed)!=1:
        raise RuntimeError("Installed live source-change guard drifted")
    injected='''    # swrlz-current-operation-noncode-v2: current music and advice turns are
    # conversation, not code artifacts, unless the user asks for actual code.
    if not source_change_mode and programming.get("codingTask") and _swrlz_operation_is_noncode(prompt):
        programming={**programming,"codingTask":False,
                     "needsFailureEvidence":False,"newProject":False,
                     "source":"current-operation-noncode-v2","changeClass":"explain"}
        yield {"type":"STATUS","phase":"NONCODE_OPERATION_OVERRIDE",
               "reason":"Current user operation is not code generation."}
'''
    source=source.replace(installed,injected+installed,1)
    func='def generate_events(payload):'
    if source.count(func)<1:
        raise RuntimeError("Missing source generation entrypoint")
    source=source.replace(func,HELPER+func,1)
    for old,new,label in (
        (PREFILL_OLD,PREFILL_NEW,"history-gate"),
        (SIGNATURE_OLD,SIGNATURE_NEW,"standalone-signature"),
        (BUDGET_OLD,BUDGET_NEW,"bounded-token-budget"),
        (RESUME_OLD,RESUME_NEW,"continuation-gate"),
    ):
        source=_replace_once(source,old,new,label)
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
    helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef) and
             n.name=="_swrlz_operation_is_noncode"]
    if len(helpers)!=1:raise AssertionError("Missing bounded operation classifier")
    ns={"re":re}
    exec(compile(ast.Module(body=helpers,type_ignores=[]),FILE,"exec"),ns)
    decide=ns["_swrlz_operation_is_noncode"]
    for prompt,expected in [
       ("Now adapt that fictional train-platform blues into an ORIGINAL compact pop song",True),
       ("Update the debugging checks to include overlapping elements and pointer events",True),
       ("Write a full original country song with a chorus",True),
       ("Explain three debugging checks for a mobile web button",True),
       ("In a toy web app a CLIENT sends a JSON request to a SERVER API. State its direction.",True),
       ("Now the server has produced its reply. What is the response direction?",True),
       ("For a hypothetical chat project list exactly three pending tasks.",True),
       ("Revise ONLY task 3; leave tasks 1 and 2 pending.",True),
       ("Write JavaScript code to fix pointer events",False),
       ("Build an HTML lyric editor with JavaScript",False),
       ("Deploy a song generator app to the repository",False),
    ]:
        if decide(prompt)!=expected:
            raise AssertionError("Operation route mismatch: "+repr(prompt))
    if text.count("NONCODE_OPERATION_OVERRIDE")!=1:
        raise AssertionError("Non-code precedence missing from generator")
    compact_helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef)
                     and n.name=="_swrlz_standalone_code_prefill"]
    if len(compact_helpers)!=1:raise AssertionError("Standalone code helper missing")
    ns={"re":re,"json":json}
    exec(compile(ast.Module(body=compact_helpers,type_ignores=[]),FILE,"exec"),ns)
    compact=ns["_swrlz_standalone_code_prefill"]
    prompt="Now implement square(n) in JavaScript using multiplication, in a code block."
    history=[{"role":"user","content":"I eventually want a JavaScript square(n) function. For now explain the goal WITHOUT writing code."},
             {"role":"assistant","content":"The function squares its numeric input by multiplying it by itself."}]
    cases=[
        (prompt,{"codingTask":True},{},history,False,True),
        (prompt,{"codingTask":True},{},[],False,True),
        (prompt,{"codingTask":True},{},history,True,False),
        (prompt,{"codingTask":False},{},history,False,False),
        (prompt,{"codingTask":True,"newProject":True},{},history,False,False),
        (prompt,{"codingTask":True},{},history+[{"role":"user","content":"more"}],False,False),
        (prompt,{"codingTask":True},{},[{"role":"user","content":"Edit my GitHub repository's source file and explain the change."},{"role":"assistant","content":"This requires the project source."}],False,False),
        (prompt,{"codingTask":True},{},[{"role":"user","content":"Explain this source: \x60\x60\x60js function square(n) {return n*n;}"},{"role":"assistant","content":"It squares n."}],False,False),
        ("Deploy a small function to the existing project",{"codingTask":True},{},history,False,False),
        (prompt,{"codingTask":True},{"projectThreadEvidence":{"id":1}},history,False,False),
    ]
    for case in cases:
        *params,expected=case
        if compact(*params)!=expected:
            raise AssertionError("Wrong standalone follow-up route: "+repr(params[0]))
    for required in ("384 if history else 1024","code_delivery and not simple_code_prefill"):
        if required not in source:raise AssertionError("Bounded code delivery missing")
    print("PROSE_OVERRIDE_STATIC_ACCEPTED 34",flush=True)

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
        manifest=json.loads((OUT/"manifest.json").read_text())
        manifest["publishedRevision"]=newrev
        (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
        print("PROSE_OVERRIDE_PUBLISHED",json.dumps({"before":rev,"after":newrev}),flush=True)
    except Exception:
        if newrev and api.repo_info(SPACE,repo_type="space").sha==newrev:
            back=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=newrev,
                 operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
                 commit_message="Rollback §C prose-intent metadata precedence to exact previous source")
            print("PROSE_OVERRIDE_ROLLED_BACK",str(back.oid),flush=True)
        raise

def rollback(api):
    """Revert only the exact source this release published; fail closed on newer revisions."""
    if os.getenv("SWRLZ_PROSE_OVERRIDE_APPROVED")!="1":
        raise RuntimeError("Rollback approval missing")
    manifest=json.loads((OUT/"manifest.json").read_text())
    published=str(manifest.get("publishedRevision") or "")
    if not published or api.repo_info(SPACE,repo_type="space").sha!=published:
        raise RuntimeError("Source changed after our publication; refusing unsafe rollback")
    old=(OUT/"before"/FILE).read_bytes()
    if digest(old)!=manifest["beforeSHA256"]:
        raise RuntimeError("Original source snapshot checksum mismatch")
    result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
             operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
             commit_message="Rollback §C operation intent after live acceptance failure")
    rev=str(result.oid)
    verified=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    if verified!=old:raise RuntimeError("Rollback readback differs from original source")
    print("PROSE_OPERATION_ACCEPTANCE_ROLLBACK",json.dumps({"before":published,"after":rev}),flush=True)


if __name__=="__main__":
    args=sys.argv[1:] or ["preflight"]
    if args not in (["preflight"],["publish"],["rollback"]):raise SystemExit("preflight|publish|rollback")
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    if args==["preflight"]:preflight(api)
    elif args==["publish"]:publish(api)
    else:rollback(api)
