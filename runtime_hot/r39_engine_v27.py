"""R39 hot v27 cross-worker cursor residency overlay.

Loads the proven v26 conversational/vectorized engine from its immutable commit, then
adds a region-shared exact-float32 recurrent cursor backed by Vercel Runtime Cache when
the base image provides the Vercel Python SDK. Worker-local prefix reuse remains the
fastest first choice. Shared restore is an exact-prefix fallback across Fluid workers.
"""
from __future__ import annotations

import base64
import concurrent.futures
import hashlib
import json
import threading
import zlib

import numpy as np
import types
import urllib.request

_V26_COMMIT = "3dc70e8d02777fd622db3ae3311fad13b7382e6a"
_V26_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V26_COMMIT}/runtime_hot/r39_engine.py"
_req = urllib.request.Request(_V26_URL, headers={"User-Agent": "swrlz-hot-r39-v27"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _v26_source = _response.read(4_000_001)
if len(_v26_source) > 4_000_000:
    raise RuntimeError("R39_V26_SOURCE_TOO_LARGE")
exec(compile(_v26_source.decode("utf-8"), _V26_URL, "exec"), globals(), globals())

# Runtime Cache is intentionally optional so this hot source remains usable on the
# current base image before 2.2.6 is manually redeployed.
try:
    from vercel.functions import RuntimeCache  # type: ignore
    _RUNTIME_CACHE = RuntimeCache(namespace="swrlz-r39-cursor-v1")
    _RUNTIME_CACHE_IMPORT_ERROR = ""
except Exception as _cache_exc:  # pragma: no cover - depends on deployed base image
    RuntimeCache = None  # type: ignore
    _RUNTIME_CACHE = None
    _RUNTIME_CACHE_IMPORT_ERROR = f"{type(_cache_exc).__name__}: {_cache_exc}"

_CURSOR_SCHEMA = "swrlz-r39-recurrent-cursor-v1"
_CURSOR_TTL_SECONDS = 15 * 60
_CURSOR_CHUNK_TOKENS = 128
_CURSOR_MAX_TOKENS = 1024
_CURSOR_WRITE_WORKERS = 6
_CURSOR_THREAD = threading.local()
_CURSOR_STATUS_LOCK = threading.RLock()
_CURSOR_STATUS: dict[str, str] = {}

_LOCAL_PREFIX_GET = _impl._prefix_get
_LOCAL_PREFIX_PUT = _impl._prefix_put
_ORIGINAL_RUN_JOB = _impl._run_job
_V26_GENERATE_EVENTS = generate_events
_V26_INSPECT_ENGINE = inspect_engine


def _cursor_request_id() -> str:
    return str(getattr(_CURSOR_THREAD, "request_id", "") or "")


def _set_cursor_status(text: str) -> None:
    request_id = _cursor_request_id()
    if not request_id:
        return
    with _CURSOR_STATUS_LOCK:
        _CURSOR_STATUS[request_id] = text


def _pop_cursor_status(request_id: str) -> str:
    with _CURSOR_STATUS_LOCK:
        return _CURSOR_STATUS.pop(str(request_id or ""), "")


def _thread_key(thread_id: str) -> str:
    digest = hashlib.sha256(str(thread_id).encode("utf-8")).hexdigest()[:40]
    return f"cursor:{digest}"


def _encode_array(value: np.ndarray) -> str:
    raw = np.ascontiguousarray(value, dtype=np.float32).tobytes(order="C")
    return base64.b64encode(zlib.compress(raw, 3)).decode("ascii")


def _decode_array(value: str, shape: tuple[int, ...]) -> np.ndarray:
    raw = zlib.decompress(base64.b64decode(value.encode("ascii"), validate=True))
    expected = int(np.prod(shape, dtype=np.int64)) * 4
    if len(raw) != expected:
        raise ValueError(f"cursor array byte mismatch: expected {expected}, got {len(raw)}")
    return np.frombuffer(raw, dtype=np.float32).reshape(shape).copy()


def _cache_get(key: str):
    if _RUNTIME_CACHE is None:
        return None
    return _RUNTIME_CACHE.get(key)


def _cache_set(key: str, value: str) -> None:
    if _RUNTIME_CACHE is None:
        return
    _RUNTIME_CACHE.set(key, value, {"ttl": _CURSOR_TTL_SECONDS, "name": "SWRLZ R39 recurrent cursor"})


def _serialize_cursor(thread_id: str, tokens: list[int], state, logits: np.ndarray) -> tuple[str, str, list[tuple[str, str]]]:
    base_key = _thread_key(thread_id)
    generation = hashlib.sha256(
        (HOT_REVISION + ":" + str(len(tokens)) + ":" + hashlib.sha256(np.asarray(tokens, dtype=np.int32).tobytes()).hexdigest()).encode("utf-8")
    ).hexdigest()[:20]
    conv = {str(layer): _encode_array(value) for layer, value in state.conv.items()}
    shards: list[tuple[str, str]] = []
    kv_manifest: dict[str, list[str]] = {}
    for layer, entries in state.kv.items():
        layer_keys: list[str] = []
        for start in range(0, len(entries), _CURSOR_CHUNK_TOKENS):
            block = entries[start:start + _CURSOR_CHUNK_TOKENS]
            if not block:
                continue
            keys = np.stack([item[0] for item in block], axis=0).astype(np.float32, copy=False).reshape(len(block), 512)
            values = np.stack([item[1] for item in block], axis=0).astype(np.float32, copy=False).reshape(len(block), 512)
            packed = np.stack((keys, values), axis=1)
            shard_key = f"{base_key}:g:{generation}:l:{int(layer)}:s:{start // _CURSOR_CHUNK_TOKENS}"
            shards.append((shard_key, _encode_array(packed)))
            layer_keys.append(shard_key)
        kv_manifest[str(layer)] = layer_keys
    meta = {
        "schema": _CURSOR_SCHEMA,
        "hotRevision": HOT_REVISION,
        "modelSha256": MODEL_SHA256,
        "tokens": [int(x) for x in tokens],
        "pos": int(state.pos),
        "conv": conv,
        "logits": _encode_array(np.asarray(logits, dtype=np.float32).reshape(-1)),
        "kv": kv_manifest,
        "chunkTokens": _CURSOR_CHUNK_TOKENS,
    }
    return base_key, json.dumps(meta, separators=(",", ":"), ensure_ascii=False), shards


def _persist_cursor(thread_id: str, tokens: list[int], state, logits: np.ndarray) -> None:
    if _RUNTIME_CACHE is None:
        _set_cursor_status("shared cursor unavailable on this base image; worker-local prefix cache remains active")
        return
    if not thread_id:
        _set_cursor_status("shared cursor skipped: threadId missing")
        return
    if not tokens or len(tokens) > _CURSOR_MAX_TOKENS:
        _set_cursor_status(f"shared cursor skipped: {len(tokens)} token(s) exceeds {_CURSOR_MAX_TOKENS}-token persistence bound")
        return
    try:
        base_key, meta_text, shards = _serialize_cursor(thread_id, tokens, state, logits)
        if shards:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(_CURSOR_WRITE_WORKERS, len(shards))) as pool:
                futures = [pool.submit(_cache_set, key, value) for key, value in shards]
                for future in futures:
                    future.result()
        # Metadata is the commit marker and is deliberately written last so readers never
        # observe a new cursor before all of its shards are available.
        _cache_set(base_key, meta_text)
        _set_cursor_status(f"shared cursor committed · tokens={len(tokens)} · shards={len(shards)} · exactFloat32=true · ttl={_CURSOR_TTL_SECONDS}s")
    except Exception as exc:
        _set_cursor_status(f"shared cursor write failed safely ({type(exc).__name__}: {exc}); worker-local cache preserved")


def _restore_cursor(thread_id: str, tokens: list[int]):
    if _RUNTIME_CACHE is None or not thread_id:
        return 0, None, None
    try:
        base_key = _thread_key(thread_id)
        raw_meta = _cache_get(base_key)
        if raw_meta is None:
            _set_cursor_status("shared cursor miss · no region cache entry for this conversation")
            return 0, None, None
        if isinstance(raw_meta, bytes):
            raw_meta = raw_meta.decode("utf-8")
        meta = json.loads(str(raw_meta)) if isinstance(raw_meta, str) else raw_meta
        if not isinstance(meta, dict):
            raise ValueError("cursor metadata is not an object")
        if meta.get("schema") != _CURSOR_SCHEMA or meta.get("hotRevision") != HOT_REVISION or meta.get("modelSha256") != MODEL_SHA256:
            _set_cursor_status("shared cursor ignored · runtime/model lineage changed")
            return 0, None, None
        cached_tokens = [int(x) for x in list(meta.get("tokens") or [])]
        if not cached_tokens or len(cached_tokens) > len(tokens) or tokens[:len(cached_tokens)] != cached_tokens:
            _set_cursor_status(f"shared cursor ignored · exact token prefix mismatch · cached={len(cached_tokens)} current={len(tokens)}")
            return 0, None, None
        state = _impl.base.RecurrentState()
        for layer_text, encoded in dict(meta.get("conv") or {}).items():
            layer = int(layer_text)
            if layer not in state.conv:
                raise ValueError(f"unknown conv layer {layer}")
            state.conv[layer] = _decode_array(str(encoded), (2, 1024))
        kv_manifest = dict(meta.get("kv") or {})
        for layer in list(state.kv):
            shard_keys = list(kv_manifest.get(str(layer)) or [])
            entries = []
            for shard_key in shard_keys:
                raw = _cache_get(str(shard_key))
                if raw is None:
                    raise ValueError(f"missing KV shard for layer {layer}")
                if isinstance(raw, bytes):
                    raw = raw.decode("ascii")
                packed_raw = zlib.decompress(base64.b64decode(str(raw).encode("ascii"), validate=True))
                width_bytes = 2 * 512 * 4
                if len(packed_raw) % width_bytes:
                    raise ValueError(f"KV shard byte mismatch for layer {layer}")
                count = len(packed_raw) // width_bytes
                packed = np.frombuffer(packed_raw, dtype=np.float32).reshape(count, 2, 512).copy()
                for row in packed:
                    entries.append((row[0].copy(), row[1].copy()))
            state.kv[layer] = entries
        state.pos = int(meta.get("pos") or len(cached_tokens))
        if state.pos != len(cached_tokens):
            raise ValueError(f"cursor position mismatch: pos={state.pos}, tokens={len(cached_tokens)}")
        logits = _decode_array(str(meta.get("logits") or ""), (65536,))
        _set_cursor_status(f"shared cursor restored · reused={len(cached_tokens)}/{len(tokens)} · crossWorker=true · exactFloat32=true")
        return len(cached_tokens), state, logits
    except Exception as exc:
        _set_cursor_status(f"shared cursor restore failed safely ({type(exc).__name__}: {exc}); cold/local fallback selected")
        return 0, None, None


def _shared_prefix_get(tokens: list[int]):
    local = _LOCAL_PREFIX_GET(tokens)
    if local[0] > 0:
        _set_cursor_status(f"worker-local cursor hit · reused={local[0]}/{len(tokens)} · crossWorker=false")
        return local
    return _restore_cursor(str(getattr(_CURSOR_THREAD, "thread_id", "") or ""), tokens)


def _shared_prefix_put(tokens: list[int], state, logits: np.ndarray | None) -> None:
    _LOCAL_PREFIX_PUT(tokens, state, logits)
    if logits is None:
        return
    count = int(getattr(_CURSOR_THREAD, "put_count", 0)) + 1
    _CURSOR_THREAD.put_count = count
    # The engine performs one put after prompt prefill and a second after generation.
    # Persist only the second, append-ready cursor so shared storage never points at a
    # prompt-only state while the assistant answer is still being generated.
    if count < 2:
        return
    _persist_cursor(str(getattr(_CURSOR_THREAD, "thread_id", "") or ""), list(tokens), state, logits)


def _run_job_with_cursor(job, payload, is_cancelled):
    _CURSOR_THREAD.thread_id = str(payload.get("threadId") or "")
    _CURSOR_THREAD.request_id = str(payload.get("requestId") or "")
    _CURSOR_THREAD.put_count = 0
    try:
        return _ORIGINAL_RUN_JOB(job, payload, is_cancelled)
    finally:
        _CURSOR_THREAD.thread_id = ""
        _CURSOR_THREAD.request_id = ""
        _CURSOR_THREAD.put_count = 0


_impl._prefix_get = _shared_prefix_get
_impl._prefix_put = _shared_prefix_put
_impl._run_job = _run_job_with_cursor

_impl.HOT_SERVER_VERSION = "2.1.36"
_impl.HOT_REVISION = "2.1.36-hot-boundary-v27-region-shared-recurrent-cursor-v3.2"
HOT_SERVER_VERSION = _impl.HOT_SERVER_VERSION
HOT_REVISION = _impl.HOT_REVISION


def generate_events(payload, is_cancelled=None):
    request_id = str(payload.get("requestId") or "")
    # Direct/non-detached inference fallback still receives conversation identity.
    _CURSOR_THREAD.thread_id = str(payload.get("threadId") or "")
    _CURSOR_THREAD.request_id = request_id
    _CURSOR_THREAD.put_count = 0
    try:
        for event in _V26_GENERATE_EVENTS(payload, is_cancelled):
            status = _pop_cursor_status(request_id)
            if status:
                yield {"type": "STATUS", "phase": "CURSOR_RESIDENCY", "reason": status}
            yield event
        status = _pop_cursor_status(request_id)
        if status:
            yield {"type": "STATUS", "phase": "CURSOR_RESIDENCY", "reason": status}
    finally:
        _CURSOR_THREAD.thread_id = ""
        _CURSOR_THREAD.request_id = ""
        _CURSOR_THREAD.put_count = 0


def inspect_engine():
    result = _V26_INSPECT_ENGINE()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "crossWorkerCursorPersistence": _RUNTIME_CACHE is not None,
            "sharedCursorBackend": "vercel-runtime-cache" if _RUNTIME_CACHE is not None else "unavailable-until-base-2.2.6",
            "sharedCursorSchema": _CURSOR_SCHEMA,
            "sharedCursorExactFloat32": True,
            "sharedCursorMetadataCommitLast": True,
            "sharedCursorChunkTokens": _CURSOR_CHUNK_TOKENS,
            "sharedCursorMaxTokens": _CURSOR_MAX_TOKENS,
            "sharedCursorTtlSeconds": _CURSOR_TTL_SECONDS,
            "sharedCursorImportError": _RUNTIME_CACHE_IMPORT_ERROR,
            "workerLocalCursorFirst": True,
        })
    return result
