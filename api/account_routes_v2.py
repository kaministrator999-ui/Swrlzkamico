from __future__ import annotations

from typing import Any

from api import account_routes as _base


async def _enqueue_generation(payload: dict[str, Any], *, request_id: str) -> None:
    """Publish durable generation using the public Vercel Python Queues API.

    request_id is already persisted as the idempotent job key in Redis before this call.
    Vercel Queues provides at-least-once delivery; the worker therefore re-checks terminal
    state before doing model work.
    """
    from vercel.queue import send

    await send(_base.QUEUE_TOPIC, payload)


def install(server) -> None:
    _base._enqueue_generation = _enqueue_generation
    _base.install(server)
