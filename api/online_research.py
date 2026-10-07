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
from typing import Any, Callable

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
_trace_local=threading.local()

def set_trace_sink(sink:Callable[[dict[str,Any]],None]|None)->None:
    _trace_local.sink=sink if callable(sink) else None

def clear_trace_sink()->None:
    _trace_local.sink=None

@dataclass
class Evidence:
    title:str;url:str;snippet:str;source:str;query:str;rank:int;fetched_at:int

def requested(profile_id:Any)->bool:return "+ONLINE" in str(profile_id or "").upper()
def _clean_query(value:Any)->str:return re.sub(r"\s+"," ",str(value or "")).strip()[:500]
def _provider()->str:
    return "bounded-web-search-chain-v1"

def _trace_public_url(url:Any)->tuple[str,str]:
    try:
        parsed=urllib.parse.urlsplit(str(url or ""))
        host=str(parsed.hostname or "").lower()[:240]
        if parsed.scheme not in {"http","https"} or not host:return host,""
        path=parsed.path or "/"
        safe=urllib.parse.urlunsplit((parsed.scheme,parsed.netloc,path,"",""))
        return host,safe[:1200]
    except Exception:
        return "",""

def _emit_trace(phase:str,reason:str="",provider:str="",url:Any="",status:Any=None,result_count:Any=None,response_bytes:Any=None,error_type:str="")->dict[str,Any]:
    host,safe_url=_trace_public_url(url)
    event={
        "contract":"swrlz-online-trace-event-v1",
        "atUnixMs":int(time.time()*1000),
        "phase":str(phase or "ONLINE_TRACE")[:80],
        "activity":str(reason or "")[:240],
        "provider":str(provider or "")[:120],
        "site":host,
        "url":safe_url,
    }
    if status is not None:event["httpStatus"]=status if isinstance(status,(str,int,float,bool)) else str(status)[:80]
    if result_count is not None:
        try:event["resultCount"]=int(result_count)
        except Exception:pass
    if response_bytes is not None:
        try:event["responseBytes"]=int(response_bytes)
        except Exception:pass
    if error_type:event["errorType"]=str(error_type)[:120]
    sink=getattr(_trace_local,"sink",None)
    if callable(sink):
        try:sink(dict(event))
        except Exception:pass
    print("SWRLZ_ONLINE_TRACE "+json.dumps(event,ensure_ascii=False,separators=(",",":")),flush=True)
    return event

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

def _search_html(url:str)->tuple[int,str,int]:
    safe=_validate_public_url(url)
    req=urllib.request.Request(safe,headers={"User-Agent":USER_AGENT,"Accept":"text/html,application/xhtml+xml;q=0.9,*/*;q=0.1","Accept-Language":"en-US,en;q=0.8"})
    with _opener().open(req,timeout=SEARCH_TIMEOUT_SECONDS) as response:
        raw=response.read(MAX_FETCH_BYTES+1)
        status=int(getattr(response,"status",200) or 200)
    if len(raw)>MAX_FETCH_BYTES:raise ValueError("SEARCH_RESPONSE_TOO_LARGE")
    return status,raw.decode("utf-8","replace"),len(raw)

def _clean_search_text(value:str,limit:int)->str:
    value=re.sub(r"(?is)<(script|style|svg)[^>]*>.*?</\1>"," ",str(value or ""))
    value=html.unescape(re.sub(r"<[^>]+>"," ",value))
    return re.sub(r"\s+"," ",value).strip()[:limit]

def _ddg_target(href:str)->str:
    value=html.unescape(str(href or ""))
    if value.startswith("//"):value="https:"+value
    parsed=urllib.parse.urlsplit(value)
    if parsed.netloc.endswith("duckduckgo.com"):
        target=urllib.parse.parse_qs(parsed.query).get("uddg",[""])[0]
        if target:value=urllib.parse.unquote(target)
    return value

def _evidence_result(query:str,href:str,title:str,snippet:str,rank:int)->dict[str,Any]|None:
    try:safe=_validate_public_url(_ddg_target(href))
    except ValueError:return None
    target=urllib.parse.urlsplit(safe)
    clean_title=_clean_search_text(title,300)
    if not clean_title:return None
    return asdict(Evidence(title=clean_title,url=safe,snippet=_clean_search_text(snippet,1200),source=target.netloc.lower(),query=query,rank=rank,fetched_at=int(time.time())))

def _parse_ddg_html(query:str,text:str)->tuple[list[dict[str,Any]],int]:
    anchors=list(re.finditer(r'<a[^>]+class=["\'][^"\']*\bresult__a\b[^"\']*["\'][^>]+href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',text,re.I))
    results=[]
    for index,anchor in enumerate(anchors):
        region_end=anchors[index+1].start() if index+1<len(anchors) else min(len(text),anchor.end()+5000)
        region=text[anchor.end():region_end]
        sm=re.search(r'class=["\'][^"\']*\bresult__snippet\b[^"\']*["\'][^>]*>([\s\S]*?)</(?:a|div)>',region,re.I)
        item=_evidence_result(query,anchor.group(1),anchor.group(2),sm.group(1) if sm else "",len(results)+1)
        if item:results.append(item)
        if len(results)>=MAX_RESULTS_PER_QUERY:break
    return results,len(anchors)

def _parse_ddg_lite(query:str,text:str)->tuple[list[dict[str,Any]],int]:
    anchors=list(re.finditer(r'<a[^>]+(?:class=["\'][^"\']*\bresult-link\b[^"\']*["\'][^>]*)?href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',text,re.I))
    results=[]
    accepted_anchors=0
    for index,anchor in enumerate(anchors):
        href=_ddg_target(anchor.group(1))
        parsed=urllib.parse.urlsplit(href)
        if not parsed.hostname or parsed.hostname.endswith("duckduckgo.com"):continue
        accepted_anchors+=1
        region_end=anchors[index+1].start() if index+1<len(anchors) else min(len(text),anchor.end()+2500)
        region=text[anchor.end():region_end]
        sm=re.search(r'class=["\'][^"\']*\bresult-snippet\b[^"\']*["\'][^>]*>([\s\S]*?)</(?:td|div|span)>',region,re.I)
        item=_evidence_result(query,href,anchor.group(2),sm.group(1) if sm else "",len(results)+1)
        if item:results.append(item)
        if len(results)>=MAX_RESULTS_PER_QUERY:break
    return results,accepted_anchors

def _parse_bing_html(query:str,text:str)->tuple[list[dict[str,Any]],int]:
    blocks=list(re.finditer(r'<li[^>]+class=["\'][^"\']*\bb_algo\b[^"\']*["\'][^>]*>([\s\S]*?)</li>',text,re.I))
    results=[]
    for block in blocks:
        body=block.group(1)
        am=re.search(r'<h2[^>]*>\s*<a[^>]+href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',body,re.I)
        if not am:continue
        sm=re.search(r'<p[^>]*>([\s\S]*?)</p>',body,re.I)
        item=_evidence_result(query,am.group(1),am.group(2),sm.group(1) if sm else "",len(results)+1)
        if item:results.append(item)
        if len(results)>=MAX_RESULTS_PER_QUERY:break
    return results,len(blocks)

def _provider_attempt(provider:str,url:str,parser,query:str)->list[dict[str,Any]]:
    _emit_trace("SEARCH_PROVIDER_VISIT",provider=provider,url=url,reason="Searching provider")
    try:
        status,text,response_bytes=_search_html(url)
        results,anchors=parser(query,text)
        print("SWRLZ_SEARCH_PROVIDER_CAMERA "+json.dumps({"contract":"swrlz-search-provider-camera-v2","provider":provider,"httpStatus":status,"responseBytes":response_bytes,"resultAnchors":anchors,"acceptedResults":len(results)},separators=(",",":")),flush=True)
        _emit_trace("SEARCH_PROVIDER_RESULTS" if results else "SEARCH_PROVIDER_EMPTY",provider=provider,url=url,status=status,result_count=len(results),reason=("Search results found" if results else "No usable results from provider"))
        return results
    except Exception as exc:
        print("SWRLZ_SEARCH_PROVIDER_CAMERA "+json.dumps({"contract":"swrlz-search-provider-camera-v2","provider":provider,"errorType":type(exc).__name__,"acceptedResults":0},separators=(",",":")),flush=True)
        _emit_trace("SEARCH_PROVIDER_ERROR",provider=provider,url=url,error_type=type(exc).__name__,reason="Provider failed")
        return []

def search_public(query:Any)->list[dict[str,Any]]:
    """Public bounded search capability for specialized adapters.

    Uses the same provider chain and URL safety boundary as research(); it only
    skips the generic research reasoner when a caller already owns the domain-
    specific evidence-selection logic.
    """
    clean=_clean_query(query)
    return _ddg_search(clean) if clean else []


def fetch_public(url:str)->dict[str,Any]:
    """Public bounded page fetch using the canonical SSRF-safe fetch boundary."""
    return _page_fetch(url)


def _ddg_search(query:str)->list[dict[str,Any]]:
    encoded=urllib.parse.urlencode({"q":query})
    attempts=[
        ("duckduckgo-html","https://html.duckduckgo.com/html/?"+encoded,_parse_ddg_html),
        ("duckduckgo-lite","https://lite.duckduckgo.com/lite/?"+encoded,_parse_ddg_lite),
        ("bing-html","https://www.bing.com/search?"+urllib.parse.urlencode({"q":query,"setlang":"en-us"}),_parse_bing_html),
    ]
    for provider,url,parser in attempts:
        results=_provider_attempt(provider,url,parser,query)
        if results:
            _emit_trace("SEARCH_PROVIDER_SELECTED",reason="Using "+provider,provider=provider,url=url,result_count=len(results))
            print("SWRLZ_SEARCH_PROVIDER_SELECTED "+json.dumps({"contract":"swrlz-search-provider-selected-v1","provider":provider,"resultCount":len(results)},separators=(",",":")),flush=True)
            return results
    return []

def _page_fetch(url:str)->dict[str,Any]:
    safe=_validate_public_url(url)
    _emit_trace("PAGE_FETCH_STARTED",provider="web-page",url=safe,reason="Visiting result page")
    try:
        req=urllib.request.Request(safe,headers={"User-Agent":USER_AGENT,"Accept":"text/html,text/plain;q=0.9,*/*;q=0.1"})
        with _opener().open(req,timeout=PAGE_TIMEOUT_SECONDS) as response:
            final=_validate_public_url(response.geturl());status=getattr(response,"status",200);ctype=str(response.headers.get("Content-Type","")).lower();raw=response.read(MAX_PAGE_BYTES+1)
        if len(raw)>MAX_PAGE_BYTES:raise ValueError("PAGE_RESPONSE_TOO_LARGE")
        if not ("text/" in ctype or "html" in ctype or "json" in ctype):raise ValueError("PAGE_CONTENT_TYPE_BLOCKED")
        text=raw.decode("utf-8","replace");tm=re.search(r"<title[^>]*>([\s\S]*?)</title>",text,re.I);title=html.unescape(re.sub(r"<[^>]+>"," ",tm.group(1))).strip()[:300] if tm else ""
        cleaned=re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>"," ",text)
        cleaned=re.sub(r"(?i)<br\s*/?>","\n",cleaned)
        cleaned=re.sub(r"(?i)</(?:p|div|li|h[1-6]|section|article|blockquote|tr)>","\n",cleaned)
        cleaned=html.unescape(re.sub(r"<[^>]+>"," ",cleaned))
        extract=re.sub(r"[ \t\r\f\v]+"," ",cleaned)
        extract=re.sub(r" *\n *","\n",extract)
        extract=re.sub(r"\n{3,}","\n\n",extract).strip()[:6000]
        _emit_trace("PAGE_FETCH_COMPLETE",provider="web-page",url=final,status=int(status),response_bytes=len(raw),reason="Page fetched")
        return {"finalUrl":final,"status":int(status),"title":title,"extract":extract,"fetchedAt":int(time.time()*1000)}
    except Exception as exc:
        _emit_trace("PAGE_FETCH_ERROR",provider="web-page",url=safe,error_type=type(exc).__name__,reason="Page fetch failed")
        raise

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
    requested_sink=payload.get("_eventSink") if isinstance(payload,dict) else None
    clean_payload=dict(payload or {})
    clean_payload.pop("_eventSink",None)
    previous_sink=getattr(_trace_local,"sink",None)
    sink=requested_sink if callable(requested_sink) else previous_sink
    _trace_local.sink=sink if callable(sink) else None
    _emit_trace("RESEARCH_STARTED",reason="Online research started",provider=_provider())
    try:
        module=_load_hot()
        if module:
            try:
                bundle=module.research(clean_payload,{"search":_ddg_search,"fetch":_page_fetch,"provider":_provider()})
                encoded=json.dumps(bundle,ensure_ascii=False,separators=(",",":"))
                if len(encoded)>MAX_EVIDENCE_CHARS:
                    while bundle.get("evidence") and len(json.dumps(bundle,ensure_ascii=False,separators=(",",":")))>MAX_EVIDENCE_CHARS:bundle["evidence"].pop()
                    bundle["resultCount"]=len(bundle.get("evidence",[]));bundle["truncated"]=True
                _emit_trace("RESEARCH_COMPLETE",reason="Online research complete",provider=str(bundle.get("provider") or _provider()),result_count=len(bundle.get("evidence") or []))
                return bundle
            except Exception as exc:
                _emit_trace("RESEARCH_REASONER_ERROR",reason="Online research reasoner failed",provider=_provider(),status="ERROR",error_type=type(exc).__name__)
                print("SWRLZ_RESEARCH_HOT_FAILURE "+json.dumps({"at":int(time.time()*1000),"requestId":str(clean_payload.get("requestId") or "")[:200],"error":type(exc).__name__},separators=(",",":")),flush=True)
        bundle=_legacy_research(clean_payload)
        _emit_trace("RESEARCH_COMPLETE",reason="Online research complete",provider=str(bundle.get("provider") or _provider()),result_count=len(bundle.get("evidence") or []))
        return bundle
    finally:
        _trace_local.sink=previous_sink
