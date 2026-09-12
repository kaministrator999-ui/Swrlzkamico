#!/usr/bin/env python3
"""Deterministic verification for the stable Frozen Web Collector host."""
from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request

ROOT = Path(__file__).resolve().parents[1]
host = importlib.import_module("api.collector_host")


class FakeModule:
    MODULE_ID = host.MODULE_ID
    API_SCHEMA_VERSION = host.API_SCHEMA_VERSION

    @staticmethod
    async def handle(*, request: Request, path: str, context: Any):
        return {"ok": True, "path": path, "version": context.module_version, "source": context.source_branch}

    @staticmethod
    def inspect_module():
        return {
            "moduleId": host.MODULE_ID,
            "apiSchemaVersion": host.API_SCHEMA_VERSION,
            "stateSchemaVersion": 1,
            "storage": {
                "backend": "vercel-blob",
                "configured": True,
                "access": "private",
                "authoritativeState": "swrlz/collector/control/state.json",
                "ephemeralTmpUsedAsAuthority": False,
                "storeIdSuffix": "secret",
            },
        }


class FakeServer:
    def __init__(self) -> None:
        self.app = FastAPI()
        self.CAPABILITIES: dict[str, Any] = {}
        self.events: list[tuple[str, dict[str, Any]]] = []

    @staticmethod
    def auth(request: Request) -> bool:
        return request.headers.get("x-swrlz-admin-token") == "verification-secret"

    def activity(self, event: str, **fields: Any) -> None:
        self.events.append((event, fields))

    def _write_server_state(self) -> None:
        return None


def make_request(*, token: str | None = None, body: bytes = b"", content_length: int | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if token is not None:
        headers.append((b"x-swrlz-admin-token", token.encode()))
    if content_length is not None:
        headers.append((b"content-length", str(content_length).encode()))
    delivered = False

    async def receive():
        nonlocal delivered
        if delivered:
            return {"type": "http.request", "body": b"", "more_body": False}
        delivered = True
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST" if body or content_length else "GET",
        "scheme": "https",
        "path": "/api/collector",
        "raw_path": b"/api/collector",
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 443),
    }
    return Request(scope, receive)


async def run() -> None:
    version_data = b"ID=frozen-web-collector\nVERSION=1.0.0\n"
    assert host._parse_version(version_data) == "1.0.0"

    source = b'''MODULE_ID="frozen-web-collector"\nAPI_SCHEMA_VERSION=1\nasync def handle(**kwargs): return {"ok": True}\ndef inspect_module(): return {"ok": True}\n'''
    loaded = host._load_module(source, hashlib.sha256(source).hexdigest())
    assert loaded.MODULE_ID == host.MODULE_ID
    assert callable(loaded.handle) and callable(loaded.inspect_module)

    receipt = {
        "moduleId": host.MODULE_ID,
        "moduleVersion": "1.0.0",
        "apiSchemaVersion": 1,
        "source": "github-runtime",
        "sourceBranch": "runtime",
        "sourcePath": host.COLLECTOR_SOURCE,
        "sourceSha256": "a" * 64,
        "versionSource": host.VERSION_SOURCE,
        "versionSourceSha256": "b" * 64,
        "lastSuccessAt": 1.0,
        "lastError": None,
        "refreshSeconds": host.REFRESH_SECONDS,
        "deploymentRequiredForRuntimeChanges": False,
    }
    host._refresh = lambda force=False: (FakeModule(), receipt)
    server = FakeServer()
    host.install(server)
    root_endpoint = next(route.endpoint for route in server.app.routes if getattr(route, "path", None) == "/api/collector")
    route_endpoint = next(route.endpoint for route in server.app.routes if getattr(route, "path", None) == "/api/collector/{subpath:path}")

    readiness = await route_endpoint(make_request(), "readiness")
    readiness_payload = json.loads(readiness.body.decode("utf-8"))
    assert readiness.status_code == 200 and readiness_payload["ready"] is True
    assert readiness_payload["module"]["id"] == host.MODULE_ID
    assert readiness_payload["storage"]["configured"] is True
    assert "storeIdSuffix" not in readiness_payload["storage"]

    unauthorized = await root_endpoint(make_request())
    assert unauthorized.status_code == 401

    oversized_header = await root_endpoint(make_request(token="verification-secret", content_length=host.MAX_REQUEST_BYTES + 1))
    assert oversized_header.status_code == 413

    oversized_body = await root_endpoint(make_request(token="verification-secret", body=b"x" * (host.MAX_REQUEST_BYTES + 1)))
    assert oversized_body.status_code == 413

    authorized = await root_endpoint(make_request(token="verification-secret"))
    payload = json.loads(authorized.body.decode("utf-8"))
    assert authorized.status_code == 200
    assert payload == {"ok": True, "path": "status", "version": "1.0.0", "source": "runtime"}
    assert authorized.headers["x-swrlz-collector-branch"] == "runtime"
    assert authorized.headers["x-swrlz-collector-version"] == "1.0.0"

    capability = server.CAPABILITIES["frozen-web-collector-host"]
    assert capability["authentication"].startswith("SWRLZ admin token")
    assert capability["deploymentRequiredForRuntimeChanges"] is False

    print("Stable Frozen Web Collector host verification: PASS")
    print("Verified fixed contract, safe readiness, Admin rejection, actual/header body limits, dispatch, and source receipts")


if __name__ == "__main__":
    asyncio.run(run())
