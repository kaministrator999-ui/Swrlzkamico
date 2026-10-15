"""Recognize a request to propose a repository text-file action, never grant write authority."""
from __future__ import annotations
import re


def wants_github_text_file_creation(prompt: str) -> bool:
    """Return True only for a reasonably clear creation intent, not discussion or code generation.

    This is a conservative routing hint for the explicit approval UI, not an
    executor, a model substitute, or permission to mutate GitHub.
    """
    if not isinstance(prompt, str):
        return False
    text = " ".join(prompt.lower().split())
    repo = bool(re.search(r"\b(?:github|repo|repository)\b", text))
    plain_text = bool(re.search(r"\b(?:txt|text)\s+file\b|\bfile\s*\.txt\b|\b[a-z0-9_-]+\.txt\b", text))
    action = bool(re.search(r"\b(?:make|create|add|write|save|put)\b", text))
    if not (repo and plain_text and action):
        return False
    # Questions about mechanisms, non-creation operations and code-generation
    # requests remain conversation/programming tasks, not tool-action proposals.
    if re.search(r"\b(?:how\s+(?:can|do|to|would)|explain|tutorial|instructions|example\s+of|show\s+me\s+how)\b", text):
        return False
    if re.search(r"\b(?:do\s+not|don't|dont|never|without)\s+(?:(?:actually|really|ever)\s+)?(?:make|create|add|write|save|put)\b", text):
        return False
    if re.search(r"\b(?:code|script|function|program)\s+(?:that|to|which)\s+(?:(?:can|will)\s+)?(?:make|create|add|write|save|put)\b", text):
        return False
    if re.search(r"\b(?:write|make|create|generate)\s+(?:me\s+)?(?:python|javascript|js|bash|shell|kotlin|java|typescript|ruby)\b", text):
        return False
    return True
