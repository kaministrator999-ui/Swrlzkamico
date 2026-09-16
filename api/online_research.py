from __future__ import annotations

import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from typing import Any

MAX_QUERIES = 6
MAX_RESULTS_PER_QUERY = 8
MAX_EVIDENCE_CHARS = 28000
MAX_FETCH_BYTES = 1_000_000
SEARCH_TIMEOUT_SECONDS = 12.0
USER_AGENT = "SWRLZ-Research/1.0 (+evidence-broker)"


@dataclass
class Evidence:
    title: str
    url: str
    snippet: str
    source: str
    query: str
    rank: int
    fetched_at: int


def requested(profile_id: Any) -> bool:
    return "+ONLINE" in str(profile_id or "").upper()


def _clean_query(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:500]


def _query_plan(payload: dict[str, Any]) -> list[str]:
    prompt = _clean_query(payload.get("prompt"))
    if not prompt:
        return []
    # The broker does not interpret user intent. The Brain may provide explicit
    # researchQueries; otherwise the exact user request is the conservative seed.
    raw = payload.get("researchQueries")
    queries: list[str] = []
    if isinstance(raw, list):
        for item in raw:
            q = _clean_query(item)
            if q and q not in queries:
                queries.append(q)
            if len(queries) >= MAX_QUERIES:
                break
    if not queries:
        queries = [prompt]
    return queries


def _provider() -> str:
    configured = os.environ.get("SWRLZ_SEARCH_PROVIDER", "duckduckgo-html").strip().lower()
    return configured if configured in {"duckduckgo-html"} else "duckduckgo-html"


def _ddg_search(query: str) -> list[Evidence]:
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=SEARCH_TIMEOUT_SECONDS) as response:
        raw = response.read(MAX_FETCH_BYTES + 1)
    if len(raw) > MAX_FETCH_BYTES:
        raise ValueError("SEARCH_RESPONSE_TOO_LARGE")
    text = raw.decode("utf-8", "replace")
    blocks = re.findall(r'<div[^>]+class="result[^\"]*"[\s\S]*?</div>\s*</div>', text, re.I)
    results: list[Evidence] = []
    for block in blocks:
        anchor = re.search(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', block, re.I)
        if not anchor:
            continue
        href = html.unescape(anchor.group(1))
        parsed = urllib.parse.urlsplit(href)
        if parsed.netloc.endswith("duckduckgo.com"):
            target = urllib.parse.parse_qs(parsed.query).get("uddg", [""])[0]
            if target:
                href = urllib.parse.unquote(target)
        target = urllib.parse.urlsplit(href)
        if target.scheme not in {"http", "https"} or not target.netloc:
            continue
        title = re.sub(r"<[^>]+>", " ", anchor.group(2))
        title = html.unescape(re.sub(r"\s+", " ", title)).strip()
        sm = re.search(r'class="result__snippet"[^>]*>([\s\S]*?)</(?:a|div)>', block, re.I)
        snippet = re.sub(r"<[^>]+>", " ", sm.group(1)) if sm else ""
        snippet = html.unescape(re.sub(r"\s+", " ", snippet)).strip()[:1200]
        results.append(Evidence(title=title[:300], url=href[:2000], snippet=snippet, source=target.netloc.lower(), query=query, rank=len(results)+1, fetched_at=int(time.time())))
        if len(results) >= MAX_RESULTS_PER_QUERY:
            break
    return results


def research(payload: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    queries = _query_plan(payload)
    provider = _provider()
    evidence: list[Evidence] = []
    errors: list[dict[str, str]] = []
    seen: set[str] = set()
    for query in queries:
        try:
            found = _ddg_search(query)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as exc:
            errors.append({"query": query, "error": f"{type(exc).__name__}:{str(exc)[:160]}"})
            continue
        for item in found:
            canonical = item.url.split("#", 1)[0]
            if canonical in seen:
                continue
            seen.add(canonical)
            evidence.append(item)
    bundle = {
        "contractId": "swrlz_online_evidence_v1",
        "requested": True,
        "provider": provider,
        "queries": queries,
        "resultCount": len(evidence),
        "evidence": [asdict(x) for x in evidence],
        "errors": errors,
        "elapsedMs": round((time.perf_counter() - started) * 1000),
        "epistemicPolicy": "retrieval-is-evidence-not-truth",
    }
    encoded = json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
    if len(encoded) > MAX_EVIDENCE_CHARS:
        while bundle["evidence"] and len(json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))) > MAX_EVIDENCE_CHARS:
            bundle["evidence"].pop()
        bundle["resultCount"] = len(bundle["evidence"])
        bundle["truncated"] = True
    return bundle
