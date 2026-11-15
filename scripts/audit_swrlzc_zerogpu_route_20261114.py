#!/usr/bin/env python3
"""Read-only ZeroGPU route/usage inspection for the actual §C Space.
Only emit function names, durations, and token-permitted quota aggregates.
"""
import ast,os,json,re,sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
SPACE="kamiloki/Swyrlz"
FILES=("app.py","original_workstation.py","qwen_coder_engine.py","model_router.py")
def emit(**d):print("SWRLZ_ZEROGPU_ROUTE "+json.dumps(d,sort_keys=True),flush=True)
def decorative(node):
 for dec in getattr(node,"decorator_list",[]):
  root=dec.func if isinstance(dec,ast.Call) else dec
  if isinstance(root,ast.Attribute) and root.attr=="GPU" and isinstance(root.value,ast.Name) and root.value.id=="spaces":
   args={}
   if isinstance(dec,ast.Call):
    for kw in dec.keywords:
     if kw.arg in ("duration","size"):
      args[kw.arg]=kw.value.value if isinstance(kw.value,ast.Constant) else "dynamic"
   return args
 return None
def main():
 token=os.getenv("HF_TOKEN");api=HfApi(token=token)
 repo=api.repo_info(SPACE,repo_type="space")
 sources={}
 for path in FILES:
  try:sources[path]=Path(hf_hub_download(SPACE,path,repo_type="space",revision=repo.sha,token=token)).read_text("utf8")
  except Exception as e:emit(file=path,errorType=type(e).__name__)
 active=[]
 for path,source in sources.items():
  try:
   tree=ast.parse(source)
   hit=[]
   for node in ast.walk(tree):
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
     settings=decorative(node)
     if settings is not None:
      usages=len(re.findall(r"\b"+re.escape(node.name)+r"\s*\(",sources.get("app.py","")))
      hit.append({"function":node.name,"line":node.lineno,"settings":settings,
                 "appCallSiteMatches":usages})
   emit(file=path,gpuDecoratedFunctions=hit,
        sourceImportedFromApp=bool(re.search(r"\b"+re.escape(path[:-3])+r"\b",sources.get("app.py",""))))
   active+=hit
  except SyntaxError:emit(file=path,parseError=True)
 try:
  import huggingface_hub
  emit(sdkVersion=huggingface_hub.__version__,quotaMethod=hasattr(api,"get_zero_gpu_quota"))
  if hasattr(api,"get_zero_gpu_quota"):
   q=api.get_zero_gpu_quota()
   emit(quotaBaseSeconds=getattr(q,"base",None),
        quotaRemainingSeconds=getattr(q,"remaining",None),
        quotaResetAt=str(getattr(q,"resets_at",None)),
        quotaAvailable=True)
 except Exception as e:
  emit(quotaAvailable=False,errorType=type(e).__name__,
       permissionOrBillingScopeRequired=True)
 emit(gpuWrappersFound=len(active),actualUserRequestsNotProbed=True,
      underlyingModelWeightsNotRead=True)
if __name__=="__main__":main()
