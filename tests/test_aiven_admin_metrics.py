"""Regression tests for the read-only, manually invoked Aiven admin meter."""
from __future__ import annotations

import json
import os
import unittest
from unittest import mock

from api import aiven_metrics


class AivenAdminMetricsTests(unittest.TestCase):
    def test_unconfigured_is_inert(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(aiven_metrics, "_fetch") as fetch:
            outcome = aiven_metrics.read_aiven_metrics()
        self.assertEqual(outcome["code"], "AIVEN_NOT_CONFIGURED")
        self.assertFalse(outcome["configured"])
        fetch.assert_not_called()

    def test_configured_reads_service_and_hourly_metrics_only(self):
        env = {
            "SWRLZ_AIVEN_API_TOKEN": "never-send-this-value",
            "SWRLZ_AIVEN_PROJECT": "sample-project",
            "SWRLZ_AIVEN_SERVICE": "sample-service",
        }
        provider = [
            {"service": {"state": "RUNNING", "plan": "free", "service_type": "pg",
                         "disk_space_mb": 10240, "service_uri": "never-return-this"}},
            {"metrics": {"cpu_usage": {"rows": [[123, 22.5]]},
                         "password": "never-return-this", "mem_usage": 35.1}},
        ]
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(aiven_metrics, "_fetch", side_effect=provider) as fetch:
            outcome = aiven_metrics.read_aiven_metrics()
        self.assertTrue(outcome["ok"])
        self.assertEqual(outcome["service"]["diskCapacityMB"], 10240)
        self.assertEqual(outcome["metrics"]["cpu_usage"]["rows"][-1][-1], 22.5)
        self.assertEqual(outcome["metricsPeriod"], "hour")
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(fetch.call_args_list[0].args[0], "GET")
        self.assertEqual(fetch.call_args_list[1].args[0], "POST")
        self.assertEqual(fetch.call_args_list[1].args[3], {"period": "hour"})
        body = json.dumps(outcome)
        self.assertNotIn(env["SWRLZ_AIVEN_API_TOKEN"], body)
        self.assertNotIn("never-return-this", body)

    def test_malformed_config_never_contacts_provider(self):
        env = {
            "SWRLZ_AIVEN_API_TOKEN": "private",
            "SWRLZ_AIVEN_PROJECT": "../other-project",
            "SWRLZ_AIVEN_SERVICE": "sample",
        }
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(aiven_metrics, "_fetch") as fetch:
            outcome = aiven_metrics.read_aiven_metrics()
        self.assertEqual(outcome["code"], "INVALID_AIVEN_SERVICE_CONFIGURATION")
        fetch.assert_not_called()

    def test_metrics_bounded_and_non_finite_rejected(self):
        result = aiven_metrics._safe_metrics({
            "rows": list(range(100)),
            "password": "unsafe",
            "cpu_usage": float("inf"),
        })
        self.assertEqual(result["rows"], list(range(68, 100)))
        self.assertNotIn("password", result)
        self.assertNotIn("cpu_usage", result)


if __name__ == "__main__":
    unittest.main()
