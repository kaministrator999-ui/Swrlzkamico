"""Read-only post-rollback HF health isolation, no secrets or source mutation."""
from __future__ import annotations
import json,os,urllib.request,urllib.error,time
from huggingface_hub import HfApi
SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"

def emit(k,**fields):print("SWRLZ_HEALTH_ISOLATION "+json.dumps({"part":k,**fields},sort_keys=True),flush=True)

def main():
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    try:
        info=api.repo_info(SPACE,repo_type="space")
        emit("revision",sha=info.sha)
    except Exception as exc:emit("revision",errorType=type(exc).__name__)
    try:
        run=api.get_space_runtime(SPACE)
        emit("runtime",stage=str(run.stage),hardwareType=str(getattr(run,"hardware",None))[:50])
    except Exception as exc:emit("runtime",errorType=type(exc).__name__)
    for path in ("/api/account/status","/api/storage/valkey-native-gateway-check","/api/storage/valkey-preflight"):
        try:
            req=urllib.request.Request(BASE+path,headers={"Accept":"application/json","User-Agent":"SWRLZ-ReadOnly-Health-Isolation/1"})
            with urllib.request.urlopen(req,timeout=14) as res:
                data=res.read(3000)
                parsed=json.loads(data)
                flags={}
                if "valkey-native-gateway" in path:
                    flags={"selected":parsed.get("backendSelected"),
                           "readWrite":parsed.get("nativeSETGET"),
                           "lua":parsed.get("nativeLua")}
                elif "valkey-preflight" in path:
                    details=parsed.get("valkey") or {}
                    flags={"connected":details.get("connected"),"lua":details.get("lua")}
                emit(path,http=res.status,bodyKind=type(parsed).__name__,**flags)
        except Exception as exc:
            emit(path,errorType=type(exc).__name__,
                 httpStatus=getattr(exc,"code",None) if isinstance(exc,urllib.error.HTTPError) else None)

if __name__=="__main__":main()
