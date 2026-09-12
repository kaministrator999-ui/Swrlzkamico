#!/usr/bin/env python3
"""Deterministic verification for the runtime-owned frozen web collector."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "runtime_hot" / "web_snapshot_collector.py"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("swrlz_collector_verification", SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeStore:
    configured = True

    def __init__(self, module: Any) -> None:
        self.module = module
        self.objects: dict[str, bytes] = {}
        self.etags: dict[str, str] = {}
        self.sequence = 0

    def describe(self) -> dict[str, Any]:
        return {
            "backend": "vercel-blob",
            "configured": True,
            "access": "private",
            "authKind": "verification",
            "storeIdSuffix": "hidden",
            "authoritativeState": self.module.STATE_PATH,
            "ephemeralTmpUsedAsAuthority": False,
        }

    def require(self) -> None:
        return None

    def get_bytes(self, pathname: str):
        return self.objects.get(pathname), self.etags.get(pathname), {}

    def get_json(self, pathname: str):
        body, etag, _headers = self.get_bytes(pathname)
        return (json.loads(body.decode("utf-8")), etag) if body is not None else (None, None)

    def put_json(
        self,
        pathname: str,
        value: dict[str, Any],
        *,
        etag: str | None = None,
        immutable: bool = False,
        tolerate_existing: bool = False,
    ) -> dict[str, Any]:
        body = self.module._compact_json(value)
        existing = self.objects.get(pathname)
        if etag is not None and self.etags.get(pathname) != etag:
            raise self.module.CollectorError(409, "STATE_WRITE_CONFLICT", "verification etag mismatch")
        if immutable and existing is not None:
            if tolerate_existing and existing == body:
                return {"ok": True, "existed": True, "bytes": len(body), "etag": self.etags[pathname]}
            raise self.module.CollectorError(409, "IMMUTABLE_OBJECT_CONFLICT", "verification immutable conflict")
        self.sequence += 1
        current_etag = f'"verify-{self.sequence}"'
        self.objects[pathname] = body
        self.etags[pathname] = current_etag
        return {"ok": True, "existed": False, "bytes": len(body), "etag": current_etag}

    def list(self, prefix: str, limit: int = 100):
        return [
            {"pathname": path, "size": len(body)}
            for path, body in sorted(self.objects.items())
            if path.startswith(prefix)
        ][:limit]


class Request:
    def __init__(self, method: str, body: dict[str, Any] | None = None, query: dict[str, str] | None = None) -> None:
        self.method = method
        self._body = json.dumps(body).encode("utf-8") if body is not None else b""
        self.query_params = query or {}

    async def body(self) -> bytes:
        return self._body


def response_json(response: Any) -> dict[str, Any]:
    return json.loads(bytes(response.body).decode("utf-8"))


async def invoke(module: Any, context: Any, method: str, path: str, body=None, query=None):
    response = await module.handle(Request(method, body, query), path, context)
    return response.status_code, response_json(response)


def main() -> None:
    module = load_module()
    assert module.MODULE_ID == "frozen-web-collector"
    assert module.API_SCHEMA_VERSION == 1

    try:
        module._validate_public_url("http://127.0.0.1/private", module._default_config())
        raise AssertionError("loopback URL was not rejected")
    except module.CollectorError as exc:
        assert exc.code == "SSRF_ADDRESS_REJECTED"

    previous_rw = os.environ.get("BLOB_READ_WRITE_TOKEN")
    previous_oidc = os.environ.pop("VERCEL_OIDC_TOKEN", None)
    previous_store = os.environ.pop("BLOB_STORE_ID", None)
    os.environ["BLOB_READ_WRITE_TOKEN"] = "vercel_blob_rw_abc123_verification"
    header_store = module.BlobStore()
    headers = header_store._headers()
    assert headers["x-api-version"] == "12"
    assert headers["x-vercel-blob-store-id"] == "abc123"
    assert headers["authorization"].startswith("Bearer vercel_blob_rw_")
    if previous_rw is None:
        os.environ.pop("BLOB_READ_WRITE_TOKEN", None)
    else:
        os.environ["BLOB_READ_WRITE_TOKEN"] = previous_rw
    if previous_oidc is not None:
        os.environ["VERCEL_OIDC_TOKEN"] = previous_oidc
    if previous_store is not None:
        os.environ["BLOB_STORE_ID"] = previous_store

    context = SimpleNamespace(
        module_version="1.0.0",
        module_sha256="a" * 64,
        source_branch="runtime",
        source_path="runtime_hot/web_snapshot_collector.py",
        activities=[],
    )
    context.activity = lambda kind, **fields: context.activities.append({"kind": kind, **fields})

    class EmptyStore:
        configured = False

        def describe(self):
            return {"backend": "vercel-blob", "configured": False, "access": "private"}

    original_store = module.BlobStore
    module.BlobStore = EmptyStore
    status_code, empty_status = asyncio.run(invoke(module, context, "GET", "status"))
    assert status_code == 200 and empty_status["storage"]["configured"] is False

    store = FakeStore(module)
    module.BlobStore = lambda: store
    module._validate_public_url = lambda url, config: (module._canonicalize(url), ["93.184.216.34"])

    class RedirectResponse:
        status_code = 302
        ok = True
        headers = {"location": "https://outside.example/reference"}

        def close(self):
            return None

    module._pinned_get = lambda *args, **kwargs: RedirectResponse()
    redirect_state = module._default_state()
    redirect_state["sources"] = [{"id": "source-redirect", "host": "example.com", "enabled": True}]
    try:
        module._fetch_document(redirect_state, "https://example.com/start")
        raise AssertionError("external redirect escaped the source-domain boundary")
    except module.CollectorError as exc:
        assert exc.code == "REDIRECT_DOMAIN_REJECTED"
    redirect_state["config"]["allowExternalDomains"] = True
    module._fetch_robots = lambda state, url: (True, 0.25, "robots-allowed", True)
    try:
        module._fetch_document(redirect_state, "https://example.com/start")
        raise AssertionError("redirect destination was fetched before its robots checkpoint")
    except module.CollectorError as exc:
        assert exc.code == "ROBOTS_REFRESH_REQUIRED"

    policy_state = module._default_state()
    policy_state["config"]["maxDepth"] = 4
    policy_state["sources"] = [{"id": "source-policy", "host": "example.com", "priority": 90, "policy": "shallow", "enabled": True}]
    assert module._enqueue_links(policy_state, "https://example.com/", ["/depth-two"], 2, "source-policy") == 0
    policy_state["sources"][0]["policy"] = "deep"
    assert module._enqueue_links(policy_state, "https://example.com/", ["/depth-two"], 2, "source-policy") == 1

    module._fetch_robots = lambda state, url: (True, 0.25, "robots-allowed", False)
    body_text = " ".join(
        f"Frozen collector evidence sentence {index} explains provenance quality immutable snapshots and safe browser operations."
        for index in range(1, 90)
    )
    html_body = (
        "<!doctype html><html lang='en'><head><title>Collector Evidence Guide</title></head>"
        f"<body><main><h1>Collector Evidence Guide</h1><p>{body_text}</p>"
        "<a href='/next'>Next bounded page</a></main></body></html>"
    ).encode("utf-8")
    module._fetch_document = lambda state, url: {
        "url": url,
        "addresses": ["93.184.216.34"],
        "status": 200,
        "contentType": "text/html; charset=utf-8",
        "headers": {"content-type": "text/html; charset=utf-8"},
        "body": html_body,
        "redirects": [],
        "fetchedAt": "2026-09-12T00:00:00Z",
    }

    code, payload = asyncio.run(invoke(module, context, "POST", "action", {
        "action": "configure",
        "config": {
            "minQuality": 0.10,
            "trainingMinQuality": 0.10,
            "minTextCharacters": 80,
            "maxPagesPerRun": 10,
            "maxDocuments": 10,
            "batchSize": 1,
            "minDelaySeconds": 0.25,
        },
    }))
    assert code == 200 and payload["state"]["config"]["batchSize"] == 1

    code, payload = asyncio.run(invoke(module, context, "POST", "action", {
        "action": "add-source",
        "url": "https://example.com/guide?utm_source=verification",
        "label": "Verified guide",
        "priority": 95,
        "policy": "balanced",
        "licenseNote": "Verification fixture; rights review still required.",
    }))
    assert code == 200 and payload["result"]["source"]["url"] == "https://example.com/guide"

    code, payload = asyncio.run(invoke(module, context, "POST", "action", {"action": "start"}))
    assert code == 200
    state = payload["state"]
    assert state["totals"]["documents"] == 1
    assert state["totals"]["trainingPending"] == 1
    assert state["frontierCount"] == 1
    snapshot_id = state["snapshotId"]
    document_sha = state["completed"][0]["contentSha256"]
    candidate_id = state["trainingQueue"][0]["id"]

    code, search = asyncio.run(invoke(module, context, "GET", "search", query={"q": "immutable provenance"}))
    assert code == 200 and search["count"] == 1
    assert search["results"][0]["contentSha256"] == document_sha

    code, payload = asyncio.run(invoke(module, context, "POST", "action", {"action": "pause"}))
    assert code == 200 and payload["state"]["status"] == "paused"
    code, payload = asyncio.run(invoke(module, context, "POST", "action", {"action": "seal"}))
    assert code == 200 and payload["state"]["status"] == "sealed"
    manifest = payload["result"]["manifest"]
    assert manifest["trainingReview"]["separateFromFrozenSnapshot"] is True
    manifest_without_hash = dict(manifest)
    expected_hash = manifest_without_hash.pop("manifestSha256")
    assert module._sha_bytes(module._compact_json(manifest_without_hash)) == expected_hash
    sealed_state, _etag = store.get_json(module.STATE_PATH)
    rebuilt = module._seal_payloads(
        sealed_state,
        context,
        sealed_state["sealIntentAt"],
        sealed_state["sealTotals"],
    )[2]
    assert module._compact_json(rebuilt) == module._compact_json(manifest)

    code, document = asyncio.run(invoke(module, context, "GET", "document", query={
        "snapshotId": snapshot_id,
        "sha256": document_sha,
    }))
    assert code == 200 and document["document"]["text"]
    frozen_before_review = store.objects[document["document"]["provenance"]["snapshotId"] and f"swrlz/collector/snapshots/{snapshot_id}/documents/{document_sha}.json"]

    code, rejected_review = asyncio.run(invoke(module, context, "POST", "action", {
        "action": "review",
        "candidateId": candidate_id,
        "decision": "accept",
    }))
    assert code == 400 and rejected_review["error"]["code"] == "RIGHTS_CONFIRMATION_REQUIRED"
    code, accepted_review = asyncio.run(invoke(module, context, "POST", "action", {
        "action": "review",
        "candidateId": candidate_id,
        "decision": "accept",
        "confirmRights": True,
        "note": "Fixture provenance checked.",
    }))
    assert code == 200 and accepted_review["result"]["review"]["rightsConfirmed"] is True
    assert store.objects[f"swrlz/collector/snapshots/{snapshot_id}/documents/{document_sha}.json"] == frozen_before_review
    assert f"swrlz/collector/training/accepted/{candidate_id}.json" in store.objects

    code, snapshots = asyncio.run(invoke(module, context, "GET", "snapshots"))
    assert code == 200 and snapshots["count"] == 1
    assert snapshots["snapshots"][0]["snapshotId"] == snapshot_id

    budget_state = module._default_state()
    budget_state["snapshotId"] = "web-20260912-000000-budget00"
    budget_state["status"] = "running"
    budget_state["sources"] = [{"id": "source-budget", "url": "https://example.com/guide", "priority": 90}]
    budget_state["config"]["minQuality"] = 0.1
    budget_state["config"]["trainingMinQuality"] = 0.1
    budget_state["config"]["minTextCharacters"] = 80
    budget_state["config"]["storageBudgetBytes"] = 5 * 1024 * 1024
    budget_state["totals"]["storedBytes"] = int(budget_state["config"]["storageBudgetBytes"] * 0.95) - 1_000
    before_paths = set(store.objects)
    try:
        module._process_item(store, budget_state, {
            "url": "https://example.com/guide",
            "depth": 0,
            "sourceId": "source-budget",
            "priority": 90,
        }, context)
        raise AssertionError("storage preflight did not stop the write")
    except module.CollectorError as exc:
        assert exc.code == "STORAGE_BUDGET_PREFLIGHT"
    assert set(store.objects) == before_paths

    module.BlobStore = original_store
    print("Frozen Web Snapshot Collector verification: PASS")
    print("Verified storage contract, SSRF rejection, lifecycle, checkpointing, search, immutable sealing, and separated rights-reviewed training.")


if __name__ == "__main__":
    main()
