"""Contract tests for §C model-chosen source repairs."""
import hashlib
import unittest

from api.html_project_agent_v1 import (
    VERSION, ProposalError, verify_source, prompt_messages,
    apply_proposal, inspect_static,
)
from scripts.project_code_targeted_repair_v1 import source_sha

ORIGINAL = "<!doctype html><html><head><title>Viewer</title></head><body><button id='save'>Save</button></body></html>"

def propose(source=ORIGINAL, code="<script>document.querySelector('#save').onclick=()=>alert('saved')</script>",
            anchor="</body>", hash_value=None, **extra):
    return {"schema": VERSION, "project": "interactive-3d-model-viewer",
            "patches": [{"path": "index.html",
                         "sourceSha256": hash_value or source_sha(source),
                         "op": "insert_before", "anchor": anchor, "code": code}], **extra}

class AgentContract(unittest.TestCase):
    def setUp(self):
        self.files = {"index.html": ORIGINAL}

    def test_model_selects_own_change_not_hardcoded_three_repair(self):
        result = apply_proposal("interactive-3d-model-viewer", self.files, propose(),
                                validation=lambda files: {"passed": True})
        self.assertTrue(result["readyForOwnerReview"])
        self.assertIn("onclick", result["proposedFiles"]["index.html"])
        self.assertIn("Save", result["proposedFiles"]["index.html"])
        self.assertIn("+<!doctype html>", result["diffs"]["index.html"])
        self.assertFalse(result["committed"])
        self.assertFalse(result["deployed"])

    def test_multiple_files_and_chained_patches(self):
        files = {**self.files, "style.css": "button{color:red}"}
        first = {"path":"style.css", "sourceSha256":source_sha(files["style.css"]),
                 "op":"replace_once", "anchor":"red", "code":"blue"}
        second = {"path":"style.css", "sourceSha256":source_sha("button{color:blue}"),
                  "op":"insert_after", "anchor":"}", "code":"\n/* done */"}
        proposal = {"schema":VERSION,"project":"interactive-3d-model-viewer",
                    "patches":[first,second]}
        result = apply_proposal("interactive-3d-model-viewer", files, proposal,
                                validation=lambda x: {"passed": True})
        self.assertEqual(result["proposedFiles"]["style.css"],
                         "button{color:blue}\n/* done */")
        self.assertEqual(result["changedFiles"], ["style.css"])

    def test_wrong_source_version_and_guess_rejected(self):
        with self.assertRaises(ProposalError):
            apply_proposal("interactive-3d-model-viewer", self.files,
                           propose(hash_value="0"*64))
        with self.assertRaises(ProposalError):
            apply_proposal("interactive-3d-model-viewer", self.files, propose(),
                           expected_hashes={"index.html": "bad"})

    def test_missing_anchor_and_overwrite_rejected(self):
        with self.assertRaises(ProposalError):
            apply_proposal("interactive-3d-model-viewer", self.files,
                           propose(anchor="nonexistent"))
        data = propose()
        data["patches"][0]["path"] = "../secrets.env"
        with self.assertRaises(ProposalError):
            apply_proposal("interactive-3d-model-viewer", self.files, data)
        data = propose()
        data["patches"][0]["path"] = "new-file.html"
        with self.assertRaises(ProposalError):
            apply_proposal("interactive-3d-model-viewer", self.files, data)

    def test_model_cannot_authorize_publishing(self):
        with self.assertRaises(ProposalError):
            apply_proposal("interactive-3d-model-viewer", self.files,
                           propose(approved=True, deploy=True))

    def test_failed_validation_refuses_review_ready(self):
        with self.assertRaisesRegex(ProposalError, "VALIDATION_FAILED"):
            apply_proposal("interactive-3d-model-viewer", self.files, propose(),
                           validation=lambda x: {"passed": False, "issues": ["bad"]})
        result = apply_proposal("interactive-3d-model-viewer", self.files, propose())
        self.assertFalse(result["readyForOwnerReview"])

    def test_inert_model_context(self):
        messages = prompt_messages("interactive-3d-model-viewer", self.files,
                                   ["missing JS handler"], "repair save button")
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("missing JS handler", messages[1]["content"])
        self.assertIn(source_sha(ORIGINAL), messages[1]["content"])

    def test_validates_tree_and_protects_identity(self):
        self.assertEqual(verify_source("interactive-3d-model-viewer", self.files)["index.html"],
                         source_sha(ORIGINAL))
        with self.assertRaises(ProposalError):
            verify_source("../../escape", self.files)
        with self.assertRaises(ProposalError):
            verify_source("interactive-3d-model-viewer", {"style.css":"red"})

    def test_static_evidence_not_browser_proof(self):
        # No static PASS may claim that live controls were executed.
        result = inspect_static(self.files)
        self.assertFalse(result["browserVerified"])

if __name__ == "__main__":
    unittest.main()
