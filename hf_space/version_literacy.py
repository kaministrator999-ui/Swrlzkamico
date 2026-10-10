"""Version literacy for project evidence and ordinary conversational follow-ups.

This module guides generation, not a hardcoded answer or a version authority.
A Git commit containing a version is not proof that the version began there.
"""
from __future__ import annotations

import re

VERSION_TOPIC = re.compile(
    r"\b(?:versions?|versioning|semver|calver|releases?|build\s+(?:ids?|numbers?)|"
    r"revisions?|changelogs?|release\s+tags?)\b", re.I
)
HISTORY_CUE = re.compile(
    r"\b(?:first|initial|introduced|origin|original|created|when\s+did|"
    r"which\s+commit|history|historical|changed|change\s+between)\b", re.I
)
COMPARISON_CUE = re.compile(r"\b(?:compare|difference|versus|vs\.?|between|newer|older|upgrade|downgrade)\b", re.I)
RECALL_CUE = re.compile(
    r"\b(?:again|remind\s+me|what\s+(?:were|are)|which|list|show|current|latest)\b", re.I
)


def is_version_query(prompt):
    """Broad topic recognition; the source and speaker determine actual meaning."""
    return bool(VERSION_TOPIC.search(str(prompt or "")[:1200]))


def version_intent(prompt):
    text = str(prompt or "")[:1200]
    if not is_version_query(text):
        return ""
    if COMPARISON_CUE.search(text):
        return "compare"
    if HISTORY_CUE.search(text):
        return "provenance"
    if RECALL_CUE.search(text):
        return "recall"
    return "explain"


def style_hint(prompt):
    """Small general lesson for a model, NOT a fabricated version value."""
    mode = version_intent(prompt)
    if not mode:
        return ""
    common = (
        "VERSION LITERACY (interpret meanings from context, not from numeric shape alone): "
        "A component or dependency version identifies a specific component state; "
        "a project release tag, model checkpoint, protocol schema revision, build number, "
        "document revision, Git commit SHA, and deployment revision are DISTINCT identities. "
        "A date may be a calendar version or just a date depending on surrounding labels. "
        "Examples: 2.3.349 may be a runtime module version; v198 may be a release label; "
        "1.0.0-beta.2 is a prerelease; a 40-hex SHA identifies a Git commit, NOT a module version. "
        "Resolve each identifier's owning component, source and observed status; never convert "
        "a source read, current commit, or deployment into proof of an initial/introducing commit. "
        "Use precise evidence; otherwise say provenance is unverified. "
    )
    if mode == "recall":
        return common + (
            "USER INTENT: VERSION RECALL. Resolve 'the versions', 'those' and 'again' "
            "against recent conversation and verified project-thread source snapshot. "
            "Repeat exact component-version pairs, including all requested modules; "
            "a brief recap is better than a speculative history. If snapshot is stale, "
            "say it is from the last source read, not necessarily live."
        )
    if mode == "compare":
        return common + (
            "USER INTENT: VERSION COMPARISON. Align identical components and source points, "
            "then compare only documented values/changes; avoid invented change logs. "
            "A compact table is useful when several components actually need comparison."
        )
    if mode == "provenance":
        return common + (
            "USER INTENT: VERSION HISTORY. An initial or introducing commit requires "
            "explicit git blame/tag/diff/history evidence. A current pinned SHA is NOT the "
            "initial commit. Do not invent milestones if only current values are known."
        )
    return common + (
        "USER INTENT: VERSION EXPLANATION. Explain the identifier, its owning component "
        "and relevant versioning scheme without insisting everything is semantic versioning."
    )
