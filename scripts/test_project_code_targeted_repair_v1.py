from __future__ import annotations
import json,unittest
from project_code_targeted_repair_v1 import (
    TargetedRepairError,source_sha,patch_context,parse_patch,
    apply_patch,monotonic_progress,VERSION,
)

HTML=('<html><head><title>§C</title></head><body>'
      '<button id="save">Save</button><script>const x=1;</script></body></html>')
class PatchTests(unittest.TestCase):
    def patch(self,source=HTML,op="insert_before",anchor="</head>",code="<style>.btn{color:red}</style>"):
        return json.dumps({"sourceSha256":source_sha(source),"op":op,
                           "anchor":anchor,"code":code},ensure_ascii=False)
    def test_preserve_existing_bytes(self):
        updated,receipt=apply_patch(HTML,self.patch())
        self.assertEqual(updated,HTML.replace("</head>","<style>.btn{color:red}</style></head>"))
        self.assertEqual(receipt["removedBytes"],0)
        self.assertEqual(receipt["preservedSuffixChars"],len(HTML)-HTML.index("</head>"))
        self.assertEqual(receipt["before"],source_sha(HTML))
        self.assertEqual(receipt["after"],source_sha(updated))
    def test_second_repair_after_first(self):
        revised,_=apply_patch(HTML,self.patch())
        second=self.patch(revised,"insert_before","</body>",
            '<script>document.getElementById("save").onclick=()=>{}</script>')
        result,_=apply_patch(revised,second)
        self.assertIn('<style>',result)
        self.assertIn('id="save"',result)
        self.assertIn("onclick",result)
    def test_small_replace(self):
        updated,receipt=apply_patch(HTML,self.patch(HTML,"replace_once",
              '<button id="save">Save</button>','<button id="save" type="button">Save</button>'))
        self.assertIn('type="button"',updated)
        self.assertEqual(receipt["removedBytes"],len('<button id="save">Save</button>'))
    def test_complete_tail(self):
        src='<html><body><script>const a=1;'
        updated,_=apply_patch(src,self.patch(src,"append","",'</script></body></html>'))
        self.assertTrue(updated.endswith('</html>'))
    def test_ambiguous_anchor(self):
        with self.assertRaises(TargetedRepairError) as check:
            apply_patch("foo foo",self.patch("foo foo","insert_before","foo","bar"))
        self.assertEqual(check.exception.code,"AMBIGUOUS_ANCHOR")
    def test_stale_source(self):
        with self.assertRaises(TargetedRepairError) as check:
            apply_patch(HTML,self.patch(HTML+"changed"))
        self.assertEqual(check.exception.code,"STALE_SOURCE")
    def test_no_rewrite_whole_file(self):
        with self.assertRaises(TargetedRepairError):
            apply_patch("a"*5000,self.patch("a"*5000,"replace_once","a"*3000,"b"))
    def test_binary_code_or_oversize(self):
        with self.assertRaises(TargetedRepairError):
            apply_patch(HTML,self.patch(HTML,"append","","a"*(10001)))
        with self.assertRaises(TargetedRepairError):
            apply_patch(HTML,self.patch(HTML,"append","","a\x00"))
    def test_bad_json(self):
        with self.assertRaises(TargetedRepairError):
            parse_patch("some code")
        with self.assertRaises(TargetedRepairError):
            parse_patch(json.dumps({"op":"append","code":"hi","anchor":""}))
    def test_model_cannot_change_schema(self):
        data=json.loads(self.patch())
        data["approveDeploy"]=True
        with self.assertRaises(TargetedRepairError):
            parse_patch(json.dumps(data))
    def test_progress_requires_removing_known_failure(self):
        old={"status":"REJECT","reasons":["missing-css","missing-js"]}
        self.assertTrue(monotonic_progress(old,{"status":"REJECT","reasons":["missing-js"]}))
        self.assertTrue(monotonic_progress(old,{"status":"PASS","reasons":[]}))
        self.assertFalse(monotonic_progress(old,{"status":"REJECT","reasons":["missing-css","missing-js"]}))
        self.assertFalse(monotonic_progress(old,{"status":"REJECT","reasons":["new-regression"]}))
    def test_source_tail_context(self):
        long=HTML*120
        context=patch_context(long,["missing-required-language:css"],"improve existing page")
        self.assertEqual(len(context),2)
        self.assertIn(source_sha(long),context[1]["content"])
        self.assertIn("missing-required-language:css",context[1]["content"])
        self.assertLessEqual(len(context[1]["content"]),12500)
        self.assertIn("not rewriting",context[0]["content"])
    def test_fences(self):
        fence=chr(96)*3
        raw=fence+"json\n"+self.patch()+"\n"+fence
        self.assertEqual(parse_patch(raw)["op"],"insert_before")

if __name__=="__main__":unittest.main()
