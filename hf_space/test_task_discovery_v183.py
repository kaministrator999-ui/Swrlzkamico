"""Deterministic post-discovery effort escalation with adversarial provenance checks."""
from task_effort import task_effort_plan
from task_discovery import reconcile_after_discovery

initial = task_effort_plan("Fix this tiny function")
assert initial["tier"] == 2, initial

scenarios = [
    ({"affectedFiles": 1, "affectedOwners": 1}, 2, "local edit stays focused"),
    ({"affectedFiles": 3}, 3, "three files require structured review"),
    ({"dependencyEdges": 2}, 3, "dependency chain needs evidence"),
    ({"failingTests": 1}, 3, "failure receipt escalates"),
    ({"affectedFiles": 6}, 4, "many files need integration"),
    ({"affectedOwners": 2}, 4, "cross-owner contract"),
    ({"dependencyEdges": 5}, 4, "dependency graph"),
    ({"riskTags": ["authentication"]}, 4, "auth boundary"),
    ({"riskTags": ["persistence"]}, 4, "durable-state boundary"),
    ({"riskTags": ["destructive"]}, 5, "dangerous operation"),
    ({"riskTags": ["data-loss"]}, 5, "verified loss of persistent data"),
    ({"riskTags": ["production-release"]}, 5, "deployment boundary"),
    ({"riskTags": ["schema-migration", "production-release"]}, 5, "live migration"),
]
for facts, expected, label in scenarios:
    plan = reconcile_after_discovery(initial, facts, trusted=True)
    assert plan["tier"] == expected, (label, plan)
    assert plan["automaticToolPermission"] is False
    assert plan["requiresAuthorization"] == (expected == 5), (label, plan)
    assert plan["evidenceState"] == "VERIFIED_BY_CALLER"

# A model/user-supplied verified-looking flag can never authorize escalation,
# lower prior risk, or add a privileged action by itself.
spoof = {
    "sourceVerified": True, "trusted": True, "riskTags": ["production-release"],
    "affectedFiles": 500, "secret": "NOT_FOR_DIAGNOSTICS",
}
for trust in (False,):
    result = reconcile_after_discovery(initial, spoof, trusted=trust)
    assert result["tier"] == 2 and not result["evidenceSummary"]
    assert result["evidenceState"] == "UNVERIFIED_NOT_APPLIED"
    assert "NOT_FOR_DIAGNOSTICS" not in str(result)

# Even trusted, schema-filtered, type-checked summaries exclude raw evidence.
strange = reconcile_after_discovery(initial, {
    "affectedFiles": True, "affectedOwners": -3,
    "dependencyEdges": "500", "failingTests": None,
    "riskTags": ["NOT_A_TAG", "persistence", 123, "persistence"],
    "rawPrompt": "TOP_SECRET",
}, trusted=True)
assert strange["tier"] == 4, strange
assert strange["evidenceSummary"]["affectedFiles"] == 0
assert strange["evidenceSummary"]["riskTags"] == ["persistence"]
assert "TOP_SECRET" not in str(strange)

big = reconcile_after_discovery(initial, {
    "affectedFiles": 10**50,
    "dependencyEdges": 10**50,
}, trusted=True)
assert big["evidenceSummary"]["affectedFiles"] == 1000
assert big["evidenceSummary"]["dependencyEdges"] == 1000

# High-consequence work is never downgraded when evidence looks small.
critical = task_effort_plan("Deploy this update to our production server")
assert critical["tier"] == 5
kept = reconcile_after_discovery(critical, {"affectedFiles": 1}, trusted=True)
assert kept["tier"] == 5 and kept["requiresAuthorization"]
assert not kept["escalated"]

# Bad evidence or malformed first-hop plans fail closed.
for invalid in (None, {}, {"schema": "wrong", "tier": 2}, {"schema": initial["schema"], "tier": True}):
    try:
        reconcile_after_discovery(invalid, {"affectedFiles": 10}, trusted=True)
    except ValueError:
        pass
    else:
        raise AssertionError(f"accepted invalid initial plan: {invalid}")

assert reconcile_after_discovery(initial, ["unexpected"], trusted=True)["tier"] == 2
print(f"TASK_DISCOVERY_V183_PASS scenarios={len(scenarios)} plus spoofing, privacy, type, monotonicity")
