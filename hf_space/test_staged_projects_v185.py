"""Public offline manifest/ledger tests: no inference, compiler or model output claims."""
import copy
import hashlib
import io
import json
import uuid
import zipfile
from staged_projects import (
    WorkspaceError, SCHEMA, MANIFEST_SCHEMA, parse_manifest, create_workspace,
    stage_files, project_view, package_project,
)

manifest={"schema":MANIFEST_SCHEMA,"name":"dragon-demo",
          "files":["src/app.py","tests/test_app.py","README.md"]}
text=""+chr(96)*3+"project-manifest\n"+json.dumps(manifest)+"\n"+chr(96)*3
assert parse_manifest("ordinary prose") is None
assert parse_manifest(text)==manifest
project=create_workspace(parse_manifest(text),"workspace-"+uuid.uuid4().hex,"req-1")
assert project["revision"]==1 and not project["canDownload"]
assert project["missingFiles"]==manifest["files"]
def f(path,content):
    return {"path":path,"content":content,"language":"python"}
def put(state,files,request,replace=False,revision=None):
    return stage_files(state,files,expected_revision=state["revision"] if revision is None else revision,
        request_id=request,artifact_id="artifact-"+request,
        artifact_revision=1,artifact_source_hash="a"*64,allow_replace=replace)

project,receipt=put(project,[f("src/app.py","print(1)\n")],"req-1")
assert receipt=="COMMITTED" and project["revision"]==2 and not project["canDownload"]
assert project_view(project)["missingFiles"]==["tests/test_app.py","README.md"]
try:package_project(project)
except WorkspaceError as exc:assert "INCOMPLETE" in str(exc)
else:raise AssertionError("missing files became downloadable")
unchanged,receipt=put(project,[f("src/app.py","print(1)\n")],"req-2")
assert receipt=="UNCHANGED" and unchanged==project
snapshot=copy.deepcopy(project)
for violation in (
    [f("other.py","malicious")],
    [f("src/app.py","changed")],
    [f("README.md","A"),f("README.md","B")],
    [f("../evil.py","attack")],
    [f("README.md","A"),f("other.py","B")],
):
    try:put(project,violation,"bad")
    except WorkspaceError:pass
    else:raise AssertionError("Atomic ledger accepted invalid files: "+str(violation))
    assert snapshot==project,"failed apply mutated canonical state"

try:put(project,[f("README.md","A")],"bad",revision=1)
except WorkspaceError as exc:assert "REVISION_CONFLICT" in str(exc)
else:raise AssertionError("stale writer committed")
project,receipt=put(project,[f("tests/test_app.py","assert True\n")],"req-2")
assert not project["canDownload"] and project["revision"]==3
project,receipt=put(project,[f("README.md","# Demo\n")],"req-3")
assert project["canDownload"] and project["revision"]==4
assert project["completion"]=="FILES_PRESENT_UNVERIFIED"
assert project["verification"]=="NOT_RUN"
package=package_project(project)
assert package["archive"] and package["fileCount"]==3
with zipfile.ZipFile(io.BytesIO(package["body"])) as z:
    assert z.namelist()==["README.md","src/app.py","tests/test_app.py"]
    assert z.read("src/app.py")==b"print(1)\n"

# Full revisions/explicit replacement preserve unrelated files.
try:put(project,[f("src/app.py","print(2)\n")],"req-4")
except WorkspaceError as exc:assert "EXISTING_FILE_CHANGE" in str(exc)
else:raise AssertionError("implicit replace accepted")
updated,_=put(project,[f("src/app.py","print(2)\n")],"req-4",replace=True)
assert updated["revision"]==5
assert next(x for x in updated["entries"] if x["path"]=="README.md")["content"]=="# Demo\n"
assert next(x for x in updated["entries"] if x["path"]=="src/app.py")["content"]=="print(2)\n"
assert project["revision"]==4 and package_project(project)["sha256"]==package["sha256"]
tampered=copy.deepcopy(updated);tampered["entries"][0]["content"]="tamper"
try:package_project(tampered)
except WorkspaceError as exc:assert "HASH" in str(exc)
else:raise AssertionError("tampered file downloadable")
assert "print(1)" not in str(project_view(project)), "public ledger leaked code"

# No ambient arbitrary JSON, duplicate manifest, unsafe paths or wrong shapes.
for bad in [
    {**manifest,"files":["src/main.py","src/Main.py"]},
    {**manifest,"files":["src","src/main.py"]},
    {**manifest,"files":["src/../evil.py","README.md"]},
    {**manifest,"files":["README.md"]},
    {**manifest,"files":[f"file-{i}.py" for i in range(33)]},
    {**manifest,"name":"../../escape"},
]:
    body=chr(96)*3+"project-manifest\n"+json.dumps(bad)+"\n"+chr(96)*3
    try:parse_manifest(body)
    except WorkspaceError:pass
    else:raise AssertionError("invalid manifest accepted "+repr(bad))
try:parse_manifest(text+"\n"+text)
except WorkspaceError:pass
else:raise AssertionError("double manifest accepted")
assert parse_manifest(json.dumps(manifest)) is None
print("STAGED_PROJECTS_V185_PASS staged three-turn ZIP, atomicity, old revisions, path safety, no fake verification")
