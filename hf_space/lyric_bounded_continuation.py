"""Bounded model-authored continuation for exact-line original verses.

Decode until the requested number of complete, nonempty authored lines,
then stop consuming tokens at that line boundary. This is an explicit output
stop condition, not post-generation editing, artificial padding, or an
opportunity to drop unsafe duplicated lines. Formal validation still owns
acceptance and always sees every line returned by this bounded decoder.

No source lyrics, prompts, candidate text or private user data in telemetry.
"""
from __future__ import annotations

import time
from typing import Any


def _nth_completed_line_end(text: str, wanted: int) -> int | None:
    """Exclusive character offset immediately after the Nth nonblank LF line."""
    nonblank = 0
    start = 0
    for index, ch in enumerate(text):
        if ch != "\n":
            continue
        if text[start:index].strip():
            nonblank += 1
            if nonblank >= wanted:
                return index + 1
        start = index + 1
    return None


def buffered_bounded_lyric_continuation(
    model: Any,
    messages: list[dict[str, Any]],
    max_tokens: int,
    temperature: float,
    *,
    max_lines: int,
) -> tuple[str, dict[str, Any]]:
    """Capture bounded model output, never synthesize or alter a lyrical line.

    If the model has already emitted extra tokens within a streaming chunk,
    the explicit *generation* cap treats them as beyond the output boundary.
    Non-lyrical material, repeated lines and malformed candidates still fail
    the separate existing continuation validator.
    """
    limit = max(1, min(8, int(max_lines)))
    started = time.perf_counter()
    first_token_at = None
    chunks = 0
    buffer = ""
    stop_at = None
    for part in model.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,
    ):
        choices = part.get("choices") or []
        delta = (choices[0].get("delta") or {}).get("content") if choices else None
        if not delta:
            continue
        if first_token_at is None:
            first_token_at = time.perf_counter()
        buffer += str(delta)
        chunks += 1
        stop_at = _nth_completed_line_end(buffer, limit)
        if stop_at is not None:
            buffer = buffer[:stop_at]
            break
    # A final unterminated line is still model-authored. Preserve it for
    # validation, where wrong line count will be rejected normally.
    ended = time.perf_counter()
    return buffer, {
        "durationMs": round((ended-started)*1000, 3),
        "firstTokenLatencyMs": round((first_token_at-started)*1000, 3)
        if first_token_at is not None else None,
        "deltaChunks": chunks,
        "stoppedAtLineBoundary": stop_at is not None,
        "requestedSegmentLines": limit,
        "returnedSegmentLines": len([line for line in buffer.splitlines() if line.strip()]),
    }
