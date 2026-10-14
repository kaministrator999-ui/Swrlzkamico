"""Account-isolated, encrypted, CAS-protected Chat project work hints.

This registry tracks declared work *intent*, not GitHub activity, private
conversation history, approvals, model weights, or a repository lock. It has no
GitHub mutation method and never changes the stage-one capability gate.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from fastapi import HTTPException

import account_chat_store as store
import github_connection as gh

SCHEMA = "swrlz-project-work-intent-v1"
TTL_SECONDS = 90 * 60
MAX_ITEMS = 36
MAX_RETRIES = 4
PATH = re.compile(r"(?<![\w/])(?:[\w§.-]+/){1,7}[\w§.-]+\.(?:py|js|mjs|ts|tsx|jsx|html|css|json|md|kt|java|go|rs)(?!\w)")
START = re.compile(r"\b(?:implement|build|fix|repair|debug|refactor|develop|design|start(?:ed)? working on|work(?:ing)? on|continue working on|improve|review)\b", re.I)
SUBJECT = re.compile(r"\b(?:github|repository|repo|coding|code|inference|model|chat|workstation|project|module|source|file|architecture)\b", re.I)
HYPOTHETICAL = re.compile(r"^\s*(?:should|would|could|what if|imagine|hypothetically)\b", re.I)
CAS = ("local raw=redis.call('GET',KEYS[1]);"
       "local expected=tonumber(ARGV[1]);"
       "if not raw then if expected~=0 then return 0 end;"
       "else local ok,old=pcall(cjson.decode,raw);"
       "if not ok or type(old)~='table' or tonumber(old['revision'])~=expected then return 0 end end;"
       "redis.call('SET',KEYS[1],ARGV[2],'EX',tonumber(ARGV[3])); return 1")


def _key(owner):
    if not store.OWNER.fullmatch(str(owner or "")):
        raise HTTPException(401, "Verified Google identity required")
    return "swrlz:project:work:v1:" + hashlib.sha256(owner.encode("utf-8")).hexdigest()


def _read(config, owner):
    raw = gh._redis(config, "GET", _key(owner))
    if raw is None:
        return 0, []
    try:
        env = json.loads(raw)
        data = store._decrypt(config, env["encrypted"])
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(503, "Project coordination state unreadable") from exc
    if (not isinstance(env, dict) or type(env.get("revision")) is not int
            or not isinstance(data, dict) or data.get("schema") != SCHEMA
            or data.get("owner") != owner or data.get("revision") != env["revision"]
            or not isinstance(data.get("items"), list)):
        raise HTTPException(503, "Project coordination state invalid")
    return env["revision"], data["items"]


def _persist(config, owner, revision, items):
    data = {"schema": SCHEMA, "owner": owner, "revision": revision + 1, "items": items}
    envelope = {"revision": revision + 1, "encrypted": store._encrypt(config, data)}
    outcome = gh._redis(config, "EVAL", CAS, "1", _key(owner),
                        str(revision), json.dumps(envelope, separators=(",", ":")),
                        str(TTL_SECONDS))
    if outcome in (1, "1"):
        return True
    if outcome in (0, "0"):
        return False
    raise HTTPException(503, "Project coordination update not confirmed")


def _paths(value):
    return sorted(set(PATH.findall(str(value or ""))))[:8]


def _keywords(value):
    blocked = {"about", "with", "from", "that", "this", "please", "work", "doing",
               "code", "model", "project", "source", "chat", "files", "have", "into"}
    return {w for w in re.findall(r"[a-z]{5,}", value.lower()) if w not in blocked}


def declared_goal(prompt):
    """A subject mention or exploratory question does not claim active work."""
    prompt = str(prompt or "").strip()
    if (not 12 <= len(prompt) <= 3200 or HYPOTHETICAL.match(prompt)
            or not START.search(prompt) or not SUBJECT.search(prompt)):
        return None
    # Questions asking whether we should do something aren't declarations.
    if re.match(r"^(?:can|may|is it possible|do you think)\b", prompt, re.I):
        return None
    clean = re.sub(r"\s+", " ", prompt)[:220]
    return {"title": clean, "paths": _paths(prompt),
            "keywords": sorted(_keywords(clean))[:16]}


def _current(items, now):
    return [dict(x) for x in items if isinstance(x, dict)
            and x.get("schema") == SCHEMA
            and isinstance(x.get("expiresAt"), int)
            and int(x["expiresAt"]) > now
            and isinstance(x.get("conversationId"), str)
            and isinstance(x.get("repository"), str)][:MAX_ITEMS]


def _relate(item, proposed):
    a, b = set(item.get("paths") or []), set(proposed.get("paths") or [])
    if a and b and a & b:
        return "same-file"
    common = set(item.get("keywords") or []) & set(proposed.get("keywords") or [])
    if len(common) >= 2:
        return "possible-related-goal"
    return None


def observe(owner, conversation_id, repository, prompt, source_sha=""):
    """Register only an explicit scoped work request; return safe other-thread hints.

    No repository write, model assertion of session liveness, or exclusive lock.
    The record is an intent timestamp, with an expiry if the conversation stops.
    """
    proposed = declared_goal(prompt)
    if proposed is None:
        return {"status": "NOT_DECLARED", "overlaps": []}
    if (not gh._REPO.fullmatch(str(repository or ""))
            or not isinstance(conversation_id, str) or not 1 <= len(conversation_id) <= 160):
        return {"status": "SCOPE_UNVERIFIED", "overlaps": []}
    config = store._config()
    now = int(time.time())
    for _ in range(MAX_RETRIES):
        revision, original = _read(config, owner)
        items = _current(original, now)
        overlaps = []
        for item in items:
            if (item["repository"].casefold() != repository.casefold()
                    or item["conversationId"] == conversation_id):
                continue
            relation = _relate(item, proposed)
            if relation:
                overlaps.append({"workItemId": str(item.get("workItemId") or "")[:40],
                                 "title": str(item.get("title") or "")[:150],
                                 "relationship": relation,
                                 "lastObservedAt": item.get("lastObservedAt"),
                                 "sourceSha": str(item.get("sourceSha") or "")[:40]})
        # One bounded intent record per conversation/repository; new project
        # intent replaces that thread's previous active hint, not its history.
        items = [item for item in items if not
                 (item["repository"].casefold() == repository.casefold()
                  and item["conversationId"] == conversation_id)]
        uid = hashlib.sha256((owner + "\0" + repository + "\0" + conversation_id).encode()).hexdigest()[:24]
        items.append({"schema": SCHEMA, "workItemId": uid,
                      "repository": repository, "conversationId": conversation_id,
                      "title": proposed["title"], "paths": proposed["paths"],
                      "keywords": proposed["keywords"],
                      "mode": "read-only-or-design",
                      "status": "DECLARED", "sourceSha": str(source_sha or "")[:40],
                      "lastObservedAt": now, "expiresAt": now + TTL_SECONDS})
        if _persist(config, owner, revision, items[-MAX_ITEMS:]):
            return {"status": "RECORDED", "overlaps": overlaps[:4]}
    raise HTTPException(409, "Project work changed concurrently; retry safely")


def list_work(owner, repository):
    """Show safe summaries of this account's recent declared work only."""
    if not gh._REPO.fullmatch(str(repository or "")):
        raise HTTPException(422, "Verified repository required")
    _revision, entries = _read(store._config(), owner)
    now = int(time.time())
    return [{"workItemId": x["workItemId"], "title": x["title"][:150],
             "repository": x["repository"], "paths": x.get("paths", [])[:8],
             "lastObservedAt": x["lastObservedAt"], "status": "RECENT_DECLARATION"}
            for x in _current(entries, now)
            if x["repository"].casefold() == repository.casefold()]
