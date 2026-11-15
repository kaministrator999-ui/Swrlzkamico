"""Bounded, account-owned coding workspace and automatic multi-pass generation.

Generated files are persisted only from complete fenced blocks. A model's terminal
event is not proof that a program compiled or ran. No user code is executed here.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from typing import Any, Callable, Iterable

FENCE = chr(96) * 3
FILE_BLOCK = re.compile(re.escape(FENCE) + r"([^\n]*)\n(.*?)\n?" + re.escape(FENCE), re.S)
FILE_NAME = re.compile(r"(?:^|\s)file=([^\s]+)")
CODE_VERBS = re.compile(r"\b(?:write|create|make|build|generate|implement|code|program|fix|repair|modify|extend|continue|finish|update|add)\b", re.I)
CODE_TARGETS = re.compile(r"\b(?:html|javascript|typescript|python|css|website|webpage|web\s+app|app|source\s+code|script|program|frontend|backend|code|project)\b", re.I)
MAX_FILES = 48
MAX_FILE_CHARS = 180_000
MAX_PROJECT_CHARS = 600_000
WORKSPACE_TTL = 30 * 24 * 3600
CODE_PASSES = max(1, min(int(os.environ.get("SWRLZ_CODE_AUTO_PASSES", "6")), 12))
CODE_TIME_BUDGET = max(30, min(int(os.environ.get("SWRLZ_CODE_TIME_BUDGET_SECONDS", "240")), 900))


def is_code_job(prompt: str, intent: str = "") -> bool:
    if str(intent).upper() in {"CODE", "CODING", "PROJECT"}:
        return True
    prompt = str(prompt or "")
    return bool(CODE_VERBS.search(prompt) and CODE_TARGETS.search(prompt))


def safe_path(raw: str) -> str | None:
    name = str(raw or "").strip().replace("\\", "/")
    if not name or len(name) > 160 or name.startswith("/") or "\x00" in name:
        return None
    parts = name.split("/")
    if any(part in {"", ".", ".."} for part in parts) or ":" in name:
        return None
    return name if re.fullmatch(r"[A-Za-z0-9_./-]+", name) else None


def completed_files(text: str) -> dict[str, str]:
    """Only accept explicit, closed file fences; never synthesize missing code."""
    files: dict[str, str] = {}
    for index, match in enumerate(FILE_BLOCK.finditer(text)):
        header = match.group(1).strip()
        declared = FILE_NAME.search(header)
        language = header.split()[0].lower() if header else ""
        path = safe_path(declared.group(1)) if declared else None
        if path is None and not declared and index == 0:
            path = {"html": "index.html", "css": "styles.css",
                    "javascript": "script.js", "js": "script.js",
                    "python": "main.py", "py": "main.py",
                    "typescript": "index.ts", "ts": "index.ts"}.get(language)
        if not path or not match.group(2).strip():
            continue
        if len(match.group(2)) > MAX_FILE_CHARS:
            continue
        files[path] = match.group(2).rstrip("\n")
        if len(files) >= MAX_FILES:
            break
    # A plain standalone HTML document is a valid single-file artifact too.
    if not files and not text.count(FENCE):
        plain = str(text or "").strip()
        if (re.match(r"(?is)^<!doctype\\s+html\\b|^<html\\b", plain)
                and re.search(r"(?is)</html\\s*>\\s*$", plain)
                and len(plain) <= MAX_FILE_CHARS):
            files["index.html"] = plain
    return files


def output_incomplete(text: str, *, hit_limit: bool) -> bool:
    """Structural incompleteness, not a claim that functional tests passed."""
    code = str(text or "")
    if code.count(FENCE) % 2:
        return True
    if re.search(r"<!doctype\s+html|<html\b", code, re.I) and not re.search(r"</html\s*>", code, re.I):
        return True
    if hit_limit and not completed_files(code):
        return True
    return False


def unique_delta(existing: str, addition: str) -> str:
    """Drop only exact overlapping prefixes (never guess how to rewrite code)."""
    addition = str(addition or "")
    existing = str(existing or "")
    maximum = min(len(existing), len(addition), 2048)
    for size in range(maximum, 19, -1):
        if existing.endswith(addition[:size]):
            return addition[size:]
    return addition


def next_pass_prompt(original: str, assembled: str, guidance: list[str]) -> str:
    tail = assembled[-3500:]
    instructions = "\n".join("- " + line[:1500] for line in guidance[-5:])
    return (
        "Continue the SAME coding task. The source already emitted is canonical: "
        "do not regenerate or repeat it. Produce only the missing suffix, including "
        "any necessary closing tags/fences. Preserve existing functionality. "
        "If guidance changes a completed file, output ONLY that file in a closed "
        "fenced block marked file=path; do not repeat other project files. "
        "No placeholders or fabricated test results.\n"
        "ORIGINAL REQUEST:\n" + original[:1800] +
        "\nCURRENT OUTPUT TAIL (READ-ONLY, DO NOT REPEAT):\n" + tail +
        ("\nNEW USER INSTRUCTIONS:\n" + instructions if instructions else "") +
        "\nCONTINUE FROM THE EXACT END OF THE CURRENT OUTPUT:"
    )


def _key(store: Any, user_id: str, request_id: str) -> str:
    return store._key("coding-workspace-v1", user_id, request_id)


def workspace_snapshot(*, store: Any, user_id: str, request_id: str,
                       thread_id: str = "", include_content: bool = False) -> dict[str, Any]:
    from api.live_code_controls import _owned
    job = _owned(store, user_id, request_id, thread_id)
    raw = store._command("GET", _key(store, user_id, request_id), sensitive=True)
    data = json.loads(raw) if raw else {"version": 0, "files": {}}
    contents = data.get("files") if isinstance(data.get("files"), dict) else {}
    files = {p: (v if include_content else {k: val for k, val in v.items() if k != "content"})
             for p, v in contents.items()}
    return {"requestId": request_id, "threadId": job.thread_id,
            "version": int(data.get("version") or 0), "files": files,
            "validation": "structural-only", "runtimeVerified": False}


def checkpoint_workspace(*, store: Any, user_id: str, request_id: str,
                         thread_id: str, source: str) -> dict[str, Any]:
    """CAS upsert of complete changed files, leaving other files untouched."""
    from api.live_code_controls import _owned
    _owned(store, user_id, request_id, thread_id)
    incoming = completed_files(source)
    if not incoming:
        return {"changed": [], "completeFiles": 0}
    key = _key(store, user_id, request_id)
    script = (
        "local old=redis.call('GET',KEYS[1]) or '' "
        "if old~=ARGV[1] then return 0 end "
        "redis.call('SET',KEYS[1],ARGV[2],'EX',ARGV[3]);return 1"
    )
    for _ in range(5):
        old = store._command("GET", key, sensitive=True) or ""
        data = json.loads(old) if old else {"version": 0, "files": {}}
        files = dict(data.get("files") or {})
        changed = []
        for name, code in incoming.items():
            digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
            if (files.get(name) or {}).get("sha256") == digest:
                continue
            files[name] = {"sha256": digest, "chars": len(code),
                           "content": code, "structuralValid": True}
            changed.append(name)
        if not changed:
            return {"changed": [], "completeFiles": len(files)}
        if len(files) > MAX_FILES or sum(v["chars"] for v in files.values()) > MAX_PROJECT_CHARS:
            return {"changed": [], "completeFiles": len(files), "limit": "WORKSPACE_SIZE_LIMIT"}
        next_value = json.dumps({"version": int(data.get("version", 0)) + 1,
                                 "files": files, "updatedAt": time.time()},
                                ensure_ascii=False, separators=(",", ":"))
        result = store._command("EVAL", script, 1, key, old, next_value,
                                WORKSPACE_TTL, sensitive=True)
        if int(result or 0) == 1:
            return {"changed": changed, "completeFiles": len(files)}
    raise RuntimeError("CODING_WORKSPACE_REVISION_CONFLICT")


def code_generation_events(engine: Any, payload: dict[str, Any],
                           cancelled: Callable[[], bool], *,
                           store: Any, user_id: str, request_id: str,
                           thread_id: str) -> Iterable[dict[str, Any]]:
    """One logical coding job across bounded inference calls and safe checkpoints.

    Callers still own ordered stream events and durable assistant message state.
    Steering is observed between calls; it never mutates a live decode buffer.
    """
    from api import live_code_controls as controls
    original = str(payload.get("prompt") or "")
    emitted = ""
    planned_controls: list[dict[str, Any]] = []
    started = time.monotonic()
    generation = dict(payload.get("generation") or {})
    generation["maxTokens"] = max(512, int(generation.get("maxTokens") or 0))
    task_payload = dict(payload, generation=generation)
    for step in range(CODE_PASSES):
        if cancelled():
            yield {"type": "CANCELLED", "phase": "CANCELLED", "reason": "Coding task cancelled."}
            return
        if time.monotonic() - started >= CODE_TIME_BUDGET:
            yield {"type": "FAILED", "phase": "CODE_BUDGET_EXHAUSTED",
                   "reason": "Coding time budget reached; partial source preserved."}
            return
        yield {"type": "STATUS", "phase": "CODING_PASS",
               "reason": "Coding pass " + str(step + 1) + "/" + str(CODE_PASSES)}
        hit_limit = False
        terminal = None
        pass_output = ""
        for event in engine.generate_events(task_payload, cancelled):
            if not isinstance(event, dict):
                continue
            kind = str(event.get("type") or "")
            phase = str(event.get("phase") or "")
            if phase in {"DECODE_LIMIT_REACHED", "OUTPUT_LIMIT_REACHED"}:
                hit_limit = True
            if kind == "DELTA":
                raw = str(event.get("text") or "")
                addition = unique_delta(emitted, raw) if not pass_output else raw
                emitted += addition
                pass_output += addition
                if addition:
                    yield {**event, "text": addition}
                if len(emitted) > MAX_PROJECT_CHARS:
                    yield {"type": "FAILED", "phase": "CODE_SIZE_LIMIT",
                           "reason": "Coding output limit reached; partial output preserved."}
                    return
            elif kind in {"COMPLETED", "FAILED", "CANCELLED"}:
                terminal = event
                if kind != "COMPLETED":
                    yield event
                    return
            else:
                yield event
        checkpoint = checkpoint_workspace(store=store, user_id=user_id,
                                          request_id=request_id,
                                          thread_id=thread_id, source=emitted)
        if checkpoint.get("limit"):
            yield {"type": "STATUS", "phase": "CODE_WORKSPACE_LIMIT",
                   "reason": str(checkpoint["limit"])}
        if planned_controls and checkpoint.get("changed"):
            for control in planned_controls:
                controls.transition_control(user_id=user_id, request_id=request_id,
                    control_id=control["controlId"],
                    state="REVISION_PRODUCED_UNVERIFIED", store=store)
            planned_controls = []
        pending = [c for c in controls._read_controls(store, user_id, request_id)
                   if c.get("kind") == "STEER" and c.get("state") == "RECORDED_PENDING_EXECUTOR"]
        structurally_incomplete = output_incomplete(emitted, hit_limit=hit_limit)
        if terminal is not None and not structurally_incomplete and not pending and not planned_controls:
            yield terminal
            return
        if step + 1 >= CODE_PASSES:
            yield {"type": "FAILED", "phase": "CODE_INCOMPLETE",
                   "reason": "Automatic coding passes exhausted; partial source and complete file checkpoints are preserved."}
            return
        if pending:
            planned_controls.extend(pending)
            yield {"type": "STATUS", "phase": "CODE_GUIDANCE_RECEIVED",
                   "reason": "Live instructions received; integration is not yet verified."}
        task_payload = dict(task_payload, prompt=next_pass_prompt(
            original, emitted, [str(c.get("text") or "") for c in planned_controls]))
        yield {"type": "STATUS", "phase": "CODE_CONTINUING",
               "reason": "Continuing the same coding job automatically."}
    yield {"type": "FAILED", "phase": "CODE_INCOMPLETE",
           "reason": "Coding task remained incomplete."}
