"""R39 v68: restore canonical latest-user-text namespace over v67."""
from __future__ import annotations
import json,time,urllib.request

_V67_COMMIT="d080434b426ece68b92e14af8f5fb9e1a34daffd"
_V67_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V67_COMMIT}/runtime_hot/r39_engine_v67.py"
_CONTRACT="r39-v68-latest-user-namespace-v1"

def _log(stage,**fields):
    record={"contract":_CONTRACT,"stage":stage,"atUnixMs":int(time.time()*1000)}
    for key,value in fields.items():
        if value is None or isinstance(value,(str,int,float,bool)):
            record[str(key)[:64]]=value
    print("SWRLZ_R39_HOTLOAD "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

_log("v67-fetch-start",v67SourceCommit=_V67_COMMIT)
_req=urllib.request.Request(_V67_URL,headers={"User-Agent":"swrlz-r39-v68"})
with urllib.request.urlopen(_req,timeout=20) as _response:
    _source=_response.read(4_000_001)
if len(_source)>4_000_000:
    raise RuntimeError("R39_V67_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V67_URL+"#v68","exec"),globals(),globals())

_V67_INSPECT=inspect_engine
_V67_GENERATE=generate_events

_canonical_latest_user_text=getattr(globals().get("_impl"),"_latest_user_text",None)
if not callable(_canonical_latest_user_text):
    _log("bridge-contract-failed",missing="_impl._latest_user_text")
    raise RuntimeError("R39_V68_CANONICAL_LATEST_USER_TEXT_UNAVAILABLE")
_latest_user_text=_canonical_latest_user_text

def _namespace_bridge_self_test():
    checks={}
    failures=[]
    try:
        checks["latestUserText"]=_latest_user_text({"prompt":"  bridge probe  "})=="bridge probe"
    except Exception as exc:
        checks["latestUserText"]=False
        failures.append("latestUserText:"+type(exc).__name__)
    try:
        state=_conversation_state({"prompt":"Hey 👋","history":[]})
        checks["conversationState"]=isinstance(state,dict)
    except Exception as exc:
        checks["conversationState"]=False
        failures.append("conversationState:"+type(exc).__name__+":"+str(exc)[:120])
    try:
        profile=_programming_profile({"prompt":"Fix the bug in our current repo."})
        checks["programmingProfile"]=bool(isinstance(profile,dict) and profile.get("active"))
    except Exception as exc:
        checks["programmingProfile"]=False
        failures.append("programmingProfile:"+type(exc).__name__+":"+str(exc)[:120])
    return {"ok":all(checks.values()),"checks":checks,"failures":failures,"contract":_CONTRACT}

_BRIDGE_SELF_TEST=_namespace_bridge_self_test()
if not _BRIDGE_SELF_TEST.get("ok"):
    _log("bridge-self-test-failed",failures="|".join(_BRIDGE_SELF_TEST.get("failures") or [])[:240])
    raise RuntimeError("R39_V68_LATEST_USER_NAMESPACE_SELF_TEST_FAILED")

HOT_SERVER_VERSION="2.1.80"
HOT_REVISION="2.1.80-hot-v67-latest-user-namespace-repair-v68"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_log("hydrate-ok",hotServerVersion=HOT_SERVER_VERSION,v67Preserved=True,latestUserTextBridge=True,canonicalOwner="_impl._latest_user_text",conversationStateProbe=True,programmingProfileProbe=True)

def inspect_engine():
    result=_V67_INSPECT()
    if isinstance(result,dict):
        result.update({
            "hotServerVersion":HOT_SERVER_VERSION,
            "hotRevision":HOT_REVISION,
            "v67Preserved":True,
            "latestUserTextNamespaceBridge":True,
            "latestUserTextCanonicalOwner":"_impl._latest_user_text",
            "latestUserTextBridgeChangesSemantics":False,
            "latestUserTextNamespaceSelfTest":dict(_BRIDGE_SELF_TEST),
            "v67SourceCommit":_V67_COMMIT,
        })
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    _camera(request_id,"v68-enter",contract=_CONTRACT,v67Preserved=True,latestUserTextBridge=True,canonicalOwner="_impl._latest_user_text")
    try:
        for event in _V67_GENERATE(payload,is_cancelled):
            yield event
    except Exception as exc:
        _camera(request_id,"v68-generate-exception",contract=_CONTRACT,errorType=type(exc).__name__,errorMessage=str(exc)[:240])
        raise
