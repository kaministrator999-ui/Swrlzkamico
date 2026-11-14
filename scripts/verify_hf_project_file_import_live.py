#!/usr/bin/env python3
"""Live read-only regression of §C imported source ownership and thread continuity.

Creates only anonymous synthetic sample source files; it never reads real
user data. Does not write repositories, project workspaces, or §E.
"""
import http.cookiejar,json,time,urllib.error,urllib.request,uuid
BASE="https://kamiloki-swyrlz.hf.space"
H={"User-Agent":"Swyrlz-Synthetic-File-Ownership-Check","Cache-Control":"no-cache"}
one=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
two=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
rid=str(uuid.uuid4());tid="swrlz-source-owner-check-"+uuid.uuid4().hex
tag="swrlz-test-tag-"+uuid.uuid4().hex
files=[{"path":"index.html","content":f"<!doctype html><html><body><button id='save'>{tag}</button></body></html>"},
       {"path":"src/main.js","content":"document.getElementById('save').addEventListener('click',()=>{});"}]
def post(opener,path,body):
    req=urllib.request.Request(BASE+path,method="POST",
        data=json.dumps(body).encode(),headers={**H,"Content-Type":"application/json"})
    with opener.open(req,timeout=30) as r:return r.status,json.load(r)
def sync(opener):
    req=urllib.request.Request(BASE+"/api/lalm_station/sync",headers=H)
    with opener.open(req,timeout=30) as r:return json.load(r)
payload={"modelId":"700m","threadId":tid,"requestId":rid,
    "prompt":"Read the uploaded source files; do not edit or publish anything.",
    "profileId":"LALM","timeZone":"UTC","projectFiles":files}
status,_=post(one,"/api/lalm_station/send",payload)
assert status==202
try:
    owned=None
    for step in range(10):
        state=sync(one)
        t=next((x for x in state.get("threads",[]) if x.get("id")==tid),None)
        if t and t.get("activeImportedArtifactId"):
            owned=t;break
        time.sleep(3)
    assert owned is not None,"User's own uploaded artifact not visible"
    artifacts=[a for a in owned.get("codeArtifacts",[]) if a.get("importedUserSource")]
    assert len(artifacts)==1
    artifact=artifacts[0]
    assert {x.get("path") for x in artifact.get("files",[])}=={"index.html","src/main.js"}
    assert any(tag in str(f.get("content","")) for f in artifact["files"])
    assert artifact.get("currentRevision")==1 and artifact.get("currentSourceHash")
    second=sync(two)
    assert not any(t.get("id")==tid for t in second.get("threads",[])),"Imported thread exposed to foreign session"
    assert tag not in json.dumps(second),"Imported file content exposed to foreign session"
    print("SWRLZ_LIVE_FILE_OWNERSHIP_VERIFIED",json.dumps({
        "ownSession":True,"foreignSessionIsolated":True,
        "files":len(artifact["files"]),"revision":artifact["currentRevision"],
        "sourceShaPresent":bool(artifact.get("currentSourceHash"))}),flush=True)
finally:
    try:post(one,"/api/lalm_station/cancel",{"requestId":rid})
    except Exception:pass
