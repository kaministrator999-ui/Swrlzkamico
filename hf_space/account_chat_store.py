"""Encrypted Redis storage for verified Google sessions and user chat histories.

The server verifies Google ID tokens before creating an account session. A
random, HttpOnly cookie identifies an encrypted Redis login record for seven
days, surviving a Space process replacement without a bearer token in JS.
Chat snapshots use a single account-owned CAS revision and no automatic TTL:
the user may explicitly delete threads. The previous chat mutation contract
already carries optimistic revisions.
"""
from __future__ import annotations
import hashlib
import json
import re
import secrets
import time
import zlib
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
import github_connection as gh

SCHEMA="swrlz-google-chat-v1"
LOGIN_SCHEMA="swrlz-google-login-v1"
MAX_BYTES=2200000
# The old limit still applies to login payloads; native Chat grows independently.
# Hard bounds guard decompression, unusually large uploads and Redis write budgets.
CHAT_MAX_RAW=32_000_000
CHAT_MAX_CIPHER=40_000_000
CHAT_CHUNK_BYTES=640_000
CHAT_MAX_CHUNKS=64
CHAT_INLINE="fernet-zlib-inline-v2"
CHAT_CHUNKED="fernet-zlib-chunked-v2"
CHAT_NONCE=re.compile(r"^[0-9a-f]{32}$")
LOGIN_TTL=7*86400
SID=re.compile(r"^[0-9a-f]{32}$")
OWNER=re.compile(r"^google:[A-Za-z0-9_-]{5,200}$")
_CAS_LUA=(
    "local raw=redis.call('GET',KEYS[1]);"
    "local expected=tonumber(ARGV[1]);"
    "if not raw then if expected~=0 then return 0 end;"
    "else local ok,prior=pcall(cjson.decode,raw);"
    "if not ok or type(prior)~='table' or tonumber(prior['revision'])~=expected then return 0 end end;"
    "redis.call('SET',KEYS[1],ARGV[2]); return 1"
)

def _config():
    c=gh._settings()
    if not c.get("fernet") or not c.get("redis_token") or not c.get("redis") or not c["redis"].startswith("https://"):
        raise HTTPException(503,"Durable Google account and conversation storage is not configured")
    try: Fernet(c["fernet"].encode("ascii"))
    except Exception as exc: raise HTTPException(503,"Durable account encryption key invalid") from exc
    return c

def configured():
    try:_config();return True
    except HTTPException:return False

def _sid_key(sid):
    if not SID.fullmatch(str(sid or "")):return ""
    return "swrlz:google:login:v1:"+hashlib.sha256(sid.encode("ascii")).hexdigest()

def _chat_key(owner):
    if not OWNER.fullmatch(str(owner or "")):
        raise HTTPException(401,"Verified Google identity required")
    return "swrlz:google:chat:v1:"+hashlib.sha256(owner.encode("utf-8")).hexdigest()

def _encrypt(c,value):
    raw=json.dumps(value,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode("utf-8")
    if len(raw)>MAX_BYTES:raise HTTPException(413,"Account conversation history exceeds the safe snapshot size; export or remove large artifacts first")
    return Fernet(c["fernet"].encode("ascii")).encrypt(raw).decode("ascii")

def _decrypt(c,cipher):
    try:
        return json.loads(Fernet(c["fernet"].encode("ascii")).decrypt(cipher.encode("ascii")))
    except (InvalidToken,UnicodeError,ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        raise HTTPException(503,"Stored encrypted account data cannot be read; no changes were made") from exc

def save_login(sid,user):
    key=_sid_key(sid)
    if not key or not isinstance(user,dict) or not OWNER.fullmatch(str(user.get("id") or "")):
        raise HTTPException(400,"Invalid verified account session")
    c=_config()
    fields={k:str(user.get(k) or "")[:512] for k in ("id","email","displayName","picture")}
    body={"schema":LOGIN_SCHEMA,"owner":fields["id"],"user":fields,"createdAt":int(time.time())}
    if gh._redis(c,"SET",key,_encrypt(c,body),"EX",LOGIN_TTL)!="OK":
        raise HTTPException(503,"Verified Google session could not be persisted")

def load_login(sid):
    key=_sid_key(sid)
    if not key:return None
    c=_config()
    encrypted=gh._redis(c,"GET",key)
    if not encrypted:return None
    body=_decrypt(c,encrypted)
    user=body.get("user") if isinstance(body,dict) else None
    if (body.get("schema")!=LOGIN_SCHEMA or not isinstance(user,dict)
        or body.get("owner")!=user.get("id") or not OWNER.fullmatch(str(body.get("owner") or ""))):
        raise HTTPException(503,"Stored Google session failed owner validation")
    return user

def revoke_login(sid):
    key=_sid_key(sid)
    if key:gh._redis(_config(),"DEL",key)

def _chat_chunk_key(owner,nonce,index):
    # Refuse user-controlled Redis paths. Owner always passes _chat_key's
    # verified-identity validator; nonce is a server-generated random ID.
    parent=_chat_key(owner)
    if not CHAT_NONCE.fullmatch(str(nonce or "")) or not isinstance(index,int) or not 0<=index<CHAT_MAX_CHUNKS:
        raise HTTPException(503,"Stored account chat chunk reference invalid")
    return parent+":v2chunk:"+nonce+":"+str(index)


def _decode_native_chat(c,envelope,owner):
    """Support original Fernet JSON and new compressed snapshots, fail closed."""
    kind=envelope.get("format")
    if kind is None:
        # Legacy v1 records are read without any rewrite/migration side effect.
        return _decrypt(c,envelope.get("encrypted") or "")
    if kind not in (CHAT_INLINE,CHAT_CHUNKED):
        raise HTTPException(503,"Stored account chat format not supported; nothing modified")
    if kind==CHAT_INLINE:
        cipher=envelope.get("encrypted")
        if not isinstance(cipher,str) or not 0<len(cipher)<=CHAT_CHUNK_BYTES:
            raise HTTPException(503,"Stored account chat inline payload invalid")
    else:
        nonce=envelope.get("nonce")
        count=envelope.get("parts")
        if not isinstance(count,int) or not 1<=count<=CHAT_MAX_CHUNKS:
            raise HTTPException(503,"Stored account chat parts invalid")
        pieces=[]
        for i in range(count):
            part=gh._redis(c,"GET",_chat_chunk_key(owner,nonce,i))
            if not isinstance(part,str) or not 0<len(part)<=CHAT_CHUNK_BYTES:
                raise HTTPException(503,"Stored account chat part missing or invalid; no changes made")
            pieces.append(part)
        cipher="".join(pieces)
    if len(cipher)>CHAT_MAX_CIPHER or hashlib.sha256(cipher.encode("ascii",errors="replace")).hexdigest()!=envelope.get("cipherSha256"):
        raise HTTPException(503,"Stored account chat content integrity check failed; no changes made")
    try:
        compressed=Fernet(c["fernet"].encode("ascii")).decrypt(cipher.encode("ascii"))
        decoder=zlib.decompressobj()
        raw=decoder.decompress(compressed,CHAT_MAX_RAW+1)
        if (len(raw)>CHAT_MAX_RAW or not decoder.eof or decoder.unconsumed_tail
                or decoder.unused_data or len(raw)!=envelope.get("rawBytes")):
            raise ValueError("Bounded native Chat decompression failed")
        return json.loads(raw)
    except (InvalidToken,UnicodeError,ValueError,TypeError,KeyError,zlib.error,json.JSONDecodeError) as exc:
        raise HTTPException(503,"Stored compressed account chat cannot be read; no changes made") from exc


def _native_chat_parts(c,record):
    raw=json.dumps(record,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode("utf-8")
    if len(raw)>CHAT_MAX_RAW:
        raise HTTPException(413,"Native Chat account history reached its bounded capacity; existing data was not overwritten")
    cipher=Fernet(c["fernet"].encode("ascii")).encrypt(zlib.compress(raw,6)).decode("ascii")
    if len(cipher)>CHAT_MAX_CIPHER:
        raise HTTPException(413,"Compressed Chat history exceeds the bounded storage budget; previous data was preserved")
    common={"revision":record["revision"],"rawBytes":len(raw),
            "cipherSha256":hashlib.sha256(cipher.encode("ascii")).hexdigest()}
    if len(cipher)<=CHAT_CHUNK_BYTES:
        return {**common,"format":CHAT_INLINE,"encrypted":cipher},[]
    parts=[cipher[i:i+CHAT_CHUNK_BYTES] for i in range(0,len(cipher),CHAT_CHUNK_BYTES)]
    if len(parts)>CHAT_MAX_CHUNKS:
        raise HTTPException(413,"Native Chat history needs too many encrypted parts; previous data was preserved")
    nonce=secrets.token_hex(16)
    return {**common,"format":CHAT_CHUNKED,"nonce":nonce,"parts":len(parts)},parts


def load_chat(owner):
    c=_config()
    raw=gh._redis(c,"GET",_chat_key(owner))
    if raw is None:return None
    try:envelope=json.loads(raw)
    except (TypeError,ValueError) as exc:raise HTTPException(503,"Stored chat history envelope invalid") from exc
    if not isinstance(envelope,dict) or not isinstance(envelope.get("revision"),int):
        raise HTTPException(503,"Stored chat history revision invalid")
    data=_decode_native_chat(c,envelope,owner)
    if not isinstance(data,dict) or data.get("schema")!=SCHEMA or data.get("owner")!=owner:
        raise HTTPException(503,"Stored chat history owner invalid")
    if data.get("revision")!=envelope["revision"]:
        raise HTTPException(503,"Stored chat history revision mismatch")
    if not isinstance(data.get("threads"),list) or not isinstance(data.get("currentId"),str):
        raise HTTPException(503,"Stored chat history shape invalid")
    return {"revision":data["revision"],"currentId":data["currentId"],
            "threads":data["threads"],"activeGeneration":None,"ownerGoogleId":owner}


def save_chat(owner,state,expected_revision):
    """Publish new encrypted chunks only by atomic revision-matched manifest CAS.

    The old v1 key remains the canonical pointer. A failed CAS cannot expose
    partial chunks. Unknown transport outcomes preserve chunks rather than risk
    deleting data that might already be referenced by a committed manifest.
    """
    c=_config()
    key=_chat_key(owner)
    if (not isinstance(expected_revision,int) or expected_revision<0
        or not isinstance(state,dict) or int(state.get("revision",-1))!=expected_revision+1
        or str(state.get("ownerGoogleId") or "")!=owner):
        raise HTTPException(409,"Chat history revision changed; synchronize before retrying")
    record={"schema":SCHEMA,"owner":owner,"revision":state["revision"],
            "currentId":state["currentId"],"threads":state["threads"]}
    envelope,parts=_native_chat_parts(c,record)
    written=[]
    if parts:
        # The manifest is still untouched. An incomplete set is unreachable.
        for i,part in enumerate(parts):
            key_part=_chat_chunk_key(owner,envelope["nonce"],i)
            if gh._redis(c,"SET",key_part,part)!="OK":
                raise HTTPException(503,"Native Chat encrypted chunk was not confirmed stored; previous history remains")
            written.append(key_part)
    response=gh._redis(c,"EVAL",_CAS_LUA,"1",key,str(expected_revision),
                      json.dumps(envelope,separators=(",",":")))
    if response in (1,"1"):return True
    if response in (0,"0"):
        # Definitive CAS reject: this manifest was not published. Keep cleanup
        # best-effort only; inaccessible chunks never constitute saved history.
        for key_part in written:
            try:gh._redis(c,"DEL",key_part)
            except Exception:pass
        return False
    raise HTTPException(503,"Native Chat storage did not confirm atomic commit; do not retry blindly")
