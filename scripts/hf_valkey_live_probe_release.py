#!/usr/bin/env python3
"""Guarded additive probe for the existing Hugging Face Chat Space.

Does not switch active storage or copy accounts. Never prints database URIs.
"""
from __future__ import annotations
import ast
import io
import json
import os
import re
import sys
import time
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download

SPACE = "kamiloki/Swyrlz"
EXPECTED_REV = "88ea11f8cc6e25995c4235c03a04df35c3944830"
MARKER = "# SWRLZ_VALKEY_NON_DESTRUCTIVE_PROBE_V1"
PATHS = ("station.py", "requirements.txt")
OUT = Path("valkey-live-probe-snapshot")

PROBE = r'''"""Nondestructive, cached Valkey/Upstash connectivity probe.

Does not select providers, migrate records, expose credentials, or modify user keys.
"""
from __future__ import annotations
import os
import secrets
import threading

_lock = threading.Lock()
_result = None

def _run():
    from redis import Redis
    import requests
    answer = {"contract":"swrlz-storage-preflight-v1",
              "valkey":{"tls":False,"readWrite":False,"lua":False},
              "upstash":{"reachable":False},
              "activeBackendUnchanged":True,
              "dataMigrated":False}
    url = os.environ.get("SWRLZ_VALKEY_URL", "")
    if url.startswith("rediss://"):
        answer["valkey"]["tls"] = True
        key = "swrlz:probe:valkey:" + secrets.token_hex(12)
        client = None
        try:
            client = Redis.from_url(url, decode_responses=True, socket_connect_timeout=3,
                                    socket_timeout=6, ssl_cert_reqs="required", max_connections=3)
            if client.ping() is True:
                answer["valkey"]["connected"] = True
                ok = client.set(key, "ok", ex=30, nx=True)
                answer["valkey"]["readWrite"] = bool(ok and client.get(key) == "ok")
                if answer["valkey"]["readWrite"]:
                    answer["valkey"]["lua"] = client.eval("return redis.call('GET', KEYS[1])", 1, key) == "ok"
        except Exception as exc:
            answer["valkey"]["errorType"] = type(exc).__name__
        finally:
            if client is not None:
                try: client.delete(key)
                except Exception: pass
    else:
        answer["valkey"]["errorType"] = "MissingTLSUri"
    upstream_url = os.environ.get("UPSTASH_REDIS_REST_URL", "").strip()
    upstream_token = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "").strip()
    if upstream_url.startswith("https://") and upstream_token:
        try:
            response = requests.post(upstream_url, json=["PING"], timeout=(3,6),
                headers={"Authorization":"Bearer " + upstream_token})
            answer["upstash"]["reachable"] = bool(
                response.ok and isinstance(response.json(),dict) and
                response.json().get("result") == "PONG")
            answer["upstash"]["httpStatus"] = response.status_code
        except Exception as exc:
            answer["upstash"]["errorType"] = type(exc).__name__
    return answer

def install(app):
    @app.get("/api/storage/valkey-preflight")
    def valkey_preflight():
        global _result
        with _lock:
            if _result is None:
                _result = _run()
            return dict(_result)
'''

def prepare(api, sha):
    if sha != EXPECTED_REV:
        raise RuntimeError("LIVE_SPACE_REVISION_CHANGED_REFUSE_MUTATION")
    info = api.repo_info(SPACE, repo_type="space")
    present = set(api.list_repo_files(SPACE, repo_type="space", revision=sha))
    if not set(PATHS).issubset(present) or "valkey_preflight.py" in present:
        raise RuntimeError("LIVE_SPACE_LAYOUT_CHANGED_REFUSE_MUTATION")
    originals = {}
    for p in PATHS:
        originals[p] = Path(hf_hub_download(SPACE, p, repo_type="space", revision=sha, token=api.token)).read_bytes()
    station = originals["station.py"].decode("utf-8")
    req = originals["requirements.txt"].decode("utf-8")
    if MARKER in station or "valkey_preflight" in station or "redis>=5,<7" in req:
        raise RuntimeError("LIVE_SPACE_ALREADY_PATCHED_REFUSE_REWRITE")
    if not re.search(r"^\s*app\s*=\s*FastAPI\s*\(", station, re.MULTILINE):
        raise RuntimeError("LIVE_SPACE_FASTAPI_APP_MISSING")
    addition = '\n' + MARKER + '\nfrom valkey_preflight import install as _install_valkey_preflight\n_install_valkey_preflight(app)\n'
    station = station.rstrip() + addition
    req = req.rstrip() + '\nredis>=5,<7\n'
    ast.parse(station, filename="station.py")
    ast.parse(PROBE, filename="valkey_preflight.py")
    patched = {"station.py":station.encode("utf-8"),
               "requirements.txt":req.encode("utf-8"),
               "valkey_preflight.py":PROBE.encode("utf-8")}
    OUT.mkdir(exist_ok=True)
    for path, data in originals.items():
        dst=OUT/path
        dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_bytes(data)
    (OUT/"manifest.json").write_text(json.dumps({"space":SPACE,"revision":sha,
        "backupFiles":list(PATHS),"addedFile":"valkey_preflight.py",
        "change":"additive-probe-no-backend-switch"},indent=2))
    return patched

def main():
    token=os.environ.get("HF_TOKEN","").strip()
    if not token:
        print("PROBE_RELEASE_UNAVAILABLE: missing HF_TOKEN")
        return 2
    api=HfApi(token=token)
    sha=api.repo_info(SPACE, repo_type="space").sha
    patched=prepare(api,sha)
    print("SWRLZ_VALKEY_PROBE_PREPARED "+json.dumps({"space":SPACE,
        "sourceRevision":sha,"files":list(patched),"backendSwitched":False,"dataCopied":False}))
    if sys.argv[1:] == ["publish"]:
        # Compare-and-swap the exact source revision to avoid overwriting any live change.
        result=api.create_commit(repo_id=SPACE,repo_type="space",
            operations=[CommitOperationAdd(path_in_repo=path,path_or_fileobj=io.BytesIO(data))
                        for path,data in patched.items()],
            commit_message="Add guarded TLS Valkey connectivity probe without storage cutover",
            parent_commit=sha)
        print("SWRLZ_VALKEY_PROBE_PUBLISHED "+json.dumps({
            "space":SPACE,"newRevision":result.oid,"activeStorageUnchanged":True}))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
