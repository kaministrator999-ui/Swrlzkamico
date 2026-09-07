from __future__ import annotations

import api.chat as chat
import api.chat_extensions as extensions


def _fast_status_payload():
    """Status is a receipt, not an inference/model-load trigger."""
    base = extensions._original_status_payload()
    if not chat._raw_upstream_url():
        try:
            engine, source = extensions._engine()
            engine_id = str(engine.ENGINE_ID)
            model_sha = str(engine.MODEL_SHA256)
            hot_revision = str(getattr(engine, "HOT_REVISION", ""))
        except Exception as exc:
            source = "unavailable"
            engine_id = ""
            model_sha = ""
            hot_revision = ""
            if not extensions.LOCAL_READINESS.get("checked"):
                extensions.LOCAL_READINESS.update({"ok": False, "code": "R39_ENGINE_IMPORT_FAILED", "detail": f"{type(exc).__name__}: {exc}"})
        ready = extensions.LOCAL_READINESS
        base["mode"] = "LOCAL_R39"
        base["localR39"] = {
            "containerVerificationAvailable": True,
            "engineWired": True,
            "engineId": engine_id,
            "modelSha256": model_sha,
            "engineSource": source,
            "hotRevision": hot_revision,
            "autoInitializeOnStream": True,
            "manualGate5Required": False,
            "oneTokenReady": bool(ready.get("oneTokenReady")),
            "interactiveReady": bool(ready.get("interactiveReady")),
            "readinessChecked": bool(ready.get("checked")),
            "statusProbeNonBlocking": True,
            "blockers": [] if ready.get("interactiveReady") else [str(ready.get("code") or "R39_ENGINE_NOT_PROBED")],
        }
    return base


def install(server) -> None:
    chat._status_payload = _fast_status_payload
    server.CAPABILITIES["chat-fast-status"] = {
        "kind": "read-only",
        "ready": True,
        "path": "/api/chat/ops",
        "modelInspectionOnStatus": False,
        "detail": "Status never calls inspect_engine; verification and generation own model work.",
    }
