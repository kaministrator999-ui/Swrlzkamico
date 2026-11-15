from __future__ import annotations
import unittest
from hf_chat_html_quality_release_v1 import patch_engine, test_overlay


class PatchContractTests(unittest.TestCase):
    def test_synthetic_generation_hooks(self):
        test_overlay()

    def test_reject_drift_without_mutation(self):
        fixture=b'def generate_events(payload):\n    return payload\n'
        with self.assertRaises(RuntimeError):
            patch_engine(fixture)

if __name__=="__main__":unittest.main()
