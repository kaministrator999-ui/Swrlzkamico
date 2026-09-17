"""Redis-backed canonical Chat turn state.

A generation job and its user/assistant records form one durable lifecycle invariant:
if the job exists, the referenced assistant placeholder must exist until terminal commit.
"""
from __future__ import annotations
import json,time
from dataclasses import asdict,replace
from typing import Any
from api.durable_chat_contract import GenerationJobRecord,MessageRecord,ThreadRecord
from api.durable_redis_store import DurableStoreUnavailable
from api.durable_redis_atomic import AtomicRedisRestChatStore

_BEGIN_CANONICAL_TURN_LUA=r'''
if redis.call('EXISTS',KEYS[1])==1 then return 0 end
if redis.call('EXISTS',KEYS[2])==1 or redis.call('EXISTS',KEYS[3])==1 then return -1 end
redis.call('SET',KEYS[2],ARGV[2]); redis.call('ZADD',KEYS[4],ARGV[4],cjson.decode(ARGV[2]).message_id)
redis.call('SET',KEYS[3],ARGV[3]); redis.call('ZADD',KEYS[4],ARGV[5],cjson.decode(ARGV[3]).message_id)
redis.call('SET',KEYS[1],ARGV[1]); redis.call('SADD',KEYS[5],ARGV[6]); redis.call('SET',KEYS[6],ARGV[7]); redis.call('ZADD',KEYS[7],ARGV[8],ARGV[9]); return 1
'''
_FINISH_CANONICAL_TURN_LUA=r'''
if redis.call('EXISTS',KEYS[1])~=1 then return -1 end
if redis.call('EXISTS',KEYS[2])~=1 then return -2 end
redis.call('SET',KEYS[2],ARGV[1]); redis.call('SET',KEYS[1],ARGV[2]); redis.call('SREM',KEYS[3],ARGV[3]); return 1
'''
_REPAIR_ASSISTANT_LUA=r'''
if redis.call('EXISTS',KEYS[1])~=1 then return -1 end
if redis.call('EXISTS',KEYS[2])==1 then return 0 end
redis.call('SET',KEYS[2],ARGV[1]); redis.call('ZADD',KEYS[3],ARGV[2],ARGV[3]); return 1
'''
_CAMERA_CONTRACT="swrlz-canonical-redis-lifecycle-v2"
def _camera(stage:str,**fields:Any)->None:
 r={"contract":_CAMERA_CONTRACT,"stage":stage,"atUnixMs":int(time.time()*1000)}
 for k,v in fields.items():
  if v is None or isinstance(v,(str,int,float,bool)):r[str(k)[:64]]=v
 print("SWRLZ_CHAT_REDIS "+json.dumps(r,ensure_ascii=False,separators=(",",":")),flush=True)
def configured()->bool:return AtomicRedisRestChatStore.configured()
def store()->AtomicRedisRestChatStore:return AtomicRedisRestChatStore.from_env()
def _message(redis:AtomicRedisRestChatStore,*,user_id:str,message_id:str)->MessageRecord|None:
 return redis._get_json(redis._key("message",user_id,message_id),MessageRecord)
def _assert_invariant(redis:AtomicRedisRestChatStore,*,job:GenerationJobRecord,prompt:str)->None:
 u=_message(redis,user_id=job.user_id,message_id=job.user_message_id); a=_message(redis,user_id=job.user_id,message_id=job.assistant_message_id)
 if u is None or u.role!="USER" or u.committed_text!=prompt:_camera("begin-invariant-failed",requestId=job.request_id,missing="user");raise DurableStoreUnavailable("canonical Redis user record missing after begin")
 if a is None or a.role!="ASSISTANT" or a.request_id!=job.request_id:_camera("begin-invariant-failed",requestId=job.request_id,missing="assistant");raise DurableStoreUnavailable("canonical Redis assistant record missing after begin")
 _camera("begin-invariant-ok",requestId=job.request_id,assistantState=a.state)
def begin_canonical_turn(*,user_id:str,thread_id:str,request_id:str,user_message_id:str,assistant_message_id:str,prompt:str,title:str,user_created_at_ms:int,assistant_created_at_ms:int,turn_contract:str)->None:
 redis=store(); existing=redis.get_generation(user_id=user_id,request_id=request_id)
 if existing is not None:_verify_existing(redis,existing,thread_id,user_message_id,assistant_message_id,prompt);_assert_invariant(redis,job=existing,prompt=prompt);return
 now=time.time();ua=user_created_at_ms/1000.0;aa=assistant_created_at_ms/1000.0;old=redis.get_thread(user_id=user_id,thread_id=thread_id);thread=old or ThreadRecord(thread_id=thread_id,user_id=user_id,title=title or "New conversation",created_at=ua,updated_at=now)
 if old is not None:thread=replace(old,title=(title if old.title=="New conversation" and title else old.title),updated_at=now)
 p={"authority":"server","turnContract":turn_contract,"commitPhase":"PRE_GENERATION"};u=MessageRecord(message_id=user_message_id,thread_id=thread_id,user_id=user_id,role="USER",received_text=prompt,committed_text=prompt,provenance=p,interpretation={},state="COMPLETE",request_id=request_id,created_at=ua,updated_at=now);a=MessageRecord(message_id=assistant_message_id,thread_id=thread_id,user_id=user_id,role="ASSISTANT",received_text=None,committed_text="",provenance=p,interpretation={},state="STREAMING",request_id=request_id,created_at=aa,updated_at=now);job=GenerationJobRecord(request_id=request_id,user_id=user_id,thread_id=thread_id,user_message_id=user_message_id,assistant_message_id=assistant_message_id,state="QUEUED",created_at=now,updated_at=now)
 keys=[redis._key("job",user_id,request_id),redis._key("message",user_id,user_message_id),redis._key("message",user_id,assistant_message_id),redis._key("messages",user_id,thread_id),redis._key("activeJobs",user_id),redis._key("thread",user_id,thread_id),redis._key("threads",user_id)];args=[json.dumps(asdict(job),separators=(",",":")),json.dumps(asdict(u),separators=(",",":")),json.dumps(asdict(a),separators=(",",":")),str(ua),str(aa),request_id,json.dumps(asdict(thread),separators=(",",":")),str(thread.updated_at),thread_id]
 result=int(redis._command("EVAL",_BEGIN_CANONICAL_TURN_LUA,len(keys),*keys,*args) or 0);_camera("begin-eval",requestId=request_id,result=result)
 if result==-1:raise ValueError("CHAT_TURN_MESSAGE_ID_CONFLICT")
 if result==0:
  winner=redis.get_generation(user_id=user_id,request_id=request_id)
  if winner is None:raise DurableStoreUnavailable("canonical Redis claim lost without durable winner")
  _verify_existing(redis,winner,thread_id,user_message_id,assistant_message_id,prompt);job=winner
 _assert_invariant(redis,job=job,prompt=prompt)
def _verify_existing(redis:AtomicRedisRestChatStore,job:GenerationJobRecord,thread_id:str,user_message_id:str,assistant_message_id:str,prompt:str)->None:
 if job.thread_id!=thread_id or job.user_message_id!=user_message_id or job.assistant_message_id!=assistant_message_id:raise ValueError("CHAT_TURN_REQUEST_ID_MESSAGE_CONFLICT")
 m=_message(redis,user_id=job.user_id,message_id=user_message_id)
 if m is None or m.committed_text!=prompt or m.role!="USER":raise ValueError("CHAT_TURN_MESSAGE_ID_CONTENT_CONFLICT")
def canonical_history(*,user_id:str,thread_id:str,request_id:str,limit:int=32)->list[dict[str,str]]:
 redis=store();out=[]
 for m in redis.list_messages(user_id=user_id,thread_id=thread_id):
  if m.request_id==request_id or m.role not in {"USER","ASSISTANT"}:continue
  text=m.committed_text.strip()
  if not text or m.state in {"STREAMING","FAILED","CANCELLED"}:continue
  out.append({"role":m.role,"text":text[:2000]})
 return out[-max(1,min(int(limit),32)):]
def _repair_assistant(redis:AtomicRedisRestChatStore,*,job:GenerationJobRecord,assistant_message_id:str,turn_contract:str)->MessageRecord:
 now=time.time();a=MessageRecord(message_id=assistant_message_id,thread_id=job.thread_id,user_id=job.user_id,role="ASSISTANT",received_text=None,committed_text="",provenance={"authority":"server","turnContract":turn_contract,"commitPhase":"PRE_GENERATION_REPAIRED"},interpretation={},state="STREAMING",request_id=job.request_id,created_at=now,updated_at=now);keys=[redis._key("job",job.user_id,job.request_id),redis._key("message",job.user_id,assistant_message_id),redis._key("messages",job.user_id,job.thread_id)];args=[json.dumps(asdict(a),separators=(",",":")),str(now),assistant_message_id];result=int(redis._command("EVAL",_REPAIR_ASSISTANT_LUA,len(keys),*keys,*args) or 0);_camera("assistant-repair",requestId=job.request_id,result=result)
 if result==-1:raise DurableStoreUnavailable("canonical Redis generation disappeared before assistant repair")
 repaired=_message(redis,user_id=job.user_id,message_id=assistant_message_id)
 if repaired is None:raise DurableStoreUnavailable("canonical Redis assistant repair did not persist")
 return repaired
def finish_canonical_turn(*,user_id:str,request_id:str,assistant_message_id:str,text:str,terminal_type:str,reason:str,turn_contract:str)->None:
 redis=store();job=redis.get_generation(user_id=user_id,request_id=request_id)
 if job is None or job.assistant_message_id!=assistant_message_id:raise ValueError("CHAT_TURN_GENERATION_NOT_FOUND")
 a=_message(redis,user_id=user_id,message_id=assistant_message_id)
 if a is None:_camera("assistant-missing-at-finish",requestId=request_id);a=_repair_assistant(redis,job=job,assistant_message_id=assistant_message_id,turn_contract=turn_contract)
 terminal=str(terminal_type or "FAILED").upper();ms={"COMPLETED":"COMPLETE","CANCELLED":"CANCELLED","FAILED":"FAILED"}.get(terminal,"FAILED");js={"COMPLETED":"COMPLETE","CANCELLED":"CANCELLED","FAILED":"FAILED"}.get(terminal,"FAILED");now=time.time();a=replace(a,committed_text=str(text or "")[:200000],state=ms,updated_at=now,provenance={**a.provenance,"authority":"server","turnContract":turn_contract,"commitPhase":"TERMINAL","terminalType":terminal,"terminalReason":str(reason or "")[:2000]});job=replace(job,state=js,updated_at=now,completed_at=now);keys=[redis._key("job",user_id,request_id),redis._key("message",user_id,assistant_message_id),redis._key("activeJobs",user_id)];args=[json.dumps(asdict(a),separators=(",",":")),json.dumps(asdict(job),separators=(",",":")),request_id];result=int(redis._command("EVAL",_FINISH_CANONICAL_TURN_LUA,len(keys),*keys,*args) or 0);_camera("finish-eval",requestId=request_id,result=result,terminal=terminal)
 if result!=1:raise DurableStoreUnavailable("canonical Redis terminal commit failed")
