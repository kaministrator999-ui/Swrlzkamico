"""R39 v72: bounded coding inference failure detail camera over v71.

Preserves all v71/v70 generation semantics. This wrapper only records the suppressed
base-generator failure category/type/detail needed to diagnose the two-token coding crash.
"""
from __future__ import annotations
import json,re,time,urllib.request

_V71_COMMIT="b1bfa7eaec5eec7b21b020a7f8d7ec423416d5ab"
_V71_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V71_COMMIT}/runtime_hot/r39_engine_v71.py"
_V72_CONTRACT="r39-v72-coding-inference-failure-detail-v1"

def _v72_boot(stage,**fields):
    record={"contract":_V72_CONTRACT,"stage":stage,"atUnixMs":int(time.time()*1000)}
    for key,value in fields.items():
        if value is None or isinstance(value,(str,int,float,bool)):
            record[str(key)[:64]]=value
    print("SWRLZ_R39_HOTLOAD "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

_v72_boot("v71-fetch-start",v71SourceCommit=_V71_COMMIT)
_req=urllib.request.Request(_V71_URL,headers={"User-Agent":"swrlz-r39-v72"})
with urllib.request.urlopen(_req,timeout=20) as _response:
    _source=_response.read(4_000_001)
if len(_source)>4_000_000:
    raise RuntimeError("R39_V71_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V71_URL+"#v72","exec"),globals(),globals())

_V71_INSPECT=inspect_engine
_V71_GENERATE=generate_events
_V71_CANDIDATE_GENERATE=globals().get("_V24_GENERATE_FOR_V27")
if not callable(_V71_CANDIDATE_GENERATE) or not callable(globals().get("_camera")):
    raise RuntimeError("R39_V72_CANDIDATE_CAMERA_BOUNDARY_UNAVAILABLE")

_FAILURE_RE=re.compile(r"Hot local R39 inference failed \(([^:()]{1,80}):\s*(.*?)\)\.?$",re.I|re.S)

def _terminal_failure_detail(event):
    categories=event.get("categories") if isinstance(event,dict) else None
    category=""
    if isinstance(categories,(list,tuple)) and categories:
        category=str(categories[0] or "")[:96]
    reason=str(event.get("reason") or "") if isinstance(event,dict) else ""
    exception_type=""
    detail=""
    match=_FAILURE_RE.search(reason)
    if match:
        exception_type=str(match.group(1) or "").strip()[:80]
        detail=re.sub(r"\s+"," ",str(match.group(2) or "")).strip()[:220]
    elif reason:
        detail=re.sub(r"\s+"," ",reason).strip()[:220]
    return category,exception_type,detail

def _v72_candidate_generate(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    pass_kind="repair" if isinstance(payload,dict) and payload.get("_swrlzRepairPass") else "first"
    for event in _V71_CANDIDATE_GENERATE(payload,is_cancelled):
        if isinstance(event,dict) and str(event.get("type") or "") in {"FAILED","CANCELLED"}:
            category,exception_type,detail=_terminal_failure_detail(event)
            _camera(
                request_id,
                "coding-inference-terminal-detail",
                contract=_V72_CONTRACT,
                passKind=pass_kind,
                terminalType=str(event.get("type") or ""),
                category=category,
                exceptionType=exception_type,
                detailPreview=detail,
            )
        yield event

# v27 resolves this global dynamically for both first candidate and bounded repair.
_V24_GENERATE_FOR_V27=_v72_candidate_generate

def _self_test_v72():
    sample={
        "type":"FAILED",
        "reason":"Hot local R39 inference failed (ValueError: sample shape mismatch).",
        "categories":["R39_HOT_INFERENCE_RUNTIME_FAILED"],
    }
    category,exception_type,detail=_terminal_failure_detail(sample)
    checks={
        "candidateBoundary":callable(_V71_CANDIDATE_GENERATE),
        "category":category=="R39_HOT_INFERENCE_RUNTIME_FAILED",
        "exceptionType":exception_type=="ValueError",
        "boundedDetail":detail=="sample shape mismatch",
    }
    return {"ok":all(checks.values()),"checks":checks,"contract":_V72_CONTRACT}

_V72_SELF_TEST=_self_test_v72()
if not _V72_SELF_TEST.get("ok"):
    raise RuntimeError("R39_V72_FAILURE_DETAIL_SELF_TEST_FAILED")

HOT_SERVER_VERSION="2.1.84"
HOT_REVISION="2.1.84-hot-coding-inference-failure-detail-v72"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
_v72_boot(
    "hydrate-ok",
    hotServerVersion=HOT_SERVER_VERSION,
    v71Preserved=True,
    failureDetailCamera=True,
    selfTest=True,
)

def inspect_engine():
    result=_V71_INSPECT()
    if isinstance(result,dict):
        result.update({
            "hotServerVersion":HOT_SERVER_VERSION,
            "hotRevision":HOT_REVISION,
            "v71Preserved":True,
            "codingInferenceFailureDetailCamera":True,
            "codingInferenceFailureDetailContract":_V72_CONTRACT,
            "codingInferenceFailureDetailSelfTest":dict(_V72_SELF_TEST),
            "v71SourceCommit":_V71_COMMIT,
        })
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    _camera(request_id,"v72-enter",contract=_V72_CONTRACT,v71Preserved=True,failureDetailCamera=True)
    for event in _V71_GENERATE(payload,is_cancelled):
        yield event
