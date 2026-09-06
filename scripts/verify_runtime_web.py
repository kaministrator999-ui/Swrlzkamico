from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAT = ROOT / "api" / "chat.py"
VERCEL = ROOT / "vercel.json"
CONTRACT = ROOT / "docs" / "contracts" / "SWRLZ_RUNTIME_WEB_WORKSPACE_V1.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = CHAT.read_text("utf-8")
    ast.parse(source, filename=str(CHAT))

    require('APP_VERSION = "1.1.0"' in source, "chat bridge version must be 1.1.0")
    require('LIVE_WEB_ROOT = Path("/tmp/swrlz-admin/web")' in source, "runtime web root missing")
    require('RUNTIME_WEB_TOKEN = RUNTIME_ROOT / "web-chat-token.txt"' in source, "runtime chat token override missing")
    require('@app.get("/live/{asset_path:path}", include_in_schema=False)' in source, "live asset route missing")
    require('root not in candidate.parents' in source, "resolved live path confinement missing")
    require('"Cache-Control"] = "no-store, max-age=0"' in source, "live no-store policy missing")
    require('_runtime_web_token()' in source, "runtime token lookup missing")

    config = json.loads(VERCEL.read_text("utf-8"))
    require(config.get("git", {}).get("deploymentEnabled", {}).get("dev") is False, "dev branch must not auto-deploy")
    rewrites = config.get("rewrites", [])
    require({"source": "/live", "destination": "/api/chat/live"} in rewrites, "live root rewrite missing")
    require({"source": "/live/:path*", "destination": "/api/chat/live/:path*"} in rewrites, "live path rewrite missing")
    require(CONTRACT.is_file(), "runtime web workspace contract missing")

    print("PASS runtime web workspace")
    print("PASS dev deployment suppression")
    print("PASS runtime chat token override")


if __name__ == "__main__":
    main()
