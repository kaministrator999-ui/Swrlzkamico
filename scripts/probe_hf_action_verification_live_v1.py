#!/usr/bin/env python3
"""Anonymous read-only §C action-check acceptance for the exact deployed revision."""
from __future__ import annotations
import json
import re
import time
import uuid

import requests
from huggingface_hub import HfApi
from probe_hf_http500_feedback_live_v1 import BASE, send_and_wait

SPACE = "kamiloki/Swyrlz"
EXPECTED = "cf93df2865b57fb52163f05c45404e44276f786b"


def log(event, **info):
    print("ACTION_CHECK_GUEST " + json.dumps(
        {"event": event, **info}, sort_keys=True), flush=True)


def check_runtime():
    api = HfApi()
    deadline = time.monotonic() + 480
    while time.monotonic() < deadline:
        head = str(api.repo_info(SPACE, repo_type="space").sha)
        if head != EXPECTED:
            raise RuntimeError("Space revision moved; refuse unpinned test")
        runtime = api.get_space_runtime(SPACE)
        state = str(runtime.stage).upper()
        served = str((runtime.raw or {}).get("sha") or "")
        log("runtime", state=state, sourceMatches=(served == EXPECTED))
        if "RUNNING" in state and served == EXPECTED:
            return
        time.sleep(12)
    raise TimeoutError("Expected deployed source not serving")


def main():
    check_runtime()
    session = requests.Session()
    me = session.get(BASE + "/api/account/me", timeout=25)
    if me.ok and (me.json() or {}).get("user"):
        raise RuntimeError("Not anonymous; abort")
    sync = session.get(BASE + "/api/lalm_station/sync", timeout=30)
    if sync.status_code != 200:
        raise RuntimeError("Live guest station not ready")
    thread = "action-check-guest-" + uuid.uuid4().hex[:16]
    # Entirely fictional, no user account or personal files.
    prompt = (
        "I'm trying to find better-paid software QA work. I already have a "
        "software QA resume and two working HTML sites I built. What do you "
        "think I should do next to pursue a technical role?"
    )
    reply, receipt = send_and_wait(session, thread, prompt)
    low = reply.casefold()
    unsupported_file_claim = bool(re.search(
        r"\b(?:i checked|i opened|i accessed|i reviewed)\s+(?:your|the)\s+"
        r"(?:personal\s+)?(?:files|library|drive|resumes|repositories)\b", low))
    missing_assets_claim = bool(re.search(
        r"\byou (?:do not|don't|have no)\s+(?:have\s+)?(?:a |any )?"
        r"(?:resume|website|projects)\b", low))
    log("result", replyChars=len(reply),
        elapsedMs=receipt["elapsedMs"], phases=receipt.get("phases", []),
        unsupportedFileClaim=unsupported_file_claim,
        deniedExistingAssets=missing_assets_claim,
        snippet=reply[:230])
    if unsupported_file_claim or missing_assets_claim or len(reply.strip()) < 45:
        raise AssertionError("Live response invented an inventory result or lost context")
    log("PASS", source=EXPECTED, scope="anonymous-career-portfolio-advice",
        note="One live response; does not establish universal action-check reliability")


if __name__ == "__main__":
    main()
