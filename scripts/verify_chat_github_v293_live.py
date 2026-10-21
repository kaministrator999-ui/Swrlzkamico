"""Read-only public HF acceptance for Chat v293 release provenance.

This script NEVER signs in, calls model-generation endpoints, mutates GitHub,
or claims verification of a Google/GitHub-authenticated user session.
It is intentionally usable with Python stdlib alone in GitHub Actions.
"""
from __future__ import annotations

import json
import os
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SPACE_ID = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
META = "https://huggingface.co/api/spaces/" + SPACE_ID
EXPECTED_SOURCE = "e90b2f395589da8cbfb0315a5c1db9f70e2afcb4"
EXPECTED_REVISION = "2b9475e46675932d2651d2c899ea6efdee629779"
EXPECTED_CHAT = "1.1.18"
AGENT = "swrlz-v293-readonly-release-acceptance/1.0"


def read(url: str, attempts: int = 3):
    """Bounded public GET. No cookies, sessions, tokens or authorization headers."""
    for attempt in range(attempts):
        req = Request(url, headers={"User-Agent": AGENT, "Cache-Control": "no-cache"})
        try:
            with urlopen(req, timeout=25) as response:
                return response.status, response.read(300000).decode("utf-8", "replace")
        except HTTPError as error:
            if error.code not in (502, 503, 504) or attempt == attempts - 1:
                return error.code, error.read(4096).decode("utf-8", "replace")
        except (OSError, URLError):
            if attempt == attempts - 1:
                raise
        time.sleep(3 * (attempt + 1))
    raise AssertionError("HTTP retry budget exhausted")


def checkpoint(label: str, **values):
    # Public, bounded receipts only: no response bodies or personal data logged.
    print(json.dumps({"checkpoint": label, **values}, sort_keys=True), flush=True)


def main():
    status, response = read(META)
    assert status == 200, ("space-metadata-unavailable", status)
    metadata = json.loads(response)
    sha = str(metadata.get("sha") or "")
    assert sha == EXPECTED_REVISION, ("wrong-live-space-revision", sha, EXPECTED_REVISION)
    checkpoint("hf-space-revision", status="PASS", spaceRevision=sha, sourceCommit=EXPECTED_SOURCE)

    status, html = read(BASE + "/", attempts=5)
    assert status == 200, ("chat-unavailable", status)
    assert re.search(r"<html\b", html, re.I), "Chat HTML was not served"
    assert re.search(
        r'<meta\s+name="swrlz-chat-version"\s+content="' + re.escape(EXPECTED_CHAT) + r'"',
        html,
        re.I,
    ), "Expected canonical Chat version metadata not served"
    checkpoint("chat-html", status="PASS", httpStatus=status, chatVersion=EXPECTED_CHAT)

    status, body = read(BASE + "/api/hf/models")
    assert status == 200, ("model-catalog-unavailable", status)
    catalog = json.loads(body)
    assert isinstance(catalog.get("models"), list) and catalog["models"], "Model catalog empty"
    checkpoint("model-catalog", status="PASS", httpStatus=status, modelCount=len(catalog["models"]))

    # Deliberate unauthenticated probes; never forge owner/session or request a write.
    for path, name in (
        ("/api/account/me", "anonymous-account-isolation"),
        ("/api/github/status", "anonymous-github-status-isolation"),
        ("/api/github/start?access=public-write", "anonymous-github-oauth-isolation"),
    ):
        status, _ = read(BASE + path, attempts=2)
        assert status == 401, (name, "expected-not-authenticated-401", status)
        checkpoint(name, status="PASS", httpStatus=status)

    checkpoint("scope", status="PARTIAL", note="No authenticated GitHub read or Android UI acceptance asserted")


if __name__ == "__main__":
    main()
