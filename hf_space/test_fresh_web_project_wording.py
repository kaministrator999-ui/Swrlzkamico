"""Natural creation wording keeps separate web projects out of old source scope."""
import unittest

from brain_programming import programming_intent
from programming_repair_context import fresh_project_history
from response_cognition import requests_web_source


VIEWER = '```html file=index.html\n<!doctype html><html><body><h1>Viewer</h1><script>window.fixture=true;</script></body></html>\n```'
HISTORY = [
    {'role': 'user', 'text': 'Create a viewer HTML page'},
    {'id': 'viewer-answer', 'role': 'assistant', 'text': VIEWER,
     'meta': {'codeArtifactId': 'viewer', 'artifactRevision': 1,
              'artifactSourceHash': 'a' * 64, 'artifactSourceSnapshot': VIEWER}},
]


class FreshWebProjectWording(unittest.TestCase):
    def test_independent_named_creation_drops_previous_project_source_and_heading(self):
        prior = programming_intent(HISTORY[0]['text'], [], [])
        prior['intentContract']['literalUiText'] = [{'target': 'heading', 'text': 'Old heading'}]
        for prompt in (
            'Can you do a 3D model editor page',
            'Build 3D model editor page',
            'Now make a 3d model editor html page',
            'Make a separate page for a 3d editor',
            'Create an HTML page',
            'Make an HTML editor page with the same colors',
            'Create another editor page using that viewer colors',
            'Build a standalone web page for editing models',
            'Write a model viewer web page',
            'Create a page for a text editor',
        ):
            with self.subTest(prompt=prompt):
                self.assertTrue(requests_web_source(prompt))
                state = programming_intent(prompt, HISTORY, [], prior)
                self.assertTrue(state['codingTask'])
                self.assertTrue(state['newProject'])
                self.assertEqual(state['projectContext'], 'new')
                self.assertEqual(state['intentContract']['originalRequest'], prompt)
                self.assertFalse(state['intentContract']['literalUiText'])
                self.assertFalse(state['artifactMutationRequested'])
                self.assertEqual(state['artifactTargetId'], '')
                self.assertEqual(fresh_project_history(HISTORY, state), [])

    def test_explicit_current_page_conversion_stays_owned_edit(self):
        prior = programming_intent(HISTORY[0]['text'], [], [])
        for prompt in (
            'Turn this viewer into a 3D model editor page',
            'Make this viewer into a 3d model editor page',
            'Now can you make this viewer into a 3d editor html page',
            'Make that existing viewer page into an editor',
            'Make it a 3D model editor page',
            'Make this one a 3D model editor page',
        ):
            with self.subTest(prompt=prompt):
                state = programming_intent(prompt, HISTORY, [], prior)
                self.assertTrue(state['codingTask'])
                self.assertFalse(state['newProject'])
                self.assertTrue(state['artifactMutationRequested'])
                self.assertEqual(state['artifactTargetId'], 'viewer')
                self.assertEqual(fresh_project_history(HISTORY, state), HISTORY)

    def test_assets_and_written_pages_are_not_application_creation(self):
        for prompt in (
            'Create a 3D mesh for a model editor HTML page',
            'Create a rigged character for a 3D viewer page',
            'Make a music track for a separate editor page',
            'Write a page about a 3D editor',
            'Write a proposal for an HTML editor page',
            'Write a page for a poem about a 3D model editor',
        ):
            with self.subTest(prompt=prompt):
                self.assertFalse(requests_web_source(prompt))


if __name__ == '__main__':
    unittest.main()
