"""R39 v58: planner namespace repair + active hot-load diagnostics over v57.

Preserves v57/v56 conversation intelligence and fixes the second inherited namespace
fault exposed after the legacy `base` alias was repaired.  The canonical response
budget planner lives on `_impl`; v54/v55/v56 expect a module-level planner symbol.
Bridge that symbol before loading v57, then verify the inherited planner contract.

Also emits bounded boot/contract cameras that make hot-loader failures visible in
production logs without logging prompts, responses, secrets, or hidden reasoning.
"""
from __future__ import annotations
import json
import time
import urllib.request

_V57_COMMIT="e5f17eedf60c22bf92aa296125aed91535f16a18"
_V57_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V57_COMMIT}/runtime_hot/r39_engine_v57.py"
_BOOT_CONTRACT="r39-hot-loader-camera-v1"

def _boot(stage,**fields):
    record={"contract":_BOOT_CONTRACT,"stage":stage,"targetVersion":"2.1.69","targetRevision":"2.1.69-hot-planner-namespace-loader-camera-v58","atUnixMs":int(time.time()*1000)}
    for key,value in fields.items():
        if value is None or isinstance(value,(str,int,float,bool)):
            record[str(key)[:64]]=value
    print("SWRLZ_R39_HOTLOAD "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

# Existing hot hydration keeps the canonical v17 implementation module in `_impl`.
# Bridge its planner into the exec namespace before v57 -> v56 -> v55 -> v54 loads.
_impl=globals().get("_impl")
if _impl is None:
    _boot("preflight-failed",missing="_impl")
    raise RuntimeError("R39_ACTIVE_IMPL_UNAVAILABLE")
_impl_plan=getattr(_impl,"_plan_response_budget",None)
if not callable(_impl_plan):
    _boot("preflight-failed",missing="_impl._plan_response_budget")
    raise RuntimeError("R39_ACTIVE_RESPONSE_PLANNER_UNAVAILABLE")
_plan_response_budget=_impl_plan
_boot("preflight-ok",plannerBridge="_impl._plan_response_budget",v57SourceCommit=_V57_COMMIT)

try:
    _req=urllib.request.Request(_V57_URL,headers={"User-Agent":"swrlz-r39-v58"})
    with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
    if len(_source)>4_000_000:raise RuntimeError("R39_V57_SOURCE_TOO_LARGE")
    exec(compile(_source.decode("utf-8"),_V57_URL+"#v58","exec"),globals(),globals())
except Exception as exc:
    _boot("hydrate-failed",errorType=type(exc).__name__,errorMessage=str(exc)[:240])
    raise

_V57_INSPECT=inspect_engine
_V57_GENERATE=generate_events
HOT_SERVER_VERSION="2.1.69"
HOT_REVISION="2.1.69-hot-planner-namespace-loader-camera-v58"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

# Validate the exact inherited contracts that caused the two recent load failures.
_contracts={
    "planner":callable(globals().get("_plan_response_budget")),
    "v54Planner":callable(globals().get("_V54_PLAN_RESPONSE_BUDGET")),
    "v55Planner":callable(globals().get("_V55_PLAN_RESPONSE_BUDGET")),
    "baseSampler":callable(getattr(globals().get("base"),"_sample",None)),
    "camera":callable(globals().get("_camera")),
}
if not all(_contracts.values()):
    missing=",".join(key for key,value in _contracts.items() if not value)
    _boot("contract-failed",missing=missing)
    raise RuntimeError("R39_INHERITED_CONTRACT_MISSING:"+missing)
_boot("hydrate-ok",planner=True,v54Planner=True,v55Planner=True,baseSampler=True,camera=True)

def inspect_engine():
    result=_V57_INSPECT()
    if isinstance(result,dict):result.update({
        "hotServerVersion":HOT_SERVER_VERSION,
        "hotRevision":HOT_REVISION,
        "plannerNamespaceRepair":True,
        "plannerNamespaceTarget":"_impl._plan_response_budget",
        "hotLoaderCamera":True,
        "hotLoaderCameraContract":_BOOT_CONTRACT,
        "hotLoaderCameraLogsPromptOrResponseText":False,
        "inheritedContractPreflight":True,
        "v57SourceCommit":_V57_COMMIT,
    })
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    _camera(request_id,"v58-contract-ready",contract="swrlz_inherited_planner_namespace_v1",plannerBridge="_impl._plan_response_budget",inheritedContractsVerified=True)
    try:
        for event in _V57_GENERATE(payload,is_cancelled):yield event
    except Exception as exc:
        _camera(request_id,"v58-generate-exception",contract="swrlz_inherited_planner_namespace_v1",errorType=type(exc).__name__,errorMessage=str(exc)[:240])
        raise
