"""R39 v69: compact lightweight programming context and repair bounded prefill diagnostics."""
from __future__ import annotations
import json,time,urllib.request

_V68_COMMIT="9420c0e02b63821c1271ad38c6f826b00c3b013c"
_V68_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V68_COMMIT}/runtime_hot/r39_engine_v68.py"
_CONTRACT="r39-v69-lightweight-programming-prefill-v1"

def _log(stage,**fields):
    record={"contract":_CONTRACT,"stage":stage,"atUnixMs":int(time.time()*1000)}
    for key,value in fields.items():
        if value is None or isinstance(value,(str,int,float,bool)):record[str(key)[:64]]=value
    print("SWRLZ_R39_HOTLOAD "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

_log("v68-fetch-start",v68SourceCommit=_V68_COMMIT)
_req=urllib.request.Request(_V68_URL,headers={"User-Agent":"swrlz-r39-v69"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V68_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V68_URL+"#v69","exec"),globals(),globals())

_V68_INSPECT=inspect_engine
_V68_GENERATE=generate_events
_ORIGINAL_V41_GENERATE=globals().get("_V41_GENERATE")
_ORIGINAL_RENDER_CAMERA=globals().get("_render_camera")

_canonical_get_model=getattr(globals().get("_impl"),"_get_model",None)
if not callable(_canonical_get_model):raise RuntimeError("R39_V69_CANONICAL_GET_MODEL_UNAVAILABLE")
_get_model=_canonical_get_model
_cleaner=globals().get("_clean_noncoding_history")
if not callable(_cleaner):_cleaner=getattr(globals().get("_impl"),"_clean_noncoding_history",None)
if not callable(_cleaner):raise RuntimeError("R39_V69_HISTORY_CLEANER_UNAVAILABLE")
_clean_noncoding_history=_cleaner
if not callable(_ORIGINAL_V41_GENERATE) or not callable(_ORIGINAL_RENDER_CAMERA):raise RuntimeError("R39_V69_PREFILL_BOUNDARY_UNAVAILABLE")

_LIGHTWEIGHT_FLAG="_swrlz_lightweight_programming"
_COMPACT_MARKER=("[SWRLZ_LIGHTWEIGHT_PROGRAMMING v1] Standalone lightweight coding task. "
 "Answer the user's current coding request directly. Preserve literal user text and Unicode. "
 "Satisfy requested code and explanation. Do not add repository, project-architecture, tool, "
 "or deployment ceremony unless the user explicitly requires it and the applicable permission boundary allows it.")
_DYNAMIC_POLICY_PREFIXES=("[SWRLZ_PROGRAMMING_MODE ","[SWRLZ_CONTEXT_FOCUS ","[SWRLZ_CONVERSATION_STATE ","User language preference:")
_STATIC_POLICY_NAMES=("_CONVERSATION_INTELLIGENCE_POLICY","_MAP_TO_POINT_POLICY","_UNICODE_AWARENESS_POLICY","_REASONING_RECOVERY_POLICY","_TRAJECTORY_POLICY","_REPAIR_POLICY","_ACCEPT_POLICY")

def _history_chars(history):
    total=0
    for item in history if isinstance(history,list) else []:
        if isinstance(item,dict):total+=len(str(item.get("text") or item.get("content") or ""))
    return total

def _known_internal_policy(text):
    value=str(text or "")
    if value.startswith(_DYNAMIC_POLICY_PREFIXES):return True
    for name in _STATIC_POLICY_NAMES:
        policy=globals().get(name)
        if isinstance(policy,str) and value==policy:return True
    return False

def _compact_lightweight_payload(payload):
    if not isinstance(payload,dict) or not payload.get(_LIGHTWEIGHT_FLAG):
        return payload,{"active":False,"removed":0,"beforeMessages":0,"afterMessages":0,"beforeChars":0,"afterChars":0,"dialoguePreserved":True}
    out=dict(payload);history=list(out.get("history") or []);before_chars=_history_chars(history);kept=[];removed=0;compact_present=False;dialogue_before=[];dialogue_after=[]
    for item in history:
        if not isinstance(item,dict):kept.append(item);continue
        role=str(item.get("role") or "").strip().lower();text=str(item.get("text") or item.get("content") or "")
        if role in {"user","human","assistant","ai"}:dialogue_before.append((role,text))
        if role=="system" and text.startswith("[SWRLZ_LIGHTWEIGHT_PROGRAMMING v1]"):
            if not compact_present:kept.append(item);compact_present=True
            else:removed+=1
            continue
        if role=="system" and _known_internal_policy(text):removed+=1;continue
        kept.append(item)
    if not compact_present:kept.insert(0,{"role":"system","text":_COMPACT_MARKER})
    for item in kept:
        if isinstance(item,dict):
            role=str(item.get("role") or "").strip().lower()
            if role in {"user","human","assistant","ai"}:dialogue_after.append((role,str(item.get("text") or item.get("content") or "")))
    out["history"]=kept
    return out,{"active":True,"removed":removed,"beforeMessages":len(history),"afterMessages":len(kept),"beforeChars":before_chars,"afterChars":_history_chars(kept),"dialoguePreserved":dialogue_before==dialogue_after}

# Legacy v36 token-exact rendered-prompt tracing is intentionally retired. Bounded count/timing cameras remain.
def _prefill_trace(payload):
    if False:yield None

def _v69_render_camera(payload,request_id):
    view,stats=_compact_lightweight_payload(payload)
    if stats.get("active"):_camera(request_id,"lightweight-context-compaction",contract=_CONTRACT,beforeMessages=stats.get("beforeMessages"),afterMessages=stats.get("afterMessages"),beforeChars=stats.get("beforeChars"),afterChars=stats.get("afterChars"),internalPoliciesRemoved=stats.get("removed"),dialoguePreserved=stats.get("dialoguePreserved"),renderView=True)
    return _ORIGINAL_RENDER_CAMERA(view,request_id)
_render_camera=_v69_render_camera

def _v69_v41_generate(payload,is_cancelled=None):
    routed,stats=_compact_lightweight_payload(payload);request_id=_request_id(payload) if isinstance(payload,dict) else ""
    if stats.get("active"):_camera(request_id,"lightweight-context-applied",contract=_CONTRACT,beforeMessages=stats.get("beforeMessages"),afterMessages=stats.get("afterMessages"),beforeChars=stats.get("beforeChars"),afterChars=stats.get("afterChars"),internalPoliciesRemoved=stats.get("removed"),dialoguePreserved=stats.get("dialoguePreserved"),inferenceView=True)
    for event in _ORIGINAL_V41_GENERATE(routed,is_cancelled):yield event
_V41_GENERATE=_v69_v41_generate

def _compaction_self_test():
    unknown={"role":"system","text":"CUSTOM_SYSTEM_OWNER must survive"};user={"role":"user","text":"print('§')"};assistant={"role":"assistant","text":"prior exact"}
    synthetic={_LIGHTWEIGHT_FLAG:True,"history":[{"role":"system","text":"[SWRLZ_PROGRAMMING_MODE v1] verbose"},{"role":"system","text":"[SWRLZ_CONTEXT_FOCUS v1] verbose"},{"role":"system","text":"[SWRLZ_CONVERSATION_STATE v3] verbose"},{"role":"system","text":"User language preference: keep assistant language clean; do not use profanity."},unknown,user,assistant]}
    compact,stats=_compact_lightweight_payload(synthetic);hist=compact.get("history") or []
    exact_unknown=sum(1 for x in hist if isinstance(x,dict) and x.get("text")==unknown["text"])==1
    exact_user=sum(1 for x in hist if isinstance(x,dict) and x.get("role")=="user" and x.get("text")==user["text"])==1
    exact_assistant=sum(1 for x in hist if isinstance(x,dict) and x.get("role")=="assistant" and x.get("text")==assistant["text"])==1
    one_marker=sum(1 for x in hist if isinstance(x,dict) and str(x.get("text") or "").startswith("[SWRLZ_LIGHTWEIGHT_PROGRAMMING v1]"))==1
    idempotent,_=_compact_lightweight_payload(compact);untouched={"history":[{"role":"system","text":"[SWRLZ_PROGRAMMING_MODE v1] keep outside lightweight"}]};untouched_after,_=_compact_lightweight_payload(untouched)
    checks={"getModelBridge":callable(_get_model),"historyCleaner":callable(_clean_noncoding_history),"dialoguePreserved":bool(stats.get("dialoguePreserved") and exact_user and exact_assistant),"unknownSystemPreserved":exact_unknown,"knownPoliciesCompacted":stats.get("removed")==4,"oneCompactMarker":one_marker,"idempotent":idempotent.get("history")==compact.get("history"),"nonLightweightUnchanged":untouched_after==untouched}
    return {"ok":all(checks.values()),"checks":checks,"contract":_CONTRACT}

_COMPACTION_SELF_TEST=_compaction_self_test()
if not _COMPACTION_SELF_TEST.get("ok"):raise RuntimeError("R39_V69_LIGHTWEIGHT_COMPACTION_SELF_TEST_FAILED")

HOT_SERVER_VERSION="2.1.81"
HOT_REVISION="2.1.81-hot-lightweight-programming-prefill-v69"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
_log("hydrate-ok",hotServerVersion=HOT_SERVER_VERSION,v68Preserved=True,getModelBridge=True,boundedRenderCamera=True,rawPromptTokenTraceRetired=True,lightweightCompactionSelfTest=True)

def inspect_engine():
    result=_V68_INSPECT()
    if isinstance(result,dict):result.update({"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"v68Preserved":True,"lightweightProgrammingContextCompaction":True,"lightweightProgrammingDialoguePreserved":True,"unknownSystemPoliciesPreserved":True,"prefillRenderGetModelBridge":True,"rawPromptTokenTraceRetired":True,"lightweightProgrammingCompactionSelfTest":dict(_COMPACTION_SELF_TEST),"crossWorkerComputeCheckpointing":False,"crossWorkerRestartCostMitigatedByContextCompaction":True,"v68SourceCommit":_V68_COMMIT})
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else "";profile=_programming_profile(payload) if isinstance(payload,dict) else {"active":False}
    lightweight=bool(profile.get("active") and profile.get("projectContext")=="none" and profile.get("architectureDepth")=="lightweight")
    routed=dict(payload) if isinstance(payload,dict) else payload
    if lightweight and isinstance(routed,dict):routed[_LIGHTWEIGHT_FLAG]=True
    _camera(request_id,"v69-enter",contract=_CONTRACT,v68Preserved=True,lightweightProgramming=lightweight,getModelBridge=True,rawPromptTokenTraceRetired=True)
    try:
        for event in _V68_GENERATE(routed,is_cancelled):yield event
    except Exception as exc:
        _camera(request_id,"v69-generate-exception",contract=_CONTRACT,errorType=type(exc).__name__,errorMessage=str(exc)[:240]);raise
