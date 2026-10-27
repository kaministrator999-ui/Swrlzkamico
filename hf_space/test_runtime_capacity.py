"""Read-only resource-controller parsing and a deliberately narrow public API."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from runtime_capacity import MAX_FILE_BYTES, parse_runtime_capacity, runtime_capacity_snapshot
import station


class RuntimeCapacityParser(unittest.TestCase):
    def test_measured_limits_and_usage_are_numeric(self):
        result = parse_runtime_capacity({"memory.max": "16106127360\n",
            "memory.current": "8300000000\n", "memory.peak": "9000000000\n",
            "cpu.max": "250000 100000\n"})
        self.assertEqual(result["source"], "cgroup-v2")
        self.assertEqual(result["memory"], {"limitBytes": 16106127360, "limitState": "measured",
            "currentBytes": 8300000000, "currentState": "measured",
            "peakBytes": 9000000000, "peakState": "measured"})
        self.assertEqual(result["cpu"], {"quotaMicros": 250000, "periodMicros": 100000,
            "limitCores": 2.5, "state": "measured"})

    def test_max_means_no_visible_controller_limit_not_unknown_capacity(self):
        result = parse_runtime_capacity({"memory.max": "max", "memory.current": "0",
            "memory.peak": "0", "cpu.max": "max 100000"})
        self.assertIsNone(result["memory"]["limitBytes"])
        self.assertEqual(result["memory"]["limitState"], "unlimited")
        self.assertEqual(result["memory"]["currentBytes"], 0)
        self.assertEqual(result["cpu"], {"quotaMicros": None, "periodMicros": 100000,
            "limitCores": None, "state": "unlimited"})

    def test_missing_or_malformed_counters_are_unavailable(self):
        for invalid in [None, "", "-1", "+2", "1.5", "123 bytes", "1\n2", "∞",
                        "9" * 20, str(1 << 63), "0" * (MAX_FILE_BYTES + 1)]:
            with self.subTest(value=str(invalid)[:30]):
                result = parse_runtime_capacity({"memory.max": invalid, "memory.current": invalid,
                    "memory.peak": invalid, "cpu.max": invalid})
                self.assertEqual(result["source"], "unavailable")
                for key in ["limitBytes", "currentBytes", "peakBytes"]:
                    self.assertIsNone(result["memory"][key])
                self.assertEqual(result["cpu"]["state"], "unavailable")
        result = parse_runtime_capacity({"memory.current": "max", "memory.peak": "max"})
        self.assertEqual(result["memory"]["currentState"], "unavailable")
        self.assertEqual(result["memory"]["peakState"], "unavailable")

    def test_cpu_fields_require_positive_integers_and_exact_shape(self):
        for invalid in ["100000", "100 200 extra", "max", "max 0", "0 100000",
                        "-1 100000", "1.5 100000", "100000 -1", "100000 max",
                        "100000 0", "9223372036854775808 100000"]:
            with self.subTest(value=invalid):
                result = parse_runtime_capacity({"cpu.max": invalid})
                self.assertEqual(result["cpu"], {"quotaMicros": None, "periodMicros": None,
                    "limitCores": None, "state": "unavailable"})

    def test_partial_observations_do_not_invent_other_values(self):
        result = parse_runtime_capacity({"memory.current": "50", "unexpected": "private"})
        self.assertEqual(result["source"], "cgroup-v2")
        self.assertEqual(result["memory"]["currentBytes"], 50)
        self.assertIsNone(result["memory"]["limitBytes"])
        self.assertEqual(result["memory"]["limitState"], "unavailable")
        self.assertNotIn("private", json.dumps(result))

    def test_reader_bounds_bytes_and_handles_missing_non_ascii_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "memory.max").write_text("1024\n")
            (root / "memory.current").write_bytes(b"9" * (MAX_FILE_BYTES + 1))
            (root / "memory.peak").write_bytes(b"\xff")
            result = runtime_capacity_snapshot(root)
        self.assertEqual(result["memory"]["limitBytes"], 1024)
        self.assertIsNone(result["memory"]["currentBytes"])
        self.assertIsNone(result["memory"]["peakBytes"])
        self.assertEqual(result["cpu"]["state"], "unavailable")
        self.assertEqual(runtime_capacity_snapshot(root)["source"], "unavailable")


class RuntimeCapacityHTTP(unittest.TestCase):
    def test_public_get_returns_only_approved_shape_without_account_or_model_access(self):
        expected = parse_runtime_capacity({"memory.max": "1000", "memory.current": "300",
            "memory.peak": "400", "cpu.max": "100000 100000"})
        with TestClient(station.app) as client, \
                patch.object(station, "runtime_capacity_snapshot", return_value=expected) as snapshot, \
                patch.object(station, "_account_session", side_effect=AssertionError("no account access")), \
                patch.object(station, "routes", side_effect=AssertionError("no model access")):
            response = client.get("/api/hf/runtime-capacity?path=private&model=safe")
            self.assertEqual(response.status_code, 200)
            snapshot.assert_called_once_with()
            self.assertEqual(response.headers["cache-control"], "no-store")
            self.assertNotIn("set-cookie", response.headers)
            data = response.json()
            self.assertEqual(data, expected)
            self.assertEqual(set(data), {"schema", "source", "scope", "memory", "cpu"})
            self.assertEqual(set(data["memory"]), {"limitBytes", "limitState", "currentBytes",
                "currentState", "peakBytes", "peakState"})
            self.assertEqual(set(data["cpu"]), {"quotaMicros", "periodMicros", "limitCores", "state"})
            serialized = response.text.lower()
            for private in ["private", "safe-model", "credentials", "environment", "/sys/", "/proc/",
                            "hostname", "process", "account", "token", "user"]:
                self.assertNotIn(private, serialized)
            self.assertEqual(client.post("/api/hf/runtime-capacity").status_code, 405)

    def test_unavailable_controller_files_remain_a_valid_explicit_unknown_response(self):
        expected = parse_runtime_capacity({})
        with TestClient(station.app) as client, patch.object(station, "runtime_capacity_snapshot", return_value=expected):
            response = client.get("/api/hf/runtime-capacity")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["source"], "unavailable")
        self.assertEqual(response.json()["memory"]["limitState"], "unavailable")
        self.assertEqual(response.json()["cpu"]["state"], "unavailable")


if __name__ == "__main__":
    unittest.main()
