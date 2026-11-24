#!/usr/bin/env python3
"""Read-only end-to-end live §C existing-project repair routing smoke.

Submits the user's verbatim prompt through the public Station transport using
an isolated disposable guest session. It NEVER signs in as another user, writes
GitHub files, or approves a repair. Guest mode must return explicit owner-source
unavailability rather than failure-evidence-required / new HTML generation.
"""
from __future__ import annotations
import http.cookiejar
import json
import time
import urllib.parse
import urllib.request
import uuid

BASE = "https://kamiloki-swyrlz.hf.space"
PROMPT = (
    "Inspect the existing interactive-3d-model-viewer project on GitHub. "
    "Identify why it fails to render correctly and repair it using your own coding model. "
    "Retrieve the actual source, generate targeted patches, validate them, and revise any failed patches until validation passes. "
    "Preserve the existing functionality and design. Do not regenerate the entire HTML page or rely on a predetermined repair script. "
    "Present the actual changes, validation results, and approval request. Once approved, commit, deploy, and verify that the project works."
)


def main():
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    request_id, thread_id = str(uuid.uuid4()), "swrlz-existing-repair-v5-" + str(uuid.uuid4())
    headers = {"User-Agent": "Swrlz-Repair-Route-Acceptance-v5", "Cache-Control": "no-cache"}
    payload = {
        "modelId": "700m", "prompt": PROMPT,
        "requestId": request_id, "threadId": thread_id,
        "profileId": "LALM", "timeZone": "UTC",
    }
    call = urllib.request.Request(
        BASE + "/api/lalm_station/send",
        method="POST",
        headers={**headers, "Content-Type": "application/json"},
        data=json.dumps(payload).encode("utf-8"))
    with opener.open(call, timeout=40) as response:
        ack = json.load(response)
        if response.status != 202 or ack.get("accepted") is not True:
            raise RuntimeError("LIVE_STATION_SEND_NOT_ACCEPTED")
    url = BASE + "/api/lalm_station/stream?" + urllib.parse.urlencode({"requestId": request_id})
    phases, texts, terminal = [], [], None
    started = time.monotonic()
    with opener.open(urllib.request.Request(url, headers=headers), timeout=200) as response:
        for line in response:
            if time.monotonic()-started > 180:
                raise RuntimeError("LIVE_REPAIR_STREAM_TIMEOUT")
            try:
                event = json.loads(line)
            except ValueError:
                continue
            kind = str(event.get("type") or "").upper()
            phase = str(event.get("phase") or "")
            if phase:
                phases.append(phase)
            if kind == "DELTA":
                texts.append(str(event.get("text") or ""))
            if kind in ("COMPLETED", "COMPLETE", "FAILED", "CANCELLED"):
                terminal = kind
                break
    output = "".join(texts)
    receipt = {
        "accepted": True, "terminal": terminal, "routeSourceUnavailable": "EXISTING_PROJECT_SOURCE_UNAVAILABLE" in phases,
        "oldEvidenceGate": "EVIDENCE_REQUIRED" in phases,
        "oldHandoff": "NOVERIFIEDHTMLCODEARTIFACT" in output,
        "genericFailureText": "need the failure evidence first" in output.lower(),
        "phases": phases[-20:], "textLength": len(output),
    }
    print("SWRLZ_LIVE_REPAIR_END_TO_END_RECEIPT", json.dumps(receipt), flush=True)
    if receipt["oldEvidenceGate"] or receipt["oldHandoff"] or receipt["genericFailureText"]:
        raise RuntimeError("OLD_GENERIC_CODER_STILL_INTERCEPTS_PROJECT")
    if not receipt["routeSourceUnavailable"]:
        raise RuntimeError("VERIFIED_PROJECT_SOURCE_BLOCKER_NOT_OBSERVED_IN_GUEST_PROBE")
    if terminal not in ("COMPLETED", "COMPLETE"):
        raise RuntimeError("GUEST_PROJECT_ROUTE_DID_NOT_COMPLETE")
    print("SWRLZ_LIVE_REPAIR_ROUTE_ACCEPTED_V5", flush=True)


if __name__ == "__main__":
    main()
