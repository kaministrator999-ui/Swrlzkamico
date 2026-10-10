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
import time
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
import github_connection as gh

SCHEMA="swrlz-google-chat-v1"
LOGIN_SCHEMA="swrlz-google-login-v1"
MAX_BYTES=2200000
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

def load_chat(owner):
    c=_config()
    raw=gh._redis(c,"GET",_chat_key(owner))
    if raw is None:return None
    try:envelope=json.loads(raw)
    except (TypeError,ValueError) as exc:raise HTTPException(503,"Stored chat history envelope invalid") from exc
    if not isinstance(envelope,dict) or not isinstance(envelope.get("revision"),int):
        raise HTTPException(503,"Stored chat history revision invalid")
    data=_decrypt(c,envelope.get("encrypted") or "")
    if not isinstance(data,dict) or data.get("schema")!=SCHEMA or data.get("owner")!=owner:
        raise HTTPException(503,"Stored chat history owner invalid")
    if data.get("revision")!=envelope["revision"]:
        raise HTTPException(503,"Stored chat history revision mismatch")
    if not isinstance(data.get("threads"),list) or not isinstance(data.get("currentId"),str):
        raise HTTPException(503,"Stored chat history shape invalid")
    return {"revision":data["revision"],"currentId":data["currentId"],
            "threads":data["threads"],"activeGeneration":None,"ownerGoogleId":owner}

def save_chat(owner,state,expected_revision):
    """Only a revision-matched full account snapshot may replace the previous."""
    c=_config()
    key=_chat_key(owner)
    if (not isinstance(expected_revision,int) or expected_revision<0
        or not isinstance(state,dict) or int(state.get("revision",-1))!=expected_revision+1
        or str(state.get("ownerGoogleId") or "")!=owner):
        raise HTTPException(409,"Chat history revision changed; synchronize before retrying")
    record={"schema":SCHEMA,"owner":owner,"revision":state["revision"],
            "currentId":state["currentId"],"threads":state["threads"]}
    envelope={"revision":state["revision"],"encrypted":_encrypt(c,record)}
    response=gh._redis(c,"EVAL",_CAS_LUA,"1",key,str(expected_revision),
                      json.dumps(envelope,separators=(",",":")))
    if response in (1,"1"):return True
    if response in (0,"0"):return False
    raise HTTPException(503,"Chat storage did not confirm its atomic commit")
