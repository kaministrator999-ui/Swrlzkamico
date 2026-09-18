from __future__ import annotations

import hashlib
import json
import threading
import time
from collections.abc import Iterator
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from api.chat_transcript_store import OWNER_ID, STORE

SESSION_TTL_SECONDS = 30 * 60
MAX_SESSION_EVENTS = 4096
TRANSCRIPT_CONTRACT = "generation-transcript-v1"
SHARED_TRANSCRIPT_CONTRACT = "shared-private-blob-v1"
CONTINUITY_HANDOFF = "non-terminal-v1"


def install(chat_extensions) -> None:
    """Detach local R39 generation from one browser stream and share transcript state.

    One worker still owns the active model/KV generation state. Private Blob stores a
    bounded authoritative transcript checkpoint so any worker can answer transcript
    synchronization without starting a duplicate generation. Event replay remains
    local to the generation owner; cross-worker clients synchronize from the shared
    transcript until they reconnect to the owner or the transcript becomes terminal.
    """
    chat = chat_extensions.chat
    base_normalize = chat._normalize_chat_request
    base_stream_response = chat._stream_response

    lock = threading.RLock()
    sessions: dict[str, dict[str, Any]] = {}

    def normalize(payload: dict[str, Any]) -> dict[str, Any]:
        raw_profile = str(payload.get("profileId") or "")[:96]
        normalized = base_normalize(payload)
        normalized_profile = str(normalized.get("profileId") or "")[:96]
        try:
            normalized["resumeAfterSeq"] = max(0, int(payload.get("resumeAfterSeq") or 0))
        except (TypeError, ValueError):
            normalized["resumeAfterSeq"] = 0
        print("SWRLZ_ONLINE_INTENT_CAMERA " + json.dumps({
            "contract": "swrlz-online-intent-camera-v1",
            "stage": "request-normalized",
            "requestId": str(normalized.get("requestId") or ""),
            "rawProfileId": raw_profile,
            "normalizedProfileId": normalized_profile,
            "rawOnlineRequested": chat_extensions.online_research_requested(raw_profile),
            "normalizedOnlineRequested": chat_extensions.online_research_requested(normalized_profile),
            "resumeAfterSeq": int(normalized.get("resumeAfterSeq") or 0),
        }, ensure_ascii=False, separators=(",", ":")))
        return normalized

    def canonical_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in payload.items() if k != "resumeAfterSeq"}

    def online_requested(payload: dict[str, Any]) -> bool:
        # Freeze explicit client intent at admission; reconnects cannot downgrade it.
        return chat_extensions.online_research_requested(payload.get("profileId"))

    def fingerprint(payload: dict[str, Any]) -> str:
        raw = json.dumps(canonical_payload(payload), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def prune() -> None:
        cutoff = time.time() - SESSION_TTL_SECONDS
        with lock:
            stale = [rid for rid, session in sessions.items() if session.get("terminal") and float(session.get("updatedAt") or 0) < cutoff]
            for rid in stale:
                sessions.pop(rid, None)

    def transcript_payload(session: dict[str, Any], *, source: str = "local-worker") -> dict[str, Any]:
        condition: threading.Condition = session["condition"]
        with condition:
            return {
                "ok": True,
                "contract": TRANSCRIPT_CONTRACT,
                "requestId": str(session.get("requestId") or ""),
                "fingerprint": str(session.get("fingerprint") or ""),
                "ownerId": str(session.get("ownerId") or OWNER_ID),
                "text": str(session.get("transcript") or ""),
                "textRevision": int(session.get("textRevision") or 0),
                "lastSeq": int(session.get("lastSeq") or 0),
                "lastDeltaSeq": int(session.get("lastDeltaSeq") or 0),
                "phase": str(session.get("phase") or ""),
                "terminal": bool(session.get("terminal")),
                "terminalType": str(session.get("terminalType") or ""),
                "identity": dict(session.get("identity") or {}),
                "createdAt": float(session.get("createdAt") or 0),
                "updatedAt": float(session.get("updatedAt") or 0),
                "storage": {
                    "contract": SHARED_TRANSCRIPT_CONTRACT,
                    "configured": STORE.configured,
                    "source": source,
                    "private": True,
                    "ownerLocal": str(session.get("ownerId") or OWNER_ID) == OWNER_ID,
                    "lastError": str(session.get("durableError") or ""),
                },
            }

    def durable_snapshot(session: dict[str, Any]) -> dict[str, Any]:
        value = transcript_payload(session, source="durable-checkpoint")
        value["storage"]["source"] = "durable-blob"
        return value

    def checkpoint_worker(session: dict[str, Any]) -> None:
        condition: threading.Condition = session["condition"]
        try:
            while True:
                with condition:
                    if not session.get("durableDirty"):
                        return
                    session["durableDirty"] = False
                try:
                    STORE.write(durable_snapshot(session))
                    with condition:
                        session["durableError"] = ""
                        session["lastDurableWriteAt"] = time.time()
                except Exception as exc:
                    with condition:
                        session["durableError"] = f"{type(exc).__name__}: {exc}"[:300]
                time.sleep(0.12)
        finally:
            with condition:
                session["durableWriteRunning"] = False
                needs_more = bool(session.get("durableDirty"))
            if needs_more:
                schedule_checkpoint(session, force=True)

    def schedule_checkpoint(session: dict[str, Any], *, force: bool = False) -> None:
        if not STORE.configured:
            return
        condition: threading.Condition = session["condition"]
        with condition:
            session["durableDirty"] = True
            elapsed = time.time() - float(session.get("lastDurableWriteAt") or 0)
            if session.get("durableWriteRunning") or (not force and elapsed < 0.30):
                return
            session["durableWriteRunning"] = True
        thread = threading.Thread(target=checkpoint_worker, args=(session,), name=f"swrlz-transcript-checkpoint-{str(session.get('requestId') or '')[-16:]}", daemon=True)
        thread.start()

    def append_event(session: dict[str, Any], event: dict[str, Any]) -> None:
        encoded = chat._encode_event(event)
        condition: threading.Condition = session["condition"]
        with condition:
            seq = int(event["seq"])
            session["events"].append((seq, encoded))
            if len(session["events"]) > MAX_SESSION_EVENTS:
                session["events"] = session["events"][-MAX_SESSION_EVENTS:]
            session["lastSeq"] = seq
            session["updatedAt"] = time.time()
            phase = str(event.get("phase") or "").strip()
            if phase:
                session["phase"] = phase
            if str(event.get("type") or "") == "DELTA":
                text = str(event.get("text") or "")
                if text:
                    session["transcript"] = str(session.get("transcript") or "") + text
                    session["textRevision"] = int(session.get("textRevision") or 0) + 1
                    session["lastDeltaSeq"] = seq
            identity = event.get("identity")
            if isinstance(identity, dict):
                session["identity"] = dict(identity)
            terminal = bool(event.get("terminal"))
            if terminal:
                session["terminal"] = True
                session["terminalType"] = str(event.get("type") or "")
            condition.notify_all()
        schedule_checkpoint(session, force=terminal or str(event.get("type") or "") == "STARTED")

    def run_generation(session: dict[str, Any], payload: dict[str, Any]) -> None:
        request_id = payload["requestId"]
        chat_extensions.LOCAL_CANCELLED.discard(request_id)
        seq = 1
        append_event(session, chat._bridge_event(seq, "STARTED", request_id, phase="ANALYZING_REQUEST", reason="Request admitted by the resumable local R39 generation owner."))
        seq += 1
        try:
            # Preserve the canonical online-research seam when resumable generation owns
            # the local stream. The resumable owner previously bypassed
            # chat_extensions._local_stream(), so +ONLINE reached R39 policy but never
            # executed server-authorized retrieval.
            research_requested = bool(session.get("onlineResearchRequested"))
            # Preserve admitted capability explicitly across the Human -> Brain seam.
            payload = dict(payload)
            payload["onlineResearchRequested"] = research_requested
            if research_requested:
                engine, source = chat_extensions._engine()
                planning_started = time.perf_counter()
                append_event(session, chat._bridge_event(seq, "STATUS", request_id, phase="RESEARCH_PLANNING", reason="Brain is resolving the semantic research target, requested information, constraints and search specificity."))
                seq += 1
                planner = getattr(engine, "plan_research", None)
                if callable(planner):
                    try:
                        # Internal planner control data: never append planner events to the user transcript.
                        print("SWRLZ_BRAIN_RESEARCH_ADAPTER " + json.dumps({"contract":"swrlz-brain-research-adapter-camera-v1","stage":"planner-enter","requestId":request_id,"profileId":str(payload.get("profileId") or "")[:96],"onlineResearchRequested":bool(payload.get("onlineResearchRequested")),"hasOnlineEvidence":bool(payload.get("onlineEvidence"))}, ensure_ascii=False, separators=(",", ":")))
                        plan = planner(payload)
                        print("SWRLZ_BRAIN_RESEARCH_ADAPTER " + json.dumps({"contract":"swrlz-brain-research-adapter-camera-v1","stage":"planner-exit","requestId":request_id,"planType":type(plan).__name__,"queryCandidateCount":len(plan.get("queries", [])) if isinstance(plan, dict) and isinstance(plan.get("queries"), list) else 0}, ensure_ascii=False, separators=(",", ":")))
                    except Exception as exc:
                        plan = {"queries": [str(payload.get("prompt") or "")], "plannerFallback": True, "plannerError": type(exc).__name__}
                else:
                    plan = {"queries": [str(payload.get("prompt") or "")], "plannerFallback": True, "plannerError": "PLAN_RESEARCH_UNAVAILABLE"}
                # Normalize planner output before it crosses the stable retrieval boundary.
                # R39 may return structured/non-string query candidates; retrieval accepts
                # only bounded human-readable query strings. Fall back to the exact prompt.
                raw_queries = plan.get("queries", []) if isinstance(plan, dict) else []
                queries = []
                if isinstance(raw_queries, list):
                    for item in raw_queries:
                        if isinstance(item, str):
                            query = " ".join(item.split())[:500]
                        elif isinstance(item, dict):
                            query = " ".join(str(item.get("query") or item.get("queryText") or item.get("q") or item.get("text") or "").split())[:500]
                        else:
                            query = ""
                        if query and query not in queries:
                            queries.append(query)
                        if len(queries) >= 6:
                            break
                if not queries:
                    requested = " ".join(str(plan.get("requestedInformation") or "").split()) if isinstance(plan, dict) else ""
                    target = " ".join(str(plan.get("target") or "").split()) if isinstance(plan, dict) else ""
                    semantic_fallback = " ".join(part for part in (requested, target) if part).strip()
                    fallback_query = (semantic_fallback or " ".join(str(payload.get("prompt") or "").split()))[:500]
                    queries = [fallback_query] if fallback_query else []
                    if isinstance(plan, dict):
                        plan["plannerFallback"] = True
                        plan["plannerFallbackReason"] = "NO_VALID_STRING_QUERIES"
                if not isinstance(plan, dict):
                    plan = {}
                plan["queries"] = queries
                payload["researchPlan"] = plan
                payload["researchQueries"] = queries
                append_event(session, chat._bridge_event(seq, "STATUS", request_id, phase="RESEARCH_TARGET_RESOLVED", reason=f"Research target resolved in {round((time.perf_counter()-planning_started)*1000)} ms; preparing {len(queries)} bounded query set(s).", categories=["ONLINE_RESEARCH", "SEMANTIC_TARGET_RESOLUTION"]))
                seq += 1
                append_event(session, chat._bridge_event(seq, "STATUS", request_id, phase="QUERY_PLAN_READY", reason=("Search query ready: " + queries[0][:180]) if queries else "Research target resolved, but no safe query text was available.", categories=["ONLINE_RESEARCH", "QUERY_PLAN"]))
                seq += 1
                append_event(session, chat._bridge_event(seq, "STATUS", request_id, phase="SOURCE_FETCH_STARTED", reason="Searching online sources now. Retrieved pages remain untrusted evidence until evaluated."))
                seq += 1
                bundle = chat_extensions.run_online_research(payload)
                payload["onlineEvidence"] = chat_extensions._research_context(bundle)
                reason = f"Retrieved {bundle.get('resultCount', 0)} candidate evidence item(s) across {len(bundle.get('queries', []))} query set(s) in {bundle.get('elapsedMs', 0)} ms."
                append_event(session, chat._bridge_event(seq, "STATUS", request_id, phase="SOURCE_FETCH_COMPLETE", reason=reason, categories=["ONLINE_RESEARCH", "EVIDENCE_UNTRUSTED_EXTERNAL"]))
                seq += 1
                append_event(session, chat._bridge_event(seq, "STATUS", request_id, phase="EVIDENCE_EVALUATION_STARTED", reason="Passing bounded provenance-bearing evidence to the Brain for relevance, authority, freshness, corroboration, conflict evaluation and source-grounded synthesis."))
                seq += 1
            engine, source = chat_extensions._engine()
            evidence = payload.get("onlineEvidence")
            evidence_count = int(evidence.get("resultCount") or 0) if isinstance(evidence, dict) else 0
            print("SWRLZ_BRAIN_RESEARCH_ADAPTER " + json.dumps({"contract":"swrlz-brain-research-adapter-camera-v1","stage":"synthesis-enter","requestId":request_id,"profileId":str(payload.get("profileId") or "")[:96],"onlineResearchRequested":bool(payload.get("onlineResearchRequested")),"hasResearchPlan":bool(payload.get("researchPlan")),"researchQueryCount":len(payload.get("researchQueries", [])) if isinstance(payload.get("researchQueries"), list) else 0,"hasOnlineEvidence":isinstance(evidence, dict),"onlineEvidenceCount":evidence_count,"engineSource":source,"engineRevision":str(getattr(engine, "HOT_REVISION", ""))[:160]}, ensure_ascii=False, separators=(",", ":")))
            source_events = engine.generate_events(payload, lambda: request_id in chat_extensions.LOCAL_CANCELLED)
            try:
                for raw in chat_extensions._heartbeat_events(source_events):
                    if raw.get("type") == "ROUTE":
                        chat_extensions.LOCAL_READINESS.update({
                            "checked": True,
                            "oneTokenReady": True,
                            "interactiveReady": True,
                            "ok": True,
                            "engineId": str(engine.ENGINE_ID),
                            "engineSource": source,
                        })
                    event = chat_extensions._event_payload(seq, request_id, raw)
                    append_event(session, event)
                    seq += 1
                    if event.get("terminal"):
                        return
            except RuntimeError as exc:
                if "StopIteration" not in str(exc):
                    raise
            if not session.get("terminal"):
                append_event(session, chat._bridge_event(seq, "FAILED", request_id, phase="ERROR", reason="The local generation owner ended without a terminal model event.", categories=["LOCAL_GENERATION_ENDED_WITHOUT_TERMINAL"], terminal=True))
        except Exception as exc:
            if not session.get("terminal"):
                append_event(session, chat._bridge_event(seq, "FAILED", request_id, phase="ERROR", reason=f"The local generation owner failed ({type(exc).__name__}).", categories=["LOCAL_GENERATION_OWNER_FAILED"], terminal=True))
        finally:
            chat_extensions.LOCAL_CANCELLED.discard(request_id)
            session["updatedAt"] = time.time()
            schedule_checkpoint(session, force=True)

    def remote_snapshot(request_id: str) -> dict[str, Any] | None:
        try:
            return STORE.read(request_id)
        except Exception:
            return None

    def get_or_start(payload: dict[str, Any]) -> dict[str, Any]:
        prune()
        request_id = payload["requestId"]
        clean = canonical_payload(payload)
        fp = fingerprint(clean)
        with lock:
            existing = sessions.get(request_id)
            if existing is not None:
                if existing.get("fingerprint") != fp:
                    raise chat.BridgeError(409, "REQUEST_ID_REUSE_MISMATCH", "This requestId already owns a different generation payload.")
                return existing
        remote = remote_snapshot(request_id)
        if remote is not None:
            remote_fp = str(remote.get("fingerprint") or "")
            if remote_fp and remote_fp != fp:
                raise chat.BridgeError(409, "REQUEST_ID_REUSE_MISMATCH", "This requestId already owns a different durable generation payload.")
            if str(remote.get("ownerId") or "") != OWNER_ID:
                code = "GENERATION_SESSION_REMOTE_TERMINAL" if remote.get("terminal") else "GENERATION_SESSION_REMOTE_OWNER"
                raise chat.BridgeError(409, code, "This generation is owned by another worker. Synchronize through the shared transcript instead of starting a duplicate generation.")
        with lock:
            existing = sessions.get(request_id)
            if existing is not None:
                return existing
            condition = threading.Condition(threading.RLock())
            now = time.time()
            session: dict[str, Any] = {
                "requestId": request_id,
                "fingerprint": fp,
                "ownerId": OWNER_ID,
                "condition": condition,
                "events": [],
                "lastSeq": 0,
                "lastDeltaSeq": 0,
                "phase": "ANALYZING_REQUEST",
                "transcript": "",
                "textRevision": 0,
                "identity": {},
                "terminal": False,
                "terminalType": "",
                "createdAt": now,
                "updatedAt": now,
                "durableError": "",
                "durableDirty": False,
                "durableWriteRunning": False,
                "lastDurableWriteAt": 0.0,
                "onlineResearchRequested": online_requested(clean),
                "profileId": str(clean.get("profileId") or ""),
            }
            sessions[request_id] = session
            print("SWRLZ_ONLINE_INTENT_CAMERA " + json.dumps({
                "contract": "swrlz-online-intent-camera-v1",
                "stage": "session-admitted",
                "requestId": request_id,
                "profileId": str(session.get("profileId") or ""),
                "onlineResearchRequested": bool(session.get("onlineResearchRequested")),
                "resumeAfterSeq": int(payload.get("resumeAfterSeq") or 0),
            }, ensure_ascii=False, separators=(",", ":")))
        if STORE.configured:
            try:
                STORE.write(durable_snapshot(session))
                session["lastDurableWriteAt"] = time.time()
            except Exception as exc:
                session["durableError"] = f"{type(exc).__name__}: {exc}"[:300]
        thread = threading.Thread(target=run_generation, args=(session, clean), name=f"swrlz-generation-{request_id[-20:]}", daemon=True)
        session["thread"] = thread
        thread.start()
        return session

    def session_stream(session: dict[str, Any], after_seq: int) -> Iterator[bytes]:
        cursor = max(0, int(after_seq))
        condition: threading.Condition = session["condition"]
        while True:
            with condition:
                available = [(seq, encoded) for seq, encoded in session["events"] if seq > cursor]
                terminal = bool(session.get("terminal"))
                last_seq = int(session.get("lastSeq") or 0)
                if not available and not (terminal and cursor >= last_seq):
                    condition.wait(timeout=8.5)
                    continue
            for seq, encoded in available:
                cursor = seq
                yield encoded
            if terminal and cursor >= last_seq:
                return

    def stream_response(payload: dict[str, Any]):
        clean = canonical_payload(payload)
        if chat._raw_upstream_url():
            return base_stream_response(clean)
        after_seq = max(0, int(payload.get("resumeAfterSeq") or 0))
        try:
            session = get_or_start(payload)
        except chat.BridgeError as exc:
            if exc.code in {"GENERATION_SESSION_REMOTE_OWNER", "GENERATION_SESSION_REMOTE_TERMINAL"}:
                response = chat._json_error(exc.status, exc.code, exc.detail)
                response.headers["X-SWRLZ-Continuity-Handoff"] = CONTINUITY_HANDOFF
                response.headers["X-SWRLZ-Generation-Session"] = "resumable-v1"
                response.headers["X-SWRLZ-Transcript-Contract"] = TRANSCRIPT_CONTRACT
                response.headers["X-SWRLZ-Transcript-Storage"] = SHARED_TRANSCRIPT_CONTRACT if STORE.configured else "worker-memory-only"
                return response
            raise
        replay_through = int(session.get("lastSeq") or 0)
        headers = chat._no_store_headers()
        headers.update({
            "X-SWRLZ-Stream-Contract": chat.STREAM_CONTRACT,
            "X-SWRLZ-Request-Id": payload["requestId"],
            "X-SWRLZ-Generation-Session": "resumable-v1",
            "X-SWRLZ-Transcript-Contract": TRANSCRIPT_CONTRACT,
            "X-SWRLZ-Transcript-Storage": SHARED_TRANSCRIPT_CONTRACT if STORE.configured else "worker-memory-only",
            "X-SWRLZ-Resume-After-Seq": str(after_seq),
            "X-SWRLZ-Replay-Through-Seq": str(replay_through),
            "X-Accel-Buffering": "no",
        })
        return StreamingResponse(session_stream(session, after_seq), media_type="application/x-ndjson", headers=headers)

    @chat.app.post("/transcript", include_in_schema=False)
    @chat.app.post("/api/chat/transcript", include_in_schema=False)
    async def transcript_snapshot(request: Request):
        try:
            chat._require_web_token(request)
            payload = await chat._read_json(request)
            request_id = chat._clean_request_id(payload.get("requestId"))
            prune()
            with lock:
                session = sessions.get(request_id)
            if session is not None:
                return JSONResponse(transcript_payload(session), headers=chat._no_store_headers())
            durable = remote_snapshot(request_id)
            if durable is not None:
                durable["ok"] = True
                durable["contract"] = TRANSCRIPT_CONTRACT
                durable.setdefault("storage", {})
                durable["storage"].update({"contract": SHARED_TRANSCRIPT_CONTRACT, "configured": STORE.configured, "source": "durable-blob", "private": True, "ownerLocal": str(durable.get("ownerId") or "") == OWNER_ID})
                return JSONResponse(durable, headers=chat._no_store_headers())
            return chat._json_error(404, "GENERATION_SESSION_NOT_FOUND", "The requested generation transcript is not present in local or shared transcript state.")
        except chat.BridgeError as exc:
            return chat._json_error(exc.status, exc.code, exc.detail)

    chat._normalize_chat_request = normalize
    chat._stream_response = stream_response
    chat_extensions.RESUMABLE_GENERATIONS = sessions
    chat_extensions.RESUMABLE_GENERATION_LOCK = lock
    chat_extensions.RESUMABLE_GENERATION_TTL_SECONDS = SESSION_TTL_SECONDS
    chat_extensions.RESUMABLE_GENERATION_CONTRACT = "resumable-v1"
    chat_extensions.GENERATION_TRANSCRIPT_CONTRACT = TRANSCRIPT_CONTRACT
    chat_extensions.GENERATION_TRANSCRIPT_STORAGE = STORE.describe()
