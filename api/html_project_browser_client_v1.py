"""§C's remote browser tool. It never grants publication authority."""
from __future__ import annotations
import hmac,json,os,secrets,time,urllib.error,urllib.request
try:
    from browser_worker_protocol_v1 import VERSION,MAX_BODY,encode,mac,file_hashes,verify_envelope
except ImportError:
    from api.browser_worker_protocol_v1 import VERSION,MAX_BODY,encode,mac,file_hashes,verify_envelope
URL="https://kamiloki-swrlz-browser-worker.hf.space/v1/render"
class BrowserUnavailable(RuntimeError):pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise BrowserUnavailable("BROWSER_WORKER_REDIRECT")
def validate(project,files,canvas=False,checks=None,*,key=None):
    key=key or os.environ.get("SWRLZ_BROWSER_WORKER_KEY","")
    if len(key)!=64:raise BrowserUnavailable("BROWSER_WORKER_NOT_CONFIGURED")
    nonce=secrets.token_hex(16)
    raw=encode({"schema":VERSION,"nonce":nonce,"timestamp":int(time.time()),
                "project":project,"files":files,"canvas":bool(canvas),"checks":checks or []})
    if len(raw)>MAX_BODY:raise BrowserUnavailable("BROWSER_REQUEST_TOO_LARGE")
    req=urllib.request.Request(URL,data=raw,headers={"Content-Type":"application/json",
        "X-Swrlz-Signature":mac(key,"request",raw)},method="POST")
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=65) as response:
            body=response.read(80_001)
            if len(body)>80_000:raise BrowserUnavailable("BROWSER_RESPONSE_TOO_LARGE")
        envelope=json.loads(body)
        result=verify_envelope(key,envelope,project=project,hashes=file_hashes(files),nonce=nonce,max_age=180)
    except (OSError,ValueError,TypeError) as exc:
        raise BrowserUnavailable("BROWSER_WORKER_UNAVAILABLE: "+type(exc).__name__) from exc
    if result.get("infrastructureError") or result.get("sandbox") is not True:
        raise BrowserUnavailable(str(result.get("infrastructureError") or "BROWSER_SANDBOX_UNVERIFIED"))
    return envelope
