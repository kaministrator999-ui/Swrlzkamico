"""Offline structural and contract checks; never misreport these as live model inference."""
import ast,json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))
from model_router import dispatch, ModelUnavailable, routes
from fastapi.testclient import TestClient
from station import app as station_app, set_generator
class Candidate(unittest.TestCase):
 def test_station_send_sync_and_route_rejection(self):
  set_generator(lambda payload:iter([{"type":"DELTA","text":"R39 test output"},{"type":"COMPLETE"}]),lambda payload:iter([{"type":"DELTA","text":"Original test output"},{"type":"COMPLETED"}]))
  with TestClient(station_app) as client:
   self.assertEqual(client.get("/").status_code,200)
   self.assertEqual(client.get("/api/lalm_station/sync").status_code,200)
   body={"requestId":"req-test","threadId":"thread-test","messageId":"user-test","assistantMessageId":"assistant-test","prompt":"hello","modelId":"stock"}
   self.assertEqual(client.post("/api/lalm_station/send",json=body).status_code,202)
   import time
   for _ in range(100):
    original=client.get("/api/lalm_station/sync").json()
    if original["activeGeneration"] and original["activeGeneration"]["terminal"]:break
    time.sleep(.01)
   self.assertEqual(original["threads"][0]["messages"][-1]["text"],"Original test output")
   self.assertEqual(original["threads"][0]["messages"][-1]["meta"]["modelId"],"stock")
   body["requestId"]="req-r39";body["messageId"]="user-r39";body["assistantMessageId"]="assistant-r39"
   body["modelId"]="r39"
   self.assertEqual(client.post("/api/lalm_station/send",json=body).status_code,202)
   import time
   for _ in range(100):
    snap=client.get("/api/lalm_station/sync").json()
    if snap["activeGeneration"] and snap["activeGeneration"]["terminal"]:break
    time.sleep(.01)
   self.assertEqual(snap["activeGeneration"]["terminalType"],"COMPLETE")
   self.assertEqual(snap["threads"][0]["messages"][-1]["text"],"R39 test output")
   self.assertEqual(snap["threads"][0]["messages"][-1]["meta"]["modelId"],"r39")
 def test_model_routes_fail_closed(self):
  self.assertEqual([r.model_id for r in routes()],["r39","stock","compare"])
  self.assertTrue(routes()[1].available)
  self.assertFalse(routes()[2].available)
  with self.assertRaises(ModelUnavailable): list(dispatch("stock",{},lambda p:iter([{"type":"DELTA","text":"wrong model"}])))
  with self.assertRaises(ModelUnavailable): list(dispatch("compare",{},lambda p:iter([])))
  self.assertEqual(list(dispatch("r39",{},lambda p:iter([{"type":"DELTA","text":"real route"}])))[0]["text"],"real route")
 def test_source_contract(self):
  src=(ROOT/"hf_space/app.py").read_text(encoding="utf-8")
  tree=ast.parse(src)
  self.assertIn("generate_events",src)
  self.assertIn('kind=="DELTA"',src)
  self.assertIn('kind=="FAILED"',src)
  self.assertNotIn("torch.hub",src)
 def test_model_provenance(self):
  p=json.loads((ROOT/"hf_space/MODEL_PROVENANCE.json").read_text(encoding="utf-8"))
  m=json.loads((ROOT/"hf_space/lalm§wyrlz.transport.json").read_text(encoding="utf-8"))
  self.assertEqual(p["transportSha256"],m["sha256"])
  self.assertEqual(p["transportChunks"],54)
  self.assertEqual(p["rawSha256"],"65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee")
 def test_canonical_source(self):
  for rel in ("accepted_runtime/lalm/r39_engine.py","swyrlz/r39_inference.py","swyrlz/backend.py"):
   self.assertEqual((ROOT/rel).read_bytes(),(ROOT/"hf_space"/rel).read_bytes())
  self.assertIn('id="hfModel"',(ROOT/"hf_space/chat/§wyrlz/index.html").read_text(encoding="utf-8"))
  self.assertTrue((ROOT/"api/lalm_station.py").is_file(), "Canonical account-backed Chat bridge must remain available as migration reference")
 def test_no_secret_or_billing_code(self):
  app=(ROOT/"hf_space/app.py").read_text(encoding="utf-8")
  for term in ("HF_TOKEN","request_space_hardware","add_space_secret","billing"):
   self.assertNotIn(term,app)
if __name__=="__main__":unittest.main()
