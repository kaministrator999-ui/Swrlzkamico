"""Contract tests for first-read account migration without external dependencies."""
import ast
import json
from pathlib import Path
import unittest

tree = ast.parse((Path(__file__).resolve().parents[1] / "api/chat_state.py").read_text())
functions = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef)
                             and node.name in {"_read_state", "_validated_redis_state"}], type_ignores=[])


class Redis:
    def __init__(self, raw=None):
        self.raw = raw
        self.calls = []
        self.failure = None

    def _command(self, name, *args):
        self.calls.append(name)
        if self.failure:
            raise self.failure
        if name == "GET":
            return self.raw
        if name == "SET":
            assert args[2] == "NX"
            if self.raw is None:
                self.raw = args[1]
            return "OK"
        raise AssertionError(name)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.record = {"contract": "swrlz-chat-account-state-v1", "userId": "user", "revision": 1}
        self.redis = Redis()
        self.blob_calls = 0
        self.candidates = [("token", "store", "read")]
        self.legacy = self.record
        def read_blob(_user):
            self.blob_calls += 1
            return self.legacy
        ns = {"Any": object, "json": json, "CONTRACT": self.record["contract"],
              "MAX_STATE_BYTES": 2097152, "_redis_key": lambda user: user,
              "canonical_redis_store": lambda: self.redis, "_blob_auth_candidates": lambda: self.candidates,
              "_read_blob": read_blob}
        exec(compile(functions, "<chat-state>", "exec"), ns)
        self.read = lambda: ns["_read_state"]("user")

    def test_canonical_avoids_blob(self):
        self.redis.raw = json.dumps(self.record)
        self.assertEqual(self.read(), self.record)
        self.assertEqual(self.blob_calls, 0)

    def test_missing_copies_once_and_verifies(self):
        self.assertEqual(self.read(), self.record)
        self.assertEqual(self.redis.calls, ["GET", "SET", "GET"])
        self.assertEqual(self.read(), self.record)
        self.assertEqual(self.blob_calls, 1)

    def test_redis_connection_failure_fails_closed(self):
        self.redis.failure = ConnectionError("offline")
        with self.assertRaises(ConnectionError):
            self.read()
        self.assertEqual(self.blob_calls, 0)

    def test_corrupt_redis_fails_closed(self):
        self.redis.raw = '{"contract":"untrusted"}'
        with self.assertRaisesRegex(RuntimeError, "CHAT_STATE_REDIS_INVALID"):
            self.read()
        self.assertEqual(self.blob_calls, 0)

    def test_unconfigured_legacy_empty_is_safe(self):
        self.candidates = []
        self.assertIsNone(self.read())

    def test_missing_legacy_does_not_write(self):
        self.legacy = None
        self.assertIsNone(self.read())
        self.assertEqual(self.redis.calls, ["GET"])

    def test_concurrent_update_wins(self):
        newer = {**self.record, "revision": 8}
        class Race(Redis):
            def _command(inner, name, *args):
                if name == "SET":
                    inner.raw = json.dumps(newer)
                return super()._command(name, *args)
        self.redis = Race()
        self.assertEqual(self.read(), newer)

    def test_failed_migration_never_returns_unsaved_state(self):
        class Drop(Redis):
            def _command(inner, name, *args):
                if name == "SET":
                    return None
                return super()._command(name, *args)
        self.redis = Drop()
        with self.assertRaisesRegex(RuntimeError, "CHAT_STATE_MIGRATION_NOT_PERSISTED"):
            self.read()


if __name__ == "__main__":
    unittest.main()
