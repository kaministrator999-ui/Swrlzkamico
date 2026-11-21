"""Generic fallback for public factual research when the primary search is empty.

Uses the existing safe bounded HTTP page fetcher to discover Wikipedia article
titles and fetch real summaries. No hardcoded question answers, no public search
of private conversation history, and no assertion that retrieved facts are
semantically verified. HTML excerpts remain untrusted source data.
"""
from __future__ import annotations

import html
import json
import re
from typing import Any
from urllib.parse import quote, urlsplit

MAX_CANDIDATES = 3
_ENC = re.compile(r"(?i)\b(?:research|search|look\s+up|look\s+for|what\s+are|"
                  r"what\s+were|which\s+are|list|all\s+the|give\s+me|"
                  r"please|their\s+names|explain|tell\s+me|how\s+many|"
                  r"the|a|an)\b")
_STOP = frozenset(("what","which","how","list","all","the","are","were","of",
                   "and","its","their","names","please","research","about",
                   "give","have","many","some","any","with","from","for"))


def _plain(value: Any, length: int = 500) -> str:
    clean=html.unescape(re.sub(r"<[^>]{0,350}>"," ",str(value or "")))
    return " ".join(clean.split())[:length]


def search_terms(question: Any) -> str:
    text=" ".join(str(question or "").split())
    if not text or len(text)>300:
        return ""
    text=_ENC.sub(" ",text)
    text=re.sub(r"[\?\!\.,:;]+"," ",text)
    # Keep relational prepositions in search queries: "moons of Mars"
    # resolves more reliably than "moons Mars". Ignore them only during
    # relevance scoring, where "of" is not a meaningful subject keyword.
    words=[x for x in text.split() if x.lower() not in (_STOP-{"of"})]
    return " ".join(words[:13])[:130]


def _article_tokens(value: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]{2,}",value)
            if w.lower() not in _STOP}


def wikipedia_public_fallback(question: Any, fetch_page: Any) -> list[dict[str,str]]:
    """Return at most 3 relevant real Wikipedia page summaries.

    External source text is treated as untrusted evidence, never as a prompt
    instruction or an automatically proven exhaustive list.
    """
    topic=search_terms(question)
    if not topic or not callable(fetch_page):
        return []
    query_url=("https://en.wikipedia.org/w/rest.php/v1/search/page?"
               "q="+quote(topic,safe="")+"&limit=2")
    try:
        response=fetch_page(query_url)
        if not isinstance(response,dict) or int(response.get("status") or 0)!=200:
            return []
        final=urlsplit(str(response.get("finalUrl") or ""))
        if (final.scheme!="https" or final.hostname!="en.wikipedia.org"
                or final.path!="/w/rest.php/v1/search/page"):
            return []
        data=json.loads(str(response.get("extract") or "")[:12000])
        pages=data.get("pages",[]) if isinstance(data,dict) else []
        if not isinstance(pages,list):
            return []
    except (OSError,TypeError,ValueError,KeyError,json.JSONDecodeError):
        return []
    desired=_article_tokens(topic)
    result=[]
    seen=set()
    for item in pages[:5]:
        if not isinstance(item,dict):
            continue
        key=str(item.get("key") or "")
        title=_plain(item.get("title"),160)
        if not key or not title or "/" in key or "#" in key or len(key)>180:
            continue
        title_tokens=_article_tokens(title)
        common=desired.intersection(title_tokens)
        # Filter unrelated search results (e.g., missions, novels or films
        # mentioned in the article body but not requested by the user).
        if len(common)<min(2,len(desired)):
            continue
        if key.lower() in seen:
            continue
        seen.add(key.lower())
        summary_url=("https://en.wikipedia.org/w/api.php?"
                     "action=query&prop=extracts&exintro=1&explaintext=1"
                     "&exsentences=3&titles="+quote(key,safe="_()-")
                     +"&format=json&formatversion=2")
        try:
            summary_page=fetch_page(summary_url)
            if not isinstance(summary_page,dict) or int(summary_page.get("status") or 0)!=200:
                continue
            dest=urlsplit(str(summary_page.get("finalUrl") or ""))
            if dest.scheme!="https" or dest.hostname!="en.wikipedia.org":
                continue
            if dest.path!="/w/api.php":
                continue
            result_json=json.loads(str(summary_page.get("extract") or "")[:8000])
            if not isinstance(result_json,dict):
                continue
            query=result_json.get("query") or {}
            pages_out=query.get("pages") or []
            if not isinstance(pages_out,list) or len(pages_out)!=1:
                continue
            summary=pages_out[0]
            if not isinstance(summary,dict) or "missing" in summary:
                continue
            summary_title=_plain(summary.get("title"),160)
            if summary_title.lower()!=title.lower():
                continue
            excerpt=_plain(summary.get("extract"),650)
            if re.search(r"\bmay refer to\b",excerpt,re.I):
                continue
            if len(excerpt)<45:
                continue
            result.append({
                "title":"Wikipedia: "+summary_title,
                "url":"https://en.wikipedia.org/wiki/"+quote(key,safe="_()-"),
                "snippet":excerpt,
                "referenceRole":"retrieved_public_encyclopedia_summary",
            })
        except (OSError,TypeError,ValueError,KeyError,json.JSONDecodeError):
            continue
        if len(result)>=MAX_CANDIDATES:
            break
    return result
