#!/usr/bin/env python3
"""Exact-source, guarded Aiven private-admin integration for existing §C HF Space.

Default mode is inspection only. Never copy the historical server over the
current Hugging Face Station. No unrelated page, model or hardware edits.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
MODULE = Path(__file__).resolve().parents[1] / "hf_space" / "aiven_admin.py"
MARKER = "# SWRLZ_ADMIN_AIVEN_V1"
LOGIN_ANCHOR = '    sid=uuid.uuid4().hex'
HOOK = (
    "\n" + MARKER + "\n"
    "from aiven_admin import install as _install_aiven_admin\n"
    "_install_aiven_admin(app, _legacy_account_session)\n"
)


def patch_station(source: str) -> str:
    """Add verified email claim to the existing durable Google login only.

    Use Redis-backed _legacy_account_session for admin, not the broader Forge
    account resolver. A live-source drift is an error, never a loose match.
    """
    if MARKER in source:
        raise ValueError("AIVEN_ADMIN_ALREADY_INSTALLED")
    if source.count("def _legacy_account_session(") != 1:
        raise ValueError("HF_DURABLE_GOOGLE_SESSION_ANCHOR_MISSING")
    if "return sid,account_chat_store.load_login(sid)" not in source:
        raise ValueError("HF_DURABLE_SESSION_VERIFICATION_DRIFT")
    start_marker = '@app.post("/api/account/google")'
    end_marker = '@app.post("/api/account/logout")'
    if source.count(start_marker) != 1 or source.count(end_marker) != 1:
        raise ValueError("HF_GOOGLE_LOGIN_ROUTE_MISSING")
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    login = source[start:end]
    if (
        login.count(LOGIN_ANCHOR) != 1
        or "google_id_token.verify_oauth2_token(" not in login
        or "account_chat_store.save_login(sid,user)" not in login
    ):
        raise ValueError("HF_GOOGLE_CLAIM_PROJECTION_DRIFT")
    updated_login = login.replace(
        LOGIN_ANCHOR,
        "    # Persist the Google-issued email verification result with this login.\n"
        "    user['emailVerified']=claims.get('email_verified') is True\n"
        + LOGIN_ANCHOR,
        1,
    )
    updated = source[:start] + updated_login + source[end:] + HOOK
    ast.parse(updated, filename="station.py")
    return updated

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def preflight(api, token: str):
    """Fetch exact current revision; never patch a historic or inferred source."""
    from huggingface_hub import hf_hub_download

    revision = api.repo_info(SPACE, repo_type="space").sha
    if len(revision) != 40:
        raise RuntimeError("HF_REVISION_UNAVAILABLE")
    names = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    if "aiven_admin.py" in names:
        raise RuntimeError("HF_AIVEN_ADMIN_ALREADY_EXISTS_REVIEW_REQUIRED")
    before = Path(hf_hub_download(
        SPACE, "station.py", repo_type="space", revision=revision, token=token
    )).read_bytes()
    updated = patch_station(before.decode("utf-8")).encode("utf-8")
    module = MODULE.read_bytes()
    ast.parse(module.decode("utf-8"), filename="aiven_admin.py")
    for needle in (
        b'SWRLZ_ADMIN_GOOGLE_SUB',
        b'SWRLZ_SANDBOX_WRITE_GOOGLE_SUB',
        b'SWRLZ_ADMIN_GOOGLE_EMAIL',
        b'emailVerified',
        b'@app.get("/api/admin/aiven/metrics"',
        b'@app.get("/admin/aiven"',
    ):
        if needle not in module:
            raise RuntimeError("ADMIN_GUARD_INCOMPLETE")
    if b"_install_aiven_admin(app, _legacy_account_session)" not in updated:
        raise RuntimeError("UNVERIFIED_ADMIN_ACCOUNT_SESSION_GUARD")
    if b"from aiven_admin import install" not in updated:
        raise RuntimeError("HF_ADMIN_INSTALL_HOOK_MISSING")
    if b"google_id_token.verify_oauth2_token(" not in updated:
        raise RuntimeError("GOOGLE_TOKEN_VERIFICATION_LOST")
    return revision, before, updated, module


def release(mode: str) -> None:
    from huggingface_hub import HfApi, CommitOperationAdd, CommitOperationDelete

    token = os.environ.get("HF_TOKEN", "").strip()
    api = HfApi(token=token or None)
    revision, before, updated, module = preflight(api, token)
    print(json.dumps({
        "phase": "VALIDATED", "space": SPACE, "baseRevision": revision,
        "stationBeforeSha256": digest(before), "stationAfterSha256": digest(updated),
        "adminModuleSha256": digest(module), "changes": ["station.py", "aiven_admin.py"],
        "publicChatEdited": False, "modelsEdited": False, "secretsPrinted": False,
    }))
    if mode == "validate":
        return
    if os.environ.get("SWRLZ_AIVEN_ADMIN_RELEASE_APPROVED") != "1":
        raise RuntimeError("EXPLICIT_ADMIN_RELEASE_APPROVAL_REQUIRED")
    if not token:
        raise RuntimeError("HF_TOKEN_REQUIRED")
    # An unconfigured owner must never be called an active admin.
    owner = (os.environ.get("SWRLZ_ADMIN_GOOGLE_SUB", "").strip()
             or os.environ.get("SWRLZ_ADMIN_GOOGLE_EMAIL", "").strip())
    if not owner:
        raise RuntimeError("PRIVATE_GOOGLE_OWNER_SECRET_REQUIRED")
    if api.repo_info(SPACE, repo_type="space").sha != revision:
        raise RuntimeError("LIVE_HF_SOURCE_CHANGED_BEFORE_DEPLOY")
    # Set these only from the CI secret store; values never enter repository files.
    for name in (
        "SWRLZ_ADMIN_GOOGLE_SUB", "SWRLZ_ADMIN_GOOGLE_EMAIL",
        "SWRLZ_AIVEN_API_TOKEN", "SWRLZ_AIVEN_PROJECT", "SWRLZ_AIVEN_SERVICE",
    ):
        value = os.environ.get(name, "").strip()
        if value:
            api.add_space_secret(repo_id=SPACE, key=name, value=value)
    checkpoint = Path("hf-aiven-predeploy-station.py")
    checkpoint.write_bytes(before)
    response = api.create_commit(
        repo_id=SPACE, repo_type="space", parent_commit=revision,
        operations=[
            CommitOperationAdd(path_in_repo="station.py", path_or_fileobj=updated),
            CommitOperationAdd(path_in_repo="aiven_admin.py", path_or_fileobj=module),
        ],
        commit_message="§C: admin-only Aiven monitoring for verified Kami Google account",
    )
    published = str(response.oid)
    print(json.dumps({"phase": "DEPLOYED_UNVERIFIED", "revision": published,
                      "rollbackBase": revision, "liveAcceptance": False}))
    # The push alone is not runtime acceptance. Confirm bytes using pinned SHA.
    from huggingface_hub import hf_hub_download
    try:
        for name, expected in (("station.py", updated), ("aiven_admin.py", module)):
            path = hf_hub_download(
                SPACE, name, repo_type="space", revision=published, token=token
            )
            if Path(path).read_bytes() != expected:
                raise RuntimeError("POST_DEPLOY_SOURCE_MISMATCH:" + name)
        print(json.dumps({"phase": "SOURCE_VERIFIED_RUNTIME_UNVERIFIED",
                          "revision": published}))
    except Exception:
        if api.repo_info(SPACE, repo_type="space").sha == published:
            api.create_commit(
                repo_id=SPACE, repo_type="space", parent_commit=published,
                operations=[
                    CommitOperationAdd(path_in_repo="station.py", path_or_fileobj=before),
                    CommitOperationDelete(path_in_repo="aiven_admin.py"),
                ],
                commit_message="rollback: restore exact §C Station after Aiven source verification failure",
            )
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("validate", "deploy"), default="validate")
    args = parser.parse_args()
    release(args.mode)
