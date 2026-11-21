"""Read-only verification of existing Hugging Face Space Valkey probe."""
import json
import time
import urllib.error
import urllib.request
import sys

URL="https://kamiloki-swyrlz.hf.space/api/storage/valkey-preflight"
def main():
    deadline=time.monotonic()+420
    last_type="NotReady"
    while time.monotonic()<deadline:
        try:
            req=urllib.request.Request(URL,headers={"Accept":"application/json","User-Agent":"SWRLZ-Valkey-Verification/1"})
            with urllib.request.urlopen(req,timeout=15) as response:
                raw=response.read(3000)
                if len(raw)>=3000: raise ValueError("OversizedProviderReply")
            body=json.loads(raw)
            if not isinstance(body,dict) or body.get("contract")!="swrlz-storage-preflight-v1":
                last_type="ProbeNotInstalledOnActiveProcess"
            else:
                valkey=body.get("valkey") if isinstance(body.get("valkey"),dict) else {}
                upstash=body.get("upstash") if isinstance(body.get("upstash"),dict) else {}
                receipt={
                    "space":"kamiloki/Swyrlz",
                    "probeContractVerified":True,
                    "valkeyTLSUri":bool(valkey.get("tls")),
                    "valkeyConnected":bool(valkey.get("connected")),
                    "valkeyReadWrite":bool(valkey.get("readWrite")),
                    "valkeyLua":bool(valkey.get("lua")),
                    "valkeyErrorType":str(valkey.get("errorType") or "")[:80],
                    "upstashReachable":bool(upstash.get("reachable")),
                    "upstashHTTPStatus":upstash.get("httpStatus") if type(upstash.get("httpStatus")) is int else None,
                    "upstashErrorType":str(upstash.get("errorType") or "")[:80],
                    "activeBackendUnchanged":body.get("activeBackendUnchanged") is True,
                    "migrationPerformed":body.get("dataMigrated") is True,
                }
                print("SWRLZ_VALKEY_LIVE_VERIFY "+json.dumps(receipt,sort_keys=True))
                return 0 if (receipt["valkeyConnected"] and receipt["valkeyReadWrite"] and receipt["valkeyLua"]
                             and receipt["activeBackendUnchanged"] and not receipt["migrationPerformed"]) else 1
        except urllib.error.HTTPError as exc:
            last_type="HTTP_"+str(exc.code)
        except Exception as exc:
            last_type=type(exc).__name__
        time.sleep(8)
    print("SWRLZ_VALKEY_LIVE_VERIFY "+json.dumps({"space":"kamiloki/Swyrlz",
          "probeReady":False,"lastErrorType":last_type,"backendSwitched":False}))
    return 2

if __name__=="__main__":
    sys.exit(main())
