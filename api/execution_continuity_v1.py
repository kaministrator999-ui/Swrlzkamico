"""Source-grounded execution continuity for §C; no increased decoder limits.

The per-request controller consumes existing persisted draft checkpoint events and
continues the *same* source with the current coder's built-in resume capability.
Only one active iterator at a time. No tools, writes or permissions are inferred.
"""
from __future__ import annotations
import hashlib
import re

READ_ONLY = re.compile(
    r"\b(?:inspect|analy[sz]\w*|investigat\w*|diagnos\w*|"
    r"check|report|compare|review|verify|look\s+at)\b", re.I)
NO_MUTATION = re.compile(
    r"\b(?:do\s+not|don't|without|no)\b"
    r".{0,110}\b(?:creat\w*|edit\w*|modif\w*|chang\w*|"
    r"writ\w*|repair\w*|mutat\w*)\b", re.I)
MAX_BYTES = 240 * 1024  # Existing source-checkpoint storage contract.


def read_only(payload):
    """A grounded inspection request is not a programming deliverable."""
    if not isinstance(payload, dict) or not isinstance(payload.get("activeHtmlProject"), dict):
        return False
    prompt = str(payload.get("receivedText") or payload.get("prompt") or "")
    return bool(READ_ONLY.search(prompt) and NO_MUTATION.search(prompt))


def eligible(payload):
    """Never bypass a GitHub mutation route or an explicit read-only request."""
    return (isinstance(payload, dict)
            and not payload.get("githubSourceChangeTask")
            and not payload.get("sourceChangeMode")
            and not read_only(payload))


def _checkpoint(value):
    if not isinstance(value, dict) or value.get("schema") != "swrlz-long-code-checkpoint-v1":
        return None
    source = value.get("source")
    if not isinstance(source, str):
        return None
    raw = source.encode("utf-8")
    if not raw or len(raw) > MAX_BYTES:
        return None
    if hashlib.sha256(raw).hexdigest() != value.get("sourceSha256"):
        return None
    return value


def _stopped(payload):
    check = payload.get("_cancelCheck")
    if callable(check):
        try:
            return bool(check())
        except Exception:
            return True  # Fail closed on broken cancellation.
    return False


def stream(payload, coder, initial):
    """Resume checkpointed work automatically while progress is demonstrable.

    Existing Station persists CODE_OUTPUT_CHECKPOINT and only promotes
    accepted drafts. Reruns consume that exact checkpoint; a repeated SHA
    twice, an invalid checkpoint, user Stop, or a real platform failure ends
    the turn without claiming completed or validated code.
    """
    if not eligible(payload):
        yield from initial
        return
    current = initial
    seen = {}
    while True:
        checkpoint = None
        completed = False
        producer = iter(current)
        try:
            for event in producer:
                if _stopped(payload):
                    yield {"type": "CANCELLED", "phase": "CANCELLED"}
                    return
                if isinstance(event, dict) and event.get("type") == "CODE_OUTPUT_CHECKPOINT":
                    checkpoint = _checkpoint(event.get("checkpoint"))
                    if checkpoint is None:
                        yield {"type": "STATUS", "phase": "CODE_CHECKPOINT_INVALID",
                               "reason": "The source checkpoint failed integrity validation."}
                        yield {"type": "COMPLETED", "phase": "PARTIAL",
                               "outputIncomplete": True, "blocker": "INVALID_CHECKPOINT"}
                        return
                    # Forward to the existing Station checkpoint persistence
                    # before starting another generation; never manufacture success.
                    yield event
                    break
                if isinstance(event, dict) and event.get("type") in ("COMPLETED", "CANCELLED", "FAILED"):
                    completed = True
                yield event
        finally:
            close = getattr(producer, "close", None)
            if callable(close):
                close()
        if checkpoint is None or completed:
            return
        if _stopped(payload):
            yield {"type": "CANCELLED", "phase": "CANCELLED"}
            return
        key = checkpoint["sourceSha256"]
        seen[key] = seen.get(key, 0) + 1
        if seen[key] >= 2:
            yield {"type": "STATUS", "phase": "CODE_CONTINUATION_BLOCKED",
                   "reason": "Two consecutive saved checkpoints contain the same source. "
                             "No more identical retries will be attempted."}
            yield {"type": "COMPLETED", "phase": "PARTIAL",
                   "outputIncomplete": True, "blocker": "NO_FORWARD_PROGRESS"}
            return
        # This updates only this per-turn payload. The worker's original user
        # prompt and same-thread source identity are unchanged. Station sees
        # this binding when it receives CODE_OUTPUT_FINISHED.
        payload["codeContinuation"] = checkpoint
        yield {"type": "STATUS", "phase": "CODE_AUTO_CONTINUING",
               "reason": "Resuming the existing unverified draft automatically.",
               "sourceSha256": key, "sourceBytes": len(checkpoint["source"].encode("utf-8")),
               "segmentsCompleted": checkpoint.get("segmentsCompleted")}
        current = coder(payload)
