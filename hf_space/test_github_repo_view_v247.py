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
    "Can you display the files in the repo",  # Dragon Chat (57): bad coder route
    "Can you show me the files in the repo",  # Dragon Chat (57): false file lookup
    "Can you show me the files in the github",
    "Can you view the files in our repository",
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
        assert any(e.get("phase") in ("GITHUB_READ_EVIDENCE","GITHUB_READ_STAGE") for e in events), events
        assert any("GitHub directory" in e.get("text","") for e in events)
        assert not any(e.get("phase")=="CODER_AUTO_ROUTE" for e in events)

def test_guard_preserves_real_programming_and_permission_limits():
    for prompt in NEGATIVE:
        assert reads.classify_read(prompt) is None, prompt
    assert brain.programming_intent("Write Python code to list repo files",[],[])["codingTask"]
    assert brain.programming_intent("Create a program to enumerate files in the repo",[],[])["codingTask"]
    # Generic collection names are not concrete source filenames.
    assert github._natural_repo_read_target("Can you show me the files in the repo") is None
    assert github._natural_repo_read_target("Can you show me the files in the github") is None
    assert github._natural_repo_read_target("Can you show me README.md in the repo") == "README.md"
    assert reads.classify_read("Can you display the files?") is None
    assert not github.is_github_conversation("Can you display the files?")
    assert reads.classify_read("Can I see the files?") is None, "No implicit repo access without explicit scope"
    assert not github.is_github_conversation("Can I see the files?")
    assert github.GITHUB_CAPABILITY_STAGE=="read-repository"


def test_dragon58_root_context_followup_and_topic_fallback():
    """Latest thread in export (58): root listing succeeded, next scoped read failed."""
    from model_router import dispatch
    ctx = {"repo":"owner/repo","branch":"main","sourceSha":"a"*40,
           "directory":"","lastFile":"","kind":"directory"}
    shorter = "Can you show me the files"
    assert reads.classify_read(shorter) is None
    assert not github.is_github_conversation(shorter)
    assert github._implicit_repo_command(shorter, ctx) == "@GitHub files"
    assert github._implicit_repo_command("Can you display the files", ctx) == "@GitHub files"
    assert github._implicit_repo_command("Can you list files", ctx) == "@GitHub files"
    assert github._implicit_repo_command(shorter, None) is None
    assert github._implicit_repo_command(shorter, {**ctx, "sourceSha":"invalid"}) is None
    assert github._implicit_repo_command("Write code to show the files", ctx) is None
    assert github._implicit_repo_command("Delete these files", ctx) is None
    assert github._implicit_repo_command("Tell me about file permissions", ctx) is None
    feature = {**ctx, "branch":"feature/read"}
    assert github._implicit_repo_command(shorter, feature) == "@GitHub files on branch feature/read"
    observed = []
    def fake_read(data):
        observed.append(data["prompt"])
        yield {"type":"DELTA","text":"## GitHub directory: /\n- file README.md"}
        yield {"type":"COMPLETED","phase":"COMPLETE"}
    with mock.patch.object(github,"command_events",side_effect=fake_read), \
         mock.patch.object(github,"_post_github",side_effect=AssertionError("write forbidden")):
        events=list(github.agent_events({"userId":"google:test","prompt":shorter,"githubContext":ctx}))
    assert observed == ["@GitHub files"], observed
    assert any(e.get("phase") == "GITHUB_READ_STAGE" for e in events), events
    assert any("GitHub directory" in e.get("text","") for e in events), events
    def no_model(*args, **kwargs):
        raise AssertionError("A bare file topic is not an inference task")
    for model in ("700m","stock","coder","r39"):
        events=list(dispatch(model,{"prompt":"Files","history":[],"pinnedContext":[]},
                             no_model,no_model,no_model,no_model))
        assert any(e.get("phase")=="TOPIC_CLARIFICATION" for e in events), model
        assert any("GitHub repository" in e.get("text","") for e in events), model
        assert not any(e.get("phase")=="CODER_AUTO_ROUTE" for e in events), model


def test_dragon59_named_document_opinion_uses_verified_source():
    """Only the newest Dragon Chat (59) thread is current release evidence."""
    import hashlib
    specialist=github.source_specialist
    ctx={"repo":"owner/repo","branch":"main","sourceSha":"a"*40,
         "directory":"","lastFile":"","kind":"directory"}
    requests=(
        "What do you think of the §tart doc in the repo §wyrlz?",
        "Lol I asked what your opinion of our repo §tart doc is",
    )
    for question in requests:
        req=specialist.parse(question, ctx)
        assert req and req["path"]=="§wyrlz_§tart.md", (question,req)
        assert github.is_github_conversation(question), question
    assert specialist.parse("What do you think of README.md in the repo",ctx)["path"]=="README.md"
    assert specialist.parse("Your opinion of the §tart §E doc in the repo",ctx)["path"]=="§tart_§E.md"
    assert specialist.parse("What do you think of the repo?",ctx) is None
    assert specialist.parse("What do you think of my music?",ctx) is None
    assert specialist.parse("Edit the §tart doc in the repo",ctx)["mode"] == "change-proposal"

    content="# §wyrlz §tart\n\nCanonical project entrypoint. Other contracts own deployment.\n"
    raw=content.encode("utf-8")
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    snapshot={"sourceSha":"a"*40,
              "items":[{"path":"§wyrlz_§tart.md","type":"file","sha":sha}]}
    calls=[]
    def fake_coder(payload):
        calls.append(payload)
        yield {"type":"DELTA","text":"The document defines a canonical project entrypoint and identifies separate owners for deployment contracts. This separation helps keep runtime responsibilities clear, although the document is long."}
        yield {"type":"COMPLETED","phase":"COMPLETE"}
    with mock.patch.object(github,"_config",return_value={}), \
         mock.patch.object(github,"_load",return_value={"token":"test-secret","repo":"owner/repo"}), \
         mock.patch.object(github,"_effective_access",return_value={"allowed":True,"defaultBranch":"main"}), \
         mock.patch.object(github.explorer,"pinned_tree",return_value=snapshot), \
         mock.patch.object(github,"_read_optional",return_value={"sha":sha,"body":content}), \
         mock.patch.object(github,"_post_github",side_effect=AssertionError("write not allowed")):
        events=list(github.agent_events({"userId":"google:owner",
            "prompt":requests[0],"requestedModelId":"700m","githubContext":ctx},
            coder_generator=fake_coder))
    assert any(e.get("phase")=="CODER_SOURCE_READING" for e in events), events
    assert any(e.get("phase")=="GITHUB_CODER_READ_ONLY" for e in events), events
    assert any(e.get("type")=="GITHUB_CONTEXT" and
               e["context"].get("lastFile")=="§wyrlz_§tart.md" for e in events), events
    assert any("The document defines a canonical project entrypoint" in e.get("text","") for e in events)
    assert len(calls)==1
    assert "Give a direct opinion of the SELECTED DOCUMENT" in calls[0]["prompt"]
    assert "Canonical project entrypoint" in calls[0]["prompt"]
    assert "test-secret" not in calls[0]["prompt"]
    assert not any("Verified Git-tree inventory" in e.get("text","") for e in events)


def test_dragon60_named_doc_opinion_followup_is_verified():
    """Latest Dragon Chat (60): do not invent a Forge Start document."""
    import hashlib
    specialist=github.source_specialist
    ctx={"repo":"owner/repo","branch":"main","sourceSha":"a"*40,
         "directory":"","lastFile":"§wyrlz_§tart.md","kind":"file"}
    question="Now what about the §tart §E document"
    req=specialist.parse(question,ctx)
    assert req and req["path"]=="§tart_§E.md" and req.get("opinionFollowup"), req
    assert specialist.parse("What about the §tart §E document",ctx)["path"]=="§tart_§E.md"
    assert specialist.parse("Now what about docs/ENGINE.md document",ctx)["path"]=="docs/ENGINE.md"
    assert specialist.parse(question,None) is None
    assert specialist.parse(question,{**ctx,"sourceSha":"invalid"}) is None
    assert specialist.parse(question,{**ctx,"lastFile":""}) is None
    assert specialist.parse(question,{**ctx,"repo":"another user"}) is None
    assert specialist.parse("Now what about a strange unrelated issue",ctx) is None
    assert specialist.parse("Delete the §tart §E document",ctx) is None
    # This natural follow-up is routed by the verified thread-scope Station gate.
    assert specialist.parse(question,ctx) is not None
    source="# §tart §E — §wyrl§ Engine Build & Deploy Router\n\nForge has a separate Hugging Face deployment lane.\n"
    raw=source.encode("utf-8")
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    tree={"sourceSha":"a"*40,
          "items":[{"path":"§tart_§E.md","type":"file","sha":blob}]}
    calls=[]
    def fake_coder(payload):
        calls.append(payload)
        yield {"type":"DELTA","text":"The Forge-specific router separates the engine build and deployment lane from Chat. Its title and introductory content describe a distinct Hugging Face engine target for engine work."}
        yield {"type":"COMPLETED","phase":"COMPLETE"}
    with mock.patch.object(github,"_config",return_value={}), \
         mock.patch.object(github,"_load",return_value={"token":"test-secret","repo":"owner/repo"}), \
         mock.patch.object(github,"_effective_access",return_value={"allowed":True,"defaultBranch":"main"}), \
         mock.patch.object(github.explorer,"pinned_tree",return_value=tree), \
         mock.patch.object(github,"_read_optional",return_value={"sha":blob,"body":source}), \
         mock.patch.object(github,"_post_github",side_effect=AssertionError("no writes")):
        events=list(github.agent_events({"userId":"google:owner","prompt":question,
            "requestedModelId":"700m","githubContext":ctx},coder_generator=fake_coder))
    assert any(e.get("phase")=="CODER_SOURCE_READING" for e in events), events
    assert any(e.get("phase")=="GITHUB_CODER_READ_ONLY" for e in events), events
    assert any(e.get("type")=="GITHUB_CONTEXT" and
               e["context"].get("lastFile")=="§tart_§E.md" for e in events), events
    assert any("Forge-specific router separates" in e.get("text","") for e in events), events
    assert len(calls)==1
    assert "Give a direct opinion" in calls[0]["prompt"]
    assert "Forge has a separate Hugging Face deployment lane" in calls[0]["prompt"]
    assert "test-secret" not in calls[0]["prompt"]
    assert not any("SCWRLZ_§tart.md" in e.get("text","") for e in events)


def test_dragon61_source_purpose_not_provenance_echo():
    """Screenshots: model repeated SHA IDs and contradicted already verified source."""
    from github_source_specialist_v241 import (
        _source_answer_is_metadata_echo, _verified_document_outline)
    broken=("The verified source for the user's original request is the GitHub "
            "repository owner/repo with the commit " + "a"*40 +
            " and blob " + "b"*40 + ". The source is not verified, "
            "but it contains details about this file.")
    assert _source_answer_is_metadata_echo(broken)
    assert _source_answer_is_metadata_echo("The blob SHA is " + "a"*40)
    assert _source_answer_is_metadata_echo("No information.")
    meaningful=("This engine file serves as a build and deployment router. "
                "Its Startup contract tells maintainers to read the manifest, "
                "build script and patch modules, validate generated output, "
                "then verify the actual hosted release marker.")
    assert not _source_answer_is_metadata_echo(meaningful)

    source=("# §tart §E — §wyrl§ Engine Build & Deploy Router\n\n"
            "## Canonical lane\n\nThe Forge target is independent of Chat.\n\n"
            "## Startup contract\n\n"
            "- Read this router and the engine README.\n"
            "- Validate final generated HTML and JavaScript before merge.\n"
            "## Deployment truth contract\n\n"
            "Upload is not live-host verification.\n")
    outline=_verified_document_outline(source, "§tart_§E.md")
    assert "Engine Build & Deploy Router" in outline
    assert "Startup contract" in outline
    assert "Read this router" in outline
    assert "Validate final generated HTML" in outline
    assert "not an independent full-document model assessment" in outline

    import hashlib
    ctx={"repo":"owner/repo","branch":"main","sourceSha":"a"*40,
         "directory":"","lastFile":"§wyrlz_§tart.md","kind":"file"}
    raw=source.encode("utf-8")
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    tree={"sourceSha":"a"*40,"items":[{"path":"§tart_§E.md","sha":blob,"type":"file"}]}
    def meta_echo(_):
        yield {"type":"DELTA","text":broken}
        yield {"type":"COMPLETED","phase":"COMPLETE"}
    with mock.patch.object(github,"_config",return_value={}), \
         mock.patch.object(github,"_load",return_value={"token":"secret","repo":"owner/repo"}), \
         mock.patch.object(github,"_effective_access",return_value={"allowed":True,"defaultBranch":"main"}), \
         mock.patch.object(github.explorer,"pinned_tree",return_value=tree), \
         mock.patch.object(github,"_read_optional",return_value={"sha":blob,"body":source}):
        events=list(github.agent_events({"userId":"google:owner",
            "prompt":"Can you examine the §tart §E file and explain its purpose?",
            "requestedModelId":"700m","githubContext":ctx},coder_generator=meta_echo))
    assert any(e.get("phase")=="GITHUB_SOURCE_ANSWER_FALLBACK" for e in events), events
    deltas=[e.get("text","") for e in events if e.get("type")=="DELTA"]
    assert any("Engine Build & Deploy Router" in v for v in deltas), deltas
    assert not any("source is not verified" in v for v in deltas), deltas

if __name__=="__main__":
    test_exported_prompt_selects_real_authenticated_read()
    test_guard_preserves_real_programming_and_permission_limits()
    test_dragon58_root_context_followup_and_topic_fallback()
    test_dragon59_named_document_opinion_uses_verified_source()
    test_dragon60_named_doc_opinion_followup_is_verified()
    test_dragon61_source_purpose_not_provenance_echo()
    print("v247: repo-files view routes authenticated GitHub read; coder/write guard PASSED")
