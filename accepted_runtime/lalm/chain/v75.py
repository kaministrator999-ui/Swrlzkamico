"""R39 v75 overlay: preserve coding-artifact provenance and runnable edit semantics after v74."""
from __future__ import annotations
import ast,re

_V75_CONTRACT="r39-v75-programming-continuation-semantics-v1"
_V74_INSPECT_V75=inspect_engine
_V74_GENERATE_V75=generate_events
_V74_PROGRAMMING_PROFILE_V75=_programming_profile
_V74_ARTIFACT_GAPS_V75=_artifact_acceptance_gaps
_V74_PREPARE_V27_V75=_prepare_v27_payload
_V74_REPAIR_PAYLOAD_V75=_repair_payload

_RETRY_ALLOW_V75=re.compile(r"\b(?:retry|try\s+again|ask\s+again|keep\s+(?:asking|prompting)|until\s+(?:valid|correct)|repeat|loop)\b",re.I)
_RESTRUCTURE_ALLOW_V75=re.compile(r"\b(?:rename|refactor|restructure|rewrite\s+from\s+scratch|convert\s+(?:it|this|that)\s+to\s+(?:a\s+)?class|make\s+(?:it|this|that)\s+(?:a\s+)?class)\b",re.I)
_ENTRY_REMOVAL_ALLOW_V75=re.compile(r"\b(?:library|module|definition\s+only|function\s+only|do\s+not\s+call|don't\s+call|remove.{0,40}\bcall)\b",re.I|re.S)
_CONTINUATION_DIRECTIVE_V75=(
    "When editing referenced standalone code, preserve existing behavior and callable names unless explicitly asked to change them. "
    "Keep the revision complete and runnable. Make only the requested semantic change; do not add retry loops or unrelated features unless requested."
)

def _v75_is_continuation(text):
    value=str(text or "")
    return bool(_CODE_REFERENT_RE.search(value) or ((_CONTINUE_RE.search(value) and not _STOP_RE.search(value))))

def _v75_default_profile(distance):
    return {"active":True,"codingTask":True,"projectContext":"none","changeClass":"feature","architectureDepth":"lightweight",
            "architectureReconciliation":False,"diagnostics":False,"projectCoaching":False,"toolEvidenceRequired":False,
            "source":"assistant-code-artifact-root","inherited":True,
            "inheritedFrom":f"assistant@history_distance_{distance}","implementationTruth":"runtime-scaffolded"}

def _v75_artifact_origin(payload,limit=20,max_depth=6):
    history=_v74_history(payload)
    if not history:return None
    start=max(0,len(history)-max(4,int(limit)));cursor=len(history)-1;depth=0;latest_text=None;latest_distance=None
    while cursor>=start and depth<max_depth:
        ai_idx=None;ai_text=""
        for i in range(cursor,start-1,-1):
            role,text=_v74_role_text(history[i])
            if role in {"assistant","ai"} and _v74_has_code_artifact(text):
                ai_idx=i;ai_text=text;break
        if ai_idx is None:break
        distance=len(history)-ai_idx
        if latest_text is None:latest_text=ai_text;latest_distance=distance
        user_idx=None;user_text=""
        for i in range(ai_idx-1,start-1,-1):
            role,text=_v74_role_text(history[i])
            if role in {"user","human"}:user_idx=i;user_text=text;break
        if user_idx is None:break
        if _EXPLICIT_PROJECT_RE.search(user_text):
            profile=dict(_V73_PROGRAMMING_PROFILE({"prompt":user_text}))
            if not profile.get("active"):
                profile={"active":True,"codingTask":True,"projectContext":"existing","changeClass":"feature","architectureDepth":"normal",
                         "architectureReconciliation":True,"diagnostics":False,"projectCoaching":False,"toolEvidenceRequired":True,
                         "source":"artifact-explicit-project-promotion","inherited":True,"implementationTruth":"runtime-scaffolded"}
            return {"profile":profile,"assistantDistance":latest_distance,"continuationDepth":depth,"originUserDistance":len(history)-user_idx}
        if _v75_is_continuation(user_text):
            depth+=1;cursor=user_idx-1;continue
        profile=dict(_V73_PROGRAMMING_PROFILE({"prompt":user_text}))
        if not profile.get("active"):profile=_v75_default_profile(distance)
        return {"profile":profile,"assistantDistance":latest_distance,"continuationDepth":depth,"originUserDistance":len(history)-user_idx}
    if latest_text is not None:
        return {"profile":_v75_default_profile(latest_distance),"assistantDistance":latest_distance,"continuationDepth":depth,"originUserDistance":None}
    return None

def _v75_inherit(latest,artifact):
    base=dict(artifact.get("profile") or {});context=str(base.get("projectContext") or "none");change=_v74_change_class(latest)
    mutation=change in {"create","feature","fix","refactor","migrate","deploy"}
    depth="lightweight" if context=="none" or change=="explain" else ("deep" if change in {"migrate","deploy"} else "normal")
    return {"active":True,"codingTask":True,"projectContext":context,"changeClass":change,"architectureDepth":depth,
            "architectureReconciliation":bool(context=="existing" and mutation),"diagnostics":bool(change=="fix"),
            "projectCoaching":bool(context=="new" and mutation),"toolEvidenceRequired":bool(context=="existing" and mutation),
            "source":"conversation-artifact-provenance-v75","inherited":True,
            "inheritedFrom":f"assistant@history_distance_{artifact.get('assistantDistance')}",
            "implementationTruth":"runtime-scaffolded","artifactContinuation":True,
            "continuationDepth":int(artifact.get("continuationDepth") or 0),"originUserDistance":artifact.get("originUserDistance")}

def _programming_profile(payload):
    base=dict(_V74_PROGRAMMING_PROFILE_V75(payload))
    if not isinstance(payload,dict):return base
    latest=_prog_latest(payload)
    if not latest:return base
    last_programming,_=_v74_last_assistant_programming(payload)
    continuation=bool(_CODE_REFERENT_RE.search(latest) or ((_CONTINUE_RE.search(latest) and not _STOP_RE.search(latest)) and last_programming))
    if continuation and not _EXPLICIT_PROJECT_RE.search(latest):
        artifact=_v75_artifact_origin(payload)
        if artifact:return _v75_inherit(latest,artifact)
    return base

def _v75_sig_code(code):
    try:tree=ast.parse(str(code or ""))
    except SyntaxError:return {"valid":False,"defined":[],"entry":[],"called":[],"exec":False,"whileTrue":0}
    defined={n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}
    called=set()
    for stmt in tree.body:
        if isinstance(stmt,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef,ast.Import,ast.ImportFrom)):continue
        for node in ast.walk(stmt):
            if isinstance(node,ast.Call):
                if isinstance(node.func,ast.Name):called.add(node.func.id)
                elif isinstance(node.func,ast.Attribute):called.add(node.func.attr)
    inert=(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef,ast.Import,ast.ImportFrom,ast.Pass,ast.Assign,ast.AnnAssign)
    loops=sum(1 for n in ast.walk(tree) if isinstance(n,ast.While) and isinstance(n.test,ast.Constant) and n.test.value is True)
    return {"valid":True,"defined":sorted(defined),"entry":sorted(defined&called),"called":sorted(called),
            "exec":any(not isinstance(s,inert) for s in tree.body),"whileTrue":loops}

def _v75_sig_text(text):
    valid=[_v75_sig_code(code) for code in _python_blocks(text)]
    valid=[s for s in valid if s.get("valid")]
    if not valid:return {"valid":False,"defined":[],"entry":[],"called":[],"exec":False,"whileTrue":0}
    runnable=[s for s in valid if s.get("exec") or s.get("entry")]
    return dict((runnable or valid)[0])

def _v75_best_baseline(payload):
    fallback=None
    for item in reversed(_v74_history(payload)[-20:]):
        role,text=_v74_role_text(item)
        if role not in {"assistant","ai"} or not _v74_has_code_artifact(text):continue
        sig=_v75_sig_text(text)
        if not sig.get("valid"):continue
        if fallback is None:fallback=sig
        if sig.get("exec") or sig.get("entry"):return sig
    return fallback

def _v75_semantic_gaps(candidate,baseline,prompt):
    if not candidate.get("valid") or not baseline.get("valid"):return []
    value=str(prompt or "");gaps=[]
    restructure=bool(_RESTRUCTURE_ALLOW_V75.search(value));remove_entry=bool(_ENTRY_REMOVAL_ALLOW_V75.search(value));retry=bool(_RETRY_ALLOW_V75.search(value))
    if baseline.get("defined") and not restructure and not set(baseline["defined"]).issubset(set(candidate.get("defined") or [])):
        gaps.append("continuation-symbol-preservation")
    if baseline.get("entry") and not remove_entry and not set(baseline["entry"]).issubset(set(candidate.get("called") or [])):
        gaps.append("continuation-entrypoint-call")
    if baseline.get("exec") and not candidate.get("exec") and not remove_entry:
        gaps.append("continuation-runnable-entrypoint")
    if not int(baseline.get("whileTrue") or 0) and int(candidate.get("whileTrue") or 0)>0 and not retry:
        gaps.append("unrequested-retry-loop")
    return gaps

def _artifact_acceptance_gaps(text,req,original_prompt):
    inherited=list(_V74_ARTIFACT_GAPS_V75(text,req,original_prompt))
    if inherited:return inherited
    baseline=(req or {}).get("_swrlzContinuationBaseline") if isinstance(req,dict) else None
    if not isinstance(baseline,dict) or not baseline.get("valid"):return []
    candidates=[]
    for code in _python_blocks(text):
        sig=_v75_sig_code(code)
        if sig.get("valid"):candidates.append(_v75_semantic_gaps(sig,baseline,original_prompt))
    if any(not gaps for gaps in candidates):return []
    return min(candidates,key=len) if candidates else ["continuation-runnable-semantics"]

def _prepare_v27_payload(payload):
    prepared=_V74_PREPARE_V27_V75(payload)
    baseline=(payload or {}).get("_swrlzContinuationBaseline") if isinstance(payload,dict) else None
    if isinstance(baseline,dict) and baseline.get("valid"):
        req=dict(prepared.get("_swrlzRequirementLedger") or {});req["_swrlzContinuationBaseline"]=dict(baseline);prepared["_swrlzRequirementLedger"]=req
    return prepared

def _repair_payload(prepared,first_text,gaps):
    clone=_V74_REPAIR_PAYLOAD_V75(prepared,first_text,gaps)
    semantic={"continuation-symbol-preservation","continuation-entrypoint-call","continuation-runnable-entrypoint","unrequested-retry-loop","continuation-runnable-semantics"}
    if semantic.intersection(set(str(x) for x in (gaps or []))):
        guidance=("Preserve prior callable names and runnable entrypoint unless explicitly asked to change them. "
                  "Apply only the requested edit; do not add retry loops unless requested. Return complete corrected runnable code. ")
        clone["prompt"]=guidance+str(clone.get("prompt") or "");clone["responseDirective"]=guidance+str(clone.get("responseDirective") or "")
        clone["_swrlzContinuationSemanticRepair"]=True
    return clone

def _self_test_v75():
    fence=chr(96)*3
    u0="Write a small Python program that asks for a number and prints whether it is even or odd."
    c0=fence+"python\ndef even_odd():\n    number=int(input('Enter a number: '))\n    print('Even' if number%2==0 else 'Odd')\n\neven_odd()\n"+fence
    u1="Can you add an error catch to that code?"
    c1=fence+"python\ndef even_odd():\n    try:\n        number=int(input('Enter a number: '))\n        print('Even' if number%2==0 else 'Odd')\n    except ValueError:\n        print('Invalid input')\n\neven_odd()\n"+fence
    hist=[{"role":"USER","text":u0},{"role":"ASSISTANT","text":c0},{"role":"USER","text":u1},{"role":"ASSISTANT","text":c1}]
    p=_programming_profile({"prompt":"Make the invalid-input message clearer in that code.","history":hist})
    promoted=hist+[{"role":"USER","text":"Put that code in our existing repo."},{"role":"ASSISTANT","text":c1}]
    q=_programming_profile({"prompt":"Add logging to that code.","history":promoted})
    base=_v75_sig_text(c0);req={"requireRunnableCode":True,"requirePython":True,"_swrlzContinuationBaseline":base}
    missing=fence+"python\ndef evenodd():\n    try:\n        number=int(input('Enter a number: '))\n    except ValueError:\n        print('Invalid')\n"+fence
    retry=fence+"python\ndef even_odd():\n    while True:\n        try:\n            number=int(input('Enter a number: '))\n        except ValueError:\n            print('Invalid')\n\neven_odd()\n"+fence
    checks={
        "multiHopStandalone":bool(p.get("projectContext")=="none" and p.get("architectureDepth")=="lightweight" and p.get("artifactContinuation")),
        "explicitProjectPromotion":bool(q.get("projectContext")=="existing" and q.get("architectureReconciliation")),
        "missingEntrypointRejected":"continuation-entrypoint-call" in _artifact_acceptance_gaps(missing,req,u1),
        "unrequestedRetryRejected":"unrequested-retry-loop" in _artifact_acceptance_gaps(retry,req,u1),
        "minimalEditAccepted":not _artifact_acceptance_gaps(c1,req,u1),
    }
    return {"ok":all(checks.values()),"checks":checks,"contract":_V75_CONTRACT}

_V75_SELF_TEST=_self_test_v75()
if not _V75_SELF_TEST.get("ok"):raise RuntimeError("R39_V75_CONTINUATION_SEMANTICS_SELF_TEST_FAILED")

HOT_SERVER_VERSION="2.1.87"
HOT_REVISION="2.1.87-hot-programming-continuation-semantics-v75"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

def inspect_engine():
    result=_V74_INSPECT_V75()
    if isinstance(result,dict):
        result.update({"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"v74Preserved":True,
                       "programmingContinuationProvenance":True,"runnableEditSemanticGate":True,"unrequestedRetryLoopGate":True,
                       "programmingContinuationSemanticContract":_V75_CONTRACT,
                       "programmingContinuationSemanticSelfTest":dict(_V75_SELF_TEST)})
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    profile=_programming_profile(payload) if isinstance(payload,dict) else {"active":False}
    routed=dict(payload) if isinstance(payload,dict) else payload;baseline=None
    if isinstance(routed,dict) and profile.get("artifactContinuation"):
        baseline=_v75_best_baseline(routed)
        if baseline and baseline.get("valid"):routed["_swrlzContinuationBaseline"]=dict(baseline)
        routed["responseDirective"]=(str(routed.get("responseDirective") or "").strip()+" "+_CONTINUATION_DIRECTIVE_V75).strip()
    _camera(request_id,"v75-enter",contract=_V75_CONTRACT,v74Preserved=True,artifactContinuation=bool(profile.get("artifactContinuation")),
            continuationDepth=int(profile.get("continuationDepth") or 0),projectContext=profile.get("projectContext"),
            architectureDepth=profile.get("architectureDepth"),architectureReconciliation=bool(profile.get("architectureReconciliation")),
            baselineRunnable=bool(baseline and baseline.get("exec")),baselineEntrypointCount=len((baseline or {}).get("entry") or []),
            runnableEditSemanticGate=True)
    for event in _V74_GENERATE_V75(routed,is_cancelled):yield event
