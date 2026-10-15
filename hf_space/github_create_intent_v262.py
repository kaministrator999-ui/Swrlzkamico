"""Classify a human Chat request for *proposed* general GitHub file creation."""
from __future__ import annotations
import re

_FILE_WORD = re.compile(r"\b(?:file|files|filename|upload|image|picture|document|script)\b|"
                        r"(?:\.[A-Za-z0-9]{1,15})\b", re.I)
_ACTION_WORD = re.compile(r"\b(?:create|make|add|upload|save|put|write)\b", re.I)
_REPO_WORD = re.compile(r"\b(?:github|repo|repository)\b", re.I)
_EXCLUDE = re.compile(r"\b(?:explain|describe|research|tutorial|how\s+(?:do|can|would|to)|"
                      r"what\s+if|can\s+(?:it|she|the\s+AI)|"
                      r"implement\s+(?:support|a\s+feature)|"
                      r"(?:needs?|should)\s+(?:to\s+)?be\s+able)\b", re.I)
_NEGATE = re.compile(r"\b(?:do\s+not|don't|dont|never)\s+(?:\w+\s+){0,3}"
                     r"(?:create|upload|put|write|make|add|save)\b", re.I)


def wants_github_general_file_proposal(prompt):
    if not isinstance(prompt, str) or len(prompt) > 10000:
        return False
    return bool(_FILE_WORD.search(prompt) and _ACTION_WORD.search(prompt)
                and _REPO_WORD.search(prompt) and not _EXCLUDE.search(prompt)
                and not _NEGATE.search(prompt))
