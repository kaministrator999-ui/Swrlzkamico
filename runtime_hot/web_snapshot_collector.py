"""Runtime-owned SWRLZ frozen web snapshot collector.

The stable deployment authenticates and dispatches to this fixed runtime source.
This module owns bounded collection, provenance, search preparation, explicit
training review, and private Vercel Blob persistence. ``/tmp`` is never an
authoritative collector store.
"""
from __future__ import annotations

import hashlib
import html
import ipaddress
import json
import math
import os
import re
import socket
import time
import urllib.parse
import urllib.robotparser
import uuid
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any

import requests
import urllib3
from fastapi.responses import JSONResponse

MODULE_ID = "frozen-web-collector"
API_SCHEMA_VERSION = 1
STATE_SCHEMA_VERSION = 1
STATE_PATH = "swrlz/collector/control/state.json"
BLOB_API = "https://vercel.com/api/blob"
USER_AGENT = "SWRLZFrozenCollector/1.0 (+https://swrlzkamico-o3nu.vercel.app/collector)"
ROBOTS_AGENT = "SWRLZFrozenCollector"
MAX_BODY_BYTES = 160_000
MAX_EVENTS = 180
MAX_REJECTED = 1_000
MAX_FRONTIER = 5_000
MAX_COMPLETED = 5_000
MAX_TRAINING_QUEUE = 1_000
MAX_ROBOTS_BYTES = 64_000
STATE_GROWTH_RESERVE_BYTES = 32_768
TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src"}
ALLOWED_MIMES = {"text/html", "application/xhtml+xml", "text/plain"}
STOP_WORDS = {
    "about", "after", "again", "also", "among", "and", "are", "because", "been", "before",
    "being", "between", "both", "but", "can", "could", "does", "each", "for", "from", "had",
    "has", "have", "into", "its", "more", "most", "not", "other", "our", "out", "over", "such",
    "than", "that", "the", "their", "then", "there", "these", "they", "this", "through", "under",
    "using", "very", "was", "were", "what", "when", "where", "which", "while", "will", "with",
    "would", "you", "your",
}


class CollectorError(Exception):
    def __init__(self, status: int, code: str, message: str, detail: Any = None):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.detail = detail


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_text(value: str) -> str:
    return _sha_bytes(value.encode("utf-8"))


def _compact_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _safe_error_text(response: requests.Response) -> str:
    try:
        body = response.json()
        message = body.get("error", body) if isinstance(body, dict) else body
        if isinstance(message, dict):
            message = message.get("message") or message.get("code") or "request rejected"
        return str(message)[:320]
    except Exception:
        return (response.text or response.reason or "request rejected")[:320]


class BlobStore:
    """Small Python transport matching the public Vercel Blob HTTP contract."""

    def __init__(self) -> None:
        read_write = os.environ.get("BLOB_READ_WRITE_TOKEN", "").strip()
        oidc = os.environ.get("VERCEL_OIDC_TOKEN", "").strip()
        configured_store = os.environ.get("BLOB_STORE_ID", "").strip()
        if read_write:
            pieces = read_write.split("_")
            store_id = pieces[3] if len(pieces) > 3 else ""
            self.auth_kind = "read-write"
            self.token = read_write
            self.store_id = store_id.removeprefix("store_")
        elif oidc and configured_store:
            self.auth_kind = "oidc"
            self.token = oidc
            self.store_id = configured_store.removeprefix("store_")
        else:
            self.auth_kind = "unconfigured"
            self.token = ""
            self.store_id = ""
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    @property
    def configured(self) -> bool:
        return bool(self.token and self.store_id)

    def describe(self) -> dict[str, Any]:
        return {
            "backend": "vercel-blob",
            "configured": self.configured,
            "access": "private",
            "authKind": self.auth_kind,
            "storeIdSuffix": self.store_id[-6:] if self.store_id else None,
            "authoritativeState": STATE_PATH,
            "ephemeralTmpUsedAsAuthority": False,
        }

    def require(self) -> None:
        if not self.configured:
            raise CollectorError(
                503,
                "STORAGE_NOT_CONFIGURED",
                "Private Vercel Blob is not connected to this production project.",
                "Expected BLOB_READ_WRITE_TOKEN or VERCEL_OIDC_TOKEN with BLOB_STORE_ID.",
            )

    def _headers(self, **extra: str) -> dict[str, str]:
        self.require()
        return {
            "authorization": f"Bearer {self.token}",
            "x-vercel-blob-store-id": self.store_id,
            "x-api-version": "12",
            "x-api-blob-request-attempt": "0",
            "x-api-blob-request-id": f"{self.store_id}:{int(time.time() * 1000)}:{uuid.uuid4().hex[:12]}",
            **extra,
        }

    def get_bytes(self, pathname: str) -> tuple[bytes | None, str | None, dict[str, str]]:
        self.require()
        encoded = urllib.parse.quote(pathname.lstrip("/"), safe="/-._~")
        url = f"https://{self.store_id}.private.blob.vercel-storage.com/{encoded}?cache=0"
        response = self.session.get(url, headers={"authorization": f"Bearer {self.token}"}, timeout=(5, 20))
        if response.status_code == 404:
            return None, None, {}
        if not response.ok:
            raise CollectorError(503, "BLOB_READ_FAILED", _safe_error_text(response))
        return response.content, response.headers.get("etag"), dict(response.headers)

    def get_json(self, pathname: str) -> tuple[dict[str, Any] | None, str | None]:
        data, etag, _headers = self.get_bytes(pathname)
        if data is None:
            return None, None
        try:
            value = json.loads(data.decode("utf-8"))
        except Exception as exc:
            raise CollectorError(503, "BLOB_JSON_INVALID", f"Stored JSON is invalid: {type(exc).__name__}") from exc
        if not isinstance(value, dict):
            raise CollectorError(503, "BLOB_JSON_SHAPE_INVALID", "Stored collector object is not a JSON object.")
        return value, etag

    def put_json(
        self,
        pathname: str,
        value: dict[str, Any],
        *,
        etag: str | None = None,
        immutable: bool = False,
        tolerate_existing: bool = False,
    ) -> dict[str, Any]:
        body = _compact_json(value)
        headers = self._headers(
            **{
                "content-type": "application/json; charset=utf-8",
                "x-content-type": "application/json; charset=utf-8",
                "x-vercel-blob-access": "private",
                "x-add-random-suffix": "0",
                "x-allow-overwrite": "0" if immutable else "1",
                "x-cache-control-max-age": "60",
            }
        )
        if etag:
            headers["x-if-match"] = etag
        response = self.session.put(
            BLOB_API + "/",
            params={"pathname": pathname},
            headers=headers,
            data=body,
            timeout=(5, 30),
        )
        if not response.ok:
            message = _safe_error_text(response)
            conflict = response.status_code in {400, 409, 412} and any(
                marker in message.lower() for marker in ("exist", "overwrite", "precondition", "etag")
            )
            if tolerate_existing and conflict:
                existing, existing_etag, _ = self.get_bytes(pathname)
                if existing == body:
                    return {
                        "ok": True,
                        "existed": True,
                        "pathname": pathname,
                        "bytes": len(body),
                        "etag": existing_etag,
                    }
                raise CollectorError(409, "IMMUTABLE_OBJECT_CONFLICT", "An immutable object exists with different content.")
            if conflict:
                raise CollectorError(409, "STATE_WRITE_CONFLICT", "Collector state changed on another worker; reload and retry.")
            raise CollectorError(503, "BLOB_WRITE_FAILED", message)
        try:
            result = response.json()
        except Exception:
            result = {}
        response_etag = response.headers.get("etag")
        return {
            "ok": True,
            "pathname": pathname,
            "bytes": len(body),
            "etag": response_etag,
            **(result if isinstance(result, dict) else {}),
        }

    def list(self, prefix: str, limit: int = 100) -> list[dict[str, Any]]:
        response = self.session.get(
            BLOB_API,
            params={"prefix": prefix, "limit": max(1, min(limit, 1_000))},
            headers=self._headers(),
            timeout=(5, 20),
        )
        if not response.ok:
            raise CollectorError(503, "BLOB_LIST_FAILED", _safe_error_text(response))
        value = response.json()
        blobs = value.get("blobs", []) if isinstance(value, dict) else []
        return [item for item in blobs if isinstance(item, dict)]


def _default_config() -> dict[str, Any]:
    return {
        "storageBudgetBytes": 100 * 1024 * 1024,
        "runBudgetSeconds": 1_800,
        "requestBudgetSeconds": 35,
        "maxPagesPerRun": 600,
        "maxDocuments": 500,
        "maxDepth": 2,
        "maxLinksPerPage": 30,
        "maxDocumentsPerDomain": 100,
        "maxBytesPerDomain": 20 * 1024 * 1024,
        "maxDomains": 12,
        "maxDocumentBytes": 1_500_000,
        "batchSize": 1,
        "minQuality": 0.62,
        "trainingMinQuality": 0.76,
        "minTextCharacters": 320,
        "chunkWords": 700,
        "chunkOverlapWords": 80,
        "minDelaySeconds": 1.0,
        "explorationPercent": 25,
        "respectRobots": True,
        "allowExternalDomains": False,
        "preferredDomains": [],
        "blockedDomains": [],
        "allowedMimeTypes": sorted(ALLOWED_MIMES),
    }


def _totals() -> dict[str, Any]:
    return {
        "pagesAttempted": 0,
        "documents": 0,
        "rejected": 0,
        "duplicates": 0,
        "bytesFetched": 0,
        "storedBytes": 0,
        "bytesSavedByDedup": 0,
        "chunks": 0,
        "explorationFetched": 0,
        "trainingPending": 0,
        "trainingAccepted": 0,
        "trainingRejected": 0,
        "runtimeSeconds": 0.0,
    }


def _default_state() -> dict[str, Any]:
    return {
        "schemaVersion": STATE_SCHEMA_VERSION,
        "moduleId": MODULE_ID,
        "stateRevision": 0,
        "status": "idle",
        "reason": "Ready for source configuration.",
        "snapshotId": None,
        "createdAt": _now(),
        "updatedAt": _now(),
        "startedAt": None,
        "sessionStartedAt": None,
        "sessionStartedEpoch": None,
        "sessionPages": 0,
        "runCounter": 0,
        "pausedAt": None,
        "sealedAt": None,
        "currentUrl": None,
        "lastUrl": None,
        "lastCheckpoint": None,
        "config": _default_config(),
        "sources": [],
        "frontier": [],
        "completed": {},
        "contentHashes": {},
        "urlRevisions": {},
        "rejected": [],
        "domainStats": {},
        "robots": {},
        "trainingQueue": [],
        "snapshots": [],
        "totals": _totals(),
        "events": [],
    }


def _load_state(store: BlobStore) -> tuple[dict[str, Any], str | None]:
    if not store.configured:
        return _default_state(), None
    value, etag = store.get_json(STATE_PATH)
    if value is None:
        return _default_state(), None
    if value.get("schemaVersion") != STATE_SCHEMA_VERSION or value.get("moduleId") != MODULE_ID:
        raise CollectorError(409, "STATE_SCHEMA_MISMATCH", "Stored collector state uses an incompatible schema.")
    return value, etag


def _save_state(store: BlobStore, state: dict[str, Any], etag: str | None) -> str | None:
    state["stateRevision"] = int(state.get("stateRevision", 0)) + 1
    state["updatedAt"] = _now()
    expected_revision = state["stateRevision"]
    result = store.put_json(STATE_PATH, state, etag=etag, immutable=etag is None)
    new_etag = result.get("etag") if isinstance(result.get("etag"), str) else None
    if new_etag:
        return new_etag
    persisted, fetched_etag = store.get_json(STATE_PATH)
    if persisted is None or int(persisted.get("stateRevision", -1)) != expected_revision:
        raise CollectorError(409, "STATE_WRITE_CONFLICT", "Collector state could not be confirmed after writing; reload and retry.")
    return fetched_etag


def _event(state: dict[str, Any], kind: str, message: str, **fields: Any) -> None:
    state.setdefault("events", []).append({"at": _now(), "kind": kind, "message": message, **fields})
    state["events"] = state["events"][-MAX_EVENTS:]


def _domain_matches(host: str, rule: str) -> bool:
    normalized = rule.strip().lower().lstrip(".")
    return bool(normalized) and (host == normalized or host.endswith("." + normalized))


def _normalize_domain(raw: str) -> str:
    value = raw.strip().lower().lstrip(".").rstrip(".")
    if not value:
        raise CollectorError(400, "DOMAIN_EMPTY", "Domain entries cannot be empty.")
    try:
        value = value.encode("idna").decode("ascii")
    except Exception as exc:
        raise CollectorError(400, "DOMAIN_INVALID", f"Invalid domain: {raw}") from exc
    if len(value) > 253 or not re.fullmatch(r"[a-z0-9.-]+", value):
        raise CollectorError(400, "DOMAIN_INVALID", f"Invalid domain: {raw}")
    return value


def _canonicalize(raw_url: str) -> str:
    raw_url = (raw_url or "").strip()
    if len(raw_url) > 2_048:
        raise CollectorError(400, "URL_TOO_LONG", "URL exceeds the 2,048 character limit.")
    try:
        parsed = urllib.parse.urlsplit(raw_url)
    except Exception as exc:
        raise CollectorError(400, "URL_INVALID", "URL could not be parsed.") from exc
    if parsed.scheme.lower() not in {"http", "https"}:
        raise CollectorError(400, "URL_SCHEME_REJECTED", "Only http and https URLs are allowed.")
    if parsed.username or parsed.password:
        raise CollectorError(400, "URL_CREDENTIALS_REJECTED", "URLs containing credentials are not allowed.")
    if not parsed.hostname:
        raise CollectorError(400, "URL_HOST_REQUIRED", "URL must include a hostname.")
    try:
        host = parsed.hostname.encode("idna").decode("ascii").lower().rstrip(".")
    except Exception as exc:
        raise CollectorError(400, "URL_HOST_INVALID", "Hostname is invalid.") from exc
    try:
        port = parsed.port
    except ValueError as exc:
        raise CollectorError(400, "URL_PORT_INVALID", "URL port is invalid.") from exc
    if port not in {None, 80, 443}:
        raise CollectorError(400, "URL_PORT_REJECTED", "Only ports 80 and 443 are allowed.")
    netloc = f"[{host}]" if ":" in host else host
    if port and not ((parsed.scheme.lower() == "http" and port == 80) or (parsed.scheme.lower() == "https" and port == 443)):
        netloc = f"{netloc}:{port}"
    path = urllib.parse.quote(urllib.parse.unquote(parsed.path or "/"), safe="/%:@-._~!$&'()*+,;=")
    pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    pairs = [(key, value) for key, value in pairs if not key.lower().startswith("utm_") and key.lower() not in TRACKING_KEYS]
    query = urllib.parse.urlencode(sorted(pairs), doseq=True)
    return urllib.parse.urlunsplit((parsed.scheme.lower(), netloc, path, query, ""))


def _validate_public_url(url: str, config: dict[str, Any]) -> tuple[str, list[str]]:
    canonical = _canonicalize(url)
    parsed = urllib.parse.urlsplit(canonical)
    host = parsed.hostname or ""
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal", ".localhost")):
        raise CollectorError(400, "SSRF_HOST_REJECTED", "Local and internal hostnames are blocked.")
    if any(_domain_matches(host, item) for item in config.get("blockedDomains", [])):
        raise CollectorError(403, "DOMAIN_BLOCKED", "This domain is in the collector block registry.")
    try:
        records = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise CollectorError(422, "DNS_RESOLUTION_FAILED", f"DNS resolution failed for {host}.") from exc
    addresses = sorted({record[4][0] for record in records})
    if not addresses:
        raise CollectorError(422, "DNS_EMPTY", f"DNS returned no addresses for {host}.")
    for address in addresses:
        ip = ipaddress.ip_address(address.split("%", 1)[0])
        if not ip.is_global:
            raise CollectorError(403, "SSRF_ADDRESS_REJECTED", f"Non-public address blocked for {host}.")
    return canonical, addresses


class _PinnedResponse:
    def __init__(self, response: Any, pool: Any) -> None:
        self._response = response
        self._pool = pool
        self.status_code = int(response.status)
        self.reason = str(response.reason or "")
        self.headers = response.headers
        content_type = str(response.headers.get("content-type", ""))
        charset = re.search(r"charset\s*=\s*['\"]?([^;\s'\"]+)", content_type, re.I)
        self.encoding = charset.group(1) if charset else "utf-8"

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    def iter_content(self, chunk_size: int = 65_536):
        while True:
            chunk = self._response.read(chunk_size, decode_content=True)
            if not chunk:
                break
            yield chunk

    def close(self) -> None:
        try:
            self._response.release_conn()
        finally:
            self._pool.close()


def _pinned_get(
    url: str,
    addresses: list[str],
    *,
    headers: dict[str, str],
    connect_timeout: float,
    read_timeout: float,
) -> _PinnedResponse:
    """Connect through a validated public address to prevent DNS rebinding."""

    parsed = urllib.parse.urlsplit(url)
    hostname = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    target = parsed.path or "/"
    if parsed.query:
        target += "?" + parsed.query
    authority = f"[{hostname}]" if ":" in hostname else hostname
    if parsed.port is not None:
        authority += f":{parsed.port}"
    request_headers = {**headers, "Host": authority}
    timeout = urllib3.Timeout(connect=connect_timeout, read=read_timeout)
    last_error: Exception | None = None
    for address in addresses[:4]:
        if parsed.scheme == "https":
            pool: Any = urllib3.HTTPSConnectionPool(
                address,
                port=port,
                timeout=timeout,
                retries=False,
                cert_reqs="CERT_REQUIRED",
                assert_hostname=hostname,
                server_hostname=hostname,
            )
        else:
            pool = urllib3.HTTPConnectionPool(address, port=port, timeout=timeout, retries=False)
        try:
            response = pool.urlopen(
                "GET",
                target,
                headers=request_headers,
                redirect=False,
                preload_content=False,
                decode_content=True,
            )
            return _PinnedResponse(response, pool)
        except Exception as exc:
            last_error = exc
            pool.close()
    raise CollectorError(
        422,
        "FETCH_CONNECT_FAILED",
        f"Unable to connect to a validated public address for {hostname}: {type(last_error).__name__}",
    )


class _TextExtractor(HTMLParser):
    BLOCKS = {"article", "blockquote", "br", "dd", "div", "dt", "h1", "h2", "h3", "h4", "h5", "h6", "li", "main", "p", "pre", "section", "td", "th", "title"}
    SKIP = {"aside", "canvas", "footer", "form", "nav", "noscript", "script", "style", "svg", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.skip_depth = 0
        self.language: str | None = None
        self.license_notes: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {key.lower(): value or "" for key, value in attrs}
        if tag == "html" and attrs_map.get("lang"):
            self.language = attrs_map["lang"][:40]
        if tag in self.SKIP:
            self.skip_depth += 1
        if self.skip_depth:
            return
        if tag in self.BLOCKS:
            self.parts.append("\n")
        if tag == "title":
            self.in_title = True
        if tag == "a" and attrs_map.get("href"):
            self.links.append(attrs_map["href"][:2_048])
        if tag == "link" and "license" in attrs_map.get("rel", "").lower() and attrs_map.get("href"):
            self.license_notes.append(attrs_map["href"][:500])
        if tag == "meta":
            name = (attrs_map.get("name") or attrs_map.get("property") or "").lower()
            if name in {"license", "rights", "copyright"} and attrs_map.get("content"):
                self.license_notes.append(attrs_map["content"][:500])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1
            return
        if not self.skip_depth and tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_title:
            self.title_parts.append(data)
        self.parts.append(data)


def _normalize_text(value: str) -> str:
    value = value.replace("\r", "\n").replace("\u00a0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in value.split("\n")]
    output: list[str] = []
    blank = False
    for line in lines:
        if line:
            output.append(line)
            blank = False
        elif output and not blank:
            output.append("")
            blank = True
    return "\n".join(output).strip()


def _extract(body: bytes, content_type: str, url: str) -> dict[str, Any]:
    charset_match = re.search(r"charset\s*=\s*([^;\s]+)", content_type, re.I)
    charset = charset_match.group(1).strip("'\"") if charset_match else "utf-8"
    try:
        decoded = body.decode(charset, errors="replace")
    except LookupError:
        decoded = body.decode("utf-8", errors="replace")
    mime = content_type.split(";", 1)[0].strip().lower()
    if mime == "text/plain":
        text = _normalize_text(decoded)
        title = urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1] or urllib.parse.urlsplit(url).hostname or "Untitled"
        return {"title": title[:300], "text": text, "links": [], "language": None, "licenseNotes": []}
    parser = _TextExtractor()
    try:
        parser.feed(decoded)
        parser.close()
    except Exception as exc:
        raise CollectorError(422, "HTML_PARSE_FAILED", f"HTML parsing failed: {type(exc).__name__}") from exc
    title = _normalize_text(" ".join(parser.title_parts))[:300]
    if not title:
        title = urllib.parse.urlsplit(url).hostname or "Untitled"
    return {
        "title": html.unescape(title),
        "text": _normalize_text("".join(parser.parts)),
        "links": parser.links[:600],
        "language": parser.language,
        "licenseNotes": parser.license_notes[:12],
    }


def _tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9][a-z0-9_-]{1,40}", text.lower()) if token not in STOP_WORDS]


def _term_profile(text: str, limit: int = 48) -> tuple[dict[str, int], int]:
    tokens = _tokenize(text)
    return dict(Counter(tokens).most_common(limit)), len(tokens)


def _quality(extracted: dict[str, Any], source_priority: int) -> dict[str, Any]:
    text = extracted["text"]
    tokens = _tokenize(text)
    unique_ratio = len(set(tokens)) / max(1, len(tokens))
    sentence_count = len(re.findall(r"[.!?](?:\s|$)", text))
    length_score = min(len(text) / 8_000, 1.0) * 0.35
    diversity_score = min(unique_ratio / 0.45, 1.0) * 0.20
    structure_score = min(sentence_count / 20, 1.0) * 0.15
    title_score = 0.10 if extracted.get("title") and extracted["title"] != "Untitled" else 0.0
    source_score = max(0, min(source_priority, 100)) / 100 * 0.20
    score = round(max(0.0, min(1.0, length_score + diversity_score + structure_score + title_score + source_score)), 4)
    email_count = len(re.findall(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", text))
    phone_count = len(re.findall(r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)", text))
    privacy_risk = "review" if email_count or phone_count else "low"
    return {
        "score": score,
        "characters": len(text),
        "words": len(tokens),
        "uniqueRatio": round(unique_ratio, 4),
        "sentences": sentence_count,
        "privacyRisk": privacy_risk,
        "emailMatches": email_count,
        "phoneMatches": phone_count,
    }


def _chunk_text(text: str, words_per_chunk: int, overlap: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    step = max(1, words_per_chunk - overlap)
    return [" ".join(words[start:start + words_per_chunk]) for start in range(0, len(words), step) if words[start:start + words_per_chunk]]


def _snapshot_prefix(snapshot_id: str) -> str:
    return f"swrlz/collector/snapshots/{snapshot_id}"


def _source_for_item(state: dict[str, Any], item: dict[str, Any]) -> dict[str, Any] | None:
    return next((source for source in state.get("sources", []) if source.get("id") == item.get("sourceId")), None)


def _registered_hosts(state: dict[str, Any]) -> set[str]:
    return {
        str(source.get("host"))
        for source in state.get("sources", [])
        if source.get("enabled", True) and source.get("host")
    }


def _domain_state(state: dict[str, Any], host: str) -> dict[str, Any]:
    return state.setdefault("domainStats", {}).setdefault(host, {
        "attempted": 0,
        "accepted": 0,
        "rejected": 0,
        "duplicates": 0,
        "bytes": 0,
        "storedBytes": 0,
        "nextAllowedAt": 0.0,
        "lastFetchAt": None,
    })


def _fetch_robots(state: dict[str, Any], url: str) -> tuple[bool, float, str, bool]:
    config = state["config"]
    if not config.get("respectRobots", True):
        return True, float(config["minDelaySeconds"]), "robots-disabled-by-admin", False
    parsed = urllib.parse.urlsplit(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    cached = state.setdefault("robots", {}).get(origin)
    now_epoch = time.time()
    fresh = False
    if not cached or now_epoch - float(cached.get("fetchedEpoch", 0)) > 86_400:
        fresh = True
        robots_url = origin + "/robots.txt"
        try:
            for _redirect in range(4):
                robots_url, addresses = _validate_public_url(robots_url, config)
                response = _pinned_get(
                    robots_url,
                    addresses,
                    headers={"User-Agent": USER_AGENT, "Accept": "text/plain", "Accept-Encoding": "gzip, deflate"},
                    connect_timeout=5,
                    read_timeout=10,
                )
                try:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location", "")
                        if not location:
                            raise CollectorError(422, "ROBOTS_REDIRECT_INVALID", "robots.txt redirect omitted its location.")
                        robots_url = _canonicalize(urllib.parse.urljoin(robots_url, location))
                        continue
                    if response.status_code == 404:
                        body = ""
                        status = 404
                    elif response.ok:
                        robots_data = bytearray()
                        for chunk in response.iter_content(chunk_size=16_384):
                            robots_data.extend(chunk)
                            if len(robots_data) > MAX_ROBOTS_BYTES:
                                raise CollectorError(413, "ROBOTS_TOO_LARGE", "robots.txt exceeded the safety limit.")
                        body = bytes(robots_data).decode(response.encoding or "utf-8", errors="replace")
                        status = response.status_code
                        state["totals"]["bytesFetched"] += len(robots_data)
                    else:
                        body = "User-agent: *\nDisallow: /"
                        status = response.status_code
                finally:
                    response.close()
                break
            else:
                raise CollectorError(422, "ROBOTS_REDIRECT_LIMIT", "robots.txt exceeded the redirect limit.")
            cached = {"fetchedAt": _now(), "fetchedEpoch": now_epoch, "status": status, "body": body[:MAX_ROBOTS_BYTES]}
        except Exception as exc:
            cached = {
                "fetchedAt": _now(),
                "fetchedEpoch": now_epoch,
                "status": 0,
                "body": "User-agent: *\nDisallow: /",
                "error": f"{type(exc).__name__}: {exc}"[:240],
            }
        state["robots"][origin] = cached
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(origin + "/robots.txt")
    parser.parse(str(cached.get("body", "")).splitlines())
    allowed = bool(parser.can_fetch(ROBOTS_AGENT, url))
    delay = parser.crawl_delay(ROBOTS_AGENT) or parser.crawl_delay("*") or float(config["minDelaySeconds"])
    return allowed, max(float(config["minDelaySeconds"]), min(float(delay), 60.0)), "robots-allowed" if allowed else "robots-denied", fresh


def _fetch_document(state: dict[str, Any], url: str) -> dict[str, Any]:
    config = state["config"]
    current = url
    redirects: list[dict[str, Any]] = []
    for _ in range(5):
        current, addresses = _validate_public_url(current, config)
        response = _pinned_get(
            current,
            addresses,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
                "Accept-Encoding": "gzip, deflate",
            },
            connect_timeout=5,
            read_timeout=15,
        )
        if response.status_code in {301, 302, 303, 307, 308}:
            location = response.headers.get("location", "")
            response.close()
            if not location:
                raise CollectorError(422, "REDIRECT_LOCATION_MISSING", "Redirect response did not include a location.")
            target = _canonicalize(urllib.parse.urljoin(current, location))
            target, _target_addresses = _validate_public_url(target, config)
            target_host = urllib.parse.urlsplit(target).hostname or ""
            if not config.get("allowExternalDomains") and target_host not in _registered_hosts(state):
                raise CollectorError(403, "REDIRECT_DOMAIN_REJECTED", "Redirect left the registered source domains.")
            known_domains = set(state.get("domainStats", {})) | _registered_hosts(state)
            if target_host not in known_domains and len(known_domains) >= int(config["maxDomains"]):
                raise CollectorError(429, "DOMAIN_QUOTA", "Redirect would exceed the configured domain budget.")
            target_domain = _domain_state(state, target_host)
            wait_seconds = max(0.0, float(target_domain.get("nextAllowedAt", 0)) - time.time())
            if wait_seconds > 0:
                raise CollectorError(
                    425,
                    "REDIRECT_POLITENESS_WAIT",
                    "Redirect destination is waiting for its domain politeness window.",
                    {"retryAfterSeconds": round(wait_seconds, 2)},
                )
            allowed, delay, _reason, robots_fresh = _fetch_robots(state, target)
            target_domain["nextAllowedAt"] = time.time() + delay
            if not allowed:
                raise CollectorError(403, "ROBOTS_DENIED", "robots.txt does not allow the redirect destination.")
            if robots_fresh:
                raise CollectorError(
                    425,
                    "ROBOTS_REFRESH_REQUIRED",
                    "Redirect destination robots policy was cached; retry after its politeness delay.",
                    {"retryAfterSeconds": round(delay, 2)},
                )
            redirects.append({"from": current, "to": target, "status": response.status_code})
            current = target
            continue
        if not response.ok:
            status = response.status_code
            response.close()
            raise CollectorError(422, "FETCH_HTTP_ERROR", f"Source returned HTTP {status}.")
        content_type = response.headers.get("content-type", "application/octet-stream")
        mime = content_type.split(";", 1)[0].strip().lower()
        if mime not in set(config["allowedMimeTypes"]):
            response.close()
            raise CollectorError(415, "MIME_REJECTED", f"Content type {mime or 'unknown'} is not enabled.")
        declared = response.headers.get("content-length", "")
        if declared.isdigit() and int(declared) > int(config["maxDocumentBytes"]):
            response.close()
            raise CollectorError(413, "DOCUMENT_TOO_LARGE", "Declared response size exceeds the document limit.")
        data = bytearray()
        try:
            for chunk in response.iter_content(chunk_size=65_536):
                if chunk:
                    data.extend(chunk)
                if len(data) > int(config["maxDocumentBytes"]):
                    raise CollectorError(413, "DOCUMENT_TOO_LARGE", "Decoded response exceeds the document limit.")
            headers = {
                key.lower(): value[:500]
                for key, value in response.headers.items()
                if key.lower() in {"content-type", "content-length", "etag", "last-modified", "date", "cache-control"}
            }
            status = response.status_code
        finally:
            response.close()
        return {
            "url": current,
            "addresses": addresses,
            "status": status,
            "contentType": content_type,
            "headers": headers,
            "body": bytes(data),
            "redirects": redirects,
            "fetchedAt": _now(),
        }
    raise CollectorError(422, "REDIRECT_LIMIT", "Source exceeded the four-redirect limit.")


def _frontier_has(state: dict[str, Any], url: str) -> bool:
    return any(item.get("url") == url for item in state.get("frontier", []))


def _enqueue_links(state: dict[str, Any], base_url: str, links: list[str], depth: int, source_id: str | None) -> int:
    config = state["config"]
    source = next((item for item in state.get("sources", []) if item.get("id") == source_id), None) or {}
    policy = str(source.get("policy", "balanced"))
    global_depth = int(config["maxDepth"])
    policy_depth = min(global_depth, 1) if policy == "shallow" else min(global_depth, 2) if policy == "balanced" else global_depth
    if depth > policy_depth:
        return 0
    seed_hosts = _registered_hosts(state)
    preferred = config.get("preferredDomains", [])
    blocked = config.get("blockedDomains", [])
    existing_domains = set(state.get("domainStats", {})) | {item for item in seed_hosts if item}
    added = 0
    for raw in links:
        try:
            candidate = _canonicalize(urllib.parse.urljoin(base_url, raw))
            host = urllib.parse.urlsplit(candidate).hostname or ""
            if any(_domain_matches(host, item) for item in blocked):
                continue
            if not config.get("allowExternalDomains") and host not in seed_hosts:
                continue
            if host not in existing_domains and len(existing_domains) >= int(config["maxDomains"]):
                continue
            if candidate in state.get("completed", {}) or _frontier_has(state, candidate):
                continue
            preferred_host = any(_domain_matches(host, item) for item in preferred)
            exploration = host not in seed_hosts and not preferred_host
            source_priority = int(source.get("priority", 60))
            inherited_priority = max(1, min(100, source_priority - depth * 5))
            state["frontier"].append({
                "url": candidate,
                "depth": depth,
                "sourceId": source_id,
                "referrer": base_url,
                "priority": min(100, inherited_priority + 10) if preferred_host else inherited_priority if host in seed_hosts else min(35, inherited_priority),
                "exploration": exploration,
                "discoveredAt": _now(),
            })
            existing_domains.add(host)
            added += 1
            if added >= int(config["maxLinksPerPage"]) or len(state["frontier"]) >= MAX_FRONTIER:
                break
        except CollectorError:
            continue
    return added


def _reject(state: dict[str, Any], item: dict[str, Any], code: str, message: str) -> None:
    record = {"url": item.get("url"), "depth": item.get("depth"), "code": code, "message": message[:320], "at": _now()}
    state.setdefault("rejected", []).append(record)
    state["rejected"] = state["rejected"][-MAX_REJECTED:]
    state["totals"]["rejected"] += 1
    host = urllib.parse.urlsplit(str(item.get("url", ""))).hostname or "unknown"
    _domain_state(state, host)["rejected"] += 1
    state.setdefault("completed", {})[str(item.get("url"))] = {"status": "rejected", **record}
    _event(state, "rejected", f"Rejected {item.get('url')}", code=code)


def _pressure(state: dict[str, Any]) -> dict[str, Any]:
    config = state["config"]
    totals = state["totals"]
    state_bytes = len(_compact_json(state))
    storage_used = int(totals.get("storedBytes", 0)) + state_bytes
    storage_ratio = storage_used / max(1, int(config["storageBudgetBytes"]))
    document_ratio = int(totals.get("documents", 0)) / max(1, int(config["maxDocuments"]))
    page_ratio = int(state.get("sessionPages", 0)) / max(1, int(config["maxPagesPerRun"]))
    elapsed = 0.0
    if state.get("status") == "running" and state.get("sessionStartedEpoch"):
        elapsed = max(0.0, time.time() - float(state["sessionStartedEpoch"]))
    runtime_ratio = elapsed / max(1, int(config["runBudgetSeconds"]))
    highest = max(storage_ratio, document_ratio, page_ratio, runtime_ratio)
    level = "stop" if highest >= 0.95 else "pressure" if highest >= 0.85 else "warning" if highest >= 0.70 else "normal"
    return {
        "level": level,
        "highestRatio": round(highest, 4),
        "storageRatio": round(storage_ratio, 4),
        "documentRatio": round(document_ratio, 4),
        "pageRatio": round(page_ratio, 4),
        "runtimeRatio": round(runtime_ratio, 4),
        "storageUsedBytes": storage_used,
        "stateBytes": state_bytes,
        "sessionElapsedSeconds": round(elapsed, 2),
        "thresholds": {"warning": 0.70, "pressure": 0.85, "automaticPause": 0.95},
    }


def _choose_frontier(state: dict[str, Any]) -> tuple[dict[str, Any] | None, float]:
    now_epoch = time.time()
    ready: list[dict[str, Any]] = []
    next_epoch: float | None = None
    for item in state.get("frontier", []):
        host = urllib.parse.urlsplit(str(item.get("url", ""))).hostname or ""
        allowed_at = float(_domain_state(state, host).get("nextAllowedAt", 0))
        if allowed_at <= now_epoch:
            ready.append(item)
        elif next_epoch is None or allowed_at < next_epoch:
            next_epoch = allowed_at
    if not ready:
        return None, max(0.0, (next_epoch or now_epoch) - now_epoch)
    pressure_level = _pressure(state)["level"]
    exploration = [item for item in ready if item.get("exploration")]
    ratio = int(state["totals"].get("explorationFetched", 0)) / max(1, int(state["totals"].get("pagesAttempted", 0)))
    target = float(state["config"].get("explorationPercent", 25)) / 100
    if exploration and ratio < target and pressure_level not in {"pressure", "stop"}:
        candidates = exploration
    else:
        candidates = [item for item in ready if not item.get("exploration")] or ready
    item = sorted(candidates, key=lambda entry: (-int(entry.get("priority", 0)), int(entry.get("depth", 0)), entry.get("discoveredAt", "")))[0]
    state["frontier"].remove(item)
    return item, 0.0


def _write_immutable(store: BlobStore, state: dict[str, Any], path: str, value: dict[str, Any]) -> dict[str, Any]:
    result = store.put_json(path, value, immutable=True, tolerate_existing=True)
    if not result.get("existed"):
        state["totals"]["storedBytes"] += int(result.get("bytes", 0))
    return result


def _process_item(store: BlobStore, state: dict[str, Any], item: dict[str, Any], context: Any) -> dict[str, Any]:
    canonical, _addresses = _validate_public_url(str(item.get("url", "")), state["config"])
    host = urllib.parse.urlsplit(canonical).hostname or "unknown"
    domain = _domain_state(state, host)
    config = state["config"]
    if int(domain["accepted"]) >= int(config["maxDocumentsPerDomain"]):
        raise CollectorError(429, "DOMAIN_DOCUMENT_QUOTA", "Per-domain document quota reached.")
    if int(domain["bytes"]) >= int(config["maxBytesPerDomain"]):
        raise CollectorError(429, "DOMAIN_BYTE_QUOTA", "Per-domain byte quota reached.")
    robots_allowed, delay, robots_reason, robots_fresh = _fetch_robots(state, canonical)
    domain["nextAllowedAt"] = time.time() + delay
    if not robots_allowed:
        raise CollectorError(403, "ROBOTS_DENIED", "robots.txt does not allow this collector URL.")
    if robots_fresh:
        state["frontier"].append(item)
        return {"result": "robots-cached", "retryAfterSeconds": round(delay, 2)}

    state["totals"]["pagesAttempted"] += 1
    state["sessionPages"] = int(state.get("sessionPages", 0)) + 1
    domain["attempted"] += 1
    if item.get("exploration"):
        state["totals"]["explorationFetched"] += 1
    fetched = _fetch_document(state, canonical)
    final_host = urllib.parse.urlsplit(fetched["url"]).hostname or host
    if final_host != host:
        domain = _domain_state(state, final_host)
        domain["attempted"] += 1
        host = final_host
        if int(domain["accepted"]) >= int(config["maxDocumentsPerDomain"]):
            raise CollectorError(429, "DOMAIN_DOCUMENT_QUOTA", "Redirect destination reached its document quota.")
        if int(domain["bytes"]) >= int(config["maxBytesPerDomain"]):
            raise CollectorError(429, "DOMAIN_BYTE_QUOTA", "Redirect destination reached its byte quota.")
    domain["lastFetchAt"] = fetched["fetchedAt"]
    if int(domain["bytes"]) + len(fetched["body"]) > int(config["maxBytesPerDomain"]):
        raise CollectorError(429, "DOMAIN_BYTE_QUOTA", "This response would exceed the per-domain byte quota.")
    state["totals"]["bytesFetched"] += len(fetched["body"])
    domain["bytes"] += len(fetched["body"])
    extracted = _extract(fetched["body"], fetched["contentType"], fetched["url"])
    source = _source_for_item(state, item) or {}
    quality = _quality(extracted, int(source.get("priority", item.get("priority", 50))))
    if quality["characters"] < int(config["minTextCharacters"]):
        raise CollectorError(422, "TEXT_TOO_SHORT", "Extracted useful text is below the configured minimum.")
    if quality["score"] < float(config["minQuality"]):
        raise CollectorError(422, "QUALITY_REJECTED", f"Quality score {quality['score']:.2f} is below the configured threshold.")

    text = extracted["text"]
    content_hash = _sha_text(text)
    previous = state.setdefault("contentHashes", {}).get(content_hash)
    if previous:
        state["totals"]["duplicates"] += 1
        state["totals"]["bytesSavedByDedup"] += len(text.encode("utf-8"))
        domain["duplicates"] += 1
        state["completed"][canonical] = {
            "status": "duplicate",
            "at": _now(),
            "duplicateOf": previous,
            "contentSha256": content_hash,
            "title": extracted["title"],
            "url": canonical,
        }
        return {"result": "duplicate", "contentSha256": content_hash, "duplicateOf": previous}

    chunks = _chunk_text(text, int(config["chunkWords"]), int(config["chunkOverlapWords"]))
    chunk_refs: list[dict[str, Any]] = []
    chunk_artifacts: list[tuple[str, dict[str, Any]]] = []
    prefix = _snapshot_prefix(str(state["snapshotId"]))
    for index, chunk in enumerate(chunks):
        chunk_hash = _sha_text(chunk)
        chunk_value = {"schemaVersion": 1, "sha256": chunk_hash, "text": chunk, "words": len(chunk.split())}
        chunk_path = f"{prefix}/chunks/{chunk_hash}.json"
        chunk_artifacts.append((chunk_path, chunk_value))
        chunk_refs.append({"index": index, "sha256": chunk_hash, "path": chunk_path})

    term_freq, word_count = _term_profile(text)
    previous_hash = state.setdefault("urlRevisions", {}).get(canonical)
    provenance = {
        "canonicalUrl": fetched["url"],
        "requestedUrl": canonical,
        "sourceDomain": host,
        "capturedAt": fetched["fetchedAt"],
        "snapshotId": state["snapshotId"],
        "contentSha256": content_hash,
        "previousContentSha256": previous_hash,
        "resolvedPublicAddresses": fetched["addresses"],
        "redirects": fetched["redirects"],
        "responseHeaders": fetched["headers"],
        "robots": robots_reason,
        "sourceId": item.get("sourceId"),
        "sourcePriority": source.get("priority", item.get("priority")),
        "sourceLicenseNote": source.get("licenseNote") or None,
        "documentLicenseNotes": extracted.get("licenseNotes", []),
    }
    document = {
        "schemaVersion": 1,
        "snapshotId": state["snapshotId"],
        "contentSha256": content_hash,
        "title": extracted["title"],
        "language": extracted.get("language"),
        "text": text,
        "quality": quality,
        "provenance": provenance,
        "chunks": chunk_refs,
        "importantLinks": extracted["links"][: int(config["maxLinksPerPage"])],
    }
    document_path = f"{prefix}/documents/{content_hash}.json"
    revision = {
        "schemaVersion": 1,
        "snapshotId": state["snapshotId"],
        "canonicalUrl": canonical,
        "contentSha256": content_hash,
        "previousContentSha256": previous_hash,
        "documentPath": document_path,
        "capturedAt": fetched["fetchedAt"],
        "revisionSha256": _sha_text(f"{canonical}\n{content_hash}\n{fetched['fetchedAt']}"),
    }
    revision_path = f"{prefix}/revisions/{revision['revisionSha256']}.json"

    candidate: dict[str, Any] | None = None
    license_notes = [note for note in [source.get("licenseNote"), *extracted.get("licenseNotes", [])] if note]
    if quality["score"] >= float(config["trainingMinQuality"]) and quality["privacyRisk"] == "low":
        candidate_id = f"candidate-{_sha_text(str(state['snapshotId']))[:8]}-{content_hash[:18]}"
        candidate = {
            "id": candidate_id,
            "status": "pending",
            "snapshotId": state["snapshotId"],
            "documentSha256": content_hash,
            "documentPath": document_path,
            "url": canonical,
            "title": extracted["title"],
            "quality": quality["score"],
            "privacyCheck": "pass",
            "licenseNotes": license_notes,
            "rightsConfirmationRequired": True,
            "createdAt": _now(),
        }
    artifacts: list[tuple[str, dict[str, Any]]] = [
        *chunk_artifacts,
        (document_path, document),
        (revision_path, revision),
    ]
    if candidate is not None:
        artifacts.append((f"{prefix}/training_candidates/{candidate['id']}.json", candidate))
    planned_bytes = sum(len(_compact_json(value)) for _path, value in artifacts)
    projected_bytes = (
        int(state["totals"].get("storedBytes", 0))
        + len(_compact_json(state))
        + planned_bytes
        + STATE_GROWTH_RESERVE_BYTES
    )
    safety_limit = int(int(config["storageBudgetBytes"]) * 0.95)
    if projected_bytes > safety_limit:
        raise CollectorError(
            507,
            "STORAGE_BUDGET_PREFLIGHT",
            "The accepted document would cross the 95% storage safety threshold; collection paused before writing artifacts.",
            {"projectedBytes": projected_bytes, "safetyLimitBytes": safety_limit, "plannedArtifactBytes": planned_bytes},
        )

    new_artifact_bytes = 0
    for artifact_path, artifact_value in artifacts:
        result = _write_immutable(store, state, artifact_path, artifact_value)
        if not result.get("existed"):
            new_artifact_bytes += int(result.get("bytes", 0))
            if "/chunks/" in artifact_path:
                state["totals"]["chunks"] += 1

    if candidate is not None and not any(existing.get("id") == candidate["id"] for existing in state.get("trainingQueue", [])):
        state.setdefault("trainingQueue", []).append(candidate)
        state["trainingQueue"] = state["trainingQueue"][-MAX_TRAINING_QUEUE:]
        state["totals"]["trainingPending"] += 1

    added_links = _enqueue_links(state, fetched["url"], extracted["links"], int(item.get("depth", 0)) + 1, item.get("sourceId"))
    completed_record = {
        "status": "accepted",
        "url": canonical,
        "finalUrl": fetched["url"],
        "title": extracted["title"],
        "contentSha256": content_hash,
        "documentPath": document_path,
        "quality": quality,
        "capturedAt": fetched["fetchedAt"],
        "sourceDomain": host,
        "sourceId": item.get("sourceId"),
        "termFreq": term_freq,
        "wordCount": word_count,
        "excerpt": text[:500],
        "chunks": len(chunk_refs),
    }
    state["completed"][canonical] = completed_record
    state["contentHashes"][content_hash] = canonical
    state["urlRevisions"][canonical] = content_hash
    state["totals"]["documents"] += 1
    domain["accepted"] += 1
    domain["storedBytes"] += new_artifact_bytes
    _event(state, "accepted", f"Accepted {canonical}", quality=quality["score"], linksAdded=added_links)
    context.activity("accepted", snapshotId=state["snapshotId"], domain=host, quality=quality["score"])
    return {
        "result": "accepted",
        "contentSha256": content_hash,
        "quality": quality["score"],
        "chunks": len(chunk_refs),
        "linksAdded": added_links,
        "trainingCandidate": candidate["id"] if candidate else None,
    }


def _trim_state(state: dict[str, Any]) -> None:
    if len(state.get("completed", {})) > MAX_COMPLETED:
        ordered = list(state["completed"].items())[-MAX_COMPLETED:]
        state["completed"] = dict(ordered)
    state["frontier"] = state.get("frontier", [])[:MAX_FRONTIER]
    state["rejected"] = state.get("rejected", [])[-MAX_REJECTED:]
    state["events"] = state.get("events", [])[-MAX_EVENTS:]


def _process_batch(store: BlobStore, state: dict[str, Any], etag: str | None, context: Any) -> tuple[list[dict[str, Any]], str | None]:
    store.require()
    if state.get("status") != "running":
        raise CollectorError(409, "COLLECTOR_NOT_RUNNING", "Start or continue the collector before running a batch.")
    started = time.monotonic()
    last_accounted = started
    results: list[dict[str, Any]] = []
    for _ in range(int(state["config"]["batchSize"])):
        pressure = _pressure(state)
        if pressure["storageRatio"] >= 0.95:
            state["status"] = "paused"
            state["pausedAt"] = _now()
            state["reason"] = "Automatically paused at the 95% storage safety threshold."
            _event(state, "budget-stop", state["reason"], pressure=pressure)
            break
        if int(state["totals"]["documents"]) >= int(state["config"]["maxDocuments"]):
            state["status"] = "ready-to-seal"
            state["reason"] = "Document budget reached; snapshot is ready to seal."
            break
        if int(state.get("sessionPages", 0)) >= int(state["config"]["maxPagesPerRun"]):
            state["status"] = "paused"
            state["pausedAt"] = _now()
            state["reason"] = "Paused at the per-run page budget. Continue to begin another bounded session."
            break
        if state.get("sessionStartedEpoch") and time.time() - float(state["sessionStartedEpoch"]) >= int(state["config"]["runBudgetSeconds"]):
            state["status"] = "paused"
            state["pausedAt"] = _now()
            state["reason"] = "Paused at the per-run time budget. Continue to begin another bounded session."
            break
        if time.monotonic() - started >= float(state["config"]["requestBudgetSeconds"]):
            state["reason"] = "Request time slice ended safely; collection remains resumable."
            break

        item, wait_seconds = _choose_frontier(state)
        if item is None:
            if state.get("frontier"):
                state["reason"] = "Waiting for the next domain politeness window."
                results.append({"result": "politeness-wait", "retryAfterSeconds": round(wait_seconds, 2)})
            else:
                state["status"] = "ready-to-seal"
                state["reason"] = "Frontier exhausted; snapshot is ready to seal."
            break
        state["currentUrl"] = item.get("url")
        try:
            item_result = _process_item(store, state, item, context)
            results.append({"url": item.get("url"), **item_result})
        except CollectorError as exc:
            if exc.code == "STORAGE_BUDGET_PREFLIGHT":
                state["frontier"].insert(0, item)
                state["status"] = "paused"
                state["pausedAt"] = _now()
                state["reason"] = exc.message
                _event(state, "budget-stop", exc.message, detail=exc.detail)
                results.append({"url": item.get("url"), "result": "paused", "code": exc.code, "message": exc.message})
            elif exc.code in {"ROBOTS_REFRESH_REQUIRED", "REDIRECT_POLITENESS_WAIT"}:
                state["frontier"].insert(0, item)
                state["reason"] = exc.message
                results.append({
                    "url": item.get("url"),
                    "result": "deferred",
                    "code": exc.code,
                    "message": exc.message,
                    "retryAfterSeconds": (exc.detail or {}).get("retryAfterSeconds", 1.0),
                })
            else:
                _reject(state, item, exc.code, exc.message)
                results.append({"url": item.get("url"), "result": "rejected", "code": exc.code, "message": exc.message})
        except Exception as exc:
            _reject(state, item, "FETCH_UNEXPECTED", f"{type(exc).__name__}: {exc}")
            results.append({"url": item.get("url"), "result": "rejected", "code": "FETCH_UNEXPECTED"})
        state["lastUrl"] = item.get("url")
        state["currentUrl"] = None
        _trim_state(state)
        now_monotonic = time.monotonic()
        state["totals"]["runtimeSeconds"] = round(
            float(state["totals"].get("runtimeSeconds", 0)) + now_monotonic - last_accounted,
            3,
        )
        last_accounted = now_monotonic
        state["lastCheckpoint"] = {
            "revision": int(state.get("stateRevision", 0)) + 1,
            "at": _now(),
            "lastUrl": state["lastUrl"],
        }
        etag = _save_state(store, state, etag)
        if results[-1].get("result") in {"robots-cached", "politeness-wait", "deferred"}:
            break
    if state.get("status") != "running" or not results:
        now_monotonic = time.monotonic()
        state["totals"]["runtimeSeconds"] = round(
            float(state["totals"].get("runtimeSeconds", 0)) + now_monotonic - last_accounted,
            3,
        )
        etag = _save_state(store, state, etag)
    return results, etag


def _new_snapshot_state(previous: dict[str, Any]) -> dict[str, Any]:
    state = _default_state()
    state["config"] = previous.get("config", _default_config())
    state["sources"] = previous.get("sources", [])
    state["trainingQueue"] = previous.get("trainingQueue", [])[-MAX_TRAINING_QUEUE:]
    state["snapshots"] = previous.get("snapshots", [])[-100:]
    state["urlRevisions"] = dict(previous.get("urlRevisions", {}))
    previous_totals = previous.get("totals", {})
    state["totals"]["trainingPending"] = int(previous_totals.get("trainingPending", 0))
    state["totals"]["trainingAccepted"] = int(previous_totals.get("trainingAccepted", 0))
    state["totals"]["trainingRejected"] = int(previous_totals.get("trainingRejected", 0))
    state["snapshotId"] = f"web-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    state["status"] = "running"
    state["reason"] = "Collection started from the durable source registry."
    state["startedAt"] = _now()
    state["sessionStartedAt"] = state["startedAt"]
    state["sessionStartedEpoch"] = time.time()
    state["runCounter"] = int(previous.get("runCounter", 0)) + 1
    for source in state["sources"]:
        if not source.get("enabled", True):
            continue
        state["frontier"].append({
            "url": source["url"],
            "depth": 0,
            "sourceId": source["id"],
            "referrer": None,
            "priority": int(source.get("priority", 80)),
            "exploration": False,
            "discoveredAt": _now(),
        })
    _event(state, "started", f"Started snapshot {state['snapshotId']}", sources=len(state["frontier"]))
    return state


def _index_documents(state: dict[str, Any]) -> dict[str, Any]:
    documents = [
        {
            "url": value.get("url"),
            "finalUrl": value.get("finalUrl"),
            "title": value.get("title"),
            "contentSha256": value.get("contentSha256"),
            "documentPath": value.get("documentPath"),
            "quality": value.get("quality", {}).get("score"),
            "capturedAt": value.get("capturedAt"),
            "sourceDomain": value.get("sourceDomain"),
            "termFreq": value.get("termFreq", {}),
            "wordCount": value.get("wordCount", 0),
            "excerpt": value.get("excerpt", ""),
        }
        for value in state.get("completed", {}).values()
        if value.get("status") == "accepted"
    ]
    return {"schemaVersion": 1, "kind": "lexical-bm25-preparation", "snapshotId": state["snapshotId"], "documents": documents}


def _seal_payloads(
    state: dict[str, Any], context: Any, sealed_at: str, manifest_totals: dict[str, Any]
) -> tuple[dict[str, Any], str, dict[str, Any], str]:
    prefix = _snapshot_prefix(str(state["snapshotId"]))
    index = _index_documents(state)
    index_hash = _sha_bytes(_compact_json(index))
    index_path = f"{prefix}/indexes/{index_hash}.json"
    candidates = [item for item in state.get("trainingQueue", []) if item.get("snapshotId") == state["snapshotId"]]
    manifest = {
        "schemaVersion": 1,
        "snapshotId": state["snapshotId"],
        "status": "sealed",
        "createdAt": state["startedAt"],
        "sealedAt": sealed_at,
        "collector": {
            "moduleId": MODULE_ID,
            "moduleVersion": context.module_version,
            "moduleSha256": context.module_sha256,
            "sourceBranch": context.source_branch,
            "sourcePath": context.source_path,
        },
        "sources": state["sources"],
        "config": state["config"],
        "totals": manifest_totals,
        "acceptedDocuments": len(index["documents"]),
        "rejectedDocuments": len(state.get("rejected", [])),
        "frontierRemaining": len(state.get("frontier", [])),
        "index": {"kind": index["kind"], "sha256": index_hash, "path": index_path},
        "trainingReview": {
            "separateFromFrozenSnapshot": True,
            "pendingCandidates": len([item for item in candidates if item.get("status") == "pending"]),
            "promotionRequiresExplicitReview": True,
        },
        "immutability": "manifest and content-addressed artifacts are write-once; future collection creates a new snapshot",
    }
    manifest_hash = _sha_bytes(_compact_json(manifest))
    manifest["manifestSha256"] = manifest_hash
    return index, index_path, manifest, manifest_hash


def _seal(store: BlobStore, state: dict[str, Any], context: Any) -> dict[str, Any]:
    if state.get("status") not in {"paused", "ready-to-seal"}:
        raise CollectorError(409, "SEAL_STATE_INVALID", "Pause the running collector before sealing.")
    if int(state["totals"].get("documents", 0)) < 1:
        raise CollectorError(409, "SEAL_EMPTY", "At least one accepted document is required before sealing.")
    sealed_at = str(state.get("sealIntentAt") or _now())
    manifest_totals = dict(state.get("sealTotals") or state["totals"])
    index, index_path, manifest, manifest_hash = _seal_payloads(state, context, sealed_at, manifest_totals)
    prefix = _snapshot_prefix(str(state["snapshotId"]))
    manifest_path = f"{prefix}/manifest.json"
    store.put_json(index_path, index, immutable=True, tolerate_existing=True)
    store.put_json(manifest_path, manifest, immutable=True, tolerate_existing=True)
    state["totals"]["storedBytes"] = (
        int(manifest_totals.get("storedBytes", 0))
        + len(_compact_json(index))
        + len(_compact_json(manifest))
    )
    state["status"] = "sealed"
    state["sealedAt"] = sealed_at
    state["reason"] = "Snapshot sealed immutably. Start creates a new snapshot."
    if not any(item.get("snapshotId") == state["snapshotId"] for item in state.setdefault("snapshots", [])):
        state["snapshots"].append({
            "snapshotId": state["snapshotId"],
            "sealedAt": state["sealedAt"],
            "manifestPath": manifest_path,
            "manifestSha256": manifest_hash,
            "documents": len(index["documents"]),
        })
    state["snapshots"] = state["snapshots"][-100:]
    _event(state, "sealed", f"Sealed snapshot {state['snapshotId']}", manifestSha256=manifest_hash)
    context.activity("sealed", snapshotId=state["snapshotId"], documents=len(index["documents"]), manifestSha256=manifest_hash)
    return manifest


def _search_index(index: dict[str, Any], query: str, limit: int) -> list[dict[str, Any]]:
    query_terms = _tokenize(query)[:12]
    documents = [doc for doc in index.get("documents", []) if isinstance(doc, dict)]
    if not query_terms or not documents:
        return []
    average_length = sum(max(1, int(doc.get("wordCount", 0))) for doc in documents) / len(documents)
    document_frequency = {term: sum(1 for doc in documents if term in doc.get("termFreq", {})) for term in query_terms}
    scored: list[tuple[float, dict[str, Any]]] = []
    for doc in documents:
        frequency = doc.get("termFreq", {})
        length = max(1, int(doc.get("wordCount", 0)))
        score = 0.0
        for term in query_terms:
            tf = int(frequency.get(term, 0))
            if not tf:
                continue
            df = document_frequency[term]
            inverse = math.log(1 + (len(documents) - df + 0.5) / (df + 0.5))
            score += inverse * (tf * 2.2) / (tf + 1.2 * (0.25 + 0.75 * length / max(1.0, average_length)))
        title = str(doc.get("title", "")).lower()
        if any(term in title for term in query_terms):
            score += 0.8
        if score > 0:
            scored.append((score, doc))
    return [
        {
            "score": round(score, 4),
            "title": doc.get("title"),
            "url": doc.get("url"),
            "contentSha256": doc.get("contentSha256"),
            "documentPath": doc.get("documentPath"),
            "quality": doc.get("quality"),
            "capturedAt": doc.get("capturedAt"),
            "sourceDomain": doc.get("sourceDomain"),
            "excerpt": doc.get("excerpt", ""),
        }
        for score, doc in sorted(scored, key=lambda pair: pair[0], reverse=True)[:limit]
    ]


def _clean_domain_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or len(value) > 100:
        raise CollectorError(400, "CONFIG_INVALID", f"{field} must be a list of at most 100 domains.")
    return sorted(set(_normalize_domain(str(item)) for item in value if str(item).strip()))


def _apply_config(state: dict[str, Any], patch: Any) -> dict[str, Any]:
    if not isinstance(patch, dict):
        raise CollectorError(400, "CONFIG_INVALID", "config must be a JSON object.")
    integer_ranges = {
        "storageBudgetBytes": (5 * 1024 * 1024, 5 * 1024 * 1024 * 1024),
        "runBudgetSeconds": (30, 10_800),
        "requestBudgetSeconds": (5, 45),
        "maxPagesPerRun": (1, 10_000),
        "maxDocuments": (1, 10_000),
        "maxDepth": (0, 8),
        "maxLinksPerPage": (0, 200),
        "maxDocumentsPerDomain": (1, 5_000),
        "maxBytesPerDomain": (256_000, 2 * 1024 * 1024 * 1024),
        "maxDomains": (1, 100),
        "maxDocumentBytes": (32_000, 10_000_000),
        "batchSize": (1, 5),
        "minTextCharacters": (80, 20_000),
        "chunkWords": (100, 2_000),
        "chunkOverlapWords": (0, 500),
        "explorationPercent": (0, 50),
    }
    float_ranges = {"minQuality": (0.0, 1.0), "trainingMinQuality": (0.0, 1.0), "minDelaySeconds": (0.25, 60.0)}
    updated = dict(state["config"])
    for key, raw in patch.items():
        if key in integer_ranges:
            if isinstance(raw, bool):
                raise CollectorError(400, "CONFIG_INVALID", f"{key} must be an integer.")
            try:
                value = int(raw)
            except Exception as exc:
                raise CollectorError(400, "CONFIG_INVALID", f"{key} must be an integer.") from exc
            low, high = integer_ranges[key]
            if not low <= value <= high:
                raise CollectorError(400, "CONFIG_RANGE", f"{key} must be between {low} and {high}.")
            updated[key] = value
        elif key in float_ranges:
            try:
                value = float(raw)
            except Exception as exc:
                raise CollectorError(400, "CONFIG_INVALID", f"{key} must be numeric.") from exc
            low, high = float_ranges[key]
            if not low <= value <= high:
                raise CollectorError(400, "CONFIG_RANGE", f"{key} must be between {low} and {high}.")
            updated[key] = value
        elif key in {"respectRobots", "allowExternalDomains"}:
            if not isinstance(raw, bool):
                raise CollectorError(400, "CONFIG_INVALID", f"{key} must be true or false.")
            updated[key] = raw
        elif key in {"preferredDomains", "blockedDomains"}:
            updated[key] = _clean_domain_list(raw, key)
        elif key == "allowedMimeTypes":
            if not isinstance(raw, list) or not raw:
                raise CollectorError(400, "CONFIG_INVALID", "allowedMimeTypes must be a non-empty list.")
            values = sorted(set(str(item).lower().strip() for item in raw))
            if any(value not in ALLOWED_MIMES for value in values):
                raise CollectorError(400, "MIME_CONFIG_REJECTED", "Only the fixed safe text MIME set may be enabled.")
            updated[key] = values
        else:
            raise CollectorError(400, "CONFIG_FIELD_UNKNOWN", f"Unknown config field: {key}")
    if updated["chunkOverlapWords"] >= updated["chunkWords"]:
        raise CollectorError(400, "CONFIG_RANGE", "chunkOverlapWords must be smaller than chunkWords.")
    if updated["trainingMinQuality"] < updated["minQuality"]:
        raise CollectorError(400, "CONFIG_RANGE", "trainingMinQuality cannot be below minQuality.")
    state["config"] = updated
    _event(state, "configured", "Collector budgets and policies updated.", fields=sorted(patch))
    return updated


def _public_state(state: dict[str, Any], store: BlobStore, context: Any) -> dict[str, Any]:
    completed = list(state.get("completed", {}).values())[-100:]
    safe_completed = [{key: value for key, value in item.items() if key not in {"termFreq"}} for item in completed]
    wait_ms = 0
    if state.get("status") == "running" and state.get("frontier"):
        waits = []
        for item in state["frontier"]:
            host = urllib.parse.urlsplit(str(item.get("url", ""))).hostname or ""
            waits.append(max(0.0, float(_domain_state(state, host).get("nextAllowedAt", 0)) - time.time()))
        wait_ms = int(min(waits or [0]) * 1000)
    return {
        "ok": True,
        "module": {"id": MODULE_ID, "version": context.module_version, "sha256": context.module_sha256, "apiSchemaVersion": API_SCHEMA_VERSION},
        "storage": store.describe(),
        "state": {
            **{
                key: value
                for key, value in state.items()
                if key not in {"completed", "contentHashes", "urlRevisions", "robots", "frontier", "trainingQueue", "rejected", "events"}
            },
            "completed": safe_completed,
            "completedCount": len(state.get("completed", {})),
            "frontier": state.get("frontier", [])[:200],
            "frontierCount": len(state.get("frontier", [])),
            "trainingQueue": state.get("trainingQueue", [])[-200:],
            "trainingQueueCount": len(state.get("trainingQueue", [])),
            "rejected": state.get("rejected", [])[-200:],
            "events": state.get("events", [])[-120:],
            "robotsDomains": len(state.get("robots", {})),
            "nextStepAfterMs": wait_ms,
            "pressure": _pressure(state),
        },
        "runtime": {"branch": context.source_branch, "path": context.source_path, "hotUpdatable": True, "deploymentRequiredForCompatibleChanges": False},
    }


async def _read_action_body(request: Any) -> dict[str, Any]:
    raw = await request.body()
    if len(raw) > MAX_BODY_BYTES:
        raise CollectorError(413, "ACTION_BODY_TOO_LARGE", "Action body exceeds the collector limit.")
    try:
        body = json.loads(raw.decode("utf-8")) if raw else {}
    except Exception as exc:
        raise CollectorError(400, "ACTION_JSON_INVALID", "Action body must be valid JSON.") from exc
    if not isinstance(body, dict):
        raise CollectorError(400, "ACTION_SHAPE_INVALID", "Action body must be a JSON object.")
    return body


async def _action(request: Any, store: BlobStore, state: dict[str, Any], etag: str | None, context: Any) -> dict[str, Any]:
    store.require()
    body = await _read_action_body(request)
    action = str(body.get("action", "")).strip().lower()
    saved = False
    result: dict[str, Any] = {}
    if state.get("sealIntentAt") and state.get("status") != "sealed" and action not in {"seal", "storage-check"}:
        raise CollectorError(409, "SEAL_IN_PROGRESS", "A durable seal is in progress; retry Seal before any other mutation.")
    if action == "configure":
        if state.get("status") == "running":
            raise CollectorError(409, "CONFIG_WHILE_RUNNING", "Pause before changing collection policy.")
        result = {"config": _apply_config(state, body.get("config"))}
    elif action == "add-source":
        if state.get("status") == "running":
            raise CollectorError(409, "SOURCE_WHILE_RUNNING", "Pause before changing the source registry.")
        url, _addresses = _validate_public_url(str(body.get("url", "")), state["config"])
        priority = int(body.get("priority", 80))
        if not 1 <= priority <= 100:
            raise CollectorError(400, "SOURCE_PRIORITY", "Source priority must be from 1 to 100.")
        policy = str(body.get("policy", "balanced")).strip().lower()
        if policy not in {"shallow", "balanced", "deep"}:
            raise CollectorError(400, "SOURCE_POLICY", "Source policy must be shallow, balanced, or deep.")
        existing = next((item for item in state["sources"] if item.get("url") == url), None)
        source = existing or {"id": f"source-{_sha_text(url)[:14]}", "createdAt": _now(), "stats": {"snapshots": 0}}
        source.update({
            "url": url,
            "host": urllib.parse.urlsplit(url).hostname,
            "label": str(body.get("label") or urllib.parse.urlsplit(url).hostname or "Source")[:120],
            "priority": priority,
            "policy": policy,
            "licenseNote": str(body.get("licenseNote", ""))[:500],
            "enabled": bool(body.get("enabled", True)),
            "updatedAt": _now(),
        })
        if existing is None:
            state["sources"].append(source)
        _event(state, "source-added" if existing is None else "source-updated", f"Registered {url}", priority=priority)
        result = {"source": source}
    elif action == "remove-source":
        if state.get("status") == "running":
            raise CollectorError(409, "SOURCE_WHILE_RUNNING", "Pause before changing the source registry.")
        source_id = str(body.get("sourceId", ""))
        before = len(state["sources"])
        state["sources"] = [item for item in state["sources"] if item.get("id") != source_id]
        if len(state["sources"]) == before:
            raise CollectorError(404, "SOURCE_NOT_FOUND", "Source was not found.")
        _event(state, "source-removed", f"Removed source {source_id}")
        result = {"removed": source_id}
    elif action == "start":
        if state.get("status") == "running":
            raise CollectorError(409, "ALREADY_RUNNING", "Collector is already running.")
        if state.get("status") == "paused" and state.get("snapshotId"):
            raise CollectorError(409, "PAUSED_SNAPSHOT_EXISTS", "Continue or seal the paused snapshot before starting another.")
        if not any(source.get("enabled", True) for source in state.get("sources", [])):
            raise CollectorError(409, "NO_SOURCES", "Register at least one enabled source before starting.")
        state = _new_snapshot_state(state)
        etag = _save_state(store, state, etag)
        batch, etag = _process_batch(store, state, etag, context)
        saved = True
        result = {"batch": batch}
    elif action == "pause":
        if state.get("status") != "running":
            raise CollectorError(409, "PAUSE_STATE_INVALID", "Collector is not running.")
        state["status"] = "paused"
        state["pausedAt"] = _now()
        state["reason"] = str(body.get("reason") or "Paused by operator.")[:240]
        _event(state, "paused", state["reason"])
    elif action == "continue":
        if state.get("status") != "paused":
            raise CollectorError(409, "CONTINUE_STATE_INVALID", "Only a paused snapshot can continue.")
        state["status"] = "running"
        state["pausedAt"] = None
        state["sessionStartedAt"] = _now()
        state["sessionStartedEpoch"] = time.time()
        state["sessionPages"] = 0
        state["runCounter"] = int(state.get("runCounter", 0)) + 1
        state["reason"] = "Resumed from the durable frontier checkpoint."
        _event(state, "continued", state["reason"], runCounter=state["runCounter"])
    elif action == "step":
        batch, etag = _process_batch(store, state, etag, context)
        saved = True
        result = {"batch": batch}
    elif action == "seal":
        if not state.get("sealIntentAt"):
            if state.get("status") not in {"paused", "ready-to-seal"}:
                raise CollectorError(409, "SEAL_STATE_INVALID", "Pause the running collector before sealing.")
            if int(state["totals"].get("documents", 0)) < 1:
                raise CollectorError(409, "SEAL_EMPTY", "At least one accepted document is required before sealing.")
            sealed_at = _now()
            manifest_totals = dict(state["totals"])
            planned_index, _index_path, planned_manifest, _manifest_hash = _seal_payloads(
                state, context, sealed_at, manifest_totals
            )
            planned_bytes = len(_compact_json(planned_index)) + len(_compact_json(planned_manifest))
            projected_bytes = (
                int(state["totals"].get("storedBytes", 0))
                + len(_compact_json(state))
                + planned_bytes
                + STATE_GROWTH_RESERVE_BYTES
            )
            safety_limit = int(int(state["config"]["storageBudgetBytes"]) * 0.95)
            if projected_bytes > safety_limit:
                raise CollectorError(
                    507,
                    "STORAGE_BUDGET_PREFLIGHT",
                    "Sealing would cross the 95% storage safety threshold; increase the storage budget before retrying.",
                    {"projectedBytes": projected_bytes, "safetyLimitBytes": safety_limit, "plannedArtifactBytes": planned_bytes},
                )
            state["sealIntentAt"] = sealed_at
            state["sealTotals"] = manifest_totals
            state["sealPlannedBytes"] = planned_bytes
            _event(state, "seal-intent", "Durable seal intent recorded before immutable writes.")
            etag = _save_state(store, state, etag)
        manifest = _seal(store, state, context)
        result = {"manifest": manifest}
    elif action == "review":
        candidate_id = str(body.get("candidateId", ""))
        decision = str(body.get("decision", "")).strip().lower()
        if decision not in {"accept", "reject"}:
            raise CollectorError(400, "REVIEW_DECISION", "Review decision must be accept or reject.")
        candidate = next((item for item in state.get("trainingQueue", []) if item.get("id") == candidate_id), None)
        if candidate is None:
            raise CollectorError(404, "CANDIDATE_NOT_FOUND", "Training candidate was not found.")
        if candidate.get("status") != "pending":
            raise CollectorError(409, "CANDIDATE_ALREADY_REVIEWED", "Training candidate already has a decision.")
        if decision == "accept" and body.get("confirmRights") is not True:
            raise CollectorError(400, "RIGHTS_CONFIRMATION_REQUIRED", "Accepting training material requires explicit rights/provenance confirmation.")
        review = {
            "schemaVersion": 1,
            "candidateId": candidate_id,
            "decision": decision,
            "reviewedAt": _now(),
            "reviewNote": str(body.get("note", ""))[:1_000],
            "rightsConfirmed": bool(body.get("confirmRights")),
            "snapshotId": candidate["snapshotId"],
            "documentSha256": candidate["documentSha256"],
            "sourceUrl": candidate["url"],
            "reviewSeparation": "Explicit review; frozen snapshot membership alone never authorizes training.",
        }
        if decision == "accept":
            document, _document_etag = store.get_json(candidate["documentPath"])
            if document is None:
                raise CollectorError(503, "CANDIDATE_DOCUMENT_MISSING", "Candidate document is missing from the frozen snapshot.")
            corpus = {
                **review,
                "title": document.get("title"),
                "text": document.get("text"),
                "chunks": document.get("chunks"),
                "quality": document.get("quality"),
                "provenance": document.get("provenance"),
            }
            _write_immutable(store, state, f"swrlz/collector/training/accepted/{candidate_id}.json", corpus)
            state["totals"]["trainingAccepted"] += 1
        else:
            _write_immutable(store, state, f"swrlz/collector/training/rejected/{candidate_id}.json", review)
            state["totals"]["trainingRejected"] += 1
        state["totals"]["trainingPending"] = max(0, int(state["totals"]["trainingPending"]) - 1)
        candidate["status"] = "accepted" if decision == "accept" else "rejected"
        candidate["reviewedAt"] = review["reviewedAt"]
        _event(state, "training-review", f"Training candidate {decision}ed.", candidateId=candidate_id)
        result = {"review": review}
    elif action == "storage-check":
        objects = store.list("swrlz/collector/", 1)
        return {**_public_state(state, store, context), "action": action, "result": {"storageCheck": "pass", "visibleObjects": len(objects)}}
    else:
        raise CollectorError(400, "ACTION_UNKNOWN", f"Unknown collector action: {action}")
    if not saved:
        _save_state(store, state, etag)
    response = _public_state(state, store, context)
    response["action"] = action
    response["result"] = result
    return response


async def handle(request: Any, path: str, context: Any) -> JSONResponse:
    store = BlobStore()
    try:
        state, etag = _load_state(store)
        normalized = (path or "status").strip("/").lower()
        if request.method == "GET" and normalized in {"", "status", "host/refresh"}:
            payload = _public_state(state, store, context)
            if normalized == "host/refresh":
                payload["hostRefresh"] = "requested"
            return JSONResponse(payload, headers={"Cache-Control": "no-store"})
        if request.method == "GET" and normalized == "snapshots":
            store.require()
            manifests = [item for item in store.list("swrlz/collector/snapshots/", 1_000) if str(item.get("pathname", "")).endswith("/manifest.json")]
            return JSONResponse({"ok": True, "snapshots": state.get("snapshots", []), "objects": manifests, "count": len(manifests)}, headers={"Cache-Control": "no-store"})
        if request.method == "GET" and normalized == "snapshot":
            store.require()
            snapshot_id = str(request.query_params.get("id", ""))
            if not re.fullmatch(r"web-[A-Za-z0-9-]{12,80}", snapshot_id):
                raise CollectorError(400, "SNAPSHOT_ID_INVALID", "A valid snapshot id is required.")
            manifest, _manifest_etag = store.get_json(f"{_snapshot_prefix(snapshot_id)}/manifest.json")
            if manifest is None:
                raise CollectorError(404, "SNAPSHOT_NOT_FOUND", "Snapshot manifest was not found.")
            return JSONResponse({"ok": True, "manifest": manifest}, headers={"Cache-Control": "no-store"})
        if request.method == "GET" and normalized == "document":
            store.require()
            snapshot_id = str(request.query_params.get("snapshotId", ""))
            digest = str(request.query_params.get("sha256", ""))
            if not re.fullmatch(r"web-[A-Za-z0-9-]{12,80}", snapshot_id) or not re.fullmatch(r"[a-f0-9]{64}", digest):
                raise CollectorError(400, "DOCUMENT_ID_INVALID", "Valid snapshotId and sha256 values are required.")
            document, _document_etag = store.get_json(f"{_snapshot_prefix(snapshot_id)}/documents/{digest}.json")
            if document is None:
                raise CollectorError(404, "DOCUMENT_NOT_FOUND", "Frozen document was not found.")
            return JSONResponse({"ok": True, "document": document}, headers={"Cache-Control": "no-store"})
        if request.method == "GET" and normalized == "search":
            store.require()
            query = str(request.query_params.get("q", "")).strip()
            if not 1 <= len(query) <= 200:
                raise CollectorError(400, "SEARCH_QUERY_INVALID", "Search query must contain 1 to 200 characters.")
            snapshot_id = str(request.query_params.get("snapshotId", state.get("snapshotId") or ""))
            if snapshot_id == state.get("snapshotId"):
                index = _index_documents(state)
            else:
                if not re.fullmatch(r"web-[A-Za-z0-9-]{12,80}", snapshot_id):
                    raise CollectorError(400, "SNAPSHOT_ID_INVALID", "A valid snapshot id is required.")
                manifest, _manifest_etag = store.get_json(f"{_snapshot_prefix(snapshot_id)}/manifest.json")
                if manifest is None:
                    raise CollectorError(404, "SNAPSHOT_NOT_FOUND", "Snapshot manifest was not found.")
                index, _index_etag = store.get_json(str(manifest.get("index", {}).get("path", "")))
                if index is None:
                    raise CollectorError(503, "SNAPSHOT_INDEX_MISSING", "Snapshot index is missing.")
            results = _search_index(index, query, 20)
            return JSONResponse({"ok": True, "query": query, "snapshotId": snapshot_id, "results": results, "count": len(results)}, headers={"Cache-Control": "no-store"})
        if request.method == "POST" and normalized == "action":
            payload = await _action(request, store, state, etag, context)
            return JSONResponse(payload, headers={"Cache-Control": "no-store"})
        raise CollectorError(404, "COLLECTOR_ROUTE_NOT_FOUND", "Collector route was not found.")
    except CollectorError as exc:
        return JSONResponse(
            status_code=exc.status,
            content={"ok": False, "error": {"code": exc.code, "message": exc.message, "detail": exc.detail}, "storage": store.describe()},
            headers={"Cache-Control": "no-store"},
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": {"code": "COLLECTOR_UNEXPECTED", "message": f"{type(exc).__name__}: {exc}"[:500]}, "storage": store.describe()},
            headers={"Cache-Control": "no-store"},
        )


def inspect_module() -> dict[str, Any]:
    store = BlobStore()
    return {
        "moduleId": MODULE_ID,
        "apiSchemaVersion": API_SCHEMA_VERSION,
        "stateSchemaVersion": STATE_SCHEMA_VERSION,
        "storage": store.describe(),
        "lifecycleActions": ["configure", "add-source", "remove-source", "start", "pause", "continue", "step", "seal", "review", "storage-check"],
        "search": {"kind": "lexical-bm25-preparation", "endpoint": "/api/collector/search"},
        "security": ["admin-authenticated-host", "public-IP-only", "IP-pinned-connect", "hostname-verified-TLS", "redirect-revalidation", "robots", "MIME-limit", "response-byte-limit", "domain-rate-limit"],
    }
