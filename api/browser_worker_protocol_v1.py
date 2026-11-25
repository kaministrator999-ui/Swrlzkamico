"""Narrow authenticated §C browser-worker protocol, with no project authority."""
from __future__ import annotations
import hashlib,hmac,json,re,time
VERSION="swrlz-browser-worker-v1"
MAX_BODY=2_500_000
MAX_FILES=48
MAX_BYTES=1_000_000
PATH=re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*(?:/[A-Za-z0-9][A-Za-z0-9_.-]*){0,7}\Z")
SLUG=re.compile(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?\Z")
NONCE=re.compile(r"[0-9a-f]{32}\Z")
EXT={".html",".htm",".js",".mjs",".css",".json",".svg"}
def encode(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(raw):
    return hashlib.sha256(raw).hexdigest()
def mac(key,kind,raw):
    return hmac.new(key.encode(),kind.encode()+b"\0"+raw,hashlib.sha256).hexdigest()
def derive_key(token):
    if not token:raise ValueError("BROWSER_KEY_UNAVAILABLE")
    return hmac.new(token.encode(),b"swrlz-browser-worker-auth-v1",hashlib.sha256).hexdigest()
def validate_request(obj,now=None):
    if not isinstance(obj,dict) or set(obj)!={"schema","nonce","timestamp","project","files","canvas","checks"}:
        raise ValueError("INVALID_BROWSER_REQUEST")
    if obj["schema"]!=VERSION or not isinstance(obj["nonce"],str) or not NONCE.fullmatch(obj["nonce"]):
        raise ValueError("INVALID_BROWSER_IDENTITY")
    if type(obj["timestamp"]) is not int or abs((time.time() if now is None else now)-obj["timestamp"])>120:
        raise ValueError("STALE_BROWSER_REQUEST")
    if not isinstance(obj["project"],str) or not SLUG.fullmatch(obj["project"]):
        raise ValueError("INVALID_BROWSER_PROJECT")
    files=obj["files"]
    if not isinstance(files,dict) or not 1<=len(files)<=MAX_FILES or "index.html" not in files:
        raise ValueError("INVALID_BROWSER_FILES")
    total=0
    for path,body in files.items():
        if (not isinstance(path,str) or len(path)>180 or not PATH.fullmatch(path)
                or any(p.startswith(".") or p=="node_modules" for p in path.split("/"))
                or "."+path.rsplit(".",1)[-1].lower() not in EXT or not isinstance(body,str) or "\0" in body):
            raise ValueError("INVALID_BROWSER_ASSET")
        total+=len(body.encode())
    if total>MAX_BYTES or type(obj["canvas"]) is not bool:
        raise ValueError("BROWSER_LIMIT_EXCEEDED")
    checks=obj["checks"]
    if not isinstance(checks,list) or len(checks)>8:raise ValueError("BROWSER_CHECK_LIMIT")
    for c in checks:
        if not isinstance(c,dict) or c.get("op") not in ("click","check","uncheck","visible","text","checked","unchecked"):
            raise ValueError("BROWSER_CHECK_OPERATION")
        required={"op","selector"}|({"text"} if c["op"]=="text" else set())
        if set(c)!=required or not isinstance(c["selector"],str) or not re.fullmatch(r"#[A-Za-z][A-Za-z0-9_-]{0,80}",c["selector"]):
            raise ValueError("BROWSER_CHECK_SELECTOR")
        if c["op"]=="text" and (not isinstance(c["text"],str) or len(c["text"])>200):
            raise ValueError("BROWSER_CHECK_TEXT")
    return obj
def file_hashes(files):
    return {path:digest(body.encode()) for path,body in files.items()}
def verify_envelope(key,envelope,*,project,hashes,nonce=None,max_age=7200,now=None):
    if not isinstance(envelope,dict) or set(envelope)!={"receipt","signature"}:
        raise ValueError("BROWSER_RECEIPT_SHAPE")
    receipt=envelope["receipt"]
    if not isinstance(receipt,dict) or not isinstance(envelope["signature"],str) or not hmac.compare_digest(
            mac(key,"receipt",encode(receipt)),envelope["signature"]):
        raise ValueError("BROWSER_RECEIPT_SIGNATURE")
    if (receipt.get("schema")!=VERSION or receipt.get("project")!=project or receipt.get("hashes")!=hashes
            or type(receipt.get("timestamp")) is not int
            or abs((time.time() if now is None else now)-receipt["timestamp"])>max_age
            or (nonce is not None and receipt.get("nonce")!=nonce)):
        raise ValueError("BROWSER_RECEIPT_IDENTITY")
    return receipt
