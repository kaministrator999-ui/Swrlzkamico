"""v223: repository explorer source, scoped auth, continuity and mobile contract."""
import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from fastapi import HTTPException

sys.path.insert(0,str(Path(__file__).parent))
import github_connection as gh
import github_explorer_v223 as exp
# The lightweight GitHub CI does not run full HF packaging first; Station
# mounts this directory at import time, so create its empty test-only shell.
(Path(__file__).parent/"chat/§wyrlz/assets").mkdir(parents=True,exist_ok=True)
import station

REPO="owner/demo"
OWNER="google:verifiedOwner"
SHA="b"*40
RECORD={"token":"opaque-test-only","repo":REPO,"scopes":"read:user"}

ROWS=[
    {"path":"README.md","type":"blob","size":75,"sha":"1"*40},
    {"path":"src","type":"tree","sha":"2"*40},
    {"path":"src/app.py","type":"blob","size":150,"sha":"3"*40},
    {"path":"src/config.json","type":"blob","size":25,"sha":"4"*40},
    {"path":"docs","type":"tree","sha":"5"*40},
    {"path":"docs/config.py","type":"blob","size":40,"sha":"6"*40},
    {"path":"docs/guide.md","type":"blob","size":100,"sha":"7"*40},
    {"path":"src/internal","type":"tree","sha":"8"*40},
    {"path":"src/internal/worker.py","type":"blob","size":80,"sha":"9"*40},
]

def api(token,path):
    assert token==RECORD["token"],"Credential boundary violated"
    if path=="/repos/"+REPO+"/commits/main":return {"sha":SHA}
    if path=="/repos/"+REPO+"/git/trees/"+SHA+"?recursive=1":
        return {"tree":ROWS,"truncated":False}
    if path.startswith("/repos/"+REPO+"/commits?sha="+SHA+"&path="):
        return [{"sha":"c"*40,"commit":{"committer":{"date":"2026-10-11T19:00:00Z"},"message":"Latest change"}},
                {"sha":"d"*40,"commit":{"committer":{"date":"2025-10-11T19:00:00Z"},"message":"Added path"}}]
    if path=="/repos/"+REPO+"/compare/main...feature%2Fexample?per_page=30":
        return {"files":[{"filename":"src/app.py","status":"modified","additions":5,"deletions":1,"patch":"@@ -1 +1 @@\n-old\n+new"}],
                "base_commit":{"sha":"a"*40},"head_commit":{"sha":SHA},"total_commits":4}
    if path=="/repos/"+REPO+"/contents?ref=main":
        return [{"type":"file","path":"README.md"},{"type":"dir","path":"src"}]
    raise AssertionError("Unexpected GitHub REST route: "+path)

def snapshot():
    return exp.pinned_tree(api,RECORD["token"],REPO,"main")

def test_tree_directory_counts_sizes_and_search():
    snap=snapshot()
    assert snap["sourceSha"]==SHA and snap["complete"]
    root=exp.directory(snap)
    assert root["count"]==3,root
    assert root["stats"]=={"path":"","recursiveFiles":6,"recursiveDirectories":3,
                           "gitBlobBytes":470,"sizeComplete":True},root
    src=exp.directory(snap,"src")
    assert src["stats"]["recursiveFiles"]==3 and src["stats"]["gitBlobBytes"]==255
    deeper=next(x for x in src["entries"] if x["name"]=="internal")
    assert deeper["fileCount"]==1 and deeper["sizeBytes"]==80
    app=next(x for x in src["entries"] if x["name"]=="app.py")
    assert app["sizeBytes"]==150
    found=exp.find_files(snap,"config")
    assert found["total"]==2 and {x["path"] for x in found["matches"]}=={"src/config.json","docs/config.py"}
    assert exp.find_files(snap,"worker", "src")["total"]==1

def test_incomplete_tree_and_unsafe_paths_fail_closed():
    with mock.patch.object(exp,"MAX_ENTRIES",2):
        try: snapshot()
        except exp.ExplorerError as exc: assert "incomplete" in str(exc)
        else: raise AssertionError("Incomplete repo counted as exhaustive")
    def truncated(t,p):
        result=api(t,p)
        return {**result,"truncated":True} if "/git/trees/" in p else result
    try: exp.pinned_tree(truncated,RECORD["token"],REPO,"main")
    except exp.ExplorerError as exc: assert "incomplete" in str(exc)
    else: raise AssertionError("Truncated repo accepted")
    for bad in ("../private","/etc/passwd","docs//config","bad?query","bad\\slash"):
        try: exp.safe_path(bad)
        except exp.ExplorerError:pass
        else:raise AssertionError("Unsafe path accepted "+bad)
    for bad in ("../../main","feature//x","https://bad/",""):
        try: exp.safe_branch(bad)
        except exp.ExplorerError:pass
        else:raise AssertionError("Unsafe ref accepted "+bad)
    try:exp.directory(snapshot(),"not/a/folder")
    except exp.ExplorerError:pass
    else:raise AssertionError("Unknown folder returned verified stats")

def test_history_and_bounded_diff_evidence():
    last=exp.history(api,RECORD["token"],REPO,SHA,"src/app.py")
    assert last["lastCommit"]["date"].startswith("2026-10-11")
    assert last["firstSeenComplete"] and last["firstSeenPathCommit"]["sha"]=="d"*40
    assert "not a filesystem" in last["caution"]
    comparison=exp.comparison(api,RECORD["token"],REPO,"main","feature/example")
    assert comparison["headSha"]==SHA and comparison["totalCommits"]==4
    assert len(comparison["files"])==1 and comparison["files"][0]["status"]=="modified"

def test_authenticated_endpoints_and_only_selected_repo():
    with mock.patch.object(gh,"_explorer_owner",return_value=(OWNER,RECORD,REPO,"main")), \
         mock.patch.object(gh,"_api",side_effect=api), \
         mock.patch.object(gh,"_read_optional",return_value={"body":"def app():\n    return 1",
                                                           "sha":"3"*40}):
        root=gh.explorer_directory(object())
        assert root["repository"]==REPO and root["stats"]["recursiveFiles"]==6
        file=gh.explorer_file(object(),"src/app.py")
        assert file["readable"] and file["content"].startswith("def app()")
        assert gh.explorer_search(object(),"config")["total"]==2
        assert gh.explorer_history(object(),"src/app.py")["firstSeenComplete"]
        assert gh.explorer_modified(object(),"src/app.py")["lastChangedAt"].startswith("2026-10-11")
        assert gh.explorer_compare(object(),"main","feature/example")["totalCommits"]==4
        try:gh.explorer_file(object(),"private/no.txt")
        except HTTPException as exc:assert exc.status_code==422
        else:raise AssertionError("Unverified file returned")
    with mock.patch.object(gh,"GITHUB_CAPABILITY_STAGE","unknown"):
        try:gh._explorer_owner(object())
        except HTTPException as exc:assert exc.status_code==403
        else:raise AssertionError("Non-read-only stage accepted")

def test_thread_continuity_and_read_only_guard():
    context=gh.normalize_thread_context({"repo":REPO,"branch":"main","sourceSha":SHA,
                                        "directory":"src","lastFile":"src/app.py"})
    assert context
    assert gh._implicit_repo_command("How many files are there?",context)=="@GitHub stats src"
    assert gh._implicit_repo_command("And directories?",context)=="@GitHub stats src"
    assert gh._implicit_repo_command("Show the files",context)=="@GitHub files src"
    assert gh._implicit_repo_command("Show the largest 5 files",context)=="@GitHub largest 5 src"
    assert gh._implicit_repo_command("Which python files?",context)=="@GitHub search .py"
    assert gh._implicit_repo_command("Read that file",context)=="@GitHub read file src/app.py"
    assert gh._implicit_repo_command("Create a file",context) is None
    assert gh._implicit_repo_command("Change deployment today",context) is None
    assert gh._implicit_repo_command("Hi",context) is None
    assert gh._implicit_repo_command("How many files are there?",None) is None
    assert not gh._read_stage_command("@GitHub delete file src/app.py")
    assert gh._read_stage_command("@GitHub stats src")
    assert gh._read_stage_command("@GitHub compare main...feature/example")
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(gh,"_effective_access",return_value={"allowed":True,"defaultBranch":"main"}), \
         mock.patch.object(gh,"_api",side_effect=api):
        events=list(gh.command_events({"userId":OWNER,"prompt":"@GitHub files"}))
        source=[e for e in events if e.get("type")=="GITHUB_CONTEXT"]
        assert source and source[0]["context"]["repo"]==REPO and source[0]["context"]["sourceSha"]==SHA

def test_persist_verified_ui_browsing_context():
    record={"revision":1,"ownerGoogleId":OWNER,"threads":[
        {"id":"threadA","messages":[]},
        {"id":"threadB","messages":[]}]}
    async def case(owner=OWNER, source=SHA, path="src"):
        request=SimpleNamespace(json=lambda:None)
        async def payload():return {"threadId":"threadA","kind":"dir","path":path,
                                   "branch":"main","sourceSha":source}
        request.json=payload
        with mock.patch.object(station,"_session",return_value=("session",record)), \
             mock.patch.object(station,"_account_session",return_value=({},{"id":owner})), \
             mock.patch.object(station.github_connection,"_explorer_owner",
                               return_value=(OWNER,RECORD,REPO,"main")), \
             mock.patch.object(station.github_connection.explorer,"pinned_tree",return_value=snapshot()), \
             mock.patch.object(station,"_refresh_account_chat",return_value=None), \
             mock.patch.object(station,"_commit_revision",side_effect=lambda s:s.update(revision=s["revision"]+1)):
            return await station.set_thread_github_context(request)
    saved=asyncio.run(case())
    assert saved["ok"] and saved["githubContext"]["directory"]=="src"
    assert record["threads"][0]["githubContext"]["repo"]==REPO
    assert not record["threads"][1].get("githubContext")
    try:asyncio.run(case(source="a"*40))
    except HTTPException as exc:assert exc.status_code==409
    else:raise AssertionError("Stale source accepted")
    try:asyncio.run(case(owner="google:other"))
    except HTTPException as exc:assert exc.status_code==403
    else:raise AssertionError("Cross-account context accepted")
    try:asyncio.run(case(path="private"))
    except HTTPException as exc:assert exc.status_code==404
    else:raise AssertionError("Unverified path accepted")

if __name__=="__main__":
    test_tree_directory_counts_sizes_and_search()
    test_incomplete_tree_and_unsafe_paths_fail_closed()
    test_history_and_bounded_diff_evidence()
    test_authenticated_endpoints_and_only_selected_repo()
    test_thread_continuity_and_read_only_guard()
    test_persist_verified_ui_browsing_context()
    print("GitHub v223 metadata, read-only APIs, user/thread isolation and follow-ups PASS")
