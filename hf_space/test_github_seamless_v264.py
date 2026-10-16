"""v264 seamless GitHub Chat actions: verified inspection before write and no menus."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import github_conversation_actions_v264 as c
from github_general_create_v262 import CreateFileError

AUTH={"repo":"kaministrator999-ui/Swrlzing-core","branch":"main","token":"never-print-token"}
ENTRIES={
    "docs/README.md":{"type":"blob","sha":"a"*40,"mode":"100644"},
    "src/older.py":{"type":"blob","sha":"b"*40,"mode":"100644"},
    "src/readme.py":{"type":"blob","sha":"c"*40,"mode":"100644"},
    "assets/bird.png":{"type":"blob","sha":"d"*40,"mode":"100644"},
    "write-action-tests/Testing.txt":{"type":"blob","sha":"d"*40,"mode":"100644"},
    "src":{"type":"tree","sha":"e"*40,"mode":"040000"},
}
class Seamless(unittest.TestCase):
    def setUp(self):
        c._pending.clear()
        self.calls=[]
        self.patches=[
          patch.object(c,"_read_tree",side_effect=lambda u:(AUTH,ENTRIES,"f"*40)),
          patch.object(c.rename,"prepare",side_effect=self.rename_prepare),
          patch.object(c.rename,"confirm",side_effect=self.rename_confirm),
          patch.object(c.create,"prepare",side_effect=self.create_prepare),
          patch.object(c.create,"confirm",side_effect=self.create_confirm),
        ]
        for p in self.patches:p.start()
        self.user="google:owner";self.thread="thread-1"
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        c._pending.clear()
    def rename_prepare(self,u,src,dst):
        self.calls.append(("rename.prepare",u,src,dst))
        return {"approvalToken":"rename-secret","repo":AUTH["repo"],
                "branch":"main","sourcePath":src,"destinationPath":dst}
    def rename_confirm(self,u,ticket,approved):
        self.calls.append(("rename.confirm",u,ticket,approved))
        return {"ok":True,"verified":True,"atomic":True,"overwrite":False,
                "operation":"RENAME_FILE","repo":AUTH["repo"],"branch":"main",
                "sourcePath":"src/older.py","destinationPath":"src/new.py",
                "blobSha":"b"*40,"commitSha":"c"*40,"mode":"100644",
                "commitUrl":"https://github.com/"+AUTH["repo"]+"/commit/"+"c"*40}
    def create_prepare(self,u,path,data,type):
        self.calls.append(("create.prepare",u,path,data,type))
        return {"approvalToken":"create-secret","repo":AUTH["repo"],"branch":"main",
                "bytes":len(data),"sha256":"e"*64}
    def create_confirm(self,u,ticket,approved):
        self.calls.append(("create.confirm",u,ticket,approved))
        return {"ok":True,"verified":True,"path":"docs/new.md",
                "repo":AUTH["repo"],"commitSha":"a"*40,
                "widget":{"contract":"swrlz-widget-v1","kind":"github-work",
                          "data":{"source":"verified-provider"}}}
    def act(self,prompt,user=None,thread=None):
        return c.handle(user or self.user,thread or self.thread,prompt)

    def test_latest_export_pronoun_rename_is_verified_and_requires_yes(self):
        context={"repo":AUTH["repo"],"branch":"main","sourceSha":"a"*40,
                 "directory":"write-action-tests","lastFile":""}
        history=[
            {"role":"user","text":"Can you see the files in the GitHub repo"},
            {"role":"assistant","text":"Directory listing shown"},
            {"role":"user","text":"Can you see the testing.txt file"},
            {"role":"assistant","text":"GitHub action unavailable (404)"},
            {"role":"user","text":"Can you see the testing.txt file"},
            {"role":"assistant","text":"GitHub action unavailable (404)"},
        ]
        prompt="And you rename that file for me to testing1.txt"
        self.assertFalse(c.is_file_action(prompt))  # Never infer without scope.
        self.assertTrue(c.is_file_action(prompt,context,history))
        proposal=c.handle(self.user,self.thread,prompt,context,history)
        self.assertIn("write-action-tests/Testing.txt",proposal["text"])
        self.assertIn("write-action-tests/testing1.txt",proposal["text"])
        self.assertIn("Nothing changed yet",proposal["text"])
        self.assertEqual(self.calls[0][0],"rename.prepare")
        self.assertEqual(self.calls[0][2:4],("write-action-tests/Testing.txt",
                                            "write-action-tests/testing1.txt"))
        self.assertTrue(c.has_pending(self.user,self.thread))
        approved=self.act("yes")
        self.assertIn("Renamed",approved["text"])
        self.assertEqual(self.calls[-1][0],"rename.confirm")

    def test_contextual_rename_fails_closed_on_repo_change_or_ambiguous_name(self):
        prompt="And you rename that file for me to testing1.txt"
        history=[{"role":"user","text":"Can you see the testing.txt file"}]
        scope={"repo":AUTH["repo"],"branch":"main","sourceSha":"a"*40,
               "directory":"write-action-tests"}
        switched={**scope,"repo":"unrelated/other"}
        r=c.handle(self.user,self.thread,prompt,switched,history)
        self.assertIn("repository or branch changed",r["text"])
        self.assertEqual(self.calls,[])
        # A root-scope mention with two same-named files cannot select one.
        scope["directory"]=""
        with patch.object(c,"_read_tree",return_value=(AUTH,{
            "a/Testing.txt":{"type":"blob"},"b/testing.txt":{"type":"blob"}},"f"*40)):
            r=c.handle(self.user,self.thread,prompt,scope,history)
        self.assertIn("can't identify one verified file",r["text"])
        self.assertFalse(c.has_pending(self.user,self.thread))
        self.assertEqual(self.calls,[])

    def test_missing_exact_file_suggests_verified_near_matches_no_write(self):
        r=self.act("Rename src/old.py to src/new.py in my GitHub repo")
        self.assertTrue(r["handled"])
        self.assertIn("No file named",r["text"])
        self.assertIn("src/older.py",r["text"])
        self.assertIn("Nothing changed",r["text"])
        self.assertFalse(self.calls)
        self.assertFalse(c.has_pending(self.user,self.thread))

    def test_missing_with_no_similar_never_invents_file(self):
        r=self.act("Rename xyzxyz.ext to abc.ext in the repo")
        self.assertIn("No file named",r["text"])
        self.assertIn("didn't find any close matches",r["text"])
        self.assertFalse(self.calls)

    def test_exact_path_required_fuzzy_does_not_rename(self):
        self.act("Rename docs/Readme.md to docs/NEW.md in the repo")
        self.assertFalse(self.calls)

    def test_verified_source_creates_proposal_only(self):
        r=self.act("Rename src/older.py to src/new.py in my repo")
        self.assertIn("Ready to rename",r["text"])
        self.assertIn("Nothing changed yet",r["text"])
        self.assertEqual([x[0] for x in self.calls],["rename.prepare"])
        self.assertTrue(c.has_pending(self.user,self.thread))

    def test_two_turn_approval_only_then_receipt(self):
        self.act("Rename src/older.py to new.py in repo")
        self.assertEqual(self.calls[0][2:4],("src/older.py","src/new.py"))
        yes=self.act("Yes")
        self.assertIn("Renamed",yes["text"])
        self.assertEqual(yes["widget"]["kind"],"github-rename")
        self.assertEqual([x[0] for x in self.calls],["rename.prepare","rename.confirm"])
        self.assertIs(self.calls[1][3],True)
        self.assertFalse(c.has_pending(self.user,self.thread))
        # Repeated or late yes cannot replay a mutation.
        self.assertFalse(c.is_file_action("yes"))
        self.assertFalse(c.has_pending(self.user,self.thread))

    def test_decline_consumes_ticket_without_mutation(self):
        self.act("Rename src/older.py to new.py in repo")
        result=self.act("no")
        self.assertEqual(result["text"],"Cancelled. Nothing changed.")
        self.assertEqual(self.calls[-1][0],"rename.confirm")
        self.assertFalse(self.calls[-1][-1])
        self.assertFalse(c.has_pending(self.user,self.thread))

    def test_thread_isolation(self):
        self.act("Rename src/older.py to new.py in repo")
        self.assertFalse(c.has_pending(self.user,"another-thread"))
        self.assertFalse(c.has_pending("google:other",self.thread))
        self.assertFalse(any(x[0]=="rename.confirm" for x in self.calls))
        self.act("yes",user="google:other",thread="another-thread")
        self.assertFalse(any(x[0]=="rename.confirm" for x in self.calls))

    def test_expired_and_interrupted_tickets(self):
        self.act("Rename src/older.py to new.py in repo")
        with c._lock:c._pending[(self.user,self.thread)]["expiry"]=0
        self.assertFalse(c.has_pending(self.user,self.thread))
        c.expire_interrupted(self.user,self.thread)
        self.assertFalse(any(x[0]=="rename.confirm" for x in self.calls))

    def test_occupied_destination_and_directory(self):
        r=self.act("Rename src/older.py to docs/README.md in repo")
        self.assertIn("already exists",r["text"])
        self.assertFalse(self.calls)
        r=self.act("Rename src to moved-src in repo")
        self.assertIn("not a regular file",r["text"])
        self.assertFalse(self.calls)

    def test_create_named_file_with_content_is_two_turn_operation(self):
        r=self.act("Create a file named docs/new.md in GitHub repo\ncontents: Hello world")
        self.assertIn("Ready to create",r["text"])
        self.assertEqual(self.calls[-1][0],"create.prepare")
        self.assertEqual(self.calls[-1][2],"docs/new.md")
        yes=self.act("yes")
        self.assertIn("Created",yes["text"])
        self.assertEqual(self.calls[-1][0],"create.confirm")
        self.assertTrue(self.calls[-1][-1])

    def test_missing_content_asks_in_chat_not_form(self):
        r=self.act("Create a file named docs/new.md in my GitHub repo")
        self.assertIn("What should go in",r["text"])
        self.assertEqual(self.calls,[])
        r2=self.act("A normal file body.")
        self.assertIn("Ready to create",r2["text"])
        self.assertEqual(self.calls[-1][0],"create.prepare")
        self.assertEqual(self.calls[-1][2],"docs/new.md")
        self.assertIn("Yes",r2["text"])
        self.act("no")
        self.assertEqual(self.calls[-1][0],"create.confirm")
        self.assertFalse(self.calls[-1][-1])

    def test_no_meta_requests_or_negation(self):
        for prompt in [
            "How do I rename src/old.py to new.py in my repo?",
            "Don't rename src/old.py to new.py in repo",
            "Add a feature to rename GitHub files",
            "Our system should be able to rename files in GitHub",
            "Write Python code to rename GitHub files",
            "Can you explain what GitHub file creation means?",
        ]:
            self.assertFalse(c.is_file_action(prompt),prompt)
        self.assertTrue(c.is_file_action("Rename src/older.py to new.py"))
        self.assertTrue(c.is_file_action("Create file named docs/new.md in my GitHub repo"))
        self.assertTrue(c.is_file_action("Create docs/new.json in my GitHub repo"))

    def test_failure_does_not_claim_success(self):
        self.patches[1].stop()
        with patch.object(c.rename,"prepare",side_effect=CreateFileError("GITHUB_WRITE_SCOPE_REQUIRED",403)):
            r=self.act("Rename src/older.py to new.py in repo")
        self.assertIn("write",r["text"].lower())
        self.assertFalse(c.has_pending(self.user,self.thread))
        self.assertNotIn("Renamed",r["text"])

if __name__=="__main__":unittest.main()
