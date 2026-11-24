"""Owner-reviewed bridge from validated §C code artifacts to an HTML project in GitHub.

This module DOES NOT infer write authorization from the model. A user must
explicitly request both GitHub and publication, then independently approve
the GitHub commit and Hugging Face deployment in the same conversation.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import re
import threading
import time
from urllib.parse import quote

import github_html_publish_action_v1 as publishing

REPO = publishing.REPO
TTL = 300
# Retain expired decisions briefly so a late approval receives an authoritative
# refusal rather than falling through to a language-model-generated claim.
EXPIRED_RECEIPT_TTL = 3600
_DECISION_YES = re.compile(r"\s*(?:yes|yes please|yep|yup|confirm|approved|approve|go ahead|do it|proceed)\s*[.!]?\s*", re.I)
_DECISION_NO = re.compile(r"\s*(?:no|nope|cancel|decline|rejected|reject|stop|never mind|nevermind)\s*[.!]?\s*", re.I)
MAX_FILES = publishing.MAX_FILES
MAX_BYTES = publishing.MAX_BYTES
SAFE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
SLUG = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?\Z")
TEXT_EXT = frozenset({".html", ".htm", ".css", ".js", ".mjs", ".json", ".svg"})
_lock = threading.RLock()
_pending = {}


class HandoffError(Exception):
    def __init__(self, code):
        self.code = str(code)
        super().__init__(self.code)


def intent(prompt):
    """Classify an explicit compound creation request; never authorize a mutation."""
    if not isinstance(prompt, str) or len(prompt) > 12000:
        return None
    p = re.sub(r"\s+", " ", prompt).lower()
    if re.search(r"\b(?:do not|don't|never|without)\s+(?:\w+\s+){0,3}(?:publish|deploy|upload|commit)\b", p):
        return None
    categories = (
        r"\b(?:html|webpage|web\s*page|website|web\s*site|web\s*app|webapp)\b",
        r"\b(?:github|repository|repo)\b",
        r"\b(?:publish|deploy|host|go live|put (?:it|this) live)\b",
        r"\b(?:create|build|make|generate|write|develop|code)\b",
    )
    if not all(re.search(pattern, p) for pattern in categories):
        return None
    named = re.search(
        r"\b(?:project|website|site|webpage)\s+(?:named|called)\s+([a-z0-9][a-z0-9-]{1,47})\b", p
    )
    return {"kind": "html-project-generate-and-publish",
            "requestedSlug": named.group(1) if named else ""}


def is_saved_review_request(prompt):
    """Explicit owner request to review the latest stored artifact in this thread."""
    return bool(isinstance(prompt, str) and re.fullmatch(
        r"\\s*@github\\s+review\\s+saved\\s+html\\s+project\\s*[.!]?\\s*",
        prompt, re.I))


def _source_hash(files):
    normalized = [
        {"path": str(f.get("path") or ""),
         "language": str(f.get("language") or ""),
         "content": str(f.get("content") or "")}
        for f in files
    ]
    serialized = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _slug(artifact, hinted):
    if hinted and SLUG.fullmatch(hinted):
        return hinted
    index = next((f.get("content") or "" for f in artifact["files"] if f["path"] == "index.html"), "")
    title = re.search(r"<title[^>]*>([^<]{1,120})</title\s*>", index, re.I)
    label = title.group(1) if title else ""
    label = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:48].strip("-")
    if len(label) >= 3 and SLUG.fullmatch(label):
        return label
    return "html-" + str(artifact["currentSourceHash"])[:12]


def _validated(artifact):
    if not isinstance(artifact, dict) or artifact.get("type") != "code":
        raise HandoffError("NO_VALIDATED_CODE_ARTIFACT")
    files = artifact.get("files")
    if not isinstance(files, list) or not (1 <= len(files) <= MAX_FILES):
        raise HandoffError("PROJECT_FILE_COUNT_INVALID")
    current_hash = str(artifact.get("currentSourceHash") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", current_hash) or _source_hash(files) != current_hash:
        raise HandoffError("PROJECT_ARTIFACT_HASH_MISMATCH")
    out, seen, total = [], set(), 0
    for f in files:
        if not isinstance(f, dict) or not isinstance(f.get("path"), str) or not isinstance(f.get("content"), str):
            raise HandoffError("PROJECT_FILE_INVALID")
        rel = f["path"].replace("\\", "/")
        parts = rel.split("/")
        if len(parts) > 8 or not all(part and not part.startswith(".") and SAFE.fullmatch(part) for part in parts):
            raise HandoffError("PROJECT_PATH_UNSAFE")
        ext = "." + parts[-1].rsplit(".", 1)[-1].lower() if "." in parts[-1] else ""
        if ext not in TEXT_EXT or rel.lower() in seen:
            raise HandoffError("PROJECT_PATH_DUPLICATE_OR_UNSUPPORTED")
        data = f["content"]
        if "\x00" in data:
            raise HandoffError("PROJECT_BINARY_NOT_ALLOWED")
        count = len(data.encode("utf-8"))
        total += count
        if total > MAX_BYTES:
            raise HandoffError("PROJECT_TOO_LARGE")
        seen.add(rel.lower())
        out.append({"path": rel, "content": data, "bytes": count})
    if "index.html" not in seen:
        raise HandoffError("PROJECT_INDEX_MISSING")
    # This Space intentionally has a sandboxed, network-disabled CSP.
    for f in out:
        if f["path"].lower().endswith((".html", ".css")) and re.search(
            r"""(?:<script[^>]+src\s*=\s*["']https?://|<link[^>]+href\s*=\s*["']https?://|@import\s+(?:url\()?["']?https?://)""",
            f["content"], re.I):
            raise HandoffError("REMOTE_DEPENDENCY_INCOMPATIBLE_WITH_SANDBOX")
    return out, total


def stage(user_id, thread_id, artifact, request):
    """Create only a time-limited in-memory approval proposal; zero GitHub writes."""
    if not str(user_id or "").startswith("google:"):
        raise HandoffError("SIGN_IN_REQUIRED")
    if not isinstance(request, dict) or request.get("kind") != "html-project-generate-and-publish":
        raise HandoffError("EXPLICIT_PUBLISH_INTENT_REQUIRED")
    files, total = _validated(artifact)
    slug = _slug(artifact, str(request.get("requestedSlug") or ""))
    if not SLUG.fullmatch(slug):
        raise HandoffError("PROJECT_SLUG_INVALID")
    preview = {
        "mode": "create", "repo": REPO, "branch": "main", "project": slug,
        "sourceSha": artifact["currentSourceHash"], "sourceHash": artifact["currentSourceHash"],
        "artifactId": str(artifact.get("id") or ""), "artifactRevision": int(artifact.get("currentRevision") or 0),
        "files": [{"path": f["path"], "bytes": f["bytes"]} for f in files],
        "bytes": total, "destinationPrefix": "html-projects/" + slug + "/",
        "expiresInSeconds": TTL,
    }
    with _lock:
        _pending[(user_id, thread_id)] = {
            "expires": time.monotonic() + TTL,
            "slug": slug, "files": copy.deepcopy(files),
            "sourceHash": artifact["currentSourceHash"], "artifactId": preview["artifactId"],
            "artifactRevision": preview["artifactRevision"],
        }
    return {"contract": "swrlz-widget-v1", "kind": "github-html-publish-review",
            "title": "Review GitHub HTML project creation", "provider": "GitHub", "data": preview}


def is_decision(prompt):
    return bool(isinstance(prompt, str) and
                (_DECISION_YES.fullmatch(prompt) or _DECISION_NO.fullmatch(prompt)))


def decision_approved(prompt):
    if not is_decision(prompt):
        raise HandoffError("EXPLICIT_DECISION_REQUIRED")
    return bool(_DECISION_YES.fullmatch(prompt))


def has_approval_record(user_id, thread_id):
    with _lock:
        p = _pending.get((user_id, thread_id))
        if not p:
            return False
        if time.monotonic() - p["expires"] > EXPIRED_RECEIPT_TTL:
            _pending.pop((user_id, thread_id), None)
            return False
        return True


def has_pending(user_id, thread_id):
    with _lock:
        p = _pending.get((user_id, thread_id))
        return bool(p and p["expires"] > time.monotonic())


def expire(user_id, thread_id):
    with _lock:
        _pending.pop((user_id, thread_id), None)


def _create_project(auth, project):
    """One non-forced, immutable multi-file Git commit, never overwrite files."""
    sha = publishing._head(auth)
    commit = publishing._github(auth, "GET", "git/commits/" + sha)
    root_tree = str((commit.get("tree") or {}).get("sha") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", root_tree):
        raise HandoffError("BASE_TREE_UNVERIFIED")
    tree = publishing._github(auth, "GET", "git/trees/" + root_tree, params={"recursive": "1"})
    if not isinstance(tree, dict) or tree.get("truncated") is not False:
        raise HandoffError("BASE_TREE_UNAVAILABLE")
    prefix = "html-projects/" + project["slug"] + "/"
    if any(str(entry.get("path") or "").startswith(prefix) for entry in tree.get("tree") or []):
        raise HandoffError("PROJECT_ALREADY_EXISTS_NO_OVERWRITE")
    elements = []
    for f in project["files"]:
        blob = publishing._github(auth, "POST", "git/blobs", data={
            "content": f["content"], "encoding": "utf-8"})
        blob_sha = str(blob.get("sha") or "")
        if not re.fullmatch(r"[a-f0-9]{40}", blob_sha):
            raise HandoffError("BLOB_UNVERIFIED")
        elements.append({"path": prefix + f["path"], "mode": "100644",
                         "type": "blob", "sha": blob_sha})
    built = publishing._github(auth, "POST", "git/trees",
                               data={"base_tree": root_tree, "tree": elements})
    tree_sha = str(built.get("sha") or "")
    if not re.fullmatch(r"[a-f0-9]{40}", tree_sha):
        raise HandoffError("PROJECT_TREE_UNVERIFIED")
    result = publishing._github(auth, "POST", "git/commits", data={
        "message": "feat(§C): create owner-approved HTML project " + project["slug"],
        "tree": tree_sha, "parents": [sha]})
    new_sha = str(result.get("sha") or "")
    if not re.fullmatch(r"[a-f0-9]{40}", new_sha):
        raise HandoffError("PROJECT_COMMIT_UNVERIFIED")
    # Non-force rejects concurrent writes rather than overwriting main.
    publishing._github(auth, "PATCH", "git/refs/heads/main",
                       data={"sha": new_sha, "force": False})
    for f in project["files"]:
        found = publishing._github(
            auth, "GET", "contents/" + quote(prefix + f["path"], safe="/"),
            params={"ref": new_sha})
        if found.get("encoding") != "base64" or base64.b64decode(
            str(found.get("content") or "").replace("\n", ""), validate=True
        ) != f["content"].encode("utf-8"):
            raise HandoffError("COMMITTED_BYTES_NOT_VERIFIED")
    return new_sha


def confirm(user_id, thread_id, approved):
    if type(approved) is not bool:
        raise HandoffError("EXPLICIT_BOOLEAN_REQUIRED")
    with _lock:
        project = _pending.pop((user_id, thread_id), None)
    if project is None or project["expires"] <= time.monotonic():
        raise HandoffError("GITHUB_CREATE_APPROVAL_EXPIRED")
    if not approved:
        return {"text": "GitHub project creation rejected. No repository write or deployment was authorized."}
    try:
        auth = publishing._authorized(user_id)
        sha = _create_project(auth, project)
    except publishing.PublishActionError as exc:
        raise HandoffError(exc.code) from exc
    result = {"text": (
        "Created HTML project " + project["slug"] + " at commit " + sha +
        ". All generated file bytes were verified against GitHub. "
        "Preparing separate Hugging Face deployment approval. "),
        "commitSha": sha, "project": project["slug"],
    }
    try:
        deployment = publishing.prepare(user_id, thread_id, project["slug"])
    except publishing.PublishActionError as exc:
        result["text"] += ("Deployment review not prepared (" + exc.code +
            "). The GitHub commit remains saved; request @GitHub publish HTML project " +
            project["slug"] + " after resolving the problem.")
        return result
    result["widget"] = {"contract": "swrlz-widget-v1", "kind": "github-html-publish-review",
                        "title": "Review HTML project deployment", "provider": "GitHub",
                        "data": deployment}
    result["text"] += "Approve the separate deployment review to publish to the existing §C Space."
    return result
