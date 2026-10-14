"""Compact, evidence-based progress receipts for §wyrlz Chat (v238).

Only observed Station statuses become timeline entries. No hidden reasoning,
untrusted code content, auth tokens, precise location or guessed progress
percentages are included. This projection is also saved with each response.
"""
from __future__ import annotations

import re
import time

SCHEMA = "swrlz-chat-activity-timeline-v1"
MAX_EVENTS = 64
_PHASE = re.compile(r"^[A-Z][A-Z0-9_]{1,79}$")
_REDACT = re.compile(
    r"(?i)(bearer\s+\S+|gh[opusr]_[A-Za-z0-9_]{12,}|"
    r"(?:access[_-]?token|api[_-]?key|password|secret)\s*[:=]\s*\S+|"
    r"https?://\S+|(?:-?\d{1,3}\.\d{5,})\s*,\s*(?:-?\d{1,3}\.\d{5,}))"
)
_SKIP = frozenset({"RESPONSE_COGNITION", "MEMORY_CANDIDATE", "DIAGNOSTIC_READY",
                   "GENERATION_TELEMETRY"})


def mark_new(statuses, start, at_unix_ms=None):
    """Timestamp only genuinely new events, at the server observation boundary."""
    if not isinstance(statuses, list):
        return
    moment = int(at_unix_ms or time.time() * 1000)
    for item in statuses[max(0, int(start)):]:
        if isinstance(item, dict) and "atUnixMs" not in item:
            item["atUnixMs"] = moment


def _clean(value, limit=110):
    source = str(value or "").replace("\n", " ").replace("\r", " ")
    source = _REDACT.sub("[redacted]", source)
    source = re.sub(r"[\x00-\x1f\x7f<>\\]", " ", source)
    return " ".join(source.split())[:limit]


def project(statuses, accepted_at=None, request_id=None):
    """Return safe chronology and explicit omission count.

    No synthetic completion or success event is fabricated. A missing clock
    stays null rather than being estimated from the wall clock at read time.
    """
    accepted = int(accepted_at) if isinstance(accepted_at, (int, float)) and accepted_at > 0 else None
    rows = []
    for index, item in enumerate(statuses if isinstance(statuses, list) else []):
        if not isinstance(item, dict):
            continue
        phase = str(item.get("phase") or "").upper()
        if not _PHASE.fullmatch(phase) or phase in _SKIP:
            continue
        reason = _clean(item.get("reason"), 130)
        timestamp = item.get("atUnixMs")
        timestamp = int(timestamp) if isinstance(timestamp, (int, float)) and timestamp > 0 else None
        # At most one row per contiguous repetition of an identical activity.
        if rows and (rows[-1]["phase"], rows[-1]["reason"]) == (phase, reason):
            continue
        rows.append({
            "index": index + 1,
            "phase": phase,
            "reason": reason,
            "atUnixMs": timestamp,
        })
    omitted = max(0, len(rows) - MAX_EVENTS)
    events = rows if not omitted else rows[:1] + rows[-(MAX_EVENTS - 1):]
    receipt = {"schema": SCHEMA, "acceptedAtUnixMs": accepted,
               "events": events, "omittedCount": omitted}
    if request_id:
        receipt["requestId"] = str(request_id)[:160]
    return receipt
