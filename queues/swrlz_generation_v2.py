from __future__ import annotations

from vercel.queue import subscribe

from queues.swrlz_generation import generate_swrlz_response as _legacy_handler


@subscribe(topic="swrlz-generation")
async def generate_swrlz_response(payload) -> None:
    """Vercel subscriber adapter.

    The public Python queue subscriber receives the decoded payload directly. The original
    worker was authored against an older Message wrapper shape, so adapt it here while the
    durable execution body remains unchanged.
    """
    class _Message:
        def __init__(self, value):
            self.payload = value

    await _legacy_handler.__wrapped__(_Message(payload)) if hasattr(_legacy_handler, "__wrapped__") else await _legacy_handler(_Message(payload))
