"""Read-only §C Space metadata inspection. Never fetch or print secret values."""
from __future__ import annotations
import json
import os
import sys
from huggingface_hub import HfApi

TARGET = "kamiloki/Swyrlz"
CHECKED_KEYS = (
    "SWRLZ_VALKEY_URL",
    "SWRLZ_REDIS_REST_URL",
    "SWRLZ_REDIS_REST_TOKEN",
    "KV_REST_API_URL",
    "KV_REST_API_TOKEN",
    "SWRLZ_REDIS_BACKEND",
)


def main() -> int:
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        print("PREFLIGHT_UNAVAILABLE: GitHub HF_TOKEN is not available")
        return 2
    api = HfApi(token=token)
    try:
        info = api.repo_info(TARGET, repo_type="space")
        names = set(api.list_repo_files(TARGET, repo_type="space", revision=info.sha))
        secrets = api.get_space_secrets(TARGET)
        variables = api.get_space_variables(TARGET)
    except Exception as exc:
        # Avoid printing raw provider errors: a request could include credential-bearing URLs.
        print("PREFLIGHT_UNAVAILABLE:", type(exc).__name__)
        return 2
    report = {
        "target": TARGET,
        "space_revision": info.sha,
        "secret_or_variable_presence": {
            key: ("secret" if key in secrets else "variable" if key in variables else "absent")
            for key in CHECKED_KEYS
        },
        "space_file_presence": {
            key: key in names
            for key in ("app.py", "station.py", "requirements.txt",
                        "api/durable_redis_store.py", "api/chat_transcript_store.py",
                        "api/google_account.py", "api/canonical_redis_state.py")
        },
        "operation": "READ_ONLY_METADATA",
        "secrets_read": False,
        "data_written": False,
    }
    print("SWRLZ_VALKEY_PREFLIGHT " + json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
