"""Admission preserves long pasted source; model context fitting remains separate."""
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
import station


class LargePromptBoundary(unittest.TestCase):
    def setUp(self):
        self.session = {'revision': 0, 'ownerGoogleId': 'anonymous', 'currentId': '',
                        'activeGeneration': None, 'threads': []}
        self.patches = [
            patch.object(station, '_sessions', {'boundary-session': self.session}),
            patch.object(station, '_account_session', return_value=(None, None)),
            patch.object(station, 'routes', return_value=[SimpleNamespace(model_id='700m', available=True)]),
            patch.object(station._pool, 'submit'),
        ]
        self.mocks = [p.start() for p in self.patches]
        for p in self.patches:
            self.addCleanup(p.stop)
        self.client = TestClient(station.app)
        self.addCleanup(self.client.close)
        self.client.cookies.set('swrlz_hf_sid', 'boundary-session')

    def send(self, prompt):
        return self.client.post('/api/lalm_station/send', json={
            'modelId': '700m', 'prompt': prompt, 'threadId': 'boundary-thread',
            'requestId': 'boundary-request', 'assistantMessageId': 'boundary-answer'})

    def test_longer_than_previous_cap_reaches_worker_and_history_unchanged(self):
        prompt = 'Review this source:\n' + ('x' * (32769 - len('Review this source:\n') - 8)) + '\nTHE-END'
        self.assertEqual(len(prompt), 32769)
        response = self.send(prompt)
        self.assertEqual(response.status_code, 202, response.text)
        self.assertEqual(self.session['threads'][0]['messages'][0]['text'], prompt)
        self.mocks[-1].assert_called_once()
        payload = next(value for value in self.mocks[-1].call_args.args if isinstance(value, dict) and 'prompt' in value)
        self.assertEqual(payload['prompt'], prompt)

    def test_maximum_is_accepted_without_shortening(self):
        prompt = 'x' * station.MAX_PROMPT_CHARS
        self.assertEqual(self.send(prompt).status_code, 202)
        self.assertEqual(self.session['threads'][0]['messages'][0]['text'], prompt)
        self.mocks[-1].assert_called_once()

    def test_one_character_over_maximum_rejects_before_history_or_worker(self):
        response = self.send('x' * (station.MAX_PROMPT_CHARS + 1))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.session['threads'], [])
        self.assertIsNone(self.session['activeGeneration'])
        self.mocks[-1].assert_not_called()

    def test_frontend_composer_and_server_character_bounds_match(self):
        class Composer(HTMLParser):
            value = None
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == 'textarea' and attrs.get('id') == 'prompt':
                    self.value = int(attrs['maxlength'])
        parser = Composer()
        parser.feed((Path(__file__).resolve().parents[1] / 'chat/§wyrlz/index.html').read_text())
        self.assertEqual(parser.value, 131072)
        self.assertEqual(parser.value, station.MAX_PROMPT_CHARS)


if __name__ == '__main__':
    unittest.main()
