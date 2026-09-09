#!/usr/bin/env python3
"""Source-level verification for the integrated SWRLZ Vercel chat surface."""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "2.2.7"
EXPECTED_CHAT_VERSION = "1.4.0-rc.1"
STREAM_CONTRACT = "swrlz_llm_stream_v2"
ONLINE_STREAM_CONTRACT = "swrlz_llm_stream_v3"


def require(path: str) -> Path:
    target = ROOT / path
    assert target.is_file(), f"missing required file: {path}"
    return target


def read(path: str) -> str:
    return require(path).read_text("utf-8")


def check_python() -> None:
    for path in (
        "api/index.py", "api/server_v213.py", "api/chat.py", "api/chat_extensions.py", "api/online_evidence.py",
        "api/__init__.py", "swyrlz/r39_inference.py", "swyrlz/gate5_live.py",
        "swyrlz/r39_matvec_patch.py", "swyrlz/r39_tokenizer_patch.py",
    ):
        ast.parse(read(path), filename=path)


def check_index() -> None:
    wrapper = read("api/index.py"); base = read("api/server_v213.py")
    assert f'VERSION = "{EXPECTED_VERSION}"' in wrapper
    assert 'from api import server_v213 as _server' in wrapper
    assert '_server.CAPABILITIES["local-r39-inference"]' in wrapper
    assert 'app.mount("/api/chat", swrlz_chat_app' in base
    assert '"chat":"/api/chat"' in base or '"chat": "/api/chat"' in base
    assert 'TOKEN = os.environ.get("SWRLZ_ADMIN_TOKEN", "").strip()' in base
    assert "DOWNLOAD_CHUNK = 3 * 1024 * 1024" in base


def check_chat_bridge() -> None:
    base=read("api/chat.py"); ext=read("api/chat_extensions.py"); evidence=read("api/online_evidence.py"); engine=read("swyrlz/r39_inference.py")
    for token in (f'STREAM_CONTRACT_V2 = "{STREAM_CONTRACT}"','SWRLZ_WEB_CHAT_TOKEN','SWRLZ_CHAT_UPSTREAM_URL','SWRLZ_CHAT_UPSTREAM_NODE_ID','SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF','_proxy_stream','_validate_upstream_event'):
        assert token in base, f"chat bridge invariant missing: {token}"
    assert f'chat.APP_VERSION="{EXPECTED_CHAT_VERSION}"' in ext or f'chat.APP_VERSION = "{EXPECTED_CHAT_VERSION}"' in ext
    assert 'chat._proxy_stream(payload) if upstream_ready else _local_stream(payload)' in ext
    assert 'generate_events' in ext and 'LOCAL_R39' in engine
    assert 'event_type=="DELTA"' in ext or 'event_type == "DELTA"' in ext
    assert 'IncrementalDecoder' in engine and 'getincrementaldecoder("utf-8")' in engine
    assert '_probe_local_once' in ext and 'manualGate5Required' in ext
    assert 'COMPUTE_HEARTBEAT' in ext and 'ThreadPoolExecutor' in ext
    for token in ('ONLINE_STREAM_CONTRACT', 'knowledgeMode', 'ONLINE_EVIDENCE_REQUIRES_V3', 'STREAM_CONTRACT_V3'):
        assert token in base, f"online request/stream invariant missing: {token}"
    for token in ('ONLINE_ROUTE', 'build_grounded_payload', 'knowledgeReceipt', 'ONLINE_EVIDENCE_UPSTREAM_UNSUPPORTED'):
        assert token in ext, f"online orchestration invariant missing: {token}"
    for token in (ONLINE_STREAM_CONTRACT, 'class SafeFetcher', 'class OnlineEvidenceService', 'REQUEST_SCOPED_INFERENCE_ONLY', 'trainingEligible', '_PinnedHTTPSConnection'):
        assert token in evidence, f"online evidence invariant missing: {token}"


def check_chat_page() -> None:
    text=read("web/chat.html"); js=read("web/chat_enhancements.js"); css=read("web/chat_enhancements.css")
    for element_id in ("messages","messageStack","composer","prompt","sendButton","settingsDialog","accessToken","knowledgeMode"):
        assert f'id="{element_id}"' in text
    assert "sessionStorage" in text and "localStorage" in text
    assert 'event.type === "DELTA"' in text and "message.text += event.text" in text
    assert 'event.type === "RESET"' in text and 'message.text = ""' in text
    assert 'function createThread()' in text and 'function deleteThread(id)' in text
    assert 'COPY TEXT' in js and 'CLEAR CAMERA' in js
    assert 'Local R39 ready' in js
    assert 'repairDrawerStack' in js and '.sidebar-scrim' in css
    assert ONLINE_STREAM_CONTRACT in text and 'event.type === "SOURCE"' in text
    assert 'trainingEligible: false' in text and 'ONLINE · EVIDENCE' in text


def check_docs_and_env() -> None:
    env=read(".env.example")
    for name in ("SWRLZ_ADMIN_TOKEN","SWRLZ_WEB_CHAT_TOKEN","SWRLZ_CHAT_UPSTREAM_URL","SWRLZ_CHAT_UPSTREAM_NODE_ID","SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF","SWRLZ_CHAT_UPSTREAM_BEARER","SWRLZ_ONLINE_EVIDENCE_ENABLED","SWRLZ_ONLINE_EVIDENCE_PROVIDER"):
        assert name in env
    chat_readme=read("SWRLZ_VERCEL_CHAT_README.md"); root_readme=read("README.md"); contract=read("docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md")
    assert f"Server revision: **{EXPECTED_VERSION}**" in root_readme
    assert f"Chat review candidate: **{EXPECTED_CHAT_VERSION}**" in root_readme
    assert f"Chat review candidate: **{EXPECTED_CHAT_VERSION}**" in chat_readme
    assert "LOCAL_R39" in contract and "local r39 contract" in contract.lower()
    for path in ("docs/contracts/SWRLZ_ONLINE_EVIDENCE_V1.md","docs/contracts/SWRLZ_LLM_STREAM_V3.md","docs/data/SWRLZ_ONLINE_KNOWLEDGE_DATA_POLICY_V1.md","docs/checkpoints/SWRLZ-WEB-KNOWLEDGE-001A_CHECKPOINT.md"):
        assert "SWRLZ-WEB-KNOWLEDGE-001A" in read(path), f"checkpoint identity missing: {path}"


def check_transport_exclusions() -> None:
    vercel=json.loads(read("vercel.json")); encoded=json.dumps(vercel); ignore=read(".vercelignore")
    assert ".transport/**" in encoded
    assert ".transport/" in ignore
    assert "SWRLZ_NEW_SERVER_GITHUB_READY.zip" in ignore


def main() -> int:
    checks=(("Python syntax",check_python),(f"unified SERVER {EXPECTED_VERSION} wrapper/base",check_index),("offline/online chat bridge",check_chat_bridge),("safe streaming chat UI",check_chat_page),("documentation/environment accounting",check_docs_and_env),("Vercel transport exclusions",check_transport_exclusions))
    for label,fn in checks: fn(); print(f"PASS  {label}")
    print("PASS  integrated SWRLZ Vercel chat source gates")
    return 0

if __name__ == "__main__":
    try: raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL  {type(exc).__name__}: {exc}",file=sys.stderr); raise
