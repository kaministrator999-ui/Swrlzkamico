"""Per-request cooperative + loopback socket interruption for §C CPU streaming.

The caller owns authentication and request IDs. No user text, tokens or network
destinations are logged. Only the registered request can be interrupted.
"""
from __future__ import annotations
from contextlib import contextmanager
import http.client
import json
import socket
import threading

class _Scope:
    def __init__(self, request_id, checker):
        self.request_id=request_id
        self.checker=checker
        self.cancel=threading.Event()
        self.conn=None

_lock=threading.RLock()
_local=threading.local()
_scopes={}

def bind_generation_cancel(request_id, checker):
    if not isinstance(request_id,str) or not request_id or not callable(checker):
        raise ValueError("Bound generator requires a request ID and checker")
    scope=_Scope(request_id,checker)
    with _lock:
        if request_id in _scopes:
            raise ValueError("Duplicate generation cancellation scope")
        _scopes[request_id]=scope
    _local.scope=scope
    return scope

def _scope():
    return getattr(_local,"scope",None)

def generation_cancelled():
    scope=_scope()
    return bool(scope and (scope.cancel.is_set() or scope.checker()))

def release_generation_cancel(request_id):
    with _lock:
        scope=_scopes.get(request_id)
        if scope and scope is _scope():
            _scopes.pop(request_id,None)
    if getattr(_local,"scope",None) is not None:
        if getattr(_local.scope,"request_id",None)==request_id:
            _local.scope=None

def cancel_active_request(request_id):
    """Signal exact registered generation and break its local blocking socket."""
    with _lock:
        scope=_scopes.get(request_id)
        if scope is None:return False
        scope.cancel.set()
        conn=scope.conn
        sock=getattr(conn,"sock",None) if conn else None
    if sock is not None:
        try:sock.shutdown(socket.SHUT_RDWR)
        except OSError:pass
    return True

@contextmanager
def completion_response(payload,port,post,timeout=900):
    """The original HTTP adapter is retained outside a bound Station request.

    A bound live completion uses a tracked loopback socket; cancellation can
    interrupt both prefill response-header waiting and streamed token reads.
    """
    scope=_scope()
    if scope is None:
        with post("/v1/chat/completions",payload,timeout=timeout) as response:
            yield response
        return
    if generation_cancelled():
        raise InterruptedError("GENERATION_CANCELLED")
    conn=http.client.HTTPConnection("127.0.0.1",int(port),timeout=timeout)
    try:
        conn.connect()
        with _lock:
            if scope.cancel.is_set():
                raise InterruptedError("GENERATION_CANCELLED")
            scope.conn=conn
        if generation_cancelled():
            raise InterruptedError("GENERATION_CANCELLED")
        data=json.dumps(payload,separators=(",",":")).encode("utf-8")
        conn.request("POST","/v1/chat/completions",body=data,
                     headers={"Content-Type":"application/json"})
        response=conn.getresponse()
        if response.status>=400:
            raise RuntimeError("QWEN35_HTTP_"+str(response.status))
        yield response
    finally:
        with _lock:
            if scope.conn is conn:
                scope.conn=None
        conn.close()
