"""Serve published standalone HTML on §C's existing Space in an opaque origin.

This path is deliberately *not* mounted beneath /chat/§wyrlz/assets. Every
HTML document receives an enforced CSP sandbox without allow-same-origin.
"""
from __future__ import annotations

import mimetypes
from pathlib import Path, PurePosixPath
import re

from fastapi import HTTPException
from fastapi.responses import Response

SLUG = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?\\Z")
SAFE_PART = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\\Z")
SUFFIXES = frozenset((".html", ".htm", ".css", ".js", ".mjs", ".json",
                      ".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif",
                      ".ico", ".woff", ".woff2"))
ORIGIN = "https://kamiloki-swyrlz.hf.space"
CSP = (
    "sandbox allow-scripts; default-src 'none'; "
    "script-src 'unsafe-inline' " + ORIGIN + "; "
    "style-src 'unsafe-inline' " + ORIGIN + "; "
    "img-src data: blob: " + ORIGIN + "; "
    "font-src data: " + ORIGIN + "; "
    "connect-src 'none'; form-action 'none'; object-src 'none'; "
    "base-uri 'none'; frame-ancestors 'self' https://huggingface.co"
)
HEADERS = {
    "Content-Security-Policy": CSP,
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Access-Control-Allow-Origin": "*",
    "Cross-Origin-Resource-Policy": "cross-origin",
}


def resolve_asset(base: Path, slug: str, asset_path: str) -> Path:
    if not SLUG.fullmatch(slug):
        raise HTTPException(404, "Unknown HTML project")
    rel = PurePosixPath(asset_path or "index.html")
    if (rel.is_absolute() or not rel.parts or len(rel.parts) > 8
            or any(part in (".", "..") or part.startswith(".")
                   or not SAFE_PART.fullmatch(part) for part in rel.parts)
            or rel.suffix.lower() not in SUFFIXES):
        raise HTTPException(404, "Invalid project asset")
    folder = base / slug
    candidate = folder.joinpath(*rel.parts)
    # No symlink escape even if the runtime checkout contains a hostile link.
    if base.is_symlink() or folder.is_symlink():
        raise HTTPException(404, "Unsafe project directory")
    cursor = folder
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise HTTPException(404, "Unsafe project asset")
    actual = candidate.resolve()
    if not actual.is_relative_to(folder.resolve()) or not actual.is_file():
        raise HTTPException(404, "Project asset not found")
    return actual


def install(app, root: Path) -> None:
    directory = Path(root) / "published-html-projects"

    @app.get("/api/html-projects/{slug}/", include_in_schema=False)
    @app.get("/api/html-projects/{slug}/{asset_path:path}", include_in_schema=False)
    async def _html_project_file(slug: str, asset_path: str = "index.html"):
        target = resolve_asset(directory, slug, asset_path)
        content = target.read_bytes()
        if len(content) > 1_000_000:
            raise HTTPException(413, "Project asset too large")
        media_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if target.suffix.lower() in {".html", ".htm"}:
            media_type = "text/html; charset=utf-8"
        elif target.suffix.lower() in {".js", ".mjs"}:
            media_type = "text/javascript; charset=utf-8"
        headers = dict(HEADERS)
        if target.suffix.lower() in {".html", ".htm", ".svg"}:
            headers["Content-Security-Policy"] = CSP
        return Response(content, media_type=media_type, headers=headers)
