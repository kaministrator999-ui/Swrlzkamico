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
        prompt_messages, apply_proposal, bind_model_edits, inspect_static, ProposalError,
        verify_source, MAX_ROUNDS
    )
    import html_project_repair_v1 as approval
except ImportError:  # repository-unit-test layout
    from api.html_project_agent_v1 import (
        prompt_messages, apply_proposal, bind_model_edits, inspect_static, ProposalError,
        verify_source, MAX_ROUNDS
    )
    from api import html_project_repair_v1 as approval

try:
    from html_project_dependency_tool_v1 import MAP, pinned_url, DependencyError
except ImportError:
    from api.html_project_dependency_tool_v1 import MAP, pinned_url, DependencyError

MAX_GENERATED_CHARS = 52_000
REPAIR_LOOP_VERSION = "swrlz-evidence-tool-loop-v12"
TEXT_EXTENSIONS = frozenset((".html", ".htm", ".js", ".mjs",
                             ".css", ".json", ".svg"))


def _source_files(owner, project):
    """Read manifest-pinned files under existing owner's Google/GitHub OAuth."""
    try:
        import github_html_publish_action_v1 as publishing
    except ImportError:
        from api import github_html_publish_action_v1 as publishing
    auth = publishing._authorized(owner)
    sha = publishing._head(auth)
    manifest = publishing._manifest(auth, sha, project["project"])
    if manifest["repo"] != project["repo"] or manifest["sourceSha"] != sha:
        raise ProposalError("WRONG_REPOSITORY")
    source_files = {}
    for info in manifest["files"]:
        rel = info["path"]
        if not rel.lower().endswith(tuple(TEXT_EXTENSIONS)):
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
    # Isolate repair inference from the outer conversation's GitHub plan,
    # evidence-report, artifact-generation, and approval contracts.
    model_payload = {key: base_payload[key] for key in (
        "requestId", "threadId", "_cancelCheck"
    ) if key in base_payload}
    # swrlz-exact-patches-v10: legacy source pin lineage.
    model_payload["modelId"] = "coder"
    model_payload["repairPatchProtocol"] = "swrlz-exact-patches-v11"
    model_payload["prompt"] = (
        "SOURCE-PRESERVING EXISTING PROJECT REPAIR TASK\n"
        + system + "\nVERIFIED REPOSITORY SOURCE AND DIAGNOSTICS:\n" + task
        + "\nRETURN A SINGLE JSON OBJECT ONLY. No HTML page, no markdown."
    )
    model_payload["history"] = []
    model_payload["programmingIntent"] = {
        "codingTask": False, "source": "verified-existing-project-patch"
    }
    model_payload["presentationIntent"] = "PROSE"
    # githubSourceChangeTask selects a DIFFERENT constrained JSON grammar in
    # qwen_coder_engine. Never send it for exact existing-project repairs.
    model_payload["responseDirective"] = (
        "Return a single JSON object containing patches [{path, op, anchor, code}]. "
        "Use localize_imports for source-declared pinned npm importmap CSP violations. "
        "Do not substitute another CDN. "
        "Do not calculate source hashes or supply schema/project identity; the trusted "
        "server binds those. Never return a replacement page, review instructions, "
        "prose, or approval claims."
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
    parsed = _parse_json("".join(output))
    if not isinstance(parsed, dict):
        raise ProposalError("INVALID_MODEL_PATCH_PROPOSAL: expected JSON object, got " +
                            type(parsed).__name__)
    return parsed


def requested_publish_after_approval(task):
    """Approval scope is derived only from the user's explicit instruction."""
    text=str(task or "")
    if re.search(r"\b(?:do not|don't|never|without|no)\s+(?:deploy|publish|deployment|publication)\b",text,re.I):
        return False
    return bool(re.search(r"\b(?:once|after|upon)\s+(?:you\s+)?(?:approved|approval|approve)\b[^.!?]{0,100}\b(?:deploy|publish)\b",text,re.I))

DEPENDENCY_ISSUES = frozenset(("CSP_EXTERNAL_MODULE", "BARE_MODULE_UNRESOLVED",
                               "LOCAL_MODULE_MISSING"))

def dependency_actions(files, baseline):
    """Discover executable tool arguments from immutable source, never model paths."""
    issues = baseline.get("issues") or []
    affected = {i.get("file") for i in issues if isinstance(i,dict)
                and i.get("code") == "CSP_EXTERNAL_MODULE"}
    actions = []
    for path in sorted(affected & files.keys()):
        if not path.endswith((".html",".htm")):
            continue
        matches = list(MAP.finditer(files[path]))
        if len(matches) != 1:
            continue
        match = matches[0]
        try:
            obj = json.loads(match.group(1))
            mappings = obj["imports"]
            if set(obj) != {"imports"} or not isinstance(mappings,dict) or not mappings:
                continue
            for name,url in mappings.items():
                if not isinstance(name,str) or not isinstance(url,str):
                    raise DependencyError("INVALID_IMPORT_MAP")
                pinned_url(url)
        except (ValueError, TypeError, KeyError):
            continue
        anchor = match.group().split(">",1)[0]+">"
        if files[path].count(anchor) == 1:
            actions.append({"path":path,"op":"localize_imports","anchor":anchor,"code":""})
    return actions

def dependency_only_recovery(task, baseline, actions):
    """Automatic prerequisite recovery is scoped to broad load/render repair.
    
    Do not substitute a dependency-only candidate for a feature-specific task,
    change a project's security policy, or bypass a user restriction.
    """
    text = str(task or "")
    if re.search(r"\b(?:do not|don't|never|without|no)\s+(?:install|add|download|fetch|localize|change)\b[^.!?]{0,80}\b(?:dependencies|packages|libraries|assets|modules|imports)\b",text,re.I):
        return False
    if not re.search(r"\b(?:repair|fix|correct|resolve)\b",text,re.I):
        return False
    if not re.search(r"\b(?:render(?:ing)?|load(?:ing)?|startup|blank|broken|fails?|failure|not working|dependencies|modules|import\s*map|CSP)\b",text,re.I):
        return False
    # Do not silently drop a requested feature or additional UI/behavior change.
    if re.search(r"\b(?:add|implement|introduce|redesign|new feature|change the color|change the layout)\b",text,re.I):
        return False
    issues=baseline.get("issues") or []
    return bool(actions and issues and all(isinstance(i,dict) and
        i.get("code") in DEPENDENCY_ISSUES for i in issues))

def _cancel(payload):
    if callable(payload.get("_cancelCheck")) and payload["_cancelCheck"]():
        raise ProposalError("CANCELLED")

def repair_candidate(payload, coder_generate, project, files, task, diagnostics):
    """Shared production/probe repair loop; does not stage, commit or deploy."""
    source_hashes=verify_source(project,files)
    _cancel(payload)
    baseline=inspect_static(files)
    actions=dependency_actions(files,baseline)
    # Evidence is computed from the source we just pinned; old chat report text
    # is supplemental only and never defines the allowed tool arguments.
    evidence=[]
    if baseline.get("issues"):
        evidence.append({"originalStaticIssues":baseline["issues"][:12]})
    if actions:
        evidence.append({"availableToolCalls":actions,
                         "instruction":"Use the exact available localize_imports call to obtain real pinned assets. Repointing to node_modules or another CDN cannot create files."})
    evidence.extend(list(diagnostics or [])[:4])
    failures=[]
    recover=dependency_only_recovery(task,baseline,actions)
    for attempt in range(MAX_ROUNDS):
        _cancel(payload)
        yield {"type":"STATUS","phase":"REPAIR_MODEL_PATCH",
               "reason":"Model patch attempt "+str(attempt+1)+"/"+str(MAX_ROUNDS)}
        messages=prompt_messages(project,files,evidence,task,prior_failures=failures)
        try:
            raw=_model_patch(coder_generate,payload,messages)
            edits=raw.get("patches")
            if isinstance(edits,list) and any(isinstance(p,dict) and p.get("op")=="localize_imports" for p in edits):
                yield {"type":"STATUS","phase":"REPAIR_DEPENDENCIES",
                       "reason":"Coding model selected pinned dependency localization."}
            proposal=bind_model_edits(project,files,raw)
            result=apply_proposal(project,files,proposal,expected_hashes=source_hashes,validation=inspect_static)
            _cancel(payload)
            if not result["readyForOwnerReview"]:
                raise ProposalError("VALIDATION_NOT_VERIFIED")
            return proposal,result,"model",failures
        except (ProposalError,ValueError,TypeError) as exc:
            _cancel(payload)
            if str(exc)=="CANCELLED":
                raise
            failures.append(str(exc)[:1800])
            yield {"type":"STATUS","phase":"REPAIR_PATCH_REJECTED",
                   "reason":str(exc)[:360],"attempt":attempt+1}
            if recover:
                # The model has attempted the task. Recover the missing executable
                # prerequisite using the capability discovered in the ORIGINAL
                # source. This is executor recovery, not a fabricated model edit.
                # All other rejected edits are discarded. Approval remains required.
                yield {"type":"STATUS","phase":"REPAIR_DEPENDENCIES",
                       "reason":"Repair executor recovering verified missing dependency assets from the original source."}
                try:
                    _cancel(payload)
                    raw={"patches":actions,"rationale":"Evidence-driven executor recovery of pinned dependency assets after rejected model patch."}
                    proposal=bind_model_edits(project,files,raw)
                    result=apply_proposal(project,files,proposal,expected_hashes=source_hashes,validation=inspect_static)
                    _cancel(payload)
                    if not result["readyForOwnerReview"]:
                        raise ProposalError("DEPENDENCY_RECOVERY_NOT_VERIFIED")
                    return proposal,result,"executor-dependency-recovery",failures
                except (ProposalError,ValueError,TypeError) as fallback_error:
                    _cancel(payload)
                    if str(fallback_error)=="CANCELLED":
                        raise
                    failures.append("DEPENDENCY_RECOVERY_FAILED: "+str(fallback_error)[:1000])
                    yield {"type":"STATUS","phase":"REPAIR_PATCH_REJECTED",
                           "reason":failures[-1][:360],"attempt":attempt+1}
                    # Do not redownload or retry the same failing capability.
                    recover=False
    raise ProposalError("MAX_REPAIR_ATTEMPTS_EXHAUSTED:\n"+"\n".join(
        "Attempt evidence "+str(i+1)+": "+reason[:500] for i,reason in enumerate(failures[-5:])))

def run(payload, coder_generate):
    """Owner-authenticated source -> shared candidate loop -> owner review."""
    if not approval.should_route(payload):
        raise ProposalError("INVALID_REPAIR_CONTEXT")
    owner=payload.get("htmlRepairOwner")
    thread=payload.get("htmlRepairThreadId")
    project=payload["activeHtmlProject"]
    if not isinstance(owner,str) or not owner.startswith("google:") or not thread:
        yield {"type":"STATUS","phase":"REPAIR_AUTH_REQUIRED"}
        yield {"type":"DELTA","text":"Owner-authenticated project repair is unavailable in this session. No GitHub mutation or deployment occurred."}
        yield {"type":"COMPLETED","phase":"PARTIAL","blocker":"OWNER_CONTEXT_MISSING"}
        return
    yield {"type":"STATUS","phase":"REPAIR_READING_SOURCE",
           "reason":"Reading immutable owner GitHub project files."}
    try:
        sha,files=_source_files(owner,project)
        source_hashes=verify_source(project["project"],files)
        task=str(payload.get("receivedText") or payload.get("prompt") or "")
        diagnostics=[str(payload.get("projectFileEvidence") or "")[:1200]]
        proposal,result,origin,failures=yield from repair_candidate(
            payload,coder_generate,project["project"],files,task,diagnostics)
        _cancel(payload)
        full_delivery=requested_publish_after_approval(task)
        review=approval.prepare_model(owner,thread,project["project"],sha,proposal,
                                     source_hashes,result,publish_after_validation=full_delivery)
        yield {"type":"WIDGET","widget":review}
        yield {"type":"STATUS","phase":"REPAIR_REVIEW_READY",
               "reason":"Exact patches passed the browser-free static validator; origin: "+origin}
        lead=("The coding model proposed a source-preserving repair to " if origin=="model"
              else "The coding model's patch was rejected; the repair executor recovered the verified dependency assets. The source-preserving candidate changes ")
        yield {"type":"DELTA","text":lead+", ".join(result["changedFiles"])+
               ". Exact source hashes and static checks passed. "+
               ("Review the diff and reply YES to authorize browser validation, the source-pinned GitHub commit, Hugging Face deployment, and live browser verification. "
                if full_delivery else "Review the diff and reply YES to authorize browser validation and a GitHub repair PR only. ")+
               "Reply NO to cancel. No GitHub write, browser run or Hugging Face deployment has occurred."}
        yield {"type":"COMPLETED","phase":"COMPLETE"}
    except Exception as exc:
        reason=str(exc)[:3500]
        yield {"type":"DELTA","text":"The repair did not pass source, model-output and static validation:\n\n"+reason+
               "\n\nNo GitHub change or deployment is verified."}
        yield {"type":"COMPLETED","phase":"PARTIAL","blocker":"UNVERIFIED_REPAIR"}
