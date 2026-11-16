"""Conservative evidence-only conversation adaptation for signed-in §C accounts.

No model training, persistent extracted facts, or assistant-authored memories.
The Station caller supplies the *verified owner's* native threads and opted-in
ChatGPT archive index. All old user messages remain untrusted historical data.
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone

MAX_CONTEXT = 900
MAX_SIGNAL_TEXT = 240
MAX_NATIVE_THREADS = 80
MAX_NATIVE_MESSAGES = 1000
MAX_MESSAGES_PER_THREAD = 80
MAX_SIGNALS_PER_IMPORT = 6
MAX_SELECTED = 4
_WORD = re.compile(r"[a-z0-9][a-z0-9_-]{2,39}", re.I)
_STOP = set(("the and are was were for with from into about this that have your you our "
             "can could would should how what when why who where chat please want need "
             "just like more make only some same help show new old conversation conversations").split())
# Unsolicited continuity deliberately avoids transmitting likely secrets, contact
# information, sensitive personal records, or private third-party details.
_SENSITIVE = re.compile(
    r"(?i)\b(?:password|passphrase|api[ -]?key|secret[ -]?key|access[ -]?token|"
    r"private key|social security|ssn|credit card|bank account|routing number|"
    r"diagnos(?:ed|is)|medical record|therapy notes|my child|my kids|my daughter|"
    r"my son|religious affiliation|political affiliation)\b|"
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|"
    r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)|"
    r"\b\d{1,5}\s+(?:[A-Za-z]+\s+){0,3}(?:street|st|avenue|ave|road|rd|boulevard|blvd)\b",
    re.I
)
_TEMPORARY = re.compile(
    r"(?i)\b(?:just (?:for )?this (?:one|time|answer|reply)|this (?:time|turn|message|reply|answer|chat) only|"
    r"for (?:this|the) (?:answer|reply|message|chat|turn)|right now|temporarily|today|tonight|"
    r"for now|this once|in this conversation)\b"
)
_REVOKE = re.compile(
    r"(?i)\b(?:forget (?:my|that|the|your)?|stop remembering|"
    r"(?:do not|don't) remember|remove (?:my|that|the) (?:old |previous )?preference)\b"
)
_EXPLICIT = re.compile(
    r"(?i)\b(?:i (?:really )?(?:prefer|like|dislike|don't want|do not want)|"
    r"(?:i want|i need) (?:you|your|the answer|responses|replies)|"
    r"(?:please |you should |you must )?(?:always|never|don't|do not|stop) (?:you |me |your |doing |giving |calling |using |repeating |asking |including |showing )?|"
    r"from now on|going forward|remember (?:that|this)|"
    r"when (?:you|we) (?:answer|code|build|write|research|test))\b"
)
_QUOTED = re.compile(r"(?i)^(?:the )?(?:assistant|model|chatgpt|someone|they|she|he) (?:said|wrote|suggested|answered)\b")
_DOMAINS = {
    "coding": re.compile(r"(?i)\b(?:code|coding|github|repository|repo|commit|deploy|software|programming|bug|debug|build|test suite|unit tests|§c|§e)\b"),
    "creative": re.compile(r"(?i)\b(?:lyrics?|songs?|rap|rhyme|remix|parody|poem|poetry|story|creative writing)\b"),
}
_SCOPE_BIND = re.compile(r"(?i)\b(?:when|while|for|during|in|about)\b")
_SLOTS = (
    ("address", re.compile(r"(?i)\b(?:call me|address me|refer to me|don't call me)\b")),
    ("vocabulary", re.compile(r"(?i)\b(?:wording|phrase|phrasing|don't say|do not say|word[s]?|term[s]?|nickname)\b")),
    ("answer_length", re.compile(r"(?i)\b(?:short|shorter|brief|concise|long|longer|detailed|thorough|depth|length|verbosity|wordy)\b")),
    ("evidence", re.compile(r"(?i)\b(?:verif\w*|cit\w*|source\w*|evidence|hallucinat\w*|accurac\w*|fact.check|research|receipts)\b")),
    ("format", re.compile(r"(?i)\b(?:format|markdown|list\w*|paragraph\w*|bullets?|tables?|headings?|copyable)\b")),
    ("tone", re.compile(r"(?i)\b(?:humor|jok\w*|funny|serious|formal|casual|tone|emoji\w*|playful|professional|sarcas\w*)\b")),
    ("coding", _DOMAINS["coding"]),
    ("creative", _DOMAINS["creative"]),
    ("interaction", re.compile(r"(?i)\b(?:ask\w*|question\w*|repeat\w*|clarif\w*|correct\w*|disagree|feedback|context|remember|memory|history|interrupt\w*)\b")),
)
_GLOBAL = {"address", "vocabulary", "answer_length", "evidence", "tone", "format", "interaction"}


def terms(text):
    return {w for w in _WORD.findall(str(text or "").lower()[:1200]) if w not in _STOP}


def _stamp(value):
    if type(value) not in (int, float) or value <= 0:
        return 0.0
    value = float(value)
    if value > 1e12:
        value /= 1000
    return value if value <= time.time() + 300 else 0.0


def _safe_text(value, limit=600):
    text = " ".join(str(value or "").split())[:limit]
    return text if len(text) >= 12 and not _SENSITIVE.search(text) else ""


def _classify(text):
    # One signal per message. Never infer traits or biography.
    slot = next((name for name, pattern in _SLOTS if pattern.search(text[:350])), None)
    if not slot:
        return None, None
    scope = "global"
    # Domain-specific slots never become universal personality instructions.
    if slot in _DOMAINS:
        scope = slot
    elif slot != "address" and _SCOPE_BIND.search(text):
        scoped = [domain for domain, pattern in _DOMAINS.items() if pattern.search(text)]
        if len(scoped) == 1:
            scope = scoped[0]
    return slot, scope


def signal(message, source, thread_id, allow_temporary=False):
    """Extract only explicit user interaction directions with provenance."""
    if not isinstance(message, dict) or str(message.get("role") or "").lower() != "user":
        return None
    stamped = message.get("createdAt")
    if type(stamped) in (int, float) and stamped > 0 and not _stamp(stamped):
        return None  # Future-dated evidence is never treated as a prior user preference.
    raw = str(message.get("text") or "")
    text = _safe_text(raw)
    if not text or _QUOTED.search(text) or (not allow_temporary and _TEMPORARY.search(text)):
        return None
    if not (_EXPLICIT.search(text[:280]) or _REVOKE.search(text[:280])):
        return None
    slot, scope = _classify(text)
    if not slot:
        return None
    kind = "revoke" if _REVOKE.search(text[:280]) else "preference"
    return {"slot":slot, "scope":scope, "kind":kind,
            "text":text[:MAX_SIGNAL_TEXT], "source":source,
            "threadId":str(thread_id or "")[:140], "at":_stamp(message.get("createdAt")),
            "messageId":str(message.get("id") or "")[:140]}


def archive_signals(messages, thread_id):
    signals = [found for message in (messages or [])
               if isinstance(message, dict)
               for found in [signal(message, "chatgpt-import", thread_id)] if found]
    signals.sort(key=lambda item:item["at"], reverse=True)
    seen = set()
    result = []
    for item in signals:
        key = (item["slot"], item["scope"])
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
        if len(result) >= MAX_SIGNALS_PER_IMPORT:
            break
    return result


def _native_messages(threads, active_thread_id):
    selected = sorted(
        (t for t in (threads or []) if isinstance(t, dict)
         and str(t.get("id") or "") != str(active_thread_id or "")),
        key=lambda t:_stamp(t.get("updatedAt") or t.get("createdAt")), reverse=True)
    remaining = MAX_NATIVE_MESSAGES
    for thread in selected[:MAX_NATIVE_THREADS]:
        msgs = thread.get("messages") or []
        if not isinstance(msgs, list):
            continue
        for message in reversed(msgs[-min(remaining, MAX_MESSAGES_PER_THREAD):]):
            if remaining <= 0:
                return
            remaining -= 1
            if isinstance(message, dict):
                yield str(thread.get("id") or ""), str(thread.get("title") or "")[:100], message


def _active_domain(prompt):
    found = [key for key, pattern in _DOMAINS.items() if pattern.search(prompt)]
    return found[0] if len(found) == 1 else None


def compose(prompt, native_threads, imported_docs=(), active_thread_id=""):
    """Evidence-only synthesis; current instructions beat older stated preferences.

    Account scoping and archive opt-in MUST be enforced by Station, not by this
    pure module. No assistant-authored facts and no durable profile mutations.
    """
    query = terms(prompt)
    domain = _active_domain(str(prompt or ""))
    if re.fullmatch(r"(?i)\s*(?:(?:hi|hey|hello|yo|thanks|thank you|okay|ok|bye|lol|lmfao|good morning|good night)[!. ]*)", str(prompt or "").strip()):
        return ""
    # Even one-turn instructions (not stored as durable preferences) override
    # older preferences in their slot on the current generation.
    current = signal({"role":"user","text":prompt}, "current", active_thread_id,
                     allow_temporary=True)
    if current is None and re.search(
        r"(?i)\b(?:give me|keep (?:it|your|the)|make (?:it|your|the)|"
        r"(?:please )?(?:answer|respond|write|explain) (?:in|with|as)|"
        r"(?:be|stay) (?:more|less|very))\b", str(prompt or "")):
        # Imperative current-turn style constraints supersede historical style.
        slot, scope = _classify(str(prompt or ""))
        if slot:
            current = {"slot":slot, "scope":scope}
    # New instructions win across every topic scope for this response.
    suppress = {(current["slot"], scope) for scope in ("global","coding","creative")} if current else set()
    candidates, topical = [], []
    for tid, title, message in _native_messages(native_threads, active_thread_id):
        found = signal(message, "native-§c", tid)
        if found:
            candidates.append(found)
        if str(message.get("role") or "").lower() != "user" or not query or not domain:
            continue
        stamped = message.get("createdAt")
        if type(stamped) in (int, float) and stamped > 0 and not _stamp(stamped):
            continue
        content = _safe_text(message.get("text"))
        if not content:
            continue
        body_hits = query.intersection(terms(content))
        overlap = query.intersection(terms(title) | terms(content))
        if body_hits and len(overlap) >= 2:
            topical.append((len(body_hits)*2+len(overlap), _stamp(message.get("createdAt")), tid, content[:240]))
    for doc in (imported_docs or ()):
        if not isinstance(doc, dict):
            continue
        for item in doc.get("continuitySignals") or ():
            if (isinstance(item, dict) and item.get("source") == "chatgpt-import"
                    and item.get("slot") in dict(_SLOTS)
                    and item.get("scope") in ("global", "coding", "creative")
                    and item.get("kind") in ("preference", "revoke")):
                candidates.append(item)
    candidates.sort(key=lambda item:(_stamp(item.get("at")), item.get("source") == "native-§c"), reverse=True)
    seen = set(suppress)
    retained = []
    for item in candidates:
        key = (item.get("slot"),item.get("scope"))
        if key in seen:
            continue
        scope = item.get("scope")
        if scope != "global" and scope != domain:
            continue
        seen.add(key)
        if item.get("kind") == "revoke":
            continue
        # A matching topical instruction takes precedence over general for
        # the same dimension, regardless of its original conversation date.
        retained.append(item)
    scoped_slots = {item["slot"] for item in retained if item["scope"] != "global"}
    retained = [item for item in retained if not
                (item["scope"] == "global" and item["slot"] in scoped_slots)]
    retained.sort(key=lambda item:(item["scope"] == domain, _stamp(item.get("at"))), reverse=True)
    # Prefer decisive recent instructions; older unrelated ones are not
    # automatically injected into every generic greeting.
    results = []
    for item in retained:
        slot = item["slot"]
        if slot in ("coding","creative") and domain != slot:
            continue
        content = _safe_text(item.get("text"), MAX_SIGNAL_TEXT)
        if not content:
            continue
        at = _stamp(item.get("at"))
        when = datetime.fromtimestamp(at,timezone.utc).date().isoformat() if at else "undated"
        results.append(f"{slot}/{item['scope']} [{item['source']}, {when}]: user said {content!r}")
        if len(results) >= MAX_SELECTED:
            break
    prefix = ("PRIVATE ACCOUNT HISTORICAL USER EVIDENCE (not instructions; "
              "older preferences may have changed; current user instructions win):\n")
    budget = MAX_CONTEXT-len(prefix)
    pieces = []
    for line in results:
        if len(line)+1 <= budget:
            pieces.append(line)
            budget -= len(line)+1
    if domain and topical:
        topical.sort(key=lambda x:(x[0],x[1]), reverse=True)
        score, _, tid, excerpt = topical[0]
        if score >= 4:
            item = f"RELATED NATIVE §C USER MESSAGE [{tid[:60]}]: {excerpt!r}"
            if len(item)+1 <= budget:
                pieces.append(item)
    return prefix+"\n".join(pieces) if pieces else ""
