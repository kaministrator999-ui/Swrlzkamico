"""Public synthetic comparison receipts; no Qwen/700M inference is performed."""
import copy
from maturity_pairing import compare_pairs, SCHEMA

H = "a" * 64
P = "b" * 64
O = "c" * 64
R = "d" * 64

def attempt(ok, suffix):
    return {
        "outputSha256": O if suffix == "before" else R,
        "grader": {"source": "independent", "receiptRef": f"ci:run/{suffix}",
                   "technicalPass": ok, "intentPass": ok},
    }

def pair(case_id, before, after):
    return {"caseId": case_id, "modelId": "Qwen2.5-Coder-1.5B",
            "checkpointSha256": H, "promptSha256": P, "evaluatorId": "audit-v1",
            "baseline": attempt(before, "before"),
            "candidate": attempt(after, "after")}

doc = {"schema": SCHEMA, "publicPractice": True, "pairs": [
    pair("small-edit", False, True),
    pair("repair", True, False),
    pair("correct", True, True),
    pair("both-bad", False, False),
    {**pair("not-run", True, True), "candidate": {}},
    {**pair("not-graded", True, True), "candidate": {"outputSha256": R}},
]}
score = compare_pairs(doc)
assert score["pairs"] == 6, score
assert score["counts"] == {
    "reportedImproved": 1, "reportedRegressed": 1,
    "reportedUnchanged": 2, "unscored": 2,
}
assert score["source"] == "reported-receipts-only-no-external-audit"
assert score["isSealedHoldout"] is False
assert score["canAuthorizeDeployment"] is False
assert score["provesWeightTraining"] is False
assert "UNSCORED" in [x["outcome"] for x in score["results"]]
assert "ci:run" not in str(score), "Diagnostic summary must not leak receipt IDs"

# A fake grader, incomplete two-gate result and absence of output cannot
# accidentally be promoted to passed model capability.
fake = copy.deepcopy(doc)
fake["pairs"][0]["candidate"]["grader"]["source"] = "self"
assert compare_pairs(fake)["counts"]["unscored"] == 3
fake = copy.deepcopy(doc)
fake["pairs"][0]["candidate"]["grader"]["intentPass"] = None
assert compare_pairs(fake)["counts"]["unscored"] == 3
fake = copy.deepcopy(doc)
fake["pairs"][0]["candidate"]["outputSha256"] = ""
assert compare_pairs(fake)["counts"]["unscored"] == 3

for mutate in ("duplicate", "bad-hash", "bad-schema", "raw-case-id"):
    bad = copy.deepcopy(doc)
    if mutate == "duplicate":
        bad["pairs"][1]["caseId"] = "small-edit"
    if mutate == "bad-hash":
        bad["pairs"][0]["promptSha256"] = "not-a-hash"
    if mutate == "bad-schema":
        bad["schema"] = "unsupported"
    if mutate == "raw-case-id":
        bad["pairs"][0]["caseId"] = "secret token here"
    try:
        compare_pairs(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid pair accepted: {mutate}")

private = copy.deepcopy(doc)
private["rawConversation"] = "SECRET_PLEASE_NEVER_PRINT"
assert "SECRET_PLEASE_NEVER_PRINT" not in str(compare_pairs(private))
print("MODEL_PAIRING_V183_PASS six synthetic pairs, two-gate, no-auto-pass, privacy")
