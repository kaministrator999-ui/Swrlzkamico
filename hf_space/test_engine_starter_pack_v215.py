"""v215 §E atomic draft pack, source identity and GitHub confirmation regressions."""
import hashlib
import json
import re
import sys
from pathlib import Path
from unittest import mock

from fastapi import HTTPException
sys.path.insert(0, str(Path(__file__).parent))
import github_connection as gh
import forge_project_tools_v213 as engine
import engine_starter_pack_v215 as pack
import github_workflows_v212 as wf

USER="google:verified-user"
REPO=engine.ENGINE_REPO
REC={"token":"never-show-token", "repo":REPO, "scopes":"read:user public_repo"}
MAIN="a"*40
BRANCH="b"*40
SEED_BLOB="c"*40
MANIFEST_BLOB="d"*40
TREE="e"*40
SCENE={"engine":"§wyrl§ Engine · Maker v10.0", "version":10,
       "project":{"name":"Moonbell Meadow","canonicalId":"sheep-tag-meadow","template":"sheep-tag-meadow",
                  "kind":"sheep-tag","sheepTag":{"duration":1200,"headstart":30}},
       "editor":{"layers":[{"id":"layer-one","name":"Meadow"}]},
       "scene":{"actors":[{"id":"sheep-one","type":"st-sheep","editorLayerIds":["layer-one"]}]}}
MANIFEST={"schema":"swrlz-forge-source-v2","name":"§wyrl§ Engine v10.0",
          "patches":["patches/v1_%02d.py"%i for i in range(60)]}
CODES={}


def fake_api(token,path):
    assert token==REC["token"]
    if path=="/repos/"+REPO:
        return {"full_name":REPO,"private":False,"default_branch":"main",
                "permissions":{"pull":True,"push":True,"admin":True}}
    if path.startswith("/repos/"+REPO+"/git/ref/heads/"):
        return {"object":{"sha":MAIN if path.endswith("/main") else BRANCH}}
    if path=="/repos/"+REPO+"/git/commits/"+BRANCH:
        return {"tree":{"sha":TREE}}
    if path.startswith("/repos/"+REPO+"/contents/"):
        raise HTTPException(404,"no target file yet")
    raise AssertionError("unexpected REST path "+path)


def fake_text(token,repo,path,ref,max_bytes=500000):
    assert token==REC["token"] and repo==REPO
    if path==engine.SOURCE and ref=="main":
        return {"sha":MANIFEST_BLOB,"body":json.dumps(MANIFEST)}
    if path==engine.SCENES+"/sheep-tag-meadow.swyrl.json" and ref=="main":
        return {"sha":SEED_BLOB,"body":json.dumps(SCENE)}
    raise AssertionError("unexpected source "+path+" @"+str(ref))


def redis(_c,cmd,key,*rest):
    if cmd=="SET":
        assert key not in CODES
        CODES[key]=rest[0]
        return "OK"
    if cmd=="GETDEL":
        return CODES.pop(key,None)
    raise AssertionError("Unexpected Redis "+cmd)


def source_patches():
    return (mock.patch.object(gh,"_config",return_value={}),
            mock.patch.object(gh,"_load",return_value=REC),
            mock.patch.object(gh,"_api",side_effect=fake_api),
            mock.patch.object(gh,"_text",side_effect=fake_text),
            mock.patch.object(gh,"_redis",side_effect=redis))


def test_native_scene_and_pack_schema_validation():
    files,desc=pack._build_pack("sheep-tag-meadow","dawn-meadow",SCENE,MANIFEST,
                                SEED_BLOB,MANIFEST_BLOB,MAIN)
    assert len(files)==2
    assert files[0][0].endswith("dawn-meadow.swyrl.json")
    assert files[1][0].endswith("dawn-meadow.starter.json")
    scene=json.loads(files[0][1])
    assert scene["project"]["canonicalId"]=="dawn-meadow"
    assert scene["project"]["template"]=="sheep-tag-meadow"
    assert scene["project"]["kind"]=="sheep-tag"
    assert scene["scene"]["actors"]==SCENE["scene"]["actors"]
    assert desc["status"]=="draft-unregistered"
    assert desc["source"]["seedBlob"]==SEED_BLOB
    assert desc["scene"]["sha256"]==hashlib.sha256(files[0][1].encode()).hexdigest()
    assert desc["requires"] and "Projects registration" in desc["requires"]
    for mutant in ({**SCENE,"scene":{"actors":[{"id":"dup","editorLayerIds":["absent"]}]}},
                   {**SCENE,"editor":{"layers":[{"id":"x"},{"id":"x"}]}}):
        try:
            pack._validate_scene(mutant)
            raise AssertionError("Bad project accepted")
        except HTTPException: pass


def test_second_confirmation_atomic_two_files_and_one_branch_update():
    CODES.clear()
    posts=[];refupdates=[]
    def post(_rec,_repo,route,body):
        posts.append((route,body))
        if route=="trees":
            assert body["base_tree"]==TREE
            assert len(body["tree"])==2
            assert all(item["path"].startswith(engine.ROOT+"/") for item in body["tree"])
            return {"sha":"1"*40}
        if route=="commits":
            assert body["tree"]=="1"*40 and body["parents"]==[BRANCH]
            return {"sha":"2"*40}
        raise AssertionError("unexpected Git write")
    def update(*args):
        refupdates.append(args)
        return True
    p=source_patches()
    with p[0],p[1],p[2],p[3],p[4], \
         mock.patch.object(pack,"_git_post",side_effect=post), \
         mock.patch.object(pack,"_git_ref_update",side_effect=update):
        proposal=gh._github_command(USER,"@GitHub engine pack sheep-tag-meadow as dawn-meadow on feature/dawn")
        assert "NOTHING WRITTEN" in proposal and not posts and not refupdates
        assert "two" in proposal.lower() and "unregistered" in proposal.lower()
        code=re.search(r"@GitHub confirm ([\w-]+)",proposal).group(1)
        result=gh._github_command(USER,"@GitHub confirm "+code)
        assert "one atomic two-file" in result and "NOT registered" in result
        assert len(posts)==2 and len(refupdates)==1
        assert refupdates[0][2]=="feature/dawn" and refupdates[0][3]=="2"*40
        assert "already used" in gh._github_command(USER,"@GitHub confirm "+code)
        assert len(posts)==2


def test_stale_source_and_unknown_repo_fail_closed():
    CODES.clear()
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value={"token":"t","repo":"other/repo"}):
        try:
            gh._github_command(USER,"@GitHub engine pack help")
            raise AssertionError("Wrong repo unexpectedly accepted")
        except HTTPException as exc:
            assert exc.status_code==409
    with mock.patch.object(gh,"_api",side_effect=fake_api), \
         mock.patch.object(gh,"_text",side_effect=fake_text), \
         mock.patch.object(pack,"_git_post",side_effect=AssertionError("No Git write")):
        result=pack._confirm(gh,REC,REPO,{"seed":"sheep-tag-meadow","dest":"dawn-meadow",
                    "branch":"feature/dawn","headSha":"f"*40,"mainSha":MAIN,
                    "sourceBlob":SEED_BLOB,"manifestBlob":MANIFEST_BLOB})
        assert "branch changed" in result.lower()
    assert not pack.is_command("@GitHub engine deploy v10.0")
    assert pack.is_command("@GitHub engine pack verify dawn-meadow on feature/dawn")


def test_readback_digest_verifies_actual_github_files():
    scene_files,meta=pack._build_pack("sheep-tag-meadow","dawn-meadow",SCENE,MANIFEST,SEED_BLOB,MANIFEST_BLOB,MAIN)
    source={scene_files[0][0]:{"sha":"3"*40,"body":scene_files[0][1]},
            scene_files[1][0]:{"sha":"4"*40,"body":scene_files[1][1]}}
    with mock.patch.object(gh,"_api",side_effect=fake_api), \
         mock.patch.object(gh,"_read_optional",side_effect=lambda tok,repo,path,ref,max_bytes:source[path]):
        report=pack._verify(gh,REC,REPO,"dawn-meadow","feature/dawn")
        assert "data only" in report and "digest checks PASS" in report
        assert "SHA-256" in report and "does NOT verify editor registration" in report
        changed=json.loads(source[scene_files[1][0]]["body"])
        changed["scene"]["sha256"]="0"*64
        source[scene_files[1][0]]["body"]=json.dumps(changed)
        try:
            pack._verify(gh,REC,REPO,"dawn-meadow","feature/dawn")
            raise AssertionError("Altered content accepted")
        except HTTPException:pass


def test_station_and_git_owner_constraints():
    root=Path(__file__).parent
    text=(root/"github_connection.py").read_text()
    assert "engine_starter_pack_v215.confirm(" in text
    assert "engine_starter_pack_v215.events(" in text
    assert "engine_starter_pack_v215.is_command(prompt)" in text
    chat=(root.parent/"chat/§wyrlz/index.html").read_text()
    assert 'id="githubStarterPackGuide"' in chat
    assert 'prompt.value="@GitHub engine pack help"' in chat
    assert "force" in __import__("inspect").getsource(pack._git_ref_update)
    assert '"force": False' in __import__("inspect").getsource(pack._git_ref_update)
    assert "DEPLOY_REQUEST" not in str(pack._build_pack("sheep-tag-meadow","dawn-meadow",SCENE,MANIFEST,SEED_BLOB,MANIFEST_BLOB,MAIN)[0])
    assert "http" not in str(pack._TEMPLATES) if hasattr(pack,"_TEMPLATES") else True


if __name__=="__main__":
    test_native_scene_and_pack_schema_validation()
    test_second_confirmation_atomic_two_files_and_one_branch_update()
    test_stale_source_and_unknown_repo_fail_closed()
    test_readback_digest_verifies_actual_github_files()
    test_station_and_git_owner_constraints()
    print("v215 §E atomic pack GitHub tool tests passed")
