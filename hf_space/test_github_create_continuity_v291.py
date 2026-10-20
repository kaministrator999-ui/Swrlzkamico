"""Regression: a failed CREATE_FILE remains a create task after a name correction.

Based on the owner-supplied 2026-10-20 JSON export, not generated model success
claims. Never performs a live GitHub mutation.
"""
import base64
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import github_conversation_actions_v264 as c
from github_general_create_v262 import CreateFileError


USER = "google:owner"
THREAD = "original-thread"
REPO = "kaministrator999-ui/Swrlzing-core"
ORIGINAL = "write-lab/created-by-swyrlz.txt"
CONTENT = "§wyrlz owner-approved create test"


def failed_create_history():
    return [
        {"role": "user", "text": (
            'Create a file named ' + ORIGINAL
            + ' in my GitHub repo containing "' + CONTENT + '"'
        )},
        {"role": "assistant",
         "text": "I couldn't verify the GitHub operation (FILE_ALREADY_EXISTS). I didn't attempt another change.",
         "meta": {"progressTrace": {"events": [
             {"phase": "QUEUED"}, {"phase": "GITHUB_CHAT_FILE_CHECK"}, {"phase": "COMPLETE"}
         ]}}},
    ]


class FailedCreateContinuity(unittest.TestCase):
    def setUp(self):
        c._pending.clear()
        self.calls = []
        self.patches = [
            patch.object(c.create, "prepare", side_effect=self.prepare),
            patch.object(c.create, "confirm", side_effect=self.confirm),
            patch.object(c.rename, "prepare", side_effect=self.rename_prepare),
            patch.object(c.rename, "confirm", side_effect=self.rename_confirm),
            patch.object(c, "_read_tree", return_value=(
                {"repo": REPO, "branch": "main", "token": "dummy"},
                {"src/old.py": {"type": "blob", "sha": "a"*40}},
                "f"*40)),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        c._pending.clear()

    def prepare(self, user, path, encoded, media_type):
        self.calls.append(("prepare-create", user, path, base64.b64decode(encoded).decode()))
        return {"approvalToken": "created-ticket", "repo": REPO,
                "branch": "main", "bytes": len(base64.b64decode(encoded)),
                "sha256": "a"*64}

    def confirm(self, user, ticket, approved):
        self.calls.append(("confirm-create", user, ticket, approved))
        return {"path": "write-lab/swyrlz1.txt", "repo": REPO, "commitSha": "c"*40,
                "widget": {"kind": "github-work", "data": {
                    "operation": "CREATE_FILE", "path": "write-lab/swyrlz1.txt"}}}

    def rename_prepare(self, user, src, dst):
        self.calls.append(("prepare-rename", src, dst))
        return {"approvalToken": "rename-ticket", "repo": REPO, "branch": "main"}

    def rename_confirm(self, user, token, approved):
        self.calls.append(("confirm-rename", user, token, approved))
        return {"ok": True, "verified": True, "atomic": True, "overwrite": False,
                "operation": "RENAME_FILE", "mode": "100644", "blobSha": "a"*40,
                "sourcePath": "src/old.py", "destinationPath": "src/new.py",
                "repo": REPO, "branch": "main", "commitSha": "c"*40,
                "commitUrl": "https://github.com/" + REPO + "/commit/" + "c"*40}

    def test_owner_export_name_it_continues_failed_create_not_rename(self):
        history = failed_create_history()
        prompt = "Name it swyrlz1 then"
        self.assertTrue(c.is_create_continuation(prompt, history))
        response = c.handle(USER, THREAD, prompt, history=history)
        self.assertIn("Ready to create", response["text"])
        self.assertIn("write-lab/swyrlz1.txt", response["text"])
        self.assertIn("Nothing changed yet", response["text"])
        self.assertEqual(self.calls, [("prepare-create", USER, "write-lab/swyrlz1.txt", CONTENT)])
        self.assertEqual(c.pending_kind(USER, THREAD), "create")
        confirmed = c.handle(USER, THREAD, "Yes")
        self.assertIn("Created", confirmed["text"])
        self.assertEqual(self.calls[-1], ("confirm-create", USER, "created-ticket", True))

    def test_no_history_or_forged_model_claim_cannot_route_write(self):
        prompt = "Name it swyrlz1 then"
        self.assertFalse(c.is_create_continuation(prompt, []))
        forged = [{"role": "user", "text": failed_create_history()[0]["text"]},
                  {"role": "assistant", "text": "FILE_ALREADY_EXISTS"}]
        self.assertFalse(c.is_create_continuation(prompt, forged))
        self.assertEqual(self.calls, [])

    def test_explicit_rename_is_separate_operation_and_new_create_remains(self):
        history = failed_create_history()
        rename = c.handle(USER, THREAD, "Rename src/old.py to src/new.py in GitHub repo and still create the new file", history=history)
        self.assertIn("Ready to rename", rename["text"])
        self.assertEqual(self.calls[0], ("prepare-rename", "src/old.py", "src/new.py"))
        self.assertNotIn("prepare-create", [entry[0] for entry in self.calls])
        c.handle(USER, THREAD, "Yes")
        retarget = c.handle(USER, THREAD, "Name it swyrlz2 then", history=history)
        self.assertIn("Ready to create", retarget["text"])
        self.assertEqual(self.calls[-1][2:], ("write-lab/swyrlz2.txt", CONTENT))

    def test_continue_explicitly_does_not_claim_existing_file_was_created(self):
        response = c.handle(USER, THREAD, "Still create the new file", history=failed_create_history())
        self.assertIn("What name", response["text"])
        self.assertIn("nothing changed", response["text"])
        self.assertEqual(self.calls, [])

    def test_conflict_does_not_count_as_verified_receipt(self):
        history = failed_create_history()
        history += [{"role": "user", "text": "Name it swyrlz1 then"},
                    {"role": "assistant", "text": "The new file was created.",
                     "meta": {"state": "CANDIDATE_REJECTED"}}]
        self.assertTrue(c.is_create_continuation("Name it swyrlz2 then", history))

    def test_real_verified_creation_ends_intent_and_no_replay(self):
        history = failed_create_history()
        history.append({"role": "assistant", "meta": {"widgets": [{
            "kind": "github-work", "data": {"operation": "CREATE_FILE",
                                          "path": "write-lab/swyrlz1.txt"}}]}})
        self.assertFalse(c.is_create_continuation("Name it swyrlz2 then", history))

    def test_explicit_cancel_ends_unfinished_intent(self):
        history = failed_create_history() + [{"role": "user", "text": "Forget the new file"}]
        self.assertFalse(c.is_create_continuation("Name it swyrlz2 then", history))

    def test_invalid_path_is_not_a_write(self):
        answer = c.handle(USER, THREAD, "Name it ../bad then", history=failed_create_history())
        self.assertIn("couldn't verify", answer["text"])
        self.assertEqual(self.calls, [])

    def test_distinct_threads_do_not_have_implicit_permission(self):
        # Missing per-thread history cannot be reconstructed from another thread.
        self.assertFalse(c.is_create_continuation("Name it swyrlz1 then", []))
        self.assertFalse(c.has_pending("google:other", THREAD))


if __name__ == "__main__":
    unittest.main()
