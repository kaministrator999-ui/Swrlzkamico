"""Runtime-owned SWRLZ frozen web snapshot collector hotfix wrapper.

Server 2.3.85 / Frozen Web Collector 1.0.1 preserves the verified 1.0.0
collector implementation byte-for-byte from the pinned runtime commit below,
then replaces only its durable state-save function. The patch fixes an existing
state.json edge case where a private Blob read can provide no usable ETag: the
old code interpreted that as a brand-new object and requested an immutable
create, which Vercel Blob correctly rejects when state.json already exists.

The pinned base commit plus Git-blob hash check prevents this wrapper from
silently executing mutable/unverified source. Future collector work should
flatten this compatibility wrapper back into the canonical implementation once
that source is intentionally revised.
"""
from __future__ import annotations

import hashlib as _patch_hashlib
import urllib.request as _patch_urlrequest

_PATCH_BASE_COMMIT = "4b4d548c6519bec8c0b52ef524fa55e5a6c7ab88"
_PATCH_BASE_GIT_BLOB = "0ce4e586922fd68fdda3ef4891db6c12c35266e2"
_PATCH_BASE_URL = (
    "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/"
    f"{_PATCH_BASE_COMMIT}/runtime_hot/web_snapshot_collector.py"
)

_PATCH_OLD_SAVE_STATE = '''def _save_state(store: BlobStore, state: dict[str, Any], etag: str | None) -> str | None:\n    state["stateRevision"] = int(state.get("stateRevision", 0)) + 1\n    state["updatedAt"] = _now()\n    expected_revision = state["stateRevision"]\n    result = store.put_json(STATE_PATH, state, etag=etag, immutable=etag is None)\n    new_etag = result.get("etag") if isinstance(result.get("etag"), str) else None\n    if new_etag:\n        return new_etag\n    persisted, fetched_etag = store.get_json(STATE_PATH)\n    if persisted is None or int(persisted.get("stateRevision", -1)) != expected_revision:\n        raise CollectorError(409, "STATE_WRITE_CONFLICT", "Collector state could not be confirmed after writing; reload and retry.")\n    return fetched_etag\n'''

_PATCH_NEW_SAVE_STATE = '''def _save_state(store: BlobStore, state: dict[str, Any], etag: str | None) -> str | None:\n    previous_revision = int(state.get("stateRevision", 0))\n    state["stateRevision"] = previous_revision + 1\n    state["updatedAt"] = _now()\n    expected_revision = state["stateRevision"]\n\n    effective_etag = etag\n    immutable = False\n    if effective_etag is None:\n        # A missing ETag does not mean the durable pathname is absent. Re-read\n        # with cache=0 (BlobStore.get_json) and distinguish existing state from\n        # a genuinely new object before choosing create-vs-overwrite behavior.\n        persisted_before, discovered_etag = store.get_json(STATE_PATH)\n        if persisted_before is None:\n            immutable = True\n        else:\n            persisted_revision = int(persisted_before.get("stateRevision", -1))\n            if persisted_revision != previous_revision:\n                raise CollectorError(\n                    409,\n                    "STATE_WRITE_CONFLICT",\n                    "Collector state advanced before this write; reload and retry.",\n                    {"expectedRevision": previous_revision, "actualRevision": persisted_revision},\n                )\n            effective_etag = discovered_etag\n\n    result = store.put_json(STATE_PATH, state, etag=effective_etag, immutable=immutable)\n    response_etag = result.get("etag") if isinstance(result.get("etag"), str) and result.get("etag") else None\n\n    # Confirm the exact state, not only the revision. This keeps the no-ETag\n    # fallback fail-loud if another worker supersedes the write before the\n    # consistent read-back completes.\n    persisted, fetched_etag = store.get_json(STATE_PATH)\n    actual_revision = int(persisted.get("stateRevision", -1)) if persisted is not None else -1\n    if persisted is None or actual_revision != expected_revision or _compact_json(persisted) != _compact_json(state):\n        raise CollectorError(\n            409,\n            "STATE_WRITE_CONFLICT",\n            "Collector state was superseded while confirming the write; reload and retry.",\n            {"expectedRevision": expected_revision, "actualRevision": actual_revision},\n        )\n    return response_etag or fetched_etag\n'''


def _patch_git_blob_sha(data: bytes) -> str:
    prefix = f"blob {len(data)}\\0".encode("ascii")
    return _patch_hashlib.sha1(prefix + data).hexdigest()


_request = _patch_urlrequest.Request(
    _PATCH_BASE_URL,
    headers={"User-Agent": "swrlz-frozen-web-collector-hotfix/1.0.1", "Cache-Control": "no-cache"},
)
with _patch_urlrequest.urlopen(_request, timeout=12) as _response:
    _base_bytes = _response.read(900_001)
if len(_base_bytes) > 900_000:
    raise RuntimeError("COLLECTOR_PATCH_BASE_TOO_LARGE")
if _patch_git_blob_sha(_base_bytes) != _PATCH_BASE_GIT_BLOB:
    raise RuntimeError("COLLECTOR_PATCH_BASE_HASH_MISMATCH")
_base_source = _base_bytes.decode("utf-8")
if _base_source.count(_PATCH_OLD_SAVE_STATE) != 1:
    raise RuntimeError("COLLECTOR_PATCH_TARGET_MISMATCH")
_patched_source = _base_source.replace(_PATCH_OLD_SAVE_STATE, _PATCH_NEW_SAVE_STATE, 1)
exec(compile(_patched_source, _PATCH_BASE_URL + "#state-write-hotfix-1.0.1", "exec"), globals(), globals())

# Preserve inspectability of the temporary compatibility layer without changing
# the stable collector API or state schema.
_patch_base_inspect_module = inspect_module


def inspect_module() -> dict[str, Any]:
    details = _patch_base_inspect_module()
    details["compatibilityPatch"] = {
        "id": "blob-state-etag-fallback-1",
        "collectorVersion": "1.0.1",
        "baseCommit": _PATCH_BASE_COMMIT,
        "baseGitBlob": _PATCH_BASE_GIT_BLOB,
        "stateSchemaChanged": False,
        "apiSchemaChanged": False,
    }
    return details
