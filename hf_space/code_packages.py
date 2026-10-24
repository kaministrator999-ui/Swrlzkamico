"""Bounded downloadable code-artifact packages, not a general server filesystem API.

Uses only the stdlib. Takes committed artifact file records, never user-selected
filesystem paths. It never reads paths from disk, executes generated code, or
uploads the generated archive to GitHub or HF.
"""
from __future__ import annotations

import hashlib
import io
import re
import unicodedata
import zipfile

MAX_FILES = 32
MAX_FILE_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024
MAX_PATH_BYTES = 240
_ALLOWED_SEGMENT = re.compile(r"^[a-zA-Z0-9_ .@+()\-]+$")
_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *{f"COM{i}" for i in range(1, 10)}, *{f"LPT{i}" for i in range(1, 10)}}
_ARCHIVE_REQUEST = re.compile(
    r"\b(?:zip (?:it|them|this|these|the files?|the project)|"
    r"archive (?:it|them|this|these|the files?|the project)|"
    r"(?:send|provide|deliver|package|bundle|download|put) "
    r"(?:me )?(?:the |this |these )?(?:files? |project |code )?"
    r"(?:as |into |in )?(?:a |an )?(?:zip|archive)|"
    r"(?:as|into|in) (?:a |an )?(?:zip|archive)|"
    r"(?:zip|archive) (?:file|format|download|please))\b", re.I,
)


class PackageError(ValueError):
    """Unsafe or unrepresentable code-file package."""


def wants_archive(user_text: str) -> bool:
    """Conservative delivery intent; does not conflate ZIP source code with ZIP delivery."""
    text = re.sub(r"\s+", " ", str(user_text or "")[:5000])
    return bool(_ARCHIVE_REQUEST.search(text))


def safe_relative_path(raw: str) -> str:
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise PackageError("invalid file path")
    raw = unicodedata.normalize("NFC", raw)
    if raw.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", raw):
        raise PackageError("absolute paths not allowed")
    normalized = raw.replace("\\", "/")
    if len(normalized.encode("utf-8")) > MAX_PATH_BYTES:
        raise PackageError("file path too long")
    parts = normalized.split("/")
    if len(parts) > 16:
        raise PackageError("directory nesting exceeds limit")
    for part in parts:
        if (not part or part in (".", "..") or part.rstrip(" .") != part
            or len(part) > 100 or not _ALLOWED_SEGMENT.fullmatch(part)
            or part.split(".", 1)[0].upper() in _WINDOWS_RESERVED
            or part.casefold() in (".git", "__pycache__")):
            raise PackageError("unsafe path component")
    return "/".join(parts)


def _files(files: list[dict]) -> list[tuple[str, bytes]]:
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
        raise PackageError("expected 1..32 complete files")
    prepared = []
    seen = set()
    size = 0
    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get("content"), str):
            raise PackageError("artifact contains missing or non-text file")
        path = safe_relative_path(entry.get("path"))
        fold = path.casefold()
        if fold in seen:
            raise PackageError("duplicate file paths")
        seen.add(fold)
        payload = entry["content"].encode("utf-8")
        if len(payload) > MAX_FILE_BYTES:
            raise PackageError("single generated file exceeds limit")
        size += len(payload)
        if size > MAX_TOTAL_BYTES:
            raise PackageError("generated project exceeds package limit")
        prepared.append((path, payload))
    return prepared


def _archive_name(prepared: list[tuple[str, bytes]]) -> str:
    paths = [path for path, _ in prepared]
    roots = {path.split("/", 1)[0] for path in paths if "/" in path}
    if len(roots) == 1 and all(path.startswith(next(iter(roots)) + "/") for path in paths):
        base = next(iter(roots))
    elif len(paths) == 1:
        base = paths[0].rsplit("/", 1)[-1].rsplit(".", 1)[0]
    else:
        base = "project-files"
    return re.sub(r"[^a-zA-Z0-9_.-]", "-", base)[:80].strip(" .") + ".zip"


def build_package(files: list[dict], *, force_archive: bool = False) -> dict:
    """Return downloadable bytes and filename from exact revision file bodies."""
    prepared = _files(files)
    archive = force_archive or len(prepared) != 1
    if not archive:
        path, payload = prepared[0]
        return {
            "filename": path.rsplit("/", 1)[-1],
            "mediaType": "application/octet-stream",
            "body": payload,
            "archive": False,
            "fileCount": 1,
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=False) as zipped:
        for path, payload in sorted(prepared):
            item = zipfile.ZipInfo(filename=path, date_time=(1980, 1, 1, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.create_system = 3
            item.external_attr = 0o100644 << 16
            zipped.writestr(item, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    body = output.getvalue()
    return {
        "filename": _archive_name(prepared),
        "mediaType": "application/zip",
        "body": body,
        "archive": True,
        "fileCount": len(prepared),
        "sha256": hashlib.sha256(body).hexdigest(),
    }
