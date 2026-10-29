"""Controlled account/host protocol tests; no network or real Google login."""
import base64
import copy
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

from cryptography.fernet import Fernet
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from starlette.requests import Request as StarletteRequest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import account_chat_store as accounts
import forge_embed as embed

ALICE = {"id": "google:alice12345", "email": "alice@example.test", "displayName": "Alice"}
BOB = {"id": "google:bob987654", "email": "bob@example.test", "displayName": "Bob"}
SID = "a" * 32
BOB_SID = "b" * 32
HOST = "host_" + "1" * 32
CHANNEL = "channel_" + "2" * 32
THREAD = "thread-123"
PROJECT = "3" * 32
PARENT = "https://kamiloki-swrlz-forge-moba.static.hf.space"
CONTEXT = {"projectId": PROJECT, "project": {"name": "Test scene", "kind": "scene"},
           "workspace": "scene", "mode": "edit", "epoch": 1,
           "selectedId": None, "meshes": [], "actors": [], "totalMeshes": 0,
           "totalActors": 0, "canUndo": False, "canRedo": False}


class MemoryRedis:
    def __init__(self):
        self.values = {}
        self.lock = threading.Lock()
        self.force_reply = None
        self.before_eval = None

    def __call__(self, config, verb, *args):
        if verb == "GET":
            with self.lock:
                return self.values.get(args[0])
        if verb == "SET":
            with self.lock:
                self.values[args[0]] = args[1]
            return "OK"
        if verb == "DEL":
            with self.lock:
                return int(self.values.pop(args[0], None) is not None)
        if verb != "EVAL":
            raise AssertionError("Unexpected storage operation")
        script, count, *rest = args
        assert script == embed._TX
        count = int(count)
        keys, arguments = rest[:count], rest[count:]
        expected, writes, deletes = map(json.loads, arguments)
        if self.before_eval:
            self.before_eval(keys)
        if self.force_reply is not None:
            return self.force_reply
        with self.lock:
            for index, prior in expected:
                if self.values.get(keys[index - 1], False) != prior:
                    return 0
            for index, value, ttl in writes:
                assert type(ttl) is int and ttl > 0
                self.values[keys[index - 1]] = value
            for index in deletes:
                self.values.pop(keys[index - 1], None)
        return 1


class ForgeEmbedTest(unittest.TestCase):
    def setUp(self):
        self.clock = 1000.0
        self.redis = MemoryRedis()
        self.config = {"redis": "https://redis.test", "redis_token": "test-token",
                       "fernet": Fernet.generate_key().decode()}
        self.patches = [patch.object(accounts, "_config", return_value=self.config),
                        patch.object(embed.gh, "_redis", side_effect=self.redis),
                        patch.object(embed, "_now", side_effect=lambda: self.clock)]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        accounts.save_login(SID, ALICE)
        accounts.save_login(BOB_SID, BOB)
        self.camera = []
        self.app = FastAPI()
        def legacy(request):
            sid = request.cookies.get("test-login")
            return sid, accounts.load_login(sid)
        embed.install(self.app, legacy, diagnostic_hook=self.camera.append)
        @self.app.get("/test/account")
        def account(request: Request):
            sid, user = embed.resolve_account(request)
            return {"sid": sid, "user": user}
        self.client = TestClient(self.app, base_url=embed.CHAT_ORIGIN)
        self.addCleanup(self.client.close)
        self.addCleanup(lambda: setattr(embed, "_diagnostic_hook", None))

    def post(self, path, body, *, token=None, host_token=None, origin=embed.CHAT_ORIGIN, sid=None):
        headers = {"Origin": origin}
        if token:
            headers["Authorization"] = "Bearer " + token
        if host_token:
            headers["X-Swrlz-Forge-Host"] = host_token
        if sid:
            headers["Cookie"] = "test-login=" + sid
        return self.client.post(path, json=body, headers=headers)

    def pair(self, sid=SID, *, host=HOST, channel=CHANNEL):
        verifier = "v" * 64
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        binding = {"parentOrigin": PARENT, "hostId": host, "channelId": channel}
        created = self.post("/api/forge/embed/pair", {**binding, "challenge": challenge})
        self.assertEqual(created.status_code, 200, created.text)
        pair_id = created.json()["pairId"]
        approved = self.post("/api/forge/embed/pair/approve", {"pairId": pair_id, **binding}, sid=sid)
        self.assertEqual(approved.status_code, 200, approved.text)
        exchanged = self.post("/api/forge/embed/pair/exchange", {"pairId": pair_id, "verifier": verifier,
                              "hostId": host, "channelId": channel})
        self.assertEqual(exchanged.status_code, 200, exchanged.text)
        return exchanged.json()["token"], {"pairId": pair_id, "verifier": verifier, "hostId": host, "channelId": channel}

    def activate(self, token, *, context=CONTEXT, thread=THREAD, project=PROJECT, host=HOST, channel=CHANNEL):
        presence = self.post("/api/forge/embed/presence", {"threadId": thread, "projectId": project,
                             "context": context}, token=token)
        self.assertEqual(presence.status_code, 200, presence.text)
        body = {"ticket": presence.json()["ticket"], "visible": True, "threadId": thread,
                "projectId": project, "hostId": host, "channelId": channel, "context": context}
        activated = self.post("/api/forge/embed/host/activate", body, origin=PARENT)
        self.assertEqual(activated.status_code, 200, activated.text)
        return activated.json(), body

    def request(self, token=None):
        headers = [(b"origin", embed.CHAT_ORIGIN.encode())]
        if token:
            headers.append((b"authorization", ("Bearer " + token).encode()))
        return StarletteRequest({"type": "http", "method": "POST", "path": "/api/station/send", "headers": headers})

    def generation(self):
        token, _ = self.pair()
        lease, _ = self.activate(token)
        context = embed.authorize_generation(self.request(token), lease["leaseId"], THREAD, "generation-1")
        return token, lease, context

    def batch(self, context):
        # Auth tests isolate the native data validator, which has its own real
        # schema/precondition suite. The durable boundary still invokes it.
        with patch("forge_chat_actions.validate_operations", side_effect=lambda ctx, ops: copy.deepcopy(ops)):
            return embed.create_batch(context, [{"op": "fixture.native", "id": "op1"}])

    def take(self, lease, batch_id):
        return self.post(f"/api/forge/embed/host/batches/{batch_id}/take", {"leaseId": lease["leaseId"]},
                         host_token=lease["hostToken"], origin=PARENT)

    def test_pair_is_pkce_bound_single_use_and_owner_cannot_be_claimed(self):
        verifier = "x" * 64
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        binding = {"parentOrigin": PARENT, "hostId": HOST, "channelId": CHANNEL}
        result = self.post("/api/forge/embed/pair", {**binding, "challenge": challenge})
        pair_id = result.json()["pairId"]
        self.assertEqual(result.json()["loginUrl"], "/forge/login?pairId=" + pair_id)
        self.assertEqual(self.post("/api/forge/embed/pair/approve", {"pairId": pair_id, **binding,
                         "owner": BOB["id"]}, sid=SID).status_code, 200)
        exchange = {"pairId": pair_id, "verifier": "y" * 64, "hostId": HOST, "channelId": CHANNEL}
        before = dict(self.redis.values)
        self.assertEqual(self.post("/api/forge/embed/pair/exchange", exchange).status_code, 401)
        self.assertEqual(self.redis.values, before)
        exchange["verifier"] = verifier
        result = self.post("/api/forge/embed/pair/exchange", exchange)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["user"]["id"], ALICE["id"])
        self.assertNotIn("parentSid", result.json())
        self.assertEqual(self.post("/api/forge/embed/pair/exchange", exchange).status_code, 404)
        self.assertTrue(all(ALICE["id"] not in value and SID not in value for value in self.redis.values.values()))

    def test_pair_origin_opener_binding_approval_and_expiry_fail_closed(self):
        for origin in ("https://evil.test", "null", ""):
            self.assertEqual(self.post("/api/forge/embed/pair", {}, origin=origin).status_code, 403)
        self.assertEqual(self.post("/api/forge/embed/pair", {"parentOrigin": "https://evil.test"}).status_code, 403)
        verifier = "z" * 64
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        binding = {"parentOrigin": PARENT, "hostId": HOST, "channelId": CHANNEL}
        pair_id = self.post("/api/forge/embed/pair", {**binding, "challenge": challenge}).json()["pairId"]
        approval = {"pairId": pair_id, **binding}
        self.assertEqual(self.post("/api/forge/embed/pair/approve", approval).status_code, 401)
        self.assertEqual(self.post("/api/forge/embed/pair/approve", {**approval, "channelId": "bad"}, sid=SID).status_code, 403)
        self.assertEqual(self.post("/api/forge/embed/pair/exchange", {"pairId": pair_id, "verifier": verifier,
                         "hostId": HOST, "channelId": CHANNEL}).status_code, 409)
        self.clock += embed.PAIR_TTL + 1
        self.assertEqual(self.client.get("/api/forge/embed/pair/" + pair_id).status_code, 404)

    def test_concurrent_pair_redemptions_have_one_atomic_winner(self):
        verifier = "r" * 64
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        binding = {"parentOrigin": PARENT, "hostId": HOST, "channelId": CHANNEL}
        pair_id = self.post("/api/forge/embed/pair", {**binding, "challenge": challenge}).json()["pairId"]
        self.assertEqual(self.post("/api/forge/embed/pair/approve", {"pairId": pair_id, **binding}, sid=SID).status_code, 200)
        barrier = threading.Barrier(2)
        self.redis.before_eval = lambda keys: barrier.wait(timeout=5)
        body = {"pairId": pair_id, "verifier": verifier, "hostId": HOST, "channelId": CHANNEL}
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _: self.post("/api/forge/embed/pair/exchange", body).status_code, range(2)))
        self.redis.before_eval = None
        self.assertEqual(sorted(outcomes), [200, 409])

    def test_cookie_blocked_embed_account_and_invalid_auth_never_falls_back(self):
        token, _ = self.pair()
        result = self.client.get("/test/account", headers={"Authorization": "Bearer " + token})
        self.assertEqual(result.json()["user"]["id"], ALICE["id"])
        self.assertTrue(result.json()["sid"].startswith("forge:"))
        for auth in ("Bearer sfe1_" + "bad" * 20, "Bearer sfh1_" + "a" * 43, "Basic abc"):
            result = self.client.get("/test/account", headers={"Authorization": auth, "Cookie": "test-login=" + BOB_SID})
            self.assertEqual(result.status_code, 401)
        self.assertEqual(self.client.get("/test/account").json(), {"sid": None, "user": None})
        self.assertEqual(self.client.get("/test/account", headers={"Authorization": "Bearer " + token,
                         "Origin": PARENT}).status_code, 403)

    def test_swapped_encrypted_session_cannot_change_a_bearers_owner(self):
        token, _ = self.pair()
        other_token, _ = self.pair(BOB_SID, host="bob_" + "7" * 32)
        first, second = embed._key("session", token), embed._key("session", other_token)
        self.redis.values[first] = self.redis.values[second]
        result = self.client.get("/test/account", headers={"Authorization": "Bearer " + token})
        self.assertEqual(result.status_code, 503)
        self.assertEqual(result.json()["detail"], "FORGE_STORED_RECORD_INVALID")

    def test_root_logout_and_embed_logout_revoke_live_tools_immediately(self):
        token, lease, context = self.generation()
        accounts.revoke_login(SID)
        with self.assertRaises(HTTPException) as error:
            embed.revalidate(context)
        self.assertEqual(error.exception.detail, "FORGE_PARENT_LOGIN_REVOKED")
        self.assertEqual(self.client.get("/test/account", headers={"Authorization": "Bearer " + token}).status_code, 401)
        accounts.save_login(SID, ALICE)
        self.assertEqual(self.post("/api/forge/embed/logout", {}, token=token).status_code, 200)
        with self.assertRaises(HTTPException):
            embed.revalidate(context)
        self.assertIsNotNone(accounts.load_login(SID))

    def test_presence_requires_exact_host_origin_binding_and_one_use(self):
        token, _ = self.pair()
        presence = self.post("/api/forge/embed/presence", {"threadId": THREAD, "projectId": PROJECT,
                             "context": CONTEXT}, token=token).json()
        body = {"ticket": presence["ticket"], "visible": True, "hostId": HOST, "channelId": CHANNEL,
                "threadId": THREAD, "projectId": PROJECT, "context": CONTEXT}
        for origin in (embed.CHAT_ORIGIN, "https://evil.test", ""):
            self.assertEqual(self.post("/api/forge/embed/host/activate", body, origin=origin).status_code, 403)
        self.assertEqual(self.post("/api/forge/embed/host/activate", {**body, "visible": False}, origin=PARENT).status_code, 403)
        self.assertEqual(self.post("/api/forge/embed/host/activate", {**body, "threadId": "other"}, origin=PARENT).status_code, 403)
        self.assertEqual(self.post("/api/forge/embed/host/activate", body, origin=PARENT).status_code, 200)
        self.assertEqual(self.post("/api/forge/embed/host/activate", body, origin=PARENT).status_code, 401)

    def test_forged_standalone_other_account_and_other_embed_contexts_are_denied(self):
        token, lease, context = self.generation()
        for fake in ({"lease_id": lease["leaseId"], "trusted": True}, None, replace(context, _seal=object())):
            with self.assertRaises(HTTPException) as error:
                embed.revalidate(fake)
            self.assertEqual(error.exception.status_code, 403)
        with self.assertRaises(HTTPException):
            embed.authorize_generation(self.request(), lease["leaseId"], THREAD, "standalone")
        with self.assertRaises(HTTPException):
            embed.authorize_generation(self.request(token), lease["leaseId"], "other-thread", "other-gen")
        other_token, _ = self.pair(BOB_SID, host="bob_" + "4" * 32)
        with self.assertRaises(HTTPException):
            embed.authorize_generation(self.request(other_token), lease["leaseId"], THREAD, "bob-gen")
        same_owner_token, _ = self.pair(host="other_" + "5" * 32)
        self.assertFalse(embed.context_request_matches(self.request(same_owner_token), context))
        self.assertFalse(embed.context_request_matches(self.request(other_token), context))
        self.assertFalse(embed.context_request_matches(self.request(), context))
        self.assertTrue(embed.context_request_matches(self.request(token), context))
        embed.invalidate_generation(context)
        self.assertTrue(embed.context_request_matches(self.request(token), context))
        with self.assertRaises(HTTPException):
            embed.revalidate(context)

    def test_new_presence_thread_project_and_lease_expiry_revoke_old_generation(self):
        token, lease, context = self.generation()
        self.post("/api/forge/embed/presence", {"threadId": "new-thread", "projectId": "new-project", "context": CONTEXT}, token=token)
        with self.assertRaises(HTTPException) as error:
            embed.revalidate(context)
        self.assertEqual(error.exception.detail, "FORGE_LEASE_REVOKED")
        lease2, _ = self.activate(token)
        context2 = embed.authorize_generation(self.request(token), lease2["leaseId"], THREAD, "generation-2")
        self.clock += embed.LEASE_TTL + 1
        with self.assertRaises(HTTPException) as error:
            embed.revalidate(context2)
        self.assertEqual(error.exception.detail, "FORGE_LEASE_EXPIRED")

    def test_heartbeat_freshness_close_and_hidden_host_revoke(self):
        token, lease, context = self.generation()
        heartbeat = {"leaseId": lease["leaseId"], "hostId": HOST, "channelId": CHANNEL,
                     "threadId": THREAD, "projectId": PROJECT, "visible": True, "context": {**CONTEXT, "epoch": 2}}
        self.assertEqual(self.post("/api/forge/embed/host/heartbeat", heartbeat,
                         host_token=lease["hostToken"], origin=PARENT).status_code, 200)
        with self.assertRaises(HTTPException) as error:
            embed.revalidate(context)
        self.assertEqual(error.exception.detail, "FORGE_NATIVE_CONTEXT_STALE")
        embed.revalidate(context, require_snapshot=False)
        self.assertEqual(self.post("/api/forge/embed/host/heartbeat", {**heartbeat, "visible": False},
                         host_token=lease["hostToken"], origin=PARENT).status_code, 409)
        with self.assertRaises(HTTPException):
            embed.revalidate(context, require_snapshot=False)
        lease2, _ = self.activate(token)
        self.assertEqual(self.post("/api/forge/embed/host/close", {"leaseId": lease2["leaseId"]},
                         host_token=lease2["hostToken"], origin=PARENT).status_code, 200)

    def test_batch_receipt_nonce_is_private_single_use_and_actual_failure_is_preserved(self):
        token, lease, context = self.generation()
        batch_id = self.batch(context)
        public = context.public_binding()
        self.assertNotIn("hostToken", public)
        self.assertNotIn("receiptNonce", public)
        taken = self.take(lease, batch_id)
        self.assertEqual(taken.status_code, 200, taken.text)
        nonce = taken.json()["receiptNonce"]
        self.assertEqual(self.take(lease, batch_id).status_code, 409)
        finish = {"leaseId": lease["leaseId"], "receiptNonce": "sfr1_" + "z" * 43,
                  "results": [{"ok": True}], "context": CONTEXT}
        path = f"/api/forge/embed/host/batches/{batch_id}/finish"
        self.assertEqual(self.post(path, finish, host_token=lease["hostToken"], origin=PARENT).status_code, 409)
        finish["receiptNonce"] = nonce
        finish["results"] = [{"ok": False, "code": "NATIVE_TARGET_CHANGED", "token": token,
                              "message": "secret " + nonce + " " + lease["hostToken"]}]
        result = self.post(path, finish, host_token=lease["hostToken"], origin=PARENT)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertFalse(result.json()["allSucceeded"])
        self.assertNotIn(token, result.text)
        self.assertNotIn(nonce, result.text)
        self.assertNotIn(lease["hostToken"], result.text)
        self.assertEqual(self.post(path, finish, host_token=lease["hostToken"], origin=PARENT).status_code, 409)
        waited = embed.wait_batch(context, batch_id, timeout=0)
        self.assertEqual(waited["status"], "finished")
        self.assertFalse(waited["allSucceeded"])

    def test_timeout_cancel_and_native_validation_prevent_late_execution(self):
        token, lease, context = self.generation()
        with patch("forge_chat_actions.validate_operations", side_effect=HTTPException(400, "INVALID_NATIVE_OPERATION")):
            before = dict(self.redis.values)
            with self.assertRaises(HTTPException):
                embed.create_batch(context, [{"op": "eval", "code": "anything"}])
            self.assertEqual(self.redis.values, before)
        batch_id = self.batch(context)
        self.assertEqual(embed.wait_batch(context, batch_id, timeout=0)["status"], "timeout")
        self.assertEqual(self.take(lease, batch_id).status_code, 409)
        self.assertEqual(embed.wait_batch(context, batch_id, timeout=0)["status"], "cancelled")

    def test_batch_take_rejects_stale_snapshot_and_wrong_host_credential(self):
        token, lease, context = self.generation()
        batch_id = self.batch(context)
        self.assertEqual(self.post(f"/api/forge/embed/host/batches/{batch_id}/take", {"leaseId": lease["leaseId"]},
                         host_token="sfh1_" + "z" * 43, origin=PARENT).status_code, 401)
        heartbeat = {"leaseId": lease["leaseId"], "hostId": HOST, "channelId": CHANNEL,
                     "threadId": THREAD, "projectId": PROJECT, "visible": True, "context": {**CONTEXT, "epoch": 2}}
        self.assertEqual(self.post("/api/forge/embed/host/heartbeat", heartbeat,
                         host_token=lease["hostToken"], origin=PARENT).status_code, 200)
        self.assertEqual(self.take(lease, batch_id).status_code, 409)

    def test_only_host_endpoints_expose_narrow_cors_without_cookies(self):
        host = "/api/forge/embed/host/heartbeat"
        result = self.client.options(host, headers={"Origin": PARENT, "Access-Control-Request-Method": "POST",
                                     "Access-Control-Request-Headers": "Content-Type, X-Swrlz-Forge-Host"})
        self.assertEqual(result.status_code, 204)
        self.assertEqual(result.headers["Access-Control-Allow-Origin"], PARENT)
        self.assertNotIn("Access-Control-Allow-Credentials", result.headers)
        for method, headers in (("GET", "Content-Type"), ("POST", "Authorization")):
            self.assertEqual(self.client.options(host, headers={"Origin": PARENT,
                             "Access-Control-Request-Method": method, "Access-Control-Request-Headers": headers}).status_code, 403)
        for path in ("/api/forge/embed/pair", "/test/account"):
            self.assertNotIn("Access-Control-Allow-Origin", self.client.options(path, headers={"Origin": PARENT}).headers)

    def test_safe_json_bounds_and_unknown_transaction_ack_never_claim_success(self):
        for value in ({"token": "private"}, {"__proto__": {}}, {"number": float("nan")},
                      {"number": 10 ** 1000}, {"text": "\ud800"}, {"items": list(range(513))}):
            with self.subTest(value=repr(value)[:60]), self.assertRaises(HTTPException):
                embed._safe_json(value)
        for reply in (True, False, 1.0, 0.0, "OK", 3):
            self.redis.force_reply = reply
            with self.subTest(reply=repr(reply)), self.assertRaises(HTTPException) as error:
                embed._new("fixture", "record", {"schema": embed.SCHEMA, "expiresAt": 2000}, 10)
            self.assertEqual(error.exception.status_code, 503)

    def test_camera_is_bounded_secret_free_and_failures_have_no_authority_effect(self):
        token, lease, context = self.generation()
        batch_id = self.batch(context)
        taken = self.take(lease, batch_id)
        self.assertEqual(taken.status_code, 200)
        raw = json.dumps(self.camera)
        for private in (token, lease["hostToken"], taken.json()["receiptNonce"], SID,
                        ALICE["id"], ALICE["email"], CONTEXT["project"]["name"]):
            self.assertNotIn(private, raw)
        self.assertTrue(any(event["event"] == "batch.taken" for event in self.camera))
        with patch.object(embed, "_diagnostic_hook", side_effect=RuntimeError("camera unavailable")):
            self.assertEqual(self.post("/api/forge/embed/host/close", {"leaseId": lease["leaseId"]},
                             host_token=lease["hostToken"], origin=PARENT).status_code, 200)
        with patch.object(embed, "_diagnostic_hook", None):
            self.assertEqual(self.post("/api/forge/embed/pair", {}, origin="https://evil.test").status_code, 403)


if __name__ == "__main__":
    unittest.main()
