"""Static guard against reintroducing Vercel as a runtime/deployment authority."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HostingAuthorityTests(unittest.TestCase):
    def test_active_docs_identify_hf(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Hugging Face is the active hosting", readme)

    def test_no_vercel_config_or_workflow(self):
        self.assertFalse((ROOT / "vercel.json").exists())
        self.assertFalse((ROOT / ".vercel").exists())
        self.assertFalse((ROOT / ".github/workflows/manual-vercel-production.yml").exists())
        self.assertFalse((ROOT / ".github/workflows/verify-collector-live.yml").exists())

    def test_no_legacy_queue_dependency(self):
        for name in ("pyproject.toml", "queues/swrlz_generation_v3.py",
                     "api/account_routes.py", "api/account_routes_v2.py",
                     "api/lalm_station.py"):
            with self.subTest(name=name):
                source = (ROOT / name).read_text(encoding="utf-8")
                self.assertNotIn("vercel.queue", source)
                self.assertNotIn("vercel-queue", source)

    def test_redis_is_canonical_for_user_chat(self):
        source = (ROOT / "api/chat_state.py").read_text(encoding="utf-8")
        self.assertIn('redis._command("SET", key, body, "NX")', source)
        self.assertNotIn("def _write_blob(", source)
        self.assertIn("CHAT_STATE_MIGRATION_NOT_PERSISTED", source)

    def test_explicit_hf_deployment_gate_kept(self):
        workflow = (ROOT / ".github/workflows/manual-hf-space.yml").read_text(encoding="utf-8")
        self.assertIn("kamiloki/Swyrlz", workflow)
        self.assertIn("Snapshot existing production HF reference", workflow)
        self.assertIn("Require explicit publish authorization", workflow)


if __name__ == "__main__":
    unittest.main()
