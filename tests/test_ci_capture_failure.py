"""Failure visibility must preserve exit status, redact credentials, and escape annotations."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/ci_capture_failure.py'
spec = importlib.util.spec_from_file_location('ci_capture_failure', SCRIPT)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class FailureVisibilityTests(unittest.TestCase):
    def run_command(self, source, extra=None):
        env = dict(os.environ, SWRLZ_TEST_SECRET='synthetic-sensitive-value', **(extra or {}))
        return subprocess.run([sys.executable, str(SCRIPT), '--label', 'Synthetic boundary', '--',
                               sys.executable, '-c', source], env=env, text=True, capture_output=True)

    def test_failed_command_retains_status_redacts_and_escapes(self):
        result = self.run_command('import os,sys;print(os.environ["SWRLZ_TEST_SECRET"]);print("literal%0A");print("::warning::literal text");sys.exit(7)')
        self.assertEqual(result.returncode, 7)
        self.assertNotIn('synthetic-sensitive-value', result.stdout)
        self.assertIn('[REDACTED]', result.stdout)
        annotation = [line for line in result.stdout.splitlines() if line.startswith('::error::')]
        self.assertEqual(len(annotation), 1)
        self.assertIn('Synthetic boundary failed with exit 7.', annotation[0])
        self.assertIn('literal%250A%0A::warning::literal text', annotation[0])

    def test_success_does_not_emit_failure(self):
        result = self.run_command('print("Successful browser checks")')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Successful browser checks', result.stdout)
        self.assertNotIn('::error::', result.stdout)

    def test_annotation_is_bounded_and_multiline_credentials_redact(self):
        value = '%\n§' * 10000
        encoded = helper.annotation_text(value)
        self.assertLessEqual(len(encoded.encode('utf-8')), 7600)
        self.assertNotIn('\n', encoded)
        secrets = helper.credential_values({'PRIVATE_KEY': 'first-sensitive-line\nsecond-sensitive-line', 'PATH': '/ordinary/path'})
        self.assertEqual(helper.redact('first-sensitive-line\nsecond-sensitive-line', secrets), '[REDACTED]')
        self.assertEqual(helper.redact('second-sensitive-line\n', secrets), '[REDACTED]\n')


if __name__ == '__main__':
    unittest.main()
