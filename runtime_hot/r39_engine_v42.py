"""R39 v42: brain-owned social fast path + bounded prefill cameras over v41."""
from __future__ import annotations
import json
import time
import urllib.request

_V41_COMMIT = "1b75ca5c46c1f67f19fb4a4f145722aa13718840"
_V41_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V41_COMMIT}/runtime_hot/r39_engine_v41.py"
_req = urllib.request.Request(_V41_URL, headers={"User-Agent":"swrlz-r39-v42"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V41_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V41_URL + "#v42", "exec"), globals(), globals())

_V41_INSPECT = inspect_engine
_V41_GENERATE = generate_events
HOT_SERVER_VERSION = "2.1.53"
HOT_REVISION = "2.1.53-hot-social-fastpath-prefill-cameras-v42"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION
_CAMERA_CONTRACT = "r39-prefill-camera-v1"


def _camera(request_id, stage, **fields):
    record={"contract":_CAMERA_CONTRACT,"requestId":request_id,"stage":stage,"engineVersion":HOT_SERVER_VERSION,"engineRevision":HOT_REVISION,"atUnixMs":int(time.time()*1000)}
    for key,value in fields.items():
        if value is None or isinstance(value,(str,int,float,bool)):
            record[str(key)[:64]]=value
    print("SWRLZ_R39_CAMERA "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)


def _payload_camera(payload, request_id):
    history=payload.get("history") if isinstance(payload,dict) else None
    history=history if isinstance(history,list) else []
    history_chars=sum(len(str(x.get("text") or x.get("content") or "")) for x in history if isinstance(x,dict))
    _camera(request_id,"payload",promptChars=len(str((payload or {}).get("prompt") or "")),historyMessages=len(history),historyChars=history_chars,responseDirectiveChars=len(str((payload or {}).get("responseDirective") or "")),hasTemporalContext=isinstance((payload or {}).get("swrlzUserTimeContext"),dict))


def _render_camera(payload, request_id):
    started=time.monotonic()
    try:
        prepared=_clean_noncoding_history(payload)
        prompt=base.render_chat_prompt(prepared)
        model=_get_model()
        tokens=model.tokenizer.encode(prompt)
        _camera(request_id,"rendered-prompt",renderedPromptChars=len(prompt),renderedPromptTokens=len(tokens),renderMs=int((time.monotonic()-started)*1000))
    except Exception as exc:
        _camera(request_id,"render-error",errorType=type(exc).__name__,elapsedMs=int((time.monotonic()-started)*1000))


def inspect_engine():
    result=_V41_INSPECT()
    if isinstance(result,dict):
        result.update({"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"socialFastPath":True,"socialFastPathOwner":"lalm","socialFastPathModelPrefill":False,"prefillCamera":True,"prefillCameraContract":_CAMERA_CONTRACT,"prefillCameraLogsPromptText":False,"v41SourceCommit":_V41_COMMIT})
    return result


def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload)
    _payload_camera(payload,request_id)
    # Exact simple greetings are already semantically resolved by the brain's social
    # classifier and safe finalizer. Do not spend a full model prefill/decode cycle to
    # rediscover a greeting that the acceptance layer may replace anyway.
    if _simple_social_turn(payload):
        started=time.monotonic()
        _camera(request_id,"social-fastpath-enter",route="social",modelPrefillSkipped=True)
        reply=_safe_social_reply(payload)
        yield {"type":"STATUS","phase":"SOCIAL_FASTPATH","reason":"Brain-owned greeting fast path resolved an exact social opener without model prefill."}
        yield {"type":"DELTA","phase":"WRITING","text":reply}
        yield {"type":"COMPLETED","phase":"COMPLETE","reason":"Exact social opener completed through the LALM social fast path."}
        _camera(request_id,"social-fastpath-complete",elapsedMs=int((time.monotonic()-started)*1000),replyChars=len(reply))
        return
    _render_camera(payload,request_id)
    for event in _V41_GENERATE(payload,is_cancelled):
        yield event
