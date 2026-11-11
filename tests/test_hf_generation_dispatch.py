"""Lightweight HF dispatcher contract tests (no external services)."""
import asyncio
import threading
import unittest
from unittest.mock import patch

from api import hf_generation_dispatch as dispatch


class HuggingFaceGenerationDispatchTests(unittest.TestCase):
    def test_rejects_unknown_topic(self):
        with self.assertRaisesRegex(ValueError, "TOPIC_INVALID"):
            asyncio.run(dispatch.send("unknown", {"requestId": "r-unknown"}))

    def test_rejects_mismatched_request_id(self):
        with self.assertRaisesRegex(ValueError, "REQUEST_ID_INVALID"):
            asyncio.run(dispatch.send("swrlz-generation", {"requestId": "one"}, idempotency_key="two"))

    def test_idempotent_in_flight_dispatch(self):
        started = threading.Event()
        release = threading.Event()
        calls = []

        def worker(payload):
            calls.append(payload["requestId"])
            started.set()
            release.wait(timeout=5)

        with patch.object(dispatch, "_run", side_effect=worker):
            request = {"requestId": "hf-dispatch-test-unique"}
            first = asyncio.run(dispatch.send("swrlz-generation", request))
            self.assertTrue(started.wait(timeout=3))
            second = asyncio.run(dispatch.send("swrlz-generation", request))
            self.assertEqual(first, second)
            self.assertEqual(calls, ["hf-dispatch-test-unique"])
            release.set()
        self.assertTrue(release.is_set())


if __name__ == "__main__":
    unittest.main()
