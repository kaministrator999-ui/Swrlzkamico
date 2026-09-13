"""Bounded production Blob verification using the exact published collector.

This is a storage/engine check, not a claim of browser or API authentication.
Only an empty configuration save is allowed. No saved contents are printed.
"""
from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import os
import re
import sys
import types
from pathlib import Path

import requests

ORIGIN = "https://swrlzkamico-o3nu.vercel.app"
SOURCE_PATH = "runtime_hot/web_snapshot_collector.py"


def load_engine(expected):
    digest = expected["engineSha256"]
    commit = expected["runtimeCommit"]
    assert re.fullmatch(r"[a-f0-9]{64}", digest), "Invalid expected source hash."
    assert re.fullmatch(r"[a-f0-9]{40}", commit), "Invalid pinned source commit."
    readiness_response = requests.get(
        ORIGIN + "/api/collector/readiness", timeout=(5, 30),
        headers={"Cache-Control": "no-store"}, allow_redirects=False,
    )
    assert readiness_response.status_code == 200, "Production readiness failed."
    readiness = readiness_response.json()
    assert readiness.get("ok") is True, "Production collector is not ready."
    assert readiness["host"]["sourceSha256"] == digest, "Live engine differs from pinned source."
    assert readiness["module"]["version"] == expected["collectorVersion"], "Live collector version changed."
    assert readiness["storage"]["configured"] is True, "Production storage is not configured."
    assert readiness["storage"]["access"] == "private", "Production storage is not private."
    assert readiness["host"]["deploymentRequiredForRuntimeChanges"] is False, "Runtime update boundary changed."
    response = requests.get(
        f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{commit}/{SOURCE_PATH}",
        timeout=(5, 30), allow_redirects=False,
    )
    assert response.status_code == 200, "Pinned engine download failed."
    assert len(response.content) <= 900_000, "Pinned engine is too large."
    assert hashlib.sha256(response.content).hexdigest() == digest, "Pinned engine hash mismatch."
    module = types.ModuleType("verified_collector_engine")
    exec(compile(response.content, SOURCE_PATH, "exec"), module.__dict__)
    assert module.MODULE_ID == "frozen-web-collector", "Wrong collector module."
    assert module.STATE_PATH == "swrlz/collector/control/state.json", "Wrong state path."
    return module


async def verify_storage(expected, engine):
    store = engine.BlobStore()
    store.require()
    before, etag = engine._load_state(store)
    assert etag, "Expected existing private state with a strong write version."
    assert before["status"] != "running", "Collection is running; no verification write attempted."
    assert not before.get("sealIntentAt") or before["status"] == "sealed", "Sealing is active; no verification write attempted."
    saved = copy.deepcopy(before)
    context = types.SimpleNamespace(
        module_version=expected["collectorVersion"],
        module_sha256=expected["engineSha256"],
        source_branch="runtime", source_path=SOURCE_PATH,
        activity=lambda *args, **kwargs: None,
    )

    class EmptyConfigurationRequest:
        async def body(self):
            return b'{"action":"configure","config":{}}'

    # This is the same action implementation used by the deployed host, with the
    # same previously read version. A concurrent change must fail conditionally.
    payload = await engine._action(EmptyConfigurationRequest(), store, saved, etag, context)
    assert payload["ok"] is True, "The exact collector action failed."
    assert saved["stateRevision"] == before["stateRevision"] + 1, "Revision did not advance once."
    for key in set(before) | set(saved):
        if key not in {"stateRevision", "updatedAt", "events"}:
            assert before.get(key) == saved.get(key), "Saved collection content changed."
    # A new store/session proves persistence independently of the action's readback.
    reloaded, _ = engine._load_state(engine.BlobStore())
    assert reloaded == saved, "Saved state did not persist on a fresh read."
    return {
        "ok": True, "scope": "production-blob-exact-engine",
        "collectorVersion": expected["collectorVersion"],
        "engineSha256": expected["engineSha256"],
        "beforeRevision": before["stateRevision"],
        "savedRevision": saved["stateRevision"],
        "reloadedRevision": reloaded["stateRevision"],
        "configurationUnchanged": True, "collectionContentUnchanged": True,
        "statePersisted": True, "collectionStatus": reloaded["status"],
        "documents": reloaded["totals"]["documents"],
        "sources": len(reloaded["sources"]),
        "trainingAccepted": reloaded["totals"]["trainingAccepted"],
    }


def main():
    try:
        expected = json.loads(Path(".collector/VERIFY_REQUEST.json").read_text("utf-8"))
        engine = load_engine(expected)
        print(json.dumps(asyncio.run(verify_storage(expected, engine)), separators=(",", ":")))
    except Exception as error:
        # Never print a traceback, private state, provider credentials or URLs.
        message = str(error)
        for value in sorted((v for v in os.environ.values() if len(v) >= 8), key=len, reverse=True):
            message = message.replace(value, "[redacted]")
        print(json.dumps({"ok": False, "scope": "production-blob-exact-engine", "error": message[:500]}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
