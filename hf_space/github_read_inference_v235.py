"""Read-only user question -> existing evidence command, never tool authority.

Scope comes from explicit GitHub wording or a previously verified same-thread
repository context. This classifier selects an allowed read, not the answer:
GitHub results, pinned revisions and inspection limits still own the facts.
"""
from __future__ import annotations
import re

_MUTATION = re.compile(
    r"\b(?:add|build|create|delete|deploy|dispatch|edit|fix|"
    r"implement|install|merge|modify|patch|push|refactor|remove|rename|"
    r"rerun|retry|rewrite|run|trigger|update|upload|write)\b", re.I)
_REPO = re.compile(r"\b(?:github|repo|repository)\b", re.I)
_READ = re.compile(
    r"\b(?:analy[sz]e|architecture|compare|count|describe|directory|"
    r"directories|display|browse|view|explain|explore|file|files|folder|folders|history|inspect|"
    r"how|largest|list|locate|modified|overview|read|relate|related|relationship|report|"
    r"search|see|show|size|source|structure|summari[sz]e|tree|what|"
    r"where|which|how many|when)\b", re.I)
_PATH = re.compile(
    r"(?<![\w./])(?:[A-Za-z0-9_§.+-]+/){1,6}[A-Za-z0-9_§.+-]+"
    r"|(?<![\w./])[A-Za-z0-9_§.+-]+\.(?:py|js|mjs|ts|tsx|jsx|"
    r"html|css|json|md|txt|yaml|yml|toml|kt|java|go|rs|sh|xml|sql)",
    re.I)
_BARE = re.compile(r"\b(?:folder|directory|under|inside|within|in)\s+"
                   r"(?:the\s+)?(?:folder\s+|directory\s+)?"
                   r"([A-Za-z0-9_§.-]{2,80})(?=\s|$)", re.I)
_BAD_PATH = re.compile(r"[\\\x00-\x1f?#%*{}\[\]<>|]")
_COMMAND = re.compile(r"^@github\s+", re.I)
_PREFIX = re.compile(r"^@github\s+(?:ask\s+)?", re.I)
_EXPLICIT_COMMAND = re.compile(
    r"^(?:@github\s+)(?:files|stats|largest|report|read|open|view|"
    r"history|search|compare|project status|chat status|permissions|"
    r"capabilities|help)(?:\s|$)", re.I)


def _safe(path):
    path = str(path or "").strip().strip("`\"'").rstrip(".,!?").strip("/")
    if (not path or len(path) > 160 or _BAD_PATH.search(path)
            or any(p in ("", ".", "..") for p in path.split("/"))):
        return ""
    return path


def _scope_context(context):
    if not isinstance(context, dict):
        return "", ""
    # The account/tool layer separately re-verifies repository access. These
    # hints are never trusted as GitHub authorization or as source evidence.
    directory = _safe(context.get("directory"))
    file_path = _safe(context.get("lastFile"))
    return directory, file_path


def _paths(question):
    found = []
    for m in _PATH.finditer(question):
        item = _safe(m.group(0))
        if item and item.casefold() not in [x.casefold() for x in found]:
            found.append(item)
        if len(found) == 8:
            break
    return found


def classify_read(prompt, context=None):
    """Return one *existing* Stage-1 @GitHub read command, or None.

    A natural-language question is not a source of new GitHub capabilities.
    Do not route writes, freeform dialogue, private-history recall, or ambiguous
    pronouns with no verified thread context into a repo operation.
    """
    raw = str(prompt or "").strip()
    if not raw or len(raw) > 600 or "\n" in raw or "\r" in raw:
        return None
    if re.fullmatch(
            r"(?i)(?:what (?:is|are)|how does) (?:github|(?:a|the) (?:git )?repo(?:sitory)?)"
            r"(?: work)?[?.!]*", raw):
        return None  # General GitHub education is not a connected-repository read.
    if _EXPLICIT_COMMAND.match(raw):
        return None  # existing command owners handle their own parameters
    if _MUTATION.search(raw) or re.search(r"\bcommit\s+(?:my\s+|the\s+|these\s+)?(?:changes?|code|files?)\b", raw, re.I):
        return None
    if re.search(r"\b(?:remember|recall|previous chat|chat history|"
                 r"imported conversations?|chatgpt archive)\b", raw, re.I):
        return None
    directory, last_file = _scope_context(context)
    explicit = bool(_COMMAND.match(raw) or _REPO.search(raw))
    if not explicit and not (directory or last_file):
        return None
    # Thread context is a scope hint, not permission to reinterpret unrelated dialogue.
    if not explicit and not re.search(
            r"\b(?:file|folder|directory|repo|repository|source|code|"
            r"module|function|path|project|it|that|those|them|here)\b",
            raw, re.I):
        return None
    q = _PREFIX.sub("", raw) if _COMMAND.match(raw) else raw
    if not _READ.search(q):
        return None
    lower = q.casefold()
    paths = _paths(q)
    branch_match = re.search(r"\b(?:on|from)\s+branch\s+([A-Za-z0-9][A-Za-z0-9._/-]{0,100})\b", q, re.I)
    named_branch = branch_match[1] if branch_match else ""
    if not named_branch and isinstance(context, dict):
        candidate = str(context.get("branch") or "")
        rev = str(context.get("sourceSha") or "")
        if (candidate not in ("", "main", "master")
                and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,100}", candidate)
                and re.fullmatch(r"[a-f0-9]{40}", rev)):
            named_branch = candidate
    if branch_match:
        paths = [p for p in paths if p != branch_match[1]]
    suffix = (" on branch " + named_branch) if named_branch else ""
    # A directory named in a question is a literal scope, never a guessed
    # implementation owner. Do not pick random matching files by meaning.
    if not paths:
        end_scope = re.search(
            r"\b([A-Za-z0-9_§.-]{2,80})\s+(?:folder|directory)\b", q, re.I)
        if end_scope:
            candidate = _safe(end_scope[1])
            if candidate not in ("the", "this", "that", "current", "our", "my"):
                paths = [candidate]
    if not paths:
        m = _BARE.search(q)
        if m and m[1].lower() not in (
            "repo", "repository", "github", "project", "source", "code",
            "file", "files", "folder", "directory", "this", "that", "our",
            "my", "the", "here", "which", "what", "how", "git", "history"):
            if re.search(r"\b(?:folder|directory|under|inside|within|files?\s+in|directories\s+in)\b", q, re.I):
                paths = [_safe(m[1])]
    scoped = paths[:]
    if last_file and paths and re.search(r"\b(?:that|this|the|original)\s+(?:original\s+)?file\b", lower):
        scoped = [last_file] + [p for p in paths if p != last_file]
    if not scoped and re.search(r"\b(?:this|that|those|same|last|previous|original|first)\s+"
                                r"(?:(?:original|first|previous|source|earlier)\s+)*files?\b|\b(?:it|that file)\b",lower):
        if last_file:
            scoped = [last_file]
        elif not explicit:
            return None
    if not scoped and re.search(r"\b(?:this|that|current|same)\s+"
                                r"(?:folder|directory)\b|\bhere\b", lower):
        if directory:
            scoped = [directory]
        elif not explicit:
            return None
    if re.search(r"\b(?:how many|count|number of|total|size of)\b", lower) and re.search(
            r"\b(?:files?|folders?|directories|directory|bytes|size)\b", lower):
        return "@GitHub stats" + (" " + scoped[0] if scoped else "") + suffix
    if re.search(r"\b(?:largest|biggest)\b", lower) and re.search(r"\bfiles?\b", lower):
        return "@GitHub largest 15" + (" " + scoped[0] if scoped else "") + suffix
    if re.search(r"\b(?:history|when|last modified|last changed|"
                 r"first added|changed|modified|changes? (?:to|in))\b",lower):
        if scoped:
            return "@GitHub history " + scoped[0] + suffix
        return "@GitHub report structure /" + suffix
    # A named singular file is a deterministic repository read, including
    # conversational "can you see <name> file" phrasing. Do not send it
    # through the generic GitHub command parser or programming inference.
    if scoped and re.search(r"\b(?:see|find|show|read|open|view)\b", lower) and re.search(r"\bfile\b", lower):
        return "@GitHub read file " + scoped[0] + suffix
    if re.search(r"\b(?:list|show|see|browse|open|display|view)\b", lower) and re.search(
            r"\b(?:files?|folders?|directories|contents|tree)\b", lower):
        if re.search(r"\b(?:all|every|entire|complete|recursive|again)\b", lower) and re.search(
                r"\b(?:files?|tree)\b", lower):
            return "@GitHub files recursive" + (" " + scoped[0] if scoped else "") + suffix
        return "@GitHub files" + (" " + scoped[0] if scoped else "") + suffix
    if re.search(r"\b(?:read|open|show)\b", lower) and re.search(r"\bfile\b", lower):
        if scoped:
            return "@GitHub read file " + scoped[0] + suffix
        return None  # explicit target required for a source-file read
    if re.search(r"\b(?:explain|explore|describe|summari[sz]e|analy[sz]e|"
                 r"inspect|how|what|which|where|architecture|"
                 r"dependencies|related|relationship|work|purpose|overview)\b", lower):
        if scoped:
            cmd = "@GitHub report deep " + " | ".join(scoped)
            return cmd + (" on branch " + named_branch if named_branch else "")
        return "@GitHub report structure /" + (" on branch " + named_branch if named_branch else "")
    return None
