"""v240 risk-asymmetric chat/model intent and authorization boundary regression.

No production account data, real tools or external writes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from intent_risk_v240 import classify, clarification, MODEL_POLICY
from response_cognition import response_cognition_policy, classify_response_cognition
from model_router import dispatch
import github_connection as gh


def _disallowed(*args, **kwargs):
    raise AssertionError("No model, search or external side effect should execute")


def test_topic_introductions_are_not_actions():
    for word in ("Files", "files?", "Music", "Statistics", "Code", "Projects", "Memories"):
        assert classify(word) == "topic", word
        assert clarification(word) is None
    # Read interpretations must remain reversible and explicit reads still route.
    for query in ("List the Python files", "What are the repo statistics?",
                  "Read README.md", "Explain the source relationship",
                  "Write a song", "Write Python sample code", "Edit this poem for tone"):
        assert classify(query) == "ordinary", query
        assert clarification(query) is None


def test_ambiguous_mutations_require_scope():
    for query in ("Delete it", "Remove those", "Deploy", "Publish that",
                  "Send it", "Transfer it", "Commit changes", "Edit the file",
                  "Rename it", "Run", "Could you delete that?"):
        assert classify(query) == "unclear-mutation", query
        text = clarification(query)
        assert text and "?" in text and "won't" in text, query
    for query in ("Don't delete it", "What would happen if we deploy?",
                  "Delete README.md in repository demo", "Deploy service X to stage Y",
                  "Explain how to delete a file", "Send a draft email to Bob as an example"):
        assert classify(query) == "ordinary", query
        assert clarification(query) is None


def test_all_model_routes_clarify_before_generating_or_search():
    for model in ("700m", "coder", "stock", "r39"):
        payload = {"prompt": "Delete it", "history": [],
                   "pinnedContext": [{"artifactId": "pinned-artifact",
                                      "text": "sensitive content"}]}
        events = list(dispatch(model, payload, _disallowed, _disallowed,
                               _disallowed, _disallowed))
        assert any(x.get("phase") == "MUTATION_CLARIFICATION" for x in events), model
        assert any(x.get("fastPath") == "mutation-clarification" for x in events), model
        assert any("won't" in x.get("text", "") for x in events), model


def test_model_policy_includes_strict_writes_and_flexible_reads():
    state = classify_response_cognition("Files", [], {})
    policy = response_cognition_policy(state)
    for clause in ("Read-only interpretations are revisable",
                   "Pinned workspaces", "require a clear operation",
                   "Writing creative text"):
        assert clause in policy, clause
    assert MODEL_POLICY in policy


def test_github_stage_one_remains_locked_and_ambiguity_resolves_without_tools():
    ctx = {"repo": "owner/demo", "branch": "fix/example",
           "sourceSha": "a"*40, "directory": "hf_space",
           "lastFile": "hf_space/github_connection.py"}
    assert "Did you want" in gh.ambiguous_topic_reply("Files", ctx)
    assert gh._implicit_repo_command("Files", ctx) is None
    assert gh._implicit_repo_command("List files in this folder", ctx) == (
        "@GitHub files hf_space on branch fix/example")
    for command in ("@GitHub create branch fix/write from main",
                    "@GitHub delete file README.md",
                    "@GitHub confirm abcd1234"):
        assert gh._stage_blocks(command)
    # A specified target is NOT equivalent to a write grant.
    assert gh._stage_blocks("@GitHub edit file README.md")
    assert not gh._read_stage_command("@GitHub edit file README.md")


if __name__ == "__main__":
    test_topic_introductions_are_not_actions()
    test_ambiguous_mutations_require_scope()
    test_all_model_routes_clarify_before_generating_or_search()
    test_model_policy_includes_strict_writes_and_flexible_reads()
    test_github_stage_one_remains_locked_and_ambiguity_resolves_without_tools()
    print("v240 risk-asymmetric intent / no-implicit-write regression PASS")
