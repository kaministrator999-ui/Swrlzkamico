import ast
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from hf_chat_selective_retrieval_trial import patch_engine, ANCHOR

class IntegrationTests(unittest.TestCase):
    def test_exact_generator_patch(self):
        src='import os\n\ndef generate_events(payload):\n    yield {"type":"DELTA","text":"ok"}\n\nX="onlineContext"\n'
        patched=patch_engine(src)
        ast.parse(patched)
        self.assertIn("from api.online_research import research",patched)
        self.assertIn("SWRLZ_SELECTIVE_RETRIEVAL_ENABLED",patched)
        self.assertIn('yield {"type":"DELTA","text":"ok"}',patched)
        self.assertEqual(patched.count("def generate_events(payload):"),1)
        with self.assertRaises(RuntimeError):patch_engine(patched)

    def test_source_drift_fail_closed(self):
        for body in ('import os\nX="onlineContext"\n',
                     'import os\ndef generate_events(payload):\n    yield 1\n',
                     'X="onlineContext"\n'+ANCHOR+'    yield 1\n'):
            with self.assertRaises(RuntimeError):patch_engine(body)

if __name__ == "__main__":
    unittest.main()
