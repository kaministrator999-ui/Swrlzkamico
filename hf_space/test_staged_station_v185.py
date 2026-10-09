"""Real Station handlers on dummy model routes: process-local, no model downloads."""
import io
import json
import sys
import types
import uuid
import zipfile
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0,str(Path(__file__).resolve().parent))
router=types.ModuleType("model_router")
router.dispatch=lambda *args,**kw:iter(())
router.routes=lambda:[]
router.ModelUnavailable=type("ModelUnavailable",(RuntimeError,),{})
sys.modules["model_router"]=router
(Path(__file__).resolve().parent/"chat"/"§wyrlz"/"assets").mkdir(parents=True,exist_ok=True)
import station  # noqa: E402

def fence(label,body):
    tick=chr(96)*3
    return tick+label+"\n"+body+"\n"+tick
def source(path,body):
    return fence("python file="+path,body)
manifest={"schema":"swrlz-project-manifest-v1","name":"dragon-project",
          "files":["src/main.py","tests/test_main.py","README.md"]}
manifest_text=fence("project-manifest",json.dumps(manifest))
station._sessions.clear()
thread={"id":"thread-a","messages":[],"codeArtifacts":[],"projectWorkspaces":[]}
second={"id":"thread-b","messages":[],"codeArtifacts":[],"projectWorkspaces":[]}
station._sessions["alpha"]={"threads":[thread],"revision":0,"currentId":"thread-a","activeGeneration":None}
station._sessions["beta"]={"threads":[second],"revision":0,"currentId":"thread-b","activeGeneration":None}

def commit(req,txt,selected=None):
    msg={"id":"answer-"+req,"role":"assistant","text":txt,"meta":{"state":"COMPLETE"}}
    artifact=station._create_code_artifact(thread,msg,req,txt)
    thread["messages"].append(msg)
    receipt=station._stage_completed_generation(thread,{"stagedProject":selected},txt,req,artifact)
    return receipt,msg,artifact

start=manifest_text+"\n"+source("src/main.py","print(1)")
receipt,msg,artifact=commit("request-1",start)
assert receipt["status"]=="COMMITTED",receipt
assert artifact and [x["path"] for x in artifact["files"]]==["src/main.py"], artifact
project=thread["autoProjectWorkspaces"][0]
assert project["fileCount"]==1 and not project["canDownload"]
assert thread["projectWorkspaces"]==[], "Auto workspace touched the manual owner"
assert project["missingFiles"]==["tests/test_main.py","README.md"]
snapshot=station._snapshot(station._sessions["alpha"])
view=snapshot["currentThread"]["autoProjectWorkspaces"][0]
assert "entries" not in view and view["revision"]==2
assert "print(1)" not in json.dumps(view)
assert station._select_staged_workspace(thread,"What's a turtle?") is None
assert station._select_staged_workspace(thread,"Continue project: next files")["id"]==project["id"]

client=TestClient(station.app)
client.cookies.set("swrlz_hf_sid","alpha")
url="/api/lalm_station/projects/download"
def get(revision=None,session=None,tid="thread-a",mid=None):
    q={"threadId":tid,"workspaceId":mid or project["id"],
       "revision":revision or project["revision"],
       "manifestSha256":project["manifestSha256"]}
    return client.get(url,params=q)
assert get().status_code==409
assert get(tid="thread-b").status_code==404
client.cookies.set("swrlz_hf_sid","beta")
assert get().status_code==404
client.cookies.set("swrlz_hf_sid","alpha")

old=station.project_view(project)
receipt,msg2,a2=commit("request-2",source("tests/test_main.py","assert True"),
                      {**old,"allowReplace":False})
assert receipt["status"]=="COMMITTED"
project=thread["autoProjectWorkspaces"][0]
assert project["revision"]==3 and not project["canDownload"]
assert get(revision=2).status_code==404

# Wrong source file and stale session snapshot must leave the prior bytes intact.
prior=json.dumps(project,sort_keys=True)
r,_,_=commit("request-bad",source("src/unknown.py","pass"),
             {**station.project_view(project),"allowReplace":False})
assert r["status"]=="REJECTED" and "UNDECLARED" in r["error"]
assert json.dumps(project,sort_keys=True)==prior
r,_,_=commit("request-stale",source("README.md","# Readme"),
             {**old,"allowReplace":False})
assert r["status"]=="REJECTED" and "REVISION_CONFLICT" in r["error"]
assert json.dumps(project,sort_keys=True)==prior

r,_,_=commit("request-3",fence("markdown file=README.md","# Dragon"),
             {**station.project_view(project),"allowReplace":False})
assert r["status"]=="COMMITTED"
project=thread["autoProjectWorkspaces"][0]
assert project["revision"]==4 and project["canDownload"]
done=get()
assert done.status_code==200 and done.headers["content-type"].startswith("application/zip")
assert done.headers["cache-control"]=="private, no-store"
with zipfile.ZipFile(io.BytesIO(done.content)) as z:
    assert z.namelist()==["README.md","src/main.py","tests/test_main.py"]
    assert z.read("README.md")==b"# Dragon\n"
    assert z.read("src/main.py")==b"print(1)\n"
assert get(revision=3).status_code==404

# Edited file requires user-directed edit intent; update preserves old files.
receipt,_,_=commit("request-4",source("src/main.py","print(2)"),
                   {**station.project_view(project),"allowReplace":False})
assert receipt["status"]=="REJECTED"
receipt,_,_=commit("request-5",source("src/main.py","print(2)"),
                   {**station.project_view(project),"allowReplace":True})
assert receipt["status"]=="COMMITTED"
project=thread["autoProjectWorkspaces"][0]
assert project["revision"]==5
assert get(revision=4).status_code==404
updated=get()
assert updated.status_code==200
with zipfile.ZipFile(io.BytesIO(updated.content)) as z:
    assert z.read("src/main.py")==b"print(2)\n"
    assert z.read("README.md")==b"# Dragon\n"

print("STAGED_STATION_V185_PASS 3-turn commit, incomplete archive refusal, revisions, scoped-cookie ZIP, repair")
