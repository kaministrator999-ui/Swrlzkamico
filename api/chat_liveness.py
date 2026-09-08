"""Chat stream liveness tuning for Server 2.2.8.

Long cold R39 prefills can run for tens of seconds before the first DELTA. Emit a
transport heartbeat every three seconds while the engine iterator is blocked so
mobile/proxy connections receive frequent bytes without changing inference state.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

import api.chat_extensions as ext

HEARTBEAT_SECONDS = 3.0


def _heartbeat_events(source):
    iterator = iter(source)
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="swrlz-r39") as pool:
        while True:
            future = pool.submit(next, iterator)
            while True:
                try:
                    raw = future.result(timeout=HEARTBEAT_SECONDS)
                    break
                except FutureTimeout:
                    yield {
                        "type": "STATUS",
                        "phase": "COMPUTE_HEARTBEAT",
                        "reason": "Local R39 compute is still active; keeping the response stream alive.",
                    }
            yield raw


def install(server) -> None:
    ext._heartbeat_events = _heartbeat_events
    server.CAPABILITIES["chat-stream-liveness"] = {
        "kind": "runtime-transport",
        "ready": True,
        "heartbeatSeconds": HEARTBEAT_SECONDS,
        "inferenceStateMutation": False,
        "detail": "Emits transport-only status heartbeats during long R39 compute waits to reduce idle stream detachment risk.",
    }
