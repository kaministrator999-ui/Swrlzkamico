"""Offline structural and contract checks; never misreport these as live model inference."""
import ast,json,unittest,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))
from model_router import dispatch, ModelUnavailable, routes
from brain_programming import programming_intent
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
   for _ in range(100):
    original=client.get("/api/lalm_station/sync").json()
    if original["activeGeneration"] and original["activeGeneration"]["terminal"]:break
    time.sleep(.01)
   self.assertEqual(original["threads"][0]["messages"][-1]["text"],"Original test output")
   self.assertEqual(original["threads"][0]["messages"][-1]["meta"]["modelId"],"stock")
   self.assertIsInstance(original["threads"][0]["messages"][0]["createdAt"],int)
   self.assertIsInstance(original["threads"][0]["messages"][-1]["createdAt"],int)
   self.assertIsInstance(original["activeGeneration"]["programmingIntent"],dict)
   body["requestId"]="req-r39";body["messageId"]="user-r39";body["assistantMessageId"]="assistant-r39";body["modelId"]="r39"
   self.assertEqual(client.post("/api/lalm_station/send",json=body).status_code,202)
   for _ in range(100):
    snap=client.get("/api/lalm_station/sync").json()
    if snap["activeGeneration"] and snap["activeGeneration"]["terminal"]:break
    time.sleep(.01)
   self.assertEqual(snap["activeGeneration"]["terminalType"],"COMPLETE")
   self.assertEqual(snap["threads"][0]["messages"][-1]["text"],"R39 test output")
   self.assertEqual(snap["threads"][0]["messages"][-1]["meta"]["modelId"],"r39")

 def test_station_derives_timezone_aware_turn_gaps(self):
  captured={}
  def stock(payload):
   captured.update(payload)
   return iter([{"type":"DELTA","text":"ok"},{"type":"COMPLETED"}])
  set_generator(lambda payload:iter([{"type":"DELTA","text":"unused"},{"type":"COMPLETE"}]),stock)
  with TestClient(station_app) as client:
   first={"requestId":"time-r1","threadId":"time-thread","messageId":"time-u1","assistantMessageId":"time-a1","prompt":"first","modelId":"stock","timeZone":"America/Chicago"}
   self.assertEqual(client.post("/api/lalm_station/send",json=first).status_code,202)
   for _ in range(100):
    snap=client.get("/api/lalm_station/sync").json()
    if snap["activeGeneration"] and snap["activeGeneration"]["terminal"]:break
    time.sleep(.01)
   second={"requestId":"time-r2","threadId":"time-thread","messageId":"time-u2","assistantMessageId":"time-a2","prompt":"second","modelId":"stock","timeZone":"America/Chicago"}
   self.assertEqual(client.post("/api/lalm_station/send",json=second).status_code,202)
   for _ in range(100):
    snap=client.get("/api/lalm_station/sync").json()
    if snap["activeGeneration"] and snap["activeGeneration"]["terminal"]:break
    time.sleep(.01)
   temporal=captured["temporalContext"]
   self.assertEqual(temporal["schema"],"swrlz-temporal-context-v1")
   self.assertEqual(temporal["timeZone"],"America/Chicago")
   self.assertEqual(temporal["previousMessageRole"],"assistant")
   self.assertIsNotNone(temporal["gapSinceLastUserTurn"])
   self.assertIsNotNone(temporal["gapSinceLastAssistantTurn"])
   self.assertIn("createdAt",captured["history"][0])

 def test_station_live_stream_projects_incremental_delta(self):
  def stock(_payload):
   yield {"type":"STATUS","phase":"LOADING"}
   yield {"type":"DELTA","text":"Hello "}
   time.sleep(.03)
   yield {"type":"DELTA","text":"stream"}
   yield {"type":"COMPLETED","phase":"COMPLETE"}
  set_generator(lambda payload:iter([{"type":"DELTA","text":"unused"},{"type":"COMPLETE"}]),stock)
  with TestClient(station_app) as client:
   body={"requestId":"req-stream","threadId":"thread-stream","messageId":"user-stream","assistantMessageId":"assistant-stream","prompt":"hello","modelId":"stock"}
   self.assertEqual(client.post("/api/lalm_station/send",json=body).status_code,202)
   with client.stream("GET","/api/lalm_station/stream?requestId=req-stream") as response:
    self.assertEqual(response.status_code,200)
    lines=[line for line in response.iter_lines() if line]
   events=[json.loads(line) for line in lines]
   self.assertTrue(any(e.get("type")=="STATUS" and e.get("phase")=="LOADING" for e in events))
   self.assertEqual("".join(e.get("text","") for e in events if e.get("type")=="DELTA"),"Hello stream")
   self.assertTrue(events[-1].get("terminal"))

 def test_brain_routes_pinned_code_edit_to_same_artifact_revision(self):
  def stock(payload):
   if "fix" in str(payload.get("prompt") or "").lower():
    return iter([{"type":"DELTA","text":"```python file=demo.py\ntry:\n    print('v2')\nexcept Exception as exc:\n    print(exc)\n```\nAdded guarded error handling."},{"type":"COMPLETED"}])
   return iter([{"type":"DELTA","text":"```python file=demo.py\nprint('v1')\n```\nInitial demo."},{"type":"COMPLETED"}])
  set_generator(lambda payload:iter([{"type":"DELTA","text":"unused"},{"type":"COMPLETE"}]),stock)
  with TestClient(station_app) as client:
   first={"requestId":"artifact-r1","threadId":"artifact-thread","messageId":"user-r1","assistantMessageId":"assistant-r1","prompt":"make python code for a demo","modelId":"stock"}
   self.assertEqual(client.post("/api/lalm_station/send",json=first).status_code,202)
   for _ in range(100):
    snap=client.get("/api/lalm_station/sync").json()
    if snap["activeGeneration"] and snap["activeGeneration"]["terminal"]:break
    time.sleep(.01)
   thread=snap["threads"][0]
   self.assertEqual(len(thread["codeArtifacts"]),1)
   artifact=thread["codeArtifacts"][0]
   artifact_id=artifact["id"]
   self.assertEqual(artifact["currentRevision"],1)
   self.assertTrue(thread["messagePins"]["assistant-r1"])
   original_text=next(m["text"] for m in thread["messages"] if m["id"]=="assistant-r1")
   second={"requestId":"artifact-r2","threadId":"artifact-thread","messageId":"user-r2","assistantMessageId":"assistant-r2","prompt":"fix that code and add error handling","modelId":"stock"}
   self.assertEqual(client.post("/api/lalm_station/send",json=second).status_code,202)
   for _ in range(100):
    snap=client.get("/api/lalm_station/sync").json()
    if snap["activeGeneration"] and snap["activeGeneration"]["terminal"]:break
    time.sleep(.01)
   thread=snap["threads"][0];artifact=thread["codeArtifacts"][0]
   self.assertEqual(artifact["id"],artifact_id)
   self.assertEqual(artifact["currentRevision"],2)
   self.assertEqual(len(artifact["revisions"]),2)
   self.assertEqual(next(m["text"] for m in thread["messages"] if m["id"]=="assistant-r1"),original_text)
   explanation=next(m for m in thread["messages"] if m["id"]=="assistant-r2")
   self.assertNotIn("```",explanation["text"])
   self.assertEqual(explanation["meta"]["updatedCodeArtifactId"],artifact_id)
   self.assertEqual(snap["activeGeneration"]["artifactReceipt"]["action"],"REVISION_COMMITTED")
   self.assertEqual(snap["activeGeneration"]["programmingIntent"]["artifactTargetId"],artifact_id)

 def test_brain_new_project_does_not_mutate_existing_pin(self):
  pins=[{"messageId":"m1","artifactType":"code","artifactId":"a1","artifactRevision":3,"text":"```python\nprint(1)\n```","files":[{"path":"old.py","language":"python"}]}]
  intent=programming_intent("separately make a new save manager project",[],pins)
  self.assertTrue(intent["newProject"])
  self.assertFalse(intent["artifactContinuation"])
  self.assertFalse(intent["artifactMutationRequested"])
  self.assertEqual(intent["artifactTargetId"],"")

 def test_model_routes_fail_closed(self):
  self.assertEqual([r.model_id for r in routes()],["r39","stock","700m","compare"])
  self.assertTrue(routes()[1].available)
  self.assertTrue(routes()[2].available)
  self.assertFalse(routes()[3].available)
  with self.assertRaises(ModelUnavailable): list(dispatch("stock",{},lambda p:iter([{"type":"DELTA","text":"wrong model"}])))
  with self.assertRaises(ModelUnavailable): list(dispatch("compare",{},lambda p:iter([])))
  events=list(dispatch("r39",{"prompt":"hello"},lambda p:iter([{"type":"DELTA","text":"real route"}])))
  self.assertEqual(events[0]["type"],"PROGRAMMING_INTENT")
  self.assertEqual(events[-1]["text"],"real route")

 def test_source_contract(self):
  src=(ROOT/"hf_space/app.py").read_text(encoding="utf-8")
  ast.parse(src)
  ast.parse((ROOT/"hf_space/station.py").read_text(encoding="utf-8"))
  ast.parse((ROOT/"hf_space/model_router.py").read_text(encoding="utf-8"))
  ast.parse((ROOT/"hf_space/brain_programming.py").read_text(encoding="utf-8"))
  self.assertIn("generate_events",src)
  self.assertIn('kind=="DELTA"',src)
  self.assertIn('kind=="FAILED"',src)
  self.assertNotIn("torch.hub",src)
  station=(ROOT/"hf_space/station.py").read_text(encoding="utf-8")
  self.assertIn('StreamingResponse(events()',station)
  self.assertIn('/api/lalm_station/stream',station)
  self.assertIn('"createdAt":int(time.time()*1000)',station)

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
