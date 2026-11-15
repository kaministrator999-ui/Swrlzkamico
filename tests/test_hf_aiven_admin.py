"""Security and exact-source tests for private HF Aiven admin."""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


admin = _load("swrlz_test_aiven_admin", "hf_space/aiven_admin.py")
release = _load("swrlz_test_hf_aiven_release", "scripts/hf_aiven_admin_release.py")


class AdminAuthorizationTests(unittest.TestCase):
    def test_missing_owner_configuration_fails_closed(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(admin._authorized({"id": "google:anything", "emailVerified": True}))
            self.assertFalse(admin._authorized(None))

    def test_subject_is_exact_google_provider_identity(self):
        with mock.patch.dict(os.environ, {"SWRLZ_ADMIN_GOOGLE_SUB": "owner-123"}, clear=True):
            self.assertTrue(admin._authorized({"id": "google:owner-123"}))
            self.assertFalse(admin._authorized({"id": "google:other"}))
            self.assertFalse(admin._authorized({"id": "owner-123"}))

    def test_existing_sandbox_owner_is_reused(self):
        with mock.patch.dict(os.environ, {"SWRLZ_SANDBOX_WRITE_GOOGLE_SUB": "owner-123"}, clear=True):
            self.assertTrue(admin._authorized({"id": "google:owner-123"}))
            self.assertFalse(admin._authorized({"id": "google:guest"}))

    def test_email_admin_requires_google_verified_email_claim(self):
        env = {"SWRLZ_ADMIN_GOOGLE_EMAIL": "owner@example.com"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertTrue(admin._authorized({"id": "google:owner", "email": "OWNER@example.com", "emailVerified": True}))
            self.assertFalse(admin._authorized({"id": "google:other", "email": "owner@example.com", "emailVerified": False}))
            self.assertFalse(admin._authorized({"id": "google:other", "email": "owner@example.com"}))
            self.assertFalse(admin._authorized({"id": "google:other", "email": "other@example.com", "emailVerified": True}))

    def test_all_configured_identity_constraints_must_match(self):
        env = {"SWRLZ_ADMIN_GOOGLE_SUB": "owner-123", "SWRLZ_ADMIN_GOOGLE_EMAIL": "owner@example.com"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(admin._authorized({"id": "google:owner-123", "email": "wrong@example.com", "emailVerified": True}))
            self.assertTrue(admin._authorized({"id": "google:owner-123", "email": "owner@example.com", "emailVerified": True}))


class AivenMetricsTests(unittest.TestCase):
    def test_no_provider_read_without_all_service_config(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(admin, "_request") as request:
            self.assertEqual(admin.read_metrics()["code"], "AIVEN_NOT_CONFIGURED")
            request.assert_not_called()

    def test_only_expected_metrics_without_secrets(self):
        env = {"SWRLZ_AIVEN_API_TOKEN": "test-secret", "SWRLZ_AIVEN_PROJECT": "p", "SWRLZ_AIVEN_SERVICE": "s"}
        payload = [
            {"service": {"state": "RUNNING", "service_type": "pg", "plan": "free", "disk_space_mb": 8192,
                         "service_uri": "postgres://secret"}},
            {"metrics": {"cpu_usage": {"rows": [[1, 25.0]], "token": "unsafe"},
                         "disk_usage": {"rows": [[2, 45.0]]},
                         "password": "unsafe"}},
        ]
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(admin, "_request", side_effect=payload) as request:
            result = admin.read_metrics()
        self.assertTrue(result["ok"])
        self.assertEqual(result["metrics"]["cpu_usage"]["rows"], [[1, 25.0]])
        self.assertNotIn("token", result["metrics"]["cpu_usage"])
        self.assertNotIn("password", result["metrics"])
        self.assertEqual(request.call_args_list[1].args[:2], ("POST", "/project/p/service/s/metrics"))
        self.assertEqual(result["service"]["diskCapacityMB"], 8192)
        self.assertNotIn("postgres://secret", str(result))
        self.assertNotIn(env["SWRLZ_AIVEN_API_TOKEN"], str(result))

    def test_reject_unsafe_project_name(self):
        env = {"SWRLZ_AIVEN_API_TOKEN": "test-secret", "SWRLZ_AIVEN_PROJECT": "../p", "SWRLZ_AIVEN_SERVICE": "s"}
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(admin, "_request") as request:
            self.assertEqual(admin.read_metrics()["code"], "AIVEN_CONFIG_INVALID")
            request.assert_not_called()


class ExactSourcePatchTests(unittest.TestCase):
    SAMPLE = '''from fastapi import FastAPI
import uuid
app=FastAPI()
def _account_session(request):
    return None, None
@app.post("/api/account/google")
def login(request):
    claims=google_id_token.verify_oauth2_token(credential, g_req, CLIENT)
    user={"id":"google:"+claims["sub"],"email":claims["email"]}
    sid=uuid.uuid4().hex
    with _lock:_hf_accounts[sid]=user
'''
    def test_patch_preserves_existing_login_and_app(self):
        result = release.patch_station(self.SAMPLE)
        self.assertIn("user['emailVerified']=claims.get('email_verified') is True", result)
        self.assertIn("_install_aiven_admin(app, _account_session)", result)
        self.assertEqual(result.count('google_id_token.verify_oauth2_token'), 1)
        self.assertEqual(result.count(release.MARKER), 1)

    def test_unknown_live_login_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "HF_GOOGLE_CLAIM_PROJECTION_DRIFT"):
            release.patch_station(self.SAMPLE.replace("    sid=uuid.uuid4().hex\n", "    sid=new_id()\n"))

    def test_duplicate_installation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "AIVEN_ADMIN_ALREADY_INSTALLED"):
            release.patch_station(release.patch_station(self.SAMPLE))


if __name__ == "__main__":
    unittest.main()
