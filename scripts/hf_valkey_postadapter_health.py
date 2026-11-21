"""Verify the exact dormant Valkey gateway release is live and legacy account route works."""
from __future__ import annotations
import json,os,time,urllib.request
from huggingface_hub import HfApi,hf_hub_download
from pathlib import Path

SPACE="kamiloki/Swyrlz"
REV="cca069b30df86f4214138a3bfcdbb9331579f16e"
BASE="https://kamiloki-swyrlz.hf.space"

def fetch(path):
    req=urllib.request.Request(BASE+path,headers={"Accept":"application/json","User-Agent":"SWRLZ-PostValkeyRelease/1"})
    with urllib.request.urlopen(req,timeout=12) as res:
        if res.status!=200: raise RuntimeError("HTTP_NOT_200")
        raw=res.read(3000)
        if len(raw)>=3000:raise RuntimeError("BODY_TOO_LARGE")
        return json.loads(raw)

def main():
    api=HfApi(token=os.environ["HF_TOKEN"])
    info=api.repo_info(SPACE,repo_type="space")
    if info.sha!=REV:
        print("SWRLZ_POSTADAPTER_ABORT:SpaceRevisionChanged")
        return 2
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=REV))
    if "github_connection.py" not in files:
        raise RuntimeError("REDIS_GATEWAY_MISSING")
    source=Path(hf_hub_download(SPACE,"github_connection.py",repo_type="space",revision=REV,token=api.token)).read_text("utf-8")
    if source.count("# SWRLZ_VALKEY_NATIVE_REDIS_BACKEND_V1")!=1:
        raise RuntimeError("DORMANT_ADAPTER_SOURCE_MISSING")
    if "SWRLZ_REDIS_BACKEND" in api.get_space_secrets(SPACE) or "SWRLZ_REDIS_BACKEND" in api.get_space_variables(SPACE):
        raise RuntimeError("BACKEND_SWITCH_UNEXPECTED")
    end=time.monotonic()+400
    last="Starting"
    while time.monotonic()<end:
        try:
            stage=api.get_space_runtime(SPACE).stage
            if stage!="RUNNING":
                last=str(stage)[:50]
                time.sleep(8)
                continue
            account=fetch("/api/account/status")
            probe=fetch("/api/storage/valkey-preflight")
            valkey=probe.get("valkey",{})
            success=(probe.get("contract")=="swrlz-storage-preflight-v1"
                    and valkey.get("connected") is True
                    and valkey.get("readWrite") is True
                    and valkey.get("lua") is True
                    and probe.get("activeBackendUnchanged") is True
                    and probe.get("dataMigrated") is False)
            report={"space":SPACE,"spaceRevision":REV,"stage":stage,
                    "accountHTTP":200,"accountResponseIsJson":isinstance(account,dict),
                    "valkeyProbePassed":success,"upstashStatus":probe.get("upstash",{}).get("httpStatus"),
                    "activeBackend":"upstash","recordsMigrated":False,
                    "adapterSourcePresent":True}
            print("SWRLZ_POSTADAPTER_LIVE_HEALTH "+json.dumps(report,sort_keys=True))
            return 0 if success and isinstance(account,dict) else 1
        except Exception as exc:
            last=type(exc).__name__
        time.sleep(8)
    print("SWRLZ_POSTADAPTER_LIVE_HEALTH "+json.dumps({"space":SPACE,
         "ready":False,"lastErrorType":last,"backendSwitched":False}))
    return 2

if __name__=="__main__":
    raise SystemExit(main())
