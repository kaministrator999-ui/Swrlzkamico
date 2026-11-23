import unittest
from scripts.github_review_gate_v1 import ReviewGate,ReviewError,apply_approved

class Github:
    def __init__(self):self.files={};self.writes=0
    def get_file(self,r,b,p):return self.files.get((r,b,p))
    def create_file(self,r,b,p,c):
        self.writes+=1;self.files[(r,b,p)]={"sha":"a"*40,"content":c}
    def update_file(self,r,b,p,c,sha):
        self.writes+=1;self.files[(r,b,p)]={"sha":"b"*40,"content":c}

class TestReview(unittest.TestCase):
    def setUp(self):
        self.now=[0];self.gate=ReviewGate(clock=lambda:self.now[0]);self.git=Github()
        self.args=dict(actor="user",thread="thread",repo="owner/repo",branch="main",
                       path="src/file.py",operation="CREATE_FILE",content="hello")
    def decide(self,p,approved=True,actor="user",thread="thread"):
        return self.gate.decide(ticket=p.ticket,actor=actor,thread=thread,approved=approved)
    def test_create_and_readback(self):
        p=self.gate.prepare(**self.args)
        self.assertTrue(apply_approved(self.decide(p),self.git)["verified"])
        with self.assertRaises(ReviewError):self.decide(p)
    def test_rejection(self):
        p=self.gate.prepare(**self.args)
        self.assertIsNone(self.decide(p,False));self.assertEqual(self.git.writes,0)
    def test_cross_thread(self):
        p=self.gate.prepare(**self.args)
        with self.assertRaises(ReviewError):self.decide(p,actor="other")
        with self.assertRaises(ReviewError):self.decide(p,thread="other")
        self.assertIsNotNone(self.decide(p))
    def test_expiry(self):
        p=self.gate.prepare(**self.args);self.now[0]=300
        with self.assertRaises(ReviewError):self.decide(p)
    def test_superseded(self):
        p=self.gate.prepare(**self.args);self.gate.prepare(**{**self.args,"content":"new"})
        with self.assertRaises(ReviewError):self.decide(p)
    def test_no_overwrite(self):
        p=self.gate.prepare(**self.args)
        self.git.files[("owner/repo","main","src/file.py")]={"sha":"a"*40,"content":"old"}
        with self.assertRaises(ReviewError):apply_approved(self.decide(p),self.git)
        self.assertEqual(self.git.writes,0)
    def test_update_sha_bound(self):
        with self.assertRaises(ReviewError):
            self.gate.prepare(**{**self.args,"operation":"UPDATE_FILE"})
        p=self.gate.prepare(**{**self.args,"operation":"UPDATE_FILE","expected_sha":"a"*40})
        self.git.files[("owner/repo","main","src/file.py")]={"sha":"b"*40,"content":"old"}
        with self.assertRaises(ReviewError):apply_approved(p,self.git)
        self.assertEqual(self.git.writes,0)
        self.git.files[("owner/repo","main","src/file.py")]={"sha":"a"*40,"content":"old"}
        self.assertTrue(apply_approved(p,self.git)["verified"])
    def test_traversal(self):
        for path in ("../oops","a/../b","/root",".git/config","a\\b"):
            with self.assertRaises(ReviewError):self.gate.prepare(**{**self.args,"path":path})
    def test_explicit_boolean(self):
        p=self.gate.prepare(**self.args)
        with self.assertRaises(ReviewError):
            self.gate.decide(ticket=p.ticket,actor="user",thread="thread",approved="yes")

if __name__=="__main__":unittest.main()
