"""Pure multi-turn manifest correctness, SHA, concurrency and state transitions."""
import copy
from staged_workspaces import (create_workspace, attach_revision, finalize, cancel,
                               progress, downloadable_files, WorkspaceError, WorkspaceConflict)
from code_packages import build_package

WID="workspace-"+"a"*32
SHA="a"*64
paths=["src/app.py","tests/test_app.py","README.md"]
w=create_workspace(WID,"My project",paths)
assert progress(w)["completedCount"]==0 and len(progress(w)["remainingPaths"])==3
assert w["validationState"]=="NOT_RUN"
first=attach_revision(w,[{"path":"src/app.py","language":"python","content":"print(1)\n"}],
                      artifact_id="artifact-a",artifact_revision=1,artifact_sha=SHA,expected_revision=1)
assert w["revision"]==1 and not w["files"], "source input must not mutate"
assert first["revision"]==2 and progress(first)["completedCount"]==1
try:
    finalize(first,2)
except WorkspaceError:
    pass
else:
    raise AssertionError("incomplete workspace finalized")
second=attach_revision(first,[
    {"path":"tests/test_app.py","language":"python","content":"assert 1==1\n"},
    {"path":"README.md","language":"markdown","content":"# Test\n"},
],artifact_id="artifact-b",artifact_revision=2,artifact_sha=SHA,expected_revision=2)
assert progress(second)["completedCount"]==3
ready=finalize(second,3)
assert ready["state"]=="READY" and ready["revision"]==4 and len(ready["sourceHash"])==64
assert ready["validationState"]=="NOT_RUN", "package completeness is not an acceptance test"
files=downloadable_files(ready,4,ready["sourceHash"])
archive=build_package(files,force_archive=True)
assert archive["archive"] and archive["fileCount"]==3
assert build_package(downloadable_files(ready,4,ready["sourceHash"]),force_archive=True)["body"]==archive["body"]
for func in [
    lambda: attach_revision(ready,[{"path":"README.md","language":"markdown","content":"mutate"}],
                            artifact_id="artifact-c",artifact_revision=1,artifact_sha=SHA,expected_revision=4),
    lambda: finalize(ready,4),
    lambda: downloadable_files(ready,3,ready["sourceHash"]),
    lambda: downloadable_files(ready,4,"0"*64),
]:
    try:func()
    except WorkspaceConflict:pass
    else:raise AssertionError("accepted stale/finalized revision")

# Candidate patches only update the exact named path; new data invalidates old
# grading and source hashes, while initial copy is unchanged.
revised=attach_revision(first,[{"path":"src/app.py","language":"python","content":"print(2)\n"}],
                        artifact_id="artifact-c",artifact_revision=3,artifact_sha=SHA,expected_revision=2)
assert revised["files"]["src/app.py"]["content"]=="print(2)\n"
assert first["files"]["src/app.py"]["content"]=="print(1)\n"
assert revised["validationState"]=="NOT_RUN"
for invalid in [
    ["../secret.py"], ["src/a.py","src/A.py"], ["C:/absolute.py"], [],
    [f"file{i}.py" for i in range(33)]
]:
    try:create_workspace(WID,"unsafe",invalid)
    except WorkspaceError:pass
    else:raise AssertionError("unsafe manifest passed")

for rejected in [
    [{"path":"src/other.py","language":"python","content":"x"}],
    [{"path":"README.md","language":"lyrics","content":"fake source"}],
    [{"path":"README.md","language":"markdown","content":"x"* (1024*1024+1)}],
    [{"path":"src/app.py","language":"python","content":"a"},
     {"path":"src/app.py","language":"python","content":"b"}],
]:
    try:attach_revision(w,rejected,artifact_id="x",artifact_revision=1,artifact_sha=SHA,expected_revision=1)
    except WorkspaceError:pass
    else:raise AssertionError("unsafe input was accepted")

try:attach_revision(first,[{"path":"README.md","language":"markdown","content":"x"}],
                    artifact_id="x",artifact_revision=1,artifact_sha=SHA,expected_revision=1)
except WorkspaceConflict:pass
else:raise AssertionError("stale optimistic revision accepted")

abandoned=cancel(first,2)
assert abandoned["state"]=="CANCELLED"
try:finalize(abandoned,3)
except WorkspaceConflict:pass
else:raise AssertionError("cancelled workspace could finish")

tampered=copy.deepcopy(ready)
tampered["files"]["README.md"]["content"]="different"
try:downloadable_files(tampered,4,ready["sourceHash"])
except WorkspaceConflict:pass
else:raise AssertionError("tampered ZIP escaped hash check")
assert progress(first)["remainingPaths"]==["tests/test_app.py","README.md"]
print("STAGED_WORKSPACES_V185_PASS manifest, multi-turn, revision, hash, cancel, zip gate")
