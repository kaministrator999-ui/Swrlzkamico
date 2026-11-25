"""§C -> §X fixed diagnostic protocol; not a project execution backend."""
import hashlib,hmac,json,os,re,secrets,time
import requests

SCHEMA="swrlz-x-diagnostic-v1"
URL="https://kamiloki-swrlz-execution.hf.space"
STATION="https://kamiloki-swyrlz.hf.space/api/swrlz-x/v1/diagnostics"
KEY_NAME="SWRLZ_X_DIAGNOSTIC_KEY"

class DiagnosticUnavailable(RuntimeError): pass

def wire(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def mac(key,kind,raw):
    return hmac.new(key.encode(),kind.encode()+b"\0"+raw,hashlib.sha256).hexdigest()

def derive_key(token):
    if not token: raise DiagnosticUnavailable("HF_TOKEN_MISSING")
    return hmac.new(token.encode(),b"swrlz-x-diagnostic-auth-v1",hashlib.sha256).hexdigest()

def request_data(key,kind="request"):
    if not re.fullmatch(r"[a-f0-9]{64}",key or ""): raise DiagnosticUnavailable("X_KEY_NOT_CONFIGURED")
    obj={"schema":SCHEMA,"nonce":secrets.token_hex(16),"timestamp":int(time.time())}
    raw=wire(obj)
    return obj,raw.decode(),mac(key,kind,raw)

def verify(key,env,nonce):
    if not isinstance(env,dict) or set(env)!={"receipt","signature"}: raise DiagnosticUnavailable("X_RECEIPT_SHAPE")
    rec=env["receipt"]
    if not isinstance(rec,dict) or not isinstance(env["signature"],str) or not hmac.compare_digest(mac(key,"receipt",wire(rec)),env["signature"]):
        raise DiagnosticUnavailable("X_RECEIPT_SIGNATURE")
    if rec.get("schema")!=SCHEMA or rec.get("nonce")!=nonce or type(rec.get("timestamp")) is not int or abs(time.time()-rec["timestamp"])>180:
        raise DiagnosticUnavailable("X_RECEIPT_IDENTITY")
    d=rec.get("diagnostics")
    if not isinstance(d,dict) or rec.get("arbitrary_execution") is not False or rec.get("isolation_verified") is not False:
        raise DiagnosticUnavailable("X_RECEIPT_SCOPE")
    if rec.get("passed") is not True or not all(d.get(k)=="PASS" for k in ("chromium","javascript","interaction","screenshot")) or not isinstance(d.get("webgl"),dict) or d["webgl"].get("status")!="PASS" or d.get("page_errors")!=[] or not re.fullmatch(r"[a-f0-9]{64}",d.get("screenshot_sha256") or "") or not re.fullmatch(r"[a-f0-9]{64}",rec.get("fixture_sha256") or ""):
        raise DiagnosticUnavailable("X_BROWSER_DIAGNOSTIC_FAILED")
    return rec

def call_gradio(raw,signature):
    # Fixed origin, no caller-supplied URL, no redirects and no credentials in URLs.
    with requests.Session() as s:
        s.trust_env=False
        endpoint=URL+"/gradio_api/call/swrlz_diagnostics_v1"
        with s.post(endpoint,json={"data":[raw,signature]},timeout=(10,20),allow_redirects=False,stream=True) as r:
            if r.status_code!=200: raise DiagnosticUnavailable("X_HTTP_"+str(r.status_code))
            body=r.raw.read(8193)
            if len(body)>8192: raise DiagnosticUnavailable("X_EVENT_TOO_LARGE")
            event=json.loads(body).get("event_id","")
        if not re.fullmatch(r"[a-f0-9]{32}",event): raise DiagnosticUnavailable("X_EVENT_ID")
        deadline=time.monotonic()+65
        with s.get(endpoint+"/"+event,timeout=(10,25),stream=True,allow_redirects=False) as r:
            if r.status_code!=200: raise DiagnosticUnavailable("X_STREAM_HTTP_"+str(r.status_code))
            kind=""; size=0
            for line in r.iter_lines(chunk_size=1024):
                size+=len(line)+1
                if size>65536 or time.monotonic()>deadline: raise DiagnosticUnavailable("X_STREAM_LIMIT")
                if line.startswith(b"event:"):
                    kind=line[6:].strip().decode()
                if line.startswith(b"data:"):
                    if kind=="error": raise DiagnosticUnavailable("X_REMOTE_REJECTED")
                    if kind=="complete":
                        result=json.loads(line[5:].strip())
                        if not isinstance(result,list) or len(result)!=1: raise DiagnosticUnavailable("X_RESULT_SHAPE")
                        return result[0]
        raise DiagnosticUnavailable("X_STREAM_INCOMPLETE")

def diagnose(key=None):
    key=key or os.environ.get(KEY_NAME,"")
    obj,raw,sig=request_data(key)
    return verify(key,call_gradio(raw,sig),obj["nonce"])

def station_diagnose(key):
    obj,raw,sig=request_data(key,"station-request")
    with requests.post(STATION,headers={"X-Swrlz-X-Request":raw,"X-Swrlz-X-Signature":sig},timeout=(10,90),allow_redirects=False,stream=True) as r:
        if r.status_code!=200: raise DiagnosticUnavailable("STATION_HTTP_"+str(r.status_code))
        body=r.raw.read(65537)
    if len(body)>65536: raise DiagnosticUnavailable("STATION_RESPONSE_LIMIT")
    result=json.loads(body)
    if result.get("schema")!=SCHEMA or result.get("nonce")!=obj["nonce"] or not isinstance(result.get("receipt"),dict) or result["receipt"].get("passed") is not True or result.get("backendActivated") is not False or not isinstance(result.get("signature"),str):
        raise DiagnosticUnavailable("STATION_RECEIPT_INVALID")
    signed={k:v for k,v in result.items() if k!="signature"}
    if not hmac.compare_digest(mac(key,"station-receipt",wire(signed)),result["signature"]):
        raise DiagnosticUnavailable("STATION_SIGNATURE")
    return result
