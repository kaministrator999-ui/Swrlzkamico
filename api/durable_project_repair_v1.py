"""Owner-verified existing-project repair route for the durable §C Workstation.

Only the actual authenticated account can read project source or confirm writes.
Project identity comes from the user's text, not model-generated instructions.
A read failure is a terminal blocker, never an invitation to generate a new page.
"""
from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

_DECISION = re.compile(r"^\s*(yes|approve|approved|no|cancel|decline)\s*[.!]?\s*$", re.I)


def _components():
    try:
        import html_project_context_v1 as context
        import html_project_repair_v1 as approval
        import html_project_agent_runtime_v1 as runtime
    except ImportError:
        from api import html_project_context_v1 as context
        from api import html_project_repair_v1 as approval
        from api import html_project_agent_runtime_v1 as runtime
    return context, approval, runtime


def _status(phase: str, reason: str = "") -> dict[str, Any]:
    return {"type": "STATUS", "phase": phase, "reason": reason}


def _finish() -> dict[str, Any]:
    return {"type": "COMPLETED", "phase": "COMPLETE"}


def _approval_events(approval, user_id: str, thread_id: str, accept: bool):
    yield _status("REPAIR_APPROVAL_DECISION", "Processing explicit same-thread decision.")
    try:
        result = approval.confirm(user_id, thread_id, accept)
    except Exception as exc:
        yield _status("REPAIR_APPROVAL_BLOCKED", type(exc).__name__)
        yield {"type": "DELTA", "text":
               "GitHub repair approval was not accepted (" + type(exc).__name__ +
               "). No commit, deployment, or PR has been verified."}
    else:
        if not accept:
            yield {"type": "DELTA", "text":
                   "The pending repair was cancelled. No GitHub write or deployment was authorized."}
        elif result.get("dispatched") is True:
            yield {"type": "DELTA", "text":
                   "The approved GitHub repair PR workflow was dispatched for " +
                   str(result.get("project") or "the selected project") + ". " +
                   "This is not a merged PR or deployment receipt. Verify the " +
                   "workflow result before publishing. " +
                   str(result.get("workflowUrl") or "")}
        else:
            yield {"type": "DELTA", "text":
                   "GitHub repair dispatch was not verified; no deployment is claimed."}
    yield _finish()


def _review_diff(widget: dict[str, Any]) -> str:
    data = widget.get("data") if isinstance(widget.get("data"), dict) else {}
    diffs = data.get("repairDiffs") if isinstance(data.get("repairDiffs"), dict) else {}
    if not diffs:
        return ("A repair review was prepared, but the source diff is unavailable in this "
                "chat channel. Do not approve without inspecting the exact patch.")
    pieces = ["## Proposed source changes", ""]
    remaining = 16000
    for path, change in sorted(diffs.items()):
        if remaining <= 0:
            break
        if not isinstance(path, str) or not isinstance(change, str):
            continue
        fragment = change[:min(remaining, 8000)]
        pieces.append("**" + path[:180] + "**\n\x60\x60\x60diff\n" +
                      fragment.replace("\x60\x60\x60", "\x60\x60 \x60") +
                      "\n\x60\x60\x60")
        remaining -= len(fragment)
    pieces.extend(("", "Only a static, source-pinned patch proposal was prepared. "
                   "No GitHub commit or deployment has occurred. "
                   "Reply YES within five minutes to request the GitHub repair PR, "
                   "or NO to cancel."))
    return "\n".join(pieces)


def _repair_events(context, approval, runtime, *,
                   user_id: str, thread_id: str, prompt: str, project: dict,
                   engine: Any, cancelled, base_payload: dict) -> Iterator[dict]:
    yield _status("EXISTING_PROJECT_REPAIR_SELECTED",
                  "Routing the named existing GitHub project, not creating a new HTML artifact.")
    if not user_id.startswith("google:"):
        yield _status("EXISTING_PROJECT_REPAIR_AUTH_REQUIRED")
        yield {"type": "DELTA", "text":
               "Sign in with Google and connect the owning GitHub repository to repair " +
               project["project"] + ". No source was retrieved and no files were created."}
        yield _finish()
        return
    if cancelled():
        yield {"type": "CANCELLED", "phase": "CANCELLED"}
        return
    yield _status("EXISTING_PROJECT_SOURCE_READING",
                  "Reading the project's real GitHub source through owner authorization.")
    try:
        verified = context.read_project_source(user_id, project)
        evidence = context.evidence(project, verified)
        if not isinstance(evidence, str) or not re.search(
                r"(?m)^Verified Git blob: [0-9a-f]{40}$", evidence):
            raise ValueError("SOURCE_RECEIPT_INVALID")
    except Exception as exc:
        yield _status("EXISTING_PROJECT_SOURCE_UNAVAILABLE", type(exc).__name__)
        yield {"type": "DELTA", "text":
               "The existing project " + project["project"] +
               " was identified, but its owner-verified GitHub source could not be "
               "retrieved (" + type(exc).__name__ +
               "). No replacement HTML was generated, and no GitHub write or deployment occurred."}
        yield _finish()
        return

    payload = dict(base_payload)
    payload.update({
        "prompt": prompt,
        "receivedText": prompt,
        "activeHtmlProject": project,
        "projectFileEvidence": evidence,
        "htmlRepairOwner": user_id,
        "htmlRepairThreadId": thread_id,
        "_cancelCheck": cancelled,
    })

    def coder_generate(coder_payload):
        # The same installed inference model, not a canned or GitHub-provided patch.
        yield from engine.generate_events(coder_payload, cancelled)

    for event in runtime.run(payload, coder_generate):
        if not isinstance(event, dict):
            continue
        if str(event.get("type") or "").upper() == "WIDGET":
            widget = event.get("widget")
            if isinstance(widget, dict):
                yield _status("EXISTING_PROJECT_REPAIR_REVIEW",
                              "Display exact proposed diffs before an explicit owner decision.")
                yield {"type": "DELTA", "text": _review_diff(widget)}
            continue
        yield event


def route_events(*, user_id: str, thread_id: str, prompt: str,
                 engine: Any, cancelled, base_payload: dict) -> Iterator[dict] | None:
    """Return None only for ordinary chat; never fall through after repair selection."""
    if not isinstance(prompt, str) or not prompt.strip():
        return None
    context, approval, runtime = _components()
    decision = _DECISION.fullmatch(prompt)
    if (decision and user_id.startswith("google:") and
            approval.has_pending(user_id, thread_id)):
        accept = decision.group(1).lower() in {"yes", "approve", "approved"}
        return _approval_events(approval, user_id, thread_id, accept)
    project = context.resolve(prompt, {"messages": []})
    if project is None or not approval.repair_intent(prompt):
        return None
    return _repair_events(
        context, approval, runtime, user_id=user_id, thread_id=thread_id,
        prompt=prompt, project=project, engine=engine,
        cancelled=cancelled, base_payload=base_payload)
