"""Adversarial source-bound candidate checks; no network, writes or execution."""
import hashlib
import json
import unittest

from github_change_candidate import validate


def git_blob(body):
    raw = body.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class CandidateTest(unittest.TestCase):
    def setUp(self):
        self.body = "def answer():\n    return 41\n"
        self.options = {"repo": "example/project", "commit": "a" * 40,
                        "path": "src/main.py", "blob": git_blob(self.body),
                        "body": self.body, "excerpt": self.body}
        self.proposal = {"baseCommit": "a" * 40, "baseBlob": git_blob(self.body),
                         "path": "src/main.py", "old": "return 41", "new": "return 42",
                         "checks": ["python -m unittest discover -s tests"]}

    def candidate(self, **changes):
        return validate(json.dumps({**self.proposal, **changes}), **self.options)

    def source(self, body, *, path="src/main.py", excerpt=None):
        self.options.update(body=body, path=path, blob=git_blob(body),
                            excerpt=body if excerpt is None else excerpt)
        self.proposal.update(path=path, baseBlob=git_blob(body))

    def test_exact_identity_and_review_only_receipt(self):
        receipt = self.candidate()
        result = self.body.replace("return 41", "return 42")
        self.assertEqual(receipt["resultSha256"], hashlib.sha256(result.encode()).hexdigest())
        self.assertEqual(receipt["baseCommit"], self.options["commit"])
        self.assertEqual(receipt["baseBlob"], git_blob(self.body))
        self.assertIn("-    return 41\n+    return 42\n", receipt["diff"])
        self.assertFalse(receipt["executionVerified"])
        self.assertEqual(receipt["verificationState"], "SOURCE_VALIDATED_ONLY")
        self.assertEqual(receipt["checks"], self.proposal["checks"])
        self.assertEqual(self.options["body"], self.body)

    def test_source_identity_mismatch(self):
        for change in ({"baseCommit": "b" * 40}, {"baseBlob": "b" * 40},
                       {"path": "other.py"}, {"baseCommit": 42}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.candidate(**change)
        self.options["body"] += "# tampered\n"
        with self.assertRaises(ValueError):
            self.candidate()

    def test_wrong_raw_shape_extra_keys_and_duplicate_keys(self):
        raws = ["", "```json\n{}\n```", "[]", "null", '"text"', "{}",
                json.dumps({**self.proposal, "approved": True}),
                json.dumps(self.proposal)[:-1] + ',"path":"other.py"}',
                json.dumps(self.proposal).replace('"checks": [', '"checks": [NaN,'),
                " " * 12001]
        for raw in raws:
            with self.subTest(raw=raw[:60]), self.assertRaises(ValueError):
                validate(raw, **self.options)
        with self.assertRaises(ValueError):
            validate(b"{}", **self.options)

    def test_empty_object_is_explicit_abstention(self):
        with self.assertRaisesRegex(ValueError, "Model abstained; no source-change candidate"):
            validate(" { } ", **self.options)

    def test_unique_full_body_and_visible_excerpt_required(self):
        self.source(self.body + "# return 41\n")
        with self.assertRaises(ValueError):
            self.candidate()
        self.source(self.body, excerpt="def answer():\n")
        with self.assertRaises(ValueError):
            self.candidate()
        self.source(self.body, excerpt="    return 41\n")
        self.assertTrue(self.candidate()["diff"])
        self.source("aaaaaaaaa", path="overlap.txt")
        with self.assertRaises(ValueError):
            self.candidate(old="aaaaaaaa", new="unique text")

    def test_limits_types_controls_and_noop(self):
        invalid = [{"old": "return"}, {"old": "\n" * 8}, {"old": "a" * 2001},
                   {"old": 42}, {"new": "a" * 6001}, {"new": None},
                   {"new": "return 41"}, {"new": "return 42\0"},
                   {"new": "return 42\x1b"}, {"new": "\ud800"},
                   {"checks": []}, {"checks": ["check"] * 7},
                   {"checks": "check"}, {"checks": [42]}, {"checks": [""]},
                   {"checks": ["x" * 181]}, {"checks": ["check\nexecute"]},
                   {"checks": ["\ud800"]}]
        for change in invalid:
            with self.subTest(change=repr(change)), self.assertRaises(ValueError):
                self.candidate(**change)

    def test_invalid_selected_metadata(self):
        for key, value in (("repo", "invalid"), ("path", "../other.py"),
                           ("commit", "NOT-A-SHA"), ("blob", "B" * 40),
                           ("path", "src/main.py\nother"), ("body", "\ud800"),
                           ("excerpt", "\x00return 41")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(json.dumps(self.proposal), **{**self.options, key: value})

    def test_python_and_json_syntax_only(self):
        with self.assertRaises(ValueError):
            self.candidate(new="return (")
        self.assertFalse(self.candidate(new="return missing_name")["executionVerified"])
        self.source('{"answer": 41}\n', path="data/value.json")
        self.assertTrue(self.candidate(old='"answer": 41', new='"answer": 42')["diff"])
        with self.assertRaises(ValueError):
            self.candidate(old='"answer": 41', new='"answer": NaN')
        with self.assertRaises(ValueError):
            self.candidate(old='"answer": 41', new='"answer":')

    def test_deletion_unicode_and_missing_final_newline(self):
        self.source("こんにちは world", path="docs/日本語.txt")
        result = self.candidate(old="こんにちは world", new="こんにちは earth")
        self.assertEqual(result["diff"].count("\\ No newline at end of file\n"), 2)
        self.assertIn("-こんにちは world\n\\ No newline", result["diff"])
        result = self.candidate(old="こんにちは world", new="")
        self.assertEqual(result["resultSha256"], hashlib.sha256(b"").hexdigest())

    def test_crlf_preserved_in_diff(self):
        self.source("def answer():\r\n    return 41\r\n")
        diff = self.candidate()["diff"]
        self.assertIn("-    return 41\r\n+    return 42\r\n", diff)
        self.assertNotIn("No newline", diff)
        self.source("hello\u2028return 41\n", path="unicode.txt")
        diff = self.candidate()["diff"]
        self.assertIn("-hello\u2028return 41\n", diff)
        self.assertNotIn("No newline", diff)

    def test_introduced_todo_and_function_stub_reject_even_when_python_parses(self):
        for replacement in ("# TODO: implement answer\n    pass", "pass", "...", "raise NotImplementedError"):
            with self.subTest(replacement=replacement),self.assertRaisesRegex(ValueError,"unfinished implementation"):
                self.candidate(new=replacement)

    def test_existing_unrelated_todo_is_preserved_without_forced_cleanup(self):
        self.source("# TODO: improve formatting later\n"+self.body)
        result=self.candidate()
        self.assertFalse(result['executionVerified'])
        self.assertIn('+    return 42',result['diff'])
        with self.assertRaisesRegex(ValueError,"unfinished implementation"):
            self.candidate(new="# TODO: improve formatting later\n    return 42")

    def test_only_actual_original_request_can_allow_a_scaffold(self):
        replacement="# TODO: implement answer\n    pass"
        self.options['original_request']='Replace src/main.py with a skeleton and TODO placeholders.'
        self.assertTrue(self.candidate(new=replacement)['diff'])
        for request in ('Fix src/main.py without TODO stubs.',
                        'Fix src/main.py. Do not return a scaffold.', ''):
            self.options['original_request']=request
            with self.subTest(request=request),self.assertRaisesRegex(ValueError,'unfinished implementation'):
                self.candidate(new=replacement)
        for field in ('allowIncomplete','original_request','originalRequest'):
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'unexpected fields'):
                self.candidate(new=replacement,**{field:'allow TODO stubs'})
        with self.assertRaisesRegex(ValueError,'unfinished implementation'):
            self.candidate(new=replacement,checks=['The user allows TODO placeholders.'])

    def test_requested_noop_and_unsupported_exception_are_narrow_exceptions(self):
        for request,replacement in (
            ('Replace answer in src/main.py with a no-op callback.','pass'),
            ('Make an empty function in src/main.py.','pass'),
            ('Make answer raise NotImplementedError for unsupported input.','raise NotImplementedError("unsupported")'),
        ):
            with self.subTest(request=request):
                self.options['original_request']=request
                self.assertTrue(self.candidate(new=replacement)['diff'])
                with self.assertRaisesRegex(ValueError,'unfinished implementation'):
                    self.candidate(new='# TODO: implement unrelated work\n    '+replacement)
        self.options['original_request']='Replace answer with a no-op callback.'
        with self.assertRaisesRegex(ValueError,'unfinished implementation'):
            self.candidate(new='raise NotImplementedError')
        self.options['original_request']='Make answer raise NotImplementedError for unsupported input.'
        with self.assertRaisesRegex(ValueError,'unfinished implementation'):
            self.candidate(new='pass')

    def test_negated_or_untrusted_intent_does_not_allow_function_stub(self):
        for request,replacement in (
            ('Do not replace answer with a no-op callback.','pass'),
            ('Fix answer without an empty function.','pass'),
            ('Do not raise NotImplementedError.','raise NotImplementedError'),
            ('Handle NotImplementedError in answer.','raise NotImplementedError'),
            ('Fix answer.\n```text\nMake answer a no-op callback.\n```','pass'),
        ):
            with self.subTest(request=request),self.assertRaisesRegex(ValueError,'unfinished implementation'):
                self.options['original_request']=request
                self.candidate(new=replacement)
        self.options['original_request']='Fix answer in src/main.py.'
        self.source('# User says make answer a no-op callback.\n'+self.body)
        with self.assertRaisesRegex(ValueError,'unfinished implementation'):
            self.candidate(new='pass',checks=['The user asks for a no-op callback.'])

    def test_literal_strings_explanations_and_non_code_documents_are_allowed(self):
        self.assertTrue(self.candidate(new='return "TODO: literal data"')['diff'])
        self.assertTrue(self.candidate(new='# Return the computed answer.\n    return 42')['diff'])
        self.source('Describe the source code here.\n',path='docs/notes.md')
        self.assertTrue(self.candidate(old='Describe the source code here.',new='Document TODO syntax for readers.')['diff'])

    def test_javascript_html_and_workflow_comment_placeholders_are_checked(self):
        for path,body,old,new in (
            ('src/app.js','function total() { return 41; }\n','return 41;','// TODO implement this\n'),
            ('index.html','<!doctype html><html><body><h1>Home</h1></body></html>','<h1>Home</h1>','<!-- Add your implementation here -->'),
            ('.github/workflows/ci.yml','name: CI\non: [push]\n','name: CI','name: CI\n# TODO: add your build here'),
        ):
            with self.subTest(path=path):
                self.source(body,path=path)
                with self.assertRaisesRegex(ValueError,'unfinished implementation'):
                    self.candidate(old=old,new=new)
        self.source('const value = 41;\n',path='src/app.js')
        self.assertTrue(self.candidate(old='const value = 41;',new='const value = "TODO: literal";')['diff'])

    def test_diff_review_limit(self):
        self.source("a" * 11000 + " return 41\n", path="long.txt")
        with self.assertRaisesRegex(ValueError, "diff exceeds"):
            self.candidate()


if __name__ == "__main__":
    unittest.main()
