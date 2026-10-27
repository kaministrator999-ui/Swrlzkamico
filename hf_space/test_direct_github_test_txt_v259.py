"""v259: a plain test-file request is complete and should not open a form."""
import base64
import ast
import hashlib
import pathlib
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from github_txt_intent_v256 import wants_direct_github_test_txt as direct
from github_txt_intent_v256 import wants_github_text_file_creation as action
import github_sandbox_create_txt as txt


class DirectTestTxt(unittest.TestCase):
    def setUp(self):
        txt._pending.clear()
        self.owner = {"id": "google:verified"}
        self.created = False
        self.puts = []
        self.gets = []
        def request(method, path, token, body=None):
            self.assertEqual(token, "verified-existing-oauth")
            self.assertTrue(path.startswith("write-action-tests/chat-test-"))
            self.assertTrue(path.endswith(".txt"))
            if method == "GET":
                self.gets.append(path)
                if not self.created: return 404, None
                return 200, {"content": self.puts[-1]["content"]}
            if method == "PUT":
                self.assertNotIn("sha", body)
                self.assertEqual(body["branch"], "main")
                self.assertFalse(self.created)
                self.puts.append(body)
                self.created = True
                return 201, {"commit": {"sha": "verified-commit"}}
            raise AssertionError(method)
        self.auth = patch.object(txt, "_authorized", side_effect=lambda user: "verified-existing-oauth" if user==self.owner else self._reject())
        self.req = patch.object(txt, "_request", side_effect=request)
        self.auth.start()
        self.req.start()

    @staticmethod
    def _reject():
        raise txt.WriteError("GITHUB_OWNER_REQUIRED",403)

    def tearDown(self):
        self.req.stop()
        self.auth.stop()
        txt._pending.clear()

    def test_direct_plain_request_creates_verifiable_harmless_defaults(self):
        prompt="Can you create a test text file in the repo"
        self.assertTrue(direct(prompt))
        result=txt.create_requested_test_file(self.owner,"accepted-user-turn-1",prompt)
        self.assertTrue(result["verified"])
        self.assertEqual(result["commitSha"],"verified-commit")
        self.assertEqual(len(self.puts),1)
        self.assertEqual(len(self.gets),3) # preflight + confirm preflight + readback
        raw=base64.b64decode(self.puts[0]["content"])
        self.assertIn(b"Hello from",raw)
        self.assertIn(b"test",raw)
        self.assertNotIn(b"google:verified",raw)
        self.assertEqual(result["path"],self.gets[0])
        self.assertEqual(result["repo"],"kaministrator999-ui/Swrlzing-core")

    def test_same_user_turn_does_not_create_a_second_file(self):
        prompt="Can you create a test text file in the repo"
        result=txt.create_requested_test_file(self.owner,"accepted-user-turn-1",prompt)
        with self.assertRaises(txt.WriteError) as raised:
            txt.create_requested_test_file(self.owner,"accepted-user-turn-1",prompt)
        self.assertEqual(raised.exception.code,"FILE_ALREADY_EXISTS")
        self.assertEqual(len(self.puts),1)
        self.assertTrue(result["verified"])

    def test_login_is_still_mandatory(self):
        with self.assertRaises(txt.WriteError):
            txt.create_requested_test_file({"id":"google:other"},"req-2","Create a test txt file in our repo")
        self.assertEqual(len(self.puts),0)

    def test_ambiguous_requests_still_review_and_never_execute(self):
        cases=[
            "Can you create a text file in the repo",
            "Can you create a test text file in the repo with my password",
            "Can you create a test text file in another repository",
            "Can you create a test text file in the repo without permission",
            "Can you create a test text file in the repo named custom.txt",
            "How do I create a test text file in the repo?",
            "Do not create a test text file in the repo",
            "Write Python code that creates a test text file in the repo",
            "Can you delete a test text file in the repo",
        ]
        for prompt in cases:
            with self.subTest(prompt=prompt):
                self.assertFalse(direct(prompt),prompt)
                with self.assertRaises(txt.WriteError):
                    txt.create_requested_test_file(self.owner,"req",prompt)
        self.assertEqual(len(self.puts),0)

    def test_connected_route_uses_verified_id_and_is_not_model_output(self):
        src=(pathlib.Path(__file__).parent/"station.py").read_text(encoding="utf-8")
        self.assertIn('elif wants_direct_github_test_txt(prompt):',src)
        self.assertIn('{"userId": google_owner, "prompt": prompt}',src)
        self.assertIn('create_requested_test_file(',src)
        branches=[node for node in ast.walk(ast.parse(src)) if isinstance(node,ast.If)
            and any(isinstance(call,ast.Call) and isinstance(call.func,ast.Name)
                    and call.func.id=='wants_github_text_file_creation' for call in ast.walk(node.test))
            and any(isinstance(statement,ast.Assign) and any(isinstance(target,ast.Subscript)
                    and isinstance(target.value,ast.Name) and target.value.id=='payload'
                    and isinstance(target.slice,ast.Constant) and target.slice.value=='githubChatFileAction'
                    for target in statement.targets) for statement in node.body)]
        self.assertEqual(len(branches),1)
        condition=compile(ast.Expression(branches[0].test),'Station TXT route','eval')
        for local,expected in ((False,True),(True,False)):
            self.assertEqual(eval(condition,{'__builtins__':{}},{'prompt':'Create a text file',
                'local_project_intent':local,'wants_github_text_file_creation':lambda prompt:True}),expected)
        self.assertNotIn('githubDirectTestTxt"] = True',src)

if __name__=="__main__":
    unittest.main()
