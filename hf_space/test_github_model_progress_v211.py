"""v211 bounded GitHub model/tool live progress and authorization regressions."""
import sys
from pathlib import Path
from unittest import mock
from fastapi import HTTPException
sys.path.insert(0,str(Path(__file__).parent))
import github_connection as gh
# Historical mutation test cases use test-only capability mode.
gh.GITHUB_CAPABILITY_STAGE = "legacy-test-only"

REPO="owner/repo"
OWNER="google:verified-owner"
RECORD={"token":"secret-server-only", "repo":REPO, "scopes":"read:user"}

def _api(_token,path):
    if path=="/repos/"+REPO:
        return {"full_name":REPO,"default_branch":"main","private":False,
                "permissions":{"pull":True,"push":True,"triage":True}}
    if path=="/repos/"+REPO+"/issues?state=open&per_page=12":
        return [{"number":17,"title":"Known issue","html_url":"https://github.com/owner/repo/issues/17"}]
    if path=="/repos/"+REPO+"/pulls?state=open&per_page=12":
        return [{"number":19,"title":"Known PR","html_url":"https://github.com/owner/repo/pull/19"}]
    if path=="/repos/"+REPO+"/branches?per_page=30":
        return [{"name":"main","commit":{"sha":"a"*40}}]
    raise AssertionError("Unexpected GitHub API endpoint: "+path)


def test_natural_routing_and_no_false_github_actions():
    assert gh.is_github_conversation("Show my repo issues and pull requests")
    assert gh.is_github_conversation("@GitHub ask check the permission on my repo")
    assert gh.is_github_conversation("Can you check my GitHub permissions?")
    assert gh.is_github_conversation("Could you please show our repo commits?")
    assert not gh.is_github_conversation("What is GitHub?")
    assert not gh.is_github_conversation("Write a fantasy story about a repo")
    assert gh._agent_allowed_tool("issues","Show my repo issues") == "issues"
    assert gh._agent_allowed_tool("create issue", "show my repo issues") is None
    assert gh._agent_allowed_tool("read file settings.json","Read my repo settings.json") == "read file settings.json"
    assert gh._agent_allowed_tool("read file secrets.json","Read my repo README.md") is None
    assert gh._agent_allowed_tool("files ../secrets", "Show my repo ../secrets") is None


def test_real_model_plan_with_live_inference_tool_progress_and_no_mutation():
    seen_prompts=[]
    def local_model(data):
        seen_prompts.append(data)
        yield {"type":"STATUS","phase":"LOADING"}
        yield {"type":"STATUS","phase":"GENERATING"}
        yield {"type":"DELTA","text":'{"tools":["issues",'}
        yield {"type":"DELTA","text":'"pulls"]}'}
        yield {"type":"COMPLETED"}
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(gh,"_api",side_effect=_api), \
         mock.patch.object(gh,"_post_github",side_effect=AssertionError("Write forbidden")), \
         mock.patch.object(gh,"_redis",side_effect=AssertionError("No proposal storage")):
        events=list(gh.agent_events({"userId":OWNER,"prompt":"Show my repo issues and pull requests"},local_model))
    phases=[e.get("phase") for e in events if e.get("type")=="STATUS"]
    assert phases[:4]==["GITHUB_MODEL_PLAN_STARTED","GITHUB_MODEL_LOADING","GITHUB_MODEL_GENERATING","GITHUB_PLAN_READY"]
    assert phases.count("GITHUB_PERMISSION_CHECK")==2
    assert phases.count("GITHUB_PERMISSION_VERIFIED")==2
    assert phases.count("GITHUB_TOOL_STARTED")==2
    assert phases.count("GITHUB_TOOL_COMPLETE")==2
    assert phases[-1]=="GITHUB_EVIDENCE_COMPLETE"
    joined="".join(e.get("text","") for e in events if e.get("type")=="DELTA")
    assert "Known issue" in joined and "Known PR" in joined
    assert "secret-server-only" not in joined
    assert "model-planned" in next(e["reason"] for e in events if e.get("phase")=="GITHUB_PLAN_READY")
    assert seen_prompts and seen_prompts[0]["history"] == [] and seen_prompts[0]["userProfile"] == ""
    assert "secret-server-only" not in str(seen_prompts)


def test_invalid_or_unavailable_inference_degrades_to_bounded_read_tools():
    def malicious(_data):
        yield {"type":"DELTA","text":'{"tools":["delete-repo","issues"]}'}
        yield {"type":"COMPLETED"}
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(gh,"_api",side_effect=_api), \
         mock.patch.object(gh,"_post_github",side_effect=AssertionError("No mutation")):
        e=list(gh.agent_events({"userId":OWNER,"prompt":"Show my repo issues"},malicious))
    plan=next(x for x in e if x.get("phase")=="GITHUB_PLAN_READY")
    assert "safe deterministic fallback" in plan["reason"] and "issues" in plan["reason"]
    assert "Known issue" in "".join(x.get("text","") for x in e)
    assert not any("delete-repo" in str(x) for x in e)
    no_model=list(gh._agent_model_plan_events("issues",None))
    assert no_model[-1] == {"type":"PLAN_RESULT","plan":[]}


def test_write_request_does_not_run_model_or_mutation():
    with mock.patch.object(gh,"_config",side_effect=AssertionError("Should not need authorization")), \
         mock.patch.object(gh,"_post_github",side_effect=AssertionError("Write forbidden")):
        events=list(gh.agent_events({"userId":OWNER,
            "prompt":"@GitHub ask create an issue in my repo"}, lambda _: (_ for _ in ()).throw(AssertionError("No model"))))
    assert "No write attempted" in "".join(x.get("text","") for x in events)
    assert any(x.get("phase")=="GITHUB_APPROVAL_REQUIRED" for x in events)


def test_unknown_access_stops_without_inventing_permission_denial():
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(gh,"_api",side_effect=HTTPException(404,"Not found")):
        events=list(gh.agent_events({"userId":OWNER,"prompt":"@GitHub issues"}))
    assert any(x.get("phase")=="GITHUB_ACCESS_UNVERIFIED" for x in events)
    joined="".join(x.get("text","") for x in events)
    assert "could not be verified" in joined
    assert "must grant write" not in joined


def test_station_and_chat_wiring_static():
    root=Path(__file__).parent.parent
    station=(root/"hf_space/station.py").read_text()
    chat=(root/"chat/§wyrlz/index.html").read_text()
    assert "github_connection.agent_events(" in station
    assert "github_connection.is_github_conversation(prompt)" in station
    assert 'v211' not in chat or "GITHUB" in chat
    assert 'v210' not in str(gh._AGENT_TOOLS)
    assert "GITHUB_PLAN_READY" in chat



def test_stage1_issue_pr_read_plan_and_single_terminal_event():
    """Two model-selected reads must both complete while all writes stay locked."""
    def model(_payload):
        yield {"type":"DELTA","text":'{"tools":["issues","pulls"]}'}
        yield {"type":"COMPLETED"}
    with mock.patch.object(gh,"GITHUB_CAPABILITY_STAGE","read-repository"), \
         mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(gh,"_api",side_effect=_api), \
         mock.patch.object(gh,"_post_github",side_effect=AssertionError("Write forbidden")):
        events=list(gh.agent_events({"userId":OWNER,
            "prompt":"Show my repo issues and pull requests"},model))
    answer="".join(e.get("text","") for e in events if e.get("type")=="DELTA")
    assert "Known issue" in answer and "Known PR" in answer, answer
    assert len([e for e in events if e.get("type")=="COMPLETED"])==1
    assert any(e.get("phase")=="GITHUB_READ_PLAN_READY" for e in events)
    assert "validated model selection" in str(events)
    assert "secret-server-only" not in answer

def test_stage1_explicit_and_fallback_reads_without_planner():
    """An unambiguous read must not require model inference or new privileges."""
    def bad_model(_payload):
        raise AssertionError("Simple read should not launch a model")
    with mock.patch.object(gh,"GITHUB_CAPABILITY_STAGE","read-repository"), \
         mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(gh,"_api",side_effect=_api), \
         mock.patch.object(gh,"_post_github",side_effect=AssertionError("Write forbidden")):
        exact=list(gh.agent_events({"userId":OWNER,"prompt":"@GitHub issues"},bad_model))
        natural=list(gh.agent_events({"userId":OWNER,"prompt":"Show my repo issues"},bad_model))
    assert "Known issue" in str(exact)
    assert "Known issue" in str(natural)
    assert not any(e.get("phase")=="GITHUB_MODEL_PLAN_STARTED" for e in natural)

def test_stage1_model_cannot_select_mutation_or_unapproved_source():
    """Unsupported model output falls back only to the user's requested checks."""
    def malicious(_payload):
        yield {"type":"DELTA","text":'{"tools":["delete-repo","issues"]}'}
        yield {"type":"COMPLETED"}
    with mock.patch.object(gh,"GITHUB_CAPABILITY_STAGE","read-repository"), \
         mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(gh,"_api",side_effect=_api), \
         mock.patch.object(gh,"_post_github",side_effect=AssertionError("Write forbidden")):
        e=list(gh.agent_events({"userId":OWNER,
            "prompt":"Show my repo issues and pull requests"},malicious))
    assert "Known issue" in str(e) and "Known PR" in str(e)
    assert not any("delete-repo" in str(event) for event in e)
    assert "deterministic read fallback" in str(e)

def test_stage1_write_intent_never_reaches_read_model():
    def no_model(_payload):
        raise AssertionError("Model must not plan a write")
    with mock.patch.object(gh,"GITHUB_CAPABILITY_STAGE","read-repository"), \
         mock.patch.object(gh,"_post_github",side_effect=AssertionError("Write forbidden")):
        e=list(gh.agent_events({"userId":OWNER,
            "prompt":"@GitHub ask create an issue in our repo"},no_model))
    assert any(event.get("phase")=="GITHUB_STAGE_LOCKED" for event in e) or \
           any(event.get("phase")=="GITHUB_APPROVAL_REQUIRED" for event in e)
    assert "No write attempted" in str(e)

def test_model_selected_numeric_ids_are_exact_not_substrings():
    assert gh._agent_allowed_tool("pr review 17","Please review PR #17")=="pr review 17"
    assert gh._agent_allowed_tool("pr review 7","Please review PR #17") is None
    assert gh._agent_allowed_tool("issue inspect 17","Inspect issue 17")=="issue inspect 17"
    assert gh._agent_allowed_tool("issue inspect 7","Inspect issue 17") is None
    assert gh._agent_allowed_tool("issue inspect 17","Inspect issue 170") is None
    assert gh._agent_allowed_tool("pr review 17","Inspect issue 17") is None

if __name__=="__main__":
    test_natural_routing_and_no_false_github_actions()
    test_real_model_plan_with_live_inference_tool_progress_and_no_mutation()
    test_invalid_or_unavailable_inference_degrades_to_bounded_read_tools()
    test_write_request_does_not_run_model_or_mutation()
    test_unknown_access_stops_without_inventing_permission_denial()
    test_station_and_chat_wiring_static()
    test_stage1_issue_pr_read_plan_and_single_terminal_event()
    test_stage1_explicit_and_fallback_reads_without_planner()
    test_stage1_model_cannot_select_mutation_or_unapproved_source()
    test_stage1_write_intent_never_reaches_read_model()
    test_model_selected_numeric_ids_are_exact_not_substrings()
    print("v211 GitHub model-guided progress regressions passed")
