from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from api import chat

try:
    from vercel.workflow import Workflows, get_writable, read_stream, start
    _WF_AVAILABLE = True
except Exception:
    Workflows = None
    get_writable = None
    read_stream = None
    start = None
    _WF_AVAILABLE = False

wf = Workflows(namespace="swrlz-chat") if _WF_AVAILABLE else None

if wf is not None:
    @wf.step
    async def generate_chat_step(*, payload: dict):
        writable = get_writable()
        request_id = str(payload.get("requestId"))
        # Reuse the already-proven local R39 stream adapter so the durable path
        # emits the exact same protocol events as ordinary chat generation.
        from api.chat_extensions import _local_stream
        for chunk in _local_stream(payload):
            await writable.write(chunk)
        await writable.close()
        return {"ok": True, "requestId": request_id}

    @wf.workflow
    async def chat_generation_workflow(*, payload: dict):
        return await generate_chat_step(payload=payload)

_original_stream_response = chat._stream_response


def install(server):
    if not _WF_AVAILABLE:
        return

    async def durable_stream(payload):
        run = await start(chat_generation_workflow, payload=payload)
        headers = chat._no_store_headers()
        headers.update({"X-SWRLZ-Stream-Contract": chat.STREAM_CONTRACT, "X-SWRLZ-Request-Id": payload["requestId"], "X-SWRLZ-Workflow-Run-Id": run.run_id})
        return StreamingResponse(run.readable_bytes(), media_type="application/x-ndjson", headers=headers)

    async def stream_response(payload):
        upstream_ready, missing = chat._upstream_ready()
        if chat._raw_upstream_url() and not upstream_ready:
            raise chat.BridgeError(503, "UPSTREAM_CONFIGURATION_INCOMPLETE", "The upstream bridge is missing: " + ", ".join(missing))
        if upstream_ready:
            return _original_stream_response(payload)
        if payload.get("workflowRunId") and read_stream is not None:
            run = await read_stream(str(payload["workflowRunId"]))
            headers = chat._no_store_headers()
            headers["X-SWRLZ-Workflow-Run-Id"] = str(payload["workflowRunId"])
            return StreamingResponse(run.readable_bytes(), media_type="application/x-ndjson", headers=headers)
        return await durable_stream(payload)

    chat._stream_response = stream_response

    @chat.app.get("/workflow/{run_id}/stream", include_in_schema=False)
    async def workflow_stream(run_id: str, request: Request):
        if read_stream is None:
            return JSONResponse({"ok": False, "code": "WORKFLOW_UNAVAILABLE"}, status_code=503)
        try:
            run = await read_stream(run_id)
            raw_start = request.query_params.get("startIndex")
            start_index = int(raw_start) if raw_start is not None else 0
        except Exception as exc:
            return JSONResponse({"ok": False, "code": "WORKFLOW_READ_FAILED", "detail": str(exc)}, status_code=404)
        headers = chat._no_store_headers()
        headers["X-SWRLZ-Workflow-Run-Id"] = run_id
        return StreamingResponse(run.readable_bytes(start_index=start_index), media_type="application/x-ndjson", headers=headers)
