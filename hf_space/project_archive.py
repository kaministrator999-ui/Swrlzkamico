"""Bounded source-project ZIPs built from existing account-owned code artifacts.

This module never reads or writes project files on disk, executes generated
source, or grants provider access. Archive validation proves only that the
stored text files can be delivered under unambiguous relative paths.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import stat
import unicodedata
import zipfile

MAX_FILES = 2048
MAX_FILE_BYTES = 512 * 1024
MAX_PROJECT_BYTES = 32 * 1024 * 1024
MAX_PATH_BYTES = 240
MANIFEST_PATH = "SWRLZ_PROJECT_MANIFEST.json"
_RESERVED = {"con", "prn", "aux", "nul"} | {
    prefix + str(number) for prefix in ("com", "lpt") for number in range(1, 10)
}


class ProjectArchiveError(ValueError):
    pass


def source_fences(text):
    """Return complete line-delimited fences without cutting inline markers.

    Longer outer fences allow a README to contain ordinary triple-backtick
    examples. The programming contract independently rejects unfinished fences.
    Offsets preserve the original source for prose removal and UI parity.
    """
    source = str(text or "")
    opening = re.compile(r"(?m)^[ \t]{0,3}(`{3,}|~{3,})([^\r\n]*)\r?\n")
    result = []
    cursor = 0
    for match in opening.finditer(source):
        if match.start() < cursor:
            continue
        marker, header = match.groups()
        if marker[0] == "`" and "`" in header:
            continue
        closing = re.compile(r"(?m)^[ \t]{0,3}" + re.escape(marker[0])
                             + "{" + str(len(marker)) + r",}[ \t]*(?=\r?$)")
        end = closing.search(source, match.end())
        if end is None:
            continue
        result.append({"header": header, "content": source[match.end():end.start()],
                       "start": match.start(), "end": end.end()})
        cursor = end.end()
    return result


def project_markdown(files):
    """Serialize canonical source with quoted paths and collision-free fences."""
    chunks = []
    for item in files or []:
        content = str(item.get("content") or "")
        language = str(item.get("language") or "text")
        path = json.dumps(str(item.get("path") or "code.txt"), ensure_ascii=False)
        character = "~" if "`" in language + path else "`"
        marker = character * max(3, max((len(run) for run in re.findall(re.escape(character) + "+", content)), default=0) + 1)
        separator = "" if not content or content.endswith("\n") else "\n"
        chunks.append(marker + language + " file=" + path + "\n" + content + separator + marker)
    return "\n\n".join(chunks)


def parse_project_files(text):
    """Parse the existing path-labelled Markdown protocol without clipping paths.

    Completeness and language checks remain the programming contract's job.
    This shared parser makes the validated project names equal the stored names.
    """
    files = []
    attributes = re.compile(r'''([A-Za-z][\w-]*)=(?:"([^"\n]*)"|'([^'\n]*)'|([^\s]+))''')
    extensions = {"python": "py", "javascript": "js", "typescript": "ts", "html": "html",
                  "css": "css", "java": "java", "kotlin": "kt", "cpp": "cpp", "c": "c", "json": "json"}
    for index, fence in enumerate(source_fences(text), start=1):
        header = fence["header"].strip()
        parts = header.split()
        language = parts[0] if parts and "=" not in parts[0] else "text"
        attrs = {}
        for item in attributes.finditer(header):
            key = item.group(1).lower()
            if key in attrs:
                raise ProjectArchiveError("Project file headers repeat an attribute")
            attrs[key] = next(value for value in item.groups()[1:] if value is not None)
        names = [attrs[key] for key in ("file", "path", "filename") if key in attrs]
        if len(set(names)) > 1:
            raise ProjectArchiveError("Project file headers contain conflicting paths")
        path = names[0] if names else (
            "code." + extensions.get(language.lower(), "txt") if index == 1 else f"file-{index}.txt")
        files.append({"path": path, "language": language[:40], "content": fence["content"]})
        if len(files) > MAX_FILES:
            raise ProjectArchiveError(f"Project must contain between 1 and {MAX_FILES} files")
    return validate_project_files(files) if files else []


def validate_project_files(files):
    """Return text-file copies after portable path/count/byte validation."""
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
        raise ProjectArchiveError(f"Project must contain between 1 and {MAX_FILES} files")
    result = []
    names = set()
    total = 0
    for item in files:
        if not isinstance(item, dict):
            raise ProjectArchiveError("Project file records must be objects")
        path, content = item.get("path"), item.get("content")
        if not isinstance(path, str) or not isinstance(content, str):
            raise ProjectArchiveError("Project paths and file contents must be text")
        try:
            path_bytes = path.encode("utf-8")
            encoded = content.encode("utf-8")
        except UnicodeEncodeError:
            raise ProjectArchiveError("Project text must be valid UTF-8") from None
        if (not path or len(path_bytes) > MAX_PATH_BYTES or path.startswith("/")
                or "\\" in path or any(ord(char) < 32 or ord(char) == 127 for char in path)
                or any(char in path for char in ':*?"<>|')):
            raise ProjectArchiveError("Project paths must be portable relative file names")
        parts = path.split("/")
        for part in parts:
            if (part in ("", ".", "..") or part.endswith((" ", "."))
                    or part.casefold() in (".git", ".hg", ".svn")
                    or part.split(".", 1)[0].casefold() in _RESERVED):
                raise ProjectArchiveError("Project paths contain a reserved or unsafe component")
        key = unicodedata.normalize("NFC", path).casefold()
        if (key == MANIFEST_PATH.casefold() or key.startswith(MANIFEST_PATH.casefold() + "/")
                or key in names):
            raise ProjectArchiveError("Project paths collide or use the archive manifest name")
        # A path cannot be both a regular file and another file's directory.
        if any(key.startswith(name + "/") or name.startswith(key + "/") for name in names):
            raise ProjectArchiveError("Project file and directory paths collide")
        names.add(key)
        if len(encoded) > MAX_FILE_BYTES:
            raise ProjectArchiveError("A project file exceeds the 512 KiB source limit")
        total += len(encoded)
        if total > MAX_PROJECT_BYTES:
            raise ProjectArchiveError("Project exceeds the 32 MiB source limit")
        result.append({"path": path, "language": str(item.get("language") or "text")[:40],
                       "content": content})
    return result


def archive_filename(title, artifact_id, revision):
    stem = PurePosixPath(str(title or "project")).stem
    slug = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")[:56] or "project"
    identity = hashlib.sha256(str(artifact_id).encode("utf-8")).hexdigest()[:8]
    return f"{slug}-{identity}-r{int(revision)}.zip"


def build_project_archive(files, *, artifact_id, revision, source_hash=""):
    """Build an immutable revision's UTF-8 source files and honest manifest."""
    files = validate_project_files(files)
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise ProjectArchiveError("A positive artifact revision is required")
    if source_hash and not re.fullmatch(r"[a-f0-9]{64}", str(source_hash)):
        raise ProjectArchiveError("Invalid source identity")
    manifest = {
        "schema": "swrlz-project-download-v1", "artifactId": str(artifact_id),
        "revision": revision, "sourceHash": str(source_hash or ""),
        "verification": "SOURCE_FILES_ONLY", "executionVerified": False,
        "files": [{"path": item["path"], "language": item["language"],
                   "bytes": len(item["content"].encode("utf-8")),
                   "sha256": hashlib.sha256(item["content"].encode("utf-8")).hexdigest()}
                  for item in files],
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        entries = [(item["path"], item["content"].encode("utf-8")) for item in files]
        entries.append((MANIFEST_PATH, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")))
        for name, data in entries:
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    return output.getvalue()
