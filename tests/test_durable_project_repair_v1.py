"""Regression for the browser's ACTUAL durable Workstation existing-project route."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from api import durable_project_repair_v1 as bridge
from api import html_project_context_v1 as project_context
from api import html_project_repair_v1 as approval_code

FULL_PROMPT = (
    "Inspect the existing interactive-3d-model-viewer project on GitHub. "
    "Identify why it fails to render correctly and repair it using your own coding model. "
    "Retrieve the actual source, generate targeted patches, validate them, and revise any failed patches until validation passes. "
    "Preserve the existing functionality and design. Do not regenerate the entire HTML page or rely on a predetermined repair script. "
    "Present the actual changes, validation results, and approval request. Once approved, commit, deploy, and verify that the project works."
)
PROJECT = project_context.resolve(FULL_PROMPT, {"messages": []})


class FakeEngine:
    def __init__(self):
        self.calls = []
    def generate_events(self, payload, cancelled):
        self.calls.append(payload)
        yield {"type": "DELTA", "text": '{"schema":"patch"}'}
        yield {"type": "COMPLETED", "phase": "COMPLETE"}


class DurableRepairRouteTests(unittest.TestCase):
    def setUp(self):
        self.assertEqual(PROJECT["project"], "interactive-3d-model-viewer")
        self.engine = FakeEngine()
        self.context = SimpleNamespace(
            resolve=project_context.resolve,
            read_project_source=Mock(return_value={"source": "<html></html>", "blobSha": "a"*40}),
            evidence=Mock(return_value="Verified Git blob: " + "a"*40),
        )
        self.approval = SimpleNamespace(
            repair_intent=approval_code.repair_intent,
            has_pending=Mock(return_value=False),
            confirm=Mock(return_value={"dispatched": True, "project": PROJECT["project"],
                                       "workflowUrl": "https://github.com/owner/repo/actions"}),
        )
        self.runtime = SimpleNamespace(run=Mock())
        self.patch = patch.object(bridge, "_components",
                                  return_value=(self.context, self.approval, self.runtime))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def route(self, text=FULL_PROMPT, user_id="acct:durable-owner", owner_google_id="google:owner"):
        return bridge.route_events(
            user_id=user_id, owner_google_id=owner_google_id, thread_id="thread-a", prompt=text,
            engine=self.engine, cancelled=lambda: False,
            base_payload={"prompt": text, "history": []})

    def test_exact_user_prompt_enters_existing_project_not_coder_evidence_gate(self):
        self.assertTrue(approval_code.repair_intent(FULL_PROMPT))
        stream = self.route(user_id="guest:unverified", owner_google_id="")
        self.assertIsNotNone(stream)
        events = list(stream)
        phases = [e.get("phase") for e in events]
        self.assertIn("EXISTING_PROJECT_REPAIR_SELECTED", phases)
        self.assertIn("EXISTING_PROJECT_REPAIR_AUTH_REQUIRED", phases)
        self.assertNotIn("EVIDENCE_REQUIRED", phases)
        self.assertFalse(any("NOVERIFIEDHTMLCODEARTIFACT" in str(e) for e in events))
        self.assertEqual(events[-1]["type"], "COMPLETED")
        self.assertEqual(self.engine.calls, [])
        self.context.read_project_source.assert_not_called()

    def test_owner_source_failure_is_blocker_never_fresh_artifact(self):
        self.context.read_project_source.side_effect = RuntimeError("source missing")
        events = list(self.route())
        self.assertIn("EXISTING_PROJECT_SOURCE_UNAVAILABLE",
                      [e.get("phase") for e in events])
        self.assertTrue(any("No replacement HTML" in e.get("text", "") for e in events))
        self.assertEqual(self.engine.calls, [])
        self.runtime.run.assert_not_called()

    def test_authenticated_verified_source_to_model_repair_and_diff_review(self):
        def run(payload, coder):
            self.assertEqual(payload["activeHtmlProject"]["project"], PROJECT["project"])
            self.assertEqual(payload["htmlRepairOwner"], "google:owner")
            self.assertEqual(payload["htmlRepairThreadId"], "thread-a")
            self.assertIn("Verified Git blob:", payload["projectFileEvidence"])
            self.assertEqual(list(coder({"prompt": "model JSON patch"}))[-1]["type"], "COMPLETED")
            yield {"type": "STATUS", "phase": "REPAIR_MODEL_PATCH"}
            yield {"type": "WIDGET", "widget": {"data": {
                "repairDiffs": {"index.html": "--- before\n+++ after\n+fixed"}
            }}}
            yield {"type": "DELTA", "text": "Validated static patch pending owner review."}
            yield {"type": "COMPLETED", "phase": "COMPLETE"}
        self.runtime.run.side_effect = run
        events = list(self.route())
        self.assertIn("EXISTING_PROJECT_SOURCE_READING",
                      [e.get("phase") for e in events])
        self.assertIn("REPAIR_MODEL_PATCH", [e.get("phase") for e in events])
        self.assertIn("EXISTING_PROJECT_REPAIR_REVIEW",
                      [e.get("phase") for e in events])
        self.assertFalse(any(e.get("type") == "WIDGET" for e in events))
        self.assertTrue(any("index.html" in e.get("text", "") and
                            "+fixed" in e.get("text", "") for e in events))
        self.assertEqual(len(self.engine.calls), 1)
        self.context.read_project_source.assert_called_once()
        self.assertEqual(events[-1]["type"], "COMPLETED")

    def test_approval_is_same_owner_thread_and_explicit_only(self):
        self.approval.has_pending.return_value = True
        events = list(self.route("YES"))
        self.approval.has_pending.assert_called_once_with("google:owner", "thread-a")
        self.approval.confirm.assert_called_once_with("google:owner", "thread-a", True)
        self.assertTrue(any("dispatched" in e.get("text", "").lower() for e in events))
        self.assertTrue(any("not a merged PR" in e.get("text", "") for e in events))
        self.assertEqual(self.engine.calls, [])
        self.approval.confirm.reset_mock()
        events = list(self.route("NO"))
        self.approval.confirm.assert_called_once_with("google:owner", "thread-a", False)
        self.assertEqual(events[-1]["type"], "COMPLETED")

    def test_server_signed_google_subject_is_required(self):
        claims = {"sub": "acct:durable-owner",
                  "identity": {"provider": "google",
                               "providerSubject": "123456789012345678901"}}
        self.assertEqual(bridge.verified_owner_from_session(
            claims, "acct:durable-owner"), "google:123456789012345678901")
        self.assertEqual(bridge.verified_owner_from_session(
            claims, "acct:someone-else"), "")
        self.assertEqual(bridge.verified_owner_from_session(
            {"sub": "acct:durable-owner", "identity": {
                "provider": "github", "providerSubject": "123456789012345678901"}},
            "acct:durable-owner"), "")
        self.assertEqual(bridge.verified_owner_from_session(
            {"sub": "acct:durable-owner"}, "acct:durable-owner"), "")

    def test_ingress_binds_only_verified_session_owner(self):
        source = (Path(__file__).parents[1] / "api/lalm_station.py").read_text()
        self.assertIn("verify_session(request.cookies.get(SESSION_COOKIE))", source)
        self.assertIn("verified_owner_from_session(signed_claims, user_id)", source)
        self.assertIn('"ownerGoogleId": verified_owner_google_id', source)

    def test_other_chat_and_prohibited_repair_is_unchanged(self):
        self.assertIsNone(self.route("Hello"))
        self.assertIsNone(self.route("Inspect the project but do not repair it"))
        self.assertIsNone(self.route("Generate a new HTML page"))
        self.assertIsNone(self.route("Repair a project not named here"))
        self.assertEqual(self.engine.calls, [])

    def test_real_queue_source_calls_owner_route_before_engine(self):
        source = (Path(__file__).parents[1] / "queues/swrlz_generation_v3.py").read_text()
        self.assertIn("from api.durable_project_repair_v1 import route_events", source)
        self.assertIn('prompt=prompt_text,', source)
        self.assertIn("if selected_events is not None", source)
        self.assertIn('owner_google_id=str(data.get("ownerGoogleId") or "")', source)
        self.assertIn("else engine.generate_events(engine_payload, cancelled)", source)
        self.assertLess(source.index("selected_events = route_events("),
                        source.index("for raw in (selected_events"))


if __name__ == "__main__":
    unittest.main()
