"""End-to-end FastAPI download endpoint tests with local dummy model router.

The route must only return canonical artifacts from the caller's cookie-scoped
session, correct immutable revision and hash. No GGUF backend or model download.
"""
import io
import sys
import types
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))
stub=types.ModuleType("model_router")
stub.dispatch=lambda *args, **kwargs: iter(())
stub.routes=lambda: []
stub.ModelUnavailable=type("ModelUnavailable", (RuntimeError,), {})
sys.modules["model_router"]=stub

# The production HF build places the Chat assets alongside station.py. The
# source checkout does not need that built artifact for this endpoint test.
(Path(__file__).resolve().parent / "chat" / "§wyrlz" / "assets").mkdir(parents=True, exist_ok=True)
import station  # noqa: E402

def make(files, aid, msg_id, version=1, archive_requested=False):
    sha=station._artifact_source_hash(files)
    record={"revision":version,"files":files,"sourceHash":sha,"archiveRequested":archive_requested}
    artifact={"id":aid,"type":"code","sourceMessageId":msg_id,"currentRevision":version,"currentSourceHash":sha,"files":files,"revisions":[record]}
    return artifact, sha

files=[{"path":"src/main.py","language":"python","content":"print(7)\n"},
       {"path":"tests/test_main.py","language":"python","content":"assert 7 == 7\n"}]
single=[{"path":"README.md","language":"markdown","content":"# Hello\n"}]
multi, multi_hash=make(files,"artifact-multi","m1")
single_art, single_hash=make(single,"artifact-single","m2")
forced, forced_hash=make(single,"artifact-forced","m3",archive_requested=True)
other, other_hash=make(single,"artifact-private","m4")
bad, bad_hash=make([{"path":"../../secret.txt","language":"text","content":"hidden"}],"artifact-invalid","m5")

station._sessions.clear()
station._sessions.update({
    "session-a":{"threads":[{"id":"thread-a","codeArtifacts":[multi,single_art,forced,bad]}]},
    "session-b":{"threads":[{"id":"thread-b","codeArtifacts":[other]}]},
})

client=TestClient(station.app)
client.cookies.set("swrlz_hf_sid","session-a")
base="/api/lalm_station/artifacts/download"

def get(artifact_id, source_hash, rev=1, tid="thread-a", extra=None):
    q={"threadId":tid,"artifactId":artifact_id,"revision":rev,"sourceHash":source_hash}
    if extra:q.update(extra)
    return client.get(base,params=q)

resp=get("artifact-single",single_hash)
assert resp.status_code==200, resp.text
assert resp.content == b"# Hello\n" and "filename=\"README.md\"" in resp.headers["content-disposition"]
assert resp.headers["cache-control"] == "private, no-store"
assert resp.headers["x-content-type-options"] == "nosniff"
assert resp.headers["cross-origin-resource-policy"] == "same-origin"

resp=get("artifact-multi",multi_hash)
assert resp.status_code==200 and resp.headers["content-type"].startswith("application/zip")
with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
    assert sorted(z.namelist())==["src/main.py","tests/test_main.py"]
    assert z.read("src/main.py")==b"print(7)\n"

resp=get("artifact-single",single_hash,extra={"asArchive":"true"})
assert resp.status_code==200 and resp.headers["content-type"].startswith("application/zip")

resp=get("artifact-forced",forced_hash)
assert resp.status_code==200 and "filename=\"README.zip\"" in resp.headers["content-disposition"]
with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
    assert z.namelist()==["README.md"]

assert get("artifact-multi",multi_hash,rev=2).status_code==404
assert get("artifact-multi","0"*64).status_code==404
assert get("artifact-multi",multi_hash,tid="thread-b").status_code==404
assert get("artifact-private",other_hash,tid="thread-b").status_code==404
assert get("artifact-invalid",bad_hash).status_code==422
assert get("artifact-single",single_hash,rev=0).status_code==400

client.cookies.set("swrlz_hf_sid","session-b")
assert get("artifact-multi",multi_hash).status_code==404
assert get("artifact-private",other_hash,tid="thread-b").status_code==200
client.cookies.clear()
assert get("artifact-single",single_hash).status_code==404

# Mutating canonical records after the sourceHash was issued must fail closed.
single_art["revisions"][0]["files"][0]["content"]="# changed\n"
client.cookies.set("swrlz_hf_sid","session-a")
assert get("artifact-single",single_hash).status_code==409

print("CODE_PACKAGES_HTTP_V184_PASS cookies, complete revisions, SHA, ZIP, forbidden paths")
