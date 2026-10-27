"""Pure file-tree merging for an already selected, revision-bound project.

This grants no project selection, provider access or mutation authority. A caller
must independently verify the artifact owner and base revision/source identity.
Omitted paths are retained; deletions are never inferred from a model response.
"""
from __future__ import annotations

import re

from project_archive import (ProjectArchiveError, leading_file_metadata,
                             parse_project_files, source_fences,
                             validate_project_files)


class RevisionWorkspaceError(ProjectArchiveError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _named_file_records(text):
    attributes = re.compile(r'''([A-Za-z][\w-]*)=(?:"([^"\n]*)"|'([^'\n]*)'|([^\s]+))''')
    result = set()
    for fence in source_fences(str(text or "")):
        header = fence["header"].strip()
        parts = header.split()
        language = parts[0] if parts and "=" not in parts[0] else "text"
        attrs = {item.group(1).lower(): next(value for value in item.groups()[1:] if value is not None)
                 for item in attributes.finditer(header)}
        names = [attrs[key] for key in ("file", "path", "filename") if key in attrs]
        path = names[0] if names else leading_file_metadata(fence["content"], language)
        if path is not None:
            result.add((path, language[:40], fence["content"]))
    return result


def _language(value):
    name = str(value or "").lower()
    return {"html5": "html", "js": "javascript", "jsx": "javascript", "mjs": "javascript",
            "ts": "typescript", "tsx": "typescript", "py": "python", "python3": "python",
            "sh": "bash", "shell": "bash", "kt": "kotlin", "md": "markdown"}.get(name, name)


def merge_project_revision_files(current_files, candidate_text):
    """Return the complete next tree after full-file named updates/additions.

    The sole-file legacy case can identify its only destination from the owned
    existing snapshot when both languages match. Multi-file updates require
    actual filename metadata; parser-generated fallback names are not targets.
    New names must be explicit too. Every source-content byte is preserved.
    """
    current = validate_project_files(current_files)
    changed = parse_project_files(candidate_text)
    if not changed:
        raise RevisionWorkspaceError("NO_CODE", "The revision contains no complete source files")
    named = _named_file_records(candidate_text)
    for item in changed:
        identity = (item["path"], item["language"], item["content"])
        if identity in named:
            continue
        if (len(current) == len(changed) == 1
                and _language(current[0]["language"]) == _language(item["language"])
                and _language(item["language"]) not in ("", "text", "txt", "code")):
            item["path"] = current[0]["path"]
            continue
        raise RevisionWorkspaceError("FILE_PATH_REQUIRED",
            "Existing multi-file project updates require explicit relative filenames")
    replacements = {item["path"]: item for item in changed}
    # Existing order is part of the canonical source hash and remains stable.
    merged = [replacements.pop(item["path"], item) for item in current]
    merged.extend(replacements.values())
    return validate_project_files(merged)
