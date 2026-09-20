from __future__ import annotations

import html
import importlib.util
import ipaddress
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from types import ModuleType
from typing import Any

MAX_QUERIES=6
MAX_RESULTS_PER_QUERY=8
MAX_EVIDENCE_CHARS=28000
MAX_FETCH_BYTES=1_000_000
MAX_PAGE_BYTES=700_000
SEARCH_TIMEOUT_SECONDS=12.0
PAGE_TIMEOUT_SECONDS=10.0
USER_AGENT="SWRLZ-Research/2.0 (+hot-reasoner; stable-network-boundary)"
HOT_REASONER_URL="https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/runtime/runtime_hot/online_research_reasoner_v1.py"
HOT_REASONER_PATH=Path("/tmp/swrlz-admin/runtime/hot/research/online_research_reasoner.py")
PREPARED_REASONER_PATH=Path(__file__).resolve().parents[1]/"swrzl_prepared_runtime"/"research"/"online_research_reasoner.py"
HOT_REFRESH_SECONDS=15.0
_hot_lock=threading.RLock();_hot_module:ModuleType|None=None;_hot_sig:tuple[int,int]|None=None;_last_hot_refresh=0.0

@dataclass
class Evidence:
    title:str;url:str;snippet:str;source:str;query:str;rank:int;fetched_at:int

def requested(profile_id:Any)->bool:return "+ONLINE" in str(profile_id or "").upper()
def _clean_query(value:Any)->str:return re.sub(r"\s+"," ",str(value or "")).strip()[:500]
def _provider()->str:
    configured=os.environ.get("SWRLZ_SEARCH_PROVIDER","duckduckgo-html").strip().lower()
    return configured if configured in {"duckduckgo-html"} else "duckduckgo-html"

def _safe_public_host(hostname:str)->None:
    if not hostname:raise ValueError("URL_HOST_REQUIRED")
    try:infos=socket.getaddrinfo(hostname,None,type=socket.SOCK_STREAM)
    except socket.gaierror as exc:raise ValueError("URL_DNS_FAILED") from exc
    for info in infos:
        ip=ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:raise ValueError("URL_PRIVATE_ADDRESS_BLOCKED")

def _validate_public_url(url:str)->str:
    parsed=urllib.parse.urlsplit(str(url or ""))
    if parsed.scheme not in {"http","https"} or not parsed.hostname:raise ValueError("URL_PROTOCOL_BLOCKED")
    if parsed.username or parsed.password:raise ValueError("URL_CREDENTIALS_BLOCKED")
    if parsed.port not in {None,80,443}:raise ValueError("URL_PORT_BLOCKED")
    _safe_public_host(parsed.hostname)
    return urllib.parse.urlunsplit((parsed.scheme,parsed.netloc,parsed.path,parsed.query,""))[:2000]

class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        safe=_validate_public_url(urllib.parse.urljoin(req.full_url,newurl))
        return super().redirect_request(req,fp,code,msg,headers,safe)

def _opener():return urllib.request.build_opener(_SafeRedirect())

def _ddg_search(query:str)->list[dict[str,Any]]:
    url="https://html.duckduckgo.com/html/?"+urllib.parse.urlencode({"q":query})
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"text/html"})
    with _opener().open(req,timeout=SEARCH_TIMEOUT_SECONDS) as response:
        raw=response.read(MAX_FETCH_BYTES+1)
        status=int(getattr(response,"status",200) or 200)
    if len(raw)>MAX_FETCH_BYTES:raise ValueError("SEARCH_RESPONSE_TOO_LARGE")
    text=raw.decode("utf-8","replace")
    # DDG changes wrapper nesting independently of the stable result__a/result__snippet
    # classes. Parse each result anchor and bound its local result region instead of
    # requiring one exact nested </div></div> shape.
    anchors=list(re.finditer(r'<a[^>]+class=["\'][^"\']*\bresult__a\b[^"\']*["\'][^>]+href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',text,re.I))
    results=[]
    for index,anchor in enumerate(anchors):
        href=html.unescape(anchor.group(1));parsed=urllib.parse.urlsplit(href)
        if parsed.netloc.endswith("duckduckgo.com"):
            target=urllib.parse.parse_qs(parsed.query).get("uddg",[""])[0]
            if target:href=urllib.parse.unquote(target)
        try:href=_validate_public_url(href)
        except ValueError:continue
        target=urllib.parse.urlsplit(href)
        title=html.unescape(re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",anchor.group(2)))).strip()
        region_end=anchors[index+1].start() if index+1<len(anchors) else min(len(text),anchor.end()+5000)
        region=text[anchor.end():region_end]
        sm=re.search(r'class=["\'][^"\']*\bresult__snippet\b[^"\']*["\'][^>]*>([\s\S]*?)</(?:a|div)>',region,re.I)
        snippet=re.sub(r"<[^>]+>"," ",sm.group(1)) if sm else ""
        snippet=html.unescape(re.sub(r"\\s+"," ",snippet)).strip()[:1200]
        results.append(asdict(Evidence(title=title[:300],url=href,snippet=snippet,source=target.netloc.lower(),query=query,rank=len(results)+1,fetched_at=int(time.time()))))
        if len(results)>=MAX_RESULTS_PER_QUERY:break
    print("SWRLZ_SEARCH_PROVIDER_CAMERA "+json.dumps({"contract":"swrlz-search-provider-camera-v1","provider":"duckduckgo-html","httpStatus":status,"responseBytes":len(raw),"resultAnchors":len(anchors),"acceptedResults":len(results)},separators=(",",":")),flush=True)
    return results

def _page_fetch(url:str)->dict[str,Any]:
    safe=_validate_public_url(url);req=urllib.request.Request(safe,headers={"User-Agent":USER_AGENT,"Accept":"text/html,text/plain;q=0.9,*/*;q=0.1"})
    with _opener().open(req,timeout=PAGE_TIMEOUT_SECONDS) as response:
        final=_validate_public_url(response.geturl());status=getattr(response,"status",200);ctype=str(response.headers.get("Content-Type","")).lower();raw=response.read(MAX_PAGE_BYTES+1)
    if len(raw)>MAX_PAGE_BYTES:raise ValueError("PAGE_RESPONSE_TOO_LARGE")
    if not ("text/" in ctype or "html" in ctype or "json" in ctype):raise ValueError("PAGE_CONTENT_TYPE_BLOCKED")
    text=raw.decode("utf-8","replace");tm=re.search(r"<title[^>]*>([\s\S]*?)</title>",text,re.I);title=html.unescape(re.sub(r"<[^>]+>"," ",tm.group(1))).strip()[:300] if tm else ""
    cleaned=re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>"," ",text);cleaned=html.unescape(re.sub(r"<[^>]+>"," ",cleaned));extract=re.sub(r"\s+"," ",cleaned).strip()[:6000]
    return {"finalUrl":final,"status":int(status),"title":title,"extract":extract,"fetchedAt":int(time.time()*1000)}

def _refresh_hot(force:bool=False)->None:
    # Runtime reasoner activation is explicit. Audience research requests must
    # never discover/fetch the mutable runtime branch.
    return

def _reasoner_path()->Path|None:
    if HOT_REASONER_PATH.is_file(): return HOT_REASONER_PATH
    if PREPARED_REASONER_PATH.is_file(): return PREPARED_REASONER_PATH
    return None

def _load_hot()->ModuleType|None:
    global _hot_module,_hot_sig
    path=_reasoner_path()
    if path is None:return None
    st=path.stat();sig=(st.st_mtime_ns,st.st_size)
    with _hot_lock:
        if _hot_module is not None and _hot_sig==sig:return _hot_module
        spec=importlib.util.spec_from_file_location("swrlz_hot_online_research",path)
        if spec is None or spec.loader is None:return None
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        if not callable(getattr(module,"research",None)):raise RuntimeError("HOT_RESEARCH_CONTRACT_MISSING")
        _hot_module=module;_hot_sig=sig;return module

def inspect_research()->dict[str,Any]:
    module=_load_hot();base={"available":True,"stableNetworkBoundary":True,"hotReasonerAvailable":bool(module),"hotRefreshSeconds":0,"requestPathSync":False,"networkPolicy":"public-http-s-80-443-no-credentials-private-address-block"}
    if module and callable(getattr(module,"inspect_research",None)):
        try:base["hotReasoner"]=module.inspect_research()
        except Exception:pass
    return base

def _legacy_research(payload:dict[str,Any])->dict[str,Any]:
    prompt=_clean_query(payload.get("prompt"));raw=payload.get("researchQueries");queries=[]
    if isinstance(raw,list):
        for item in raw:
            q=_clean_query(item)
            if q and q not in queries:queries.append(q)
            if len(queries)>=MAX_QUERIES:break
    if not queries and prompt:queries=[prompt]
    evidence=[];errors=[];seen=set();started=time.perf_counter()
    for query in queries:
        try:found=_ddg_search(query)
        except Exception as exc:errors.append({"query":query,"error":f"{type(exc).__name__}:{str(exc)[:160]}"});continue
        for item in found:
            if item["url"] in seen:continue
            seen.add(item["url"]);evidence.append(item)
    return {"contractId":"swrlz_online_evidence_v1","requested":True,"provider":_provider(),"queries":queries,"resultCount":len(evidence),"evidence":evidence,"errors":errors,"elapsedMs":round((time.perf_counter()-started)*1000),"epistemicPolicy":"retrieval-is-evidence-not-truth","hotReasonerFallback":True}

def research(payload:dict[str,Any])->dict[str,Any]:
    module=_load_hot()
    if module:
        try:
            bundle=module.research(payload,{"search":_ddg_search,"fetch":_page_fetch,"provider":_provider()})
            encoded=json.dumps(bundle,ensure_ascii=False,separators=(",",":"))
            if len(encoded)>MAX_EVIDENCE_CHARS:
                while bundle.get("evidence") and len(json.dumps(bundle,ensure_ascii=False,separators=(",",":")))>MAX_EVIDENCE_CHARS:bundle["evidence"].pop()
                bundle["resultCount"]=len(bundle.get("evidence",[]));bundle["truncated"]=True
            return bundle
        except Exception as exc:
            print("SWRLZ_RESEARCH_HOT_FAILURE "+json.dumps({"at":int(time.time()*1000),"requestId":str(payload.get("requestId") or "")[:200],"error":type(exc).__name__},separators=(",",":")),flush=True)
    return _legacy_research(payload)
