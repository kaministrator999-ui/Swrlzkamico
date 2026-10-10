"""Shared, research-assisted original-songwriting technique library (prototype).

This is bounded retrieval-assisted inference, NOT GGUF weight training.
Reuses the canonical public search/fetch and Redis owners. Searches are
constructed only from public genre/form labels, never private user prompts.
Stores only known abstract technique IDs and public-source provenance; no
retrieved lyrics, quotations, prompts, conversations, names or scraped pages.

A hard request wait budget protects the 700M's response time. If research
fails, skip it without weakening the existing lyric-form validator.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from lyric_structure_school import _structure_cards

SCHEMA = "swrlz-original-lyric-research-v1"
TTL_SECONDS = 120 * 86400
FRESH_SECONDS = 18 * 3600
WAIT_SECONDS = 4.0
MAX_SOURCES = 4
MAX_LESSONS = 3

# This is a bounded public-topic vocabulary, not an external prompt/search
# containing the user's scenario, account, names or personal data.
_STYLE = (
    ("chopper", r"\b(?:chopper|double[- ]time|rapid[- ]fire|fast[- ]rap)\b", "chopper rap double time"),
    ("hiphop", r"\b(?:rap|hip[- ]?hop|freestyle|cypher|battle rap)\b", "hip hop rap"),
    ("rnb", r"\b(?:r&b|rhythm and blues|soul)\b", "rnb soul"),
    ("pop", r"\b(?:pop|dance|disco)\b", "pop dance"),
    ("rock", r"\b(?:rock|metal|hardcore)\b", "rock"),
    ("folk", r"\b(?:country|folk|acoustic)\b", "folk songwriting"),
    ("electronic", r"\b(?:edm|electronic|synth|dubstep)\b", "electronic music"),
    ("blues", r"\bblues\b", "blues songwriting"),
    ("jazz", r"\bjazz\b", "jazz songwriting"),
    ("comedy", r"\b(?:parody|comedy|funny)\b", "comedy songwriting"),
)
_FORM = (
    ("narrative", r"\b(?:mystery|story|storytelling|narrative|detective|plot)\b", "narrative songwriting"),
    ("continuous", r"\b(?:freestyle|continuous|no chorus|without chorus|one verse)\b", "continuous verse"),
    ("chorus", r"\b(?:chorus|hook|refrain)\b", "verse chorus structure"),
)
_TECHNIQUES = {
    "mystery-reveal": ("clue", "detective", "mystery", "reveal", "foreshadow", "red herring"),
    "chopper-contrast": ("double time", "double-time", "rapid fire", "rapid-fire", "triplet", "syllable", "flow switch"),
    "continuous-arc": ("continuous", "one verse", "freestyle", "no chorus", "through composed"),
    "narrative-cause": ("storytelling", "narrative", "story arc", "plot", "progression", "character"),
    "internal-rhyme": ("internal rhyme", "multisyllabic", "multi syllable", "rhyme scheme", "rhyme pocket"),
    "punchline-construction": ("punchline", "double entendre", "wordplay", "setup", "payoff"),
    "contrastive-bridge": ("bridge", "contrast", "middle eight"),
    "verse-chorus": ("verse chorus", "hook", "refrain", "chorus"),
    "intimate-motif": ("motif", "emotional", "intimate", "songwriting"),
    "rnb-dialogue": ("call and response", "duet", "dialogue", "soul"),
    "dance-groove": ("groove", "dance", "rhythm", "beat"),
    "electronic-layering": ("layering", "drop", "synth", "build"),
    "rock-dynamics": ("dynamics", "riff", "rock", "metal"),
    "folk-detail": ("storytelling", "detail", "folk", "acoustic"),
    "blues-aab": ("aab", "12 bar", "twelve bar", "blues"),
    "jazz-variation": ("swing", "jazz", "variation", "improv"),
    "classical-development": ("theme", "development", "classical", "orchestral"),
    "indie-contrast": ("indie", "alternative", "texture", "contrast"),
    "comedy-reversal": ("comedy", "parody", "punchline", "reversal"),
    "complex-form": ("opera", "progressive", "through composed", "suite"),
}
_GENRE_DEFAULTS = {
    "chopper": ("chopper-contrast", "internal-rhyme", "punchline-construction"),
    "hiphop": ("internal-rhyme", "punchline-construction", "narrative-cause"),
    "rnb": ("rnb-dialogue", "intimate-motif", "verse-chorus"),
    "pop": ("dance-groove", "verse-chorus", "intimate-motif"),
    "rock": ("rock-dynamics", "contrastive-bridge", "narrative-cause"),
    "folk": ("folk-detail", "narrative-cause", "intimate-motif"),
    "electronic": ("electronic-layering", "dance-groove", "contrastive-bridge"),
    "blues": ("blues-aab", "folk-detail", "jazz-variation"),
    "jazz": ("jazz-variation", "internal-rhyme", "contrastive-bridge"),
    "comedy": ("comedy-reversal", "punchline-construction", "narrative-cause"),
}
_NO_CHORUS = re.compile(r"\b(?:no|without|avoid|skip|don't)\s+(?:a\s+)?(?:chorus|hook|refrain)\b", re.I)
_OFFLINE = re.compile(r"\b(?:offline(?:\s+only)?|no\s+(?:internet|online|web|research)|don't\s+(?:browse|search)|without\s+(?:online|web)\s+research)\b", re.I)
_DISABLED = {"0", "off", "false", "disabled"}

_inflight = threading.BoundedSemaphore(2)
_ram_lock = threading.Lock()
_ram: dict[str, tuple[float, dict]] = {}


def _topic(prompt: str) -> tuple[str, str, str] | None:
    text = str(prompt or "")[:1400].casefold()
    if _OFFLINE.search(text) or os.getenv("SWRLZ_LYRIC_RESEARCH_ENABLED", "1").lower() in _DISABLED:
        return None
    style = next(((name, query) for name, pattern, query in _STYLE if re.search(pattern, text)), None)
    if not style:
        return None
    form = next(((name, query) for name, pattern, query in _FORM if re.search(pattern, text)), ("general", "songwriting structure"))
    return style[0], style[1], form[0]


def _key(topic: tuple[str, str, str]) -> str:
    return "swrlz:lyric-techniques:v1:" + topic[0] + ":" + topic[2]


def _redis():
    try:
        from api.durable_redis_store import RedisRestChatStore
        if RedisRestChatStore.configured():
            return RedisRestChatStore.from_env()
    except (ImportError, RuntimeError, ValueError):
        pass
    return None


def _valid_record(raw: object, topic: tuple[str, str, str]) -> dict | None:
    if not isinstance(raw, dict) or raw.get("schema") != SCHEMA:
        return None
    if raw.get("style") != topic[0] or raw.get("form") != topic[2]:
        return None
    allow = {card["id"] for card in _structure_cards()}
    ids = raw.get("lessonIds")
    if not isinstance(ids, list) or not (1 <= len(ids) <= MAX_LESSONS):
        return None
    if any(not isinstance(i, str) or i not in allow for i in ids):
        return None
    try:
        fetched = int(raw.get("fetchedAt", 0))
    except (TypeError, ValueError):
        return None
    if fetched < 0 or fetched > int(time.time()) + 60:
        return None
    return {"schema": SCHEMA, "style": topic[0], "form": topic[2],
            "lessonIds": ids, "sourceCount": max(0, min(MAX_SOURCES, int(raw.get("sourceCount", 0)))),
            "fetchedAt": fetched}


def _load(topic):
    key = _key(topic)
    with _ram_lock:
        entry = _ram.get(key)
    if entry and entry[0] > time.monotonic():
        return _valid_record(entry[1], topic)
    r = _redis()
    if r:
        try:
            raw = r._command("GET", key, sensitive=True)
            value = _valid_record(json.loads(raw), topic) if isinstance(raw, str) else None
            if value:
                with _ram_lock:
                    _ram[key] = (time.monotonic() + 120, value)
                return value
        except (ValueError, TypeError, RuntimeError, OSError):
            pass
    return None


def _save(topic, record):
    value = _valid_record(record, topic)
    if not value:
        return False
    with _ram_lock:
        if len(_ram) > 40:
            _ram.pop(next(iter(_ram)))
        _ram[_key(topic)] = (time.monotonic() + 120, value)
    r = _redis()
    if not r:
        return False
    try:
        r._command("SET", _key(topic),
                   json.dumps(value, ensure_ascii=True, separators=(",", ":")),
                   "EX", TTL_SECONDS, sensitive=True)
        return True
    except (ValueError, TypeError, RuntimeError, OSError):
        return False


def _source_row(item):
    if not isinstance(item, dict):
        return None
    url = str(item.get("url") or "")
    try:
        u = urlsplit(url)
        host = str(u.hostname or "").lower()
        if u.scheme != "https" or not host or host.endswith(("genius.com", "musixmatch.com", "azlyrics.com", "lyrics.com")):
            return None
        if any(part in (u.path or "").lower() for part in ("/lyrics/", "/lyric/", "/translation/")):
            return None
        if not re.fullmatch(r"[a-z0-9.-]{4,120}", host):
            return None
        info = " ".join((str(item.get("title") or ""), str(item.get("snippet") or "")))[:900].casefold()
        if not any(t in info for t in ("rap", "song", "music", "rhyme", "lyric", "flow", "verse", "chopper", "writing", "producer")):
            return None
        # Query strings and textual evidence are never stored in the library.
        return {"domain": host, "text": info}
    except (ValueError, TypeError):
        return None


def _study(topic, search):
    # The two categories cover guides AND named-song/style analysis, but do
    # not retrieve or store lyric transcriptions.
    style, query_style, form = topic
    form_query = next((q for n, _, q in _FORM if n == form), "songwriting structure")
    queries = (
        query_style + " songwriting craft guide rhyme rhythm arrangement",
        query_style + " songs structural flow analysis " + form_query,
    )
    rows = []
    for query in queries:
        try:
            results = search(query)
        except Exception:
            continue
        for item in list(results or [])[:5]:
            row = _source_row(item)
            if row and row["domain"] not in {e["domain"] for e in rows}:
                rows.append(row)
            if len(rows) >= MAX_SOURCES:
                break
    if not rows:
        return None
    # Extract only matches from the published, human-reviewed technique cards,
    # never arbitrary retrieved instructions or copyrighted source text.
    allow = {c["id"]: c for c in _structure_cards()}
    candidates = list(_GENRE_DEFAULTS.get(style, ()))
    if form == "narrative":
        candidates = ["mystery-reveal", "narrative-cause"] + candidates
    elif form == "continuous":
        candidates = ["continuous-arc"] + candidates
    elif form == "chorus":
        candidates = ["verse-chorus"] + candidates
    if form == "continuous":
        candidates = [c for c in candidates if not allow.get(c, {}).get("requiresChorus")]
    scores = []
    for index, card_id in enumerate(dict.fromkeys(candidates)):
        if card_id not in allow:
            continue
        words = _TECHNIQUES.get(card_id, ())
        signals = sum(any(term in row["text"] for term in words) for row in rows)
        # One genuinely relevant public result is a minimum, not a claim
        # that all of the studied songs support the technique.
        if signals:
            scores.append((-signals, index, card_id))
    ids = [id for _, _, id in sorted(scores)[:MAX_LESSONS]]
    if not ids:
        return None
    return {"schema": SCHEMA, "style": style, "form": form,
            "lessonIds": ids, "sourceCount": len(rows),
            "fetchedAt": int(time.time())}


def _guidance(record, topic):
    if not record:
        return ""
    allow = {c["id"]: c for c in _structure_cards()}
    no_chorus = topic[2] == "continuous"
    selected = []
    for identifier in record.get("lessonIds", []):
        card = allow.get(identifier)
        if card and not (no_chorus and card.get("requiresChorus")):
            selected.append(card["cue"])
    if not selected:
        return ""
    return ("\nONLINE-INFORMED ORIGINAL SONGWRITING MECHANICS (verified technique card selection, "
            "NOT retrieved lyrics or artist imitation): " + " ".join(selected[:MAX_LESSONS])
            + " Use original topic, objects, rhyme words, plot and language; "
            "never quote, paraphrase or imitate a particular song.")


def research_for_creation(prompt: str, search=None, *, wait_seconds: float = WAIT_SECONDS):
    """One bounded online attempt per stale genre/form; cached patterns persist.

    Do not call for online lyric lookup, coding, or non-creation requests:
    caller owns that intent boundary. An offline-only request always skips.
    """
    topic = _topic(prompt)
    empty = {"status": "SKIPPED", "sourceCount": 0, "lessonCount": 0, "cache": False}
    if topic is None:
        return "", empty
    cached = _load(topic)
    if cached and int(time.time()) - cached["fetchedAt"] < FRESH_SECONDS:
        guidance = _guidance(cached, topic)
        return guidance, {"status": "CACHED", "sourceCount": cached["sourceCount"],
                          "lessonCount": len(cached["lessonIds"]), "cache": True}
    if search is None:
        try:
            from api.online_research import search_public
            search = search_public
        except ImportError:
            search = None
    if search is None or not _inflight.acquire(blocking=False):
        hint = _guidance(cached, topic)
        return hint, {"status": "CACHED" if hint else "UNAVAILABLE",
                      "sourceCount": cached["sourceCount"] if cached else 0,
                      "lessonCount": len(cached["lessonIds"]) if cached else 0,
                      "cache": bool(hint)}
    done = threading.Event()
    response = {}
    def worker():
        try:
            record = _study(topic, search)
            if record:
                _save(topic, record)
                response["record"] = record
        finally:
            _inflight.release()
            done.set()
    threading.Thread(target=worker, name="swrlz-lyric-research", daemon=True).start()
    finished = done.wait(timeout=max(0.01, min(float(wait_seconds), WAIT_SECONDS)))
    record = response.get("record") if finished else None
    if record:
        return _guidance(record, topic), {"status": "RESEARCHED",
                                        "sourceCount": record["sourceCount"],
                                        "lessonCount": len(record["lessonIds"]),
                                        "cache": False}
    hint = _guidance(cached, topic)
    return hint, {"status": "CACHED" if hint else ("PENDING" if not finished else "UNAVAILABLE"),
                  "sourceCount": cached["sourceCount"] if cached else 0,
                  "lessonCount": len(cached["lessonIds"]) if cached else 0,
                  "cache": bool(hint)}
