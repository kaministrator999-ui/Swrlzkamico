"""v213 §E project-scoped GitHub source and draft-starter authorization regressions."""
import copy
import json
import re
import sys
from pathlib import Path
from unittest import mock

from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).parent))
import github_connection as gh
# Historical mutation test cases use test-only capability mode.
gh.GITHUB_CAPABILITY_STAGE = "legacy-test-only"
import forge_project_tools_v213 as engine
import github_workflows_v212 as workflows

OWNER = "google:verified-user"
REPO = engine.ENGINE_REPO
REC = {"token": "PRIVATE_OAUTH_TOKEN", "scopes": "read:user public_repo", "repo": REPO}
SHA_MAIN = "a" * 40
SHA_BRANCH = "b" * 40
SHA_SOURCE = "c" * 40
SHA_MANIFEST = "d" * 40
SCENE = {"engine":"§wyrl§ Engine · Maker v10.0","version":10,
         "project":{"name":"Sheep Tag · Moonbell Meadow","canonicalId":"sheep-tag-meadow",
                    "template":"sheep-tag-meadow","kind":"sheep-tag",
                    "sheepTag":{"duration":1200}},
         "editor":{"layers":[{"id":"layer-1","name":"Meadow","visible":True}]},
         "scene":{"actors":[{"id":"sheep-1","type":"st-sheep"}],"paths":{}}}
MANIFEST = {"schema":"swrlz-forge-source-v2","name":"§wyrl§ Engine v10.0",
            "patches":["patches/v9_9_episode_shuttle.py","patches/v10_0_sheep_tag.py"],
            "finalSha256":"e"*64}
DEPLOY = {"sourceCommit":"f"*40,"releaseVersion":"v10.0"}
SAVED = {}
WRITES = []


def fake_api(token, path):
    assert token == REC["token"]
    if path == "/repos/" + REPO:
        return {"full_name":REPO,"private":False,"default_branch":"main",
                "permissions":{"pull":True,"push":True,"admin":True}}
    if path == "/repos/" + REPO + "/contents/" + engine.SCENES + "?ref=main":
        return [{"type":"file","name":"sheep-tag-meadow.swyrl.json",
                 "path":engine.SCENES+"/sheep-tag-meadow.swyrl.json","size":86684},
                {"type":"file","name":"starforge-observatory.swyrl.json",
                 "path":engine.SCENES+"/starforge-observatory.swyrl.json","size":176835}]
    if path.startswith("/repos/" + REPO + "/git/ref/heads/"):
        return {"object":{"sha":SHA_MAIN if path.endswith("main") else SHA_BRANCH}}
    if path.startswith("/repos/" + REPO + "/contents/" + engine.SCENES + "/"):
        if "?ref=feature" in path:
            raise HTTPException(404, "No file present")
    if path.startswith("/repos/" + REPO + "/compare/main..."):
        return {"files":[{"filename":engine.SCENES+"/my-meadow.swyrl.json","status":"added"}]}
    raise AssertionError("Unexpected engine REST: " + path)


def fake_text(token, repo, path, ref, max_bytes=500000):
    assert token == REC["token"] and repo == REPO
    if path == engine.SOURCE:
        return {"path":path,"sha":SHA_MANIFEST,"body":json.dumps(MANIFEST)}
    if path == engine.DEPLOY:
        return {"path":path,"sha":"e"*40,"body":json.dumps(DEPLOY)}
    if path == engine.SCENES + "/sheep-tag-meadow.swyrl.json":
        assert ref == "main"
        return {"path":path,"sha":SHA_SOURCE,"body":json.dumps(SCENE)}
    raise AssertionError("Unexpected source file: " + path + " / " + str(ref))


def fake_redis(_cfg, operation, key, *args):
    if operation == "SET":
        assert key not in SAVED
        SAVED[key] = args[0]
        return "OK"
    if operation == "GETDEL":
        return SAVED.pop(key, None)
    raise AssertionError("Unexpected redis op "+operation)


def fake_write(token, method, uri, body):
    assert token == REC["token"] and method in ("PUT","POST")
    WRITES.append((method, uri, body))
    if method == "PUT":
        return {"content":{"path":engine.SCENES+"/my-meadow.swyrl.json"},
                "commit":{"sha":"1"*40}}
    return {"number":14,"html_url":"https://github.com/"+REPO+"/pull/14"}


def patches():
    return (
        mock.patch.object(gh, "_config", return_value={}),
        mock.patch.object(gh, "_load", return_value=REC),
        mock.patch.object(gh, "_api", side_effect=fake_api),
        mock.patch.object(gh, "_text", side_effect=fake_text),
        mock.patch.object(gh, "_redis", side_effect=fake_redis),
        mock.patch.object(workflows, "_write_request", side_effect=fake_write),
    )


def test_engine_entry_and_project_separation():
    assert engine.is_command("@GitHub engine status")
    assert engine.is_command("@GitHub engine clone sheep-tag-meadow as my-meadow on feature/work")
    assert engine.is_conversation("Can you inspect our game engine?")
    assert engine.is_conversation("Review our editor")
    assert not engine.is_conversation("Draw a game logo")
    assert gh.is_github_command("@GitHub engine starters")
    with mock.patch.object(gh, "_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value={"token":"t","repo":"owner/other","scopes":"read:user"}):
        try:
            gh._github_command(OWNER,"@GitHub engine status")
        except HTTPException as e:
            assert e.status_code == 409
        else:
            raise AssertionError("Other selected repository was silently replaced")


def test_source_mapping_and_realistic_mission_plan():
    with patches()[0],patches()[1],patches()[2],patches()[3]:
        result=gh._github_command(OWNER,"@GitHub engine status")
        assert "v10.0" in result and "2 ordered patches" in result
        assert "Chat/LALM have separate deployment paths" in result
        result=gh._github_command(OWNER,"@GitHub engine starters")
        assert "sheep-tag-meadow" in result and "starforge-observatory" in result
        assert "does NOT mean it appears" in result
        result=gh._github_command(OWNER,"@GitHub engine plan make a MOBA starter pack")
        assert "playable mode" in result and "not a built game" in result
        assert "native editor Save/Load/Undo/Redo" in result
        result=gh._github_command(OWNER,"@GitHub engine plan improve editor layers and undo")
        assert "editor behavior" in result
        result=gh._github_command(OWNER,"@GitHub engine plan update engine runtime physics")
        assert "engine core / renderer" in result


def test_explicit_scene_proposal_then_one_real_copy_not_game_mode():
    SAVED.clear();WRITES.clear()
    p=patches()
    with p[0],p[1],p[2],p[3],p[4],p[5]:
        proposed=gh._github_command(OWNER,"@GitHub engine clone sheep-tag-meadow as my-meadow on feature/work")
        assert "NOTHING WRITTEN" in proposed and "NOT registered" in proposed and not WRITES
        code=re.search(r"@GitHub confirm ([\w-]+)", proposed).group(1)
        done=gh._github_command(OWNER,"@GitHub confirm "+code)
        assert "confirmed" in done and "NOT" in done and len(WRITES)==1
        method,url,body=WRITES[0]
        assert method=="PUT" and url.endswith("/my-meadow.swyrl.json")
        assert body["branch"]=="feature/work" and "sha" not in body
        made=json.loads(__import__("base64").b64decode(body["content"]))
        assert made["project"]["canonicalId"]=="my-meadow"
        assert made["project"]["template"]=="sheep-tag-meadow"
        assert made["scene"]["actors"]==SCENE["scene"]["actors"]
        assert "already used" in gh._github_command(OWNER,"@GitHub confirm "+code)
        assert len(WRITES)==1


def test_source_stale_and_bad_or_protected_paths_fail_closed():
    SAVED.clear(); WRITES.clear()
    p=patches()
    with p[0],p[1],p[2],p[3],p[4],p[5]:
        bad=gh._github_command(OWNER,"@GitHub engine clone sheep-tag-meadow as sheep-tag-meadow on feature/work")
        assert "No write proposed" in bad and not SAVED
        no_template=gh._github_command(OWNER,"@GitHub engine clone invented-pack as my-meadow on feature/work")
        assert "supported distinct seed" in no_template
        for invalid in ("main","runtime","release/bad","feature/../secret"):
            try:
                engine._draft(gh,{},REC,OWNER,REPO,"sheep-tag-meadow","my-meadow",invalid)
            except HTTPException: pass
            else: raise AssertionError("Unsafe branch "+invalid)
        result=engine._confirm_draft(gh,REC,REPO,{
            "source":"sheep-tag-meadow","slug":"my-meadow","branch":"feature/work",
            "branchSha":"9"*40,"mainSha":SHA_MAIN,"sourceBlob":SHA_SOURCE
        })
        assert "moved" in result and not WRITES


def test_draft_engine_pr_scoped_and_confirmed_not_merged():
    SAVED.clear(); WRITES.clear()
    p=patches()
    with p[0],p[1],p[2],p[3],p[4],p[5]:
        proposed=gh._github_command(OWNER,"@GitHub engine review feature/work")
        assert "NOT CREATED" in proposed and not WRITES
        code=re.search(r"@GitHub confirm ([\w-]+)", proposed).group(1)
        done=gh._github_command(OWNER,"@GitHub confirm "+code)
        assert "DRAFT" in done and "NOT merged" in done and len(WRITES)==1
        assert WRITES[0][2]["draft"] is True


def test_confirmation_foreign_user_never_writes():
    SAVED.clear();WRITES.clear()
    proposed={"kind":"engine-scene-draft","owner":"google:other","repo":REPO,
              "source":"sheep-tag-meadow","slug":"my-meadow"}
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=REC), \
         mock.patch.object(gh,"_redis",return_value=json.dumps(proposed)), \
         mock.patch.object(workflows,"_write_request",side_effect=AssertionError("Forbidden write")):
        result=gh._github_command(OWNER,"@GitHub confirm Abcdefghijk1")
        assert "ownership mismatch" in result


def test_station_keeps_model_tools_and_reliability_contract():
    root=Path(__file__).parent
    station=(root/"station.py").read_text()
    assert station.count("forge_project_tools_v213.is_conversation(prompt)")>=3
    gh_code=(root/"github_connection.py").read_text()
    assert "forge_project_tools_v213.confirm(" in gh_code
    assert "forge_project_tools_v213.events(" in gh_code
    assert "engine status" in gh._AGENT_TOOLS and "engine starters" in gh._AGENT_TOOLS
    assert "DEPLOY_REQUEST.json" not in str(engine._SOURCE_STARTERS)


if __name__=="__main__":
    test_engine_entry_and_project_separation()
    test_source_mapping_and_realistic_mission_plan()
    test_explicit_scene_proposal_then_one_real_copy_not_game_mode()
    test_source_stale_and_bad_or_protected_paths_fail_closed()
    test_draft_engine_pr_scoped_and_confirmed_not_merged()
    test_confirmation_foreign_user_never_writes()
    test_station_keeps_model_tools_and_reliability_contract()
    print("v213 §E GitHub engine project/starter tools and approvals passed")
