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


# v259: a deliberately small pre-authorized case. A direct user request to
# create a *test* text file gives enough discretion for harmless defaults.
# Other file requests keep the v258 review and explicit confirmation flow.
_DIRECT_TEST_TXT = re.compile(
    r"^\s*(?:(?:can|could|would)\s+you\s+|please\s+)?"
    r"(?:create|make|add|write|put)\s+(?:me\s+)?"
    r"(?:(?:a|one)\s+)?(?:(?:simple|quick|harmless|basic)\s+)?"
    r"test\s+(?:text|txt|\.txt)\s+file\s+"
    r"(?:in|into|to|on)\s+(?:(?:the|my|our)\s+)?"
    r"(?:(?:connected|github)\s+)?(?:repo|repository)"
    r"(?:\s+for\s+me)?\s*[.!?]*\s*$",
    re.IGNORECASE,
)


def wants_direct_github_test_txt(prompt: str) -> bool:
    """True only for one explicit, standalone harmless test-create request.

    This code is NOT a grant. The trusted Station must still read a verified
    signed-in account and current *GitHub* OAuth scope + push permission.
    Requests mentioning content, filename, conditions, negation, code, or
    different destinations require the ordinary review flow.
    """
    return isinstance(prompt, str) and len(prompt) <= 400 and bool(
        _DIRECT_TEST_TXT.fullmatch(prompt)
    ) and wants_github_text_file_creation(prompt)
