from __future__ import annotations
import unittest
from hf_chat_html_quality_release_v1 import patch_engine, test_overlay
from unittest.mock import patch
import hf_chat_html_quality_release_v1 as release


class PatchContractTests(unittest.TestCase):
    def test_synthetic_generation_hooks(self):
        test_overlay()

    def test_reject_drift_without_mutation(self):
        fixture=b'def generate_events(payload):\n    return payload\n'
        with self.assertRaises(RuntimeError):
            patch_engine(fixture)


    def test_live_acceptance_retries_with_fresh_session(self):
        counter = {"calls":0}
        def flaky():
            counter["calls"] += 1
            if counter["calls"] == 1:
                raise RuntimeError("temporary anonymous session reset")
        with patch.object(release,"live_smoke_once",side_effect=flaky), patch.object(release.time,"sleep"):
            release.live_smoke()
        self.assertEqual(counter["calls"],2)

    def test_live_acceptance_never_silently_accepts_three_failures(self):
        with patch.object(release,"live_smoke_once",side_effect=RuntimeError("no receipt")) as probe:
            with patch.object(release.time,"sleep"):
                with self.assertRaises(RuntimeError):
                    release.live_smoke()
        self.assertEqual(probe.call_count,3)

if __name__=="__main__":unittest.main()
