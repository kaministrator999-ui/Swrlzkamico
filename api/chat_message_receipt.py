from __future__ import annotations

import json

from fastapi import Request

from api import chat
from api.chat_client_debug import _authorized_chat_ingress, _message_receipt

_INSTALLED = False


def install() -> None:
    """Attach the private message receipt to the mounted Chat action owner.

    The public /api/chat request may be redirected to /api/chat/ before the
    mounted Chat application owns it. Wrapping chat._post_action places the
    receipt after that routing boundary and before generation starts.
    """
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    original_post_action = chat._post_action

    async def post_action_with_receipt(request: Request, action: str):
        normalized_action = str(action or "stream").strip().lower()
        if normalized_action == "stream" and _authorized_chat_ingress(request):
            try:
                raw = await request.json()
            except Exception:
                raw = {}
            if isinstance(raw, dict):
                receipt = _message_receipt(raw, request)
                if receipt is not None:
                    receipt["receiptBoundary"] = "MOUNTED_CHAT_POST_ACTION"
                    receipt["generationStarted"] = False
                    print(
                        "SWRLZ_CHAT_MESSAGE "
                        + json.dumps(receipt, separators=(",", ":"), ensure_ascii=True),
                        flush=True,
                    )
        return await original_post_action(request, action)

    chat._post_action = post_action_with_receipt
