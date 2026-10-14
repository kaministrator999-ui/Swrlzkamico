"""Risk-asymmetric, bounded conversational intent guidance for §wyrlz Chat.

Classifies a *user utterance*, never an authorization. Tool permissions and
approved target identity always remain with the owning tool/server.
"""
from __future__ import annotations

import re

# A short topical noun introduces a subject; context may suggest relevance,
# but never silently chooses browse, statistics, searching, or mutation.
_TOPIC = frozenset((
    "file", "files", "folder", "folders", "directory", "directories",
    "stats", "statistics", "code", "projects", "project", "music",
    "memories", "documents", "pictures", "photos", "repository",
))

# These verbs *may* request a persistent or externally consequential action.
# Detect only standalone underspecified action commands. Do not convert prose,
# questions, negations, code generation or harmless creative writing into writes.
_MUTATION = re.compile(
    r"^(?:(?:hey|please|could you|can you|would you)\s+)?"
    r"(delete|erase|remove|overwrite|deploy|publish|push|merge|commit|"
    r"upload|send|post|transfer|rename|move|edit|update|replace|change|"
    r"save|share|submit|dispatch|trigger|run|execute)"
    r"(?:\s+(?:(?:it|them|this|that|these|those)|"
    r"(?:the|my|our)\s+(?:file|files|repo|repository|project|"
    r"branch|document|draft|message|post|update|changes)))?"
    r"[.?!]*$", re.I,
)
_SAFE_PREFIX = re.compile(r"^(?:do not|don't|dont|never|not|stop|avoid|without)\b", re.I)


def classify(prompt):
    """Return 'topic', 'unclear-mutation' or 'ordinary'; no tool execution."""
    raw = " ".join(str(prompt or "").strip().split())
    if not raw or len(raw) > 240 or "\n" in str(prompt or ""):
        return "ordinary"
    low = raw.casefold().rstrip("?!., ")
    if low in _TOPIC:
        return "topic"
    if _SAFE_PREFIX.match(raw):
        return "ordinary"
    if _MUTATION.fullmatch(raw):
        return "unclear-mutation"
    return "ordinary"


def clarification(prompt):
    """One concise question for a concrete-but-underspecified change request."""
    if classify(prompt) != "unclear-mutation":
        return None
    match = _MUTATION.fullmatch(" ".join(str(prompt).strip().split()))
    verb = match[1].lower() if match else "change"
    if verb in ("send", "post", "share", "submit", "transfer"):
        return ("What exactly would you like me to " + verb +
                ", and to whom or where? I won't send or publish anything "
                "without a clear target and the required authorization.")
    if verb in ("deploy", "push", "merge", "commit", "dispatch", "trigger", "run", "execute"):
        return ("Which specific project, action and target do you mean by " +
                verb + "? I won't execute or deploy anything based on an ambiguous request.")
    return ("What exactly would you like me to " + verb +
            ", and where? I won't modify anything until the target and permissions are clear.")


MODEL_POLICY = (
    "INTENT/RISK ASYMMETRY: Identify the subject separately from the user's intended "
    "action. A one-word topic (Files, Music, Code, Statistics) is not an instruction "
    "to run a tool. Use relevant prior context as a *hint*, not exclusive authority; "
    "respond conversationally with one useful clarification or a small verified "
    "read-only preview where appropriate. Read-only interpretations are revisable: "
    "if the user corrects the aim, update course without defending the guess or "
    "claiming an unperformed scan. If the user clearly asks for a safe read, "
    "do it without needless clarification. For edits, deletion, sending, "
    "publishing, deployment, purchases, account changes or other persistent/external "
    "mutations, require a clear operation, target, scope and applicable permissions. "
    "Pinned workspaces, conversation history, speculative intent, model-generated "
    "choices and earlier reads are NEVER authorization. When a consequential action "
    "is underspecified, ask one focused clarification before any mutation. "
    "Explicit targets still require separate server-owned write authorization; "
    "you may explain or draft proposed changes without executing them. Writing "
    "creative text or sample code in chat is not automatically an external write."
)
