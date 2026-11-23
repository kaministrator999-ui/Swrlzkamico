"""Pure offline safety tests for the existing-Space HTML release lane."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import hf_html_project_publish_v1 as m

class PublishTests(unittest.TestCase):
    def setUp(self):
        self.dir=tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root=Path(self.dir.name)/"html-projects"
        (self.root/"sample").mkdir(parents=True)
        (self.root/"sample"/"index.html").write_text("<!doctype html><title>Test</title>")
        self.p=patch.object(m,"PROJECT_ROOT",self.root)
        self.p.start()
        self.addCleanup(self.p.stop)

    def test_valid_manifest_scoped_and_encoded(self):
        receipt=m.manifest("sample")
        self.assertEqual(receipt["count"],1)
        self.assertTrue(receipt["destinationPrefix"].startswith("chat/§wyrlz/projects/sample/"))
        self.assertIn("/projects/sample/index.html",receipt["url"])

    def test_bad_slugs(self):
        for slug in ("../oops","a/b","A", "bad_thing", ".hidden"):
            with self.subTest(slug=slug), self.assertRaises(ValueError):
                m.manifest(slug)

    def test_unapproved_cannot_publish(self):
        with self.assertRaises(PermissionError):
            m.publish("sample","no")

    def test_no_index(self):
        (self.root/"sample"/"index.html").unlink()
        with self.assertRaises(ValueError):
            m.manifest("sample")

    def test_disallowed_file(self):
        (self.root/"sample"/"payload.py").write_text("print('bad')")
        with self.assertRaises(ValueError):
            m.manifest("sample")

    def test_symlink(self):
        (self.root/"sample"/"link.js").symlink_to(self.root/"sample"/"index.html")
        with self.assertRaises(ValueError):
            m.manifest("sample")

if __name__ == "__main__":
    unittest.main()
