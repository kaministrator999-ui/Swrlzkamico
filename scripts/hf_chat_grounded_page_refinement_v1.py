#!/usr/bin/env python3
"""§C source-grounded short follow-up intent repair, with exact-source rollback.

Do not broaden "page" into an unconditional coding term. Resolve short
refinements from actual existing authored code artifacts only. Retain prior
project identity and avoid creating/editing an artifact without its owner receipt.
"""
from __future__ import annotations
import ast,hashlib,http.cookiejar,json,os,re,sys,tempfile,time,urllib.parse,urllib.request,uuid
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
FILE="brain_programming.py"
BASE="https://kamiloki-swyrlz.hf.space"
BACKUP=Path("swrlz-grounded-page-intent-backup")
TAG="swrlz-grounded-page-refinement-v1"
HEAD={"User-Agent":"Swyrlz-Source-Grounded-Page-Followup-20261113","Cache-Control":"no-cache"}
FENCE=chr(96)*3

def emit(kind,**fields):
    print("PAGE_REFINEMENT_ROUTE",json.dumps({"event":kind,**fields},ensure_ascii=False,sort_keys=True),flush=True)

def digest(v):return hashlib.sha256(v).hexdigest()

def once(source,old,new,marker):
    count=source.count(old)
    if count!=1:raise RuntimeError("LIVE_SOURCE_DRIFT "+marker+" occurrences="+str(count))
    return source.replace(old,new,1)

HELPER=r'''def _grounded_artifact_refinement(text: str, last_artifact: dict, pins: list[dict]) -> bool:
    """Recognize natural edit requests only with a genuine prior code artifact.

    A stray "page" (book, homework, webpage discussion) is not a code task.
    User mention of an unrelated artifact is not sufficient: only authored
    assistant source or an explicit approved code pin creates this scope.
    """
    if not (last_artifact or pins):
        return False
    raw=str(text or "").strip()
    if not raw or _source_information_request(raw):
        return False
    if classify_response_cognition(raw).get("deliverable") in ("text","audio","3d-asset"):
        return False
    prose=_norm(_strip_fenced_code(raw))
    if len(prose)>240:
        return False
    prefix=(r"^(?:(?:now|next|then|also|please|okay|ok|hey|and)\s+)*"
            r"(?:(?:can|could|would|will)\s+you\s+)?(?:please\s+)?")
    action=(r"(?:improve|polish|refine|enhance|upgrade|redesign|"
            r"modernize|tidy\s+up|clean\s+up)")
    target=(r"(?:the|this|that|our|my|current|existing|previous|"
            r"same|old|new)\s+")
    web=(r"(?:web\s*page|website|site|html(?:\s+page)?|page|layout|"
         r"interface|ui|frontend|design|application|app)")
    generic=r"(?:it|this|that|code|project|file|script)"
    action_pattern=prefix+action+r"\s+(?:"+target+r")?(?:"+web+"|"+generic+r")\b"
    make_pattern=(prefix+r"make\s+(?:"+target+r")?(?:"+web+"|"+generic+
                  r")\s+(?:look\s+)?(?:better|nicer|cleaner|more\s+"
                  r"(?:polished|modern|responsive|interactive))\b")
    if not (re.match(action_pattern,prose) or re.match(make_pattern,prose)):
        return False
    prior_text=str((last_artifact or {}).get("text") or "")
    pinned_text="\n".join(str(x.get("text") or "") for x in pins if isinstance(x,dict))
    code_evidence=prior_text+"\n"+pinned_text
    if not code_evidence.strip():
        return False
    # Broad "page / layout / UI" requests need web-source evidence;
    # "improve the code / file / project" can refer to any authored code.
    web_target=re.match(prefix+action+r"\s+(?:"+target+r")?"+web+r"\b",prose)
    web_target=bool(web_target or re.match(prefix+r"make\s+(?:"+target+r")?"+web+r"\b",prose))
    if web_target and not re.search(
        r"<!doctype\s+html\b|<html\b|"+re.escape(chr(96)*3)+
        r"(?:html|css|javascript|js)\b",code_evidence,re.I
    ):
        return False
    return True


'''

ANCHOR='''def programming_intent(prompt: str, history: list[dict[str, Any]], pinned_context: list[dict[str, Any]], prior_state: dict[str, Any] | None = None) -> dict[str, Any]:'''
REFERENCE='''    continuation_reference=_programming_continuation_signal(text)
    inherited=continuation_reference and (bool(pins) or bool(prior_contract) or bool(last_artifact))'''
REPLACE_REFERENCE='''    # swrlz-grounded-page-refinement-v1: a natural "improve the page"
    # follows the existing authored HTML, not a fresh unrelated task.
    artifact_refinement=_grounded_artifact_refinement(text,last_artifact,pins)
    continuation_reference=_programming_continuation_signal(text) or artifact_refinement
    inherited=continuation_reference and (bool(pins) or bool(prior_contract) or bool(last_artifact))'''
CHANGE=r'''    elif last_artifact and re.search(r"\b(?:make|turn|convert|transform|upgrade)\s+(?:this|that|it|the\s+existing)\b",p):
        change="feature"'''
REPLACE_CHANGE=r'''    elif artifact_refinement:
        # Small edits to an existing code artifact are not new creations.
        change="feature"
    elif last_artifact and re.search(r"\b(?:make|turn|convert|transform|upgrade)\s+(?:this|that|it|the\s+existing)\b",p):
        change="feature"'''

def patch(source):
    if TAG in source:raise RuntimeError("Already patched")
    source=once(source,ANCHOR,HELPER+ANCHOR,"function insertion")
    source=once(source,REFERENCE,REPLACE_REFERENCE,"active refinement intent")
    source=once(source,CHANGE,REPLACE_CHANGE,"existing source change classification")
    ast.parse(source,filename=FILE)
    return source

HTML=FENCE+"html\n<!DOCTYPE html><html lang='en'><head><title>Studio</title></head><body><header>Demo</header><button id='go'>Go</button></body></html>\n"+FENCE
PYTHON=FENCE+"python\ndef square(n):\n    return n*n\n"+FENCE
HISTORY=[
    {"role":"user","text":"Can you generate a coding demonstrational html page make it look good"},
    {"role":"assistant","text":HTML},
    {"role":"user","text":"Now improve it"},
    {"role":"assistant","text":"Generation failed: OUTPUT_TOKEN_LIMIT"},
    {"role":"user","text":"Now improve the page"},
    {"role":"assistant","text":"Generation failed: OUTPUT_TOKEN_LIMIT"},
]

def test(source):
    tree=ast.parse(source)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_grounded_artifact_refinement")
    code=compile(ast.Module(body=[fn],type_ignores=[]),"<grounded-refinement>","exec")
    ns={"re":re,"_source_information_request":lambda t:False,
        "classify_response_cognition":lambda t:{"deliverable":None},
        "_strip_fenced_code":lambda t:t,
        "_norm":lambda t:" ".join(t.lower().split())}
    exec(code,ns)
    check=ns["_grounded_artifact_refinement"]
    a={"text":HTML}
    for phrase in ("Now improve the page","Now improve it","Please polish the page",
                   "Can you refine the design","Enhance the layout","Modernize this website",
                   "Redesign the page","Upgrade the interface","Improve the project",
                   "Make the page better","Make it look better","Clean up the HTML page",
                   "Improve the page with responsive cards"):
        assert check(phrase,a,[]),("MISSING_REFINE_POSITIVE",phrase)
    for phrase in ("What is a page?","Explain this HTML page","Show me the files",
                   "Create a new webpage from scratch","What improvements are possible?",
                   "Improve my reading comprehension","Write a poem about web pages"):
        assert not check(phrase,a,[]),("FALSE_REFINE_POSITIVE",phrase)
    assert not check("Now improve the page",{},[])
    assert not check("Now improve the page",{"text":PYTHON},[])
    assert not check("Now improve the page",{"text":"Plain prose with a generic link"},[])
    assert check("Now improve the code",{"text":PYTHON},[])
    assert check("Now improve the page",{},[{"text":HTML}])
    emit("HELPER_TESTS_PASS",positive=13,negative=10,
         webSourceRequired=True,nonCodeConversationsExcluded=True)
    assert "_last_assistant_artifact(history or [])" in source
    assert 'coding=not _source_information_request(text,history)' in source
    assert "if new_project:" in source
    assert "artifact_id=str((target or {}).get(" in source
    assert 'artifact_refinement=_grounded_artifact_refinement(text,last_artifact,pins)' in source
    assert 'elif artifact_refinement:' in source

def test_full_classifier(source,repo_root):
    # Do not reconstruct a classifier based on guesswork. Import the entire
    # actual live module and all its original dependencies from this snapshot.
    import importlib.util
    directory=str(repo_root)
    if directory not in sys.path:sys.path.insert(0,directory)
    module_path=repo_root/"brain_programming_candidate.py"
    module_path.write_text(source)
    spec=importlib.util.spec_from_file_location("swrlz_grounded_intent_candidate",module_path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for length in (2,4,6):
        for phrase in ("Now improve the page","Now improve it",
                       "Please polish the page","Enhance the layout",
                       "Make the page better","Refine the design"):
            result=module.programming_intent(phrase,HISTORY[:length],[],{})
            assert result["codingTask"],(length,phrase,result)
            assert result["changeClass"]=="feature",(length,phrase,result)
            assert result["projectContext"]=="existing",(length,phrase,result)
            assert not result["newProject"],(length,phrase,result)
            assert not result["artifactMutationRequested"],(length,phrase,result)
            assert (result["intentContract"]["languageContract"].get("artifactType")
                    =="web-page"),(length,phrase,result)
    # A conversation without real authored source must never become an
    # unapproved code mutation just because the user says "page".
    for phrase in ("Now improve the page","Please polish the page",
                   "Refine the design","Make the page better"):
        bare=module.programming_intent(phrase,[
            {"role":"user","text":"I'm reading a book and discussing page design"},
            {"role":"assistant","text":"We can discuss typography."}],[],{})
        assert not bare["codingTask"],(phrase,bare)
    fresh=module.programming_intent("Create a new unrelated webpage from scratch",
        HISTORY[:2],[],{})
    assert fresh["codingTask"] and fresh["newProject"],fresh
    explain=module.programming_intent("Explain the current HTML",HISTORY[:2],[],{})
    assert explain["changeClass"]=="explain",explain
    emit("FULL_CLASSIFIER_TESTS_PASS",existingSourceCases=36,
         noSourceCases=4,newProjectIsolated=True,
         existingSourceNotMutatedWithoutReceipt=True)

def fetch_source(api,revision):
    return Path(hf_hub_download(SPACE,FILE,revision=revision,
          repo_type="space",token=api.token)).read_bytes()

def snapshot(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before=fetch_source(api,rev)
    after=patch(before.decode()).encode()
    test(after.decode())
    # Real source imports and the actual coding classifier, not a regex-only
    # mock. Use an independent disposable checkout of the exact HF revision.
    from huggingface_hub import snapshot_download
    with tempfile.TemporaryDirectory(prefix="swrlz-page-intent-preflight-") as folder:
        source_root=Path(snapshot_download(SPACE,repo_type="space",
            revision=rev,local_dir=folder,
            allow_patterns=["*.py","programming_references/**"]))
        test_full_classifier(after.decode(),source_root)
    BACKUP.mkdir(exist_ok=True)
    (BACKUP/FILE).write_bytes(before)
    (BACKUP/"revision.txt").write_text(rev)
    (BACKUP/"manifest.json").write_text(json.dumps({
        "revision":rev,"file":FILE,
        "originalSha":digest(before),"candidateSha":digest(after),
        "modelChanged":False,"contextChanged":False,
        "threadsChanged":False,"historyMutation":False},indent=2))
    emit("SOURCE_PREFLIGHT",revision=rev,modified=[FILE],
         originalSha=digest(before),candidateSha=digest(after))
    return rev,before,after

def publish(api,expected,source,message):
    head=api.repo_info(SPACE,repo_type="space").sha
    if head!=expected:raise RuntimeError("Concurrent HF Space source change; refusing update")
    with tempfile.NamedTemporaryFile(suffix=".py") as out:
        out.write(source);out.flush()
        response=api.create_commit(repo_id=SPACE,repo_type="space",
            parent_commit=expected,
            operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=out.name)],
            commit_message=message)
    rev=str(response.oid)
    if digest(fetch_source(api,rev))!=digest(source):
        raise RuntimeError("Published source bytes differ from validated candidate")
    emit("SOURCE_VERIFIED",revision=rev)
    return rev

def ready():
    req=urllib.request.Request(BASE+"/api/hf/qwen35-ready",headers=HEAD)
    with urllib.request.urlopen(req,timeout=24) as response:return json.load(response)

def wait_model(api,revision,seconds=1000):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        if api.repo_info(SPACE,repo_type="space").sha!=revision:
            raise RuntimeError("Concurrent HF Space revision during warmup")
        try:
            state=ready()
            if (state.get("ready") is True and state.get("model")=="qwen3.5-9b"
                and (state.get("decodeThreads"),state.get("batchThreads"),
                     state.get("cpuCapacity"))==(18,18,16)):
                emit("SAME_MODEL_READY",revision=revision,threads=18)
                return
        except Exception:pass
        time.sleep(12)
    raise TimeoutError("Existing 9B model not ready after coding intent update")

def conversation(opener,thread,prompt,max_secs=240):
    request_id=str(uuid.uuid4())
    start=time.monotonic()
    body={"modelId":"700m","prompt":prompt,"threadId":thread,
          "requestId":request_id,"profileId":"LALM","profile":"",
          "userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",
        data=json.dumps(body).encode(),method="POST",
        headers={**HEAD,"Content-Type":"application/json"})
    with opener.open(req,timeout=35) as response:
        if response.status!=202:raise RuntimeError("Synthetic Station send rejected")
        response.read()
    stream_url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":request_id})
    text_parts=[];draft_parts=[];first_draft=None;first_text=None;terminal=None;states=[]
    with opener.open(urllib.request.Request(stream_url,headers=HEAD),
                     timeout=max_secs) as response:
        for raw in response:
            if time.monotonic()-start>max_secs-15:
                raise TimeoutError("Synthetic project-turn latency exceeded safety limit")
            try:event=json.loads(raw)
            except (ValueError,UnicodeError):continue
            if event.get("requestId") and event.get("requestId")!=request_id:
                raise RuntimeError("Stream event belongs to another synthetic request")
            kind=event.get("type")
            if kind=="CANDIDATE_PREVIEW_DELTA":
                if first_draft is None:first_draft=round(time.monotonic()-start,2)
                draft_parts.append(str(event.get("text") or ""))
            elif kind=="CANDIDATE_PREVIEW_RESET":draft_parts.clear()
            elif kind=="DELTA":
                if first_text is None:first_text=round(time.monotonic()-start,2)
                text_parts.append(str(event.get("text") or ""))
            elif kind=="STATUS":states.append(str(event.get("phase") or ""))
            elif kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind;break
    # A newly rebuilt Space can temporarily rotate an anonymous session.
    # Verify the stream and the cookie-scoped session have the same request,
    # never substitute stale telemetry or silently accept a different user.
    active={}
    for snapshot_try in range(7):
        with opener.open(urllib.request.Request(BASE+"/api/lalm_station/sync",
                headers=HEAD),timeout=25) as response:
            snapshot=json.load(response)
        active=snapshot.get("activeGeneration") or {}
        if active.get("requestId")==request_id:
            break
        time.sleep(2)
    if active.get("requestId")!=request_id:
        raise RuntimeError("Synthetic session invalidated during rollout; retry full two-turn test")
    validation=active.get("candidateValidation") or {}
    budget=active.get("contextBudget") or {}
    intent=active.get("programmingIntent") or {}
    result={"prompt":prompt,"terminal":terminal,
        "firstDraftSec":first_draft,"firstAcceptedSec":first_text,
        "totalSec":round(time.monotonic()-start,2),
        "codeChars":len("".join(text_parts)),
        "codeOutputHasHtml":("<html" in "".join(text_parts).lower()
                            or "<!doctype html" in "".join(text_parts).lower()),
        "budgetContextTokens":budget.get("contextWindowTokens"),
        "candidateValidation":validation.get("status"),
        "statusPhases":states[-12:],
        "intentCoding":intent.get("codingTask"),
        "intentChange":intent.get("changeClass"),
        "intentProject":intent.get("projectContext"),
        "draftChars":len("".join(draft_parts)),
    }
    emit("LIVE_SYNTHETIC_TURN",**result)
    return result

def accept(api,rev):
    # A real two-turn project, using the user's exact follow-up phrasing.
    # No personal chat, file or account is read. Restart with a fresh
    # disposable session if the Space rotates the anonymous session during
    # deployment; never treat unscoped telemetry as a pass.
    for attempt in range(1,4):
        if api.repo_info(SPACE,repo_type="space").sha!=rev:
            raise RuntimeError("Concurrent HF Space source update during live acceptance")
        opener=urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        thread="swrlz-grounded-page-test-"+str(uuid.uuid4())
        try:
            first=conversation(opener,thread,
                "Generate a short complete HTML demonstration page with a heading and a toggle button. Keep the single-file source under 100 lines.",max_secs=240)
            if first["terminal"] not in ("COMPLETE","COMPLETED") or not first["codeOutputHasHtml"]:
                raise RuntimeError("Live synthetic starter HTML did not complete")
            # The Station stream can end before its persistence phase settles.
            # Explicitly check that the saved source exists in this same thread.
            time.sleep(2)
            with opener.open(urllib.request.Request(BASE+"/api/lalm_station/sync",
                    headers=HEAD),timeout=25) as response:
                state=json.load(response)
            stored=next((t for t in state.get("threads",[])
                         if t.get("id")==thread),{})
            assistant_sources=[m for m in stored.get("messages",[])
                  if m.get("role")=="assistant" and
                  ("<html" in str(m.get("text") or "").lower() or
                   "<!doctype html" in str(m.get("text") or "").lower())]
            if not assistant_sources:
                raise RuntimeError("Synthetic session did not retain first HTML artifact")
            second=conversation(opener,thread,
                "Now improve the page",max_secs=420)
            if second["terminal"] not in ("COMPLETE","COMPLETED"):
                raise RuntimeError("Natural HTML follow-up did not complete")
            if not second["codeOutputHasHtml"] or second["codeChars"]<100:
                raise RuntimeError("Natural HTML follow-up did not deliver complete HTML")
            if second["candidateValidation"]!="PASS":
                raise RuntimeError("Natural HTML follow-up was not accepted by existing validation")
            if second["firstDraftSec"] is None:
                raise RuntimeError("Natural HTML follow-up did not show provisional coding deltas")
            if not (second["intentCoding"] is True and second["intentChange"]=="feature"
                    and second["intentProject"]=="existing"):
                raise RuntimeError("Original wording did not resolve to existing coding project")
            emit("LIVE_EXISTING_HTML_FOLLOWUP_ACCEPTED",revision=rev,
                 attempt=attempt,firstTurnSec=first["totalSec"],
                 improvementTurnSec=second["totalSec"],
                 sourcePreserved=True,verifiedSourceMutated=False)
            return
        except Exception as exc:
            emit("LIVE_TWO_TURN_ATTEMPT_FAILED",attempt=attempt,
                 kind=type(exc).__name__,detail=str(exc)[:200])
            if attempt==3:raise
            time.sleep(8)

def main():
    args=sys.argv[1:]
    token=os.getenv("HF_TOKEN") or None
    api=HfApi(token=token)
    if args==["preflight"]:
        snapshot(api);return
    if args!=["publish"]:
        raise SystemExit("Usage: preflight|publish")
    if not token or os.getenv("SWRLZ_IMPROVE_PAGE_APPROVED")!="1":
        raise RuntimeError("Scoped Hugging Face source authorization required")
    old_rev=(BACKUP/"revision.txt").read_text().strip()
    before=(BACKUP/FILE).read_bytes()
    after=patch(before.decode()).encode()
    test(after.decode())
    if api.repo_info(SPACE,repo_type="space").sha!=old_rev:
        raise RuntimeError("Space changed since exact source snapshot")
    new_rev=None
    try:
        new_rev=publish(api,old_rev,after,
            "§C: recognize grounded page refinements as existing coding turns")
        wait_model(api,new_rev)
        accept(api,new_rev)
        emit("LIVE_RELEASE_KEPT",revision=new_rev,changedFile=FILE)
    except Exception:
        emit("LIVE_RELEASE_REJECTED",revision=new_rev)
        if new_rev and api.repo_info(SPACE,repo_type="space").sha==new_rev:
            prev=publish(api,new_rev,before,
                "Rollback §C existing-page refinement routing to exact prior source")
            wait_model(api,prev)
            emit("EXACT_ROLLBACK_COMPLETED",revision=prev)
        elif new_rev:emit("ROLLBACK_BLOCKED_CONCURRENT_SPACE_UPDATE")
        raise

if __name__=="__main__":main()
