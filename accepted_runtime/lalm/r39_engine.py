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
_V82_BATCH_COMMIT="c52341389f884f37fa9c6ba1c5950aea54fceffe"
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
        from api.chat_client_debug import _lockdown as _server_lockdown
        _server_lockdown("brain-hot-entry-" + str(stage)[:120], request_id=str(fields.get("requestId") or ""), brain=record)
    except Exception:
        pass

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
    HOT_SERVER_VERSION="2.1.112"
    HOT_REVISION="2.1.112-hot-lockdown-retrace-v90"
    _impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
    _impl.HOT_REVISION=HOT_REVISION

    def _request_id(payload):
        if not isinstance(payload,dict):
            return ""
        return str(payload.get("requestId") or payload.get("request_id") or "")[:128]

    def _semantic_lockdown(stage,request_id="",**fields):
        record={"contract":"r39-semantic-primitive-lockdown-v1","stage":str(stage)[:160],"requestId":str(request_id or "")[:128],"atUnixNs":time.time_ns(),"monotonicNs":time.perf_counter_ns()}
        for key,value in fields.items():
            if value is None or isinstance(value,(str,int,float,bool)):
                record[str(key)[:96]]=value
            elif isinstance(value,(list,tuple)):
                record[str(key)[:96]]=list(value)[:1024]
            else:
                record[str(key)[:96]]=str(value)[:16000]
        print("SWRLZ_R39_LOCKDOWN "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)
        try:
            from api.chat_client_debug import _lockdown as _server_lockdown
            _server_lockdown("brain-semantic-"+str(stage)[:120],request_id=request_id,brain=record)
        except Exception:
            pass

    _base_mod=getattr(_impl,"base",None)
    if _base_mod is not None:
        _render=getattr(_base_mod,"render_chat_prompt",None)
        if callable(_render) and not bool(getattr(_render,"_swrlz_lockdown_wrapper",False)):
            def _traced_render(payload,_original=_render):
                rid=_request_id(payload) if isinstance(payload,dict) else ""
                _semantic_lockdown("render-prompt-enter",rid,historyMessages=len(payload.get("history") or []) if isinstance(payload,dict) and isinstance(payload.get("history"),list) else 0,prompt=str(payload.get("prompt") or "")[:16000] if isinstance(payload,dict) else "")
                started=time.perf_counter_ns()
                out=_original(payload)
                _semantic_lockdown("render-prompt-exit",rid,renderedChars=len(str(out)),renderedPrompt=str(out)[:64000],durationNs=time.perf_counter_ns()-started)
                return out
            _traced_render._swrlz_lockdown_wrapper=True
            _base_mod.render_chat_prompt=_traced_render

        _tok_cls=getattr(_base_mod,"BpeTokenizer",None)
        if _tok_cls is not None:
            _encode=getattr(_tok_cls,"encode",None)
            if callable(_encode) and not bool(getattr(_encode,"_swrlz_lockdown_wrapper",False)):
                def _traced_encode(self,text,_original=_encode):
                    _semantic_lockdown("tokenizer-encode-enter",textChars=len(str(text)),text=str(text)[:64000])
                    started=time.perf_counter_ns()
                    out=_original(self,text)
                    ids=[int(x) for x in out]
                    # Bounded first-block look-ahead: decode each token independently
                    # when the tokenizer exposes decode(), so corruption can be
                    # separated from consumer/generator suspension.
                    microscope=[]
                    decode_fn=getattr(self,"decode",None)
                    for idx,tid in enumerate(ids[:100]):
                        piece=""
                        if callable(decode_fn):
                            try:
                                piece=str(decode_fn([tid]))
                            except Exception as exc:
                                piece="<decode-error:"+type(exc).__name__+">"
                        microscope.append({"ordinal":idx+1,"tokenId":tid,"piece":piece[:128],"previousTokenId":ids[idx-1] if idx>0 else None,"nextTokenId":ids[idx+1] if idx+1<len(ids) else None})
                    _semantic_lockdown("tokenizer-first-block-microscope",tokenCount=len(ids),tokens=microscope)
                    _semantic_lockdown("tokenizer-encode-exit",tokenCount=len(out),tokenIds=ids,durationNs=time.perf_counter_ns()-started)
                    return out
                _traced_encode._swrlz_lockdown_wrapper=True
                _tok_cls.encode=_traced_encode

        _sample_fn=getattr(_base_mod,"_sample",None)
        if callable(_sample_fn) and not bool(getattr(_sample_fn,"_swrlz_lockdown_wrapper",False)):
            def _traced_sample(logits,history,temperature,top_p,top_k,repetition_penalty,seed,_original=_sample_fn):
                started=time.perf_counter_ns()
                _semantic_lockdown("sample-enter",logitsShape=list(getattr(logits,"shape",()) or ()),history=list(history)[-64:],temperature=float(temperature),topP=float(top_p),topK=int(top_k),repetitionPenalty=float(repetition_penalty),seed=int(seed))
                out=_original(logits,history,temperature,top_p,top_k,repetition_penalty,seed)
                _semantic_lockdown("sample-exit",selectedTokenId=int(out),durationNs=time.perf_counter_ns()-started)
                return out
            _traced_sample._swrlz_lockdown_wrapper=True
            _base_mod._sample=_traced_sample

        _semantic_lockdown("semantic-primitive-cameras-installed",primitives=["render_chat_prompt","tokenizer.encode","sample"])

    # Prefill issue diagnostics are intentionally observational here.
    # Prior speculative compaction hooks are removed under the Project Start
    # gradual-mutation rule; cameras below identify which inherited boundary
    # actually changes prompt material before any next behavioral mutation.
    def _diag_payload(stage,payload):
        if not isinstance(payload,dict):
            _entry(stage,payloadType=type(payload).__name__)
            return
        history=payload.get("history")
        history=history if isinstance(history,list) else []
        system=[x for x in history if isinstance(x,dict) and str(x.get("role") or "").lower()=="system"]
        history_chars=sum(len(str(x.get("text") or x.get("content") or "")) for x in history if isinstance(x,dict))
        system_chars=sum(len(str(x.get("text") or x.get("content") or "")) for x in system)
        request_id=_request_id(payload)
        _entry(stage,requestId=request_id,historyMessages=len(history),
               historyChars=history_chars,systemMessages=len(system),systemChars=system_chars,
               promptChars=len(str(payload.get("prompt") or "")))
        # Lockdown diagnostic intentionally exposes the inference instructions and
        # bounded conversation material during this single-user development phase.
        snapshot={
            "contract":"r39-full-lockdown-payload-v1",
            "stage":stage,
            "requestId":request_id,
            "atUnixNs":time.time_ns(),
            "history":[
                {
                    "index":idx,
                    "role":str(item.get("role") or "")[:32],
                    "text":str(item.get("text") or item.get("content") or "")[:16000],
                    "chars":len(str(item.get("text") or item.get("content") or "")),
                }
                for idx,item in enumerate(history[:256]) if isinstance(item,dict)
            ],
            "prompt":str(payload.get("prompt") or "")[:16000],
            "promptChars":len(str(payload.get("prompt") or "")),
        }
        print("SWRLZ_R39_LOCKDOWN "+json.dumps(snapshot,ensure_ascii=False,separators=(",",":")),flush=True)
        try:
            from api.chat_client_debug import _lockdown as _server_lockdown
            _server_lockdown("brain-payload-" + str(stage)[:120], request_id=request_id, brain=snapshot)
        except Exception:
            pass

    # Unicode prompt-policy separation experiment. Unicode capability remains in the
    # tokenizer/model/runtime; only the inherited prose policy is removed from model
    # history before the exact inference boundary. Cameras prove the mutation.
    _unicode_policy=globals().get("_UNICODE_AWARENESS_POLICY")
    _pre_unicode_v41=globals().get("_V41_GENERATE")
    if isinstance(_unicode_policy,str) and _unicode_policy and callable(_pre_unicode_v41):
        def _v41_without_unicode_policy(payload,is_cancelled=None,_original=_pre_unicode_v41):
            if not isinstance(payload,dict):
                for event in _original(payload,is_cancelled): yield event
                return
            out=dict(payload); before=list(out.get("history") or []); after=[]; removed=0; removed_chars=0
            for item in before:
                if isinstance(item,dict) and str(item.get("role") or "").strip().lower()=="system":
                    value=str(item.get("text") or item.get("content") or "")
                    if value==_unicode_policy:
                        removed+=1; removed_chars+=len(value); continue
                after.append(item)
            out["history"]=after
            _entry("unicode-policy-separated",requestId=_request_id(payload),removedMessages=removed,
                   removedChars=removed_chars,beforeMessages=len(before),afterMessages=len(after),
                   unicodeCapabilityPreserved=True)
            for event in _original(out,is_cancelled): yield event
        globals()["_V41_GENERATE"]=_v41_without_unicode_policy

    # Full-map trace: retain all existing cameras and extend observation upward
    # through every reachable inherited generation bridge. This is observational only.
    def _discover_generate_chain(start,limit=80):
        chain=[]; current=start; seen=set()
        for depth in range(limit):
            if not callable(current) or id(current) in seen:break
            seen.add(id(current)); g=getattr(current,"__globals__",{})
            candidates=[]
            for name,value in g.items():
                if name.startswith("_V") and name.endswith("_GENERATE") and callable(value):
                    try:num=int(name[2:name.index("_GENERATE")])
                    except Exception:continue
                    candidates.append((num,name,value))
            if not candidates:break
            candidates.sort(reverse=True)
            num,name,nxt=candidates[0]
            chain.append((f"auto-depth-{depth}-v{num}",current,name,nxt))
            current=nxt
        return chain

    _camera_chain=()
    _v51_generate=globals().get("_V51_GENERATE")
    _v50_generate=getattr(_v51_generate,"__globals__",{}).get("_V50_GENERATE") if callable(_v51_generate) else None
    _v49_generate=getattr(_v50_generate,"__globals__",{}).get("_V49_GENERATE") if callable(_v50_generate) else None
    _v48_generate=getattr(_v49_generate,"__globals__",{}).get("_V48_GENERATE") if callable(_v49_generate) else None
    _v47_generate=getattr(_v48_generate,"__globals__",{}).get("_V47_GENERATE") if callable(_v48_generate) else None
    _v46_generate=getattr(_v47_generate,"__globals__",{}).get("_V46_GENERATE") if callable(_v47_generate) else None
    _v45_generate=getattr(_v46_generate,"__globals__",{}).get("_V45_GENERATE") if callable(_v46_generate) else None
    _v44_generate=getattr(_v45_generate,"__globals__",{}).get("_V44_GENERATE") if callable(_v45_generate) else None
    _v43_generate=getattr(_v44_generate,"__globals__",{}).get("_V43_GENERATE") if callable(_v44_generate) else None
    _v42_generate=getattr(_v43_generate,"__globals__",{}).get("_V42_GENERATE") if callable(_v43_generate) else None
    _v41_generate=getattr(_v42_generate,"__globals__",{}).get("_V41_GENERATE") if callable(_v42_generate) else None
    _camera_chain=_discover_generate_chain(globals().get("generate_events"))
    # Preserve the explicitly named lower-level bridge cameras as stable landmarks.
    _explicit_chain=(
        ("v51-v50",_v51_generate,"_V50_GENERATE",_v50_generate),
        ("v50-v49",_v50_generate,"_V49_GENERATE",_v49_generate),
        ("v49-v48",_v49_generate,"_V48_GENERATE",_v48_generate),
        ("v48-v47",_v48_generate,"_V47_GENERATE",_v47_generate),
        ("v47-v46",_v47_generate,"_V46_GENERATE",_v46_generate),
        ("v46-v45",_v46_generate,"_V45_GENERATE",_v45_generate),
        ("v45-v44",_v45_generate,"_V44_GENERATE",_v44_generate),
        ("v44-v43",_v44_generate,"_V43_GENERATE",_v43_generate),
        ("v43-v42",_v43_generate,"_V42_GENERATE",_v42_generate),
        ("v42-v41",_v42_generate,"_V41_GENERATE",_v41_generate),
    )
    _seen_slots={(id(owner),slot) for _,owner,slot,_ in _camera_chain if callable(owner)}
    _camera_chain+=tuple(x for x in _explicit_chain if callable(x[1]) and (id(x[1]),x[2]) not in _seen_slots)
    _installed_boundaries=0
    for _boundary,_owner,_slot,_original in _camera_chain:
        if not callable(_owner) or not callable(_original):
            continue
        def _make_camera_bridge(boundary,original):
            def _bridge(payload,is_cancelled=None):
                _diag_payload("prefill-boundary-"+boundary,payload)
                for event in original(payload,is_cancelled):
                    yield event
            return _bridge
        _owner.__globals__[_slot]=_make_camera_bridge(_boundary,_original)
        _installed_boundaries+=1
    _entry("prefill-boundary-cameras-installed",boundaries=_installed_boundaries, mutationMode="observe-only", coverage="full-reachable-generation-chain")
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
