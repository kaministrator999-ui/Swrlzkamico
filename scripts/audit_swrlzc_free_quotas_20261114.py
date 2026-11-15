#!/usr/bin/env python3
"""2026-11-14 §C quota audit: read-only aggregate metadata, never chat values.

No Redis writes, no HF Space commit, no user content, and no credential output.
"""
import ast,datetime,json,os,re,urllib.request,urllib.error
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download

REPO="kaministrator999-ui/Swrlzkamico"
SPACE="kamiloki/Swyrlz"
FILES=("account_chat_store.py","qwen_coder_engine.py","model_router.py",
       "station.py","github_connection.py","app.py","README.md","requirements.txt")
CONSTANTS={
 "CHAT_CHUNK_BYTES","CHAT_MAX_RAW","CHAT_MAX_CIPHER","CHAT_MAX_CHUNKS",
 "CONTEXT_TOKENS","INPUT_BUDGET_TOKENS","MIN_OUTPUT_TOKENS",
 "MAX_OUTPUT_TOKENS","MAX_AUTO_SEGMENTS","MAX_SEGMENTS",
 "MAX_PENDING_CODING_INSTRUCTIONS","MAX_CHAT_PAYLOAD_BYTES",
 "MAX_CHAT_HISTORY","REDIS_MAX_CONNECTIONS"
}
def say(kind,**fields):
 print("SWRLZ_FREE_QUOTA_AUDIT "+json.dumps({"kind":kind,**fields},sort_keys=True,ensure_ascii=True),flush=True)
def github_stats():
 token=os.environ.get("GITHUB_TOKEN")
 if not token:
  say("github",error="token_unavailable");return
 base="https://api.github.com/repos/"+REPO
 def get(path):
  req=urllib.request.Request(base+path,headers={
   "Accept":"application/vnd.github+json",
   "Authorization":"Bearer "+token,
   "X-GitHub-Api-Version":"2022-11-28",
   "User-Agent":"SWRLZ-read-only-free-tier-audit"})
  with urllib.request.urlopen(req,timeout=22) as res:return json.load(res)
 try:
  repo=get("")
  artifacts=get("/actions/artifacts?per_page=100&page=1")
  total=int(artifacts.get("total_count") or 0)
  items=list(artifacts.get("artifacts") or [])
  # At most eight pages, 8 calls. Enough to see a meaningful large
  # artifact tail; do not use huge pagination to audit usage.
  for page in range(2,min(20,(total+99)//100)+1):
   items+=get("/actions/artifacts?per_page=100&page="+str(page)).get("artifacts") or []
  alive=[x for x in items if not x.get("expired")]
  mbytes=sum(int(x.get("size_in_bytes") or 0) for x in alive)
  large=sorted(alive,key=lambda x:int(x.get("size_in_bytes") or 0),reverse=True)
  say("github_artifacts",
   public=not bool(repo.get("private")),totalCount=total,
   sampledCount=len(items),sampleComplete=(len(items)>=total),
   sampledLiveCount=len(alive),sampledLiveBytes=mbytes,
   biggestBytes=[int(x.get("size_in_bytes") or 0) for x in large[:10]],
   approxPercentOf500MB=round(100*mbytes/(500*1024*1024),1),
   artifactNamesWithheld=True)
 except Exception as ex:
  say("github_artifacts",errorType=type(ex).__name__,
      httpStatus=getattr(ex,"code",None))
def scan_code(path,content):
 # Print only metadata, never arbitrary source strings or URLs.
 out={
  "file":path,"bytes":len(content.encode("utf8")),
  "hfHubDownloads":len(re.findall(r"\bhf_hub_download\s*\(",content)),
  "hfSnapshots":len(re.findall(r"\bsnapshot_download\s*\(",content)),
  "inferenceClients":len(re.findall(r"\bInferenceClient\s*\(",content)),
  "localLlama":bool(re.search(r"(?i)\bLlama\s*\(|llama_cpp|GGUF",content)),
  "hfApiCalls":len(re.findall(r"(?i)\bHfApi\s*\(",content)),
  "externalRequests":len(re.findall(r"(?i)requests\.(?:post|get|put|delete)\s*\(|httpx\.(?:get|post)\s*\(",content)),
  "redisCalls":len(re.findall(r"\b_redis\s*\(|\bredis\.call\s*\(",content)),
  "redisWholeChatReads":len(re.findall(r"\bload_chat\s*\(",content)),
  "redisWholeChatWrites":len(re.findall(r"\bsave_chat\s*\(",content)),
  "expiresOrDeletes":bool(re.search(r"\b(?:expire|EXPIRE|TTL|delete_chat|DEL)\b",content)),
  "hasMaxmemoryCheck":bool(re.search(r"MEMORY\s+USAGE|INFO\s+memory|used_memory|maxmemory",content,re.I)),
  "hasRateLimitResponse":bool(re.search(r"\b429\b|retry.after|RateLimit",content,re.I)),
 }
 if path.endswith(".py"):
  try:
   t=ast.parse(content)
   constants={}
   for node in t.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
     k=node.targets[0].id
     if k not in CONSTANTS:continue
     if isinstance(node.value,ast.Constant) and type(node.value.value) is int:
      constants[k]=node.value.value
   out["safeNumericConstants"]=constants
  except SyntaxError:out["pythonSyntaxValid"]=False
 return out
def workflow_stats():
 root=Path(".github/workflows")
 workflows=list(root.glob("*.yml"))+list(root.glob("*.yaml"))
 broad_push=[]
 push_total=0
 for file in workflows:
  body=file.read_text(encoding="utf8",errors="replace")
  if not re.search(r"(?m)^\s+push\s*:",body):continue
  push_total+=1
  lines=body.splitlines()
  hits=[i for i,line in enumerate(lines) if re.search(r"^\s+push\s*:",line)]
  for i in hits:
   segment="\n".join(lines[i+1:i+12])
   if not re.search(r"(?m)^\s+paths(?:-ignore)?\s*:",segment):
    broad_push.append(file.name)
    break
 say("github_workflow_triggers",total=len(workflows),
     pushTriggered=push_total,estimatedUnscopedPush=len(broad_push),
     selectedUnscopedExamples=broad_push[:12],heuristic=True)

def hub_stats():
 token=os.environ.get("HF_TOKEN")
 if not token:
  say("hf",error="HF_TOKEN_unavailable");return
 api=HfApi(token=token)
 try:
  info=api.repo_info(SPACE,repo_type="space",files_metadata=True)
  members=info.siblings or []
  sizes=[int(getattr(m,"size",0) or 0) for m in members]
  say("hf_space_repo",
   revision=str(info.sha),
   fileCount=len(members),knownFileBytes=sum(sizes),
   unknownFileSizes=sum(n<=0 for n in sizes),metadataOnly=True)
 except Exception as e:
  say("hf_space_repo",errorType=type(e).__name__)
  info=api.repo_info(SPACE,repo_type="space")
 try:
  quota=api.get_zero_gpu_quota()
  say("hf_owner_zero_gpu_quota",baseSeconds=getattr(quota,"base",None),
      remainingSeconds=getattr(quota,"remaining",None),
      resetAt=str(getattr(quota,"resets_at",None)),
      overquotaUsedSeconds=getattr(quota,"overquota_used",None),
      quotaIsPerAccount=True)
 except Exception as ex:
  say("hf_owner_zero_gpu_quota",errorType=type(ex).__name__,
      accessUnavailable=True)
 try:
  runtime=api.get_space_runtime(SPACE)
  say("hf_runtime",stage=str(runtime.stage),
      hardware=str(getattr(runtime,"hardware",None)),
      requestedHardware=str(getattr(runtime,"requested_hardware",None)),
      sleepTime=getattr(runtime,"sleep_time",None))
 except Exception as e:say("hf_runtime",errorType=type(e).__name__)
 available={m.rfilename for m in (info.siblings or [])}
 if not available:available=set(api.list_repo_files(SPACE,repo_type="space",revision=info.sha))
 for path in FILES:
  if path not in available:continue
  try:
   source=Path(hf_hub_download(SPACE,path,repo_type="space",revision=info.sha,token=token)).read_text(encoding="utf8")
   say("source",**scan_code(path,source))
  except Exception as e:say("source",file=path,errorType=type(e).__name__)
 # Check actual GPU-worker entry points in public Python source.
 scripts=[m.rfilename for m in (info.siblings or [])
          if m.rfilename.endswith(".py") and
          (int(getattr(m,"size",0) or 0)<250000)]
 checked=0
 workerFiles=[]
 for path in scripts[:95]:
  try:
   source=Path(hf_hub_download(SPACE,path,repo_type="space",revision=info.sha,token=token)).read_text(encoding="utf8")
   checked+=1
   if re.search(r"@spaces\.GPU\b|spaces\.GPU\s*\(",source):
    workerFiles.append(path)
  except Exception:continue
 say("zero_gpu_source",pythonFilesAvailable=len(scripts),filesChecked=checked,
     gpuDecoratedFiles=workerFiles,scanComplete=(checked==len(scripts)),
     htmlOrJavascriptGPUCallsNotDetermined=True)
 say("exclusions",aivenCurrentBytes="not accessible from HF metadata",
     hfRuntimeDiskUsage="not accessible from Hub metadata",
     customProviderBilling="not accessible from Hub metadata",
     noAccountDataRead=True,noRedisKeysRead=True,credentialsWithheld=True)
if __name__=="__main__":
 github_stats()
 workflow_stats()
 hub_stats()
