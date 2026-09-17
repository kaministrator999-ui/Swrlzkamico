"""R39 v70: harden coding completion and repair bare-fence continuation over v69."""
from __future__ import annotations
import json,re,time,urllib.request

_V69_COMMIT="a47edea4867c8082baddf27b04182430dc92fb31"
_V69_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V69_COMMIT}/runtime_hot/r39_engine_v69.py"
_CONTRACT="r39-v70-coding-terminal-repair-v1"

def _hot(stage,**fields):
    record={"contract":_CONTRACT,"stage":stage,"atUnixMs":int(time.time()*1000)}
    for key,value in fields.items():
        if value is None or isinstance(value,(str,int,float,bool)):record[str(key)[:64]]=value
    print("SWRLZ_R39_HOTLOAD "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

_hot("v69-fetch-start",v69SourceCommit=_V69_COMMIT)
_req=urllib.request.Request(_V69_URL,headers={"User-Agent":"swrlz-r39-v70"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V69_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V69_URL+"#v70","exec"),globals(),globals())

_V69_INSPECT=inspect_engine
_V69_GENERATE=generate_events
_V69_RESPONSE_GAPS=globals().get("_response_contract_gaps")
_V69_REPAIR_PAYLOAD=globals().get("_repair_payload")
_V69_V27_BASE_GENERATE=globals().get("_V24_GENERATE_FOR_V27")
_V69_COMPACT_MARKER=str(globals().get("_COMPACT_MARKER") or "")
if not all(callable(x) for x in (_V69_RESPONSE_GAPS,_V69_REPAIR_PAYLOAD,_V69_V27_BASE_GENERATE)):
    raise RuntimeError("R39_V70_REQUIRED_V27_BOUNDARY_UNAVAILABLE")
if not callable(globals().get("_response_contract")) or not callable(globals().get("_camera")):
    raise RuntimeError("R39_V70_COMPLETION_CONTRACT_UNAVAILABLE")

_BARE_FENCE_RE=re.compile(r"^\s*```(?:python|py)?\s*$",re.I)
_DECODE_STEP_RE=re.compile(r"\bDecode step\s+(\d+)\b")

def _bare_open_fence(text):
    return bool(_BARE_FENCE_RE.fullmatch(str(text or "")))

def _ensure_gap(gaps,name):
    if name not in gaps:gaps.append(name)

def _v70_response_contract_gaps(text,contract):
    gaps=list(_V69_RESPONSE_GAPS(text,contract))
    value=str(text or "")
    if isinstance(contract,dict) and contract.get("coding") and (not value.strip() or _bare_open_fence(value)):
        _ensure_gap(gaps,"complete-code")
        if contract.get("explain"):_ensure_gap(gaps,"requested-explanation")
    return gaps

# The v17 generator resolves this global dynamically at EOS and final verification.
_response_contract_gaps=_v70_response_contract_gaps

# Keep the compact v69 policy, but explicitly forbid the exact malformed terminal we observed.
if _V69_COMPACT_MARKER:
    _COMPACT_MARKER=_V69_COMPACT_MARKER+" For runnable code, never end after only an opening language fence; emit executable code before ending."


def _v70_repair_payload(prepared,first_text,gaps):
    clone=_V69_REPAIR_PAYLOAD(prepared,first_text,gaps)
    implicated="runnable-code" in set(str(x) for x in (gaps or []))
    if not implicated or not _bare_open_fence(first_text):return clone
    history=list(clone.get("history") or [])
    removed=False
    for index in range(len(history)-1,-1,-1):
        item=history[index]
        if not isinstance(item,dict):continue
        role=str(item.get("role") or "").strip().lower()
        text=str(item.get("text") or item.get("content") or "")
        if role in {"assistant","ai"} and _bare_open_fence(text):
            del history[index];removed=True;break
    continuation=(
        "The visible answer already contains one opening Python code fence. Continue inside that existing fence. "
        "Begin immediately with executable Python code; do not emit another opening code fence. "
        "Close the existing fence exactly once after the runnable code, then provide the requested brief explanation. "
        "Do not restart or repeat the language tag. "
    )
    clone["history"]=history
    clone["prompt"]=continuation+str(clone.get("prompt") or "")
    clone["responseDirective"]=continuation+str(clone.get("responseDirective") or "")
    clone["_swrlzFenceContinuationRepair"]=True
    request_id=str(clone.get("requestId") or "")
    if request_id and request_id!="v70-selftest":
        _camera(request_id,"coding-fence-repair-normalized",contract=_CONTRACT,bareOpeningFence=True,incompleteAssistantPrefixRemoved=removed,continuationInsideExistingFence=True)
    return clone

# v27 resolves the repair helper dynamically; extend that canonical repair path.
_repair_payload=_v70_repair_payload


def _terminal_reason_class(reason):
    value=str(reason or "").lower()
    if "degeneration guard" in value:return "degeneration-guard"
    if "local r39 generation completed" in value:return "base-completed"
    if "hot local r39 inference failed" in value:return "inference-failed"
    if "cancel" in value:return "cancelled"
    return "other"

def _v70_v27_candidate_generate(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    pass_kind="repair" if isinstance(payload,dict) and payload.get("_swrlzRepairPass") else "first"
    text="";delta_events=0;max_decode=0;saw_deg=False
    for event in _V69_V27_BASE_GENERATE(payload,is_cancelled):
        if not isinstance(event,dict):yield event;continue
        event=dict(event);event_type=str(event.get("type") or "");phase=str(event.get("phase") or "")
        if event_type=="DELTA":
            text+=str(event.get("text") or "");delta_events+=1
        elif event_type=="STATUS":
            if phase=="DEGENERATION_GUARD":saw_deg=True
            match=_DECODE_STEP_RE.search(str(event.get("reason") or ""))
            if match:max_decode=max(max_decode,int(match.group(1)))
        if event_type in {"COMPLETED","FAILED","CANCELLED"}:
            contract=_response_contract(payload) if isinstance(payload,dict) else {}
            gaps=_response_contract_gaps(text,contract) if isinstance(contract,dict) else []
            _camera(request_id,"coding-candidate-terminal",contract=_CONTRACT,passKind=pass_kind,terminalType=event_type,terminalReasonClass=_terminal_reason_class(event.get("reason")),deltaEvents=delta_events,deltaChars=len(text),maxDecodeStep=max_decode,sawDegenerationGuard=saw_deg,fenceCount=text.count("```"),bareOpeningFence=_bare_open_fence(text),gapCount=len(gaps),completeCodeGap="complete-code" in gaps,requestedExplanationGap="requested-explanation" in gaps)
        yield event

# v27 calls this historical base-generator alias twice: first candidate + bounded repair.
_V24_GENERATE_FOR_V27=_v70_v27_candidate_generate


def _self_test():
    probe={"prompt":"Write a small Python program. Give me complete runnable code first, then briefly explain how it works."}
    contract=_response_contract(probe)
    inherited=list(_V69_RESPONSE_GAPS("```python",contract))
    hardened=list(_response_contract_gaps("```python",contract))
    prepared={"requestId":"v70-selftest","prompt":probe["prompt"],"history":[],"_swrlzRequirementLedger":{"requireRunnableCode":True,"requirePython":True}}
    repaired=_repair_payload(prepared,"```python",["runnable-code"])
    repaired_history=list(repaired.get("history") or [])
    assistant_bare=any(isinstance(x,dict) and str(x.get("role") or "").lower() in {"assistant","ai"} and _bare_open_fence(x.get("text") or x.get("content")) for x in repaired_history)
    checks={
        "contractCoding":bool(contract.get("coding")),
        "contractExplain":bool(contract.get("explain")),
        "hardenedCompleteCodeGap":"complete-code" in hardened,
        "hardenedExplanationGap":"requested-explanation" in hardened,
        "fenceRepairActivated":bool(repaired.get("_swrlzFenceContinuationRepair")),
        "incompleteFenceRemovedFromRepairHistory":not assistant_bare,
        "continuationDirectivePresent":"Continue inside that existing fence" in str(repaired.get("prompt") or ""),
    }
    return {"ok":all(checks.values()),"checks":checks,"underlyingBareFenceGaps":inherited,"hardenedBareFenceGaps":hardened,"contract":_CONTRACT}

_SELF_TEST=_self_test()
if not _SELF_TEST.get("ok"):raise RuntimeError("R39_V70_CODING_TERMINAL_SELF_TEST_FAILED")

HOT_SERVER_VERSION="2.1.82"
HOT_REVISION="2.1.82-hot-coding-terminal-repair-v70"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
_hot("hydrate-ok",hotServerVersion=HOT_SERVER_VERSION,v69Preserved=True,codingCompletionHardened=True,fenceRepairNormalized=True,candidateTerminalCamera=True,selfTest=True,underlyingBareFenceGapCount=len(_SELF_TEST.get("underlyingBareFenceGaps") or []))

def inspect_engine():
    result=_V69_INSPECT()
    if isinstance(result,dict):result.update({"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"v69Preserved":True,"codingBareFenceCannotComplete":True,"v27FenceContinuationRepair":True,"codingCandidateTerminalCamera":True,"codingTerminalSelfTest":dict(_SELF_TEST),"v69SourceCommit":_V69_COMMIT})
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    _camera(request_id,"v70-enter",contract=_CONTRACT,v69Preserved=True,codingCompletionHardened=True,fenceRepairNormalized=True)
    for event in _V69_GENERATE(payload,is_cancelled):yield event
