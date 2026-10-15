"""v247: Dragon Chat (56) GitHub file-view utterances never fabricate code.

Only mock/in-process classification and Stage-1 dispatch; no credentials,
repository mutation, model load or network access.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parent))
import github_connection as github
import github_read_inference_v235 as reads
import brain_programming as brain

READS = (
    "Can I see the files in the repo",
    "Can I see the files in the repo?",
    "Could you show me the files in our GitHub repository?",
    "Please show the files in my repo",
    "Can you browse the files in the repo",
)
NEGATIVE = (
    "Write Python code to list repo files",
    "Create a program to enumerate files in the repo",
    "Delete all the files in our repository",
)

def test_exported_prompt_selects_real_authenticated_read():
    for prompt in READS:
        expected="@GitHub files"
        assert reads.classify_read(prompt)==expected, (prompt,reads.classify_read(prompt))
        assert github.is_github_conversation(prompt), "Station must route GitHub before the 700M/coder model"
        assert not brain.programming_intent(prompt,[],[])["codingTask"], "view is not code creation"
        # Even previously active coding work cannot turn a specific repo-view
        # request into an unrelated artifact mutation.
        prior={"intentContract":{"originalRequest":"Write a program"}}
        assert not brain.programming_intent(prompt,[],[],prior)["codingTask"]
        observed=[]
        def fake_read(data):
            observed.append(data["prompt"])
            yield {"type":"DELTA","text":"## GitHub directory: /\n- dir .github\n- file README.md"}
            yield {"type":"COMPLETED","phase":"COMPLETE"}
        with mock.patch.object(github,"command_events",side_effect=fake_read),\
             mock.patch.object(github,"_post_github",side_effect=AssertionError("write not allowed")):
            events=list(github.agent_events({
                "userId":"google:owner","prompt":prompt,
                "githubContext":{"repo":"owner/repo","branch":"main",
                                 "sourceSha":"a"*40}
            }))
        assert observed==[expected],(prompt,observed)
        assert any(e.get("phase")=="GITHUB_READ_EVIDENCE" for e in events)
        assert any("GitHub directory" in e.get("text","") for e in events)
        assert not any(e.get("phase")=="CODER_AUTO_ROUTE" for e in events)

def test_guard_preserves_real_programming_and_permission_limits():
    for prompt in NEGATIVE:
        assert reads.classify_read(prompt) is None, prompt
    assert brain.programming_intent("Write Python code to list repo files",[],[])["codingTask"]
    assert brain.programming_intent("Create a program to enumerate files in the repo",[],[])["codingTask"]
    assert reads.classify_read("Can I see the files?") is None, "No implicit repo access without explicit scope"
    assert not github.is_github_conversation("Can I see the files?")
    assert github.GITHUB_CAPABILITY_STAGE=="read-repository"

if __name__=="__main__":
    test_exported_prompt_selects_real_authenticated_read()
    test_guard_preserves_real_programming_and_permission_limits()
    print("v247: repo-files view routes authenticated GitHub read; coder/write guard PASSED")
