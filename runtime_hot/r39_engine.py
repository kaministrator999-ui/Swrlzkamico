"""Hot R39 entrypoint v90: protected factual evidence over v89."""
from __future__ import annotations
import json,time,urllib.request

_V74_COMMIT="58bfd905d0d3281b6adc1669ca8482cd04cc300c"
_V74_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V74_COMMIT}/runtime_hot/r39_engine_v74.py"
_V75_COMMIT="8a92721addbeb6709b132f826404e805d8e35029"
_V75_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V75_COMMIT}/runtime_hot/r39_engine_v75_overlay.py"
_V76_COMMIT="65bcfbb1b20bda7fb71e0ea5b52f811a2d09725b"
_V76_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V76_COMMIT}/runtime_hot/r39_engine_v76_overlay.py"
_V77_COMMIT="fae655929b24c1eff3951fba1178a488394dce53"
_V77_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V77_COMMIT}/runtime_hot/r39_engine_v77_overlay.py"
_V78_COMMIT="042baf81ad511205d49f4564e7f7b092a6ae6ac0"
_V78_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V78_COMMIT}/runtime_hot/r39_engine_v78_overlay.py"
_V79_COMMIT="188a830fee42b91849196a3ae18ef40af178a644"
_V79_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V79_COMMIT}/runtime_hot/r39_engine_v79_overlay.py"
_V80_COMMIT="44f154cf6a4ae46eb232665f36815eec2b2d8496"
_V80_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V80_COMMIT}/runtime_hot/r39_engine_v80_overlay.py"
_V81_COMMIT="94d09dce6d03d3a51632f8b6d830265481a26372"
_V81_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V81_COMMIT}/runtime_hot/r39_engine_v81_overlay.py"
_V82_BATCH_COMMIT="2807923fc71fc54c634b80aff9080202de1efc54"
_V82_BATCH_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V82_BATCH_COMMIT}/runtime_hot/r39_batch_prefill.py"
_V84_COMMIT="2e959bb9fea0af38c7f2c1e35745c3a8a8c9f066"
_V84_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V84_COMMIT}/runtime_hot/r39_engine_v84_overlay.py"
_V85_COMMIT="f63e6d1999255806f65e0d1d670d46ac8ab86994"
_V85_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V85_COMMIT}/runtime_hot/r39_engine_v85_overlay.py"
_V86_COMMIT="abc895d9d268ccae6efc5c8bb2d5cfa1bb982c7f"
_V86_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V86_COMMIT}/runtime_hot/r39_engine_v86_overlay.py"
_V87_COMMIT="e59f572d3afbbf0d825d023531cc10987572a7aa"
_V87_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V87_COMMIT}/runtime_hot/r39_engine_v87_overlay.py"
_V88_COMMIT="46eb91e1f1477069777c06a21cc8eced5c7873cb"
_V88_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V88_COMMIT}/runtime_hot/r39_engine_v88_overlay.py"
_V89_COMMIT="4cee6d758121526d170ef2a44e1ad2d365676c43"
_V89_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V89_COMMIT}/runtime_hot/r39_engine_v89_overlay.py"
_V90_COMMIT="5c242ddc4246e388ebc6478c74c3e21ceb6864ec"
_V90_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V90_COMMIT}/runtime_hot/r39_engine_v90_overlay.py"

def _entry(stage,**fields):
    record={"contract":"r39-hot-entry-camera-v1","stage":stage,"target":"v90","atUnixMs":int(time.time()*1000)}
    for k,v in fields.items():
        if v is None or isinstance(v,(str,int,float,bool)):record[str(k)[:64]]=v
    print("SWRLZ_R39_HOT_ENTRY "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

try:
    _entry("fetch-start",sourceCommit=_V74_COMMIT,overlayCommit=_V75_COMMIT,v76OverlayCommit=_V76_COMMIT,v77OverlayCommit=_V77_COMMIT,v78OverlayCommit=_V78_COMMIT,v79OverlayCommit=_V79_COMMIT,v80OverlayCommit=_V80_COMMIT,v81OverlayCommit=_V81_COMMIT,v82BatchCommit=_V82_BATCH_COMMIT,v84OverlayCommit=_V84_COMMIT,v85OverlayCommit=_V85_COMMIT,v86OverlayCommit=_V86_COMMIT,v87OverlayCommit=_V87_COMMIT,v88OverlayCommit=_V88_COMMIT,v89OverlayCommit=_V89_COMMIT,v90OverlayCommit=_V90_COMMIT)
    _request=urllib.request.Request(_V74_URL,headers={"User-Agent":"swrlz-r39-v75-loader"})
    with urllib.request.urlopen(_request,timeout=20) as _response:_source=_response.read(4000001)
    if len(_source)>4000000:raise RuntimeError("R39_V74_SOURCE_TOO_LARGE")
    _entry("fetch-ok",sourceBytes=len(_source))
    exec(compile(_source.decode("utf-8"),_V74_URL+"#v75-base","exec"),globals(),globals())

    _overlay_request=urllib.request.Request(_V75_URL,headers={"User-Agent":"swrlz-r39-v75-overlay"})
    with urllib.request.urlopen(_overlay_request,timeout=20) as _response:_overlay=_response.read(1000001)
    if len(_overlay)>1000000:raise RuntimeError("R39_V75_OVERLAY_TOO_LARGE")
    _entry("overlay-fetch-ok",overlayBytes=len(_overlay))
    exec(compile(_overlay.decode("utf-8"),_V75_URL+"#v75-overlay","exec"),globals(),globals())

    _v76_request=urllib.request.Request(_V76_URL,headers={"User-Agent":"swrlz-r39-v76-overlay"})
    with urllib.request.urlopen(_v76_request,timeout=20) as _response:_v76_overlay=_response.read(1000001)
    if len(_v76_overlay)>1000000:raise RuntimeError("R39_V76_OVERLAY_TOO_LARGE")
    _entry("v76-overlay-fetch-ok",overlayBytes=len(_v76_overlay))
    exec(compile(_v76_overlay.decode("utf-8"),_V76_URL+"#v76-overlay","exec"),globals(),globals())

    _v77_request=urllib.request.Request(_V77_URL,headers={"User-Agent":"swrlz-r39-v77-overlay"})
    with urllib.request.urlopen(_v77_request,timeout=20) as _response:_v77_overlay=_response.read(1000001)
    if len(_v77_overlay)>1000000:raise RuntimeError("R39_V77_OVERLAY_TOO_LARGE")
    _entry("v77-overlay-fetch-ok",overlayBytes=len(_v77_overlay))
    exec(compile(_v77_overlay.decode("utf-8"),_V77_URL+"#v77-overlay","exec"),globals(),globals())

    _v78_request=urllib.request.Request(_V78_URL,headers={"User-Agent":"swrlz-r39-v78-overlay"})
    with urllib.request.urlopen(_v78_request,timeout=20) as _response:_v78_overlay=_response.read(1000001)
    if len(_v78_overlay)>1000000:raise RuntimeError("R39_V78_OVERLAY_TOO_LARGE")
    _entry("v78-overlay-fetch-ok",overlayBytes=len(_v78_overlay))
    exec(compile(_v78_overlay.decode("utf-8"),_V78_URL+"#v78-overlay","exec"),globals(),globals())

    _v79_request=urllib.request.Request(_V79_URL,headers={"User-Agent":"swrlz-r39-v79-overlay"})
    with urllib.request.urlopen(_v79_request,timeout=20) as _response:_v79_overlay=_response.read(1000001)
    if len(_v79_overlay)>1000000:raise RuntimeError("R39_V79_OVERLAY_TOO_LARGE")
    _entry("v79-overlay-fetch-ok",overlayBytes=len(_v79_overlay))
    exec(compile(_v79_overlay.decode("utf-8"),_V79_URL+"#v79-overlay","exec"),globals(),globals())

    _v80_request=urllib.request.Request(_V80_URL,headers={"User-Agent":"swrlz-r39-v80-overlay"})
    with urllib.request.urlopen(_v80_request,timeout=20) as _response:_v80_overlay=_response.read(1000001)
    if len(_v80_overlay)>1000000:raise RuntimeError("R39_V80_OVERLAY_TOO_LARGE")
    _entry("v80-overlay-fetch-ok",overlayBytes=len(_v80_overlay))
    exec(compile(_v80_overlay.decode("utf-8"),_V80_URL+"#v80-overlay","exec"),globals(),globals())

    _v81_request=urllib.request.Request(_V81_URL,headers={"User-Agent":"swrlz-r39-v81-overlay"})
    with urllib.request.urlopen(_v81_request,timeout=20) as _response:_v81_overlay=_response.read(1000001)
    if len(_v81_overlay)>1000000:raise RuntimeError("R39_V81_OVERLAY_TOO_LARGE")
    _entry("v81-overlay-fetch-ok",overlayBytes=len(_v81_overlay))
    exec(compile(_v81_overlay.decode("utf-8"),_V81_URL+"#v81-overlay","exec"),globals(),globals())

    _v82_batch_request=urllib.request.Request(_V82_BATCH_URL,headers={"User-Agent":"swrlz-r39-v82-batch"})
    with urllib.request.urlopen(_v82_batch_request,timeout=20) as _response:_v82_batch_source=_response.read(1000001)
    if len(_v82_batch_source)>1000000:raise RuntimeError("R39_V82_BATCH_SOURCE_TOO_LARGE")
    _entry("v82-batch-fetch-ok",batchBytes=len(_v82_batch_source))
    exec(compile(_v82_batch_source.decode("utf-8"),_V82_BATCH_URL+"#v82-batch","exec"),_batch.__dict__,_batch.__dict__)

    _batch_install=_batch.install(_impl)
    if not isinstance(_batch_install,dict) or not _batch_install.get("installed"):
        raise RuntimeError("R39_V83_BATCH_REINSTALL_NOT_PROVEN")
    _entry("v83-batch-reinstall-ok",installed=True,blockTokens=int(_batch_install.get("blockTokens") or 0),nativeBatchAvailable=bool(_batch_install.get("nativeBatchAvailable")))
    HOT_SERVER_VERSION="2.1.95"
    HOT_REVISION="2.1.95-hot-batch-reinstall-v83"
    _impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
    _impl.HOT_REVISION=HOT_REVISION

    _v85_request=urllib.request.Request(_V85_URL,headers={"User-Agent":"swrlz-r39-v85-overlay"})
    with urllib.request.urlopen(_v85_request,timeout=20) as _response:_v85_overlay=_response.read(1000001)
    if len(_v85_overlay)>1000000:raise RuntimeError("R39_V85_OVERLAY_TOO_LARGE")
    _entry("v85-overlay-fetch-ok",overlayBytes=len(_v85_overlay))
    exec(compile(_v85_overlay.decode("utf-8"),_V85_URL+"#v85-overlay","exec"),globals(),globals())

    _v86_request=urllib.request.Request(_V86_URL,headers={"User-Agent":"swrlz-r39-v86-overlay"})
    with urllib.request.urlopen(_v86_request,timeout=20) as _response:_v86_overlay=_response.read(1000001)
    if len(_v86_overlay)>1000000:raise RuntimeError("R39_V86_OVERLAY_TOO_LARGE")
    _entry("v86-overlay-fetch-ok",overlayBytes=len(_v86_overlay))
    exec(compile(_v86_overlay.decode("utf-8"),_V86_URL+"#v86-overlay","exec"),globals(),globals())

    _v87_request=urllib.request.Request(_V87_URL,headers={"User-Agent":"swrlz-r39-v87-overlay"})
    with urllib.request.urlopen(_v87_request,timeout=20) as _response:_v87_overlay=_response.read(1000001)
    if len(_v87_overlay)>1000000:raise RuntimeError("R39_V87_OVERLAY_TOO_LARGE")
    _entry("v87-overlay-fetch-ok",overlayBytes=len(_v87_overlay))
    exec(compile(_v87_overlay.decode("utf-8"),_V87_URL+"#v87-overlay","exec"),globals(),globals())

    _v88_request=urllib.request.Request(_V88_URL,headers={"User-Agent":"swrlz-r39-v88-overlay"})
    with urllib.request.urlopen(_v88_request,timeout=20) as _response:_v88_overlay=_response.read(1000001)
    if len(_v88_overlay)>1000000:raise RuntimeError("R39_V88_OVERLAY_TOO_LARGE")
    _entry("v88-overlay-fetch-ok",overlayBytes=len(_v88_overlay))
    exec(compile(_v88_overlay.decode("utf-8"),_V88_URL+"#v88-overlay","exec"),globals(),globals())

    _v89_request=urllib.request.Request(_V89_URL,headers={"User-Agent":"swrlz-r39-v89-overlay"})
    with urllib.request.urlopen(_v89_request,timeout=20) as _response:_v89_overlay=_response.read(1000001)
    if len(_v89_overlay)>1000000:raise RuntimeError("R39_V89_OVERLAY_TOO_LARGE")
    _entry("v89-overlay-fetch-ok",overlayBytes=len(_v89_overlay))
    exec(compile(_v89_overlay.decode("utf-8"),_V89_URL+"#v89-overlay","exec"),globals(),globals())

    _v90_request=urllib.request.Request(_V90_URL,headers={"User-Agent":"swrlz-r39-v90-overlay"})
    with urllib.request.urlopen(_v90_request,timeout=20) as _response:_v90_overlay=_response.read(1000001)
    if len(_v90_overlay)>1000000:raise RuntimeError("R39_V90_OVERLAY_TOO_LARGE")
    _entry("v90-overlay-fetch-ok",overlayBytes=len(_v90_overlay))
    exec(compile(_v90_overlay.decode("utf-8"),_V90_URL+"#v90-overlay","exec"),globals(),globals())

    _inspect=inspect_engine() if callable(globals().get("inspect_engine")) else {}
    _self_test=_inspect.get("programmingContinuationSemanticSelfTest") if isinstance(_inspect,dict) else None
    if not isinstance(_self_test,dict) or not _self_test.get("ok"):
        raise RuntimeError("R39_V75_ENTRY_SELF_TEST_NOT_PROVEN")
    # v90 semantic overlays are preserved, but the active runtime authority is
    # the optimized 2.1.103 kernel lineage selected by this entrypoint.
    HOT_SERVER_VERSION="2.1.107"
    HOT_REVISION="2.1.107-hot-v49-v48-prefill-boundary-v90"
    _impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
    _impl.HOT_REVISION=HOT_REVISION

    # Compact at the actual final policy-wrapper boundary. v55 -> v54 -> v53 ->
    # v52 -> v51 inject the synthetic Brain turns in that order. Intercept the
    # inherited v50 generator called by v51: at that point all verbose policy
    # turns already exist, while model rendering/prefill has not started.
    _policy_markers=(
        "[SWRLZ_CONVERSATION_STATE ","[SWRLZ_CONTEXT_FOCUS ","[SWRLZ_TRAJECTORY",
        "[SWRLZ_REASONING","[SWRLZ_UNICODE","[SWRLZ_MAP_TO_POINT",
        "[SWRLZ_CONVERSATION_INTELLIGENCE",
    )
    def _compact_policy_payload(payload):
        if not isinstance(payload,dict): return payload,0,0,0
        enriched=dict(payload); history=list(enriched.get("history") or [])
        kept=[]; removed=0; removed_chars=0
        for turn in history:
            text=str(turn.get("text") or "") if isinstance(turn,dict) else ""
            synthetic=(isinstance(turn,dict) and str(turn.get("role") or "").lower()=="system"
                       and any(m in text[:128] for m in _policy_markers))
            if synthetic: removed+=1; removed_chars+=len(text)
            else: kept.append(turn)
        if removed:
            capsule="[SWRLZ_BRAIN v3] literal-user-first; preserve-continuity; smallest-sufficient-context; evidence-boundary; multi-act."
            kept=[{"role":"system","text":capsule}]+kept
            enriched["history"]=kept
            return enriched,removed,removed_chars,len(capsule)
        return enriched,0,0,0

    _v51_owner=globals().get("_V51_GENERATE")
    _v50_original=getattr(_v51_owner,"__globals__",{}).get("_V50_GENERATE") if callable(_v51_owner) else None
    if not callable(_v50_original):
        raise RuntimeError("R39_COMPACT_PREFILL_V50_BOUNDARY_UNAVAILABLE")
    def _compact_v50_generate(payload,is_cancelled=None):
        compacted,removed,removed_chars,capsule_chars=_compact_policy_payload(payload)
        _entry("compact-prefill-final-policy-boundary",
               requestId=_request_id(payload) if isinstance(payload,dict) else "",
               removedPolicySegments=removed,removedPolicyChars=removed_chars,
               capsuleChars=capsule_chars)
        for event in _v50_original(compacted,is_cancelled): yield event
    _v51_owner.__globals__["_V50_GENERATE"]=_compact_v50_generate

    # v50 normal generation delegates to v49, whose _V48_GENERATE bridge is the
    # last unconditional path after v51-v55 have injected their synthetic policy
    # turns. Patch that bridge as well so all legacy Brain policy prose is removed
    # before v48+ conditional research/evidence handling and base inference.
    _v50_owner=getattr(_v51_owner,"__globals__",{}).get("_V50_GENERATE") if callable(_v51_owner) else None
    _v49_generate=getattr(_v50_owner,"__globals__",{}).get("_V49_GENERATE") if callable(_v50_owner) else None
    _v48_original=getattr(_v49_generate,"__globals__",{}).get("_V48_GENERATE") if callable(_v49_generate) else None
    if not callable(_v48_original):
        raise RuntimeError("R39_COMPACT_PREFILL_V49_V48_BOUNDARY_UNAVAILABLE")
    def _compact_v48_generate(payload,is_cancelled=None):
        compacted,removed,removed_chars,capsule_chars=_compact_policy_payload(payload)
        _entry("compact-prefill-final-render-path",
               requestId=_request_id(payload) if isinstance(payload,dict) else "",
               removedPolicySegments=removed,removedPolicyChars=removed_chars,
               capsuleChars=capsule_chars)
        for event in _v48_original(compacted,is_cancelled): yield event
    _v49_generate.__globals__["_V48_GENERATE"]=_compact_v48_generate
    _entry("compact-prefill-installed",finalPolicyBoundary=True,v49v48Boundary=True)
    _entry("hydrate-ok",hotServerVersion=HOT_SERVER_VERSION,
           hotRevision=HOT_REVISION,batchSourceCommit=_V82_BATCH_COMMIT,
           responseContract=callable(globals().get("_response_contract")),
           responseContractGaps=callable(globals().get("_response_contract_gaps")),
           repairPayload=callable(globals().get("_repair_payload")),
           candidateGenerator=callable(globals().get("_V24_GENERATE_FOR_V27")),
           programmingProfile=callable(globals().get("_programming_profile")),
           camera=callable(globals().get("_camera")),
           ngramSampler=callable(globals().get("_ngram_guarded_sample")),
           artifactContinuation=True,continuationProvenance=True,runnableEditSemanticGate=True,coldPrefillProfileCamera=True,prefillKernelProfileCamera=True,onlineResearchHandoffCamera=True,inheritedResearchCallCamera=True,researchTelemetryScopeCamera=True,batchFallbackDetailCamera=True,batchFallbackExceptCamera=True,batchAdapterReinstalled=True,researchPlannerScoped=True,liveResearchPlannerStatus=True,promptCompositionCamera=True,requestFirstFreshFactual=True,protectedFactualEvidence=True,selfTest=True)
except Exception as exc:
    _entry("hydrate-failed",errorType=type(exc).__name__,errorMessage=str(exc)[:240]);raise
