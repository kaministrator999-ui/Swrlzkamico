"""Explicit human Chat request for GitHub file rename/move, not a code task."""
from __future__ import annotations
import re


def wants_github_rename_proposal(prompt):
    if not isinstance(prompt, str) or len(prompt) > 10000:
        return False
    text = " ".join(prompt.strip().split())
    if not re.search(r"\b(?:github|repo|repository)\b", text, re.I):
        return False
    if not re.search(r"\b(?:rename|move)\b", text, re.I):
        return False
    if re.search(r"\b(?:how\s+(?:do|can|to|would)|explain|tutorial|show\s+me\s+how|"
                 r"(?:allow|enable|add|implement|build)\s+(?:support|capabilit|feature)|"
                 r"(?:needs?|should)\s+(?:to\s+)?be\s+able)\b", text, re.I):
        return False
    if re.search(r"\b(?:do\s+not|don't|dont|never)\s+(?:\w+\s+){0,3}(?:rename|move)\b", text, re.I):
        return False
    if re.search(r"\b(?:write|generate|create)\s+(?:me\s+)?(?:python|javascript|code|script|"
                 r"function|program)\s+(?:\w+\s+){0,5}(?:rename|move)\b", text, re.I):
        return False
    # Asking to rename a file/repo path is a *proposal*, not write authority.
    return bool(re.search(r"\b(?:rename|move)\s+(?:the\s+|my\s+|a\s+)?(?:file\b|"
                          r"[\w./-]+\.[a-zA-Z0-9_-]+|[\w./-]+\s+to\b)", text, re.I))
