"""Runtime-owned SWRLZ frozen web snapshot collector hotfix wrapper.

Server 2.3.86 / Frozen Web Collector 1.0.2 preserves the verified 1.0.0
collector implementation from an immutable runtime commit, executes that source,
and then overrides only its durable state-save function.

This replaces the failed 1.0.1 source-string patcher. Pinning the base commit is
sufficient to make the loaded implementation immutable while avoiding brittle
text matching during module import.
"""
from __future__ import annotations

import urllib.request as _swrlz_patch_urlrequest

_SWRLZ_PATCH_BASE_COMMIT = "4b4d548c6519bec8c0b52ef524fa55e5a6c7ab88"
_SWRLZ_PATCH_BASE_URL = (
    "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/"
    f"{_SWRLZ_PATCH_BASE_COMMIT}/runtime_hot/web_snapshot_collector.py"
)

_request = _swrlz_patch_urlrequest.Request(
    _SWRLZ_PATCH_BASE_URL,
    headers={"User-Agent": "swrlz-frozen-web-collector-hotfix/1.0.2", "Cache-Control": "no-cache"},
)
with _swrlz_patch_urlrequest.urlopen(_request, timeout=12) as _response:
    _swrlz_base_bytes = _response.read(900_001)
if len(_swrlz_base_bytes) > 900_000:
    raise RuntimeError("COLLECTOR_PATCH_BASE_TOO_LARGE")
_swrlz_base_source = _swrlz_base_bytes.decode("utf-8")
exec(compile(_swrlz_base_source, _SWRLZ_PATCH_BASE_URL, "exec"), globals(), globals())


# Override only the durable control-state writer from the pinned 1.0.0 source.
def _save_state(store: BlobStore, state: dict[str, Any], etag: str | None) -> str | None:
    previous_revision = int(state.get("stateRevision", 0))
    state["stateRevision"] = previous_revision + 1
    state["updatedAt"] = _now()
    expected_revision = state["stateRevision"]

    effective_etag = etag
    immutable = False
    if effective_etag is None:
        # Missing ETag is not proof that the durable pathname is absent.
        # Re-read through cache=0 and distinguish a true create from an
        # existing object whose read path did not surface a usable ETag.
        persisted_before, discovered_etag = store.get_json(STATE_PATH)
        if persisted_before is None:
            immutable = True
        else:
            actual_before = int(persisted_before.get("stateRevision", -1))
            if actual_before != previous_revision:
                raise CollectorError(
                    409,
                    "STATE_WRITE_CONFLICT",
                    "Collector state advanced before this write; reload and retry.",
                    {"expectedRevision": previous_revision, "actualRevision": actual_before},
                )
            effective_etag = discovered_etag

    result = store.put_json(STATE_PATH, state, etag=effective_etag, immutable=immutable)
    response_etag = result.get("etag") if isinstance(result.get("etag"), str) and result.get("etag") else None

    # Always perform a consistent read-back. Comparing canonical JSON as well
    # as revision keeps the no-ETag fallback fail-loud if another worker
    # supersedes this write before confirmation.
    persisted, fetched_etag = store.get_json(STATE_PATH)
    actual_revision = int(persisted.get("stateRevision", -1)) if persisted is not None else -1
    if persisted is None or actual_revision != expected_revision or _compact_json(persisted) != _compact_json(state):
        raise CollectorError(
            409,
            "STATE_WRITE_CONFLICT",
            "Collector state was superseded while confirming the write; reload and retry.",
            {"expectedRevision": expected_revision, "actualRevision": actual_revision},
        )
    return response_etag or fetched_etag


_swrlz_base_inspect_module = inspect_module


def inspect_module() -> dict[str, Any]:
    details = _swrlz_base_inspect_module()
    details["compatibilityPatch"] = {
        "id": "blob-state-etag-fallback-2",
        "collectorVersion": "1.0.2",
        "baseCommit": _SWRLZ_PATCH_BASE_COMMIT,
        "stateSchemaChanged": False,
        "apiSchemaChanged": False,
        "replacesFailedPatch": "1.0.1",
    }
    return details
