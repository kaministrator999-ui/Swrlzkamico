import os,unittest
from unittest.mock import patch
from api import html_project_local_browser_v1 as local
class LocalBrowserTests(unittest.TestCase):
    def test_missing_namespace_runtime_fails_closed(self):
        with patch.object(local.shutil,"which",return_value=None):
            with self.assertRaisesRegex(local.LocalBrowserError,"REQUIRED_SYSTEM_PACKAGES"):
                local.command()
    def test_unsigned_local_request_never_runs(self):
        with patch.dict(os.environ,{"SWRLZ_BROWSER_WORKER_KEY":""}),patch.object(local,"run_isolated") as run:
            with self.assertRaisesRegex(local.LocalBrowserError,"SIGNING_KEY"):
                local.validate_local("fixture",{"index.html":"<html></html>"})
            run.assert_not_called()
    def test_invalid_isolation_does_not_sign(self):
        with patch.object(local,"run_isolated",side_effect=local.LocalBrowserError("LOCAL_BROWSER_NAMESPACE_UNAVAILABLE")):
            with self.assertRaisesRegex(local.LocalBrowserError,"NAMESPACE_UNAVAILABLE"):
                local.validate_local("fixture",{"index.html":"<html></html>"},key="a"*64)
