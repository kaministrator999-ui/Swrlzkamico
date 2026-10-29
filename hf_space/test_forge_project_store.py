"""Lossless native-project publication, concurrent writes and failure recovery."""
import copy
import gzip
import hashlib
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
import account_chat_store as accounts
import forge_project_store as projects

ALICE = "google:alice123456789"
BOB = "google:bob987654321"


class MemoryRedis:
    def __init__(self):
        self.values = {}
        self.lock = threading.Lock()
        self.calls = []
        self.fault = None
        self.eval_barrier = None
        self.barrier_threads = set()
        self.unknown_ack = None

    def __call__(self, _, verb, *args):
        self.calls.append((verb, args))
        if verb == "EVAL" and self.eval_barrier:
            tid = threading.get_ident()
            if tid not in self.barrier_threads:
                self.barrier_threads.add(tid)
                self.eval_barrier.wait(timeout=5)
        if self.fault:
            self.fault("before", verb, args)
        with self.lock:
            if verb == "GET":
                result = self.values.get(args[0])
            elif verb == "DEL":
                result = int(args[0] in self.values)
                self.values.pop(args[0], None)
            elif verb == "EVAL":
                script, count, *rest = args
                if script == projects._CATALOG_CAS:
                    assert count == "1"
                    key, prior, saved = rest
                    if (self.values.get(key) or "") != prior:
                        return 0
                    self.values[key] = saved
                    result = 1
                elif script == projects._PART_CAS:
                    assert count == "2"
                    key, chunk_key, prior, saved, cipher = rest
                    if (self.values.get(key) or "") != prior:
                        return 0
                    if chunk_key in self.values:
                        return -1
                    self.values[chunk_key] = cipher
                    self.values[key] = saved
                    result = 1
                else:
                    raise AssertionError("Unknown atomic script")
                if self.unknown_ack is not None:
                    result = self.unknown_ack
            else:
                raise AssertionError("Unexpected storage command " + verb)
        if self.fault:
            self.fault("after", verb, args)
        return result


def native_bytes(text="private geometry", *, extra=None):
    value = {"engine": "§wyrlz", "version": "11.59", "project": {
        "name": "Private native project", "levelPack": {"schema": "se-levels-v1", "levels": [1, 2]},
        "workspaces": {"schema": "swyrl-workspaces-v1", "files": [{"path": "test.js", "text": text}]}},
        "editor": {"layers": [{"id": "layer-a", "hidden": False}], "selection": "actor-a"},
        "scene": {"actors": [{"id": "actor-a", "geometry": text, "position": [1.5, 2, 3]}]}}
    if extra:
        value.update(extra)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class ForgeProjectStoreTest(unittest.TestCase):
    def setUp(self):
        self.redis = MemoryRedis()
        self.config = {"fernet": Fernet.generate_key().decode(), "redis": "https://redis.test",
                       "redis_token": "test-only-token"}
        self.settings_patch = patch.object(accounts.gh, "_settings", return_value=self.config)
        self.redis_patch = patch.object(projects.gh, "_redis", side_effect=self.redis)
        self.settings_patch.start()
        self.redis_patch.start()
        self.addCleanup(self.settings_patch.stop)
        self.addCleanup(self.redis_patch.stop)

    def assert_status(self, code, action):
        with self.assertRaises(HTTPException) as caught:
            action()
        self.assertEqual(caught.exception.status_code, code)
        return caught.exception

    def plan(self, raw=None, *, codec="gzip", project=None, name="Project"):
        raw = native_bytes() if raw is None else raw
        encoded = gzip.compress(raw, mtime=0) if codec == "gzip" else raw
        body = {"name": name, "expectedRevision": project["revision"] if project else 0,
                "codec": codec, "rawBytes": len(raw), "rawSha256": hashlib.sha256(raw).hexdigest(),
                "encodedBytes": len(encoded), "encodedSha256": hashlib.sha256(encoded).hexdigest()}
        if project:
            body["projectId"] = project["id"]
        return body, encoded

    def stage(self, raw=None, *, owner=ALICE, codec="gzip", project=None):
        body, encoded = self.plan(raw, codec=codec, project=project)
        begun = projects.begin_upload(owner, body)
        for index, start in enumerate(range(0, len(encoded), projects.PART_BYTES)):
            receipt = projects.put_part(owner, begun["uploadId"], index, encoded[start:start+projects.PART_BYTES])
            self.assertTrue(receipt["confirmed"])
        return begun, encoded

    def saved(self, raw=None, *, owner=ALICE, project=None):
        upload, _ = self.stage(raw, owner=owner, project=project)
        result = projects.commit_upload(owner, upload["uploadId"])
        self.assertTrue(result["durable"])
        return result["project"]

    def catalog(self, owner=ALICE):
        return projects._catalog(self.config, owner)[1]

    def test_roundtrip_exact_native_bytes_encrypted_and_metadata_only_listing(self):
        raw = native_bytes("literal user text §e\nconst secret = 'keep me';")
        saved = self.saved(raw)
        loaded, metadata = projects.load_project(ALICE, saved["id"])
        self.assertEqual(loaded, raw)
        self.assertEqual(metadata, saved)
        listing = projects.list_projects(ALICE)
        self.assertEqual(listing["projects"], [saved])
        for field in ("scene", "actors", "project", "editor", "codec", "uploadId"):
            self.assertNotIn(field, listing["projects"][0])
        at_rest = str(self.redis.values)
        for private in (ALICE, "literal user text", "Private native project", "keep me", "test-only-token"):
            self.assertNotIn(private, at_rest)
        self.assertNotIn(ALICE, projects._root(ALICE))
        catalog_key = projects._root(ALICE)
        nonce = self.catalog()["projects"][saved["id"]]["uploadId"]
        part_key = projects._chunk_key(ALICE, nonce, 0)
        self.assertEqual(catalog_key.split("{", 1)[1].split("}", 1)[0],
                         part_key.split("{", 1)[1].split("}", 1)[0])

    def test_native_snapshot_larger_than_chat_cap_preserves_geometry_levels_and_workspaces(self):
        # Approximately 70 MiB, including two independent large native fields.
        raw = native_bytes("0123456789" * (7 * 1024 * 1024 // 2))
        self.assertGreater(len(raw), 70_000_000)
        self.assertGreater(len(raw), accounts.CHAT_MAX_RAW)
        saved = self.saved(raw)
        loaded, _ = projects.load_project(ALICE, saved["id"])
        self.assertEqual(hashlib.sha256(loaded).hexdigest(), hashlib.sha256(raw).hexdigest())
        self.assertEqual(loaded, raw)

    def test_identity_multiple_parts_exact_length_and_idempotency(self):
        raw = native_bytes("a" * (projects.PART_BYTES + 30))
        body, encoded = self.plan(raw, codec="identity")
        upload = projects.begin_upload(ALICE, body)
        self.assertGreater(upload["parts"], 1)
        first = encoded[:projects.PART_BYTES]
        self.assert_status(400, lambda: projects.put_part(ALICE, upload["uploadId"], 0, first[:-1]))
        receipt = projects.put_part(ALICE, upload["uploadId"], 0, first)
        self.assertEqual(projects.put_part(ALICE, upload["uploadId"], 0, first), receipt)
        self.assert_status(409, lambda: projects.put_part(ALICE, upload["uploadId"], 0, b"b" * len(first)))
        self.assert_status(409, lambda: projects.commit_upload(ALICE, upload["uploadId"]))
        self.assertEqual(projects.list_projects(ALICE)["projects"], [])
        for index in range(1, upload["parts"]):
            start = index * projects.PART_BYTES
            projects.put_part(ALICE, upload["uploadId"], index, encoded[start:start+projects.PART_BYTES])
        saved = projects.commit_upload(ALICE, upload["uploadId"])["project"]
        self.assertEqual(projects.load_project(ALICE, saved["id"])[0], raw)

    def test_two_owner_isolation_for_project_upload_parts_and_deletion(self):
        saved = self.saved()
        upload, encoded = self.stage()
        self.assertEqual(projects.list_projects(BOB)["projects"], [])
        actions = [lambda: projects.load_project(BOB, saved["id"]),
                   lambda: projects.delete_project(BOB, saved["id"], 1),
                   lambda: projects.put_part(BOB, upload["uploadId"], 0, encoded),
                   lambda: projects.commit_upload(BOB, upload["uploadId"]),
                   lambda: projects.cancel_upload(BOB, upload["uploadId"])]
        for action in actions:
            self.assert_status(404, action)
        self.assertEqual(projects.load_project(ALICE, saved["id"])[1], saved)

    def test_stale_and_concurrent_updates_have_one_winner_without_losing_local_upload(self):
        old = self.saved(native_bytes("old"))
        a, _ = self.stage(native_bytes("new-a"), project=old)
        b, _ = self.stage(native_bytes("new-b"), project=old)
        self.redis.eval_barrier = threading.Barrier(2)
        outcomes = []
        def commit(upload):
            try:
                outcomes.append(projects.commit_upload(ALICE, upload["uploadId"]))
            except HTTPException as exc:
                outcomes.append(exc.status_code)
        workers = [threading.Thread(target=commit, args=(upload,)) for upload in (a, b)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=8)
            self.assertFalse(worker.is_alive())
        self.redis.eval_barrier = None
        self.assertEqual(len([v for v in outcomes if v == 409]), 1)
        winner = next(v["project"] for v in outcomes if isinstance(v, dict))
        self.assertEqual(winner["revision"], 2)
        self.assertEqual(projects.load_project(ALICE, winner["id"])[1], winner)
        self.assertEqual(len(self.catalog()["uploads"]), 1)
        stale, _ = self.plan(project=old)
        self.assert_status(409, lambda: projects.begin_upload(ALICE, stale))
        self.assert_status(409, lambda: projects.delete_project(ALICE, old["id"], 1))

    def test_unknown_atomic_part_outcome_is_indexed_and_safe_to_retry(self):
        body, encoded = self.plan()
        upload = projects.begin_upload(ALICE, body)
        def fail_after_part(phase, verb, args):
            if phase == "after" and verb == "EVAL" and args[0] == projects._PART_CAS:
                raise RuntimeError("private transport details")
        self.redis.fault = fail_after_part
        error = self.assert_status(503, lambda: projects.put_part(ALICE, upload["uploadId"], 0, encoded))
        self.assertNotIn("private transport", error.detail)
        self.redis.fault = None
        self.assertIn("0", self.catalog()["uploads"][upload["uploadId"]]["received"])
        self.assertTrue(projects.put_part(ALICE, upload["uploadId"], 0, encoded)["confirmed"])
        self.assertTrue(projects.commit_upload(ALICE, upload["uploadId"])["durable"])

    def test_unknown_commit_outcome_recovers_receipt_without_second_publication(self):
        old = self.saved(native_bytes("old"))
        upload, _ = self.stage(native_bytes("new"), project=old)
        fired = False
        def fail_once(phase, verb, args):
            nonlocal fired
            if not fired and phase == "after" and verb == "EVAL" and args[0] == projects._CATALOG_CAS:
                fired = True
                raise RuntimeError("timeout after commit")
        self.redis.fault = fail_once
        self.assert_status(503, lambda: projects.commit_upload(ALICE, upload["uploadId"]))
        self.redis.fault = None
        recovered = projects.commit_upload(ALICE, upload["uploadId"])
        self.assertTrue(recovered["durable"])
        self.assertTrue(recovered["alreadyCommitted"])
        self.assertEqual(recovered["project"]["revision"], 2)

    def test_failed_commit_preserves_previous_pointer_and_uncommitted_parts(self):
        raw = native_bytes("old")
        old = self.saved(raw)
        upload, _ = self.stage(native_bytes("new"), project=old)
        before = self.redis.values[projects._root(ALICE)]
        def fail_before(phase, verb, args):
            if phase == "before" and verb == "EVAL":
                raise RuntimeError("private backend failure")
        self.redis.fault = fail_before
        self.assert_status(503, lambda: projects.commit_upload(ALICE, upload["uploadId"]))
        self.redis.fault = None
        self.assertEqual(self.redis.values[projects._root(ALICE)], before)
        self.assertEqual(projects.load_project(ALICE, old["id"])[0], raw)
        self.assertIn(upload["uploadId"], self.catalog()["uploads"])

    def test_cleanup_failure_retains_indexed_journal_and_successful_new_revision(self):
        old = self.saved(native_bytes("old"))
        old_nonce = self.catalog()["projects"][old["id"]]["uploadId"]
        upload, _ = self.stage(native_bytes("new"), project=old)
        def fail_delete(phase, verb, args):
            if phase == "before" and verb == "DEL":
                raise RuntimeError("delete unavailable")
        self.redis.fault = fail_delete
        result = projects.commit_upload(ALICE, upload["uploadId"])
        self.assertTrue(result["durable"])
        self.assertTrue(result["cleanupPending"])
        self.assertIn(old_nonce, self.catalog()["garbage"])
        self.assertEqual(projects.load_project(ALICE, old["id"])[0], native_bytes("new"))
        self.redis.fault = None
        projects._cleanup(self.config, ALICE)
        self.assertEqual(self.catalog()["garbage"], {})
        self.assertNotIn(projects._chunk_key(ALICE, old_nonce, 0), self.redis.values)

    def test_cancel_and_expiry_reclaim_all_planned_parts_without_current_project_loss(self):
        old = self.saved()
        upload, _ = self.stage(native_bytes("cancelled"))
        nonce = upload["uploadId"]
        projects.cancel_upload(ALICE, nonce)
        self.assertNotIn(nonce, self.catalog()["uploads"])
        self.assertNotIn(projects._chunk_key(ALICE, nonce, 0), self.redis.values)
        expiring, encoded = self.stage(native_bytes("expired"))
        with patch.object(projects.time, "time", return_value=expiring["expiresAt"] + 1):
            self.assert_status(410, lambda: projects.put_part(ALICE, expiring["uploadId"], 0, encoded))
            projects._cleanup(self.config, ALICE)
        self.assertNotIn(expiring["uploadId"], self.catalog()["uploads"])
        self.assertEqual(projects.load_project(ALICE, old["id"])[1], old)

    def test_invalid_gzip_hash_native_shape_and_numeric_values_never_publish(self):
        variants = [b'{}', b'{"engine":"e","version":1,"project":{},"editor":{},"scene":{"actors":[]},"x":NaN}',
                    b'{"engine":"e","version":1,"project":{},"editor":{},"scene":{"actors":[]},"x":1e9999}',
                    b'{"engine":"e","engine":"x","version":1,"project":{},"editor":{},"scene":{"actors":[]}}']
        for raw in variants:
            upload, _ = self.stage(raw)
            self.assert_status(400, lambda: projects.commit_upload(ALICE, upload["uploadId"]))
            projects.cancel_upload(ALICE, upload["uploadId"])
        body, encoded = self.plan()
        body["rawSha256"] = "0" * 64
        upload = projects.begin_upload(ALICE, body)
        projects.put_part(ALICE, upload["uploadId"], 0, encoded)
        self.assert_status(400, lambda: projects.commit_upload(ALICE, upload["uploadId"]))
        projects.cancel_upload(ALICE, upload["uploadId"])
        body, encoded = self.plan(native_bytes("a" * 10000))
        body["rawBytes"] = 100
        upload = projects.begin_upload(ALICE, body)
        projects.put_part(ALICE, upload["uploadId"], 0, encoded)
        self.assert_status(413, lambda: projects.commit_upload(ALICE, upload["uploadId"]))
        self.assertEqual(projects.list_projects(ALICE)["projects"], [])

    def test_corrupt_or_missing_part_cannot_replace_previous_revision(self):
        raw = native_bytes("old")
        old = self.saved(raw)
        upload, _ = self.stage(native_bytes("new"), project=old)
        chunk = projects._chunk_key(ALICE, upload["uploadId"], 0)
        self.redis.values[chunk] = "corrupt"
        self.assert_status(503, lambda: projects.commit_upload(ALICE, upload["uploadId"]))
        self.assertEqual(projects.load_project(ALICE, old["id"])[0], raw)
        del self.redis.values[chunk]
        self.assert_status(503, lambda: projects.commit_upload(ALICE, upload["uploadId"]))

    def test_invalid_metadata_and_bounds_do_not_create_uploads(self):
        good, _ = self.plan()
        variants = [{**good, "owner": BOB}, {**good, "name": ""}, {**good, "name": "x\n"},
                    {**good, "name": "\ud800"}, {**good, "expectedRevision": True},
                    {**good, "rawBytes": projects.RAW_MAX + 1}, {**good, "encodedBytes": projects.COMPRESSED_MAX+1},
                    {**good, "rawSha256": "x" * 64}, {**good, "expectedRevision": 2**53-1}]
        for body in variants:
            with self.subTest(body=repr(body)), self.assertRaises(HTTPException):
                projects.begin_upload(ALICE, body)
        self.assertEqual(self.redis.values, {})
        self.assert_status(401, lambda: projects.list_projects("anonymous"))

    def test_catalog_corruption_and_unknown_ack_fail_closed(self):
        old = self.saved()
        key = projects._root(ALICE)
        original = self.redis.values[key]
        data = self.catalog()
        for altered in ("not-json", "[]", json.dumps({"encrypted": "broken"}),
                        projects._encoded_catalog(self.config, {**data, "owner": BOB}),
                        projects._encoded_catalog(self.config, {**data, "receipts": {"a" * 32: 3}})):
            self.redis.values[key] = altered
            self.assert_status(503, lambda: projects.list_projects(ALICE))
            self.assertEqual(self.redis.values[key], altered)
        self.redis.values[key] = original
        for ack in (True, False, 1.0, "OK"):
            self.redis.unknown_ack = ack
            body, _ = self.plan()
            self.assert_status(503, lambda: projects.begin_upload(ALICE, body))
        self.redis.unknown_ack = None
        self.assertEqual(projects.load_project(ALICE, old["id"])[1], old)

    def client(self, *, deny=False, async_callbacks=False):
        app = FastAPI()
        def authenticate(request):
            return ("verified-session", {"id": request.headers.get("x-test-owner")}) if request.headers.get("x-test-owner") else None
        def guard(request):
            if deny:
                return False
            if request.headers.get("origin") != "https://chat.test":
                raise HTTPException(403, "Wrong mutation origin")
        if async_callbacks:
            async def account(request):
                return authenticate(request)
            async def write(request):
                return guard(request)
        else:
            account, write = authenticate, guard
        projects.install(app, account, write)
        return TestClient(app)

    def test_http_authority_typed_json_body_download_and_explicit_deletion(self):
        client = self.client(async_callbacks=True)
        headers = {"x-test-owner": ALICE, "Origin": "https://chat.test"}
        body, encoded = self.plan()
        self.assertEqual(client.get("/api/forge/projects").status_code, 401)
        self.assertEqual(client.post("/api/forge/projects/uploads", json=body).status_code, 401)
        self.assertEqual(client.post("/api/forge/projects/uploads", headers={"x-test-owner": ALICE}, json=body).status_code, 403)
        self.assertEqual(self.client(deny=True).post("/api/forge/projects/uploads", headers=headers, json=body).status_code, 403)
        self.assertEqual(client.post("/api/forge/projects/uploads", headers=headers, content=json.dumps(body)).status_code, 415)
        for raw in ('{"name":"a","name":"b"}', '{bad', '{"rawBytes":NaN}', '{"rawBytes":1e9999}'):
            self.assertEqual(client.post("/api/forge/projects/uploads", headers={**headers,"content-type":"application/json"}, content=raw).status_code, 400)
        upload = client.post("/api/forge/projects/uploads", headers=headers, json=body).json()
        part_url = "/api/forge/projects/uploads/" + upload["uploadId"] + "/parts/0"
        self.assertEqual(client.put(part_url, headers=headers, content=encoded).status_code, 415)
        self.assertEqual(client.put(part_url, headers={**headers,"Content-Type":"application/octet-stream"}, content=encoded).status_code, 200)
        saved = client.post("/api/forge/projects/uploads/"+upload["uploadId"]+"/commit", headers=headers, json={}).json()["project"]
        response = client.get("/api/forge/projects/"+saved["id"], headers=headers)
        self.assertEqual(response.content, native_bytes())
        self.assertEqual(response.headers["X-SWRLZ-Project-SHA256"], saved["rawSha256"])
        self.assertIn("no-store", response.headers["Cache-Control"])
        self.assertEqual(client.delete("/api/forge/projects/"+saved["id"]+"?expectedRevision=2", headers=headers).status_code, 409)
        self.assertEqual(client.delete("/api/forge/projects/"+saved["id"]+"?expectedRevision="+"9"*5000, headers=headers).status_code, 400)
        self.assertEqual(client.delete("/api/forge/projects/"+saved["id"]+"?expectedRevision=1", headers=headers).status_code, 200)
        self.assertEqual(client.get("/api/forge/projects/"+saved["id"], headers=headers).status_code, 404)
        self.assertFalse(any(":part:" in key for key in self.redis.values))


if __name__ == "__main__":
    unittest.main()
