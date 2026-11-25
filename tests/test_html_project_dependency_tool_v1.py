import json
import unittest
from unittest.mock import patch
from api.html_project_dependency_tool_v1 import localize_imports, DependencyError
from api.html_project_agent_v1 import bind_model_edits, apply_proposal, inspect_static, ProposalError

SRC = '''<!doctype html><html><head><title>Fixture</title><script type="importmap">{"imports":{"tiny":"https://cdn.jsdelivr.net/npm/tiny@1.2.3/lib/main.js","tiny/addons/":"https://unpkg.com/tiny@1.2.3/addons/"}}</script></head><body><button>Keep me</button><script type="module">import { value } from 'tiny';
import { helper } from 'tiny/addons/helper.js';
document.querySelector('button').textContent=value+helper;</script></body></html>'''
MEMBERS={"lib/main.js":"export const value=1;",
         "addons/helper.js":"import { value } from 'tiny';\nexport const helper=value+1;",
         "LICENSE":"MIT fixture license"}
def reader(pkg,v,path):
    if pkg!="tiny" or v!="1.2.3" or path not in MEMBERS:
        raise DependencyError("DEPENDENCY_MODULE_MISSING: "+path)
    return MEMBERS[path],"sha512-fixture"

class DependencyTests(unittest.TestCase):
    def test_model_selects_tool_and_hash_pins_new_assets(self):
        files={"index.html":SRC}
        plan={"patches":[{"path":"index.html","op":"localize_imports",
                          "anchor":'<script type="importmap">',"code":""}]}
        with patch("api.html_project_agent_v1.localize_imports",
                   side_effect=lambda *a:localize_imports(*a,reader=reader)):
            bound=bind_model_edits("fixture",files,plan)
            result=apply_proposal("fixture",files,bound,validation=inspect_static)
            self.assertTrue(result["readyForOwnerReview"])
            self.assertEqual(len(bound["patches"][0]["assetHashes"]),3)
            self.assertEqual(len(result["changedFiles"]),4)
            self.assertIn("<button>Keep me</button>",result["proposedFiles"]["index.html"])
            self.assertNotIn("unpkg.com",result["proposedFiles"]["index.html"])
            self.assertFalse(result["committed"])
            bound["patches"][0]["assetHashes"]={}
            with self.assertRaisesRegex(ProposalError,"DEPENDENCY_ASSET_HASH_MISMATCH"):
                apply_proposal("fixture",files,bound,validation=inspect_static)
    def test_unpinned_and_unknown_network_rejected(self):
        for bad in (SRC.replace("@1.2.3","@latest"),
                    SRC.replace("cdn.jsdelivr.net/npm/","evil.example/npm/")):
            with self.assertRaises(DependencyError):
                localize_imports({"index.html":bad},"index.html",'<script type="importmap">',"",reader=reader)
    def test_non_unique_anchor_rejected(self):
        with self.assertRaises(DependencyError):
            localize_imports({"index.html":SRC},"index.html","script","",reader=reader)

if __name__=="__main__":
    unittest.main()
