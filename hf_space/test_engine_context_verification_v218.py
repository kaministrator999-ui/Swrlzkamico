"""v218 exact-source context relevance and truthful engine branch checks."""
import json
import sys
from pathlib import Path
from unittest import mock
from fastapi import HTTPException

sys.path.insert(0,str(Path(__file__).parent))
import engine_code_agent_v217 as agent
import forge_project_tools_v213 as engine

SHA_MAIN="a"*40
SHA_HEAD="b"*40
PREFIX="projects/swrlz-forge-moba/"
PATH=PREFIX+"runtime/anime_timeline.js"


def test_late_source_focus_and_exact_segments():
    intro="import {Player} from './game.js';\n"
    repeated=("function idle(){ return 1; }\n"*530)
    needle="function seekTimelineFrame(time){ updateTimelineScrub(time); return time; }\n"
    body=intro+repeated+needle+("function outro(){ return 0; }\n"*200)
    assert body.index(needle)>5400
    context=agent._code_context(body,"Fix Timeline Scrub seekTimelineFrame behavior",9500)
    assert needle in context, "Must retrieve relevant code beyond the first 5,400 characters"
    assert "import {Player}" in context
    assert "[excerpted; unseen source is NOT verified]" in context
    assert len(context)<13500, "Context cannot expand to full 20,000-character file"
    assert context.count(needle)==1
    terms=agent._goal_terms("Improve seekTimelineFrame and pausedTimeline")
    assert "seek" in terms and "timeline" in terms and "paused" in terms
    small="const edit = () => 1;\n"
    assert small in agent._code_context(small,"edit",9500)


def test_model_receives_relevant_source_and_proposes_exact_patch():
    intro="const boot=1;\n"
    body=intro+("const unrelated=1;\n"*450)+"function timelineScrub(){ return 'oldTime'; }\n"
    old="function timelineScrub(){ return 'oldTime'; }"
    new="function timelineScrub(){ return 'newTime'; }"
    assert body.index(old)>5400
    def model(payload):
        prompt=payload["prompt"]
        assert old in prompt, "The source model must receive the relevant late section"
        assert "history" in payload and payload["history"]==[]
        assert "private-test-token" not in prompt
        proposed=json.dumps({"edits":[{"path":PATH,"old":old,"new":new}]})
        yield {"type":"STATUS","phase":"GENERATING"}
        yield {"type":"DELTA","text":proposed}
        yield {"type":"COMPLETED"}
    events=list(agent._model_events(model,"Fix timelineScrub playback", [PATH],{PATH:body}))
    edits=next(e["edits"] for e in events if e["type"]=="MODEL_RESULT")
    assert edits is not None and edits[PATH]["old"]==old
    assert edits[PATH]["new"]==new


def test_verified_green_does_not_claim_engine_release():
    def api(_gh,_rec,_repo,suffix):
        if suffix.startswith("/compare/"):
            return {"status":"ahead","files":[
                {"filename":PREFIX+"runtime/anime_timeline.js"},
                {"filename":PREFIX+"patches/v10_1_example.py"}]}
        if suffix=="/commits/"+SHA_HEAD+"/check-runs?per_page=100":
            return {"check_runs":[{"name":"engine-syntax","status":"completed","conclusion":"success"},
                                  {"name":"unit-suite","status":"completed","conclusion":"success"}]}
        raise AssertionError("Unexpected GitHub API "+suffix)
    with mock.patch.object(agent.engine,"_access",return_value={"allowed":True}), \
         mock.patch.object(agent.engine,"_branch_head",return_value=("feature/review",SHA_HEAD)), \
         mock.patch.object(agent.approvals,"_branch_sha",return_value=SHA_MAIN), \
         mock.patch.object(agent.engine,"_github",side_effect=api):
        report=agent._verification(object(),{"token":"private-test-token"},engine.ENGINE_REPO,"feature/review")
    assert "engine-syntax: completed / success" in report
    assert "CI checks observed green ONLY" in report
    assert "hosted engine/gameplay unverified" in report
    assert "manifest patch ordering" in report
    assert "HEAD" not in report or SHA_HEAD in report


def test_pending_or_no_checks_not_green():
    for checks in ([],[{"name":"syntax","status":"in_progress","conclusion":None}],
                   [{"name":"syntax","status":"completed","conclusion":"failure"}]):
        def api(_gh,_rec,_repo,suffix):
            if suffix.startswith("/compare/"):
                return {"status":"ahead","files":[{"filename":PREFIX+"runtime/anime_timeline.js"}]}
            if suffix.startswith("/commits/"):
                return {"check_runs":checks}
            raise AssertionError(suffix)
        with mock.patch.object(agent.engine,"_access",return_value={"allowed":True}), \
             mock.patch.object(agent.engine,"_branch_head",return_value=("feature/review",SHA_HEAD)), \
             mock.patch.object(agent.approvals,"_branch_sha",return_value=SHA_MAIN), \
             mock.patch.object(agent.engine,"_github",side_effect=api):
            report=agent._verification(object(),{"token":"t"},engine.ENGINE_REPO,"feature/review")
        assert "NOT VERIFIED PASSING" in report
        assert "CI checks observed green ONLY" not in report


def test_commands_and_protection():
    assert agent.is_command("@GitHub engine code context "+PATH+" :: Fix Timeline Scrub")
    assert agent.is_command("@GitHub engine code verify feature/review")
    assert not agent.is_command("Could you delete my entire engine?")
    assert agent.VERIFY.fullmatch("engine code verify main") is None
    try:
        agent._path(".deploy/HF_SPACE_REQUEST.txt")
    except HTTPException:
        pass
    else:
        raise AssertionError("Protected path accepted")
    for invalid in ("", 123):
        try:
            agent._code_context(invalid,"code",9500)
        except HTTPException:
            pass
        else:
            raise AssertionError("Invalid context accepted")


if __name__=="__main__":
    test_late_source_focus_and_exact_segments()
    test_model_receives_relevant_source_and_proposes_exact_patch()
    test_verified_green_does_not_claim_engine_release()
    test_pending_or_no_checks_not_green()
    test_commands_and_protection()
    print("v218 engine source context and branch CI truth checks passed")
