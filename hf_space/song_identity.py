"""Deterministic song identity + ambiguity-aware discovery for §wyrlz.

This module does not fetch pages and does not verify lyric bodies. It prepares a
song entity and ranks search results before the existing bounded fetch/verifier.
"""
from __future__ import annotations

import re
import urllib.parse
import unicodedata
from typing import Any

SCHEMA="swrlz-song-identity-v1"
DISCOVERY_SCHEMA="swrlz-song-discovery-v1"

_COMMON_TITLE_WORDS={
    "work","home","hello","monster","flowers","flower","stay","sorry","love","baby",
    "fire","water","rock","city","rack","money","gold","dream","dreams","night","day",
    "party","beautiful","perfect","closer","happy","believer","radio","human","bad",
    "good","run","rise","fall","lost","alone","changes","change","crazy","sweet",
    "heart","hearts","life","time","one","two","three","you","me","us","we","go",
    "down","up","high","low","cold","hot","piece","world","girl","boy","man","woman",
}

_POSITIVE_LYRIC_DOMAINS=(
    "genius.com","azlyrics.com","musixmatch.com","lyricsfreak.com",
    "songlyrics.com","lyrics.com","allthelyrics.com","lyricfind.com",
)
_NEGATIVE_DOMAIN_HINTS=(
    "amazon.","walmart.","target.","nordstrom.","homedepot.","lowes.","wayfair.",
    "dictionary.","merriam-webster.","cambridge.","wiktionary.","etsy.","ebay.",
)
_NEGATIVE_CONTENT_HINTS=(
    "shop","shopping","buy","sale","price","rack shelf","shelving","dictionary",
    "definition","meaning of","review","reaction","instrumental","karaoke","chords",
    "guitar tabs","tabs","translation","cover version","merch","product",
)
_VERSION_TERMS=("remix","live","acoustic","clean","explicit","radio edit","original","extended","demo","sped up","slowed")
_STOP={"the","a","an","of","and","or","to","for","feat","featuring","ft","with","by"}


def _clean(value: Any, limit: int = 240) -> str:
    return " ".join(str(value or "").replace("“",'"').replace("”",'"').replace("’","'").split())[:limit]


def _fold(value: Any) -> str:
    text=unicodedata.normalize("NFKD",str(value or "")).casefold()
    text=text.replace("&"," and ")
    return re.sub(r"[^a-z0-9]+"," ",text).strip()


def _tokens(value: Any) -> list[str]:
    return [x for x in _fold(value).split() if x and x not in _STOP]


def _subject_parts(subject: str) -> tuple[str,str]:
    m=re.match(r'^"([^"]+)"(?:\s+by\s+(.+))?$',_clean(subject,500),re.I)
    if m:
        return _clean(m.group(1),180).strip(" \"'"),_clean(m.group(2),180).strip(" \"'") if m.group(2) else ""
    return _clean(subject,180).strip(" \"'"),""


def _split_features(artist: str) -> tuple[str,list[str]]:
    value=_clean(artist,220)
    m=re.split(r"(?i)\s+(?:feat\.?|featuring|ft\.?)\s+",value,maxsplit=1)
    primary=m[0].strip()
    featured=[]
    if len(m)>1:
        featured=[x.strip() for x in re.split(r"\s*(?:,|&|\band\b)\s*",m[1],flags=re.I) if x.strip()]
    return primary,featured[:6]


def _requested_version(title: str) -> tuple[str,str|None]:
    clean=_clean(title,200)
    version=None
    # Prefer parenthetical/bracketed explicit modifiers.
    for m in re.finditer(r"[\[(]([^\])]+)[\])]",clean):
        folded=_fold(m.group(1))
        if any(term in folded for term in _VERSION_TERMS):
            version=m.group(1).strip()
            clean=(clean[:m.start()]+clean[m.end():]).strip(" -")
            break
    if version is None:
        low=_fold(clean)
        for term in sorted(_VERSION_TERMS,key=len,reverse=True):
            if re.search(rf"\b{re.escape(term)}\b",low):
                version=term
                # Keep title text intact if modifier is not syntactically separable.
                break
    return clean,version


def song_identity(subject: str) -> dict[str,Any]:
    raw_title,raw_artist=_subject_parts(subject)
    title,version=_requested_version(raw_title)
    primary,featured=_split_features(raw_artist)
    title_tokens=_tokens(title)
    artist_tokens=_tokens(primary)
    common_hits=[t for t in title_tokens if t in _COMMON_TITLE_WORDS]
    punctuation_heavy=bool(re.search(r"[^A-Za-z0-9\s'’-]",title))
    short_title=len(title_tokens)<=2
    all_common=bool(title_tokens) and len(common_hits)==len(title_tokens)
    ambiguity_score=0
    if short_title: ambiguity_score+=2
    if all_common: ambiguity_score+=3
    elif common_hits: ambiguity_score+=1
    if len(title_tokens)==1: ambiguity_score+=2
    if not primary: ambiguity_score+=2
    if punctuation_heavy: ambiguity_score+=1
    ambiguity="high" if ambiguity_score>=5 else "medium" if ambiguity_score>=3 else "low"
    return {
        "schema":SCHEMA,
        "rawSubject":_clean(subject,500),
        "title":title,
        "titleFolded":_fold(title),
        "titleTokens":title_tokens[:16],
        "primaryArtist":primary,
        "primaryArtistFolded":_fold(primary),
        "artistTokens":artist_tokens[:16],
        "featuredArtists":featured,
        "requestedVersion":version,
        "ambiguity":{
            "level":ambiguity,
            "score":ambiguity_score,
            "commonWordCollision":common_hits[:12],
            "shortTitle":short_title,
            "punctuationHeavy":punctuation_heavy,
            "quotedTitleRequired":ambiguity in {"medium","high"},
            "artistRequired":bool(primary),
        },
    }



def resolve_unseparated_artist(identity: dict[str,Any], candidates: list[dict[str,Any]]) -> dict[str,Any]:
    """Resolve 'title artist' only after independent search headings prove a split.

    Never infer an artist from the number of words alone. A match must visibly
    identify title and performer in the heading of two different source families.
    """
    if not isinstance(identity,dict) or identity.get("primaryArtist"):
        return identity
    words=_clean(identity.get("title"),180).split()
    if not 3<=len(words)<=10:
        return identity

    possible=[]
    for split in range(1,len(words)):
        proposed_title=" ".join(words[:split])
        proposed_artist=" ".join(words[split:])
        title_fold=_fold(proposed_title)
        artist_fold=_fold(proposed_artist)
        families=set()
        for item in candidates[:24] if isinstance(candidates,list) else []:
            if not isinstance(item,dict):
                continue
            heading=_clean(item.get("title"),320)
            artist_first=re.match(r"^(.+?)\s+[-–—]\s+(.+?)\s+lyrics?\b",heading,re.I)
            title_first=re.match(r"^(.+?)\s+lyrics?\s+(?:by|[-–—])\s+(.+?)(?=\s+[-–—|]\s+|$)",heading,re.I)
            matched=bool(
                (artist_first and _fold(artist_first.group(1))==artist_fold
                    and _fold(artist_first.group(2))==title_fold)
                or (title_first and _fold(title_first.group(1))==title_fold
                    and _fold(title_first.group(2))==artist_fold)
            )
            if matched:
                family=source_family(item)
                if family:
                    families.add(family)
        if len(families)>=2:
            possible.append((len(families),split,proposed_title,proposed_artist,sorted(families)))

    if not possible:
        return identity
    possible.sort(key=lambda x:(-x[0],-x[1]))
    strongest=possible[0]
    if len(possible)>1 and strongest[0]==possible[1][0]:
        return identity  # conflicting equally corroborated parses; remain uncertain
    resolved=song_identity(f'"{strongest[2]}" by {strongest[3]}')
    resolved["resolution"]="CROSS_SOURCE_HEADING_CONSENSUS"
    resolved["resolutionSourceFamilies"]=strongest[4][:6]
    resolved["originalRawSubject"]=identity.get("rawSubject")
    return resolved


def supports_direct_lyric_text_fetch(item: dict[str,Any]) -> bool:
    """A video/music stream result can be linked, but not fetched as lyric body."""
    url=_clean(item.get("url"),1600)
    parsed=urllib.parse.urlsplit(url)
    host=str(parsed.hostname or "").casefold()
    if parsed.scheme not in {"http","https"} or not host:
        return False
    non_text_hosts=("youtube.com","youtu.be","tiktok.com","spotify.com","music.apple.com","soundcloud.com","vimeo.com")
    return not any(host==domain or host.endswith("."+domain) for domain in non_text_hosts)


def query_ladder(identity: dict[str,Any], max_queries: int = 8) -> list[dict[str,Any]]:
    title=_clean(identity.get("title"),180)
    artist=_clean(identity.get("primaryArtist"),180)
    version=_clean(identity.get("requestedVersion"),80)
    if not title:
        return []
    qtitle=f'"{title}"'
    qartist=f'"{artist}"' if artist else ""
    version_bit=f' "{version}"' if version else ""
    plans=[]
    def add(strategy,q):
        q=_clean(q,500)
        if q and all(x["query"]!=q for x in plans):
            plans.append({"strategy":strategy,"query":q})
    if artist:
        add("exact-title-artist",f'{qtitle} {qartist}{version_bit} lyrics')
        add("artist-title-song",f'{qartist} {qtitle}{version_bit} song lyrics')
        # For ambiguous titles, a lyric-source family is a stronger third step
        # than another generic bag-of-words query. Keep the broader structural
        # query later in the bounded ladder.
        hosts=("genius.com","azlyrics.com","musixmatch.com","allthelyrics.com","lyricsfreak.com")
        add("source-family-disambiguation",f'{qtitle} {qartist}{version_bit} lyrics site:{hosts[0]}')
        add("title-artist-verse",f'{qtitle} {qartist}{version_bit} verse chorus lyrics')
        for host in hosts[1:]:
            add("source-family-disambiguation",f'{qtitle} {qartist}{version_bit} lyrics site:{host}')
    else:
        add("exact-title",f'{qtitle}{version_bit} lyrics')
        add("title-song",f'{qtitle}{version_bit} song lyrics')
        for host in ("genius.com","azlyrics.com","musixmatch.com","allthelyrics.com","lyricsfreak.com"):
            add("source-family-disambiguation",f'{qtitle}{version_bit} lyrics site:{host}')
    return plans[:max(1,int(max_queries))]


def candidate_score(item: dict[str,Any], identity: dict[str,Any]) -> dict[str,Any]:
    title=_clean(item.get("title"),320)
    snippet=_clean(item.get("snippet"),1000)
    url=_clean(item.get("url"),1600)
    host=str(urllib.parse.urlsplit(url).hostname or "").casefold()
    hay=_fold(" ".join([title,snippet,urllib.parse.unquote(url)]))
    item_title_fold=_fold(title)

    title_phrase=_fold(identity.get("title"))
    artist_phrase=_fold(identity.get("primaryArtist"))
    title_tokens=list(identity.get("titleTokens") or [])
    artist_tokens=list(identity.get("artistTokens") or [])
    requested_version=_fold(identity.get("requestedVersion"))

    exact_title=bool(title_phrase and (
        title_phrase in item_title_fold
        or title_phrase in _fold(snippet)
        or title_phrase in _fold(urllib.parse.unquote(url))
    ))
    title_hits=sum(1 for t in title_tokens if t in hay)
    artist_hits=sum(1 for t in artist_tokens if t in hay)
    exact_artist=bool(artist_phrase and artist_phrase in hay)
    lyric_word=bool(re.search(r"\blyrics?\b",hay))
    lyric_domain=any(host==d or host.endswith("."+d) for d in _POSITIVE_LYRIC_DOMAINS)
    negative_domain=any(hint in host for hint in _NEGATIVE_DOMAIN_HINTS)
    negative_terms=[hint for hint in _NEGATIVE_CONTENT_HINTS if _fold(hint) in hay]

    found_versions=[term for term in _VERSION_TERMS if re.search(rf"\b{re.escape(_fold(term))}\b",hay)]
    version_match=bool(requested_version and requested_version in hay)
    # "original" and "explicit" are often descriptive labels on otherwise-correct
    # lyric pages. Hard mismatch is reserved for materially different arrangements.
    material_versions={"remix","live","acoustic","clean","radio edit","extended","demo","sped up","slowed"}
    found_material=[term for term in found_versions if term in material_versions]
    version_mismatch=bool(found_material and not requested_version)
    if requested_version and found_versions:
        version_mismatch=not version_match

    ambiguity=((identity.get("ambiguity") or {}).get("level") or "low")
    title_needed=max(1,min(len(title_tokens),2))
    title_ok=exact_title or title_hits>=title_needed
    artist_ok=(not artist_tokens) or exact_artist or artist_hits>=1

    score=0
    reasons=[]
    if exact_title: score+=24;reasons.append("EXACT_TITLE_PHRASE")
    else: score+=title_hits*5
    if exact_artist: score+=18;reasons.append("EXACT_ARTIST")
    else: score+=artist_hits*6
    if lyric_word: score+=5;reasons.append("LYRIC_CONTENT_HINT")
    if lyric_domain: score+=12;reasons.append("LYRIC_DOMAIN_PRIOR")
    if re.search(r"\[(?:verse|chorus|bridge|hook|intro|outro|pre[- ]?chorus)\b",snippet,re.I):
        score+=8;reasons.append("STRUCTURED_LYRIC_SNIPPET")
    if negative_domain: score-=24;reasons.append("NON_LYRIC_DOMAIN")
    if negative_terms:
        score-=min(28,7*len(negative_terms));reasons.append("NON_LYRIC_CONTENT")
    if version_match: score+=8;reasons.append("VERSION_MATCH")
    if version_mismatch: score-=16;reasons.append("VERSION_MISMATCH")

    allowed=title_ok and artist_ok and not negative_domain and not version_mismatch
    if ambiguity=="high":
        allowed=allowed and exact_title and artist_ok
    elif ambiguity=="medium":
        allowed=allowed and (exact_title or title_hits>=max(2,title_needed))

    if not title_ok: rejection="TITLE_MISMATCH"
    elif not artist_ok: rejection="ARTIST_MISMATCH"
    elif version_mismatch: rejection="VERSION_MISMATCH"
    elif negative_domain or negative_terms: rejection="NON_LYRIC_RESULT"
    elif not allowed: rejection="AMBIGUOUS_TITLE_WEAK_MATCH"
    else: rejection="ADMITTED"

    return {
        "schema":DISCOVERY_SCHEMA,
        "allowed":bool(allowed),
        "score":int(score),
        "reason":rejection,
        "signals":reasons[:12],
        "exactTitle":exact_title,
        "titleHits":title_hits,
        "titleNeeded":title_needed,
        "exactArtist":exact_artist,
        "artistHits":artist_hits,
        "lyricDomain":lyric_domain,
        "negativeContentHints":negative_terms[:6],
        "versionMatch":version_match,
        "versionMismatch":version_mismatch,
        "foundVersions":found_versions[:8],
        "materialVersionConflicts":found_material[:8],
        "host":host,
    }


def source_family(item: dict[str,Any]) -> str:
    """Return a stable source-family key so duplicate variants do not monopolize a bounded fetch budget."""
    url=_clean(item.get("url"),1600)
    source=_clean(item.get("source"),240)
    host=str(urllib.parse.urlsplit(url).hostname or source or "").casefold().strip(".")
    if host.startswith("www."):
        host=host[4:]
    for domain in _POSITIVE_LYRIC_DOMAINS:
        if host==domain or host.endswith("."+domain):
            return domain
    parts=[part for part in host.split(".") if part]
    return ".".join(parts[-2:]) if len(parts)>=2 else host


def rank_candidates(items: list[dict[str,Any]], identity: dict[str,Any]) -> list[dict[str,Any]]:
    ranked=[]
    for item in items:
        if not isinstance(item,dict):
            continue
        score=candidate_score(item,identity)
        ranked.append({**item,"songIdentityScore":score,"sourceFamily":source_family(item)})
    ranked.sort(key=lambda x:(-int((x.get("songIdentityScore") or {}).get("score") or 0),int(x.get("rank") or 999)))
    return ranked


def diversify_candidates(items: list[dict[str,Any]], identity: dict[str,Any]) -> list[dict[str,Any]]:
    """Prefer one strong candidate per source family before duplicate variants.

    This preserves global SongIdentity scoring while preventing two URLs from the
    same provider from consuming consecutive slots in a small page-fetch budget.
    """
    ranked=rank_candidates(items,identity)
    first=[]
    overflow=[]
    seen_families=set()
    for item in ranked:
        family=str(item.get("sourceFamily") or source_family(item) or "")
        if family and family not in seen_families:
            seen_families.add(family)
            first.append(item)
        else:
            overflow.append(item)
    return first+overflow
