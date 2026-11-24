"""Real model -> verified source -> patch -> validation -> owner review loop.

No model-generated text can authorize a GitHub write or Hugging Face deploy.
This generator yields only an honest receipt or a testable validation blocker.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
from urllib.parse import quote

try:
    from html_project_agent_v1 import (
        prompt_messages, apply_proposal, inspect_static, ProposalError,
        verify_source, MAX_ROUNDS
    )
    import html_project_repair_v1 as approval
    import github_html_publish_action_v1 as publishing
except ImportError:  # repository-unit-test layout
    from api.html_project_agent_v1 import (
        prompt_messages, apply_proposal, inspect_static, ProposalError,
        verify_source, MAX_ROUNDS
    )
    from api import html_project_repair_v1 as approval
    from api import github_html_publish_action_v1 as publishing

MAX_GENERATED_CHARS = 52_000
TEXT_EXTENSIONS = frozenset((".html", ".htm", ".js", ".mjs",
                             ".css", ".json", ".svg"))


def _source_files(owner, project):
    """Read manifest-pinned files under existing owner's Google/GitHub OAuth."""
    auth = publishing._authorized(owner)
    sha = publishing._head(auth)
    manifest = publishing._manifest(auth, sha, project["project"])
    if manifest["repo"] != project["repo"] or manifest["sourceSha"] != sha:
        raise ProposalError("WRONG_REPOSITORY")
    source_files = {}
    for info in manifest["files"]:
        rel = info["path"]
        if not rel.lower().endswith(TEXT_EXTENSIONS):
            continue
        path = "html-projects/" + project["project"] + "/" + rel
        response = publishing._github(
            auth, "GET", "contents/" + quote(path, safe="/"),
            params={"ref": sha})
        if not isinstance(response, dict) or response.get("encoding") != "base64":
            raise ProposalError("SOURCE_UNAVAILABLE")
        try:
            raw = base64.b64decode(
                str(response.get("content") or "").replace("\n", ""),
                validate=True)
            actual = hashlib.sha1(
                b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if response.get("sha") != actual or len(raw) != info["bytes"]:
                raise ProposalError("GITHUB_BLOB_MISMATCH")
            source_files[rel] = raw.decode("utf-8")
        except (UnicodeError, ValueError) as exc:
            raise ProposalError("SOURCE_INVALID") from exc
    verify_source(project["project"], source_files)
    return sha, source_files


def _parse_json(text):
    cleaned = str(text or "").strip()
    if cleaned.startswith("~~~"):
        cleaned = re.sub(r"^~~~(?:json)?\s*", "", cleaned, count=1, flags=re.I)
        cleaned = re.sub(r"\s*~~~$", "", cleaned)
    if cleaned.startswith("\x60\x60\x60"):
        cleaned = re.sub(r"^\x60{3}(?:json)?\s*", "", cleaned, count=1, flags=re.I)
        cleaned = re.sub(r"\s*\x60{3}$", "", cleaned)
    try:
        return json.loads(cleaned)
    except (ValueError, TypeError) as exc:
        raise ProposalError("MODEL_DID_NOT_RETURN_JSON") from exc


def _model_patch(coder_generate, base_payload, messages):
    """Invoke the existing §C coding model; do not reimplement inference."""
    system = messages[0]["content"]
    task = messages[1]["content"]
    model_payload = dict(base_payload)
    model_payload["prompt"] = (
        "SOURCE-PRESERVING EXISTING PROJECT REPAIR TASK\n"
        + system + "\nVERIFIED REPOSITORY SOURCE AND DIAGNOSTICS:\n" + task
        + "\nRETURN A SINGLE JSON OBJECT ONLY. No HTML page, no markdown."
    )
    model_payload["history"] = []
    model_payload["programmingIntent"] = {
        "codingTask": False, "source": "verified-existing-project-patch"
    }
    model_payload["githubSourceChangeTask"] = "plan"
    model_payload["responseDirective"] = (
        "Return only a single exact JSON patch proposal conforming to the "
        "swrlz-html-repair-agent-v1 contract. Never return a replacement page, "
        "review instructions, prose, or approval claims."
    )
    model_payload.pop("codeContinuation", None)
    output = []
    complete = False
    producer = iter(coder_generate(model_payload))
    try:
        for item in producer:
            if callable(base_payload.get("_cancelCheck")) and base_payload["_cancelCheck"]():
                raise ProposalError("CANCELLED")
            if not isinstance(item, dict):
                continue
            kind = str(item.get("type") or "").upper()
            if kind == "DELTA":
                output.append(str(item.get("text") or ""))
                if sum(map(len, output)) > MAX_GENERATED_CHARS:
                    raise ProposalError("MODEL_PATCH_TOO_LARGE")
            elif kind in ("CANCELLED", "FAILED"):
                raise ProposalError("MODEL_" + kind)
            elif kind in ("COMPLETED", "COMPLETE"):
                if item.get("outputIncomplete"):
                    raise ProposalError("MODEL_PATCH_INCOMPLETE")
                complete = True
    finally:
        close = getattr(producer, "close", None)
        if callable(close):
            close()
    if not complete:
        raise ProposalError("MODEL_GENERATION_INCOMPLETE")
    return _parse_json("".join(output))


def run(payload, coder_generate):
    """Finite verify/revise loop. Return owner approval widget, never a write."""
    if not approval.should_route(payload):
        raise ProposalError("INVALID_REPAIR_CONTEXT")
    owner = payload.get("htmlRepairOwner")
    thread = payload.get("htmlRepairThreadId")
    project = payload["activeHtmlProject"]
    if not isinstance(owner, str) or not owner.startswith("google:") or not thread:
        yield {"type": "STATUS", "phase": "REPAIR_AUTH_REQUIRED"}
        yield {"type": "DELTA", "text":
               "Owner-authenticated project repair is unavailable in this session. "
               "No GitHub mutation or deployment occurred."}
        yield {"type": "COMPLETED", "phase": "PARTIAL",
               "blocker": "OWNER_CONTEXT_MISSING"}
        return
    yield {"type": "STATUS", "phase": "REPAIR_READING_SOURCE",
           "reason": "Reading immutable owner GitHub project files."}
    try:
        sha, files = _source_files(owner, project)
        source_hashes = verify_source(project["project"], files)
        task = str(payload.get("receivedText") or payload.get("prompt") or "")
        diagnostics = [str(payload.get("projectFileEvidence") or "")[:2500]]
        failures = []
        for attempt in range(MAX_ROUNDS):
            if callable(payload.get("_cancelCheck")) and payload["_cancelCheck"]():
                raise ProposalError("CANCELLED")
            yield {"type": "STATUS", "phase": "REPAIR_MODEL_PATCH",
                   "reason": "Model patch attempt " + str(attempt + 1) + "/" + str(MAX_ROUNDS)}
            messages = prompt_messages(
                project["project"], files, diagnostics, task,
                prior_failures=failures)
            try:
                proposal = _model_patch(coder_generate, payload, messages)
                result = apply_proposal(
                    project["project"], files, proposal,
                    expected_hashes=source_hashes,
                    validation=inspect_static)
                if not result["readyForOwnerReview"]:
                    raise ProposalError("VALIDATION_NOT_VERIFIED")
                review = approval.prepare_model(
                    owner, thread, project["project"], sha,
                    proposal, source_hashes, result)
                yield {"type": "WIDGET", "widget": review}
                yield {"type": "STATUS", "phase": "REPAIR_REVIEW_READY",
                       "reason": "Exact patches passed the browser-free static validator."}
                yield {"type": "DELTA", "text": (
                    "The coding model proposed a source-preserving repair to "
                    + ", ".join(result["changedFiles"])
                    + ". Exact source hashes and static checks passed. "
                    "Review the proposed diff and reply YES to request a GitHub "
                    "repair PR, or NO to cancel. No GitHub write, browser run "
                    "or Hugging Face deployment has occurred.")}
                yield {"type": "COMPLETED", "phase": "COMPLETE"}
                return
            except (ProposalError, ValueError, TypeError) as exc:
                failures.append(str(exc)[:240])
                yield {"type": "STATUS", "phase": "REPAIR_PATCH_REJECTED",
                       "reason": str(exc)[:240], "attempt": attempt + 1}
        raise ProposalError("MAX_REPAIR_ATTEMPTS_EXHAUSTED: " + ", ".join(failures[-3:]))
    except (ProposalError, publishing.PublishActionError, approval.RepairError) as exc:
        reason = str(exc)[:500]
        yield {"type": "DELTA", "text": (
            "The repair did not pass source, model-output and static validation: "
            + reason + ". No GitHub change or deployment is verified.")}
        yield {"type": "COMPLETED", "phase": "PARTIAL",
               "blocker": "UNVERIFIED_REPAIR"}
