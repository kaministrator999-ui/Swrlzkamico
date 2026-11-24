"""Browser-free, source-grounded HTML project inspection for §C.

Static findings and same-Space HTTP byte checks are not rendering or interaction
proof. Never execute project scripts, fetch arbitrary user URLs, or write a repo.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
import posixpath
import re
import urllib.error
import urllib.parse
import urllib.request

VERSION = "swrlz-lightweight-web-inspector-v1"
ORIGIN = "https://kamiloki-swyrlz.hf.space"
PREFIX = "/api/html-projects/"
SLUG = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?\Z")
_MAX = 1_000_000
_TEXT_TYPES = (".html", ".htm", ".js", ".mjs", ".css", ".json", ".svg")
_IMPORT = re.compile(r"(?:^|[;\n])\s*(?:import|export)\s*(?:[\s\S]{0,170}?\sfrom\s*)?['\"]([^'\"]+)['\"]", re.M)
_DYNAMIC_IMPORT = re.compile(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
_CSS_IMPORT = re.compile(r"@import\s+(?:url\()?['\"]?([^'\"\s)]+)", re.I)
_CSS_URL = re.compile(r"url\(\s*['\"]?([^'\"\s)]+)", re.I)


class _Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.inline_scripts = []
        self._script = None
        self._body = []
        self.canvas = False
        self.buttons = 0
        self.importmaps = []
        self.module_sources = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "canvas":
            self.canvas = True
        if tag in ("button", "input") and (tag == "button" or a.get("type", "").lower() in ("button", "submit")):
            self.buttons += 1
        if tag == "script":
            kind = a.get("type", "").lower()
            if a.get("src"):
                self.references.append(("script", a["src"]))
                if kind == "module":
                    self.module_sources.append(a["src"])
            self._script = {"kind": kind, "text": ""}
        elif tag == "link" and "stylesheet" in a.get("rel", "").lower().split():
            self.references.append(("style", a.get("href", "")))
        elif tag == "link" and a.get("rel", "").lower() == "modulepreload":
            self.references.append(("script", a.get("href", "")))
        elif tag in ("img", "source", "video", "audio") and a.get("src"):
            self.references.append(("image", a["src"]))
        elif tag == "a" and a.get("href", "").startswith(("./", "../", "/")):
            self.references.append(("link", a["href"]))
    def handle_data(self, data):
        if self._script is not None:
            self._script["text"] += data
    def handle_endtag(self, tag):
        if tag == "script" and self._script is not None:
            s = self._script
            if s["kind"] == "importmap":
                self.importmaps.append(s["text"])
            elif s["kind"] in ("", "module", "text/javascript", "application/javascript"):
                self.inline_scripts.append(s)
            self._script = None


def _issue(code, path, detail, severity="error"):
    return {"code": code, "file": path, "detail": str(detail)[:200], "severity": severity}


def _resolve(base, uri):
    """Resolve a project-relative path only; never convert it into a network URL."""
    if not isinstance(uri, str):
        return None, "invalid"
    uri = uri.strip()
    if uri.startswith("data:"):
        return None, "data"
    if uri.startswith("blob:"):
        return None, "blob"
    if not uri or uri.startswith("#") or uri.startswith(("mailto:", "tel:")):
        return None, "embedded"
    parsed = urllib.parse.urlsplit(uri)
    if parsed.scheme or parsed.netloc or uri.startswith("//"):
        return None, "external"
    if uri.startswith("/"):
        return None, "absolute"
    path = posixpath.normpath(posixpath.join(posixpath.dirname(base), urllib.parse.unquote(parsed.path)))
    if path == ".." or path.startswith("../") or path.startswith("/") or "\\" in path:
        return None, "escape"
    return path, "local"


def inspect_files(files, *, known_files_complete=True):
    """Inspect bytes/dict of project-local files. No network, JS execution, or writes."""
    if not isinstance(files, dict) or not files or len(files) > 48:
        raise ValueError("PROJECT_FILE_COUNT_INVALID")
    clean = {}
    for path, content in files.items():
        if (not isinstance(path, str) or not path or path.startswith(("/", "."))
                or any(p in ("", ".", "..") or p.startswith(".") for p in path.split("/"))
                or "\\" in path):
            raise ValueError("UNSAFE_PROJECT_PATH")
        raw = content.encode("utf-8") if isinstance(content, str) else content
        if not isinstance(raw, bytes):
            raise ValueError("PROJECT_FILE_TYPE_INVALID")
        clean[path] = raw
    if sum(len(x) for x in clean.values()) > _MAX:
        raise ValueError("PROJECT_TOO_LARGE")
    problems, scripts, referenced = [], [], set()
    needs_rendering = False
    import_maps = {}
    module_sources = set()
    if "index.html" not in clean:
        problems.append(_issue("ENTRY_MISSING", "index.html", "Project has no entry HTML"))
    for path, raw in sorted(clean.items()):
        if not path.endswith((".html", ".htm")):
            continue
        try:
            markup = raw.decode("utf-8")
        except UnicodeDecodeError:
            problems.append(_issue("HTML_UTF8_INVALID", path, "Invalid UTF-8"))
            continue
        doc = _Document()
        doc.feed(markup)
        doc.close()
        needs_rendering |= doc.canvas or bool(re.search(r"\b(?:WebGLRenderingContext|webgl2?|WebGPU|THREE\.|new\s+WebGLRenderer)\b", markup, re.I))
        for rawmap in doc.importmaps:
            try:
                obj = json.loads(rawmap)
                if not isinstance(obj, dict) or not isinstance(obj.get("imports", {}), dict):
                    raise ValueError("Import map must contain an imports dictionary")
                import_maps.update(obj.get("imports", {}))
            except (ValueError, TypeError) as e:
                problems.append(_issue("IMPORTMAP_INVALID", path, e))
        for uri in doc.module_sources:
            module_path, module_kind = _resolve(path, uri)
            if module_kind == "local":
                module_sources.add(module_path)
        for category, url in doc.references:
            ref, mode = _resolve(path, url)
            if mode in ("data", "blob") and category in ("script", "style"):
                problems.append(_issue("CSP_EMBEDDED_EXECUTABLE_ASSET", path, category + " " + url))
            if mode == "external" and category in ("script", "style", "image"):
                problems.append(_issue("CSP_EXTERNAL_ASSET", path, category + " " + url))
            elif mode == "absolute" and category in ("script", "style", "image"):
                problems.append(_issue("ABSOLUTE_ASSET_UNVERIFIED", path, url))
            elif mode == "escape":
                problems.append(_issue("PROJECT_PATH_ESCAPE", path, url))
            elif mode == "local":
                if category == "link" and ref.endswith("/"):
                    ref += "index.html"
                referenced.add(ref)
                if ref not in clean and category != "link" and known_files_complete:
                    problems.append(_issue("LOCAL_ASSET_MISSING", path, ref))
        for idx, script in enumerate(doc.inline_scripts):
            if script["text"].strip():
                scripts.append({"file": path, "scriptIndex": idx, "type": script["kind"] or "classic", "text": script["text"]})
    for key, value in import_maps.items():
        if not isinstance(key, str) or not isinstance(value, str):
            problems.append(_issue("IMPORTMAP_INVALID", "index.html", "Import mapping must be a string"))
            continue
        target, kind = _resolve("index.html", value)
        if kind == "external":
            problems.append(_issue("CSP_EXTERNAL_MODULE", "index.html", key + " -> " + value))
        elif kind in ("absolute", "escape"):
            problems.append(_issue("IMPORTMAP_TARGET_UNVERIFIED", "index.html", key + " -> " + value))
        elif kind == "local" and target not in clean and known_files_complete:
            problems.append(_issue("LOCAL_MODULE_MISSING", "index.html", target))
    for path, raw in sorted(clean.items()):
        if not path.endswith((".js", ".mjs", ".css")):
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            problems.append(_issue("SCRIPT_UTF8_INVALID", path, "Invalid UTF-8"))
            continue
        if path.endswith((".js", ".mjs")):
            is_module = (path.endswith(".mjs") or path in module_sources or
                         bool(_IMPORT.findall(text)) or
                         bool(re.search(r"(?m)^\\s*export\\s+(?:default|const|let|var|function|class|\\{)", text)))
            scripts.append({"file": path, "scriptIndex": None, "type": "module" if is_module else "classic", "text": text})
    for script in scripts:
        path, body = script["file"], script["text"]
        needs_rendering |= bool(re.search(r"\b(?:WebGLRenderer|WebGLRenderingContext|webgl2?|getContext\s*\(\s*['\"]webgl)\b", body, re.I))
        for spec in _IMPORT.findall(body) + _DYNAMIC_IMPORT.findall(body):
            target = import_maps.get(spec, spec)
            if isinstance(target, str) and not target.startswith((".", "/", "http:", "https:")):
                problems.append(_issue("BARE_MODULE_UNRESOLVED", path, spec))
                continue
            ref, mode = _resolve(path, target)
            if mode in ("external", "data", "blob"):
                problems.append(_issue("CSP_EXTERNAL_MODULE", path, spec + " -> " + target))
            elif mode == "local" and ref not in clean and known_files_complete:
                problems.append(_issue("LOCAL_MODULE_MISSING", path, spec + " -> " + ref))
            elif mode in ("absolute", "escape"):
                problems.append(_issue("MODULE_TARGET_UNVERIFIED", path, spec + " -> " + target))
    for path, raw in sorted(clean.items()):
        if not path.endswith(".css"):
            continue
        css = raw.decode("utf-8", errors="replace")
        for spec in _CSS_IMPORT.findall(css) + _CSS_URL.findall(css):
            ref, mode = _resolve(path, spec)
            if mode == "external":
                problems.append(_issue("CSP_EXTERNAL_STYLE_RESOURCE", path, spec))
            elif mode == "local" and ref not in clean and known_files_complete:
                problems.append(_issue("LOCAL_ASSET_MISSING", path, ref))
    errors = [p for p in problems if p["severity"] == "error"]
    return {
        "schema": VERSION, "tier": "static", "staticPass": not errors,
        "renderingRequiredForFullVerification": needs_rendering,
        "functionalVerified": False, "syntaxVerified": False,
        "sourceSha256": hashlib.sha256(clean.get("index.html", b"")).hexdigest(),
        "fileCount": len(clean), "completeFileInventory": bool(known_files_complete), "issues": problems[:35],
        "scripts": scripts, "referencedFiles": sorted(referenced)[:60],
        "note": ("Static analysis only: no JavaScript execution, interaction, "
                 "graphics rendering, or deployment is verified."),
    }


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise ValueError("REDIRECT_NOT_ALLOWED")


def inspect_published(slug, expected_files, *, timeout=8):
    """Bounded exact-origin readback; accepts neither arbitrary hosts nor URLs."""
    if not isinstance(slug, str) or not SLUG.fullmatch(slug):
        raise ValueError("INVALID_PROJECT_SLUG")
    local = inspect_files(expected_files)
    opener = urllib.request.build_opener(_NoRedirect)
    issues = []
    for path, raw in sorted(expected_files.items()):
        if len(issues) >= 10:
            break
        url = ORIGIN + PREFIX + slug + "/" + urllib.parse.quote(path, safe="/")
        try:
            req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "Swrlz-Lightweight-Project-Inspector/1"})
            with opener.open(req, timeout=timeout) as resp:
                body = resp.read(_MAX + 1)
                if len(body) > _MAX or hashlib.sha256(body).hexdigest() != hashlib.sha256(raw.encode("utf-8") if isinstance(raw, str) else raw).hexdigest():
                    issues.append(_issue("DEPLOYED_BYTES_DIFFER", path, "Published bytes do not match the selected GitHub source"))
                if resp.status != 200:
                    issues.append(_issue("HTTP_STATUS", path, resp.status))
                csp = resp.headers.get("Content-Security-Policy", "")
                if ("sandbox allow-scripts" not in csp or "allow-same-origin" in csp
                        or "connect-src 'none'" not in csp
                        or resp.headers.get("X-Content-Type-Options", "").lower() != "nosniff"):
                    issues.append(_issue("DEPLOYMENT_SECURITY_MISMATCH", path, "Expected opaque-origin CSP and nosniff"))
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as e:
            issues.append(_issue("HTTP_UNAVAILABLE", path, type(e).__name__))
    return {"schema": VERSION, "tier": "http", "project": slug,
            "deployedBytesMatch": not issues, "functionalVerified": False,
            "renderingRequiredForFullVerification": local["renderingRequiredForFullVerification"],
            "issues": issues, "checkedFiles": len(expected_files),
            "note": "HTTP/source/security checks are not an executed page or browser-rendering test."}


def model_summary(report):
    """Compact factual findings for §C, explicitly not proof of execution."""
    fields = {k: v for k, v in report.items() if k not in ("scripts", "referencedFiles")}
    if isinstance(fields.get("issues"), list):
        fields["issues"] = fields["issues"][:12]
    return json.dumps(fields, ensure_ascii=False, sort_keys=True)[:3700]
