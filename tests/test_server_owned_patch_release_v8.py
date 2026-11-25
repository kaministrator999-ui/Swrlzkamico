"""Assert safe v8 Hugging Face source patch and live loaded-code guard."""
import ast
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location(
    "release_v8",ROOT/"scripts/hf_chat_server_owned_patch_release_v8.py")
release=importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

STATION_FIXTURE = '''
app = object()
def _swrlz_verified_repair_runtime_v7():
    import html_project_agent_runtime_v1 as _swrlz_model_repair
    return _swrlz_model_repair


def _swrlz_execute_model_repair_v7(payload, coder_generate):
    active = _swrlz_verified_repair_runtime_v7()
    yield from active.run(payload, coder_generate)

@app.get("/api/html-project-agent-v7/runtime-check", include_in_schema=False)
def old_health():
    return {}
'''


class LivePatchV8Contract(unittest.TestCase):
    def test_station_source_upgrade_is_valid_and_idempotent(self):
        source=release.patch_station(STATION_FIXTURE)
        ast.parse(source)
        self.assertEqual(source.count(release.MARKER),1)
        self.assertEqual(source.count(release.CHECK),1)
        self.assertEqual(release.patch_station(source),source)
        self.assertIn("importlib.reload(agent)",source)
        self.assertIn("importlib.reload(active)",source)

    def test_station_missing_prior_guard_is_refused(self):
        with self.assertRaisesRegex(RuntimeError,"ANCHOR_DRIFT"):
            release.patch_station("def worker(): pass")

    def test_repository_agent_runtime_source_protocol(self):
        from api.html_project_agent_v1 import bind_model_edits
        from api import html_project_agent_runtime_v1 as runtime
        # Repository tests may import the same file as both api.* and the
        # Hugging Face root module; compare functionality, not object identity.
        self.assertEqual(runtime.bind_model_edits.__name__,bind_model_edits.__name__)
        self.assertTrue(callable(runtime.bind_model_edits))
        self.assertIn("bind_model_edits",runtime.run.__code__.co_names)
        if hasattr(runtime,"repair_candidate"):
            self.assertIn("binder",runtime.repair_candidate.__code__.co_varnames)
            self.assertIs(runtime.repair_candidate.__kwdefaults__["binder"],runtime.bind_model_edits)
        self.assertNotIn("sourceSha256",runtime._model_patch.__code__.co_consts)


if __name__=="__main__":
    unittest.main()
