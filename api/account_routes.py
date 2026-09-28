from __future__ import annotations

import os
import re
import time
from dataclasses import asdict, replace
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from api.durable_chat_contract import ConflictError, LoreRecord, MessageRecord, ThreadRecord, UserProfileRecord, new_id
from api.durable_redis_store import DurableStoreUnavailable, RedisRestChatStore
from api.account_proposals import (
    ProposalPolicyError,
    ProposalStateError,
    apply_proposal,
    audit_public,
    decline_proposal,
    edit_proposal,
    normalized_policy_map,
    proposal_public,
    revert_proposal,
    submit_ai_proposal,
)
from api.google_account import (
    AuthenticationError,
    SESSION_COOKIE,
    auth_configured,
    google_client_id,
    issue_session,
    user_id_from_request,
    verify_session,
    verify_google_credential,
)
from swyrlz.interpretation_contract import InterpretationEnvelope, normalize_provenance, presentation_mode_for_request

_ID = re.compile(r"^[A-Za-z0-9._:-]{1,160}$")
_LORE_TYPES = {"USER_FACT", "USER_LORE", "COMPANION_SELF_LORE", "SHARED_LORE"}
_LORE_SCOPES = {"GLOBAL", "PROJECT", "THREAD"}
QUEUE_TOPIC = "swrlz-generation"


def _json_error(status: int, code: str, detail: str):
    return JSONResponse(status_code=status, content={"ok": False, "code": code, "detail": detail})


def _store() -> RedisRestChatStore:
    return RedisRestChatStore.from_env()


def _clean_id(value: Any, prefix: str) -> str:
    text = str(value or "").strip()
    return text if _ID.fullmatch(text) else new_id(prefix)


def _message_public(message: MessageRecord) -> dict[str, Any]:
    return {
        "id": message.message_id,
        "threadId": message.thread_id,
        "role": message.role.lower(),
        "text": message.committed_text,
        "receivedText": message.received_text,
        "provenance": message.provenance,
        "interpretation": message.interpretation,
        "state": message.state.lower(),
        "requestId": message.request_id,
        "createdAt": int(message.created_at * 1000),
        "updatedAt": int(message.updated_at * 1000),
    }


def _thread_public(store: RedisRestChatStore, user_id: str, thread: ThreadRecord, *, messages: bool = True) -> dict[str, Any]:
    value = {
        "id": thread.thread_id,
        "title": thread.title,
        "createdAt": int(thread.created_at * 1000),
        "updatedAt": int(thread.updated_at * 1000),
        "archivedAt": int(thread.archived_at * 1000) if thread.archived_at else None,
    }
    if messages:
        value["messages"] = [_message_public(m) for m in store.list_messages(user_id=user_id, thread_id=thread.thread_id)]
    return value


def _job_public(job) -> dict[str, Any]:
    return {
        "requestId": job.request_id,
        "threadId": job.thread_id,
        "userMessageId": job.user_message_id,
        "assistantMessageId": job.assistant_message_id,
        "state": job.state,
        "lastSeq": job.last_seq,
        "createdAt": int(job.created_at * 1000),
        "updatedAt": int(job.updated_at * 1000),
        "completedAt": int(job.completed_at * 1000) if job.completed_at else None,
    }


def _lore_public(lore: LoreRecord) -> dict[str, Any]:
    return {
        "id": lore.lore_id,
        "title": lore.title,
        "content": lore.content,
        "type": lore.lore_type,
        "source": lore.source,
        "provenance": dict(lore.provenance),
        "confidence": lore.confidence,
        "scope": lore.scope,
        "scopeId": lore.scope_id,
        "authoredBy": lore.authored_by,
        "editable": lore.editable,
        "active": lore.active,
        "version": lore.version,
        "createdAt": int(lore.created_at * 1000),
        "updatedAt": int(lore.updated_at * 1000),
    }


def _validated_lore_fields(body: dict[str, Any], *, current: LoreRecord | None = None) -> dict[str, Any]:
    lore_type = str(body.get("type") or (current.lore_type if current else "")).strip().upper()
    if lore_type not in _LORE_TYPES:
        raise ValueError("unsupported lore type")
    title = str(body.get("title") if "title" in body else (current.title if current else "")).strip()[:120]
    content = str(body.get("content") if "content" in body else (current.content if current else "")).strip()[:24000]
    if not title or not content:
        raise ValueError("lore title and content are required")
    scope = str(body.get("scope") or (current.scope if current else "GLOBAL")).strip().upper()
    if scope not in _LORE_SCOPES:
        raise ValueError("unsupported lore scope")
    scope_id_raw = body.get("scopeId") if "scopeId" in body else (current.scope_id if current else None)
    scope_id = str(scope_id_raw or "").strip() or None
    if scope == "GLOBAL":
        scope_id = None
    elif scope_id is None or not _ID.fullmatch(scope_id):
        raise ValueError("project/thread lore requires a valid scopeId")
    active = bool(body.get("active", current.active if current else True))
    return {"lore_type": lore_type, "title": title, "content": content, "scope": scope, "scope_id": scope_id, "active": active}


def _authenticated(request: Request) -> tuple[RedisRestChatStore, str] | JSONResponse:
    try:
        user_id = user_id_from_request(request)
        return _store(), user_id
    except AuthenticationError as exc:
        return _json_error(401, "ACCOUNT_SESSION_INVALID", str(exc))
    except Exception as exc:
        return _json_error(503, "ACCOUNT_STORE_UNAVAILABLE", str(exc))


async def _enqueue_generation(payload: dict[str, Any], *, request_id: str) -> None:
    from vercel.queue import QueueClient

    region = os.environ.get("SWRLZ_QUEUE_REGION", "iad1").strip() or "iad1"
    queue = QueueClient(region=region)
    await queue.send(QUEUE_TOPIC, payload, idempotency_key=request_id)


def install(server) -> None:
    server.CAPABILITIES["google-account-auth"] = {
        "kind": "identity",
        "ready": auth_configured(),
        "serverVerified": True,
        "identityKey": "google-sub-to-internal-user-id",
    }
    server.CAPABILITIES["durable-user-state"] = {
        "kind": "durable-storage",
        "ready": RedisRestChatStore.configured(),
        "browserLocalStorageAuthoritative": False,
        "backend": "redis-rest",
    }
    server.CAPABILITIES["durable-lore-state"] = {
        "kind": "durable-user-state",
        "ready": RedisRestChatStore.configured(),
        "contract": "swrlz-account-lore-v1",
        "authority": "account-owned-redis-rest",
        "aiWrites": False,
        "proposalProtocol": True,
    }
    server.CAPABILITIES["durable-proposal-state"] = {
        "kind": "durable-user-state",
        "ready": RedisRestChatStore.configured(),
        "contract": "swrlz-account-proposal-v1",
        "authority": "account-owned-redis-rest",
        "browserCanForgeAssistantProposal": False,
        "resolutionActions": ["edit", "approve", "decline", "revert"],
        "policyModes": ["ASK", "AUTO_LOW_RISK", "SESSION_ONLY", "NEVER"],
    }
    def _submit_account_proposal(**kwargs):
        return submit_ai_proposal(_store(), **kwargs)
    server.submit_account_proposal = _submit_account_proposal
    server.CAPABILITIES["detached-generation"] = {
        "kind": "durable-execution",
        "ready": RedisRestChatStore.configured(),
        "queueTopic": QUEUE_TOPIC,
        "clientDisconnectCancels": False,
    }
    server._write_server_state()

    @server.app.get("/api/account/status")
    async def account_status():
        return {
            "ok": True,
            "authConfigured": auth_configured(),
            "storeConfigured": RedisRestChatStore.configured(),
            "googleClientId": google_client_id() or None,
            "sessionCookie": SESSION_COOKIE,
            "detachedGeneration": True,
            "queueTopic": QUEUE_TOPIC,
        }

    @server.app.post("/api/account/google")
    async def account_google(request: Request):
        try:
            body = await request.json()
            verified = verify_google_credential(body.get("credential") if isinstance(body, dict) else "")
            store = _store()
            user, identity = store.resolve_identity(
                provider="google",
                provider_subject=verified.subject,
                email=verified.email,
                email_verified=verified.email_verified,
            )
            profile = store.get_profile(user_id=user.user_id)
            if verified.name and not profile.display_name:
                profile = store.put_profile(replace(profile, display_name=verified.name), expected_version=profile.version)
            response = JSONResponse(
                content={
                    "ok": True,
                    "user": {"id": user.user_id, "displayName": profile.display_name, "email": identity.email, "picture": verified.picture},
                    "profile": asdict(profile),
                }
            )
            response.set_cookie(
                SESSION_COOKIE,
                issue_session(user.user_id, claims={"provider":"google","providerSubject":verified.subject,"email":verified.email,"emailVerified":verified.email_verified,"name":verified.name,"picture":verified.picture,"durable":True}),
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=7 * 24 * 60 * 60,
                path="/",
            )
            return response
        except AuthenticationError as exc:
            return _json_error(401, "GOOGLE_ID_TOKEN_INVALID", str(exc))
        except Exception as exc:
            return _json_error(503, "ACCOUNT_LOGIN_FAILED", f"{type(exc).__name__}: {exc}")

    @server.app.post("/api/account/logout")
    async def account_logout():
        response = JSONResponse(content={"ok": True})
        response.delete_cookie(SESSION_COOKIE, path="/")
        return response

    @server.app.get("/api/account/me")
    async def account_me(request: Request):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            profile = store.get_profile(user_id=user_id)
            session = verify_session(request.cookies.get(SESSION_COOKIE))
            identity = session.get("identity") if isinstance(session.get("identity"), dict) else {}
            return {"ok": True, "user": {"id": user_id, "displayName": profile.display_name or identity.get("name"), "email": identity.get("email"), "picture": identity.get("picture")}, "profile": asdict(profile)}
        except Exception as exc:
            return _json_error(503, "ACCOUNT_READ_FAILED", str(exc))

    @server.app.get("/api/account/state")
    async def account_state(request: Request):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            threads = store.list_threads(user_id=user_id)[:80]
            active = store.list_active_generations(user_id=user_id)
            return {
                "ok": True,
                "profile": asdict(store.get_profile(user_id=user_id)),
                "threads": [_thread_public(store, user_id, t, messages=True) for t in threads],
                "activeGenerations": [_job_public(j) for j in active],
                "authoritative": "server",
            }
        except Exception as exc:
            return _json_error(503, "ACCOUNT_STATE_FAILED", str(exc))

    @server.app.put("/api/account/profile")
    async def account_profile(request: Request):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            body = await request.json()
            current = store.get_profile(user_id=user_id)
            display_name = str(body.get("displayName") or current.display_name or "").strip()[:120] or None
            preferences = body.get("preferences") if isinstance(body.get("preferences"), dict) else current.preferences
            model_preferences = body.get("modelPreferences") if isinstance(body.get("modelPreferences"), dict) else current.model_preferences
            ui_preferences = body.get("uiPreferences") if isinstance(body.get("uiPreferences"), dict) else current.ui_preferences
            companion_profile = body.get("companionProfile") if isinstance(body.get("companionProfile"), dict) else current.companion_profile
            expected = int(body.get("version", current.version))
            saved = store.put_profile(
                UserProfileRecord(
                    user_id=user_id,
                    display_name=display_name,
                    preferences=dict(preferences),
                    model_preferences=dict(model_preferences),
                    ui_preferences=dict(ui_preferences),
                    companion_profile=dict(companion_profile),
                    version=current.version,
                    updated_at=current.updated_at,
                ),
                expected_version=expected,
            )
            return {"ok": True, "profile": asdict(saved)}
        except Exception as exc:
            return _json_error(409 if "version" in str(exc).lower() else 400, "PROFILE_UPDATE_FAILED", str(exc))

    @server.app.get("/api/account/lore")
    async def account_lore_list(request: Request, limit: int = 300):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            records = store.list_lore(user_id=user_id, limit=max(1, min(int(limit), 500)))
            return {"ok": True, "records": [_lore_public(record) for record in records], "contract": "swrlz-account-lore-v1"}
        except Exception as exc:
            return _json_error(503, "LORE_READ_FAILED", str(exc))

    @server.app.post("/api/account/lore")
    async def account_lore_create(request: Request):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            body = await request.json()
            if not isinstance(body, dict):
                raise ValueError("lore payload must be an object")
            fields = _validated_lore_fields(body)
            now = time.time()
            provenance = {"kind": "manual-user", "surface": "chat-settings", "scope": fields["scope"].lower()}
            if fields["scope_id"]:
                provenance["scopeId"] = fields["scope_id"]
            record = LoreRecord(
                lore_id=_clean_id(body.get("loreId"), "lore"),
                user_id=user_id,
                title=fields["title"],
                content=fields["content"],
                lore_type=fields["lore_type"],
                source="user-manual",
                provenance=provenance,
                confidence=1.0,
                scope=fields["scope"],
                scope_id=fields["scope_id"],
                authored_by="USER",
                editable=True,
                active=fields["active"],
                version=1,
                created_at=now,
                updated_at=now,
            )
            saved = store.put_lore(record, expected_version=0)
            return {"ok": True, "record": _lore_public(saved), "contract": "swrlz-account-lore-v1"}
        except ConflictError as exc:
            return _json_error(409, "LORE_CREATE_CONFLICT", str(exc))
        except Exception as exc:
            return _json_error(400, "LORE_CREATE_FAILED", str(exc))

    @server.app.put("/api/account/lore/{lore_id}")
    async def account_lore_update(request: Request, lore_id: str):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            if not _ID.fullmatch(lore_id):
                return _json_error(400, "LORE_ID_INVALID", "invalid lore id")
            current = store.get_lore(user_id=user_id, lore_id=lore_id)
            if current is None:
                return _json_error(404, "LORE_NOT_FOUND", "lore record does not exist")
            if not current.editable:
                return _json_error(403, "LORE_NOT_EDITABLE", "lore record is not editable")
            body = await request.json()
            if not isinstance(body, dict):
                raise ValueError("lore payload must be an object")
            fields = _validated_lore_fields(body, current=current)
            expected = int(body.get("version", current.version))
            updated = replace(
                current,
                title=fields["title"],
                content=fields["content"],
                lore_type=fields["lore_type"],
                scope=fields["scope"],
                scope_id=fields["scope_id"],
                active=fields["active"],
            )
            saved = store.put_lore(updated, expected_version=expected)
            return {"ok": True, "record": _lore_public(saved), "contract": "swrlz-account-lore-v1"}
        except ConflictError as exc:
            return _json_error(409, "LORE_UPDATE_CONFLICT", str(exc))
        except Exception as exc:
            return _json_error(400, "LORE_UPDATE_FAILED", str(exc))

    @server.app.delete("/api/account/lore/{lore_id}")
    async def account_lore_delete(request: Request, lore_id: str, version: int | None = None):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            if not _ID.fullmatch(lore_id):
                return _json_error(400, "LORE_ID_INVALID", "invalid lore id")
            deleted = store.delete_lore(user_id=user_id, lore_id=lore_id, expected_version=version)
            if not deleted:
                return _json_error(404, "LORE_NOT_FOUND", "lore record does not exist")
            return {"ok": True, "deleted": True, "id": lore_id, "contract": "swrlz-account-lore-v1"}
        except ConflictError as exc:
            return _json_error(409, "LORE_DELETE_CONFLICT", str(exc))
        except Exception as exc:
            return _json_error(400, "LORE_DELETE_FAILED", str(exc))

    @server.app.get("/api/account/proposals")
    async def account_proposal_list(request: Request, includeResolved: bool = True, limit: int = 200):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            profile = store.get_profile(user_id=user_id)
            proposals = store.list_proposals(user_id=user_id, limit=max(1, min(int(limit), 500)), include_resolved=bool(includeResolved))
            return {
                "ok": True,
                "contract": "swrlz-account-proposal-v1",
                "policies": normalized_policy_map(profile),
                "proposals": [proposal_public(proposal) for proposal in proposals],
            }
        except Exception as exc:
            return _json_error(503, "PROPOSAL_READ_FAILED", str(exc))

    @server.app.get("/api/account/proposals/{proposal_id}/audit")
    async def account_proposal_audit(request: Request, proposal_id: str):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            if not _ID.fullmatch(proposal_id):
                return _json_error(400, "PROPOSAL_ID_INVALID", "invalid proposal id")
            proposal = store.get_proposal(user_id=user_id, proposal_id=proposal_id)
            if proposal is None:
                return _json_error(404, "PROPOSAL_NOT_FOUND", "proposal does not exist")
            events = store.list_proposal_audit(user_id=user_id, proposal_id=proposal_id)
            return {"ok": True, "proposal": proposal_public(proposal), "events": [audit_public(event) for event in events]}
        except Exception as exc:
            return _json_error(503, "PROPOSAL_AUDIT_FAILED", str(exc))

    @server.app.put("/api/account/proposals/{proposal_id}")
    async def account_proposal_edit(request: Request, proposal_id: str):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            if not _ID.fullmatch(proposal_id):
                return _json_error(400, "PROPOSAL_ID_INVALID", "invalid proposal id")
            body = await request.json()
            if not isinstance(body, dict) or not isinstance(body.get("payload"), dict):
                return _json_error(400, "PROPOSAL_EDIT_INVALID", "payload object is required")
            saved = edit_proposal(
                store,
                user_id=user_id,
                proposal_id=proposal_id,
                payload=body["payload"],
                rationale=str(body.get("rationale")) if "rationale" in body else None,
                expected_version=int(body["version"]) if body.get("version") is not None else None,
            )
            return {"ok": True, "proposal": proposal_public(saved)}
        except ConflictError as exc:
            return _json_error(409, "PROPOSAL_EDIT_CONFLICT", str(exc))
        except (ProposalPolicyError, ProposalStateError, ValueError) as exc:
            return _json_error(400, "PROPOSAL_EDIT_FAILED", str(exc))
        except Exception as exc:
            return _json_error(503, "PROPOSAL_EDIT_FAILED", str(exc))

    @server.app.post("/api/account/proposals/{proposal_id}/approve")
    async def account_proposal_approve(request: Request, proposal_id: str):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            if not _ID.fullmatch(proposal_id):
                return _json_error(400, "PROPOSAL_ID_INVALID", "invalid proposal id")
            saved = apply_proposal(store, user_id=user_id, proposal_id=proposal_id, actor="USER", auto=False)
            return {"ok": True, "proposal": proposal_public(saved)}
        except ConflictError as exc:
            return _json_error(409, "PROPOSAL_APPLY_CONFLICT", str(exc))
        except (ProposalPolicyError, ProposalStateError, ValueError) as exc:
            return _json_error(400, "PROPOSAL_APPROVE_FAILED", str(exc))
        except Exception as exc:
            return _json_error(503, "PROPOSAL_APPROVE_FAILED", str(exc))

    @server.app.post("/api/account/proposals/{proposal_id}/decline")
    async def account_proposal_decline(request: Request, proposal_id: str):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            if not _ID.fullmatch(proposal_id):
                return _json_error(400, "PROPOSAL_ID_INVALID", "invalid proposal id")
            body = await request.json()
            version = int(body.get("version")) if isinstance(body, dict) and body.get("version") is not None else None
            saved = decline_proposal(store, user_id=user_id, proposal_id=proposal_id, expected_version=version)
            return {"ok": True, "proposal": proposal_public(saved)}
        except ConflictError as exc:
            return _json_error(409, "PROPOSAL_DECLINE_CONFLICT", str(exc))
        except (ProposalStateError, ValueError) as exc:
            return _json_error(400, "PROPOSAL_DECLINE_FAILED", str(exc))
        except Exception as exc:
            return _json_error(503, "PROPOSAL_DECLINE_FAILED", str(exc))

    @server.app.post("/api/account/proposals/{proposal_id}/revert")
    async def account_proposal_revert(request: Request, proposal_id: str):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            if not _ID.fullmatch(proposal_id):
                return _json_error(400, "PROPOSAL_ID_INVALID", "invalid proposal id")
            saved = revert_proposal(store, user_id=user_id, proposal_id=proposal_id)
            return {"ok": True, "proposal": proposal_public(saved)}
        except ConflictError as exc:
            return _json_error(409, "PROPOSAL_REVERT_CONFLICT", str(exc))
        except (ProposalStateError, ValueError) as exc:
            return _json_error(400, "PROPOSAL_REVERT_FAILED", str(exc))
        except Exception as exc:
            return _json_error(503, "PROPOSAL_REVERT_FAILED", str(exc))

    @server.app.post("/api/account/thread")
    async def account_thread(request: Request):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            body = await request.json()
            now = time.time()
            thread = ThreadRecord(
                thread_id=_clean_id(body.get("threadId"), "thread"),
                user_id=user_id,
                title=str(body.get("title") or "New conversation").strip()[:120] or "New conversation",
                created_at=now,
                updated_at=now,
            )
            existing = store.get_thread(user_id=user_id, thread_id=thread.thread_id)
            saved = existing or store.put_thread(thread)
            return {"ok": True, "thread": _thread_public(store, user_id, saved)}
        except Exception as exc:
            return _json_error(400, "THREAD_CREATE_FAILED", str(exc))

    @server.app.post("/api/account/import-local")
    async def account_import_local(request: Request):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            body = await request.json()
            threads = body.get("threads") if isinstance(body, dict) else None
            if not isinstance(threads, list):
                return _json_error(400, "IMPORT_INVALID", "threads array is required")
            imported_threads = imported_messages = 0
            for raw_thread in threads[:80]:
                if not isinstance(raw_thread, dict):
                    continue
                thread_id = _clean_id(raw_thread.get("id"), "thread")
                created_ms = int(raw_thread.get("createdAt") or int(time.time() * 1000))
                updated_ms = int(raw_thread.get("updatedAt") or created_ms)
                thread = store.get_thread(user_id=user_id, thread_id=thread_id)
                if thread is None:
                    thread = ThreadRecord(
                        thread_id=thread_id,
                        user_id=user_id,
                        title=str(raw_thread.get("title") or "Imported conversation").strip()[:120],
                        created_at=created_ms / 1000,
                        updated_at=updated_ms / 1000,
                    )
                    store.put_thread(thread)
                    imported_threads += 1
                messages = raw_thread.get("messages")
                if not isinstance(messages, list):
                    continue
                for raw_message in messages[:1000]:
                    if not isinstance(raw_message, dict):
                        continue
                    role = str(raw_message.get("role") or "").upper()
                    if role not in {"USER", "ASSISTANT"}:
                        continue
                    message_id = _clean_id(raw_message.get("id"), "message")
                    if store.get_message(user_id=user_id, message_id=message_id):
                        continue
                    text = str(raw_message.get("text") or "")[:200000]
                    stamp = int(raw_message.get("createdAt") or created_ms) / 1000
                    store.put_message(
                        MessageRecord(
                            message_id=message_id,
                            thread_id=thread_id,
                            user_id=user_id,
                            role=role,
                            received_text=text if role == "USER" else None,
                            committed_text=text,
                            state="COMPLETE",
                            created_at=stamp,
                            updated_at=stamp,
                        )
                    )
                    imported_messages += 1
            return {"ok": True, "importedThreads": imported_threads, "importedMessages": imported_messages}
        except Exception as exc:
            return _json_error(400, "IMPORT_FAILED", str(exc))

    @server.app.post("/api/account/generate")
    async def account_generate(request: Request):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            body = await request.json()
            prompt = str(body.get("prompt") or "").strip()
            if not prompt or len(prompt) > 16000:
                return _json_error(400, "PROMPT_INVALID", "prompt must contain 1..16000 characters")
            thread_id = _clean_id(body.get("threadId"), "thread")
            thread = store.get_thread(user_id=user_id, thread_id=thread_id)
            if thread is None:
                now = time.time()
                thread = store.put_thread(ThreadRecord(thread_id=thread_id, user_id=user_id, title=prompt[:54], created_at=now, updated_at=now))
            request_id = _clean_id(body.get("requestId"), "web")
            provenance = normalize_provenance(body.get("inputProvenance"))
            envelope = InterpretationEnvelope(received_text=prompt, provenance=provenance)
            result = store.create_generation(
                request_id=request_id,
                user_id=user_id,
                thread_id=thread.thread_id,
                received_text=prompt,
                provenance=provenance.to_dict(),
                interpretation=envelope.to_dict().get("interpretation", {}),
            )
            if result.created:
                await _enqueue_generation(
                    {
                        "userId": user_id,
                        "requestId": request_id,
                        "threadId": thread.thread_id,
                        "prompt": prompt,
                        "inputProvenance": provenance.to_dict(),
                        "presentationIntent": presentation_mode_for_request(prompt),
                        "generation": body.get("generation") if isinstance(body.get("generation"), dict) else {},
                        "profileId": str(body.get("profileId") or "AUTO")[:96],
                    },
                    request_id=request_id,
                )
            return {
                "ok": True,
                "created": result.created,
                "thread": _thread_public(store, user_id, thread, messages=False),
                "job": _job_public(result.job),
                "userMessage": _message_public(result.user_message),
                "assistantMessage": _message_public(result.assistant_message),
            }
        except Exception as exc:
            return _json_error(503, "GENERATION_QUEUE_FAILED", f"{type(exc).__name__}: {exc}")

    @server.app.get("/api/account/generation/{request_id}/events")
    async def account_generation_events(request: Request, request_id: str, after: int = 0):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            job = store.get_generation(user_id=user_id, request_id=request_id)
            if job is None:
                return _json_error(404, "GENERATION_NOT_FOUND", "generation does not exist")
            events = store.replay_generation_events(user_id=user_id, request_id=request_id, after_seq=max(0, int(after)))
            return {"ok": True, "job": _job_public(job), "events": [event.payload for event in events]}
        except Exception as exc:
            return _json_error(503, "GENERATION_REPLAY_FAILED", str(exc))

    @server.app.post("/api/account/generation/{request_id}/cancel")
    async def account_generation_cancel(request: Request, request_id: str):
        auth = _authenticated(request)
        if isinstance(auth, JSONResponse):
            return auth
        store, user_id = auth
        try:
            job = store.get_generation(user_id=user_id, request_id=request_id)
            if job is None:
                return _json_error(404, "GENERATION_NOT_FOUND", "generation does not exist")
            if job.state not in {"COMPLETE", "FAILED", "CANCELLED"}:
                job = store.update_generation(replace(job, state="CANCELLED", completed_at=time.time()))
            return {"ok": True, "job": _job_public(job)}
        except Exception as exc:
            return _json_error(503, "GENERATION_CANCEL_FAILED", str(exc))
