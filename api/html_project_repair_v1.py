"""Owner-reviewed, source-preserving HTML repair bridge.

Natural repair intent never grants GitHub write authority. A separate same-thread
approval dispatches a pinned GitHub Actions builder that proposes a PR.
"""
from __future__ import annotations
import base64
import hashlib
import json
import re
import threading
import time

SLUG = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?\Z")
COMMAND = re.compile(r"^\s*@github\s+repair\s+(?:html\s+)?project\s+([a-z0-9][a-z0-9-]{1,47})\s*[.!]?\s*$", re.I)
REPAIR = re.compile(r"\b(?:fix|repair|patch|bundle|resolve|correct|update|modify|redeploy|make\s+(?:it|this)\s+work)\b", re.I)
NO_CHANGES = re.compile(
    r"\b(?:do not|don't|without|never)\s+(?:actually\s+|make\s+any\s+)?"
    r"(?:edit(?:ing|s)?|modify(?:ing)?|chang(?:e|es|ing)|writ(?:e|ing)|repair(?:ing|s)?|commit(?:ting|s)?)\b"
    r"(?!\s+(?:the\s+)?(?:entire|whole|unrelated|other)\b)"
    r"(?!\s+(?:until|before|without|unless)\b)"
    r"|\bno\s+(?:edits|changes|writes|repairs|commits)\b", re.I)
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
    # Verified owner project context takes precedence over generic GitHub planning.
    # A separate source-change classifier may have labeled the turn "plan",
    # but that label must not hide the existing-project repair agent.
    return repair_intent(prompt)


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



MODEL_WORKFLOW = "hf-html-project-agent-pr-v1.yml"
MODEL_WORKFLOW_URL = "https://github.com/kaministrator999-ui/Swrlzkamico/actions/workflows/" + MODEL_WORKFLOW


def prepare_model(user_id, thread_id, slug, head, patch_plan, source_hashes, result, *, publish_after_validation=False):
    """Store a reviewed model patch; no GitHub write until fresh owner YES."""
    import github_html_publish_action_v1 as publishing
    if (not isinstance(slug, str) or not SLUG.fullmatch(slug)
            or not str(user_id or "").startswith("google:")
            or not isinstance(head, str)
            or not re.fullmatch(r"[0-9a-f]{40}", head)):
        raise RepairError("INVALID_REPAIR_OWNER_OR_PROJECT")
    if not isinstance(result, dict) or result.get("readyForOwnerReview") is not True:
        raise RepairError("REPAIR_VALIDATION_REQUIRED")
    try:
        plan_text = json.dumps(patch_plan, ensure_ascii=False, separators=(",", ":"))
    except (ValueError, TypeError) as exc:
        raise RepairError("INVALID_MODEL_PATCH") from exc
    if len(plan_text.encode("utf-8")) > 48_000:
        raise RepairError("REPAIR_PLAN_TOO_LARGE_FOR_REVIEW")
    auth = publishing._authorized(user_id)
    if publishing._head(auth) != head:
        raise RepairError("MAIN_CHANGED_REPREPARE")
    manifest = publishing._manifest(auth, head, slug)
    if not isinstance(source_hashes, dict) or source_hashes != result.get("beforeHashes"):
        raise RepairError("SOURCE_HASHES_MISMATCH")
    files = result.get("changedFiles")
    if not isinstance(files, list) or not files:
        raise RepairError("EMPTY_REPAIR")
    assets = {}
    for patch in patch_plan.get("patches",[]):
        if patch.get("op")=="localize_imports":
            assets.update(patch.get("assetHashes",{}))
    after = result.get("afterHashes") or {}
    if any(path not in source_hashes and
           (not path.startswith("vendor/") or not assets.get(path) or assets[path]!=after.get(path))
           for path in files):
        raise RepairError("REPAIR_PATH_NOT_VERIFIED")
    with _lock:
        _pending[(user_id, thread_id)] = {
            "mode": "model", "expires": time.monotonic() + TTL,
            "project": slug, "sha": head,
            "blob": manifest["indexGitBlobSha"],
            "sourceHashes": dict(source_hashes),
            "plan": plan_text,
            "publishAfterValidation": publish_after_validation is True,
            "browserReceipt": result.get("validation",{}).get("browserReceipt"),
        }
    return {
        "contract": "swrlz-widget-v1", "kind": "github-html-publish-review",
        "title": "Review model-proposed existing-project repair",
        "provider": "GitHub",
        "data": {
            **manifest, "mode": "repair", "sourceBlob": manifest["indexGitBlobSha"],
            "repairStrategy": "model-exact-patch",
            "repairDiffs": result.get("diffs") or {},
            "repairValidation": result.get("validation") or {},
            "publishAfterValidation": publish_after_validation is True,
            "dependencyAssets": assets,
            "changedFiles": files,
            "workflowUrl": MODEL_WORKFLOW_URL,
            "expiresInSeconds": TTL,
            "destinationPrefix": "html-projects/" + slug + "/",
        },
    }


def _confirm_model(user_id, proposal):
    import github_html_publish_action_v1 as publishing
    try:
        from html_project_agent_runtime_v1 import _source_files
        from html_project_agent_v1 import verify_source
    except ImportError:
        from api.html_project_agent_runtime_v1 import _source_files
        from api.html_project_agent_v1 import verify_source
    project = {"project": proposal["project"],
               "repo": publishing.REPO}
    try:
        head, actual_files = _source_files(user_id, project)
        if head != proposal["sha"]:
            raise RepairError("MAIN_CHANGED_REPREPARE")
        if verify_source(proposal["project"], actual_files) != proposal["sourceHashes"]:
            raise RepairError("SOURCE_CHANGED_REPREPARE")
    except RepairError:
        raise
    except Exception as exc:
        raise RepairError("REPAIR_SOURCE_RECHECK_FAILED") from exc
    try:
        auth = publishing._authorized(user_id)
        inputs={"source_sha":proposal["sha"],"project":proposal["project"],"proposal_json":proposal["plan"],
                "publish_after_validation":"yes" if proposal.get("publishAfterValidation") is True else "no","approved":"yes"}
        if proposal.get("browserReceipt"):
            envelope=proposal["browserReceipt"]
            name="github_browser_receipt_json" if envelope.get("backend")=="github-actions" else "browser_receipt_json"
            inputs[name]=json.dumps(envelope,separators=(",",":"))
        publishing._github(auth,"POST","actions/workflows/"+MODEL_WORKFLOW+"/dispatches",
                           data={"ref":"main","inputs":inputs})
    except publishing.PublishActionError as exc:
        raise RepairError(exc.code) from exc
    return {"dispatched": True, "project": proposal["project"],
            "sourceSha": proposal["sha"], "workflowUrl": MODEL_WORKFLOW_URL,
            "strategy": "model-exact-patch",
            "publishAfterValidation": proposal.get("publishAfterValidation") is True}

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
    if proposal.get("mode") == "model":
        return _confirm_model(user_id, proposal)
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
