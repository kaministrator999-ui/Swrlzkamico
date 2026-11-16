"""Offline regression tests for §C shared-profile quality candidate."""
from __future__ import annotations

import ast
import unittest

from scripts.hf_chat_response_quality_v1 import (
    CONTRACT, CONTRACT_NAME, FUNCTION_ANCHOR, RETURN_ANCHOR,
    patch_engine, test_shared_profile,
)

BASE = (
    'import re\n'
    'BUILTIN_ASSISTANT_PROFILE = """Original §wyrlz core\\n\\nDYNAMIC MIRROR: original""" \n'
    'def _wyrlz_authored_section(heading):\n'
    '    return heading + ": original"\n\n'
    + FUNCTION_ANCHOR + "\n"
    '    programming=programming if isinstance(programming,dict) else {}\n'
    '    headings=["DYNAMIC MIRROR"]\n'
    '    if programming.get("codingTask"):\n'
    '        headings.extend(("PROJECT MODE",))\n'
    '    elif re.search(r"\\b(?:lyrics|song)\\b",str(prompt or ""),re.I):\n'
    '        headings.extend(("CREATIVE MODE",))\n'
    '    lead=BUILTIN_ASSISTANT_PROFILE.split("\\n\\n",1)[0]\n'
    + RETURN_ANCHOR + "\n\n"
    'def generate_events(payload):\n'
    '    yield {"type":"COMPLETED"}\n'
)

class SharedQualityPolicyTests(unittest.TestCase):
    def test_surgical_insertion_and_four_different_routes(self):
        changed=patch_engine(BASE)
        ast.parse(changed)
        self.assertIn(CONTRACT_NAME,changed)
        self.assertIn(repr(CONTRACT),changed)
        test_shared_profile(BASE,changed)
        # The old helper and generator, rather than an invented replacement,
        # remain exact original source except for the two quality insertions.
        self.assertIn('def generate_events(payload):\n    yield {"type":"COMPLETED"}',changed)

    def test_reapply_and_source_drift_fail_closed(self):
        changed=patch_engine(BASE)
        with self.assertRaisesRegex(ValueError,"ALREADY_PRESENT"):
            patch_engine(changed)
        for stale in (
            BASE.replace(FUNCTION_ANCHOR, "def other_profile(prompt):"),
            BASE.replace(RETURN_ANCHOR, '    return lead'),
            BASE.replace("BUILTIN_ASSISTANT_PROFILE", "ERASED_PROFILE"),
            BASE.replace("def generate_events(payload):","def stream_events(payload):"),
        ):
            with self.subTest(stale=stale[:55]):
                with self.assertRaises(ValueError):
                    patch_engine(stale)

    def test_publish_is_inert_without_canonical_approval(self):
        from unittest.mock import patch
        from scripts.hf_chat_response_quality_v1 import publish_guarded
        with patch.dict("os.environ", {"SWRLZ_RESPONSE_QUALITY_RELEASE_APPROVED": "0"}, clear=True):
            with self.assertRaisesRegex(PermissionError, "APPROVAL_REQUIRED"):
                publish_guarded()

    def test_no_private_history_or_tool_state_in_static_contract(self):
        self.assertNotIn("password",CONTRACT.lower())
        self.assertNotIn("user_id",CONTRACT.lower())
        self.assertIn("unknown",CONTRACT)
        self.assertIn("sources",CONTRACT)
        self.assertIn("songs",CONTRACT)

if __name__ == "__main__":
    unittest.main()
