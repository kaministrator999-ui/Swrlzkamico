"""v263 atomic Git tree rename — no partial create/delete, mode/blob preserved."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import github_rename_v263 as ren
import github_rename_receipt_v263 as receipt
from github_rename_intent_v263 import wants_github_rename_proposal as intent

H0="a"*40
T0="b"*40
BLOB="c"*40
T1="d"*40
H1="e"*40
REPO="kaministrator999-ui/Swrlzing-core"

class AtomicRename(unittest.TestCase):
    def setUp(self):
        ren._pending.clear()
        self.user="google:owner"
        self.repo=REPO
        self.branch="main"
        self.head=H0
        self.head_trees={H0:T0}
        self.trees={T0:[
            {"path":"src","type":"tree","mode":"040000","sha":"f"*40},
            {"path":"src/old.py","type":"blob","mode":"100755","sha":BLOB,"size":428},
            {"path":"README.md","type":"blob","mode":"100644","sha":"9"*40,"size":21},
            {"path":"assets","type":"tree","mode":"040000","sha":"8"*40},
        ]}
        self.create_tree_calls=[]
        self.create_commit_calls=[]
        self.update_ref_calls=[]
        def authorize(user,expected_repo=None):
            if user!=self.user:raise ren.CreateFileError("GOOGLE_SIGN_IN_REQUIRED",401)
            if expected_repo is not None and expected_repo!=self.repo:
                raise ren.CreateFileError("SELECTED_REPOSITORY_CHANGED_OR_UNSUPPORTED",403)
            return {"token":"linked-oauth","repo":self.repo,"branch":self.branch}
        def api(auth,method,endpoint,body=None):
            self.assertEqual(auth["token"],"linked-oauth")
            suffix=endpoint.split("/git/",1)[-1]
            if method=="GET" and suffix.startswith("ref/heads/"):
                return {"object":{"type":"commit","sha":self.head}}
            if method=="GET" and suffix.startswith("commits/"):
                sha=suffix.split("/")[-1]
                return {"sha":sha,"tree":{"sha":self.head_trees[sha]}}
            if method=="GET" and suffix.startswith("trees/"):
                tree=suffix.split("/")[-1].split("?")[0]
                return {"sha":tree,"truncated":False,"tree":self.trees[tree]}
            if method=="POST" and suffix=="trees":
                self.create_tree_calls.append(body)
                self.assertEqual(body["base_tree"],T0)
                edits=body["tree"]
                self.assertEqual(len(edits),2)
                old, new=edits
                self.assertIsNone(old["sha"])
                self.assertEqual(old["path"],"src/old.py")
                self.assertEqual(new["sha"],BLOB)
                self.assertEqual(new["mode"],"100755")
                records=[dict(x) for x in self.trees[T0] if x["path"]!=old["path"]]
                records.append({"path":new["path"],"type":"blob","mode":"100755","sha":BLOB,"size":428})
                self.trees[T1]=records
                return {"sha":T1}
            if method=="POST" and suffix=="commits":
                self.create_commit_calls.append(body)
                self.assertEqual(body["parents"],[H0])
                self.assertEqual(body["tree"],T1)
                self.head_trees[H1]=T1
                return {"sha":H1}
            if method=="PATCH" and suffix.startswith("refs/heads/"):
                self.update_ref_calls.append(body)
                self.assertIs(body["force"],False)
                self.assertEqual(body["sha"],H1)
                if self.head!=H0:
                    raise ren.CreateFileError("GITHUB_RENAME_CONFLICT_OR_PROTECTION",409)
                self.head=H1
                return {"ref":"refs/heads/main","object":{"sha":H1}}
            raise AssertionError((method,endpoint,body))
        self.mock_auth=patch.object(ren,"_authorize",side_effect=authorize)
        self.mock_api=patch.object(ren,"_api",side_effect=api)
        self.mock_perm=patch.object(ren,"_permission_for_workflows")
        for p in (self.mock_auth,self.mock_api,self.mock_perm):p.start()

    def tearDown(self):
        for p in (self.mock_perm,self.mock_api,self.mock_auth):p.stop()
        ren._pending.clear()

    def test_one_atomic_commit_and_verified_identical_blob(self):
        proposal=ren.prepare(self.user,"src/old.py","src/new.py")
        self.assertEqual(proposal["sourceBlobSha"],BLOB)
        self.assertEqual(proposal["sourceMode"],"100755")
        self.assertEqual(proposal["bytes"],428)
        self.assertFalse(self.create_tree_calls)
        assert proposal["atomic"] and not proposal["overwrite"]
        result=ren.confirm(self.user,proposal["approvalToken"],True)
        self.assertTrue(result["verified"])
        self.assertEqual(result["blobSha"],BLOB)
        self.assertEqual(result["mode"],"100755")
        self.assertEqual(result["commitSha"],H1)
        self.assertEqual(len(self.create_tree_calls),1)
        self.assertEqual(len(self.create_commit_calls),1)
        self.assertEqual(len(self.update_ref_calls),1)
        self.assertEqual(self.head,H1)
        widget=receipt.make_rename_widget(result)
        self.assertEqual(widget["kind"],"github-rename")
        self.assertEqual(widget["data"]["filesRenamed"],1)
        self.assertEqual(widget["data"]["bytesPreserved"],428)
        self.assertNotIn("linked-oauth",str(widget))

    def test_colliding_destination_no_git_mutation(self):
        with self.assertRaises(ren.CreateFileError) as ctx:
            ren.prepare(self.user,"src/old.py","README.md")
        self.assertEqual(ctx.exception.code,"DESTINATION_ALREADY_EXISTS")
        self.assertEqual(len(self.create_tree_calls),0)

    def test_source_not_found(self):
        with self.assertRaises(ren.CreateFileError) as ctx:
            ren.prepare(self.user,"missing.js","src/new.js")
        self.assertEqual(ctx.exception.code,"SOURCE_FILE_NOT_FOUND")

    def test_parent_collision(self):
        with self.assertRaises(ren.CreateFileError) as ctx:
            ren.prepare(self.user,"src/old.py","README.md/sub/file.txt")
        self.assertEqual(ctx.exception.code,"DESTINATION_PARENT_NOT_DIRECTORY")

    def test_decline_and_replay_denied(self):
        ready=ren.prepare(self.user,"src/old.py","src/new.py")
        self.assertEqual(ren.confirm(self.user,ready["approvalToken"],False)["code"],"USER_DECLINED")
        with self.assertRaises(ren.CreateFileError):
            ren.confirm(self.user,ready["approvalToken"],True)
        self.assertFalse(self.create_tree_calls)

    def test_wrong_owner_cannot_burn_ticket(self):
        ready=ren.prepare(self.user,"src/old.py","src/new.py")
        with self.assertRaises(ren.CreateFileError):
            ren.confirm("google:outsider",ready["approvalToken"],True)
        self.assertTrue(ren.confirm(self.user,ready["approvalToken"],True)["verified"])

    def test_concurrent_ref_change_fails_before_mutation(self):
        ready=ren.prepare(self.user,"src/old.py","src/new.py")
        self.head="7"*40
        self.head_trees[self.head]="6"*40
        with self.assertRaises(ren.CreateFileError) as ctx:
            ren.confirm(self.user,ready["approvalToken"],True)
        self.assertEqual(ctx.exception.code,"REPOSITORY_CHANGED_REPREPARE_REQUIRED")
        self.assertFalse(self.create_tree_calls)
        self.assertFalse(self.update_ref_calls)

    def test_repo_and_branch_change_fails(self):
        ready=ren.prepare(self.user,"src/old.py","src/new.py")
        self.repo="kaministrator999-ui/Swrlzkamico"
        with self.assertRaises(ren.CreateFileError):
            ren.confirm(self.user,ready["approvalToken"],True)
        self.assertFalse(self.update_ref_calls)

    def test_tree_truncation_rejected(self):
        original=ren._tree
        with patch.object(ren,"_tree",side_effect=ren.CreateFileError("GITHUB_TREE_UNAVAILABLE_OR_TRUNCATED",409)):
            with self.assertRaises(ren.CreateFileError):
                ren.prepare(self.user,"src/old.py","src/new.py")

    def test_directory_or_gitlink_is_not_a_file(self):
        for path in ("src","assets"):
            with self.subTest(path=path),self.assertRaises(ren.CreateFileError):
                ren.prepare(self.user,path,path+"-renamed")
        self.trees[T0].append({"path":"lib/submodule","type":"commit","mode":"160000","sha":"1"*40})
        with self.assertRaises(ren.CreateFileError):
            ren.prepare(self.user,"lib/submodule","lib/other")

    def test_path_invalid_and_workflow_scope_boundary(self):
        for path in ("../escape.py","dir/../file.py",".git/config","src//new.py"):
            with self.subTest(path=path),self.assertRaises(ren.CreateFileError):
                ren.prepare(self.user,"src/old.py",path)
        ren.prepare(self.user,"src/old.py",".github/workflows/ci.yaml")
        self.mock_perm.side_effect=ren.CreateFileError("GITHUB_WORKFLOW_SCOPE_REQUIRED",403)
        with self.assertRaises(ren.CreateFileError):
            ren.prepare(self.user,"src/old.py",".github/workflows/ci.yaml")

    def test_classifier(self):
        yes=["Rename src/old.py to src/new.py in my GitHub repo",
             "Move file README.md to docs/README.md in the repo",
             "Can you rename file app.py to app2.py on GitHub?"]
        no=["How do I rename files in GitHub?",
            "Do not rename file app.py in the repo",
            "Add the ability to rename files in our AI Chat GitHub integration",
            "Generate Python code to rename file a.py to b.py in GitHub"]
        for x in yes:self.assertTrue(intent(x),x)
        for x in no:self.assertFalse(intent(x),x)

if __name__=="__main__":
    unittest.main()
