"""Guarded fresh-start cutover of the existing §C Space to Aiven Valkey.

Reversible configuration change. Never deletes, reads, or copies personal
records from Upstash. Validates actual live Redis gateway after restart.
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE = "kamiloki/Swyrlz"
SPACE_BASE = "https://kamiloki-swyrlz.hf.space"
EXPECTED_REV = "cca069b30df86f4214138a3bfcdbb9331579f16e"
GATEWAY_FILE = "github_connection.py"
PROBE_FILE = "valkey_preflight.py"
VARIABLE = "SWRLZ_REDIS_BACKEND"
MARKER = "# SWRLZ_NATIVE_GATEWAY_POST_CUTOVER_CHECK_V1"

CHECK = r'''
# SWRLZ_NATIVE_GATEWAY_POST_CUTOVER_CHECK_V1
from threading import Lock as _valkey_check_lock_class
from secrets import token_hex as _valkey_check_token_hex
import os as _valkey_check_os

_valkey_gateway_check_lock = _valkey_check_lock_class()
_valkey_gateway_check_cached = {}
_valkey_prior_install = install

def install(app):
    _valkey_prior_install(app)

    @app.get("/api/storage/valkey-native-gateway-check")
    def valkey_native_gateway_check():
        """One cached throwaway-key test of the *live shared* Redis gateway."""
        if _valkey_check_os.getenv("SWRLZ_REDIS_BACKEND", "").strip().lower() != "valkey":
            return {"contract":"swrlz-valkey-gateway-v1","backendSelected":False,
                    "nativeSETGET":False,"nativeLua":False}
        with _valkey_gateway_check_lock:
            if "result" in _valkey_gateway_check_cached:
                return dict(_valkey_gateway_check_cached["result"])
            import github_connection as _gh
            temporary_key = "swrlz:probe:gateway:" + _valkey_check_token_hex(12)
            status = {"contract":"swrlz-valkey-gateway-v1","backendSelected":True,
                      "nativeSETGET":False,"nativeLua":False,"dataMigrated":False}
            try:
                config = _gh._settings()
                set_result = _gh._redis(config,"SET",temporary_key,"probe-ok","EX",30,"NX")
                get_result = _gh._redis(config,"GET",temporary_key)
                status["nativeSETGET"] = set_result == "OK" and get_result == "probe-ok"
                if status["nativeSETGET"]:
                    lua_result = _gh._redis(config,"EVAL",
                        "return redis.call('GET',KEYS[1])","1",temporary_key)
                    status["nativeLua"] = lua_result == "probe-ok"
            except Exception as exc:
                status["errorType"] = type(exc).__name__
            finally:
                try:
                    _gh._redis(_gh._settings(),"DEL",temporary_key)
                except Exception:
                    pass
            _valkey_gateway_check_cached["result"] = status
            return dict(status)
'''

def report(name, **kwargs):
    print(name+" "+json.dumps(kwargs,sort_keys=True),flush=True)

def http_json(path, timeout=12):
    req=urllib.request.Request(SPACE_BASE+path, headers={
        "Accept":"application/json","User-Agent":"SWRLZ-Valkey-GuardedCutover/1"})
    with urllib.request.urlopen(req,timeout=timeout) as res:
        if res.status!=200:
            raise RuntimeError("HTTP_NOT_200")
        raw=res.read(2500)
        if len(raw)>=2500: raise RuntimeError("OVERSIZED_RESPONSE")
        body=json.loads(raw)
        if not isinstance(body,dict):raise RuntimeError("INVALID_JSON_SHAPE")
        return body

def readiness(api, must_select, deadline_seconds=390):
    deadline=time.monotonic()+deadline_seconds
    last="Starting"
    while time.monotonic()<deadline:
        try:
            stage=api.get_space_runtime(SPACE).stage
            if stage!="RUNNING":
                last="stage:"+str(stage)[:36]
            else:
                account=http_json("/api/account/status")
                gateway=http_json("/api/storage/valkey-native-gateway-check")
                regular=http_json("/api/storage/valkey-preflight")
                valkey=regular.get("valkey") or {}
                selected=gateway.get("backendSelected") is True
                native_ok=(gateway.get("contract")=="swrlz-valkey-gateway-v1"
                           and gateway.get("nativeSETGET") is True
                           and gateway.get("nativeLua") is True)
                probe_ok=(regular.get("contract")=="swrlz-storage-preflight-v1"
                          and valkey.get("connected") is True
                          and valkey.get("readWrite") is True
                          and valkey.get("lua") is True)
                if selected==must_select and (not must_select or (native_ok and probe_ok)):
                    report("SWRLZ_VALKEY_READINESS",
                           stage=stage, accountHttp=200,
                           accountJson=True, selected=selected, nativeGatewayOK=native_ok,
                           valkeyTLSOK=probe_ok,
                           noAccountHistoryCopied=True)
                    return True
                last=("selected:"+str(selected)+"/expected:"+str(must_select)
                      +"/gateway:"+str(gateway.get("errorType") or "not-ready")[:35])
        except Exception as exc:
            last=type(exc).__name__
        time.sleep(7)
    report("SWRLZ_VALKEY_READINESS_FAILED", lastType=last)
    return False

def main():
    token=os.environ.get("HF_TOKEN","").strip()
    if not token:raise RuntimeError("HF_TOKEN_MISSING")
    api=HfApi(token=token)
    revision=api.repo_info(SPACE,repo_type="space").sha
    if revision!=EXPECTED_REV:
        report("SWRLZ_VALKEY_CUTOVER_BLOCKED",reason="live_source_changed",revision=revision)
        return 2
    names=set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
    if not {GATEWAY_FILE,PROBE_FILE,"station.py"}.issubset(names):
        raise RuntimeError("LIVE_FILES_MISSING")
    secrets=set(api.get_space_secrets(SPACE))
    variables=api.get_space_variables(SPACE)
    if VARIABLE in secrets or VARIABLE in variables:
        raise RuntimeError("BACKEND_ALREADY_EXPLICITLY_CONFIGURED_REFUSE")
    if not {"SWRLZ_VALKEY_URL","UPSTASH_REDIS_REST_URL",
            "UPSTASH_REDIS_REST_TOKEN","SWRLZ_GITHUB_ENCRYPTION_KEY"}.issubset(secrets):
        raise RuntimeError("REQUIRED_KEYS_MISSING")
    gateway=Path(hf_hub_download(SPACE,GATEWAY_FILE,repo_type="space",
                                revision=revision,token=token)).read_text("utf-8")
    if gateway.count("# SWRLZ_VALKEY_NATIVE_REDIS_BACKEND_V1")!=1:
        raise RuntimeError("LIVE_GATEWAY_NOT_INSTALLED")
    original=Path(hf_hub_download(SPACE,PROBE_FILE,repo_type="space",
                                 revision=revision,token=token)).read_text("utf-8")
    if original.count("def install(app):")!=1 or MARKER in original:
        raise RuntimeError("PROBE_ALREADY_PATCHED_OR_CHANGED")
    modified=original.rstrip()+"\n\n"+CHECK
    ast.parse(modified)
    Path("valkey-cutover-rollback").mkdir(exist_ok=True)
    Path("valkey-cutover-rollback/valkey_preflight.py").write_text(original,encoding="utf-8")
    Path("valkey-cutover-rollback/manifest.json").write_text(json.dumps({
        "target":SPACE,"beforeSourceRevision":revision,
        "sourceFile":PROBE_FILE,"beforeBackend":"upstash",
        "originalUserKeysDeleted":False,"migrationPerformed":False},indent=2))
    report("SWRLZ_VALKEY_CUTOVER_PREFLIGHT", sourcePinned=True,
           aivenSecretPresent=True, upstashSecretsPreserved=True,
           encryptionKeyPreserved=True, oldDataNotDeleted=True)
    if not readiness_before(api):
        raise RuntimeError("ORIGINAL_RUNTIME_NOT_HEALTHY")

    # Source-pinned additive probe update, never a replacement of station/model.
    patch=api.create_commit(repo_id=SPACE,repo_type="space",
        operations=[CommitOperationAdd(path_in_repo=PROBE_FILE,
                                      path_or_fileobj=io.BytesIO(modified.encode("utf-8")))],
        commit_message="Test real native Valkey gateway after fresh-start selection",
        parent_commit=revision)
    report("SWRLZ_VALKEY_GATEWAY_TEST_ADDED",spaceRevision=patch.oid)
    if not readiness(api,must_select=False,deadline_seconds=360):
        # Do not risk switching if optional probe failed to activate.
        raise RuntimeError("LIVE_GATEWAY_PRECUTOVER_NOT_READY")
    variable_set=False
    try:
        api.add_space_variable(SPACE, VARIABLE, "valkey",
            description="Fresh-start durable account storage on TLS Aiven Valkey")
        variable_set=True
        report("SWRLZ_VALKEY_CUTOVER_SELECTED",backend="valkey",
               dataMigrated=False, upstashDataDeleted=False)
        if not readiness(api,must_select=True,deadline_seconds=420):
            raise RuntimeError("NATIVE_GATEWAY_ACCEPTANCE_FAILED")
        current=api.get_space_variables(SPACE)
        if VARIABLE not in current:
            raise RuntimeError("BACKEND_FLAG_NOT_PERSISTED")
        report("SWRLZ_VALKEY_CUTOVER_VERIFIED",backend="valkey",
               nativeReadWrite=True,nativeLua=True,
               accountEndpoint=True,
               oldDataUntouched=True,
               note="Google sign-in needs user-side testing")
        return 0
    except Exception as exc:
        report("SWRLZ_VALKEY_CUTOVER_ROLLING_BACK",causeType=type(exc).__name__)
        if variable_set:
            try:
                api.delete_space_variable(SPACE, VARIABLE)
                report("SWRLZ_VALKEY_BACKEND_RESTORED",backend="upstash",
                       userDataDeleted=False)
            except Exception as rollback_error:
                report("SWRLZ_VALKEY_ROLLBACK_FAILED",errorType=type(rollback_error).__name__)
                raise
        raise

def readiness_before(api):
    try:
        if api.get_space_runtime(SPACE).stage!="RUNNING":
            return False
        account=http_json("/api/account/status")
        probe=http_json("/api/storage/valkey-preflight")
        valkey=probe.get("valkey") or {}
        return (isinstance(account,dict) and
                probe.get("contract")=="swrlz-storage-preflight-v1"
                and valkey.get("connected") is True
                and valkey.get("readWrite") is True
                and valkey.get("lua") is True)
    except Exception:
        return False

if __name__=="__main__":
    sys.exit(main())
