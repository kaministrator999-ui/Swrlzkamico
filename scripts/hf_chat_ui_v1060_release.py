#!/usr/bin/env python3
"""Release §C 1.0.60 visual delta onto the exact live Hugging Face Chat.

Preserves all unrelated live JavaScript, account/model/stream APIs, and files.
Only the live Chat HTML may change, with a
preflight snapshot, parent-commit CAS, readback, served-page QA, and rollback.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download

SPACE = "kamiloki/Swyrlz"
UI = "chat/§wyrlz/index.html"
VERSION = "chat/§wyrlz/VERSION.txt"
FILES = (UI,)
MARK = "/* §C 1.0.60 — Unified professional interface."
BACKUP = Path("reports/chat-ui-v1060-live-release")
BASE = "https://kamiloki-swyrlz.hf.space"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def emit(event: str, **details) -> None:
    print("CHAT_UI_1060", json.dumps({"event": event, **details},
                                    sort_keys=True, ensure_ascii=False), flush=True)


def replace_once(value: str, old: str, new: str, label: str) -> str:
    count = value.count(old)
    if count != 1:
        raise RuntimeError(f"LIVE_SOURCE_DRIFT {label}: expected 1, found {count}")
    return value.replace(old, new, 1)


class IdInventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])


def element_ids(html: str) -> list[str]:
    parser = IdInventory()
    parser.feed(html)
    return parser.ids


def visual_delta(candidate: str) -> str:
    if candidate.count(MARK) != 1:
        raise RuntimeError("Candidate is not the reviewed §C 1.0.60 design")
    if 'name="swrlz-chat-version" content="1.0.60"' not in candidate:
        raise RuntimeError("Candidate lacks the expected 1.0.60 version")
    start = candidate.index(MARK)
    end = candidate.find("\n  </style>", start)
    if end < 0:
        raise RuntimeError("Candidate stylesheet closing boundary changed")
    delta = candidate[start:end]
    if len(delta) < 15000 or "--ui-elevated" not in delta:
        raise RuntimeError("Incomplete design delta")
    # Preserve the newer live Chat's ResizeObserver-owned composer geometry.
    for old, new in (
        ("inset:0 0 102px;", "inset:0 0 var(--composer-visible-height,102px);"),
        ("inset:0 0 88px;", "inset:0 0 var(--composer-visible-height,88px);"),
    ):
        if delta.count(old) != 1:
            raise RuntimeError("Reviewed CSS did not contain the expected composer inset")
        delta = delta.replace(old,new,1)
    return delta


def patch(live: str, candidate: str) -> str:
    if MARK in live:
        if (live.count(MARK)!=1 or
            live.count('name="swrlz-chat-version" content="1.1.40"')!=1 or
            live.count('name="swrlz-chat-design-version" content="1.0.60"')!=1):
            raise RuntimeError("Pre-existing UI design/version is not a repairable 1.1.40 release")
        next_html = live
        for old, new in (
            ("inset:0 0 102px;", "inset:0 0 var(--composer-visible-height,102px);"),
            ("inset:0 0 88px;", "inset:0 0 var(--composer-visible-height,88px);"),
        ):
            if live.count(old) != 1:
                raise RuntimeError("Live design inset has drifted; refuse unreviewed repair")
            next_html = replace_once(next_html,old,new,"preserve live composer measurement")
        next_html = replace_once(next_html,
            'name="swrlz-chat-version" content="1.1.40"',
            'name="swrlz-chat-version" content="1.1.41"', "increment live repair version")
        if element_ids(live)!=element_ids(next_html):
            raise RuntimeError("Composer repair changed component IDs")
        emit("LIVE_1140_REPAIR_BUILT", nextVersion="1.1.41", preservedDynamicComposer=True)
        return next_html
    if live.count("</style>") < 1 or live.count("<body>") != 1:
        raise RuntimeError("Unexpected live Chat page structure")
    necessary = (
        'id="menuButton"', 'id="sideMenu"', 'id="menuShade"',
        'id="chatViewport"', 'id="messageList"', 'id="composerShell"',
        'id="prompt"', 'id="sendButton"', 'id="workSurfaceButton"',
        'id="workSurface"', 'id="settingsSheet"', 'id="settingsSave"',
        '<nav class="settings-nav" aria-label="Settings sections">',
    )
    missing = [needle for needle in necessary if needle not in live]
    if missing:
        raise RuntimeError("Current live Chat is structurally incompatible: " + ", ".join(missing))
    for section in ("general", "model", "you", "companion", "lore", "rapport",
                    "proposals", "appearance", "motion", "accessibility", "privacy"):
        if live.count('data-settings-section="' + section + '"') != 1:
            raise RuntimeError("Live settings section mismatch: " + section)
        if live.count('data-settings-pane="' + section + '"') != 1:
            raise RuntimeError("Live settings pane mismatch: " + section)
    delta = visual_delta(candidate)
    next_html = live.replace("  </style>", "\n    " + delta + "\n  </style>", 1)

    groups = (
        ('<nav class="settings-nav" aria-label="Settings sections">',
         '<div class="settings-nav-group-label" aria-hidden="true">Conversation</div>'),
        ('<button class="settings-nav-button" type="button" data-settings-section="you">',
         '<div class="settings-nav-group-label" aria-hidden="true">Identity</div>'),
        ('<button class="settings-nav-button" type="button" data-settings-section="lore">',
         '<div class="settings-nav-group-label" aria-hidden="true">Memory &amp; permissions</div>'),
        ('<button class="settings-nav-button" type="button" data-settings-section="appearance">',
         '<div class="settings-nav-group-label" aria-hidden="true">Interface</div>'),
    )
    for anchor, group in groups:
        placement = (anchor + "\n        " + group if anchor.startswith("<nav ")
                     else group + "\n        " + anchor)
        next_html = replace_once(next_html, anchor, placement,
                                 "settings group " + group)

    version_match = re.search(
        r'<meta name="swrlz-chat-version" content="([^"]+)">', next_html)
    if not version_match:
        raise RuntimeError("Live version meta was not found")
    if version_match.group(1) != "1.1.39":
        raise RuntimeError("UNEXPECTED_LIVE_VERSION: expected current 1.1.39")
    next_html = replace_once(next_html, version_match.group(0),
        '<meta name="swrlz-chat-version" content="1.1.40">\n  '
        '<meta name="swrlz-chat-design-version" content="1.0.60">', "version marker")

    for old, new in (
        ("<title>Chat</title>", "<title>§wyrlz · Chat</title>"),
        ("Glitch Dragon control surface", "Your §wyrlz workspace"),
        ("Structured runtime surface", "Actions, results & sources"),
        ('aria-label="Open side menu" aria-expanded="false"',
         'aria-label="Open conversations menu" aria-controls="sideMenu" aria-expanded="false"'),
    ):
        if old in next_html:
            next_html = replace_once(next_html, old, new, "cosmetic copy")

    menu_close = 'menuShade.addEventListener("click", () => setMenu(false));'
    if menu_close in live:
        next_html = replace_once(next_html, menu_close,
            menu_close + '\n      document.addEventListener("keydown",event=>{'
            'if(event.key==="Escape"&&document.body.classList.contains("menu-open"))'
            '{setMenu(false);menuButton.focus();}});', "Escape menu")
    else:
        emit("ESCAPE_BINDING_SKIPPED", reason="Existing live menu listener differs")

    # A visual-only patch must never remove, rename or add an owned component ID.
    old_ids = element_ids(live)
    if old_ids != element_ids(next_html):
        raise RuntimeError("Visual delta changed structural element IDs")
    if len(old_ids) != len(set(old_ids)):
        raise RuntimeError("Pre-existing duplicate live IDs prevent safe patch")
    if next_html.count(MARK) != 1 or next_html.count("settings-nav-group-label") < 4:
        raise RuntimeError("Presentation delta incomplete")
    if (next_html.count('name="swrlz-chat-design-version" content="1.0.60"') != 1 or
            next_html.count('name="swrlz-chat-version" content="1.1.40"') != 1):
        raise RuntimeError("Version metadata differs from candidate")
    return next_html


def api_client() -> HfApi:
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        raise RuntimeError("HF_TOKEN not configured in approved runner")
    return HfApi(token=token)


def read_space_files(api: HfApi, revision: str) -> dict[str, bytes]:
    listed = set(api.list_repo_files(SPACE, repo_type="space", revision=revision))
    missing = set(FILES) - listed
    if missing:
        raise RuntimeError("Existing Space lacks canonical Chat files: " + str(sorted(missing)))
    return {name: Path(hf_hub_download(SPACE, name, repo_type="space",
                       revision=revision, token=api.token)).read_bytes() for name in FILES}


def snapshot(api: HfApi, candidate_path: Path) -> None:
    candidate = candidate_path.read_text(encoding="utf-8")
    revision = api.repo_info(SPACE, repo_type="space").sha
    originals = read_space_files(api, revision)
    try:
        html = originals[UI].decode("utf-8")
        version = (re.search(r'swrlz-chat-version" content="([^"]+)"',html).group(1)
                   if 'swrlz-chat-version" content="' in html else "unknown")
    except UnicodeDecodeError as exc:
        raise RuntimeError("Live Chat source is not UTF-8") from exc
    emit("LIVE_BASELINE", revision=revision,
         liveVersion=version.strip(),
         uiBytes=len(originals[UI]),
         uiSha256=digest(originals[UI]),
         sourceVersion=re.search(r'swrlz-chat-version" content="([^"]+)"',html).group(1)
         if 'swrlz-chat-version" content="' in html else "unknown")
    BACKUP.mkdir(parents=True, exist_ok=True)
    for name, blob in originals.items():
        out = BACKUP / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(blob)
    manifest = {"schema":"swrlz-chat-ui-1060-v1", "space":SPACE,"revision":revision,
                "paths": list(FILES), "before":{p:digest(v) for p,v in originals.items()},
                "sourceSha256":digest(candidate.encode("utf-8"))}
    (BACKUP/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    new_html = patch(html, candidate).encode("utf-8")
    desired = {UI:new_html}
    for name, blob in desired.items():
        out = BACKUP / "candidate" / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(blob)
    manifest["after"] = {p:digest(v) for p,v in desired.items()}
    (BACKUP/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    emit("CANDIDATE_CHECKED", revision=revision, files=list(FILES),
         insertedCSSBytes=len(visual_delta(candidate)), after=manifest["after"])


def served_version(expected_version: str) -> tuple[bool,str]:
    for path in ("/chat/%C2%A7wyrlz", "/chat/%C2%A7wyrlz/index.html"):
        try:
            req = urllib.request.Request(
                BASE+path+"?design_release_v1060="+str(time.monotonic_ns()),
                headers={"User-Agent":"Swyrlz-Chat-UI-1060-Release",
                         "Cache-Control":"no-cache"})
            with urllib.request.urlopen(req,timeout=30) as response:
                payload = response.read(950000).decode("utf-8", errors="replace")
            if (MARK in payload and 'swrlz-chat-version" content="' + expected_version + '"' in payload
                    and 'swrlz-chat-design-version" content="1.0.60"' in payload):
                return True, path
        except Exception as exc:
            last = type(exc).__name__ + ": " + str(exc)[:120]
    return False, locals().get("last", "No matching 1.0.60 page response")


def upload(api: HfApi, revision: str, files: dict[str, bytes], message: str) -> str:
    result = api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=revision,
        operations=[CommitOperationAdd(path_in_repo=name,path_or_fileobj=io.BytesIO(blob))
                    for name,blob in files.items()],
        commit_message=message)
    return str(getattr(result,"oid",None) or api.repo_info(SPACE,repo_type="space").sha)


def publish(api: HfApi, candidate_path: Path) -> None:
    if os.environ.get("SWRLZ_UI_1060_DEPLOY_APPROVED") != "1":
        raise PermissionError("Explicit source-pinned UI deployment approval missing")
    manifest = json.loads((BACKUP/"manifest.json").read_text())
    original = {name: (BACKUP/name).read_bytes() for name in FILES}
    edited = {name: (BACKUP/"candidate"/name).read_bytes() for name in FILES}
    if manifest["space"]!=SPACE or api.repo_info(SPACE,repo_type="space").sha!=manifest["revision"]:
        raise RuntimeError("LIVE_REVISION_DRIFT before publish")
    if manifest["sourceSha256"] != digest(candidate_path.read_bytes()):
        raise RuntimeError("Candidate source changed since preflight")
    if {p:digest(b) for p,b in original.items()} != manifest["before"]:
        raise RuntimeError("Preflight source snapshot changed")
    if {p:digest(b) for p,b in edited.items()} != manifest["after"]:
        raise RuntimeError("Preflight candidate changed")
    actual = read_space_files(api, manifest["revision"])
    if actual != original:
        raise RuntimeError("LIVE_FILE_DRIFT before publish")
    revision = None
    try:
        revision = upload(api, manifest["revision"], edited,
            "§C: preserve live composer geometry in professional Chat UI release")
        emit("COMMITTED", revision=revision, previous=manifest["revision"])
        verify = read_space_files(api, revision)
        if verify != edited:
            raise RuntimeError("Published source does not match exact candidate")
        emit("EXACT_READBACK_PASS", revision=revision)
        expected_version = re.search(r'swrlz-chat-version" content="([^"]+)"',
                                     edited[UI].decode("utf-8")).group(1)
        for attempt in range(1,21):
            if api.repo_info(SPACE,repo_type="space").sha != revision:
                raise RuntimeError("CONCURRENT_SPACE_COMMIT during served-page check")
            ok, detail = served_version(expected_version)
            if ok:
                emit("LIVE_ACCEPTED", revision=revision, servedPath=detail, attempt=attempt,
                     files=list(FILES))
                return
            emit("SERVED_PENDING", attempt=attempt, detail=detail)
            time.sleep(10)
        raise RuntimeError("Chat UI design did not appear with expected version: "+expected_version)
    except Exception as exc:
        emit("RELEASE_REJECTED", error=type(exc).__name__, detail=str(exc)[:300],
             revision=revision)
        if revision is not None and api.repo_info(SPACE,repo_type="space").sha == revision:
            previous = upload(api, revision, original, "Rollback §C UI 1.0.60 to exact pre-release Chat")
            emit("ROLLED_BACK_EXACT_CHAT_FILES", revision=previous)
        elif revision is not None:
            emit("ROLLBACK_BLOCKED_BY_CONCURRENT_SPACE_UPDATE")
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("inspect","publish"))
    parser.add_argument("--source",type=Path,required=True)
    args = parser.parse_args()
    api = api_client()
    if args.mode == "inspect":
        snapshot(api,args.source)
    else:
        publish(api,args.source)


if __name__ == "__main__":
    main()
