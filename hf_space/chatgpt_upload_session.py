"""Bounded, Google-owned temporary upload assembly for large ZIP imports.

Transport sessions are ephemeral. Imported conversation records are durable
and encrypted by chatgpt_archive.py; staging is never a permanent archive.
"""
from __future__ import annotations
import os
import tempfile
import threading
import time
import uuid
from fastapi import HTTPException
import account_chat_store
from chatgpt_archive import MAX_ZIP

CHUNK_SIZE = 2 * 1024 * 1024
MAX_SESSIONS = 4
SESSION_TTL = 3600
_lock = threading.RLock()
_pending = {}


def _cleanup():
    now = time.time()
    for token, state in list(_pending.items()):
        if now - state["created"] > SESSION_TTL:
            _pending.pop(token, None)
            try: os.unlink(state["path"])
            except FileNotFoundError: pass


def begin(owner, size):
    account_chat_store._chat_key(owner)
    if not isinstance(size, int) or not 0 < size <= MAX_ZIP:
        raise HTTPException(413, "ZIP upload size must be within the configured limit")
    with _lock:
        _cleanup()
        # One upload per verified account at a time. Starting again intentionally
        # discards only the previous incomplete transport file, never saved chats.
        for token, state in list(_pending.items()):
            if state["owner"] == owner:
                _pending.pop(token, None)
                try: os.unlink(state["path"])
                except FileNotFoundError: pass
        if len(_pending) >= MAX_SESSIONS:
            raise HTTPException(429, "Too many imports being uploaded; retry when a slot is available")
        with tempfile.NamedTemporaryFile(prefix="swrlz-chatgpt-", suffix=".zip", delete=False) as f:
            path = f.name
        token = uuid.uuid4().hex
        _pending[token] = {"owner": owner, "size": size, "path": path,
                           "received": 0, "created": time.time()}
    return {"uploadId": token, "chunkSize": CHUNK_SIZE, "received": 0}


def progress(owner, token):
    """An upload marker is opaque and only readable by its original Google owner."""
    with _lock:
        _cleanup()
        state = _pending.get(str(token))
        if state is None or state["owner"] != owner:
            raise HTTPException(404, "Upload session expired or belongs to another account")
        return {"uploadId": str(token), "received": state["received"],
                "size": state["size"], "chunkSize": CHUNK_SIZE}


def append(owner, token, offset, chunk):
    with _lock:
        _cleanup()
        state = _pending.get(str(token))
        if state is None or state["owner"] != owner:
            raise HTTPException(404, "Upload session not found; restart this ZIP import")
        if not isinstance(chunk, bytes) or not chunk or len(chunk) > CHUNK_SIZE:
            raise HTTPException(413, "Upload chunk too large or empty")
        if not isinstance(offset, int) or offset < 0 or offset + len(chunk) > state["size"]:
            raise HTTPException(413, "Upload chunk offset or size is invalid")
        if offset != state["received"]:
            # If an acknowledgement was lost, an identical retransmission is safe.
            if offset < state["received"] and offset + len(chunk) <= state["received"]:
                with open(state["path"], "rb") as f:
                    f.seek(offset)
                    if f.read(len(chunk)) == chunk:
                        return {"received": state["received"], "size": state["size"]}
            raise HTTPException(409, "Chunk offset mismatch; resume from server-reported position")
        with open(state["path"], "ab") as f:
            f.write(chunk)
        state["received"] += len(chunk)
        return {"received": state["received"], "size": state["size"]}


def finish(owner, token):
    with _lock:
        _cleanup()
        state = _pending.get(str(token))
        if state is None or state["owner"] != owner:
            raise HTTPException(404, "Upload session not found")
        if state["received"] != state["size"]:
            raise HTTPException(409, "Upload incomplete; all chunks must arrive before import")
        _pending.pop(str(token), None)
        return state["path"]
