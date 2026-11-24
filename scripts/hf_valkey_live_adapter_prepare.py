"""Prepare, but DO NOT deploy, native Valkey adapter for active HF Chat Redis gateway."""
from __future__ import annotations
import ast, hashlib, json, os
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download

SPACE="kamiloki/Swyrlz"
BASE_REV="18812f52ccdb40da5faded7ebdb8ac31c83f0661"
TARGET="github_connection.py"
ANCHOR="def _redis(c, *args):"
MARKER="# SWRLZ_VALKEY_NATIVE_REDIS_BACKEND_V1"
PATCH = '''from functools import lru_cache as _swrlz_valkey_lru_cache

@_swrlz_valkey_lru_cache(maxsize=2)
def _swrlz_valkey_native_client(uri):
    from redis import Redis
    return Redis.from_url(uri, decode_responses=True,
                          ssl_cert_reqs="required", socket_connect_timeout=3,
                          socket_timeout=15, health_check_interval=30,
                          max_connections=20)


def _redis(c, *args):
    # SWRLZ_VALKEY_NATIVE_REDIS_BACKEND_V1
    if os.getenv("SWRLZ_REDIS_BACKEND", "upstash").strip().lower() == "valkey":
        uri = os.environ.get("SWRLZ_VALKEY_URL", "")
        if not uri.startswith("rediss://"):
            raise ValueError("Valkey TLS configuration missing")
        client = _swrlz_valkey_native_client(uri)
        pool = client.connection_pool
        connection = None
        try:
            # Raw RESP avoids redis-py callbacks changing SET "OK" into True
            # or flattening ZRANGE WITHSCORES into tuples, preserving Upstash
            # HTTP REST result types expected by legacy callers.
            connection = pool.get_connection(str(args[0]))
            connection.send_command(*args)
            return connection.read_response()
        except Exception as exc:
            raise ValueError("Valkey command unavailable: " + type(exc).__name__) from None
        finally:
            if connection is not None:
                pool.release(connection)
'''

def main():
    api=HfApi(token=os.environ["HF_TOKEN"])
    live=api.repo_info(SPACE,repo_type="space")
    if live.sha!=BASE_REV:
        raise RuntimeError("LIVE_REV_CHANGED_ABORT_NO_MUTATION")
    source=Path(hf_hub_download(SPACE,TARGET,repo_type="space",revision=BASE_REV,token=api.token)).read_text("utf-8")
    if source.count(ANCHOR)!=1 or MARKER in source:
        raise RuntimeError("REDIS_GATEWAY_SHAPE_CHANGED")
    patched=source.replace(ANCHOR,PATCH,1)
    ast.parse(patched)
    path=Path("valkey-adapter-candidate")/TARGET
    path.parent.mkdir(exist_ok=True)
    path.write_text(patched,encoding="utf-8")
    print("SWRLZ_LIVE_ADAPTER_CANDIDATE "+json.dumps({
        "baseSpaceRevision":BASE_REV,"sourceFile":TARGET,
        "originalSha256":hashlib.sha256(source.encode()).hexdigest(),
        "candidateSha256":hashlib.sha256(patched.encode()).hexdigest(),
        "defaultBackendUnchanged":True,"published":False,"migrated":False}))

if __name__=="__main__": main()
