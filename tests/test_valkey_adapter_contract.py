"""Opt-in Valkey transport tests that never contact a live database."""
import os
import unittest
from unittest.mock import patch

from api.durable_redis_store import DurableStoreUnavailable, RedisRestChatStore

TEST_URI = "rediss://default:fake-test-only@valkey.invalid:12345"


class ValkeyTransportTests(unittest.TestCase):
    def test_legacy_rest_remains_default(self):
        env = {"SWRLZ_REDIS_REST_URL": "https://redis.invalid", "SWRLZ_REDIS_REST_TOKEN": "fake-rest-token"}
        with patch.dict(os.environ, env, clear=True):
            self.assertTrue(RedisRestChatStore.configured())
            store = RedisRestChatStore.from_env()
            self.assertEqual(store.transport, "redis-rest")
            self.assertEqual(store.url, env["SWRLZ_REDIS_REST_URL"])
            self.assertEqual(RedisRestChatStore.backend_kind(), "redis-rest")

    def test_selection_requires_explicit_flag(self):
        env = {"SWRLZ_VALKEY_URL": TEST_URI,
               "SWRLZ_REDIS_REST_URL": "https://redis.invalid",
               "SWRLZ_REDIS_REST_TOKEN": "fake-rest-token"}
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(RedisRestChatStore.from_env().transport, "redis-rest")
            self.assertEqual(RedisRestChatStore.backend_kind(), "redis-rest")

    def test_valkey_uri_must_use_tls(self):
        with patch.dict(os.environ, {"SWRLZ_REDIS_BACKEND": "valkey",
                                      "SWRLZ_VALKEY_URL": "redis://localhost:6379"}, clear=True):
            self.assertFalse(RedisRestChatStore.configured())
            with self.assertRaises(DurableStoreUnavailable):
                RedisRestChatStore.from_env()

    def test_valkey_missing_uri_never_falls_back(self):
        env = {"SWRLZ_REDIS_BACKEND": "valkey",
               "SWRLZ_REDIS_REST_URL": "https://redis.invalid",
               "SWRLZ_REDIS_REST_TOKEN": "fake-rest-token"}
        with patch.dict(os.environ, env, clear=True):
            self.assertFalse(RedisRestChatStore.configured())
            with self.assertRaises(DurableStoreUnavailable):
                RedisRestChatStore.from_env()

    def test_valkey_executes_native_commands_not_http(self):
        with patch.dict(os.environ, {"SWRLZ_REDIS_BACKEND": "valkey",
                                      "SWRLZ_VALKEY_URL": TEST_URI}, clear=True):
            with patch("api.durable_redis_store._secure_valkey_client") as client, \
                 patch("api.durable_redis_store.requests.post") as http:
                client.return_value.execute_command.return_value = "pong"
                self.assertTrue(RedisRestChatStore.configured())
                store = RedisRestChatStore.from_env()
                self.assertEqual(store.transport, "valkey-tls")
                self.assertEqual(store._command("PING"), "pong")
                self.assertEqual(RedisRestChatStore.backend_kind(), "valkey-tls")
                client.assert_called_once_with(TEST_URI)
                client.return_value.execute_command.assert_called_once_with("PING")
                http.assert_not_called()

    def test_valkey_fail_closed_without_exposing_uri(self):
        with patch.dict(os.environ, {"SWRLZ_REDIS_BACKEND": "valkey",
                                      "SWRLZ_VALKEY_URL": TEST_URI}, clear=True):
            with patch("api.durable_redis_store._secure_valkey_client") as client:
                client.return_value.execute_command.side_effect = RuntimeError("private credentials")
                with self.assertRaises(DurableStoreUnavailable) as failed:
                    RedisRestChatStore.from_env()._command("GET", "somekey", sensitive=True)
                self.assertNotIn("credentials", str(failed.exception))
                self.assertNotIn(TEST_URI, str(failed.exception))

    def test_invalid_backend_is_rejected(self):
        with patch.dict(os.environ, {"SWRLZ_REDIS_BACKEND": "unexpected",
                                      "SWRLZ_REDIS_REST_URL": "https://redis.invalid",
                                      "SWRLZ_REDIS_REST_TOKEN": "fake-rest-token"}, clear=True):
            self.assertFalse(RedisRestChatStore.configured())
            with self.assertRaises(DurableStoreUnavailable):
                RedisRestChatStore.from_env()


if __name__ == "__main__":
    unittest.main()
