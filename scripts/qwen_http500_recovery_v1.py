"""Retry one transient native HTTP 500 before any completion events escape.

A failed source, code, research or lyric generation is NEVER fabricated or
replaced; caller still sees the second error if no recovery is possible.
Cancellation is authoritative; no retry after Stop. Cache is disabled once
on retry to avoid retaining a stale llama.cpp prompt-cache state.
"""
from __future__ import annotations

def native_stream_once_retry(payload, open_response, is_cancelled, on_retry=None):
    """Yield raw SSE bytes. Retry one pre-body HTTP500, not partial replies."""
    if not isinstance(payload,dict) or not callable(open_response) or not callable(is_cancelled):
        raise ValueError("Invalid native completion retry contract")
    for attempt in range(2):
        if is_cancelled():
            return
        request_payload=payload if attempt==0 else {**payload,"cache_prompt":False}
        any_body=False
        try:
            with open_response(request_payload) as response:
                for raw in response:
                    if is_cancelled():
                        return
                    if raw:
                        # Once bytes escaped, a restart risks doubled text.
                        any_body=True
                    yield raw
            return
        except RuntimeError as exc:
            if (attempt==0 and not any_body and
                    str(exc)=="QWEN35_HTTP_500" and not is_cancelled()):
                if callable(on_retry):
                    on_retry()
                continue
            raise
