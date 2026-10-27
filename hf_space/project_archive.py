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
import shlex
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
_FENCE_ATTRIBUTES = re.compile(r'''([A-Za-z][\w-]*)=(?:"([^"\n]*)"|'([^'\n]*)'|([^\s]+))''')


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



# Explicit union of Python/ECMAScript metadata whitespace, including BOM.
# Source contents are never stripped; this only interprets comment boundaries.
_METADATA_WHITESPACE = "\u0009\u000a\u000b\u000c\u000d\u001c\u001d\u001e\u001f \u0085\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"
_METADATA_EXTENSIONLESS = {"dockerfile", "makefile", "license", "copying", "notice",
    "readme", "gemfile", "procfile", "gradlew", ".gitignore", ".gitattributes",
    ".editorconfig", ".npmrc"}
_SLASH_COMMENTS = {"javascript", "js", "typescript", "ts", "jsx", "tsx", "css", "scss",
    "less", "java", "kotlin", "kt", "c", "cpp", "c++", "csharp", "cs", "rust", "go",
    "swift", "php", "jsonc"}
_HASH_COMMENTS = {"python", "py", "python3", "bash", "sh", "shell", "yaml", "yml",
    "ruby", "rb", "r", "dockerfile", "makefile", "toml", "ini", "markdown", "md"}


def leading_file_metadata(content, language):
    """Read an unambiguous first-line filename comment, never edit its bytes.

    Plain names must be one whitespace-free token with an extension (or a known
    extensionless source name). Spaces require one pair of quotes/backticks.
    URLs, ordinary prose, later comments and arbitrary quoted text are not file
    metadata. Intended unsafe paths remain candidates so the shared validator
    rejects them rather than silently replacing their identity with a default.
    """
    first = next((line.strip(_METADATA_WHITESPACE) for line in re.split(r"\r\n|\r|\n", str(content))
                  if line.strip(_METADATA_WHITESPACE)), "")
    if first.startswith("#!"):
        return None
    language = str(language).lower()
    patterns = []
    if language in {"html", "html5", "xml", "svg"}:
        patterns.append(r"<!--[ \t]*(.*?)[ \t]*-->")
    if language in _SLASH_COMMENTS:
        patterns.extend([r"//[ \t]*(.*)", r"/\*[ \t]*(.*?)[ \t]*\*/"])
    if language in _HASH_COMMENTS:
        patterns.append(r"#{1,6}[ \t]+(.*)" if language in {"markdown", "md"} else r"#[ \t]*(.*)")
    payload = None
    for pattern in patterns:
        match = re.fullmatch(pattern, first)
        if match:
            payload = match.group(1).strip(_METADATA_WHITESPACE)
            break
    if not payload:
        return None
    quoted = payload[:1] in {"\"", "'", "`"}
    if quoted:
        quote = payload[0]
        if len(payload) < 2 or payload[-1] != quote or quote in payload[1:-1]:
            return None
        payload = payload[1:-1]
    elif any(char in _METADATA_WHITESPACE for char in payload):
        return None
    if not payload or re.match(r"^(?![A-Za-z]:)[A-Za-z][A-Za-z0-9+.-]*://", payload):
        return None
    basename = re.split(r"[/\\]", payload)[-1]
    name_hint = basename.rstrip(_METADATA_WHITESPACE) if quoted else basename
    filename = bool(re.fullmatch(r"[^/\\]+\.[A-Za-z0-9][A-Za-z0-9._-]*", name_hint)
                    or name_hint.lower() in _METADATA_EXTENSIONLESS)
    unsafe_shape = (payload.startswith(("/", "\\")) or bool(re.match(r"^[A-Za-z]:", payload))
                    or any(ord(char) < 32 or ord(char) == 127 for char in payload)
                    or any(part in ("", ".", "..") or part.casefold() in {".git", ".hg", ".svn"}
                           or part.split(".", 1)[0].casefold() in _RESERVED
                           for part in re.split(r"[/\\]", payload)))
    return payload if filename or unsafe_shape else None



def leading_file_metadata_matches_path(content, language, path):
    """Match a safe leading filename label to its authoritative stored path.

    A bare filename can label a full authoritative path, but it cannot change
    that path or exempt a differently named, unsafe or later source comment.
    """
    metadata = leading_file_metadata(content, language)
    if metadata is None or not isinstance(path, str):
        return False
    try:
        validate_project_files([{"path": metadata, "content": ""}])
        validate_project_files([{"path": path, "content": ""}])
    except ProjectArchiveError:
        return False
    return metadata == path or ("/" not in metadata and metadata == path.rsplit("/", 1)[-1])


_TERMINAL_LANGUAGES = {"sh", "bash", "shell", "zsh", "console", "terminal", "shell-session", "powershell", "ps1"}
_USAGE_TOOLS = {"node", "npm", "npx", "pnpm", "yarn", "bun", "deno", "uv", "pip", "pip3",
                "dotnet", "cargo", "go", "gradle", "./gradlew", "mvn", "make", "cmake", "php", "ruby", "bundle", "docker"}


def _plain_usage_invocations(content):
    """Recognize a few CLI invocations, never a shell implementation or execution."""
    text = str(content or "")
    if len(text) > 4096 or re.search(r"\b(?:TODO|FIXME|pseudocode)\b", text, re.I):
        return False
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not 1 <= len(lines) <= 4:
        return False
    for line in lines:
        if line.startswith("$ "):
            line = line[2:]
        if (line.startswith("#") or line.endswith("\\")
                or re.search(r"[;&|<>`{}()]|\$\(", line)):
            return False
        try:
            words = shlex.split(line, comments=False)
        except ValueError:
            return False
        if not words or (words[0] not in _USAGE_TOOLS and not re.fullmatch(r"python(?:3(?:\.\d+)?)?", words[0])):
            return False
        if any(word.startswith("#") or word.lower() in
               {"-c", "-e", "-p", "--eval", "--command", "-command", "--execute"} for word in words[1:]):
            return False
    return True


def project_source_fences(text):
    """Separate narrow run instructions from actual source-file declarations.

    Only unlabelled terminal invocations following real nonterminal source and
    an immediately preceding usage/run/setup paragraph are advisory. Every raw
    fence and byte remains available through source_fences for Chat display.
    Named scripts, filename comments, primary shell output and ambiguous blocks
    retain their source identity and ordinary validation.
    """
    source = str(text or "")
    result = []
    primary_seen = False
    previous_end = 0
    source_languages = (_SLASH_COMMENTS | _HASH_COMMENTS |
        {"html", "html5", "xml", "svg", "json", "sql", "dart", "lua", "scala", "groovy"}) - _TERMINAL_LANGUAGES
    usage_intro = re.compile(
        r"^(?:#{1,6}\s*)?(?:(?:to|then|you can|please)\s+(?:run|start|serve|test|build|install)\b|"
        r"(?:run|start|serve|usage|setup|installation|install)\b|for\s+(?:setup|usage|running)\b)", re.I)
    for fence in source_fences(source):
        parts = fence["header"].strip().split()
        language = parts[0].lower() if parts and "=" not in parts[0] else "text"
        named = any(match.group(1).lower() in {"file", "path", "filename"}
                    for match in _FENCE_ATTRIBUTES.finditer(fence["header"]))
        label = leading_file_metadata(fence["content"], language)
        preceding = source[previous_end:fence["start"]].strip()
        paragraph = re.split(r"\r?\n[ \t]*\r?\n", preceding)[-1] if preceding else ""
        advisory = (primary_seen and language in _TERMINAL_LANGUAGES and not named and label is None
                    and bool(usage_intro.match(paragraph)) and _plain_usage_invocations(fence["content"]))
        if not advisory:
            result.append(fence)
            if language not in _TERMINAL_LANGUAGES and (named or label is not None or language in source_languages):
                primary_seen = True
        previous_end = fence["end"]
    return result


def parse_project_files(text):
    """Parse the existing path-labelled Markdown protocol without clipping paths.

    Completeness and language checks remain the programming contract's job.
    This shared parser makes the validated project names equal the stored names.
    """
    files = []
    extensions = {"python": "py", "javascript": "js", "typescript": "ts", "html": "html",
                  "css": "css", "java": "java", "kotlin": "kt", "cpp": "cpp", "c": "c", "json": "json"}
    for index, fence in enumerate(project_source_fences(text), start=1):
        header = fence["header"].strip()
        parts = header.split()
        language = parts[0] if parts and "=" not in parts[0] else "text"
        attrs = {}
        for item in _FENCE_ATTRIBUTES.finditer(header):
            key = item.group(1).lower()
            if key in attrs:
                raise ProjectArchiveError("Project file headers repeat an attribute")
            attrs[key] = next(value for value in item.groups()[1:] if value is not None)
        names = [attrs[key] for key in ("file", "path", "filename") if key in attrs]
        if len(set(names)) > 1:
            raise ProjectArchiveError("Project file headers contain conflicting paths")
        path = names[0] if names else leading_file_metadata(fence["content"], language)
        if path is None:
            path = "code." + extensions.get(language.lower(), "txt") if index == 1 else f"file-{index}.txt"
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
