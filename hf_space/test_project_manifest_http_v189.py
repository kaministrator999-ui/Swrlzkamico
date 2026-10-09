"""Model plan proposal must be explicitly reviewed by same caller before project creation."""
import json
import sys
import types
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0,str(Path(__file__).resolve().parent))
mock=types.ModuleType("model_router")
mock.dispatch=lambda *args,**kwargs: iter(())
mock.routes=lambda: []
mock.ModelUnavailable=type("ModelUnavailable",(RuntimeError,),{})
sys.modules["model_router"]=mock
(Path(__file__).resolve().parent/"chat"/"§wyrlz"/"assets").mkdir(parents=True,exist_ok=True)
import station  # noqa: E402

TICKS=chr(96)*3
plan={"schema":"swrlz-project-manifest-v1","title":"Small CLI","goal":"print a greeting",
    "files":[{"path":"tests/test_app.py","language":"python","purpose":"Tests","dependsOn":["src/app.py"]},
             {"path":"src/app.py","language":"python","purpose":"Runnable CLI","dependsOn":[]}]}
text=TICKS+"swrlz-project-manifest\n"+json.dumps(plan)+"\n"+TICKS
source_msg={"id":"message-plan","role":"assistant","text":text,"meta":{"state":"COMPLETE"}}
pending_msg={"id":"message-pending","role":"assistant","text":text,"meta":{"state":"GENERATING"}}
other_msg={"id":"message-invalid","role":"assistant","text":"No valid project plan","meta":{"state":"COMPLETE"}}
src_files=[{"path":"src/app.py","language":"python","content":"print('Hi')\n"}]
src_sha=station._artifact_source_hash(src_files)
artifact={"id":"artifact-src","type":"code","sourceMessageId":"message-code",
          "currentRevision":1,"files":src_files,
          "revisions":[{"revision":1,"sourceHash":src_sha,"files":src_files}]}
station._sessions.clear()
station._sessions["user-one"]={"revision":0,"currentId":"thread-x","threads":[
    {"id":"thread-x","messages":[source_msg,pending_msg,other_msg],"codeArtifacts":[artifact],"projectWorkspaces":[]},
]}
station._sessions["user-two"]={"revision":0,"currentId":"thread-x","threads":[
    {"id":"thread-x","messages":[],"codeArtifacts":[],"projectWorkspaces":[]},
]}
client=TestClient(station.app)
client.cookies.set("swrlz_hf_sid","user-one")
endpoint="/api/lalm_station/workspaces/plan"
preview=client.get(endpoint,params={"threadId":"thread-x","messageId":"message-plan"})
assert preview.status_code==200,preview.text
assert preview.headers["cache-control"]=="private, no-store"
v=preview.json()
assert v["approvalRequired"] is True
assert v["plan"]["generationOrder"]==["src/app.py","tests/test_app.py"]
assert v["plan"]["goal"]=="print a greeting"
assert len(v["messageSha256"])==64 and len(v["plan"]["planSha256"])==64
assert client.get(endpoint,params={"threadId":"thread-x","messageId":"message-pending"}).status_code==404
assert client.get(endpoint,params={"threadId":"thread-x","messageId":"message-invalid"}).status_code==422
assert client.get(endpoint,params={"threadId":"nonexistent","messageId":"message-plan"}).status_code==404
assert client.get("/api/lalm_station/workspaces",params={"threadId":"thread-x"}).json()["workspaces"]==[], "Preview must not create any workspace"
approve={"threadId":"thread-x","messageId":"message-plan",
    "expectedMessageSha256":v["messageSha256"],
    "expectedPlanSha256":v["plan"]["planSha256"]}
assert client.post(endpoint+"/approve",json={**approve,"expectedPlanSha256":"0"*64}).status_code==409
assert client.post(endpoint+"/approve",json={**approve,"expectedMessageSha256":"0"*64}).status_code==409
approved=client.post(endpoint+"/approve",json=approve)
assert approved.status_code==200,approved.text
workspace=approved.json()["workspace"]
assert workspace["revision"]==1 and workspace["hasApprovedPlan"] is True
assert workspace["remainingPaths"]==["src/app.py","tests/test_app.py"]
assert workspace["nextReadyPaths"]==["src/app.py"]
assert workspace["completedCount"]==0 and workspace["validationState"]=="NOT_RUN"
repeat=client.post(endpoint+"/approve",json=approve)
assert repeat.status_code==200 and repeat.json()["alreadyApproved"] is True
assert repeat.json()["workspace"]["id"]==workspace["id"]
assert len(client.get("/api/lalm_station/workspaces",params={"threadId":"thread-x"}).json()["workspaces"])==1

attach=client.post("/api/lalm_station/workspaces/attach",json={
    "threadId":"thread-x","workspaceId":workspace["id"],"artifactId":"artifact-src",
    "artifactRevision":1,"artifactSourceHash":src_sha,"expectedWorkspaceRevision":1,
})
assert attach.status_code==200,attach.text
state=attach.json()["workspace"]
assert state["completedCount"]==1 and state["nextReadyPaths"]==["tests/test_app.py"]
assert state["remainingPaths"]==["tests/test_app.py"]

# The completed plan is not itself a code file, even if fenced.
thread=station._sessions["user-one"]["threads"][0]
fake={"id":"new","role":"assistant","text":text,"meta":{"state":"COMPLETE"}}
assert station._create_code_artifact(thread,fake,"request-123",text) is None

# Source message revisions and lost session should never be silently trusted.
client.cookies.set("swrlz_hf_sid","user-two")
assert client.get(endpoint,params={"threadId":"thread-x","messageId":"message-plan"}).status_code==404
assert client.post(endpoint+"/approve",json=approve).status_code==404
client.cookies.clear()
assert client.get(endpoint,params={"threadId":"thread-x","messageId":"message-plan"}).status_code==404
client.cookies.set("swrlz_hf_sid","user-one")
source_msg["text"]="changed or truncated plan"
assert client.post(endpoint+"/approve",json=approve).status_code==422
print("PROJECT_MANIFEST_HTTP_V189_PASS auth, approval/SHA, source, DAG and no-code leakage")
