#!/usr/bin/env python3
"""Source-level verification for the integrated SWRLZ Vercel chat surface."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "2.1.1"
STREAM_CONTRACT = "swrlz_llm_stream_v2"


def require(path: str) -> Path:
    target = ROOT / path
    assert target.is_file(), f"missing required file: {path}"
    return target


def read(path: str) -> str:
    return require(path).read_text("utf-8")


def check_python() -> None:
    for path in ("api/index.py", "api/chat.py", "api/__init__.py"):
        ast.parse(read(path), filename=path)


def check_index() -> None:
    text = read("api/index.py")
    assert f'VERSION = "{EXPECTED_VERSION}"' in text, "SERVER version is not 2.1.1"
    assert 'app.mount("/api/chat", swrlz_chat_app' in text, "chat mount missing"
    assert '"chat": "/api/chat"' in text, "root route does not advertise chat"
    assert "OPEN CHAT" in text, "Admin chat entry point missing"
    assert "Dragon Jester Protocol" in text, "2.1.1 Admin theme marker missing"
    assert 'TOKEN = os.environ.get("SWRLZ_ADMIN_TOKEN", "").strip()' in text, "2.0.7 Admin auth normalization regressed"
    assert "DOWNLOAD_CHUNK = 3 * 1024 * 1024" in text, "chunked download contract regressed"
    assert "JSON.stringify(j,null,2)" in text, "Admin diagnostics are not preserving structured failure receipts"


def check_chat_bridge() -> None:
    text = read("api/chat.py")
    required = (
        f'STREAM_CONTRACT = "{STREAM_CONTRACT}"',
        'SWRLZ_WEB_CHAT_TOKEN',
        'SWRLZ_CHAT_UPSTREAM_URL',
        'SWRLZ_CHAT_UPSTREAM_NODE_ID',
        'SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF',
        'LOCAL_R39_STATUS_ONLY',
        'SECTION_PAYLOAD_LOCATION_AND_INFERENCE_WIRING_PENDING',
        '_local_not_ready_stream',
        '_proxy_stream',
        '_validate_upstream_event',
    )
    for token in required:
        assert token in text, f"chat bridge invariant missing: {token}"
    local = re.search(r"def _local_not_ready_stream\(.*?\n\n", text, re.S)
    assert local, "local status-only stream missing"
    assert '"DELTA"' not in local.group(0), "local not-ready path must not synthesize DELTA"


def check_chat_page() -> None:
    text = read("web/chat.html")
    for element_id in ("messages", "messageStack", "composer", "prompt", "sendButton", "settingsDialog", "accessToken"):
        assert f'id="{element_id}"' in text, f"chat UI element missing: {element_id}"
    assert "innerHTML" not in text, "chat page must not inject generated content through innerHTML"
    assert "sessionStorage" in text, "chat token session storage missing"
    assert "localStorage" in text, "browser-local thread storage missing"
    assert 'event.type === "DELTA"' in text and "message.text += event.text" in text, "committed DELTA rendering missing"
    assert 'event.type === "RESET"' in text and 'message.text = ""' in text, "RESET handling missing"


def check_docs_and_env() -> None:
    env = read(".env.example")
    for name in (
        "SWRLZ_ADMIN_TOKEN",
        "SWRLZ_WEB_CHAT_TOKEN",
        "SWRLZ_CHAT_UPSTREAM_URL",
        "SWRLZ_CHAT_UPSTREAM_NODE_ID",
        "SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF",
        "SWRLZ_CHAT_UPSTREAM_BEARER",
    ):
        assert name in env, f"environment template missing {name}"
    read("SWRLZ_VERCEL_CHAT_README.md")
    read("SWRLZ_VERCEL_CHAT_CHANGELOG.md")
    read("docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md")
    read("docs/checkpoints/INT-VERCEL-CHAT-001A_CHECKPOINT.md")
    root_readme = read("README.md")
    assert "Server revision: **2.1.1**" in root_readme
    assert "Chat revision: **1.0.0**" in root_readme


def check_transport_exclusions() -> None:
    vercel = json.loads(read("vercel.json"))
    encoded = json.dumps(vercel)
    assert ".transport/**" in encoded, "Vercel transport exclusion regressed"
    ignore = read(".vercelignore")
    assert ".transport/" in ignore, ".vercelignore transport exclusion regressed"
    assert "SWRLZ_NEW_SERVER_GITHUB_READY.zip" in ignore, "preserved server archive exclusion regressed"


def main() -> int:
    checks = (
        ("Python syntax", check_python),
        ("unified SERVER 2.1.1 mount/theme", check_index),
        ("truthful chat bridge", check_chat_bridge),
        ("safe streaming chat UI", check_chat_page),
        ("documentation/environment accounting", check_docs_and_env),
        ("Vercel transport exclusions", check_transport_exclusions),
    )
    for label, fn in checks:
        fn()
        print(f"PASS  {label}")
    print("PASS  integrated SWRLZ Vercel chat source gates")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL  {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
