"""Controlled HTTP integration of canonical Chat with live §E authority.

Real Station admission, account resolution, message persistence, native lease
checks and event projections run here. Google verification, Redis transport and
model output use deterministic doubles; no real sign-in/editor execution claim.
"""
from __future__ import annotations

import base64
import asyncio
import copy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest import mock

from cryptography.fernet import Fernet
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request as StarletteRequest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import account_chat_store as accounts
import account_profile_store as profiles
import brain_forge
import forge_chat_actions
import forge_embed as embed
import model_router
import station
from test_forge_embed import MemoryRedis, ALICE, BOB, SID, BOB_SID, PARENT, CONTEXT, HOST, CHANNEL, THREAD, PROJECT

BATCH = "d" * 32
RID = "station-forge-123"


class ForgeStationHTTP(unittest.TestCase):
    def setUp(self):
        self.redis = MemoryRedis()
        self.config = {"redis": "https://redis.test", "redis_token": "test-only", "fernet": Fernet.generate_key().decode()}
        self.saved = {}
        self.saved_transitions = []
        self.worker_calls = []
        self.dispatched = []
        self.authorized = []
        self.camera = []
        self.auto_run = True
        self.dispatch_failure = None
        self.batch_binding_update = {}
        self.profile = profiles._defaults()
        self.profile["version"] = 7
        self.profile["display_name"] = "Saved Alice"
        self.patchers = [
            mock.patch.object(station, "_sessions", {}),
            mock.patch.object(station, "_forge_contexts", {}),
            mock.patch.object(accounts, "_config", return_value=self.config),
            mock.patch.object(embed.gh, "_redis", side_effect=self.redis),
            mock.patch.object(embed, "_legacy_authenticate", station._legacy_account_session),
            mock.patch.object(embed, "_diagnostic_hook", self.camera.append),
            mock.patch.object(accounts, "load_chat", side_effect=self.load_chat),
            mock.patch.object(accounts, "save_chat", side_effect=self.save_chat),
            mock.patch.object(profiles, "load_profile", side_effect=lambda owner: copy.deepcopy(self.profile)),
            mock.patch.object(station, "routes", return_value=[SimpleNamespace(model_id="700m", available=True)]),
            mock.patch.object(station._pool, "submit", side_effect=self.submit),
            mock.patch.object(station, "dispatch", side_effect=self.dispatch),
            mock.patch.object(station.project_thread_memory, "load", return_value=None),
            mock.patch.object(station.project_work_registry, "observe", return_value={"overlaps": []}),
            mock.patch.object(station.chatgpt_account_memory, "retrieve", return_value=""),
            mock.patch.object(station.github_connection, "_config", return_value={}),
            mock.patch.object(station.github_connection, "_load", return_value=None),
            mock.patch.object(station, "persist_runtime_diagnostic", side_effect=AssertionError("Unexpected diagnostic persistence")),
            mock.patch("urllib.request.urlopen", side_effect=AssertionError("Unexpected network operation")),
        ]
        for patcher in self.patchers:
            patched = patcher.start()
            if patcher.attribute == "urlopen": self.network = patched
            self.addCleanup(patcher.stop)
        original_authorize = embed.authorize_generation
        def authorize(*args):
            context = original_authorize(*args)
            if context is not None: self.authorized.append(context)
            return context
        patched = mock.patch.object(embed, "authorize_generation", side_effect=authorize)
        patched.start()
        self.addCleanup(patched.stop)
        accounts.save_login(SID, ALICE)
        accounts.save_login(BOB_SID, BOB)
        self.client = TestClient(station.app, base_url=embed.CHAT_ORIGIN)
        self.addCleanup(self.client.close)

    def tearDown(self):
        self.network.assert_not_called()

    def load_chat(self, owner):
        return copy.deepcopy(self.saved.get(owner))

    def save_chat(self, owner, state, expected):
        previous = self.saved.get(owner)
        self.assertEqual(expected, (previous or {}).get("revision", 0))
        # Match account_chat_store.save_chat's canonical persistence surface.
        # Running jobs and trusted contexts are never account history.
        durable = {"revision": state["revision"], "currentId": state["currentId"],
                   "threads": copy.deepcopy(state["threads"]), "ownerGoogleId": owner,
                   "activeGeneration": None}
        json.dumps(durable, allow_nan=False)
        self.saved[owner] = durable
        self.saved_transitions.append(copy.deepcopy(durable))
        return True

    def submit(self, fn, *args):
        self.worker_calls.append((fn, args))
        if self.auto_run:
            return fn(*args)
        return SimpleNamespace(cancel=lambda: False)

    def dispatch(self, model, payload, *generators, forge_context=None):
        self.dispatched.append((model, copy.deepcopy(payload), forge_context))
        if forge_context is not None:
            yield {"type": "FORGE_BATCH_READY", **forge_context.public_binding(),
                   "batchId": BATCH, "token": "sfe1_" + "q" * 43,
                   "hostToken": "sfh1_" + "x" * 43, "receiptNonce": "sfr1_" + "z" * 43,
                   **self.batch_binding_update}
        if self.dispatch_failure:
            raise RuntimeError(self.dispatch_failure)
        yield {"type": "DELTA", "text": "Native receipt confirmed." if forge_context else "Hello!"}
        yield {"type": "COMPLETED", "phase": "COMPLETE"}

    def headers(self, *, token=None, sid=None, origin=embed.CHAT_ORIGIN):
        headers = {"Origin": origin}
        if token: headers["Authorization"] = "Bearer " + token
        if sid: headers["Cookie"] = "swrlz_hf_account=" + sid
        return headers

    def pair(self, *, sid=SID, host=HOST, channel=CHANNEL):
        verifier = "v" * 64
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        binding = {"parentOrigin": PARENT, "hostId": host, "channelId": channel}
        created = self.client.post("/api/forge/embed/pair", json={**binding, "challenge": challenge}, headers=self.headers())
        self.assertEqual(created.status_code, 200, created.text)
        pair_id = created.json()["pairId"]
        approved = self.client.post("/api/forge/embed/pair/approve", json={**binding, "pairId": pair_id}, headers=self.headers(sid=sid))
        self.assertEqual(approved.status_code, 200, approved.text)
        exchanged = self.client.post("/api/forge/embed/pair/exchange", json={"pairId": pair_id, "verifier": verifier, "hostId": host, "channelId": channel}, headers=self.headers())
        self.assertEqual(exchanged.status_code, 200, exchanged.text)
        return exchanged.json()["token"]

    def activate(self, token, *, host=HOST, channel=CHANNEL, context=None):
        context = CONTEXT if context is None else context
        presence = self.client.post("/api/forge/embed/presence", json={"threadId": THREAD, "projectId": PROJECT, "context": context}, headers=self.headers(token=token))
        self.assertEqual(presence.status_code, 200, presence.text)
        activated = self.client.post("/api/forge/embed/host/activate", json={"ticket": presence.json()["ticket"], "visible": True, "threadId": THREAD, "projectId": PROJECT, "hostId": host, "channelId": channel, "context": context}, headers=self.headers(origin=PARENT))
        self.assertEqual(activated.status_code, 200, activated.text)
        return activated.json()

    def send(self, *, token=None, sid=None, lease=None, **extra):
        body = {"requestId": RID, "threadId": THREAD, "messageId": "user-forge", "assistantMessageId": "assistant-forge", "modelId": "700m", "prompt": "Add a wall to the scene", "timeZone": "UTC"}
        if lease: body["forgeLeaseId"] = lease["leaseId"]
        body.update(extra)
        return self.client.post("/api/lalm_station/send", json=body, headers=self.headers(token=token, sid=sid))

    def assert_cancelled(self, context):
        with self.assertRaises(HTTPException) as caught:
            embed.revalidate(context)
        self.assertEqual(caught.exception.status_code, 409)
        self.assertIn("CANCELLED", str(caught.exception.detail))

    def test_account_me_uses_saved_profile_and_embed_owner_over_ambient_cookie(self):
        token = self.pair()
        result = self.client.get("/api/account/me", headers=self.headers(token=token, sid=BOB_SID))
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()["user"]["id"], ALICE["id"])
        self.assertEqual(result.json()["profile"]["version"], 7)
        self.assertEqual(result.json()["profile"]["display_name"], "Saved Alice")
        self.assertTrue(result.json()["saved"])
        invalid = self.client.get("/api/account/me", headers=self.headers(token="sfe1_" + "r" * 43, sid=SID))
        self.assertEqual(invalid.status_code, 401)

    def test_saved_profile_reaches_inference_with_human_and_companion_roles_separate(self):
        self.profile["display_name"] = "  HUMAN_KAMI   Example  "
        self.profile["preferences"]["general"]["personalityProfile"] = "gegd"
        self.profile["preferences"]["profile"].update(communicationStyle="technical", outputStyle="deep", pronouns="they/them")
        self.profile["companion_profile"].update(name="ASSISTANT_DRAGON", warmth="high", directness="direct", humor="low")
        self.profile["model_preferences"].update(effort="deep", responseLength="expanded")
        result = self.send(sid=SID, prompt="Say hello")
        self.assertEqual(result.status_code, 202, result.text)
        _, payload, context = self.dispatched[0]
        self.assertIsNone(context)
        self.assertEqual(payload["profileId"], "gegd")
        self.assertTrue(payload["userProfile"].startswith("Name: HUMAN_KAMI Example\n"))
        self.assertIn('"communicationStyle": "technical"', payload["userProfile"])
        self.assertIn('"outputStyle": "deep"', payload["userProfile"])
        self.assertIn('"effort": "deep"', payload["userProfile"])
        self.assertNotIn("ASSISTANT_DRAGON", payload["userProfile"])
        self.assertIn('"name": "ASSISTANT_DRAGON"', payload["profile"])
        self.assertIn('"warmth": "high"', payload["profile"])
        self.assertIn('"directness": "direct"', payload["profile"])
        self.assertNotIn("HUMAN_KAMI", payload["profile"])
        self.assertIn("no tool authority", payload["profile"])
        self.assertIn("no tool authority", payload["userProfile"])
        self.assertEqual(payload["verifiedAccountDisplayName"], ALICE["displayName"])
        self.assertEqual(station._forge_contexts, {})
        for authority in ("forgeLeaseId", "forgeContext", "googleOwner", "userId", "githubAction"):
            self.assertNotIn(authority, payload)
        durable = json.dumps(self.saved_transitions)
        self.assertNotIn("HUMAN_KAMI", durable)
        self.assertNotIn("ASSISTANT_DRAGON", durable)

    def test_unsaved_profile_does_not_invent_an_explicit_user_name_or_companion_tone(self):
        self.profile["version"] = 0
        # Even a transient unsaved projection must not become explicit saved
        # user/companion instructions merely because an account is recognized.
        self.profile["display_name"] = "UNSAVED_GHOST"
        self.profile["companion_profile"].update(name="UNSAVED_DRAGON", warmth="high")
        result = self.send(sid=SID, prompt="Say hello")
        self.assertEqual(result.status_code, 202, result.text)
        _, payload, context = self.dispatched[0]
        self.assertIsNone(context)
        self.assertEqual(payload["userProfile"], "")
        self.assertEqual(payload["profile"], "")
        self.assertNotIn("UNSAVED_GHOST", json.dumps(payload))
        self.assertNotIn("UNSAVED_DRAGON", json.dumps(payload))
        me = self.client.get("/api/account/me", headers=self.headers(sid=SID))
        self.assertEqual(me.status_code, 200, me.text)
        self.assertFalse(me.json()["saved"])

    def test_chat_frame_ancestors_are_exact_and_login_popup_cannot_be_framed(self):
        expected = {"'self'", "https://huggingface.co", *embed.PARENT_ORIGINS}
        for path in ("/", "/chat/§wyrlz"):
            page = self.client.get(path)
            self.assertEqual(page.status_code, 200, page.text[:100])
            directive = page.headers["Content-Security-Policy"].split(";")[0].split()
            self.assertEqual(directive[0], "frame-ancestors")
            self.assertEqual(set(directive[1:]), expected)
            self.assertNotIn(page.headers.get("X-Frame-Options", "").upper(), ("DENY", "SAMEORIGIN"))
        popup = self.client.get("/forge/login", params={"pairId": "a" * 32})
        self.assertEqual(popup.status_code, 200, popup.text[:100])
        self.assertEqual(popup.headers["Content-Security-Policy"], "frame-ancestors 'none'")
        self.assertEqual(popup.headers["Referrer-Policy"], "no-referrer")

    def test_models_api_preserves_existing_routes_without_a_hidden_editor_model(self):
        with mock.patch.object(station, "routes", side_effect=model_router.routes):
            result = self.client.get("/api/hf/models")
        self.assertEqual(result.status_code, 200, result.text)
        models = result.json()["models"]
        self.assertEqual([item["model_id"] for item in models], ["r39", "stock", "700m", "coder", "compare"])
        self.assertFalse(next(item for item in models if item["model_id"] == "compare")["available"])
        self.assertEqual(next(item for item in models if item["model_id"] == "coder")["checkpoint"], model_router.CODER_CHECKPOINT)
        for item in models:
            self.assertIs(type(item["available"]), bool)
            self.assertEqual(set(item), {"model_id", "label", "available", "checkpoint", "reason"})

    def test_standalone_body_flags_cannot_create_or_replay_editor_authority(self):
        response = self.send(sid=SID, prompt="Say hello", inForge=True, trusted=True,
                             forgeContext={"trusted": True}, forgeActions=[{"op": "sceneactor.add", "prefab": "wall"}],
                             owner=ALICE["id"], userId=ALICE["id"])
        self.assertEqual(response.status_code, 202, response.text)
        self.assertEqual(len(self.dispatched), 1)
        _, payload, context = self.dispatched[0]
        self.assertIsNone(context)
        for field in ("inForge", "trusted", "forgeContext", "forgeActions", "owner", "userId"):
            self.assertNotIn(field, payload)
        self.assertEqual(station._forge_contexts, {})
        snapshot = self.client.get("/api/lalm_station/sync", headers=self.headers(sid=SID)).json()
        self.assertEqual(snapshot["currentThread"]["messages"][-1]["text"], "Hello!")

    def test_cookie_account_cannot_use_even_a_real_embed_lease(self):
        token = self.pair()
        lease = self.activate(token)
        result = self.send(sid=SID, lease=lease)
        self.assertEqual(result.status_code, 401, result.text)
        self.assertEqual(self.worker_calls, [])
        self.assertEqual(self.saved_transitions, [])

    def test_public_batch_projection_is_exact_embed_only_and_never_exported(self):
        token = self.pair()
        other_token = self.pair(host="other_" + "3" * 32, channel="other_" + "4" * 32)
        lease = self.activate(token)
        result = self.send(token=token, lease=lease)
        self.assertEqual(result.status_code, 202, result.text)
        self.assertEqual(len(self.authorized), 1)
        self.assertIs(self.dispatched[0][2], self.authorized[0])
        self.assert_cancelled(self.authorized[0])
        expected_fields = {"type", "leaseId", "threadId", "generationId", "projectId", "batchId", "requestId"}
        own_sync = self.client.get("/api/lalm_station/sync", headers=self.headers(token=token))
        self.assertEqual(own_sync.status_code, 200, own_sync.text)
        own_batches = own_sync.json()["activeGeneration"]["forgeBatches"]
        self.assertEqual(len(own_batches), 1)
        self.assertEqual(set(own_batches[0]), expected_fields)
        own_stream = self.client.get("/api/lalm_station/stream", params={"requestId": RID}, headers=self.headers(token=token))
        self.assertEqual(own_stream.status_code, 200, own_stream.text)
        events = [json.loads(line) for line in own_stream.text.splitlines()]
        self.assertEqual(len([event for event in events if event["type"] == "FORGE_BATCH_READY"]), 1)
        for headers in (self.headers(sid=SID), self.headers(token=other_token)):
            projected = self.client.get("/api/lalm_station/sync", headers=headers)
            self.assertNotIn("forgeBatches", projected.json()["activeGeneration"])
            stream = self.client.get("/api/lalm_station/stream", params={"requestId": RID}, headers=headers)
            self.assertNotIn(BATCH, stream.text)
            self.assertNotIn("\"type\": \"FORGE_BATCH_READY\"", stream.text)
        exported = self.client.get("/api/lalm_station/export", headers=self.headers(token=token))
        self.assertEqual(exported.status_code, 200, exported.text)
        serial = exported.text + json.dumps(self.saved_transitions)
        for secret in (BATCH, lease["leaseId"], token, lease["hostToken"], "receiptNonce", "_seal", "_session_key", "forgeBatches"):
            self.assertNotIn(secret, serial)
        self.assertEqual(self.saved[ALICE["id"]]["threads"][0]["messages"][-1]["text"], "Native receipt confirmed.")

    def test_failed_admission_invalidates_server_context_without_message_write(self):
        token = self.pair()
        lease = self.activate(token)
        result = self.send(token=token, lease=lease, prompt="")
        self.assertEqual(result.status_code, 400, result.text)
        self.assertEqual(len(self.authorized), 1)
        self.assert_cancelled(self.authorized[0])
        self.assertEqual(self.saved_transitions, [])
        self.assertEqual(self.worker_calls, [])

    def test_cancel_invalidates_queued_context_and_already_registered_batch(self):
        self.auto_run = False
        token = self.pair()
        lease = self.activate(token)
        result = self.send(token=token, lease=lease)
        self.assertEqual(result.status_code, 202, result.text)
        context = self.authorized[0]
        batch_id = embed.create_batch(context, [{"op": "sceneactor.add", "prefab": "wall"}])
        result = self.client.post("/api/lalm_station/cancel", json={"requestId": RID}, headers=self.headers(sid=SID))
        self.assertEqual(result.status_code, 200, result.text)
        self.assert_cancelled(context)
        take = self.client.post("/api/forge/embed/host/batches/" + batch_id + "/take", json={"leaseId": lease["leaseId"]}, headers={**self.headers(origin=PARENT), "X-Swrlz-Forge-Host": lease["hostToken"]})
        self.assertEqual(take.status_code, 409, take.text)
        self.assertIn("CANCELLED", take.text)

    def test_worker_failure_invalidates_context_and_cannot_persist_credentials(self):
        token = self.pair()
        lease = self.activate(token)
        self.dispatch_failure = "CONTROLLED_NATIVE_FAILURE"
        result = self.send(token=token, lease=lease)
        self.assertEqual(result.status_code, 202, result.text)
        self.assert_cancelled(self.authorized[0])
        snapshot = self.client.get("/api/lalm_station/sync", headers=self.headers(token=token)).json()
        self.assertEqual(snapshot["activeGeneration"]["terminalType"], "FAILED")
        self.assertNotIn("sfe1_", json.dumps(snapshot))
        self.assertNotIn("sfh1_", json.dumps(snapshot))
        self.assertNotIn("sfr1_", json.dumps(snapshot))

    def test_mismatched_batch_binding_fails_without_projecting_batch(self):
        token = self.pair()
        lease = self.activate(token)
        self.batch_binding_update = {"projectId": "another-project"}
        result = self.send(token=token, lease=lease)
        self.assertEqual(result.status_code, 202, result.text)
        snapshot = self.client.get("/api/lalm_station/sync", headers=self.headers(token=token)).json()
        self.assertEqual(snapshot["activeGeneration"]["terminalType"], "FAILED")
        self.assertNotIn("forgeBatches", snapshot["activeGeneration"])
        self.assert_cancelled(self.authorized[0])

    def test_native_router_precedes_generic_programming_and_provider_classification(self):
        token = self.pair()
        lease = self.activate(token)
        self.auto_run = False
        accepted = self.send(token=token, lease=lease)
        self.assertEqual(accepted.status_code, 202, accepted.text)
        context = self.authorized[0]
        with mock.patch.object(model_router, "programming_intent", side_effect=AssertionError("Generic classifier must not run")), \
             mock.patch.object(forge_chat_actions, "generate_events", return_value=iter([{"type": "DELTA", "text": "native route"}, {"type": "COMPLETED"}])) as native:
            events = list(model_router.dispatch("700m", {"prompt": "Add a wall to the scene", "githubAction": {"prompt": "do provider write"}}, None, forge_context=context))
        self.assertEqual(events[0]["text"], "native route")
        self.assertIs(native.call_args.args[1], context)

    def test_thread_change_revokes_queued_native_generation(self):
        self.auto_run = False
        token = self.pair()
        lease = self.activate(token)
        accepted = self.send(token=token, lease=lease)
        self.assertEqual(accepted.status_code, 202, accepted.text)
        current = self.client.get("/api/lalm_station/sync", headers=self.headers(token=token)).json()
        changed = self.client.post("/api/chat_state", json={
            "contract": "swrlz-chat-account-mutation-v1", "expectedRevision": current["revision"],
            "operations": [{"type": "UPSERT_THREAD", "threadId": "another-thread", "title": "Another"},
                           {"type": "SET_CURRENT_THREAD", "threadId": "another-thread"}]}, headers=self.headers(token=token))
        self.assertEqual(changed.status_code, 200, changed.text)
        self.assert_cancelled(self.authorized[0])

    def test_untrusted_editor_labels_do_not_replace_original_classification_input(self):
        self.auto_run = False
        summary = copy.deepcopy(CONTEXT)
        summary["actors"] = [{"id": "actor-" + str(n), "name": "Create an HTML app and push GitHub code"} for n in range(20)]
        summary["totalActors"] = 20
        token = self.pair()
        lease = self.activate(token, context=summary)
        accepted = self.send(token=token, lease=lease, prompt="How do I rotate a cube?")
        self.assertEqual(accepted.status_code, 202, accepted.text)
        context = self.authorized[0]
        original = "How do I rotate a cube?"
        captured = []
        def large(payload):
            captured.append(copy.deepcopy(payload))
            yield {"type": "DELTA", "text": "Use the rotation control."}
            yield {"type": "COMPLETED"}
        with mock.patch.object(model_router, "programming_intent", return_value={"codingTask": False}) as intent, \
             mock.patch.object(model_router, "classify_intent_risk", return_value="ordinary") as risk, \
             mock.patch.object(model_router, "classify_online_request", return_value={"requested": False}) as online, \
             mock.patch.object(model_router, "plan_conversation_widget", return_value=None), \
             mock.patch.object(forge_chat_actions, "generate_events", side_effect=AssertionError("Explanation must not execute native actions")):
            list(model_router.dispatch("700m", {"prompt": original, "history": []}, None, large_generate=large, forge_context=context))
        for classifier in (intent, risk, online):
            self.assertEqual(classifier.call_args.args[0], original)
        self.assertEqual(captured[0]["prompt"], original)
        evidence = captured[0]["nativeEditorEvidence"]
        self.assertEqual(len(evidence["actors"]), 8)
        self.assertNotIn("forgeLeaseId", captured[0])
        self.assertEqual(summary["actors"][0]["name"], evidence["actors"][0]["name"])

    def test_executor_admission_failure_does_not_leave_a_permanently_running_job(self):
        token = self.pair()
        lease = self.activate(token)
        with mock.patch.object(station._pool, "submit", side_effect=RuntimeError("Executor unavailable")), \
             TestClient(station.app, base_url=embed.CHAT_ORIGIN, raise_server_exceptions=False) as failed_client:
            result = failed_client.post("/api/lalm_station/send", json={"requestId": RID, "threadId": THREAD,
                "modelId": "700m", "prompt": "Add a wall to the scene", "forgeLeaseId": lease["leaseId"]}, headers=self.headers(token=token))
        self.assertIn(result.status_code, (500, 503), result.text)
        self.assert_cancelled(self.authorized[0])
        snapshot = self.client.get("/api/lalm_station/sync", headers=self.headers(token=token)).json()
        generation = snapshot["activeGeneration"]
        self.assertTrue(generation is None or generation.get("terminal"), "Failed executor admission must not leave an eternal QUEUED generation")

    def test_stream_authenticates_only_when_a_new_private_batch_is_projected(self):
        self.auto_run = False
        token = self.pair()
        lease = self.activate(token)
        accepted = self.send(token=token, lease=lease)
        self.assertEqual(accepted.status_code, 202, accepted.text)
        context = self.authorized[0]
        request = StarletteRequest({"type": "http", "method": "GET", "scheme": "https",
            "path": "/api/lalm_station/stream", "query_string": b"", "server": ("kamiloki-swyrlz.hf.space", 443),
            "headers": [(b"origin", embed.CHAT_ORIGIN.encode()), (b"authorization", ("Bearer " + token).encode())]})
        generation = next(iter(station._sessions.values()))["activeGeneration"]
        public = {"type": "FORGE_BATCH_READY", **context.public_binding(), "requestId": RID, "batchId": BATCH}
        cycles = 0
        original_matches = embed.context_request_matches
        with mock.patch.object(embed, "context_request_matches", wraps=original_matches) as matches:
            async def connected():
                nonlocal cycles
                cycles += 1
                if cycles == 3:
                    self.assertEqual(matches.call_count, 0, "Empty queued generations must not poll Redis for event permission")
                    generation["forgeBatches"] = [public]
                elif cycles == 4:
                    self.assertEqual(matches.call_count, 1)
                    generation.update(terminal=True, terminalType="COMPLETE", phase="COMPLETE")
                return False
            async def collect():
                with mock.patch.object(request, "is_disconnected", side_effect=connected):
                    response = await station.stream_generation(request, RID)
                    return [json.loads(line) async for line in response.body_iterator]
            events = asyncio.run(collect())
            self.assertEqual(matches.call_count, 1, "An already sent batch must not trigger another authorization lookup")
        batches = [event for event in events if event["type"] == "FORGE_BATCH_READY"]
        self.assertEqual(batches, [public])
        self.assertTrue(events[-1]["terminal"])


if __name__ == "__main__":
    unittest.main()
