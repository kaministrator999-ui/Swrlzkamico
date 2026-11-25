import unittest,time
from api.browser_worker_protocol_v1 import *
class BrowserProtocolTests(unittest.TestCase):
    def request(self):
        return {"schema":VERSION,"nonce":"a"*32,"timestamp":int(time.time()),"project":"fixture",
                "files":{"index.html":"<html></html>"},"canvas":False,"checks":[]}
    def test_identity_and_receipt(self):
        obj=validate_request(self.request());key="b"*64
        rec={"schema":VERSION,"project":"fixture","nonce":obj["nonce"],"timestamp":obj["timestamp"],"hashes":file_hashes(obj["files"])}
        env={"receipt":rec,"signature":mac(key,"receipt",encode(rec))}
        self.assertEqual(verify_envelope(key,env,project="fixture",hashes=rec["hashes"]),rec)
        with self.assertRaises(ValueError):verify_envelope(key,env,project="fixture",hashes={"index.html":"bad"})
        rec["project"]="other"
        with self.assertRaises(ValueError):verify_envelope(key,env,project="other",hashes=rec["hashes"])
    def test_reject_arbitrary_path_and_execution(self):
        for change in [{"files":{"index.html":"x","../secret.js":"x"}},{"checks":[{"op":"eval","selector":"#a"}]},
                       {"checks":[{"op":"click","selector":"iframe >> body"}]},{"url":"http://127.0.0.1"}]:
            with self.assertRaises(ValueError):validate_request({**self.request(),**change})
