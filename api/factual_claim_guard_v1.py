"""Fail-closed evidence checks for the ordinary §C public-research answer path.

A deliberately narrow deterministic guard, NOT a semantic truth oracle.
It checks unsupported calendar years, numbered Acts, and known edition-alias
conflations while refusing to claim it verified arbitrary prose.
No external calls, credentials, chat history, or persistent mutation.
"""
from __future__ import annotations

import re
from typing import Any

YEAR = re.compile(r"(?<!\d)(?:18|19|20)\d{2}(?!\d)")
ACT = re.compile(r"\bacts?\s+(?:I|II|III|IV|V|VI|VII|VIII|IX|X|\d{1,2})(?:\s*(?:-|to|and|&)\s*(?:I|II|III|IV|V|VI|VII|VIII|IX|X|\d{1,2}))?\b", re.I)
EQUIVALENCE = (
    re.compile(r"\bresurrected\b.{0,110}\b(?:also known as|referred to as|aka|means|is)\b.{0,45}\bclassic\b", re.I|re.S),
    re.compile(r"\bclassic\b.{0,70}\b(?:also known as|referred to as|aka|means|is)\b.{0,45}\bresurrected\b", re.I|re.S),
    re.compile(r"\bclassic\s*(?:base\s*game)?\s*\(\s*resurrected\s*\)", re.I),
)


def sourced_answer(payload: Any) -> bool:
    if not isinstance(payload, dict) or any(payload.get(key) for key in (
            "githubSourceChangeTask", "sourceChangeIdentity", "attachments",
            "uploadedFiles", "imageEvidence", "nativeEditorEvidence")):
        return False
    evidence = payload.get("onlineContext")
    return (isinstance(evidence, dict)
            and evidence.get("contractId") == "swrlz-selective-evidence-v1"
            and isinstance(evidence.get("evidence"), list)
            and int(evidence.get("resultCount") or 0) > 0)


def evidence_passages(bundle: Any) -> list[dict[str, str]]:
    if not isinstance(bundle, dict):
        return []
    items = []
    for value in bundle.get("evidence", [])[:6]:
        if not isinstance(value, dict):
            continue
        url = str(value.get("url") or "")[:500]
        title = str(value.get("title") or "")[:180]
        excerpt = str(value.get("excerpt") or "")[:1600]
        if url.startswith("https://") and title and excerpt:
            items.append({"title": title, "url": url, "excerpt": excerpt})
    return items


def inspect_answer(answer: str, bundle: Any) -> dict[str, Any]:
    """Conservative mechanical coverage test; PASS does not prove all semantics."""
    body = str(answer or "")
    passages = evidence_passages(bundle)
    if not body.strip() or not passages:
        return {"status": "REJECT", "reasons": ["missing_text_or_evidence"],
                "verifiedScope": "numeric_and_edition_checks_only"}
    corpus = " ".join(x["title"] + " " + x["excerpt"] for x in passages)
    allowed_years = set(YEAR.findall(corpus))
    claimed_years = set(YEAR.findall(body))
    reasons = []
    unsupported = sorted(claimed_years - allowed_years)
    if unsupported:
        reasons.append("unsupported_calendar_years:" + ",".join(unsupported[:8]))
    # Numbered game acts are factual, not a generic word: require direct
    # matching reference text, not arbitrary roman numerals in game titles.
    def named_acts(value: str) -> set[str]:
        output=set()
        for match in ACT.finditer(value.replace("–","-").replace("—","-")):
            for numeral in re.findall(r"\b(?:X|IX|VIII|VII|VI|V|IV|III|II|I)\b",
                                      match.group(0), re.I):
                output.add(numeral.upper())
        return output
    corpus_acts=named_acts(corpus)
    # Explicit publisher wording like "a new fifth act" supports Act V.
    if re.search(r"\b(?:new )?fifth act\b", corpus, re.I):
        corpus_acts.add("V")
    answer_acts=named_acts(body)
    missing_acts = sorted(answer_acts - corpus_acts)
    if missing_acts:
        reasons.append("unsupported_numbered_acts:" + ",".join(missing_acts[:6]))
    # Do not mistake an explicit denial of identity for equivalence.
    equivalences=[]
    for pattern in EQUIVALENCE:
        for match in pattern.finditer(body):
            segment=match.group(0)
            if not re.search(r"\b(?:not|different|distinct|unlike|separate|rather than)\b",
                             segment, re.I):
                equivalences.append(segment)
    if equivalences:
        reasons.append("unsupported_edition_equivalence")
    # A source may mention several editions; do not give the date of the
    # original game to a named expansion or remaster without nearby support.
    for sentence in re.split(r"(?<=[.!?])\s+|\n", body):
        years = set(YEAR.findall(sentence))
        if not years:
            continue
        if re.search(r"\blord of destruction\b", sentence, re.I):
            own = " ".join(p["excerpt"] for p in passages
                           if "lord of destruction" in p["title"].lower())
            # If there is no expansion-specific source, avoid a date claim.
            if not own or not years.intersection(YEAR.findall(own)):
                reasons.append("unattributed_expansion_release_year")
        if re.search(r"\bresurrected\b", sentence, re.I) and "resurrected" in body.lower():
            own = " ".join(p["excerpt"] for p in passages
                           if "resurrected" in p["title"].lower())
            # A comparison source may mention the remaster in prose, so
            # only enforce a source-date mismatch when a title-specific
            # remaster entry was actually retrieved.
            if own and not years.intersection(YEAR.findall(own)):
                reasons.append("unattributed_remaster_release_year")
    return {"status": "REJECT" if reasons else "PASS",
            "reasons": list(dict.fromkeys(reasons))[:10],
            "verifiedScope": "numeric_and_edition_checks_only",
            "sourceCount": len(passages),
            "supportedYears": sorted(allowed_years)[:20]}


def evidence_only_reply(prompt: str, bundle: Any) -> str:
    """If validation fails, give an attributable, limited answer, never a guess."""
    items = evidence_passages(bundle)
    lines = [
        "I found references, but I couldn't verify every factual claim in a "
        "complete answer from the evidence available. I won't guess at dates, "
        "editions, or game mechanics.",
        "",
        "Sources I checked:",
    ]
    for item in items[:3]:
        # Short attributed extract, not a long copyrighted quotation.
        short = " ".join(item["excerpt"].split())[:105].rstrip(" ,;:")
        lines.append("- " + item["title"] + ": " + short + "… " + item["url"])
    lines.append("")
    lines.append("Those sources need more specific evidence before I can "
                 "confidently answer the parts they don't establish.")
    return "\n".join(lines)
