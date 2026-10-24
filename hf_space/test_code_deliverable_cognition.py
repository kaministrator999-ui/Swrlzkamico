"""Feature descriptions must not replace the requested coding operation."""
import unittest
from response_cognition import classify_response_cognition, response_cognition_policy


class CodeDeliverableCognition(unittest.TestCase):
    def test_application_features_do_not_change_requested_medium_or_operation(self):
        for prompt in (
            "Create a single-file HTML 3D viewer with drag to inspect the scene.",
            "Build a 3D HTML model viewer to inspect uploaded models.",
            "Can you write an HTML page with a message box and review button?",
            "Create a web app to compare monthly expenses.",
            "Build a JavaScript music application with audio controls.",
            "Create a Python script to analyze uploaded data.",
        ):
            with self.subTest(prompt=prompt):
                state = classify_response_cognition(prompt, [], {"codingTask": True})
                self.assertEqual(state["operation"], "create")
                self.assertEqual(state["deliverable"], "code")
                self.assertNotIn("needs a real supported engine/export", response_cognition_policy(state))

    def test_actual_asset_audio_and_written_requests_keep_their_medium(self):
        for prompt, medium in (
            ("Create a rigged 3D character model for my web application.", "3d-asset"),
            ("Create a 3D mesh using Python.", "3d-asset"),
            ("Create a music track for my JavaScript game.", "audio"),
            ("Write a poem about Python and HTML.", "text"),
        ):
            with self.subTest(prompt=prompt):
                self.assertEqual(classify_response_cognition(prompt)["deliverable"], medium)

    def test_analysis_and_corrections_keep_the_requested_action(self):
        self.assertEqual(classify_response_cognition("Review this HTML 3D viewer code.")["operation"], "analyze")
        self.assertEqual(classify_response_cognition("Explain how to create a 3D HTML viewer.")["operation"], "explain")
        history = [{"role": "user", "content": "Create an HTML viewer."}]
        self.assertEqual(classify_response_cognition("No, I meant create a viewer with zoom.", history)["operation"], "correct")


if __name__ == "__main__":
    unittest.main()
