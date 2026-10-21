"""v291 signed-in GitHub conversational create collision/name-continuity.

Mocks are confined to authorized GitHub adapters: no external network, OAuth
accounts, model inference, or real file mutation.
"""
import base64
import pathlib
import sys
import time
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import github_conversation_actions_v264 as actions
import github_general_create_v262 as create

OLD="write-lab/created-by-swyrlz.txt"
NEW="write-lab/swyrlz1.txt"
TEXT="§wyrlz owner-approved create test"
USER="google:owner"
OTHER="google:other"
THREAD="chat-v291"
PROMPT='Create a file named write-lab/created-by-swyrlz.txt in my GitHub repo containing "§wyrlz owner-approved create test"'


class CollisionFollowup(unittest.TestCase):
    def setUp(self):
        actions._pending.clear()
        self.repo="kaministrator999-ui/Swrlzing-core"
        self.branch="main"
        self.contents={OLD:TEXT.encode("utf-8")}
        self.prepared=[]
        self.writes=[]
        self.ticket_index=0
        self.tickets={}
        self.patchers=[
            patch.object(actions,"_read_tree",side_effect=self._tree),
            patch.object(create,"prepare",side_effect=self._prepare),
            patch.object(create,"confirm",side_effect=self._confirm)
        ]
        for p in self.patchers:p.start()

    def tearDown(self):
        for p in reversed(self.patchers):p.stop()
        actions._pending.clear()

    def _tree(self,user):
        if user!=USER:raise create.CreateFileError("GOOGLE_SIGN_IN_REQUIRED",401)
        return ({"repo":self.repo,"branch":self.branch},
                {p:{"type":"blob"} for p in self.contents}, "a"*40)

    def _prepare(self,user,path,content,media_type):
        self.assertEqual(user,USER)
        raw=base64.b64decode(content,validate=True)
        if path in self.contents:
            raise create.CreateFileError("FILE_ALREADY_EXISTS",409)
        self.assertEqual(media_type,"text/plain; charset=utf-8")
        self.ticket_index+=1
        ticket="ticket-"+str(self.ticket_index)
        self.tickets[ticket]=(path,raw)
        self.prepared.append((path,raw))
        return {"approvalToken":ticket,"repo":self.repo,"branch":self.branch,
                "bytes":len(raw),"sha256":"a"*64}

    def _confirm(self,user,ticket,approved):
        self.assertEqual(user,USER)
        path,raw=self.tickets.pop(ticket)
        if not approved:return {"ok":False,"code":"USER_DECLINED"}
        self.assertNotIn(path,self.contents)
        self.contents[path]=raw
        self.writes.append((path,raw))
        return {"repo":self.repo,"branch":self.branch,"path":path,"commitSha":"b"*40,
                "widget":{"contract":"swrlz-widget-v1","kind":"github-work",
                          "data":{"path":path}}}

    def collide(self):
        self.assertTrue(actions.is_file_action(PROMPT))
        output=actions.handle(USER,THREAD,PROMPT)
        self.assertIn("already exists",output["text"].lower())
        self.assertIn("new file",output["text"].lower())
        self.assertIn("nothing changed",output["text"].lower())
        self.assertEqual(actions.pending_kind(USER,THREAD),"need-new-name")
        self.assertEqual(self.contents[OLD],TEXT.encode("utf-8"))
        self.assertEqual(self.writes,[])
        return output

    def test_screenshot_sequence_continues_original_create_not_rename(self):
        self.collide()
        name_reply="Name it swyrlz1 then"
        self.assertTrue(actions.is_new_name_reply(name_reply))
        self.assertFalse(actions.is_file_action(name_reply))
        prepared=actions.handle(USER,THREAD,name_reply)
        self.assertEqual(actions.pending_kind(USER,THREAD),"create")
        self.assertEqual(self.prepared,[(NEW,TEXT.encode("utf-8"))])
        self.assertIn("Ready to create",prepared["text"])
        self.assertIn(NEW,prepared["text"])
        self.assertNotIn("Renamed",prepared["text"])
        self.assertEqual(self.writes,[],"No GitHub commit before fresh Yes")
        receipt=actions.handle(USER,THREAD,"Yes")
        self.assertIn("Created",receipt["text"])
        self.assertEqual(self.writes,[(NEW,TEXT.encode("utf-8"))])
        self.assertEqual(self.contents[OLD],TEXT.encode("utf-8"))
        self.assertEqual(self.contents[NEW],TEXT.encode("utf-8"))
        self.assertEqual(receipt["widget"]["kind"],"github-work")
        self.assertFalse(actions.has_pending(USER,THREAD))
        self.assertEqual(actions.handle(USER,THREAD,"Yes")["text"].startswith("I couldn't identify"),True)
        self.assertEqual(len(self.writes),1,"A second Yes cannot repeat a write")

    def test_no_cancel_and_same_name_never_write(self):
        self.collide()
        retry=actions.handle(USER,THREAD,"Name it created-by-swyrlz then")
        self.assertIn("existing file",retry["text"])
        self.assertEqual(actions.pending_kind(USER,THREAD),"need-new-name")
        cancel=actions.handle(USER,THREAD,"No")
        self.assertEqual(cancel["text"],"Cancelled. Nothing changed.")
        self.assertEqual(self.writes,[])
        self.assertFalse(actions.has_pending(USER,THREAD))

    def test_second_collision_stays_bounded(self):
        self.contents[NEW]=b"existing independent data"
        self.collide()
        result=actions.handle(USER,THREAD,"Name it swyrlz1 then")
        self.assertIn("already exists",result["text"])
        self.assertEqual(actions.pending_kind(USER,THREAD),"need-new-name")
        self.assertEqual(self.contents[NEW],b"existing independent data")
        self.assertEqual(self.writes,[])

    def test_repo_swap_and_wrong_account_fail_closed(self):
        self.collide()
        self.assertFalse(actions.has_pending(OTHER,THREAD))
        self.repo="kaministrator999-ui/Swrlzkamico"
        reply=actions.handle(USER,THREAD,"Name it swyrlz1 then")
        self.assertIn("selected repository",reply["text"])
        self.assertEqual(self.prepared,[])
        self.assertEqual(self.writes,[])

    def test_explicit_replacement_name_does_not_accept_arbitrary_chat(self):
        for candidate in ("Name it swyrlz1 then","Call it test-two.txt",
                          "Make it folder/name.txt","try filename test3"):
            self.assertTrue(actions.is_new_name_reply(candidate),candidate)
        for candidate in ("What is a file?","rename the existing file",
                          "Please explain GitHub","Yes","No",
                          "How can I name it?"):
            self.assertFalse(actions.is_new_name_reply(candidate),candidate)
        self.collide()
        # Unrelated topic consumes the collision continuation at Station's
        # guard. No model interpretation can write from the stale state.
        actions.expire_interrupted(USER,THREAD)
        self.assertFalse(actions.has_pending(USER,THREAD))
        self.assertEqual(self.writes,[])

    def test_old_file_is_never_renamed_or_overwritten(self):
        self.collide()
        actions.handle(USER,THREAD,"Name it swyrlz1 then")
        self.assertEqual(self.contents[OLD],TEXT.encode("utf-8"))
        actions.handle(USER,THREAD,"No")
        self.assertEqual(self.contents.keys(),{OLD})
        self.assertEqual(self.writes,[])

    def test_station_routes_same_thread_to_provider_not_coder(self):
        source=(ROOT/"station.py").read_text(encoding="utf-8")
        self.assertIn('pending_kind(google_owner,tid) == "need-new-name"',source)
        self.assertIn('github_chat_files.is_new_name_reply(prompt)',source)
        self.assertIn('payload["githubChatFileAction"]=',source)
        self.assertIn("github_chat_files.expire_interrupted",source)


if __name__=="__main__":
    unittest.main()
