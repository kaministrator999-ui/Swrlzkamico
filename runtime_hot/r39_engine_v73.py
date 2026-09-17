"""R39 v73: repair the inherited v55 n-gram sampler NumPy namespace.

Preserves v72 diagnostics and all v71/v70/v69 programming behavior. The historical
v55 sampler switches to its n-gram branch once two generated tokens exist and then
uses the bare global `np`. The exec-based lineage never guaranteed that alias in the
shared hot-module namespace, so the third decode iteration can fail with NameError.
This wrapper restores that dependency and fail-closes hydration with a threshold test.
"""
from __future__ import annotations
import json,time,urllib.request
import numpy as np

_V72_COMMIT="3c41765183650793ad6c4c552c2d2a2cc5db6056"
_V72_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V72_COMMIT}/runtime_hot/r39_engine_v72.py"
_V73_CONTRACT="r39-v73-ngram-numpy-namespace-repair-v1"
_NUMPY=np

def _v73_boot(stage,**fields):
    record={"contract":_V73_CONTRACT,"stage":stage,"atUnixMs":int(time.time()*1000)}
    for key,value in fields.items():
        if value is None or isinstance(value,(str,int,float,bool)):
            record[str(key)[:64]]=value
    print("SWRLZ_R39_HOTLOAD "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

_v73_boot("v72-fetch-start",v72SourceCommit=_V72_COMMIT)
_req=urllib.request.Request(_V72_URL,headers={"User-Agent":"swrlz-r39-v73"})
with urllib.request.urlopen(_req,timeout=20) as _response:
    _source=_response.read(4_000_001)
if len(_source)>4_000_000:
    raise RuntimeError("R39_V72_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V72_URL+"#v73","exec"),globals(),globals())

_V72_INSPECT=inspect_engine
_V72_GENERATE=generate_events

# v55's `_ngram_guarded_sample` resolves `np` dynamically from this shared exec
# namespace. Restore that dependency after the entire inherited lineage hydrates so
# later nested modules cannot accidentally leave the sampler without NumPy.
np=_NUMPY
if not callable(globals().get("_ngram_guarded_sample")):
    raise RuntimeError("R39_V73_NGRAM_SAMPLER_UNAVAILABLE")

def _self_test_v73():
    checks={"numpyBound":globals().get("np") is _NUMPY}
    try:
        logits=_NUMPY.asarray([0.1,0.2,0.3,0.4,0.5,0.6],dtype=_NUMPY.float32)
        token=_ngram_guarded_sample(logits,[1,2],0.12,0.9,6,1.05,12345)
        checks["twoTokenThresholdExecutes"]=isinstance(token,(int,_NUMPY.integer)) and 0<=int(token)<logits.size
    except Exception:
        checks["twoTokenThresholdExecutes"]=False
    return {"ok":all(checks.values()),"checks":checks,"contract":_V73_CONTRACT}

_V73_SELF_TEST=_self_test_v73()
if not _V73_SELF_TEST.get("ok"):
    raise RuntimeError("R39_V73_NGRAM_NUMPY_NAMESPACE_SELF_TEST_FAILED")

HOT_SERVER_VERSION="2.1.85"
HOT_REVISION="2.1.85-hot-ngram-numpy-namespace-repair-v73"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
_v73_boot(
    "hydrate-ok",
    hotServerVersion=HOT_SERVER_VERSION,
    v72Preserved=True,
    ngramNumpyNamespaceRepair=True,
    selfTest=True,
)

def inspect_engine():
    result=_V72_INSPECT()
    if isinstance(result,dict):
        result.update({
            "hotServerVersion":HOT_SERVER_VERSION,
            "hotRevision":HOT_REVISION,
            "v72Preserved":True,
            "ngramNumpyNamespaceRepair":True,
            "ngramNumpyNamespaceContract":_V73_CONTRACT,
            "ngramNumpyNamespaceSelfTest":dict(_V73_SELF_TEST),
            "v72SourceCommit":_V72_COMMIT,
        })
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    _camera(request_id,"v73-enter",contract=_V73_CONTRACT,v72Preserved=True,ngramNumpyNamespaceRepair=True)
    for event in _V72_GENERATE(payload,is_cancelled):
        yield event
