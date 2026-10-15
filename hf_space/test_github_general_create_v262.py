"""General GitHub CREATE_FILE permissions, paths, binary fidelity and approvals."""
import base64
import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import github_general_create_v262 as f
import github_connection as github
from github_create_intent_v262 import wants_github_general_file_proposal as intent


class GeneralCreateTest(unittest.TestCase):
    def setUp(self):
        f._pending.clear()
        self.user="google:owner"
        self.repo="kaministrator999-ui/Swrlzing-core"
        self.branch="main"
        self.token="existing-oauth"
        self.contents={}
        self.puts=[]
        self.calls=[]
        def auth(uid,expected_repo=None):
            if uid!=self.user:raise f.CreateFileError("GOOGLE_SIGN_IN_REQUIRED",401)
            if expected_repo and self.repo!=expected_repo:raise f.CreateFileError("SELECTED_REPOSITORY_CHANGED_OR_UNSUPPORTED",403)
            return {"token":self.token,"repo":self.repo,"branch":self.branch}
        def fake_api(method,authorization,path,data=None):
            self.calls.append((method,path))
            self.assertEqual(authorization["repo"],self.repo)
            self.assertEqual(authorization["token"],self.token)
            if method=="GET":
                if path not in self.contents:return 404,None
                return 200,{"encoding":"base64","content":base64.b64encode(self.contents[path]).decode("ascii")}
            if method=="PUT":
                self.assertNotIn("sha",data)
                self.assertNotIn(path,self.contents)
                self.assertEqual(data["branch"],self.branch)
                raw=base64.b64decode(data["content"],validate=True)
                self.contents[path]=raw
                self.puts.append((path,raw))
                return 201,{"commit":{"sha":"a"*40}}
            raise AssertionError(method)
        self.patches=[
            patch.object(f,"_authorize",side_effect=auth),
            patch.object(f,"_github",side_effect=fake_api),
        ]
        for p in self.patches:p.start()

    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        f._pending.clear()

    def proposal(self,path,raw,uid=None):
        return f.prepare(uid or self.user,path,base64.b64encode(raw).decode("ascii"))

    def test_source_code_json_dotfile_extensionless_unicode_nested(self):
        cases=[
            ("src/app.py",b"print('hello')\n"),
            ("README.md",b"# Project\n"),
            (".gitignore",b"__pycache__/\n"),
            ("package.json",b'{"name":"test"}\n'),
            ("data/a.csv",b"a,b\n1,2\n"),
            ("docs/日本語.txt","こんにちは".encode()),
            ("LICENSE",b""),
        ]
        for i,(path,raw) in enumerate(cases):
            with self.subTest(path=path):
                proposal=self.proposal(path,raw)
                self.assertEqual(proposal["bytes"],len(raw))
                self.assertEqual(proposal["repo"],self.repo)
                self.assertNotIn(path,self.contents)
                result=f.confirm(self.user,proposal["approvalToken"],True)
                self.assertTrue(result["verified"])
                self.assertEqual(self.contents[path],raw)
                self.assertEqual(result["sha256"],hashlib.sha256(raw).hexdigest())
        self.assertEqual(len(self.puts),len(cases))

    def test_binary_bytes_preserved_exactly(self):
        png=b"\x89PNG\r\n\x1a\n"+bytes(range(256))+b"\x00\xff"*1024
        proposal=self.proposal("assets/logo.png",png)
        receipt=f.confirm(self.user,proposal["approvalToken"],True)
        self.assertEqual(self.contents["assets/logo.png"],png)
        self.assertEqual(receipt["bytesWritten"],len(png))
        self.assertIn("logo.png",receipt["url"])

    def test_existing_file_is_never_overwritten(self):
        self.contents["README.md"]=b"Keep original"
        with self.assertRaises(f.CreateFileError) as exc:
            self.proposal("README.md",b"Try overwrite")
        self.assertEqual(exc.exception.code,"FILE_ALREADY_EXISTS")
        self.assertEqual(self.contents["README.md"],b"Keep original")
        self.assertFalse(self.puts)

    def test_double_confirmation_is_single_use(self):
        proposal=self.proposal("a.py",b"pass\n")
        self.assertTrue(f.confirm(self.user,proposal["approvalToken"],True)["verified"])
        with self.assertRaises(f.CreateFileError):
            f.confirm(self.user,proposal["approvalToken"],True)
        self.assertEqual(len(self.puts),1)

    def test_wrong_account_does_not_consume_approval(self):
        proposal=self.proposal("a.py",b"pass\n")
        with self.assertRaises(f.CreateFileError):
            f.confirm("google:other",proposal["approvalToken"],True)
        self.assertEqual(len(self.puts),0)
        self.assertTrue(f.confirm(self.user,proposal["approvalToken"],True)["verified"])

    def test_repo_selection_change_prevents_file_creation(self):
        proposal=self.proposal("src/new.py",b"hello")
        self.repo="kaministrator999-ui/Swrlzkamico"
        with self.assertRaises(f.CreateFileError) as error:
            f.confirm(self.user,proposal["approvalToken"],True)
        self.assertEqual(error.exception.code,"SELECTED_REPOSITORY_CHANGED_OR_UNSUPPORTED")
        self.assertFalse(self.puts)

    def test_cancel_is_not_write(self):
        proposal=self.proposal("src/app.js",b"alert(1)")
        self.assertEqual(f.confirm(self.user,proposal["approvalToken"],False)["code"],"USER_DECLINED")
        self.assertFalse(self.puts)

    def test_traversal_or_control_characters_blocked(self):
        invalid=["/root.txt","dir/../secret.txt","./foo",".git/config","dir/.git/obj",
                 "dir\\foo","dir//foo","dir/","dir/\x00.txt","dir/\nfile",
                 "dir/\u200bfoo","dir/"+"a"*256, "a"*513]
        for path in invalid:
            with self.subTest(path=path),self.assertRaises(f.CreateFileError):
                f.safe_path(path)
        self.assertEqual(f.safe_path(".github/workflows/build.yml"),".github/workflows/build.yml")

    def test_binary_limit_invalid_base64_and_empty_file(self):
        for bad in ("%%%%",None,base64.b64encode(b"\0"*(f.MAX_FILE_BYTES+1)).decode()):
            with self.assertRaises(f.CreateFileError):
                f.decode_file(bad)
        self.assertEqual(f.decode_file(""),b"")

    def test_classification_proposal_not_code_explanation(self):
        positives=["Create a JSON file named package.json in the Github repo",
                   "Upload a PDF file to the repository",
                   "Make a new image logo.png in the repo",
                   "Add a Python file in the GitHub repo",
                   "Put a .gitignore file in the repository"]
        negatives=["How can I create a file in GitHub?",
                   "Now the AI needs to be able to create any file GitHub accepts",
                   "Do not upload a file in the repo",
                   "Explain GitHub file permissions"]
        for prompt in positives:self.assertTrue(intent(prompt),prompt)
        for prompt in negatives:self.assertFalse(intent(prompt),prompt)


class ProviderGrantTest(unittest.TestCase):
    def test_selected_repo_must_be_allowed_and_owner_has_write_grant(self):
        record={"token":"opaque","repo":"kaministrator999-ui/Swrlzkamico",
                "login":"kaministrator999-ui","scopes":"read:user public_repo"}
        with patch.object(github,"_config",return_value={}),\
             patch.object(github,"_load",return_value=record),\
             patch.object(github,"_api",return_value={"full_name":record["repo"],"private":False,
               "default_branch":"main","permissions":{"push":True}}):
            value=f._authorize("google:verified")
            self.assertEqual(value["repo"],record["repo"])
            record["scopes"]="read:user"
            with self.assertRaises(f.CreateFileError) as exc:
                f._authorize("google:verified")
            self.assertEqual(exc.exception.code,"GITHUB_WRITE_SCOPE_REQUIRED")
            record["repo"]="not-owner/other"
            with self.assertRaises(f.CreateFileError):
                f._authorize("google:verified")


if __name__=="__main__":
    unittest.main()
