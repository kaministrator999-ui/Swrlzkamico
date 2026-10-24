"""v241 Stage-1 source-specialist and cross-thread intent regressions.

All GitHub/Redis/model interactions are deterministic mocks. No external writes.
"""
import sys
import hashlib
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import github_connection as gh
import github_source_specialist_v241 as specialist
import project_work_registry_v241 as registry

USER = "google:owner123"
REPO = "example/demo"
HEAD = "a" * 40
TEST_BODY = "def answer(x):\n    return x + 1\n"
BLOB = hashlib.sha1(b"blob " + str(len(TEST_BODY.encode())).encode() + b"\0" + TEST_BODY.encode()).hexdigest()


def test_source_question_not_code_mutation():
    assert specialist.parse("@GitHub explain file src/app.py on branch feature/review") == {
        "path": "src/app.py", "branch": "feature/review",
        "goal": "@GitHub explain file src/app.py on branch feature/review"}
    assert specialist.parse("Explain this file",
                            {"lastFile": "hf_space/model_router.py",
                             "branch": "fix/branch"})["path"] == "hf_space/model_router.py"
    assert specialist.parse("@GitHub implement src/app.py")["mode"] == "change-proposal"
    assert specialist.parse("Review and edit src/app.py") is None
    assert specialist.parse("@GitHub explain file .env") is None
    assert specialist.parse("explain the file secrets/passwords.py") == {"invalid": True}
    assert specialist.parse("Explain files src/a.py and src/b.py") == {"ambiguous": True}
    assert gh.GITHUB_CAPABILITY_STAGE == "read-repository"
    assert gh._stage_blocks("@GitHub edit file src/app.py")
    assert gh._stage_blocks("@GitHub confirm abcdefg123")


def test_verified_source_reaches_only_coder_with_correct_provenance():
    body = TEST_BODY
    def api(_token, path):
        if path == "/repos/" + REPO + "/commits/feature%2Freview":
            return {"sha": HEAD}
        if path == "/repos/" + REPO + "/git/trees/" + HEAD + "?recursive=1":
            return {"truncated": False,
                    "tree": [{"type": "blob", "path": "src/app.py",
                              "sha": BLOB, "size": len(body)}]}
        raise AssertionError("Unexpected GitHub read path: " + path)
    called = []
    def coder(payload):
        called.append(payload)
        assert HEAD in payload["prompt"]
        assert BLOB in payload["prompt"]
        assert "return x + 1" in payload["prompt"]
        assert "No compiler" not in payload["prompt"] or "tests" not in payload["prompt"]
        yield {"type": "DELTA", "text": "The function adds one to x."}
        yield {"type": "COMPLETED", "phase": "COMPLETE"}
    data = {"userId": USER,
            "prompt": "@GitHub explain file src/app.py on branch feature/review",
            "requestedModelId": "700m"}
    with mock.patch.object(gh, "_config", return_value={}), \
         mock.patch.object(gh, "_load", return_value={"token": "read-only",
                                                     "repo": REPO}), \
         mock.patch.object(gh, "_effective_access",
                           return_value={"allowed": True, "defaultBranch": "main"}), \
         mock.patch.object(gh, "_api", side_effect=api), \
         mock.patch.object(gh, "_read_optional",
                           return_value={"sha": BLOB, "body": body}), \
         mock.patch.object(gh, "_post_github",
                           side_effect=AssertionError("GitHub write attempted")):
        result = list(gh.agent_events(data, coder_generator=coder))
    assert called and len(called) == 1
    assert result[-1]["type"] == "COMPLETED"
    assert any(e.get("phase") == "GITHUB_CODER_READ_ONLY" for e in result)
    assert any(e.get("type") == "GITHUB_CONTEXT" and
               e["context"]["sourceSha"] == HEAD for e in result)
    assert any("adds one" in e.get("text", "") for e in result)
    assert not any(e.get("type") in ("GITHUB_WRITE", "COMMIT") for e in result)


def test_source_blob_mismatch_fails_closed():
    def api(_token, path):
        if "/commits/" in path:return {"sha": HEAD}
        if "/git/trees/" in path:return {
            "truncated": False,
            "tree": [{"type": "blob", "path": "src/app.py", "sha": BLOB, "size": 22}]}
        raise AssertionError(path)
    with mock.patch.object(gh, "_config", return_value={}), \
         mock.patch.object(gh, "_load",
                           return_value={"token": "only-read", "repo": REPO}), \
         mock.patch.object(gh, "_effective_access",
                           return_value={"allowed": True, "defaultBranch": "main"}), \
         mock.patch.object(gh, "_api", side_effect=api), \
         mock.patch.object(gh, "_read_optional",
                           return_value={"sha": "c"*40, "body": "fake code"}):
        result = list(gh.agent_events({
            "userId": USER,
            "prompt": "@GitHub explain file src/app.py"}, coder_generator=
            lambda _p: (_ for _ in () if False)))
    assert any("mismatched" in e.get("text", "") for e in result)
    assert not any(e.get("phase") == "GITHUB_CODER_READ_ONLY" for e in result)


def test_declared_work_vs_topic_and_safe_account_isolation():
    assert registry.declared_goal("Files") is None
    assert registry.declared_goal("Should we design GitHub inference?") is None
    assert registry.declared_goal("How many GitHub files?") is None
    assert registry.declared_goal("Please implement GitHub inference source routing")
    assert registry._key(USER) != registry._key("google:differentowner")
    assert registry._relate({"paths":["hf_space/station.py"]},
                            {"paths":["hf_space/station.py"]}) == "same-file"
    assert registry._relate({"paths":["src/alpha.py"], "keywords":["github", "inference"]},
                            {"paths":["src/beta.py"],"keywords":["github", "inference"]}) == "possible-related-goal"


def test_two_thread_work_claims_are_not_duplicate_owners():
    records = {}
    def read(_config, owner):
        return (records.get(owner, (0, []))[0],
                list(records.get(owner, (0, []))[1]))
    def persist(_config, owner, revision, items):
        prior_revision, _ = records.get(owner, (0, []))
        if prior_revision != revision:return False
        records[owner] = (revision + 1, items)
        return True
    with mock.patch.object(registry.store, "_config", return_value={}), \
         mock.patch.object(registry, "_read", side_effect=read), \
         mock.patch.object(registry, "_persist", side_effect=persist):
        a = registry.observe(USER, "thread-a", REPO,
                             "Implement GitHub inference in hf_space/station.py")
        b = registry.observe(USER, "thread-b", REPO,
                             "Improve GitHub inference for hf_space/station.py")
        c = registry.observe("google:differentowner", "thread-c", REPO,
                             "Implement GitHub inference in hf_space/station.py")
        d = registry.observe(USER, "thread-z", "different/repo",
                             "Implement GitHub inference in hf_space/station.py")
        snapshot = registry.list_work(USER, REPO)
    assert a["status"] == b["status"] == "RECORDED"
    assert a["overlaps"] == []
    assert b["overlaps"] and b["overlaps"][0]["relationship"] == "same-file"
    assert c["overlaps"] == d["overlaps"] == []
    assert len(snapshot) == 2


if __name__ == "__main__":
    test_source_question_not_code_mutation()
    test_verified_source_reaches_only_coder_with_correct_provenance()
    test_source_blob_mismatch_fails_closed()
    test_declared_work_vs_topic_and_safe_account_isolation()
    test_two_thread_work_claims_are_not_duplicate_owners()
    print("v241 dual-model and cross-thread coordination PASS")
