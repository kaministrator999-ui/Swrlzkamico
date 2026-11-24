"""Deterministic no-network regressions for Valkey egress and code completion."""
from __future__ import annotations
import ast
import re
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import hf_valkey_revision_sync_optimization as revision
import hf_code_finish_and_preview_v1 as finish

class FakeProjectArchive:
    @staticmethod
    def parse_project_files(text):
        fence=chr(96)*3
        if not text.rstrip().endswith(fence):raise ValueError("missing close")
        lines=text.strip().splitlines()
        if not lines[0].startswith(fence+"html file=index.html project=cool-webpage"):
            raise ValueError("bad header")
        body="\n".join(lines[1:-1])
        return [{"path":"index.html","content":body}]

def extract_helper():
    source=finish.HELPER
    node=next(n for n in ast.parse(source).body
              if isinstance(n,ast.FunctionDef) and n.name=="_swrlz_close_complete_html_fence")
    scope=ast.Module(body=[node],type_ignores=[])
    ns={"re":re}
    exec(compile(scope,"<html-proof>","exec"),ns)
    return ns["_swrlz_close_complete_html_fence"]

class HtmlClosureTests(unittest.TestCase):
    def setUp(self):
        self.existing=sys.modules.get("project_archive")
        sys.modules["project_archive"]=types.SimpleNamespace(parse_project_files=FakeProjectArchive.parse_project_files)
        self.closer=extract_helper()
        self.head=chr(96)*3+"html file=index.html project=cool-webpage\n"
        self.body='<!DOCTYPE html><html><head><title>X</title></head><body><div>Hi</div><script>const x=2;</script></body></html>'

    def tearDown(self):
        if self.existing is None:sys.modules.pop("project_archive",None)
        else:sys.modules["project_archive"]=self.existing

    def test_missing_fence_is_closed_without_changing_file_or_body(self):
        old=self.head+self.body
        value,ok=self.closer(old)
        self.assertTrue(ok)
        self.assertEqual(value,old+"\n"+chr(96)*3+"\n")

    def test_existing_complete_fence_is_not_rewritten(self):
        old=self.head+self.body+"\n"+chr(96)*3+"\n"
        value,ok=self.closer(old)
        self.assertTrue(ok)
        self.assertEqual(value,old)

    def test_does_not_hide_incomplete_js_or_partial_html(self):
        for body in ('<!DOCTYPE html><html><body>Hello','<!DOCTYPE html><html><body><script>const a=3;</body></html>',
                     '<!DOCTYPE html><html><body><h1>x</h1></html>',
                     '<!DOCTYPE html><html><body><style>a {color:red;</body></html>'):
            with self.subTest(body=body):
                value,ok=self.closer(self.head+body)
                self.assertFalse(ok)
                self.assertEqual(value,self.head+body)

    def test_does_not_repackage_multifile_or_unrelated_source(self):
        src=self.head+self.body+"\n"+chr(96)*3+"\n"+chr(96)*3+"css file=main.css\nx{}\n"
        self.assertFalse(self.closer(src)[1])
        self.assertFalse(self.closer("plain text")[1])

class TelemetryTruthTests(unittest.TestCase):
    def test_provider_length_remains_length_when_complete(self):
        before='''from typing import Any
def completion_validation(validation: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    result=dict(validation or {})
    reason=observation.get("finishReason")
    result["finishReason"]=reason
    result["generationComplete"]=True if reason=="stop" else False if reason=="length" else None
    if reason=="length":
        result["status"]="REJECT"
        result["reasons"]=list(dict.fromkeys([*(result.get("reasons") or []),"model-output-token-limit"]))
    return result
'''
        updated=finish.patch_telemetry(before.encode("utf-8")).decode("utf-8")
        ns={}
        exec(compile(updated,"<completion>","exec"),ns)
        fn=ns["completion_validation"]
        incomplete=fn({"status":"PASS","reasons":[]},{"finishReason":"length"})
        self.assertEqual(incomplete["status"],"REJECT")
        self.assertEqual(incomplete["finishReason"],"length")
        complete=fn({"status":"PASS","reasons":[]},
                    {"finishReason":"length","sourceCompleteByParser":True})
        self.assertEqual(complete["status"],"PASS")
        self.assertEqual(complete["finishReason"],"length")
        self.assertEqual(complete["generationComplete"],True)
        invalid=fn({"status":"REJECT","reasons":["bad-feature"]},
                   {"finishReason":"length","sourceCompleteByParser":True})
        self.assertEqual(invalid["status"],"REJECT")
        self.assertIn("bad-feature",invalid["reasons"])
        self.assertFalse(invalid.get("generationComplete"))

class RevisionTests(unittest.TestCase):
    def test_revision_parser_lua_is_non_mutating(self):
        self.assertIn("redis.call('GET'",revision.REV_HELPER)
        self.assertNotIn("redis.call('SET'",revision.REV_HELPER)
        self.assertNotIn("redis.call('DEL'",revision.REV_HELPER)

    def test_fail_closed_on_unknown_state(self):
        class FakeHTTPException(Exception):
            def __init__(self,code,description):self.status_code=code;super().__init__(description)
        class Redis:
            response=0
            def _redis(self,conf,*args):return self.response
        fake=Redis()
        src=revision.patch_account(b"def load_chat(owner):\n    pass\n").decode()
        nodes=[n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name=="peek_chat_revision"]
        scope={"_config":lambda:{"x":1},"_chat_key":lambda owner:"safe","gh":fake,
               "HTTPException":FakeHTTPException,"_CHAT_REVISION_LUA":"return 0"}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),"<revision>","exec"),scope)
        for value in (0,17,-1):
            fake.response=value
            self.assertEqual(scope["peek_chat_revision"]("google:safe"),value)
        for value in (-2,None,"3",1.3,True):
            fake.response=value
            with self.subTest(value=value),self.assertRaises(FakeHTTPException):
                scope["peek_chat_revision"]("google:safe")

if __name__=="__main__":
    unittest.main()
