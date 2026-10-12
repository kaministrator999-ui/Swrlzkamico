"""v217 real-source local-model edit proposals and one-use atomic §E GitHub writes."""
import hashlib
import json
import sys
from pathlib import Path
from unittest import mock
from fastapi import HTTPException
sys.path.insert(0,str(Path(__file__).parent))
import engine_code_agent_v217 as agent
import github_connection as gh
import forge_project_tools_v213 as engine

OWNER="google:owner"
REPO=engine.ENGINE_REPO
RECORD={"token":"test-only-opaque-token","repo":REPO,"scopes":"read:user public_repo"}
PY=engine.ROOT+"/patches/v10_0_sheep_tag.py"
JS=engine.ROOT+"/runtime/anime_timeline.js"
MAIN="a"*40
HEAD="b"*40
BLOB="c"*40
MANIFEST="d"*40
SOURCE="def apply(html):\n    value = 'starter-old'\n    return html.replace('starter-old', value)\n"
SOURCE_JS="export function timeline(){return 'starter-old';}\n"
NEW="def apply(html):\n    value = 'starter-new'\n    return html.replace('starter-old', value)\n"


def model_for(path,old,new):
    def generate(data):
        assert data["history"]==[] and "opaque-token" not in str(data)
        assert path in data["prompt"] and "starter-old" in data["prompt"]
        yield {"type":"STATUS","phase":"LOADING"}
        yield {"type":"STATUS","phase":"GENERATING"}
        raw=json.dumps({"edits":[{"path":path,"old":old,"new":new}]})
        yield {"type":"DELTA","text":raw[:30]}
        yield {"type":"DELTA","text":raw[30:]}
        yield {"type":"COMPLETED"}
    return generate


def fake_doc(token,repo,path,ref,max_bytes=0):
    assert token==RECORD["token"] and repo==REPO
    if path==PY:
        return {"sha":BLOB,"body":SOURCE}
    if path==JS:
        return {"sha":BLOB,"body":SOURCE_JS}
    raise AssertionError("unexpected source read: "+path)


def fake_manifest(_gh,_rec,_repo):
    return {"sha":MANIFEST,"body":"{}"},{"patches":["patches/test.py"]*60}


def prepared():
    changes=[]
    def store(_gh,_cfg,user,repo,item):
        assert user==OWNER and repo==REPO and item["kind"]=="engine-code-patch"
        changes.append(item)
        return "exampleCODE0123"
    return changes,store


def test_safe_file_paths_and_language_validation():
    assert agent._path(PY)==PY
    assert agent._path(JS)==JS
    assert agent._path(engine.ROOT+"/build_space.py")
    for wrong in ("main",engine.ROOT+"/source-manifest.json",
                  engine.ROOT+"/DEPLOY_REQUEST.json",
                  engine.ROOT+"/runtime/../secret.js",
                  engine.ROOT+"/runtime/.env",
                  engine.ROOT+"/patches/new.js",
                  "hf_space/station.py"):
        try:agent._path(wrong)
        except HTTPException:pass
        else:raise AssertionError("unsafe file edit allowed: "+wrong)
    try:agent._paths(JS+","+JS)
    except HTTPException:pass
    else:raise AssertionError("duplicate paths")
    agent._validate(PY,NEW)
    for invalid in ("def apply(html):\n  return (", "def renamed(html):\n return html\n"):
        try:agent._validate(PY,invalid)
        except HTTPException:pass
        else:raise AssertionError("broken patch applied")


def test_model_only_proposes_without_mutation_and_shows_exact_diff():
    edits=[{"path":PY,"old":SOURCE,"new":NEW}]
    generated=model_for(PY,SOURCE,NEW)
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(agent.engine,"_access",return_value={"allowed":True}), \
         mock.patch.object(agent.engine,"_branch_head",return_value=("feature/editor-work",HEAD)), \
         mock.patch.object(agent.approvals,"_branch_sha",return_value=MAIN), \
         mock.patch.object(agent.engine,"_manifest",side_effect=fake_manifest), \
         mock.patch.object(gh,"_text",side_effect=fake_doc), \
         mock.patch.object(agent.approvals,"_store",return_value="exampleCODE0123"), \
         mock.patch.object(agent.packs,"_git_post",side_effect=AssertionError("No GitHub writes during planning")):
        events=list(agent.events(gh,{"userId":OWNER,
            "prompt":"@GitHub engine code propose "+PY+" on feature/editor-work :: Make a small safe replacement to the starter text"},generated))
    phases=[x.get("phase") for x in events if x.get("type")=="STATUS"]
    assert "ENGINE_CODE_ACCESS" in phases and "ENGINE_CODE_MODEL_LOADING" in phases
    assert "ENGINE_CODE_DIFF_READY" in phases
    body="".join(x.get("text","") for x in events)
    assert "NOTHING WRITTEN" in body and "exampleCODE0123" in body
    assert "-    value = 'starter-old'" in body
    assert "+    value = 'starter-new'" in body
    assert "opaque-token" not in body


def test_bad_model_output_fails_closed():
    def malicious(_data):
        yield {"type":"DELTA","text":json.dumps({"edits":[{"path":JS,"old":"starter-old","new":"BAD"}]})}
        yield {"type":"COMPLETED"}
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(agent.engine,"_access",return_value={}), \
         mock.patch.object(agent.engine,"_branch_head",return_value=("feature/editor-work",HEAD)), \
         mock.patch.object(agent.approvals,"_branch_sha",return_value=MAIN), \
         mock.patch.object(agent.engine,"_manifest",side_effect=fake_manifest), \
         mock.patch.object(gh,"_text",side_effect=fake_doc), \
         mock.patch.object(agent.approvals,"_store",side_effect=AssertionError("No invalid proposal")):
        events=list(agent.events(gh,{"userId":OWNER,
            "prompt":"@GitHub engine code propose "+PY+" on feature/editor-work :: Replace source safely without inventing paths"},malicious))
    text="".join(x.get("text","") for x in events)
    assert "No commit" in text and "CODE" not in text
    assert not any(e.get("phase")=="ENGINE_CODE_DIFF_READY" for e in events)


def test_atomic_confirmation_enforces_current_sha_and_source_hash():
    updated=SOURCE.replace(SOURCE,NEW,1)
    proposal={"kind":"engine-code-patch","branch":"feature/editor-work","headSha":HEAD,
              "mainSha":MAIN,"manifestSha":MANIFEST,"edits":[{
                  "path":PY,"blob":BLOB,"old":SOURCE,"new":NEW,
                  "resultHash":hashlib.sha256(updated.encode()).hexdigest()}]}
    with mock.patch.object(agent.engine,"_access",return_value={}), \
         mock.patch.object(agent.engine,"_branch_head",return_value=("feature/editor-work",HEAD)), \
         mock.patch.object(agent.approvals,"_branch_sha",return_value=MAIN), \
         mock.patch.object(agent.engine,"_manifest",side_effect=fake_manifest), \
         mock.patch.object(gh,"_text",side_effect=fake_doc), \
         mock.patch.object(agent.engine,"_github",return_value={"tree":{"sha":"e"*40}}), \
         mock.patch.object(agent.packs,"_git_post",side_effect=[{"sha":"f"*40},{"sha":"1"*40}]) as post, \
         mock.patch.object(agent.packs,"_git_ref_update",return_value=True) as update:
        answer=agent.confirm(gh,{},RECORD,OWNER,REPO,proposal)
        assert "confirmed one atomic" in answer
        assert post.call_count==2 and update.call_count==1
        staged=post.call_args_list[0].args[3]
        assert len(staged["tree"])==1 and staged["tree"][0]["content"]==NEW
    proposal["headSha"]="3"*40
    with mock.patch.object(agent.engine,"_access",return_value={}), \
         mock.patch.object(agent.engine,"_branch_head",return_value=("feature/editor-work",HEAD)), \
         mock.patch.object(agent.approvals,"_branch_sha",return_value=MAIN), \
         mock.patch.object(agent.engine,"_manifest",side_effect=fake_manifest), \
         mock.patch.object(agent.packs,"_git_post",side_effect=AssertionError("No stale writes")):
        answer=agent.confirm(gh,{},RECORD,OWNER,REPO,proposal)
        assert "changed" in answer and "No commit" in answer


def test_routing_and_engine_release_boundary():
    conn=Path(gh.__file__).read_text()
    assert agent.is_command("@GitHub engine code help")
    assert agent.is_command("@GitHub engine code propose "+JS+" on feature/test :: Improve drawing")
    assert not agent.is_command("@GitHub engine pack verify my-meadow on feature/test")
    assert "engine_code_agent_v217.events(" in conn
    assert 'kind == "engine-code-patch"' in conn
    assert "engine_code_agent_v217.confirm(" in conn
    assert "DEPLOY_REQUEST.json" not in str(agent._paths(JS))
    assert "git_ref_update" in Path(agent.__file__).read_text()
    assert "force" not in agent._diff({PY:SOURCE},{PY:{"old":SOURCE,"new":NEW}})


if __name__=="__main__":
    test_safe_file_paths_and_language_validation()
    test_model_only_proposes_without_mutation_and_shows_exact_diff()
    test_bad_model_output_fails_closed()
    test_atomic_confirmation_enforces_current_sha_and_source_hash()
    test_routing_and_engine_release_boundary()
    print("v217 model-to-GitHub engine code proposal safety tests passed")
