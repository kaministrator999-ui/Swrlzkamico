"""Bounded generation guidance for working, coherent web projects.

This is a rendering of server-owned intent, not a validator, a template, a
permission grant or evidence that generated UI works. Source and assistant
prose are never mined for new instructions or a claimed design verdict.
"""
from __future__ import annotations

from typing import Any


def project_quality_contract(programming: dict[str, Any]) -> dict[str, Any] | None:
    """Scope quality guidance to authored web UI, preserving other route owners."""
    if (not isinstance(programming, dict) or not programming.get("codingTask")
            or programming.get("changeClass") in ("review", "explain")):
        return None
    contract = programming.get("intentContract")
    if not isinstance(contract, dict) or contract.get("implementationPolicy") == "explicit-scaffold":
        return None
    language = contract.get("languageContract")
    if not isinstance(language, dict) or language.get("artifactType") != "web-page":
        return None
    continuing = bool(not programming.get("newProject") and (
        programming.get("artifactContinuation") or programming.get("artifactMutationRequested")
        or programming.get("projectContext") == "existing" or programming.get("failureEvidence")))
    return {
        "schema": "swrlz-project-quality-v1",
        "scope": "web-ui-generation",
        "workMode": "continue" if continuing else "create",
        "designAuthority": "user-request-and-existing-project",
        "verification": "guidance-only-no-execution-claim",
    }


def project_quality_policy(programming: dict[str, Any]) -> str:
    """Describe a compact implementation/review pass without adding features."""
    quality = project_quality_contract(programming)
    if quality is None:
        return ""
    policy = (
        "\nPROJECT QUALITY: Implement the user's requested journey end to end: "
        "each visible action must affect the intended state and rendered result. "
        "Handle empty input, empty results and relevant errors where those states "
        "exist. Use semantic controls, clear labels, keyboard operation and visible "
        "focus. Keep content and actions readable, reachable and free of horizontal "
        "overflow on narrow and wide screens. Choose a coherent visual hierarchy "
        "with consistent spacing, typography and sufficient text/control contrast. "
        "Honor the requested style, stack, simplicity and single-file constraints; "
        "add no unrequested features or unnecessary framework, backend or remote "
        "dependency. Include needed local project assets and wire their actual "
        "imports and state changes. Render user-entered content as text rather "
        "than interpolating it into HTML. When persistence is requested, connect "
        "both saving and restoring state to the actual interactions. Before answering, "
        "trace the main interaction and check its empty/error path, small-screen "
        "layout and preserved requirements against the returned source. This "
        "self-review is not browser, build or test evidence."
    )
    if quality["workMode"] == "continue":
        policy += (
            "\nPROJECT CONTINUATION: Extend the current implementation. Preserve "
            "its established visual language, components, data shape/storage, "
            "public interfaces and existing working interactions except where "
            "changes are needed to implement the newest user instruction. Integrate the "
            "feature into the existing state/render flow and retain earlier "
            "requirements. Keep unchanged code inside each returned file. Follow "
            "the existing delivery contract: saved revisions can return complete "
            "changed or new files; raw-source repairs must still provide the "
            "complete required candidate. Update run instructions only if "
            "execution changes."
        )
    else:
        policy += (
            "\nSTARTER DELIVERY: Build a small, complete foundation that can be "
            "extended: keep state, behavior and presentation understandable without "
            "unnecessary abstraction. Supply real entry/config files required by "
            "the chosen stack and brief accurate run steps when the requested "
            "output format allows. A single HTML page can remain one file."
        )
    return policy
