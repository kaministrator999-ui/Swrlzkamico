from __future__ import annotations

import os
import re
import time
from dataclasses import asdict, replace
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from api.durable_chat_contract import MessageRecord, ThreadRecord, UserProfileRecord, new_id
from api.durable_redis_store import DurableStoreUnavailable, RedisRestChatStore
from api.google_account import (
    AuthenticationError,
    SESSION_COOKIE,
    auth_configured,
    google_client_id,
    issue_session,
    user_id_from_request,
    verify_google_credential,
)
from swyrlz.interpretation_contract import InterpretationEnvelope, normalize_provenance, presentation_mode_for_request

_ID = re.compile(r"^[A-Za-z0-9._:-]{1,160}$")
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
                issue_session(user.user_id),
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
            return {"ok": True, "user": {"id": user_id, "displayName": profile.display_name}, "profile": asdict(profile)}
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
            expected = int(body.get("version", current.version))
            saved = store.put_profile(
                UserProfileRecord(
                    user_id=user_id,
                    display_name=display_name,
                    preferences=dict(preferences),
                    model_preferences=dict(model_preferences),
                    ui_preferences=dict(ui_preferences),
                    version=current.version,
                    updated_at=current.updated_at,
                ),
                expected_version=expected,
            )
            return {"ok": True, "profile": asdict(saved)}
        except Exception as exc:
            return _json_error(409 if "version" in str(exc).lower() else 400, "PROFILE_UPDATE_FAILED", str(exc))

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
