"""§wyrlz stable server entrypoint.

Stable infrastructure owns the HTTP/bootstrap/control plane. Runtime application
pages, page-owned assets, and the hot R39 implementation are sourced from the
runtime branch by the dedicated hot/live loaders. The stable frozen-web
collector host applies authentication and a fixed runtime-module contract while
the collector implementation and page remain runtime-owned.

Server 2.3.111 adds bounded server-visible Chat client boot diagnostics while
preserving the runtime-source-of-truth delivery boundary.
"""
from __future__ import annotations

from api import server_v213 as _server
from api.runtime_hot import install as _install_hot_runtime, _safe_auto_sync
from api.hot_loader import get_engine
from api.chat_admin_session import install as _install_chat_admin_session
from api.chat_fast_status import install as _install_chat_fast_status
from api.chat_client_debug import install as _install_chat_client_debug
from api.chat_message_receipt import install as _install_chat_message_receipt
from api.admin_auth_guard import install as _install_admin_auth_guard
from api.live_source_guard import install as _install_live_source_guard
from api.control_plane import install as _install_control_plane
from api.native_status import install as _install_native_status
from api.contextual_input import install as _install_contextual_input
from api.account_routes_v2 import install as _install_account_routes
from api.collector_host import install as _install_collector_host
from api.chat_resume_sessions import install as _install_chat_resume_sessions
from api.chat_rmcca_passthrough import install as _install_chat_rmcca_passthrough
from api.chat_transcript_store import STORE as _transcript_store
from api.chat_state import app as _chat_state_app
import api.chat_extensions as _chat_extensions

VERSION = "2.3.111"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {"kind":"runtime-execution","ready":True,"engineId":"swrlz_r39_native_qmatvec_v1","fallbackEngineId":"swrlz_r39_python_reference_v1","boundary":"compiled direct-quantized R39 execution; hot reasoning overlay remains independent of bundled server release"}
_server.CAPABILITIES["lalm-startup-warm"] = {"kind":"runtime-execution","ready":False,"phase":"server-start","detail":"LALM/R39 is hydrated from runtime and probed before the worker is exposed to Chat."}
_server.CAPABILITIES["chat-resumable-generation"] = {"kind":"transport-continuity","ready":True,"contract":"resumable-v1","detail":"A requestId owns one local generation session; the owning worker replays events after resumeAfterSeq while shared transcript state prevents duplicate remote ownership."}
_server.CAPABILITIES["chat-generation-transcript"] = {"kind":"transport-continuity","ready":True,"contract":"generation-transcript-v1","detail":"Append-only generated text, revision, phase, sequence and terminal state are authoritative response-position synchronization state."}
_server.CAPABILITIES["chat-shared-generation-transcript"] = {"kind":"durable-transport-continuity","ready":bool(_transcript_store.configured),"contract":"shared-private-blob-v1","access":"private","ttlSeconds":1800,"detail":"The active model state remains worker-owned; bounded transcript checkpoints are shared privately across workers so a different worker can synchronize the same response without starting a duplicate generation."}
_server.CAPABILITIES["chat-account-state"] = {"kind":"durable-user-state","ready":bool(_transcript_store.configured),"contract":"swrlz-chat-account-state-v1","access":"private","authority":"server","browserLocalStorageAuthoritative":False,"detail":"Authenticated account-scoped thread/message presentation state is durable in private Blob storage; browser localStorage is a cache only."}
_server.CAPABILITIES["chat-rmcca-direct-transport"] = {"kind":"cognitive-context-transport","ready":True,"contract":"rmcca-direct-v1","fallback":"history-carrier-v1","detail":"Validated RMCCA cognitive and user-time context survives stable request normalization as bounded first-class metadata; the compact history carrier remains compatibility transport."}
_server.CAPABILITIES["runtime-delivery-optimization"] = {"kind":"performance","ready":True,"contract":"hot-runtime-delivery-v1","syncGateSeconds":30,"parallelSourceChecks":True,"assetCacheContract":"manifest-versioned-immutable-v1","detail":"Ordinary Chat requests share a gated runtime refresh authority; due source checks run concurrently; revisioned JS/CSS may remain browser-cached while HTML and manifest stay live/no-store."}
_server.CAPABILITIES["runtime-manifest-authority"] = {"kind":"runtime-source-integrity","ready":True,"contract":"github-contents-manifest-v1","authority":"github-contents-api-v1","failurePolicy":"fail-closed-no-stale-raw-manifest","assetPath":"raw-github-revisioned","detail":"The runtime manifest resolves from repository-content authority; versioned assets remain on the fast immutable raw path, and stale raw branch content cannot silently select an older manifest revision."}
_install_admin_auth_guard(_server)
_install_hot_runtime(_server)
_install_chat_admin_session(_server)
_install_chat_fast_status(_server)
_install_chat_client_debug(_server)
_install_chat_message_receipt()
_install_control_plane(_server)
_install_native_status(_server)
_install_contextual_input(_server)
_install_account_routes(_server)
_server.app.include_router(_chat_state_app.router)
_install_collector_host(_server)
_install_live_source_guard(_server)
_install_chat_resume_sessions(_chat_extensions)
_install_chat_rmcca_passthrough(_chat_extensions)


def _warm_lalm_at_start() -> None:
    """Hydrate and probe the local LALM before Chat handles user traffic."""
    try:
        sync = _safe_auto_sync(_server)
        engine, source = get_engine()
        state = engine.inspect_engine()
        _chat_extensions.LOCAL_READINESS.clear()
        _chat_extensions.LOCAL_READINESS.update({"checked": True, "engineSource": source, **state})
        _server.CAPABILITIES["lalm-startup-warm"] = {"kind":"runtime-execution","ready":bool(state.get("interactiveReady", state.get("modelReady", True))),"phase":"server-start-complete","engineSource":source,"sync":sync,"state":state}
        _server.activity("lalm-startup-warm", source=source, ready=True, branch=sync.get("branch", "runtime"))
    except Exception as exc:
        _server.CAPABILITIES["lalm-startup-warm"] = {"kind":"runtime-execution","ready":False,"phase":"server-start-fallback","error":f"{type(exc).__name__}: {exc}"}
        _server.activity("lalm-startup-warm-failed", error=f"{type(exc).__name__}: {exc}")


_warm_lalm_at_start()
_server._write_server_state()

app = _server.app
INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES