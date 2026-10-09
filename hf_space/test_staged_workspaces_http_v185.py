"""HTTP tests: manifest progression, resumability, same-cookie ownership, ZIP-ready gate."""
import io
import sys
import types
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0,str(Path(__file__).resolve().parent))
stub=types.ModuleType("model_router")
stub.dispatch=lambda *args,**kwargs: iter(())
stub.routes=lambda: []
stub.ModelUnavailable=type("ModelUnavailable",(RuntimeError,),{})
sys.modules["model_router"]=stub
(Path(__file__).resolve().parent/"chat"/"§wyrlz"/"assets").mkdir(parents=True,exist_ok=True)
import station  # noqa:E402


def owned_artifact(artifact_id, files):
    sha=station._artifact_source_hash(files)
    return {"id":artifact_id,"type":"code","sourceMessageId":artifact_id,
            "files":files,"currentRevision":1,"currentSourceHash":sha,
            "revisions":[{"revision":1,"files":files,"sourceHash":sha}]},sha

a,a_sha=owned_artifact("artifact-a",[{"path":"src/app.py","language":"python","content":"print(2)\n"}])
b,b_sha=owned_artifact("artifact-b",[
    {"path":"tests/test_app.py","language":"python","content":"assert True\n"},
    {"path":"README.md","language":"markdown","content":"# app\n"},
])
extra,extra_sha=owned_artifact("artifact-extra",[{"path":"not-required.txt","language":"text","content":"x"}])
station._sessions.clear()
station._sessions["owner"]={"revision":0,"currentId":"thread-a","threads":[
    {"id":"thread-a","messages":[],"codeArtifacts":[a,b,extra]},
]}
station._sessions["other"]={"revision":0,"currentId":"thread-a","threads":[
    {"id":"thread-a","messages":[],"codeArtifacts":[]},
]}
client=TestClient(station.app)
root="/api/lalm_station/workspaces"
client.cookies.set("swrlz_hf_sid","owner")
resp=client.post(root,json={"threadId":"thread-a","title":"Project",
                            "requiredPaths":["src/app.py","tests/test_app.py","README.md"]})
assert resp.status_code==200,resp.text
initial=resp.json()["workspace"]
wid=initial["id"]
assert initial["completedCount"]==0 and initial["revision"]==1
assert client.get(root,params={"threadId":"thread-a"}).json()["workspaces"][0]["id"]==wid

download_args={"threadId":"thread-a","workspaceId":wid,"revision":1,"sourceHash":"a"*64}
assert client.get(root+"/download",params=download_args).status_code==409
finalize={"threadId":"thread-a","workspaceId":wid,"expectedWorkspaceRevision":1}
assert client.post(root+"/finalize",json=finalize).status_code==422

attach={"threadId":"thread-a","workspaceId":wid,"artifactId":"artifact-a","artifactRevision":1,
        "artifactSourceHash":a_sha,"expectedWorkspaceRevision":1}
resp=client.post(root+"/attach",json=attach)
assert resp.status_code==200,resp.text
assert resp.json()["workspace"]["completedCount"]==1
assert client.post(root+"/attach",json=attach).status_code==409
attach["artifactId"]="artifact-extra"
attach["artifactSourceHash"]=extra_sha
attach["expectedWorkspaceRevision"]=2
assert client.post(root+"/attach",json=attach).status_code==422
attach["artifactId"]="artifact-b"
attach["artifactSourceHash"]=b_sha
resp=client.post(root+"/attach",json=attach)
assert resp.status_code==200,resp.text
assert resp.json()["workspace"]["completedCount"]==3
assert resp.json()["workspace"]["revision"]==3
assert client.post(root+"/finalize",json={**finalize,"expectedWorkspaceRevision":2}).status_code==409
done=client.post(root+"/finalize",json={**finalize,"expectedWorkspaceRevision":3})
assert done.status_code==200,done.text
ready=done.json()["workspace"]
assert ready["state"]=="READY" and ready["validationState"]=="NOT_RUN"
args={"threadId":"thread-a","workspaceId":wid,
      "revision":ready["revision"],"sourceHash":ready["sourceHash"]}
zip_resp=client.get(root+"/download",params=args)
assert zip_resp.status_code==200,zip_resp.text
assert zip_resp.headers["content-type"].startswith("application/zip")
assert zip_resp.headers["cache-control"]=="private, no-store"
assert zip_resp.headers["x-workspace-validation"]=="not-run"
with zipfile.ZipFile(io.BytesIO(zip_resp.content)) as archive:
    assert archive.namelist()==["README.md","src/app.py","tests/test_app.py"]
    assert archive.read("src/app.py")==b"print(2)\n"
assert client.get(root+"/download",params={**args,"sourceHash":"0"*64}).status_code==409
assert client.get(root+"/download",params={**args,"revision":1}).status_code==409
assert client.post(root+"/attach",json={**attach,"expectedWorkspaceRevision":4}).status_code==409
client.cookies.set("swrlz_hf_sid","other")
assert client.get(root+"/download",params=args).status_code==404
assert client.get(root,params={"threadId":"thread-a"}).json()["workspaces"]==[]
client.cookies.clear()
assert client.get(root+"/download",params=args).status_code==404
client.cookies.set("swrlz_hf_sid","owner")
assert client.post(root,json={"threadId":"forged-thread","requiredPaths":["file.py"]}).status_code==404

# The project can also be cancelled without erasing its audit/progress record.
started=client.post(root,json={"threadId":"thread-a","requiredPaths":["next.py"]}).json()["workspace"]
stop=client.post(root+"/cancel",json={"threadId":"thread-a","workspaceId":started["id"],
                                      "expectedWorkspaceRevision":started["revision"]})
assert stop.status_code==200 and stop.json()["workspace"]["state"]=="CANCELLED"
assert client.get(root+"/download",params={
    "threadId":"thread-a","workspaceId":started["id"],"revision":2,"sourceHash":"a"*64,
}).status_code==409
print("STAGED_WORKSPACES_HTTP_V185_PASS manifest, attach, partial-block, zip, cookie, cancel")
