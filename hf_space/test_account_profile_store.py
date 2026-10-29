"""Encrypted account settings behavior; no network or actual Google login."""
import copy
import json
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.fernet import Fernet
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))
import account_profile_store as profiles
import account_chat_store as storage

ALICE = "google:alice123456789"
BOB = "google:bob987654321"


class MemoryRedis:
    def __init__(self):
        self.values = {}
        self.calls = []
        self.lock = threading.Lock()
        self.read_barrier = None
        self.before_eval = None
        self.eval_reply = None

    def __call__(self, _, verb, *args):
        self.calls.append((verb, args))
        if verb == "GET":
            with self.lock:
                value = self.values.get(args[0])
            if self.read_barrier:
                self.read_barrier.wait(timeout=5)
            return value
        if verb != "EVAL":
            raise AssertionError("Unexpected storage command: " + verb)
        script, count, key, expected, prior, saved, schema = args
        assert count == "1" and script == profiles._CAS and schema == profiles.ENVELOPE_SCHEMA
        if self.before_eval:
            self.before_eval(key)
        if self.eval_reply is not None:
            return self.eval_reply
        with self.lock:
            current = self.values.get(key)
            if current is None:
                if int(expected) != 0 or prior != "":
                    return 0
            elif (current != prior or json.loads(current).get("version") != int(expected)
                  or json.loads(current).get("schema") != schema):
                return 0
            self.values[key] = saved
            return 1


class AccountProfileStoreTest(unittest.TestCase):
    def setUp(self):
        self.redis = MemoryRedis()
        self.config = {"fernet": Fernet.generate_key().decode(), "redis": "https://redis.test",
                       "redis_token": "test-only-token"}
        self.config_patch = patch.object(storage.gh, "_settings", return_value=self.config)
        self.redis_patch = patch.object(storage.gh, "_redis", side_effect=self.redis)
        self.config_patch.start()
        self.redis_patch.start()
        self.addCleanup(self.config_patch.stop)
        self.addCleanup(self.redis_patch.stop)

    def body(self, owner=ALICE):
        return {
            "version": 0, "displayName": " Alice ",
            "preferences": {
                "general": {"enterToSend": False, "personalityProfile": "gegd"},
                "profile": {"pronouns": "they/them", "role": "Engineer", "communicationStyle": "technical", "outputStyle": "deep"},
                "proposalPolicy": {name: "NEVER" for name in profiles.POLICY_CATEGORIES},
            },
            "modelPreferences": {"defaultModel": "coder", "effort": "deep", "responseLength": "expanded"},
            "uiPreferences": {"density": "comfortable", "glass": "low", "motion": "reduced", "fontScale": 1.1,
                              "highContrast": True, "reducedTransparency": True},
            "companionProfile": {"name": "Swyrlz", "title": "Project partner", "form": "Dragon", "pronouns": "they/them",
                                 "warmth": "high", "directness": "direct", "humor": "low", "loreDensity": "minimal"},
        }

    def test_missing_profile_is_full_defaults_without_creating_any_record(self):
        first = profiles.load_profile(ALICE)
        self.assertEqual(first["version"], 0)
        self.assertEqual(first["updated_at"], 0)
        self.assertEqual(first["model_preferences"]["defaultModel"], "700m")
        self.assertEqual(set(first["preferences"]["proposalPolicy"]), set(profiles.POLICY_CATEGORIES))
        first["preferences"]["general"]["enterToSend"] = False
        self.assertTrue(profiles.load_profile(ALICE)["preferences"]["general"]["enterToSend"])
        self.assertEqual(self.redis.values, {})
        self.assertEqual([verb for verb, _ in self.redis.calls], ["GET", "GET"])

    def test_explicit_save_round_trips_every_settings_section_encrypted(self):
        body = self.body()
        original = copy.deepcopy(body)
        saved = profiles.save_profile(ALICE, body)
        self.assertEqual(body, original)
        self.assertEqual(saved["display_name"], "Alice")
        self.assertEqual(saved["version"], 1)
        self.assertGreater(saved["updated_at"], 0)
        expected = copy.deepcopy(original)
        expected["displayName"] = "Alice"
        expected["uiPreferences"]["fontScale"] = "1.1"
        loaded = profiles.load_profile(ALICE)
        self.assertEqual(saved, loaded)
        for name, (target, _) in profiles._INPUT_FIELDS.items():
            self.assertEqual(loaded[target], expected[name])
        raw = str(self.redis.values)
        for private in (ALICE, "Alice", "Engineer", "Project partner", "they/them", "test-only-token"):
            self.assertNotIn(private, raw)
        self.assertNotIn(ALICE, profiles._key(ALICE))
        self.assertEqual(profiles.load_profile(BOB)["version"], 0)
        self.assertEqual(len(self.redis.values), 1)

    def test_partial_updates_preserve_omitted_settings_and_support_explicit_clear(self):
        first = profiles.save_profile(ALICE, self.body())
        second = profiles.save_profile(ALICE, {"version": 1, "displayName": None,
                                               "uiPreferences": {"motion": "off"}})
        self.assertEqual(second["version"], 2)
        self.assertIsNone(second["display_name"])
        self.assertEqual(second["preferences"], first["preferences"])
        self.assertEqual(second["companion_profile"], first["companion_profile"])
        self.assertEqual(second["ui_preferences"], {**first["ui_preferences"], "motion": "off"})

    def test_stale_revisions_do_not_replace_existing_settings(self):
        saved = profiles.save_profile(ALICE, self.body())
        before = dict(self.redis.values)
        for version in (0, 2):
            with self.subTest(version=version), self.assertRaises(HTTPException) as error:
                profiles.save_profile(ALICE, {"version": version, "displayName": "Stale"})
            self.assertEqual(error.exception.status_code, 409)
            self.assertEqual(self.redis.values, before)
        self.assertEqual(profiles.load_profile(ALICE), saved)

    def test_concurrent_first_saves_have_one_atomic_winner(self):
        self.redis.read_barrier = threading.Barrier(2)
        outcomes = []
        def save(name):
            try:
                outcomes.append(profiles.save_profile(ALICE, {"version": 0, "displayName": name}))
            except HTTPException as exc:
                outcomes.append(exc.status_code)
        workers = [threading.Thread(target=save, args=(name,)) for name in ("Browser A", "Browser B")]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=6)
            self.assertFalse(worker.is_alive())
        self.redis.read_barrier = None
        self.assertEqual(len([result for result in outcomes if result == 409]), 1)
        winner = next(result for result in outcomes if isinstance(result, dict))
        self.assertEqual(profiles.load_profile(ALICE), winner)
        self.assertEqual(winner["version"], 1)

    def test_exact_prior_record_is_also_a_cas_precondition(self):
        profiles.save_profile(ALICE, self.body())
        def intervening_change(key):
            envelope = json.loads(self.redis.values[key])
            record = storage._decrypt(self.config, envelope["encrypted"])
            record["profile"]["display_name"] = "Concurrent writer"
            envelope["encrypted"] = storage._encrypt(self.config, record)
            self.redis.values[key] = json.dumps(envelope)
        self.redis.before_eval = intervening_change
        with self.assertRaises(HTTPException) as error:
            profiles.save_profile(ALICE, {"version": 1, "displayName": "Do not overwrite"})
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(profiles.load_profile(ALICE)["display_name"], "Concurrent writer")

    def test_invalid_payloads_are_rejected_without_writes_or_truncation(self):
        cases = [None, [], {}, {"version": True}, {"version": -1}, {"version": "0"},
                 {"version": 0, "owner": BOB}, {"version": 0, "updated_at": 1},
                 {"version": 0, "displayName": "a" * 121},
                 {"version": 0, "preferences": {"general": {"enterToSend": 1}}},
                 {"version": 0, "preferences": {"profile": {"unknown": "ignored?"}}},
                 {"version": 0, "preferences": {"proposalPolicy": {"UNKNOWN": "ASK"}}},
                 {"version": 0, "modelPreferences": {"effort": "unknown"}},
                 {"version": 0, "modelPreferences": {"defaultModel": "compare"}},
                 {"version": 0, "uiPreferences": {"fontScale": True}},
                 {"version": 0, "uiPreferences": {"fontScale": float("nan")}},
                 {"version": 0, "uiPreferences": {"highContrast": "true"}},
                 {"version": 0, "companionProfile": {"name": "a" * 121}},
                 {"version": 0, "displayName": "\ud800"}]
        for body in cases:
            with self.subTest(body=repr(body)), self.assertRaises(HTTPException) as error:
                profiles.save_profile(ALICE, body)
            self.assertEqual(error.exception.status_code, 400)
            self.assertEqual(self.redis.values, {})
        with self.assertRaises(HTTPException) as error:
            profiles.save_profile(ALICE, {"version": 0, "displayName": "a" * (profiles.MAX_BODY_BYTES + 1)})
        self.assertEqual(error.exception.status_code, 413)

    def test_invalid_owner_cannot_select_a_redis_key(self):
        for owner in (None, "", "anonymous", "user_legacy123", "google:../other", "google:x"):
            for operation in (lambda: profiles.load_profile(owner), lambda: profiles.save_profile(owner, {"version": 0})):
                with self.subTest(owner=owner), self.assertRaises(HTTPException) as error:
                    operation()
                self.assertEqual(error.exception.status_code, 401)
        self.assertEqual(self.redis.calls, [])

    def test_corrupted_envelopes_fail_closed_without_defaults_or_rewrites(self):
        profiles.save_profile(ALICE, self.body())
        key = profiles._key(ALICE)
        original = self.redis.values[key]
        outer = json.loads(original)
        record = storage._decrypt(self.config, outer["encrypted"])
        variants = ["not JSON", json.dumps({**outer, "schema": "wrong"}),
                    json.dumps({**outer, "version": True}), json.dumps({**outer, "encrypted": "broken"}),
                    "x" * (profiles.MAX_RECORD_BYTES + 1)]
        for change in (lambda value: value.update(owner=BOB),
                       lambda value: value.update(schema="wrong"),
                       lambda value: value["profile"].update(version=2),
                       lambda value: value["profile"].update(updated_at=False),
                       lambda value: value["profile"]["preferences"].update(unknown=True),
                       lambda value: value["profile"]["ui_preferences"].pop("motion")):
            altered = copy.deepcopy(record)
            change(altered)
            variants.append(json.dumps({**outer, "encrypted": storage._encrypt(self.config, altered)}))
        for raw in variants:
            self.redis.values[key] = raw
            with self.subTest(raw=raw[:45]):
                for operation in (lambda: profiles.load_profile(ALICE),
                                  lambda: profiles.save_profile(ALICE, {"version": 1, "displayName": "Replacement"})):
                    with self.assertRaises(HTTPException) as error:
                        operation()
                    self.assertEqual(error.exception.status_code, 503)
                    self.assertEqual(self.redis.values[key], raw)

    def test_backend_failure_or_unknown_ack_never_claims_a_saved_profile(self):
        profiles.save_profile(ALICE, self.body())
        original = dict(self.redis.values)
        with patch.object(storage.gh, "_redis", side_effect=RuntimeError("private provider details")):
            with self.assertRaises(HTTPException) as error:
                profiles.load_profile(ALICE)
            self.assertEqual(error.exception.status_code, 503)
            self.assertNotIn("private provider details", error.exception.detail)
        for reply in ("OK", True, False, 1.0, 3):
            self.redis.eval_reply = reply
            with self.subTest(reply=reply), self.assertRaises(HTTPException) as error:
                profiles.save_profile(ALICE, {"version": 1, "displayName": "Not confirmed"})
            self.assertEqual(error.exception.status_code, 503)
            self.assertEqual(self.redis.values, original)

    def test_unconfigured_storage_and_invalid_server_time_preserve_state(self):
        with patch.object(storage.gh, "_settings", return_value={}):
            with self.assertRaises(HTTPException) as error:
                profiles.load_profile(ALICE)
            self.assertEqual(error.exception.status_code, 503)
        with patch.object(profiles.time, "time", return_value=float("inf")):
            with self.assertRaises(HTTPException) as error:
                profiles.save_profile(ALICE, {"version": 0})
            self.assertEqual(error.exception.status_code, 503)
        self.assertEqual(self.redis.values, {})

    def client(self, *, async_callbacks=False):
        app = FastAPI()
        def authenticate(request):
            return ("verified", {"id": request.headers.get("x-test-owner")})
        def guard(request):
            if request.headers.get("origin") != "https://chat.test":
                raise HTTPException(403, "Wrong mutation origin")
        if async_callbacks:
            async def account(request):
                return authenticate(request)
            async def write(request):
                return guard(request)
        else:
            account, write = authenticate, guard
        profiles.install(app, account, write)
        return TestClient(app)

    def test_routes_share_authority_and_only_explicit_put_creates_settings(self):
        client = self.client()
        self.assertEqual(client.get("/api/account/profile").status_code, 401)
        headers = {"x-test-owner": ALICE, "Origin": "https://chat.test"}
        response = client.get("/api/account/profile", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["saved"])
        self.assertTrue(response.json()["durable"])
        self.assertIn("no-store", response.headers["cache-control"])
        self.assertEqual(self.redis.values, {})
        denied = client.put("/api/account/profile", headers={"x-test-owner": ALICE}, json={"version": 0})
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(self.redis.values, {})
        response = client.put("/api/account/profile", headers=headers, json=self.body())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["saved"])
        self.assertEqual(response.json()["profile"]["version"], 1)
        self.assertEqual(client.get("/api/account/profile", headers=headers).json()["profile"], response.json()["profile"])
        other = client.get("/api/account/profile", headers={"x-test-owner": BOB})
        self.assertEqual(other.json()["profile"]["version"], 0)

    def test_http_json_types_duplicates_and_byte_bounds_fail_without_write(self):
        client = self.client(async_callbacks=True)
        headers = {"x-test-owner": ALICE, "Origin": "https://chat.test", "Content-Type": "application/json"}
        for raw in ('{"version":0,"version":0}', '{"version":0,"uiPreferences":{"fontScale":NaN}}',
                    '{"version":0,"uiPreferences":{"fontScale":1e9999}}', '[]', '{bad'):
            with self.subTest(raw=raw):
                self.assertEqual(client.put("/api/account/profile", headers=headers, content=raw).status_code, 400)
                self.assertEqual(self.redis.values, {})
        oversized = '{"version":0,"displayName":"' + 'a' * profiles.MAX_BODY_BYTES + '"}'
        self.assertEqual(client.put("/api/account/profile", headers=headers, content=oversized).status_code, 413)
        self.assertEqual(client.put("/api/account/profile", headers={**headers, "Content-Type": "text/plain"}, content='{"version":0}').status_code, 415)
        self.assertEqual(self.redis.values, {})
        self.assertEqual(client.put("/api/account/profile", headers=headers, json={"version": 0}).status_code, 200)


if __name__ == "__main__":
    unittest.main()
