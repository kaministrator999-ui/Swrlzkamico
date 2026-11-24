"""Repair routing: never regenerate HTML or write without a one-use owner approval."""
import base64
import hashlib
import importlib.util
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("html_repair_v1_test",ROOT/"api/html_project_repair_v1.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
SLUG = "interactive-3d-model-viewer"
CONTENT = ('<script type="importmap">{"imports":{"three":'
           '"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",'
           '"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"'
           '}}</script><script type="module">'
           "import * as THREE from 'three';"
           "import { OrbitControls } from 'three/addons/controls/OrbitControls.js';"
           '</script>')
RAW = CONTENT.encode()
BLOB = hashlib.sha1(b"blob "+str(len(RAW)).encode()+b"\0"+RAW).hexdigest()


class HTMLRepairTest(unittest.TestCase):
    def test_intent_and_source_scope(self):
        self.assertTrue(m.repair_intent("Repair the existing interactive 3D model viewer"))
        self.assertFalse(m.repair_intent("Inspect the viewer without editing or repairing"))
        self.assertFalse(m.repair_intent("@GitHub repair HTML project "+SLUG))
        p={"receivedText":"Repair the existing interactive 3D model viewer",
           "activeHtmlProject":{"project":SLUG},
           "projectFileEvidence":"Verified Git blob: "+BLOB}
        self.assertTrue(m.should_route(p))
        events=list(m.events(p))
        text=events[1]["text"]
        self.assertIn("verified",text.lower())
        self.assertIn("@GitHub repair HTML project "+SLUG,text)
        self.assertNotIn("<html",text)
        self.assertEqual(events[-1]["type"],"COMPLETED")
        self.assertFalse(m.should_route({**p,"projectFileEvidence":"Source unavailable"}))
        self.assertFalse(m.should_route({**p,"receivedText":"Just inspect it without changes"}))

    def test_approval_and_source_pin(self):
        received=[]
        publisher=types.ModuleType("github_html_publish_action_v1")
        publisher.PublishActionError=type("PublishActionError",(Exception,),{})
        publisher._authorized=lambda u:{"repo":"kaministrator999-ui/Swrlzkamico","branch":"main"}
        publisher._head=lambda a:"b"*40
        publisher._manifest=lambda a,head,slug:{
            "repo":"kaministrator999-ui/Swrlzkamico","branch":"main",
            "project":slug,"sourceSha":head,"indexGitBlobSha":BLOB,
            "files":[{"path":"index.html","bytes":len(RAW)}],
            "bytes":len(RAW),"destinationPrefix":"html-projects/"+slug+"/",
            "url":"https://example.invalid"}
        def github(auth,verb,path,**kwargs):
            received.append((verb,path,kwargs))
            if verb=="GET":
                return {"type":"file","encoding":"base64","sha":BLOB,
                        "content":base64.b64encode(RAW).decode()}
            return None
        publisher._github=github
        with patch.dict(sys.modules,{"github_html_publish_action_v1":publisher}):
            proposal=m.prepare("google:owner","t1",SLUG)
            self.assertEqual(proposal["data"]["mode"],"repair")
            self.assertFalse(any(verb=="POST" for verb,_,_ in received))
            rejected=m.confirm("google:owner","t1",False)
            self.assertFalse(rejected["dispatched"])
            self.assertFalse(any(verb=="POST" for verb,_,_ in received))
            m.prepare("google:owner","t1",SLUG)
            approved=m.confirm("google:owner","t1",True)
            self.assertTrue(approved["dispatched"])
            sent=[(verb,path,v) for verb,path,v in received if verb=="POST"]
            self.assertEqual(len(sent),1)
            self.assertIn("hf-html-project-repair-pr-v1.yml/dispatches",sent[0][1])
            self.assertEqual(sent[0][2]["data"]["inputs"]["source_sha"],"b"*40)
            with self.assertRaises(m.RepairError):
                m.confirm("google:owner","t1",True)

    def test_no_supported_strategy_refuses(self):
        publisher=types.ModuleType("github_html_publish_action_v1")
        publisher._github=lambda *a,**k:{
            "type":"file","encoding":"base64","content":base64.b64encode(b"<html></html>").decode(),
            "sha":hashlib.sha1(b"blob 13\0<html></html>").hexdigest()}
        with patch.dict(sys.modules,{"github_html_publish_action_v1":publisher}):
            with self.assertRaises(m.RepairError):
                m._verified_source({},SLUG)


if __name__=="__main__":
    unittest.main()
