"""Durable LALM Workstation queue consumer.

A queued turn owns inference independently of any Chat/browser connection.
Generation events are checkpointed to the shared transcript while the canonical
assistant message is terminal-committed exactly once.
"""
from __future__ import annotations

import json
import time
from types import SimpleNamespace
from typing import Any

from vercel.queue import Message, subscribe

from api import chat, chat_extensions, chat_turn_state
from api.chat_transcript_store import STORE


def _camera(stage: str, **fields: Any) -> None:
    record={"contract":"swrlz-lalm-workstation-worker-v1","stage":stage,"atUnixMs":int(time.time()*1000)}
    record.update(fields)
    print("SWRLZ_WORKSTATION_WORKER "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)


def _checkpoint(request_id: str, event: dict[str, Any]) -> None:
    """Mirror model progress into the existing shared generation transcript."""
    try:
        if hasattr(STORE, "append_event"):
            STORE.append_event(request_id, event)
        elif hasattr(STORE, "append"):
            STORE.append(request_id, event)
    except Exception as exc:
        _camera("checkpoint-error",requestId=request_id,errorType=type(exc).__name__,errorMessage=str(exc)[:300])


@subscribe(topic="swrlz-lalm-generation")
async def run_lalm_generation(message: Message[dict[str, Any]]) -> None:
    job=dict(message.payload or {})
    request_id=str(job.get("requestId") or "")
    _camera("job-enter",requestId=request_id,threadId=str(job.get("threadId") or ""))
    payload=dict(job.get("payload") or {})
    payload.update({
        "ingress":"SWRLZ_LALM_WORKSTATION_QUEUE",
        "requestId":request_id,
        "threadId":str(job.get("threadId") or ""),
        "messageId":str(job.get("userMessageId") or ""),
        "assistantMessageId":str(job.get("assistantMessageId") or ""),
        "prompt":str(job.get("prompt") or ""),
        "history":list(job.get("history") or []),
    })
    turn=chat_turn_state.CanonicalTurn(
        user_id=str(job.get("userId") or ""),
        account_scope=str(job.get("accountScope") or ""),
        thread_id=str(job.get("threadId") or ""),
        request_id=request_id,
        user_message_id=str(job.get("userMessageId") or ""),
        assistant_message_id=str(job.get("assistantMessageId") or ""),
        user_created_at=0,
        assistant_created_at=0,
        user_revision=0,
        storage_backend="redis",
    )
    text_parts: list[str]=[]
    terminal_type="FAILED"
    terminal_reason="workstation generation ended without terminal event"
    inference_failed=False
    inference_failure_reason=""
    try:
        normalized=chat._normalize_chat_request(payload)
        response=chat._stream_response(normalized)
        source=response.body_iterator
        async for chunk in source:
            raw=chunk.encode("utf-8") if isinstance(chunk,str) else bytes(chunk)
            for line in raw.decode("utf-8",errors="replace").splitlines():
                if not line.strip():
                    continue
                try:event=json.loads(line)
                except Exception:continue
                event_type=str(event.get("type") or "").upper()
                if event_type=="DELTA":
                    text_parts.append(str(event.get("text") or ""))
                if event_type=="FAILED":
                    inference_failed=True
                    inference_failure_reason=str(event.get("reason") or inference_failure_reason)
                if event.get("terminal"):
                    terminal_type=event_type or "FAILED"
                    terminal_reason=str(event.get("reason") or "")
                _checkpoint(request_id,event)
        committed_text="".join(text_parts)
        if inference_failed and not committed_text and terminal_type=="COMPLETED":
            terminal_type="FAILED"
            terminal_reason=inference_failure_reason or "inference failed before producing assistant text"
        chat_turn_state.finish_turn(turn,text=committed_text,terminal_type=terminal_type,reason=terminal_reason)
        _camera("job-terminal",requestId=request_id,terminalType=terminal_type,textChars=len(committed_text))
    except BaseException as exc:
        _camera("job-error",requestId=request_id,errorType=type(exc).__name__,errorMessage=str(exc)[:500])
        try:
            chat_turn_state.finish_turn(turn,text="".join(text_parts),terminal_type="FAILED",reason=f"{type(exc).__name__}: {exc}")
        except Exception as finish_exc:
            _camera("job-finish-error",requestId=request_id,errorType=type(finish_exc).__name__,errorMessage=str(finish_exc)[:500])
        raise
