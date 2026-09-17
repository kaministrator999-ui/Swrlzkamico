"""R39 v74: proportional programming artifact continuation routing over v73.

Preserves the live-verified v73 inference/sampling path. This wrapper repairs a
routing failure where deictic standalone-code follow-ups (for example, "add an
error catch to that code") were promoted to an existing-project debug workflow.
The route now inherits the nearest supported coding artifact/context and keeps
standalone continuations lightweight while preserving explicit project/repo work.
"""
from __future__ import annotations
import json,re,time,urllib.request

_V73_COMMIT="023ac7efdabbe8c317490bc23f410e3a370b5eaf"
_V73_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V73_COMMIT}/runtime_hot/r39_engine_v73.py"
_V74_CONTRACT="r39-v74-programming-artifact-continuation-v1"

def _v74_boot(stage,**fields):
    record={"contract":_V74_CONTRACT,"stage":stage,"atUnixMs":int(time.time()*1000)}
    for key,value in fields.items():
        if value is None or isinstance(value,(str,int,float,bool)):
            record[str(key)[:64]]=value
    print("SWRLZ_R39_HOTLOAD "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

_v74_boot("v73-fetch-start",v73SourceCommit=_V73_COMMIT)
_req=urllib.request.Request(_V73_URL,headers={"User-Agent":"swrlz-r39-v74"})
with urllib.request.urlopen(_req,timeout=20) as _response:
    _source=_response.read(4_000_001)
if len(_source)>4_000_000:
    raise RuntimeError("R39_V73_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V73_URL+"#v74","exec"),globals(),globals())

_V73_INSPECT=inspect_engine
_V73_GENERATE=generate_events
_V73_PROGRAMMING_PROFILE=_programming_profile

_CODE_REFERENT_RE=re.compile(r"\b(?:that|this|the|previous|prior|above|earlier)\s+(?:code|script|program|function|class|snippet|example)\b",re.I)
_EXPLICIT_PROJECT_RE=re.compile(r"\b(?:existing|current)\s+(?:project|repo(?:sitory)?|app|application|website|webpage|codebase|server|client|module|component)\b|\b(?:our|my|this)\s+(?:current\s+)?(?:[A-Za-z0-9_-]+\s+){0,2}(?:project|repo(?:sitory)?|app|application|website|webpage|codebase|server|client|module|component)\b|\bin\s+(?:the|this|our|my)\s+repo(?:sitory)?\b",re.I)
_ERROR_HANDLING_FEATURE_RE=re.compile(r"\b(?:add|include|implement|use|put|wrap|give)\b.{0,80}\b(?:error\s+catch(?:ing)?|error\s+handl(?:e|ing|er)|exception\s+(?:catch(?:ing)?|handl(?:e|ing|er))|try\s*/?\s*except|input\s+validation)\b",re.I|re.S)
_ACTUAL_FIX_RE=re.compile(r"\b(?:fix|debug|repair|broken|failing|regression|bug)\b",re.I)
_CODE_ARTIFACT_RE=re.compile(r"```|(?:^|\n)\s*(?:def|class|function|const|let|var|import|from|public|private|fun)\s+|<html\b|(?:^|\n)\s*[A-Za-z_][A-Za-z0-9_]*\s*=",re.I)


def _v74_history(payload):
    if not isinstance(payload,dict):return []
    return [item for item in list(payload.get("history") or []) if isinstance(item,dict)]


def _v74_role_text(item):
    role=str(item.get("role") or "").strip().lower()
    text=str(item.get("text") or item.get("content") or "").strip()
    return role,text


def _v74_has_code_artifact(text):
    return bool(_CODE_ARTIFACT_RE.search(str(text or "")))


def _v74_prior_artifact_context(payload,limit=12):
    history=_v74_history(payload)
    if not history:return None
    start=max(0,len(history)-max(2,int(limit)))
    for index in range(len(history)-1,start-1,-1):
        role,text=_v74_role_text(history[index])
        if role not in {"assistant","ai"} or not _v74_has_code_artifact(text):continue
        assistant_distance=len(history)-index
        for prior_index in range(index-1,start-1,-1):
            prior_role,prior_text=_v74_role_text(history[prior_index])
            if prior_role not in {"user","human"}:continue
            prior_profile=_V73_PROGRAMMING_PROFILE({"prompt":prior_text})
            if prior_profile.get("active"):
                return {"profile":dict(prior_profile),"assistantDistance":assistant_distance,"userDistance":len(history)-prior_index,"artifactText":text}
            if len(re.findall(r"[A-Za-z0-9_]+",prior_text))>=6:break
        return {"profile":{"active":True,"codingTask":True,"projectContext":"none","changeClass":"feature","architectureDepth":"lightweight","architectureReconciliation":False,"diagnostics":False,"projectCoaching":False,"toolEvidenceRequired":False,"source":"assistant-code-artifact","inherited":True,"inheritedFrom":f"assistant@history_distance_{assistant_distance}","implementationTruth":"runtime-scaffolded"},"assistantDistance":assistant_distance,"userDistance":None,"artifactText":text}
    return None


def _v74_last_assistant_programming(payload):
    for distance,item in enumerate(reversed(_v74_history(payload)),start=1):
        role,text=_v74_role_text(item)
        if role in {"assistant","ai"}:
            return bool(_v74_has_code_artifact(text) or _direct_programming_signal(text)),distance
        if role in {"user","human"}:return False,None
    return False,None


def _v74_change_class(latest):
    value=str(latest or "")
    if _DEPLOY_RE.search(value):return "deploy"
    if _MIGRATE_RE.search(value):return "migrate"
    if _ERROR_HANDLING_FEATURE_RE.search(value):return "feature"
    if _ACTUAL_FIX_RE.search(value):return "fix"
    if _REFACTOR_RE.search(value):return "refactor"
    if _REVIEW_RE.search(value) and not _CODE_ACTION_RE.search(value):return "review"
    if _CODE_ACTION_RE.search(value):return "feature"
    return "explain"


def _v74_inherit_profile(latest,artifact):
    base=dict(artifact.get("profile") or {})
    context=str(base.get("projectContext") or "none")
    change=_v74_change_class(latest)
    mutation=change in {"create","feature","fix","refactor","migrate","deploy"}
    if context=="none":depth="lightweight"
    elif change in {"migrate","deploy"}:depth="deep"
    elif change=="explain":depth="lightweight"
    else:depth="normal"
    source="conversation-artifact-bridge"
    inherited_from=f"assistant@history_distance_{artifact.get('assistantDistance')}"
    return {
        "active":True,"codingTask":True,"projectContext":context,"changeClass":change,
        "architectureDepth":depth,
        "architectureReconciliation":bool(context=="existing" and mutation),
        "diagnostics":bool(change=="fix"),
        "projectCoaching":bool(context=="new" and mutation),
        "toolEvidenceRequired":bool(context=="existing" and mutation),
        "source":source,"inherited":True,"inheritedFrom":inherited_from,
        "implementationTruth":"runtime-scaffolded","artifactContinuation":True,
    }


def _programming_profile(payload):
    base=dict(_V73_PROGRAMMING_PROFILE(payload))
    if not isinstance(payload,dict):return base
    latest=_prog_latest(payload)
    if not latest:return base
    explicit_project=bool(_EXPLICIT_PROJECT_RE.search(latest))
    artifact=_v74_prior_artifact_context(payload)
    last_assistant_programming,_=_v74_last_assistant_programming(payload)
    continuation=bool(_CODE_REFERENT_RE.search(latest) or ((_CONTINUE_RE.search(latest) and not _STOP_RE.search(latest)) and last_assistant_programming))
    if artifact and continuation and not explicit_project:
        return _v74_inherit_profile(latest,artifact)
    # "Add error handling" is a feature request, not proof of an existing broken
    # project. Preserve explicit project references; otherwise keep it standalone.
    if base.get("active") and _ERROR_HANDLING_FEATURE_RE.search(latest) and not explicit_project:
        base.update({"projectContext":"none","changeClass":"feature","architectureDepth":"lightweight","architectureReconciliation":False,"diagnostics":False,"projectCoaching":False,"toolEvidenceRequired":False,"source":"current-turn-proportional-feature"})
    return base


def _self_test_v74():
    prior_user="Write a small Python program that asks the user for a number and prints whether it is even or odd."
    prior_code="```python\nnumber = int(input('Enter a number: '))\nprint('Even' if number % 2 == 0 else 'Odd')\n```"
    history=[{"role":"USER","text":prior_user},{"role":"ASSISTANT","text":prior_code}]
    cases=[]
    def check(name,payload,wants):
        try:
            got=_programming_profile(payload);fail=[]
            for key,want in wants.items():
                if got.get(key)!=want:fail.append(f"{key}={got.get(key)!r} expected {want!r}")
            cases.append({"name":name,"ok":not fail,"failures":fail})
        except Exception as exc:cases.append({"name":name,"ok":False,"failures":[f"{type(exc).__name__}: {exc}"]})
    check("standalone-artifact-error-catch",{"prompt":"Can you add a error catch to that code?","history":history},{"active":True,"projectContext":"none","changeClass":"feature","architectureDepth":"lightweight","architectureReconciliation":False,"diagnostics":False,"toolEvidenceRequired":False,"inherited":True,"artifactContinuation":True})
    check("standalone-artifact-real-fix",{"prompt":"Fix the bug in that code.","history":history},{"active":True,"projectContext":"none","changeClass":"fix","architectureDepth":"lightweight","architectureReconciliation":False,"diagnostics":True,"toolEvidenceRequired":False,"inherited":True})
    check("explicit-project-stays-project",{"prompt":"Fix the error in that code in our existing repo.","history":history},{"active":True,"projectContext":"existing","changeClass":"fix","architectureDepth":"normal","architectureReconciliation":True,"diagnostics":True,"toolEvidenceRequired":True})
    check("standalone-error-handling-direct",{"prompt":"Write a small Python example and add error handling."},{"active":True,"projectContext":"none","architectureDepth":"lightweight","architectureReconciliation":False,"toolEvidenceRequired":False})
    check("non-programming-unchanged",{"prompt":"Explain quantum physics."},{"active":False})
    passed=sum(1 for case in cases if case["ok"])
    return {"ok":passed==len(cases),"passed":passed,"total":len(cases),"failures":[case for case in cases if not case["ok"]],"contract":_V74_CONTRACT}

_V74_SELF_TEST=_self_test_v74()
if not _V74_SELF_TEST.get("ok"):
    raise RuntimeError("R39_V74_PROGRAMMING_ARTIFACT_CONTINUATION_SELF_TEST_FAILED")

HOT_SERVER_VERSION="2.1.86"
HOT_REVISION="2.1.86-hot-programming-artifact-continuation-v74"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
_v74_boot("hydrate-ok",hotServerVersion=HOT_SERVER_VERSION,v73Preserved=True,programmingArtifactContinuation=True,proportionalErrorHandlingFeature=True,selfTest=True)


def inspect_engine():
    result=_V73_INSPECT()
    if isinstance(result,dict):
        result.update({
            "hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,
            "v73Preserved":True,"programmingArtifactContinuation":True,
            "proportionalErrorHandlingFeature":True,
            "programmingArtifactContinuationContract":_V74_CONTRACT,
            "programmingArtifactContinuationSelfTest":dict(_V74_SELF_TEST),
            "v73SourceCommit":_V73_COMMIT,
        })
    return result


def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    profile=_programming_profile(payload) if isinstance(payload,dict) else {"active":False}
    _camera(request_id,"v74-enter",contract=_V74_CONTRACT,v73Preserved=True,artifactContinuation=bool(profile.get("artifactContinuation")),projectContext=profile.get("projectContext"),changeClass=profile.get("changeClass"),architectureDepth=profile.get("architectureDepth"),inherited=bool(profile.get("inherited")),architectureReconciliation=bool(profile.get("architectureReconciliation")),diagnostics=bool(profile.get("diagnostics")),toolEvidenceRequired=bool(profile.get("toolEvidenceRequired")))
    for event in _V73_GENERATE(payload,is_cancelled):
        yield event