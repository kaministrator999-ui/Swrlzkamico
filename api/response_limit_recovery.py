"""Bounded model-answer continuation helpers for §C.

Local-only: these functions never research, mutate account data, or publish files.
They preserve streamed output instead of restarting it when a factual answer
reaches its genuine model output-token limit.
"""
from __future__ import annotations


def trim_overlap(previous: str, continuation: str, *, max_scan: int = 1800) -> str:
    """Drop only demonstrated duplicate prefix; never rewrite earlier output."""
    if not continuation:
        return ""
    previous = str(previous or "")
    current = str(continuation).lstrip("\n")
    if not current:
        return ""
    if current in previous[-max_scan:]:
        return ""
    if len(previous) > 100 and len(current) > 72 and current[:72] == previous[:72]:
        # A restarted answer is not a continuation.
        return ""
    scan = min(len(previous), len(current), max_scan)
    for size in range(scan, 15, -1):
        if previous.endswith(current[:size]):
            return current[size:]
    return current


def should_continue_research(finish_reason: str, payload: object, programming: object,
                             source_change_mode: str = "", longform: bool = False) -> bool:
    """Only ordinary sourced answers; code, edits and longform have other contracts."""
    evidence = payload.get("onlineContext") if isinstance(payload, dict) else None
    return (
        finish_reason == "length"
        and isinstance(evidence, dict)
        and int(evidence.get("resultCount") or 0) > 0
        and not source_change_mode
        and not longform
        and isinstance(programming, dict)
        and not programming.get("codingTask")
    )


def continuation_prompt() -> str:
    return (
        "Continue your immediately preceding factual answer from where it stopped. "
        "Do not restart, repeat earlier sentences, or introduce new research. "
        "Use only the same verified sources and clearly distinguish unsupported facts. "
        "Finish the remaining requested points in no more than 110 words and end."
    )
