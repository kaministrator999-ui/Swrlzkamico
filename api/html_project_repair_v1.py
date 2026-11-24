"""Owner-reviewed, source-preserving HTML repair bridge.

Natural repair intent never grants GitHub write authority. A separate same-thread
approval dispatches a pinned GitHub Actions builder that proposes a PR.
"""
from __future__ import annotations
import base64
import hashlib
import re
import threading
import time

SLUG = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?\Z")
COMMAND = re.compile(r"^\s*@github\s+repair\s+(?:html\s+)?project\s+([a-z0-9][a-z0-9-]{1,47})\s*[.!]?\s*$", re.I)
REPAIR = re.compile(r"\b(?:fix|repair|patch|bundle|resolve|correct|update|modify|redeploy|make\s+(?:it|this)\s+work)\b", re.I)
NO_CHANGES = re.compile(r"\b(?:do not|don't|without|no)\b.{0,100}\b(?:edit|modify|change|write|repair|commit)\b", re.I)
WORKFLOW = "hf-html-project-repair-pr-v1.yml"
WORKFLOW_URL = "https://github.com/kaministrator999-ui/Swrlzkamico/actions/workflows/" + WORKFLOW
TTL = 300
_lock = threading.RLock()
_pending = {}


class RepairError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def is_command(prompt):
    return bool(isinstance(prompt, str) and COMMAND.fullmatch(prompt))


def repair_intent(prompt):
    """Fix an existing project; read-only review is not a repair."""
    if not isinstance(prompt, str) or len(prompt) > 12000:
        return False
    if is_command(prompt) or NO_CHANGES.search(prompt):
        return False
    return bool(REPAIR.search(prompt))


def should_route(payload):
    if not isinstance(payload, dict):
        return False
    project = payload.get("activeHtmlProject")
    if not isinstance(project, dict) or not SLUG.fullmatch(str(project.get("project") or "")):
        return False
    evidence = payload.get("projectFileEvidence")
    if not isinstance(evidence, str) or not re.search(
            r"(?m)^Verified Git blob: [a-f0-9]{40}$", evidence):
        return False
    prompt = str(payload.get("receivedText") or payload.get("prompt") or "")
    return repair_intent(prompt) and not payload.get("githubSourceChangeTask")


def events(payload):
    """Produce an actionable, evidence-bound repair proposal, never fresh HTML."""
    project = payload["activeHtmlProject"]
    slug = project["project"]
    proof = re.search(r"(?m)^Verified Git blob: ([a-f0-9]{40})$",
                      payload["projectFileEvidence"]).group(1)
    cancel = payload.get("_cancelCheck")
    if callable(cancel) and cancel():
        yield {"type": "CANCELLED", "phase": "CANCELLED"}
        return
    yield {"type": "STATUS", "phase": "EXISTING_PROJECT_REPAIR",
           "reason": "Using the existing project and an owner-reviewed build workflow, not replacing the HTML."}
    lines = [
        "## Existing-project repair proposal",
        "**Project:** " + slug,
        "**Verified source blob:** " + proof,
        "**Operation:** targeted dependency repair, preserving the existing scene, "
        "controls, layout, project identity and sandbox policy.",
        "",
        "The repair workflow bundles the existing inline JavaScript module "
        "using pinned local Three.js dependencies, replaces only the remote "
        "import map and module script, verifies the artifact and opens a "
        "GitHub pull request for independent review.",
        "",
        "**Next step:** @GitHub repair HTML project " + slug,
        "That command opens an owner approval review. No PR is merged or "
        "published automatically. Publishing remains a separate approval.",
        "",
        "No GitHub files were modified or deployed by this proposal."
    ]
    if callable(cancel) and cancel():
        yield {"type": "CANCELLED", "phase": "CANCELLED"}
        return
    yield {"type": "DELTA", "text": "\n".join(lines)}
    yield {"type": "COMPLETED", "phase": "COMPLETE"}


def _verified_source(auth, slug):
    import github_html_publish_action_v1 as publishing
    entry = publishing._github(auth, "GET", "contents/html-projects/" + slug + "/index.html")
    if entry.get("type") != "file" or entry.get("encoding") != "base64":
        raise RepairError("SOURCE_UNAVAILABLE")
    try:
        raw = base64.b64decode(str(entry.get("content") or "").replace("\n", ""), validate=True)
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if actual != entry.get("sha") or len(raw) > 150_000:
            raise RepairError("SOURCE_BLOB_MISMATCH")
        code = raw.decode("utf-8")
    except (UnicodeError, ValueError, TypeError) as exc:
        raise RepairError("SOURCE_INVALID") from exc
    # Supported builder only: unknown repair patterns never enter generative overwrite.
    if (not re.search(r'<script\b[^>]*type=["\x27]importmap["\x27]', code, re.I)
            or "three@0.160.0" not in code
            or "three/addons/controls/OrbitControls.js" not in code
            or len(re.findall(r'<script\b[^>]*type=["\x27]module["\x27]', code, re.I)) != 1):
        raise RepairError("NO_VERIFIED_LOCAL_BUNDLE_STRATEGY")
    return entry["sha"], len(raw)


def prepare(user_id, thread_id, slug):
    import github_html_publish_action_v1 as publishing
    if not isinstance(slug, str) or not SLUG.fullmatch(slug):
        raise RepairError("INVALID_PROJECT")
    if not str(user_id or "").startswith("google:"):
        raise RepairError("GOOGLE_SIGN_IN_REQUIRED")
    try:
        auth = publishing._authorized(user_id)
        head = publishing._head(auth)
        manifest = publishing._manifest(auth, head, slug)
        blob, _ = _verified_source(auth, slug)
    except publishing.PublishActionError as exc:
        raise RepairError(exc.code) from exc
    if blob != manifest["indexGitBlobSha"]:
        raise RepairError("SOURCE_CHANGED")
    with _lock:
        _pending[(user_id, thread_id)] = {
            "expires": time.monotonic() + TTL, "project": slug,
            "sha": head, "blob": blob
        }
    return {"contract": "swrlz-widget-v1", "kind": "github-html-publish-review",
            "title": "Review source-preserving HTML repair",
            "provider": "GitHub",
            "data": {**manifest, "mode": "repair", "sourceBlob": blob,
                     "workflowUrl": WORKFLOW_URL, "expiresInSeconds": TTL,
                     "destinationPrefix": "html-projects/" + slug + "/",
                     "repairStrategy": "three-0.160.0-esbuild-local"}}


def has_pending(user_id, thread_id):
    with _lock:
        item = _pending.get((user_id, thread_id))
        return bool(item and item["expires"] > time.monotonic())


def expire(user_id, thread_id):
    with _lock:
        _pending.pop((user_id, thread_id), None)


def confirm(user_id, thread_id, approved):
    import github_html_publish_action_v1 as publishing
    if type(approved) is not bool:
        raise RepairError("EXPLICIT_BOOLEAN_REQUIRED")
    with _lock:
        proposal = _pending.pop((user_id, thread_id), None)
    if not proposal or proposal["expires"] < time.monotonic():
        raise RepairError("APPROVAL_MISSING_OR_EXPIRED")
    if not approved:
        return {"dispatched": False, "project": proposal["project"]}
    try:
        auth = publishing._authorized(user_id)
        if publishing._head(auth) != proposal["sha"]:
            raise RepairError("MAIN_CHANGED_REPREPARE")
        blob, _ = _verified_source(auth, proposal["project"])
        if blob != proposal["blob"]:
            raise RepairError("PROJECT_CHANGED_REPREPARE")
        publishing._github(auth, "POST", "actions/workflows/" + WORKFLOW + "/dispatches",
            data={"ref": "main", "inputs": {"source_sha": proposal["sha"],
                  "project": proposal["project"], "approved": "yes"}})
    except publishing.PublishActionError as exc:
        raise RepairError(exc.code) from exc
    return {"dispatched": True, "project": proposal["project"],
            "sourceSha": proposal["sha"], "workflowUrl": WORKFLOW_URL}
